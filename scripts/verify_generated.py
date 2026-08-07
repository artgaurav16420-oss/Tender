#!/usr/bin/env python3
"""Post-generation verification for tender_gen.py outputs."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def officecli() -> str:
    # Prefer bare name: Windows resolves it via PATHEXT and the original
    # proven-working invocation. A full .CMD path routes through cmd.exe,
    # which splits unquoted metacharacters (& in example filenames like
    # DTL-Tank...&Drawings_Optimized.docx) and breaks dumps.
    value = os.environ.get("RRCAT_OFFICECLI")
    if value:
        return value
    if shutil.which("officecli"):
        return "officecli"
    return "officecli"


DEFAULT_TEMPLATE = repo_root() / "_template.docx"


def run_officecli(args):
    # Pass args as a list: Python's list2cmdline quotes each argument for
    # cmd.exe, so metacharacters in paths (& in DTL-Tank...&Drawings.docx)
    # survive. Do NOT pre-quote args manually - double escaping breaks it.
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def dump_texts(docx_path, retries=3, delay=0.5):
    """Return (raw_text, ops) from officecli dump. Retry on Windows file lock."""
    for attempt in range(retries):
        result = run_officecli([officecli(), "dump", str(docx_path), "/body"])
        if result.returncode == 0:
            ops = json.loads(result.stdout)
            texts = []
            for op in ops:
                if isinstance(op, dict):
                    text = (op.get("props") or {}).get("text")
                    if isinstance(text, str):
                        texts.append(text)
            return "\n".join(texts), ops
        if attempt < retries - 1:
            time.sleep(delay)
    raise RuntimeError(f"officecli dump failed after {retries} attempts: {result.stdout[:300]}")


def template_expected(template_path=DEFAULT_TEMPLATE):
    raw, ops = dump_texts(template_path)
    expected = {"rejection": None, "compliance": None, "headings": [], "pagebreak_headings": []}
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
        compact = norm(text).lower()
        if expected["rejection"] is None and "failing" in compact and "acceptance criteria" in compact:
            expected["rejection"] = norm(text)
        if expected["compliance"] is None and "not allowed" in text.lower():
            expected["compliance"] = norm(text)
    return expected


def add_check(results, name, passed, detail, issue=None, status=None):
    state = status or ("PASS" if passed else "FAIL")
    results["checks"][name] = {"status": state, "passed": bool(passed), "detail": detail}
    if not passed and issue:
        results["issues"].append(issue)


def verify_document(docx_path, expected_patterns=None, template_path=DEFAULT_TEMPLATE):
    results = {"checks": {}, "issues": []}
    try:
        with zipfile.ZipFile(docx_path) as zf:
            valid = "word/document.xml" in zf.namelist()
        add_check(results, "zip_valid", valid, "valid .docx zip" if valid else "missing word/document.xml", "Output is not a valid .docx archive")
    except Exception as exc:
        add_check(results, "zip_valid", False, str(exc), f"Output not readable: {exc}")
        return results

    try:
        raw, ops = dump_texts(docx_path)
    except Exception as exc:
        add_check(results, "dump_readable", False, str(exc), f"officecli dump failed: {exc}")
        return results
    add_check(results, "dump_readable", True, "officecli dump succeeded")
    text = norm(raw)

    leaks = sorted(set(re.findall(r"\[CONFIRMED_[A-Z_0-9]+\]", raw)))
    unresolved = sorted(set(re.findall(r"\{\{[^{}]+\}\}|<TO\s+BE\s+FILLED>|\bTODO\b", raw, re.I)))
    add_check(results, "placeholder_leaks", not leaks, "no [CONFIRMED_*] tokens remain" if not leaks else str(leaks), f"Placeholder leaks: {leaks}")
    add_check(results, "unresolved_placeholders", not unresolved, "no unresolved template markers" if not unresolved else str(unresolved), f"Unresolved placeholders: {unresolved}")

    expected = template_expected(template_path)
    if expected["rejection"]:
        ok = norm(expected["rejection"]) in text
        add_check(results, "rejection_warning", ok, "rejection warning present" if ok else "missing", "Rejection warning paragraph missing")
    else:
        add_check(results, "rejection_warning", True, "template warning unavailable", status="WARN")
    if expected["compliance"]:
        ok = norm(expected["compliance"]) in text
        add_check(results, "compliance_instruction", ok, "compliance instruction present" if ok else "missing", "Compliance sheet instruction missing")
    else:
        add_check(results, "compliance_instruction", True, "template instruction unavailable", status="WARN")

    headings = expected["headings"]
    missing = [heading for heading in headings if heading not in text]
    add_check(results, "seven_sections", not missing, f"{len(headings)} section headings present" if not missing else f"missing: {missing}", f"Missing section headings: {missing}")
    positions = [text.find(heading) for heading in headings]
    ordered = all(pos >= 0 for pos in positions) and positions == sorted(positions)
    add_check(results, "section_order", ordered, "sections occur in template order" if ordered else f"positions: {positions}", "Sections are missing or out of order")

    pb_texts = []
    for op in ops:
        if isinstance(op, dict):
            props = op.get("props") or {}
            if str(props.get("pageBreakBefore", "")).lower() == "true" and isinstance(props.get("text"), str):
                pb_texts.append(norm(props["text"]))
    missing_pb = [heading for heading in expected["pagebreak_headings"] if heading not in pb_texts]
    add_check(results, "page_breaks", not missing_pb, "expected page breaks present" if not missing_pb else f"missing: {missing_pb}", status="WARN" if missing_pb else None)

    if expected_patterns:
        missing_patterns = [p for p in expected_patterns if norm(p)[:40] not in text]
        add_check(results, "pattern_lines", not missing_patterns, "equipment clauses present" if not missing_patterns else f"missing: {missing_patterns}", f"Equipment-type clauses missing: {missing_patterns}")

    return results


def print_results(results):
    for name, check in results["checks"].items():
        print(f"[{check['status']}] {name}: {check['detail']}")
    print(f"--- issues: {len(results['issues'])}")
    for issue in results["issues"]:
        print(f"  ! {issue}")


def main():
    parser = argparse.ArgumentParser(description="Verify generated tender .docx")
    parser.add_argument("docx")
    parser.add_argument("pattern_file", nargs="?", help="JSON list of expected defensive clauses")
    parser.add_argument("--json-report", type=Path, help="Write machine-readable report")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()
    patterns = None
    if args.pattern_file:
        with open(args.pattern_file, encoding="utf-8") as f:
            patterns = json.load(f)
    results = verify_document(args.docx, expected_patterns=patterns, template_path=args.template)
    print_results(results)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if not results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())