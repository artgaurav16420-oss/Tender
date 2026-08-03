#!/usr/bin/env bash
# Sync the rrcat-tender skill between the workspace (this repo) and the
# installed skill directory, implementing ADR-001 directions:
#
#   SKILL.md                                          installed -> workspace
#   Examples/*.md, AGENTS.md, _template.docx          workspace -> installed
#
# Also normalizes all Examples/*.md to UTF-8 without BOM and verifies
# integrity (SHA256 of SKILL.md + _template.docx, Examples counts,
# AGENTS.md presence).
#
# Usage:
#   bash scripts/sync.sh                    # sync + verify (installed dir must exist)
#   bash scripts/sync.sh --install          # bootstrap installed dir from workspace on first run
#   RRCAT_SKILL_DIR=/path bash scripts/sync.sh   # override install location
#
# Requires: cp, mv, head, tail, sha256sum (or shasum on macOS), wc.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL="${RRCAT_SKILL_DIR:-$HOME/.agents/skills/rrcat-tender}"
BOOTSTRAP=0
if [ "${1:-}" = "--install" ]; then BOOTSTRAP=1; fi

fail() { echo "ERROR: $*" >&2; exit 1; }
say()  { echo "sync: $*"; }

# sha256sum on Linux/Git-Bash; shasum -a 256 on macOS
if command -v sha256sum >/dev/null 2>&1; then
  sha256_of() { sha256sum "$1" | cut -d' ' -f1; }
else
  sha256_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
fi

[ -d "$WORKSPACE/Examples" ] || fail "workspace not detected (no Examples/ at $WORKSPACE)"

if [ ! -d "$INSTALL" ]; then
  if [ "$BOOTSTRAP" = "1" ]; then
    say "installed skill dir missing — bootstrapping $INSTALL from workspace"
    mkdir -p "$INSTALL" || fail "cannot create $INSTALL"
  else
    fail "installed skill dir not found: $INSTALL
Run the sync once with --install to bootstrap it from this workspace:
  bash scripts/sync.sh --install
Or set RRCAT_SKILL_DIR to the installed skill location."
  fi
fi

# Bootstrap: seed the installed dir from the workspace when SKILL.md is absent
if [ "$BOOTSTRAP" = "1" ] && [ ! -f "$INSTALL/SKILL.md" ]; then
  mkdir -p "$INSTALL/Examples"
  cp "$WORKSPACE/SKILL.md" "$INSTALL/SKILL.md"
  cp "$WORKSPACE/AGENTS.md" "$INSTALL/AGENTS.md"
  cp "$WORKSPACE/_template.docx" "$INSTALL/_template.docx"
  for f in "$WORKSPACE"/Examples/*.md; do
    [ -f "$f" ] && cp "$f" "$INSTALL/Examples/"
  done
  say "seeded installed dir from workspace (bootstrap)"
fi

# 1. Normalize encoding: strip UTF-8 BOM from all Examples/*.md
for f in "$WORKSPACE"/Examples/*.md; do
  [ -f "$f" ] || continue
  if [ "$(head -c 3 "$f")" = "$(printf '\357\273\277')" ]; then
    tail -c +4 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
    say "stripped BOM: ${f##*/}"
  fi
done

# 2. SKILL.md: installed -> workspace (canonical skill definition)
[ -f "$INSTALL/SKILL.md" ] || fail "installed SKILL.md missing at $INSTALL/SKILL.md — aborting (workspace copy kept)"
cp "$INSTALL/SKILL.md" "$WORKSPACE/SKILL.md"
say "SKILL.md: installed -> workspace"

# 3. Examples/*.md + AGENTS.md + _template.docx: workspace -> installed
mkdir -p "$INSTALL/Examples"
count=0
for f in "$WORKSPACE"/Examples/*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$INSTALL/Examples/"
  count=$((count+1))
done
cp "$WORKSPACE/AGENTS.md" "$INSTALL/AGENTS.md"
cp "$WORKSPACE/_template.docx" "$INSTALL/_template.docx"
say "Examples/*.md ($count files), AGENTS.md, _template.docx: workspace -> installed"

# 4. Verify integrity
FAILED=0
for rel in SKILL.md _template.docx; do
  h1=$(sha256_of "$INSTALL/$rel")
  h2=$(sha256_of "$WORKSPACE/$rel")
  if [ "$h1" = "$h2" ]; then
    say "SHA256 OK: $rel"
  else
    say "SHA256 MISMATCH: $rel"
    FAILED=1
  fi
done
wcount=$(ls "$WORKSPACE"/Examples/*.md 2>/dev/null | wc -l | tr -d ' ')
icount=$(ls "$INSTALL"/Examples/*.md 2>/dev/null | wc -l | tr -d ' ')
say "Examples count: workspace=$wcount installed=$icount"
[ "$wcount" = "$icount" ] || { say "Examples count MISMATCH"; FAILED=1; }
if [ -f "$INSTALL/AGENTS.md" ]; then
  say "AGENTS.md present in installed dir"
else
  say "AGENTS.md MISSING in installed dir"
  FAILED=1
fi

if [ "$FAILED" = "0" ]; then
  say "Synced — all files verified."
  exit 0
fi
fail "sync completed with integrity issues listed above"
