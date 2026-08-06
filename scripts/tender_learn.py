#!/usr/bin/env python3
"""tender_learn.py — executable /tender-learn pipeline for rrcat-tender skill.

Steps:
1. If input is .pdf: convert via markitdown to Examples/<basename>.md.
2. UTF-8 normalize the resulting .md.
3. Rule-based pattern extraction (no LLM): scan for lines containing keywords.
4. --dry-run: print extracted patterns + would-be SKILL.md update.
5. Real mode: append row to Learned Pattern Library table in workspace SKILL.md.
6. Print summary.
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(r"D:/Software Development/rrcat-tender")
EXAMPLES_DIR = WORKSPACE / "Examples"
MARKITDOWN = r"C:/Users/INP/miniconda3/Scripts/markitdown"

# Keywords for pattern extraction (rule-based)
PATTERN_KEYWORDS = [
    'compliance sheet', 'signed', 'rejection', 'ALMM', 'OEM',
    'authorization', 'warranty', 'leak', 'ASME', 'ISO', 'make',
    'model', 'acceptance', 'FAT', 'SAT', 'delivery', 'months', 'EMD'
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def utf8_normalize(path: Path) -> bool:
    """Read as bytes, decode utf-8 (replace errors), re-encode utf-8 no BOM. Return True if changed."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
    normalized = text.encode("utf-8")
    if normalized != raw:
        path.write_bytes(normalized)
        return True
    return False

def run_markitdown(input_path: Path, output_path: Path) -> bool:
    """Convert PDF to Markdown using markitdown. Return True on success."""
    if not MARKITDOWN or not os.path.exists(MARKITDOWN):
        print(f"WARN: markitdown not found at {MARKITDOWN}", file=sys.stderr)
        return False
    # markitdown CLI: markitdown <input> -o <output>
    cmd = [MARKITDOWN, str(input_path), "-o", str(output_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"WARN: markitdown failed: {result.stderr}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"WARN: markitdown exception: {e}", file=sys.stderr)
        return False

def extract_patterns(md_path: Path) -> list[str]:
    """Return unique lines containing any of PATTERN_KEYWORDS."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    found = set()
    for line in lines:
        lower = line.lower()
        for kw in PATTERN_KEYWORDS:
            if kw in lower:
                found.add(line)
                break
    return sorted(found)

def equipment_from_filename(filename: str) -> str:
    """Heuristic: strip extension, lowercase, take first significant word."""
    base = Path(filename).stem.lower()
    # Remove common suffixes/prefixes
    for affix in ['_20kwp', '_20kw', '_40ft', '_container', '_civil', '_solar', '_pv']:
        base = base.replace(affix, '')
    # Split by non-alphanumeric and take first part
    parts = re.split(r'[^a-z0-9]+', base)
    for p in parts:
        if p and len(p) >= 2:
            return p
    return base or "unknown"

def update_skill_md(workspace: Path, filename: str, equipment: str, patterns: list[str]) -> bool:
    """Append a row to the Learned Pattern Library table in SKILL.md.
    Returns True if the table was found and updated, False otherwise."""
    skill_md = workspace / "SKILL.md"
    try:
        content = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = skill_md.read_text(encoding="utf-8", errors="replace")

    lines = content.splitlines()
    # Find the Learned Pattern Library table header
    header_idx = -1
    for i, line in enumerate(lines):
        if "Learned Pattern Library" in line:
            header_idx = i
            break
    if header_idx == -1:
        print("WARN: 'Learned Pattern Library' header not found in SKILL.md", file=sys.stderr)
        return False

    # Find the start of the table (the next line that starts with '|')
    table_start = -1
    for i in range(header_idx + 1, len(lines)):
        if lines[i].strip().startswith('|'):
            table_start = i
            break
    if table_start == -1:
        print("WARN: Table start not found after header", file=sys.stderr)
        return False

    # Find the end of the table (last consecutive line starting with '|')
    table_end = table_start
    for i in range(table_start, len(lines)):
        if lines[i].strip().startswith('|'):
            table_end = i
        else:
            break

    # Build the new row
    patterns_str = ", ".join(patterns) if patterns else ""
    new_row = f"| {filename} | {equipment} | {patterns_str} |"

    # Insert after the last table row
    lines.insert(table_end + 1, new_row)

    # Also update Reference Examples list if present (look for a line with 'Reference Examples')
    for i, line in enumerate(lines):
        if "Reference Examples" in line and i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
            # Append a new bullet item after the last consecutive bullet
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('-'):
                j += 1
            lines.insert(j, f"- {filename}")
            break

    # Write back
    try:
        skill_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        print(f"WARN: Failed to write SKILL.md: {e}", file=sys.stderr)
        return False

def main():
    ap = argparse.ArgumentParser(description="Run /tender-learn pipeline")
    ap.add_argument("input_file", type=Path, help="Path to PDF or Markdown file")
    ap.add_argument("--dry-run", action="store_true", help="Do not modify SKILL.md")
    args = ap.parse_args()

    input_path = args.input_file.resolve()
    if not input_path.exists():
        print(f"FAIL: {input_path} not found", file=sys.stderr)
        return 1

    # Determine working markdown file
    md_path = None
    converted = False
    if input_path.suffix.lower() == ".pdf":
        md_path = EXAMPLES_DIR / (input_path.stem + ".md")
        print(f"Converting PDF to Markdown: {input_path.name} -> {md_path.name}")
        if not run_markitdown(input_path, md_path):
            print("FAIL: markitdown conversion failed", file=sys.stderr)
            return 1
        converted = True
    elif input_path.suffix.lower() == ".md":
        md_path = input_path
    else:
        print(f"FAIL: Unsupported file type {input_path.suffix}", file=sys.stderr)
        return 1

    # UTF-8 normalize
    if utf8_normalize(md_path):
        print(f"Normalized: {md_path.name}")
    else:
        print(f"No change: {md_path.name}")

    # Extract patterns
    patterns = extract_patterns(md_path)
    print(f"Extracted {len(patterns)} pattern lines:")
    for p in patterns:
        print(f"  - {p}")

    # Determine equipment from filename (use the markdown basename)
    equipment = equipment_from_filename(md_path.name)
    print(f"Detected equipment: {equipment}")

    # Would-be SKILL.md row
    patterns_str = ", ".join(patterns) if patterns else ""
    would_be_row = f"| {md_path.name} | {equipment} | {patterns_str} |"
    print(f"\nWould append to Learned Pattern Library table:")
    print(would_be_row)

    if args.dry_run:
        print("\nDRY-RUN: SKILL.md not modified.")
        # Clean up if we converted a PDF
        if converted and md_path.exists():
            try:
                md_path.unlink()
                print(f"Cleaned up temporary markdown: {md_path.name}")
            except Exception:
                pass
        return 0

    # Real mode: update SKILL.md
    print("\nUpdating SKILL.md...")
    if update_skill_md(WORKSPACE, md_path.name, equipment, patterns):
        print("SUCCESS: SKILL.md updated.")
    else:
        print("FAIL: Could not update SKILL.md (see warnings above)", file=sys.stderr)
        return 1

    # Clean up if we converted a PDF
    if converted and md_path.exists():
        try:
            md_path.unlink()
            print(f"Cleaned up temporary markdown: {md_path.name}")
        except Exception:
            pass

    return 0

if __name__ == "__main__":
    sys.exit(main())