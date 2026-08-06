#!/usr/bin/env python3
"""test_validate_template.py - Permanent regression tests for validate_template.

Plain asserts are NOT used; every check records PASS/FAIL and is printed with a
short display-mangle-safe marker. No pytest dependency: run directly with
    python scripts/test_validate_template.py
Exit code 0 if every check passes, 1 otherwise.

Covers:
  - validate_template(_template.docx) -> 0 issues, 0 warnings
  - structure: 7 heading-3 sections, 6 tables, 1 heading-1
  - 3 page breaks before sections 3 (Technical Requirements), 5 (Acceptance
    Criteria), 7 (Vendor Compliance Sheet)
  - placeholders: [CONFIRMED_YEARS], [CONFIRMED_COUNT], [CONFIRMED_STANDARD]
    present and exactly 3 distinct
  - whitespace-tolerant (norm) comparison of all 7 heading-3 texts against the
    ACTUAL template titles (the template is authoritative, not SKILL.md)
  - negative test: validate_template on a nonexistent path raises
"""

import importlib.util
import os
import re
import sys
from pathlib import Path

REPO = Path(r"D:\Software Development\rrcat-tender")
SCRIPTS_DIR = REPO / "scripts"
TEMPLATE = REPO / "_template.docx"

_spec = importlib.util.spec_from_file_location(
    "validate_template", str(SCRIPTS_DIR / "validate_template.py")
)
vt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vt)

# ACTUAL template heading-3 titles (byte-verified; template is authoritative).
EXPECTED_HEADINGS = [
    "1. Scope of Supply",
    "2. Bidder Qualification Criteria (BQC)",
    "3. Technical Requirements",
    "4. Bid Evaluation Criteria",
    "5. Acceptance Criteria:",
    "6. Delivery Terms",
    "7. Vendor Compliance Sheet (Mandatory)",
]

_failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    line = status + "|" + name + ("|" + detail if detail else "")
    print(line)
    if not cond:
        _failures.append(name)


def short(name):
    return re.sub(r"\W+", "_", name)[:24]


def main():
    if not TEMPLATE.exists():
        check("template_exists", False, str(TEMPLATE))
        _finish()
        return 1

    results = vt.validate_template(str(TEMPLATE))

    check("validate_template_0_issues", len(results["issues"]) == 0,
          "issues=%d" % len(results["issues"]))
    check("validate_template_0_warnings", len(results["warnings"]) == 0,
          "warnings=%d" % len(results["warnings"]))

    check("heading1_count_is_1", results["heading1_count"] == 1,
          "got=%d" % results["heading1_count"])
    check("heading3_count_is_7", results["heading3_count"] == 7,
          "got=%d" % results["heading3_count"])
    check("table_count_is_6", results["table_count"] == 6,
          "got=%d" % results["table_count"])

    pb = results.get("page_breaks_before") or []
    check("page_breaks_count_is_3", len(pb) == 3, "got=%d" % len(pb))
    check("page_break_before_technical_requirements",
          any("Technical Requirements" in t for t in pb))
    check("page_break_before_acceptance_criteria",
          any("Acceptance Criteria" in t for t in pb))
    check("page_break_before_vendor_compliance",
          any("Vendor Compliance Sheet" in t for t in pb))

    ph = list(results.get("placeholders_found") or [])
    check("placeholder_years_present", "[CONFIRMED_YEARS]" in ph)
    check("placeholder_count_present", "[CONFIRMED_COUNT]" in ph)
    check("placeholder_standard_present", "[CONFIRMED_STANDARD]" in ph)
    check("placeholder_distinct_count_is_3", len(set(ph)) == 3,
          "got=%d" % len(set(ph)))

    actual = list(results.get("heading3_texts") or [])
    check("heading3_texts_count_is_7", len(actual) == 7,
          "got=%d" % len(actual))
    for i, expected in enumerate(EXPECTED_HEADINGS):
        ok = i < len(actual) and vt.norm(actual[i]) == vt.norm(expected)
        check("heading3_%d_%s" % (i + 1, short(expected)), ok,
              "expected=%s got=%s" % (expected, actual[i] if i < len(actual) else "<missing>"))

    raised = False
    try:
        vt.validate_template(str(TEMPLATE.parent / "no_such_template.docx"))
    except Exception:
        raised = True
    check("nonexistent_path_raises", raised)

    _finish()
    return 0 if not _failures else 1


def _finish():
    print("SUMMARY|%d checks failed" % len(_failures))
    for name in _failures:
        print("FAILED_CHECK|" + name)


if __name__ == "__main__":
    sys.exit(main())
