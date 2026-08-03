#!/usr/bin/env bash
# Repo-level integrity checks for the rrcat-tender skill repository.
# Used by CI (.github/workflows/ci.yml) and locally.
# Exit 0 = PASS, 1 = FAIL.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

FAILS=0
fail() { echo "FAIL: $*"; FAILS=$((FAILS+1)); }
ok()   { echo "ok: $*"; }

# 1. SKILL.md frontmatter
for key in "name: rrcat-tender" "version:" "license:" "description:" "changelog:"; do
  grep -q "^$key" SKILL.md || fail "SKILL.md frontmatter missing '$key'"
done
ok "SKILL.md frontmatter"

# 2. UTF-8 without BOM across all Markdown
for f in SKILL.md README.md AGENTS.md CHANGELOG.md CONTRIBUTING.md docs/*.md Examples/*.md; do
  [ -f "$f" ] || continue
  if [ "$(head -c 3 "$f")" = "$(printf '\357\273\277')" ]; then fail "BOM present: $f"; fi
done
ok "no BOM across Markdown files"

# 3. Every example referenced in SKILL.md
missing=0
for f in Examples/*.md; do
  b="$(basename "$f")"
  grep -qF "$b" SKILL.md || { fail "example not referenced in SKILL.md: $b"; missing=1; }
done
[ "$missing" = 0 ] && ok "all $(ls Examples/*.md 2>/dev/null | wc -l) examples referenced"

# 4. Learned Pattern Library rows have 6 columns (>= 7 pipes, contains .md)
awk '/^## Learned Pattern Library/{f=1} f && /^\| / && /\.md/{n=gsub(/\|/, "&"); if (n != 7) print NR ": " $0}' SKILL.md > /tmp/pl_bad.txt
if [ -s /tmp/pl_bad.txt ]; then
  fail "pattern library rows must have exactly 6 columns:"; cat /tmp/pl_bad.txt
else
  ok "pattern library 6-column rows"
fi
rm -f /tmp/pl_bad.txt

# 5. _template.docx integrity (zip + word/document.xml)
if [ -f _template.docx ]; then
  unzip -t _template.docx >/dev/null 2>&1 || fail "_template.docx is not a valid zip archive"
  unzip -p _template.docx word/document.xml >/dev/null 2>&1 || fail "_template.docx missing word/document.xml"
  ok "_template.docx valid"
else
  fail "_template.docx missing"
fi

# 6. Every ADR file present, well-formed, and referenced in SKILL.md (ADR-00X)
for f in docs/adr/*.md; do
  [ -f "$f" ] || continue
  adr="$(basename "$f" | cut -c1-3)"   # e.g. 006
  head -1 "$f" | grep -q "^# ADR-" || fail "$(basename "$f") does not start with '# ADR-'"
  grep -q "ADR-$adr" SKILL.md || fail "ADR-$adr not referenced in SKILL.md"
done
ok "all ADRs present, well-formed and referenced"

# 7. Scripts present and syntactically valid
for s in scripts/sync.sh scripts/sync.ps1 scripts/verify_tender.sh scripts/verify_repo.sh scripts/validate_tender_json.py scripts/render_tender.py; do
  [ -f "$s" ] || fail "missing $s"
done
bash -n scripts/sync.sh scripts/verify_tender.sh scripts/verify_repo.sh 2>/dev/null || fail "bash syntax error in one of the .sh scripts"
python3 -c 'import ast,sys; [ast.parse(open(f, encoding="utf-8").read()) for f in sys.argv[1:]]' scripts/validate_tender_json.py scripts/render_tender.py 2>/dev/null || fail "python syntax error in one of the .py scripts"
ok "scripts present and syntactically valid"

# 8. Templates parse as JSON and example passes validation
python3 -c 'import json; json.load(open("templates/tender-schema.json")); json.load(open("templates/tender.example.json"))' 2>/dev/null || fail "invalid JSON in templates/"
python3 scripts/validate_tender_json.py templates/tender.example.json >/dev/null 2>&1 || fail "templates/tender.example.json fails schema validation"
ok "templates JSON valid + example validated"

echo "---"
if [ "$FAILS" = "0" ]; then echo "RESULT: PASS"; exit 0; fi
echo "RESULT: FAIL ($FAILS)"
exit 1
