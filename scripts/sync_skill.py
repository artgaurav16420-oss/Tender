#!/usr/bin/env python3
"""sync_skill.py one-command sync between workspace installed skill.

ADR-001 Sync Direction:
 Examples/*.md workspace -> installed skill dir
 SKILL.md installed skill dir -> workspace
UTF-8 normalization (no BOM) required BEFORE sync.
"""

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(r"D:/Software Development/rrcat-tender")
DEFAULT_TARGET = Path(r"C:/Users/INP/AppData/Local/hermes/skills/rrcat-tender")

UTF8_NO_BOM = "utf-8"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def utf8_normalize(path: Path) -> bool:
    """Read bytes, decode utf-8 (replace errors), re-encode utf-8 no BOM. Return True if changed."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
    normalized = text.encode(UTF8_NO_BOM)
    if normalized != raw:
        path.write_bytes(normalized)
        return True
    return False


def copy_and_verify(src: Path, dst: Path) -> tuple[bool, str]:
    """Copy src -> dst, verify byte-identical. Return (ok, message)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if sha256(src) == sha256(dst):
        return True, f"OK {src.name} ({src.stat().st_size} bytes)"
    return False, f"MISMATCH {src.name}"


def main():
    parser = argparse.ArgumentParser(description="Sync rrcat-tender skill")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET,
                    help="Installed skill directory (default: Hermes skills dir)")
    parser.add_argument("--dry-run", action="store_true",
                    help="Print plan without writing")
    parser.add_argument("--check", action="store_true",
                    help="Exit 1 if workspace/target differ (drift detection); no writes")
    args = parser.parse_args()

    target = args.target
    examples_src = WORKSPACE / "Examples"
    examples_dst = target / "Examples"
    skill_src = target / "SKILL.md"
    skill_dst = WORKSPACE / "SKILL.md"

    if not examples_src.exists():
        print(f"FAIL: {examples_src} not found", file=sys.stderr)
        return 1

    print(f"Workspace: {WORKSPACE}")
    print(f"Target:    {target}")
    print(f"Dry-run:   {args.dry_run}")
    print(f"Check:     {args.check}")

    # 1. UTF-8 normalize all Examples/*.md workspace
    print("\n--- UTF-8 Normalization ---")
    normalized_count = 0
    for md in sorted(examples_src.glob("*.md")):
        if md.name == "SYNC_TEST_TEMP.md":
            continue
        if utf8_normalize(md):
            print(f"  normalized: {md.name}")
            normalized_count += 1
    print(f"Normalized {normalized_count} files")

    if args.dry_run:
        print("\n--- Dry-run plan ---")
        for md in sorted(examples_src.glob("*.md")):
            print(f"  Examples/{md.name} -> {examples_dst}/{md.name}")
        print(f"  {skill_src} -> {skill_dst}")
        print("No files written.")
        return 0

    # In --check mode: compute both side hashes, compare, exit 1 if any mismatch
    if args.check:
        print("\n--- Drift check ---")
        mismatch = False
        for md in sorted(examples_src.glob("*.md")):
            if md.name == "SYNC_TEST_TEMP.md":
                continue
            dst = examples_dst / md.name
            if not dst.exists():
                print(f"  MISSING in target: {md.name}")
                mismatch = True
            elif sha256(md) != sha256(dst):
                print(f"  DIVERGED: {md.name}")
                mismatch = True
            else:
                print(f"  OK: {md.name}")
        if skill_src.exists():
            if sha256(skill_src) != sha256(skill_dst):
                print(f"  DIVERGED: SKILL.md")
                mismatch = True
            else:
                print(f"  OK: SKILL.md")
        else:
            print(f"  MISSING in target: SKILL.md")
            mismatch = True
        print(f"\n{'IN SYNC' if not mismatch else 'DRIFT DETECTED'}")
        return 0 if not mismatch else 1

    # 2. Copy Examples/*.md -> target/Examples/
    print("\n--- Copy Examples -> target ---")
    ok_all = True
    for md in sorted(examples_src.glob("*.md")):
        ok, msg = copy_and_verify(md, examples_dst / md.name)
        print(f"  {msg}")
        ok_all = ok_all and ok

    # 3. Copy target/SKILL.md -> workspace/SKILL.md
    print("\n--- Copy SKILL.md (target -> workspace) ---")
    if skill_src.exists():
        ok, msg = copy_and_verify(skill_src, skill_dst)
        print(f"  {msg}")
        ok_all = ok_all and ok
    else:
        print(f"  SKIP: {skill_src} not found")
        ok_all = False

    print(f"\n{'ALL VERIFIED' if ok_all else 'MISMATCHES DETECTED'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())