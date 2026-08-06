#!/usr/bin/env python3
"""test_learn_real_mode.py Reversible real-mode fixture test for tender_learn.py.

Creates a temporary workspace copy, runs tender_learn.py in real mode
against a fixture .md, verifies:
1. Exactly 6 table cells in new row
2. Original SKILL.md unchanged
3. Temporary workspace SKILL.md has the new row

Does not modify repository SKILL.md.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def count_table_cells(row: str) -> int:
    """Count pipe-separated cells in a markdown table row."""
    parts = [c for c in row.split('|') if c.strip() != '']
    return len(parts)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "tender_learn.py"
    fixture = repo_root / "Examples" / "Twin_Dewar_Specs.md"
    
    if not fixture.exists():
        print(f"FAIL: Fixture not found: {fixture}")
        return 1
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory(prefix="rrcat_learn_test_") as tmpdir:
        tmp = Path(tmpdir)
        workspace = tmp / "workspace"
        shutil.copytree(repo_root, workspace, dirs_exist_ok=True)
        
        skill_orig = repo_root / "SKILL.md"
        skill_tmp = workspace / "SKILL.md"
        
        # Verify original SKILL.md hash
        orig_hash = sha256(skill_orig)
        print(f"Original SKILL.md sha256: {orig_hash[:16]}...")
        
        # Run tender_learn.py in real mode against the temporary workspace
        cmd = [sys.executable, str(script), str(fixture), "--workspace", str(workspace), "--output-skill", str(skill_tmp)]
        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"FAIL: tender_learn.py exited {result.returncode}")
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return 1
        
        print("tender_learn.py output:")
        print(result.stdout[-1000:])
        
        # Check 1: Original SKILL.md unchanged
        new_orig_hash = sha256(skill_orig)
        if new_orig_hash != orig_hash:
            print(f"FAIL: Original SKILL.md was modified! {orig_hash[:16]}... -> {new_orig_hash[:16]}...")
            return 1
        print("PASS: Original SKILL.md unchanged")
        
        # Check 2: Temporary workspace SKILL.md has new 6-cell row
        new_content = skill_tmp.read_text(encoding="utf-8")
        new_rows = [line for line in new_content.splitlines() 
                    if line.strip().startswith('|') and 'Twin_Dewar_Specs.md' in line]
        
        if not new_rows:
            print("FAIL: No new row found in temporary SKILL.md for Twin_Dewar_Specs.md")
            return 1
        
        # Find the newly added row (should be the one with 6 cells)
        target_row = None
        for row in new_rows:
            cells = count_table_cells(row)
            if cells == 6:
                target_row = row
                break
        
        if not target_row:
            print("FAIL: No 6-cell row found for Twin_Dewar_Specs.md")
            return 1
        
        print(f"New row: {target_row[:120]}...")
        print(f"Cell count: {count_table_cells(target_row)}")
        
        # Check 3: Verify the row has expected columns (non-empty)
        parts = [c.strip() for c in target_row.split('|') if c.strip() != '']
        if len(parts) == 6:
            print(f"Columns: {parts}")
            # First column should be the filename
            if 'Twin_Dewar_Specs' not in parts[0]:
                print(f"FAIL: First column not filename: {parts[0]}")
                return 1
            # Second column should be equipment type
            if not parts[1]:
                print("FAIL: Equipment type column empty")
                return 1
            # Columns 3-6 should be "TBD — requires analysis" or have extracted hints
            for i in range(2, 6):
                if not parts[i]:
                    print(f"FAIL: Column {i+1} empty")
                    return 1
        else:
            print(f"FAIL: Could not parse 6 columns from row: {target_row}")
            return 1
        
        print("ALL REAL-MODE TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())