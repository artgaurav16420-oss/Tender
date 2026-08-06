#!/usr/bin/env python3
"""verify_generated.py - Post-generation verification for tender_gen.py output.

Checks (byte-accurate, via officecli dump captured in-process):
  1. placeholder leaks       - no [CONFIRMED_*] tokens remain
  2. rejection warning       - paragraph before Acceptance Criteria present
  3. compliance instruction  - 'Yes/No/Complied NOT ALLOWED' text present
  4. seven sections          - 7 heading-3 sections present, matching template
  5. page breaks             - pageBreakBefore before sections 3, 5, 7 (warn)
  6. pattern lines           - equipment-type defensive clauses present (optional)
  7. zip validity            - output is a readable .docx (zip with document.xml)

Expected texts are derived from the TEMPLATE at runtime (normalized whitespace
comparison), so the checks adapt to template wording and are immune to the
tool-result display mangling that drops spaces.
"""

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

DEFAULT_TEMPLATE = "D:/Software Development/rrcat-tender/_template.docx"


def run_officecli(args):
    """Run officecli, return (returncode, stdout)."""
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout


def dump_texts(docx_path):
    """Return (raw_text, ops) - raw concatenated body text and parsed dump ops."""
    rc, out = run_officecli(["officecli", "dump", docx_path, "/body"])
    if rc != 0:
        raise RuntimeError(f"officecli dump failed for {docx_path}: {out[:300]}")
    ops = json.loads(out)
    texts = []
    for op in ops:
        if isinstance(op, dict):
            t = (op.get("props") or {}).get("text")
            if isinstance(t, str):
                texts.append(t)
    return "\n".join(texts), ops


def norm(s):
    """Collapse all whitespace runs to single spaces, strip."""
    return re.sub(r"\s+", " ", s or "").strip()


def template_expected(template_path=DEFAULT_TEMPLATE):
    """Derive expected texts from the template: rejection warning, compliance
    instruction, section headings, page-break sections."""
    raw, ops = dump_texts(template_path)
    expected = {
        "rejection": None,
        "compliance": None,
        "headings": [],
        "pagebreak_headings": [],
    }
    for op in ops:
        if not isinstance(op, dict):
            continue
        props = op.get("props") or {}
        text = props.get("text")
        if not isinstance(text, str):
            continue
        style = str(props.get("style", "")).lower()
        if "heading" in style and text.strip():
            expected["headings"].append(norm(text))
            if str(props.get("pageBreakBefore", "")).lower() == "true":
                expected["pagebreak_headings"].append(norm(text))
        if expected["rejection"] is None and re.search(r"Failing\s+\S", text) and "acceptance criteria" in re.sub(r"\s+", " ", text).lower():
            expected["rejection"] = norm(text)
        if expected["compliance"] is None and "NOT ALLOWED" in text:
            expected["compliance"] = norm(text)
    return expected


def verify_document(docx_path, expected_patterns=None, template_path=DEFAULT_TEMPLATE):
    """Run all checks on docx_path. Returns results dict."""
    results = {
        "checks": {},   # name -> ("PASS" | "FAIL" | "WARN", detail)
        "issues": [],
    }
    docx_path = str(docx_path)

    # 7. zip validity first (cheap, fatal if broken)
    try:
        with zipfile.ZipFile(docx_path) as zf:
            names = zf.namelist()
            ok = "word/document.xml" in names
        results["checks"]["zip_valid"] = (
            "PASS" if ok else "FAIL",
            "valid .docx zip with word/document.xml" if ok else "missing word/document.xml",
        )
        if not ok:
            results["issues"].append("Output is not a valid .docx archive")
    except Exception as exc:
        results["checks"]["zip_valid"] = ("FAIL", f"not a zip: {exc}")
        results["issues"].append(f"Output not readable: {exc}")
        return results

    try:
        raw, ops = dump_texts(docx_path)
    except Exception as exc:
        results["checks"]["dump_readable"] = ("FAIL", str(exc))
        results["issues"].append(f"officecli dump failed: {exc}")
        return results

    # 1. placeholder leaks (raw text, byte-accurate)
    leaks = re.findall(r"\[CONFIRMED_[A-Z_0-9]+\]", raw)
    results["checks"]["placeholder_leaks"] = (
        "PASS" if not leaks else "FAIL",
        f"no [CONFIRMED_*] tokens remain" if not leaks
        else f"{len(leaks)} leak(s): {sorted(set(leaks))}",
    )
    if leaks:
        results["issues"].append(f"Placeholder leaks: {sorted(set(leaks))}")

    # expected texts derived from template
    expected = template_expected(template_path)
    norm_raw = norm(raw)

    # 2. rejection warning
    if expected["rejection"]:
        ok = expected["rejection"] in norm_raw
        results["checks"]["rejection_warning"] = (
            "PASS" if ok else "FAIL",
            "rejection warning paragraph present" if ok else "rejection warning paragraph missing",
        )
        if not ok:
            results["issues"].append("Rejection warning paragraph missing before Acceptance Criteria")
    else:
        results["checks"]["rejection_warning"] = ("WARN", "template has no rejection warning to compare")

    # 3. compliance instruction
    if expected["compliance"]:
        ok = expected["compliance"] in norm_raw
        results["checks"]["compliance_instruction"] = (
            "PASS" if ok else "FAIL",
            "compliance instruction text present" if ok else "compliance instruction text missing",
        )
        if not ok:
            results["issues"].append("Compliance sheet instruction text missing")
    else:
        results["checks"]["compliance_instruction"] = ("WARN", "template has no compliance text to compare")

    # 4. seven sections
    missing = [h for h in expected["headings"] if h not in norm_raw]
    results["checks"]["seven_sections"] = (
        "PASS" if not missing else "FAIL",
        f"{len(expected['headings'])} section headings present" if not missing
        else f"missing sections: {missing}",
    )
    if missing:
        results["issues"].append(f"Missing section headings: {missing}")

    # 5. page breaks before sections 3, 5, 7 (warn-level)
    pb_texts = []
    for op in ops:
        if not isinstance(op, dict):
            continue
        props = op.get("props") or {}
        if str(props.get("pageBreakBefore", "")).lower() == "true" and isinstance(props.get("text"), str):
            pb_texts.append(norm(props["text"]))
    missing_pb = [h for h in expected["pagebreak_headings"] if h not in pb_texts]
    results["checks"]["page_breaks"] = (
        "PASS" if not missing_pb else "WARN",
        f"page breaks before: {[h[:30] for h in pb_texts]}" if not missing_pb
        else f"page breaks missing before: {missing_pb}",
    )

    # 6. equipment pattern lines
    if expected_patterns:
        miss = []
        for p in expected_patterns:
            probe = norm(p)[:40]
            if probe not in norm_raw:
                miss.append(probe)
        results["checks"]["pattern_lines"] = (
            "PASS" if not miss else "FAIL",
            f"{len(expected_patterns)} equipment-type clauses injected" if not miss
            else f"missing clauses: {miss}",
        )
        if miss:
            results["issues"].append(f"Equipment-type clauses missing: {miss}")

    return results


def print_results(results):
    """Print PASS/FAIL lines (short markers, display-mangle-safe)."""
    for name, (status, detail) in results["checks"].items():
        print(f"[{status}] {name}: {detail}")
    print(f"--- issues: {len(results['issues'])}")
    for issue in results["issues"]:
        print(f"  ! {issue}")


def main():
    if len(sys.argv) < 2:
        print("usage: python verify_generated.py <docx> [pattern-file.json]", file=sys.stderr)
        return 2
    docx_path = sys.argv[1]
    patterns = None
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as f:
            patterns = json.load(f)
    results = verify_document(docx_path, expected_patterns=patterns)
    print_results(results)
    return 0 if not results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
