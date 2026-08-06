#!/usr/bin/env python3
"""test_questionnaire.py Regression tests for questionnaire.py.

Plain-assert runner (no pytest dependency -- pytest confirmed NOT
importable in this environment). Every check records PASS/FAIL and the
process exits non-zero if any check fails. Run directly:

    python scripts/test_questionnaire.py

Covers:
  detect_equipment_type() keyword -> (type_key, patterns) mapping for
    solar / PV / photovoltaic / on-grid / chiller / cooling / container /
    cold storage / cryostat / vacuum, plus the unknown-keyword default.
  Answer coverage contract: every [CONFIRMED_*] token present in
    _template.docx (18 distinct tokens) must have a non-empty value in
    get_answers('solar'). This is the leak-prevention contract: a
    generated tender must never leave a placeholder unfilled.
  make_answers_json(): writes UTF-8 JSON without BOM; json.load parses
    it; parsed keys equal get_answers() keys.
  All equipment types in questionnaire.EQUIPMENT_TYPES also cover all
    18 tokens.

Token source: the 18 tokens were enumerated from _template.docx with
`officecli dump _template.docx /body` AND cross-verified by extracting
word/document.xml from the .docx zip directly (both produce the same
sorted set; sha256 7e512e37551c6385a635c8dfba34aad5396f408b27b63932650972fda91f7065).
The zipfile method is used at runtime so the test has no officecli
dependency.

NOTE on 'on-grid': the task spec suggested on-grid -> solar, but the
ACTUAL trigger table (questionnaire.TYPE_TRIGGERS) has no 'on-grid'
entry -- the solar triggers are ["solar", "pv", "photovoltaic"].
detect_equipment_type('on-grid') therefore returns the unknown-keyword
default ("generic", []). Per instructions we test the actual API and
document that default behaviour here; the test would need updating if a
future TYPE_TRIGGERS edit adds an 'on-grid' trigger.

NOTE on the solar family name: the task spec said 'solar' -> 'Solar
System', but the ACTUAL API name is 'Solar PV System'
(questionnaire.EQUIPMENT_TYPES['solar'][0], verified byte-level via
sha256 of get_answers('solar'): c194664c...). The test asserts the
actual API value.
"""

import importlib.util
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(r"D:\Software Development\rrcat-tender")
SCRIPTS_DIR = REPO / "scripts"
TEMPLATE = REPO / "_template.docx"

_spec = importlib.util.spec_from_file_location(
    "questionnaire", str(SCRIPTS_DIR / "questionnaire.py")
)
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)

# The 18 distinct [CONFIRMED_*] tokens present in _template.docx
# (sorted; byte-verified against officecli dump /body).
EXPECTED_18_TOKENS = [
    "[CONFIRMED_ACCESSORY]",
    "[CONFIRMED_COUNT]",
    "[CONFIRMED_DESCRIPTION]",
    "[CONFIRMED_FEATURES]",
    "[CONFIRMED_FINISH]",
    "[CONFIRMED_GRADE]",
    "[CONFIRMED_KEY_SPEC]",
    "[CONFIRMED_MONTHS]",
    "[CONFIRMED_PARAM]",
    "[CONFIRMED_QTY]",
    "[CONFIRMED_RANGE]",
    "[CONFIRMED_SAFETY_STANDARD]",
    "[CONFIRMED_SPEC]",
    "[CONFIRMED_STANDARD]",
    "[CONFIRMED_STANDARD_REF]",
    "[CONFIRMED_VALUE]",
    "[CONFIRMED_WEEKS]",
    "[CONFIRMED_YEARS]",
]

_failures = []


def check(name, cond, detail=""):
    if cond:
        print("PASS %s" % name)
    else:
        print("FAIL %s: %s" % (name, detail))
        _failures.append(name)


def short(name):
    return re.sub(r"\W+", "_", name)[:40]


def non_empty(value):
    """A placeholder value counts as filled if it is not None/empty/blank."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def extract_template_tokens():
    """All distinct [CONFIRMED_*] tokens in _template.docx.

    Stdlib-only: reads word/document.xml straight from the .docx zip.
    Verified identical to `officecli dump <template> /body` (sha256
    7e512e37...).
    """
    with zipfile.ZipFile(TEMPLATE) as zf:
        doc = zf.read("word/document.xml").decode("utf-8", "replace")
    return sorted(set(re.findall(r"\[CONFIRMED_[A-Z0-9_]+\]", doc)))


def check_detect(keyword, expected_type_key, expected_name):
    """One detect_equipment_type assertion -> one PASS/FAIL line."""
    tag = "detect_%s" % short(keyword)
    type_key, patterns = q.detect_equipment_type(keyword)
    if expected_type_key == "generic":
        check(tag, type_key == "generic" and patterns == [],
              "keyword=%r got type_key=%r patterns=%d expected generic/[]"
              % (keyword, type_key, len(patterns)))
        return
    ok = (type_key == expected_type_key
          and q.TYPE_DISPLAY_NAMES.get(type_key) == expected_name
          and patterns == q.EQUIPMENT_TYPES[expected_type_key][1])
    check(tag, ok,
          "keyword=%r type_key=%s name=%s patterns=%d"
          % (keyword, type_key, q.TYPE_DISPLAY_NAMES.get(type_key), len(patterns)))


def check_coverage_solar_tokens():
    """Per-token contract: get_answers('solar') fills every template token."""
    answers = q.get_answers("solar")
    for token in EXPECTED_18_TOKENS:
        key = token[1:-1]
        check("coverage_solar_%s" % key, key in answers and non_empty(answers.get(key)),
              "missing or empty value for %s" % token)


def check_coverage_type(keyword):
    """Aggregate contract: one equipment type covers all 18 tokens."""
    answers = q.get_answers(keyword)
    missing = [t for t in EXPECTED_18_TOKENS
               if t[1:-1] not in answers or not non_empty(answers.get(t[1:-1]))]
    check("coverage_%s_all_18" % short(keyword), not missing,
          "unfilled tokens: %s" % (",".join(missing) if missing else ""))


def main():
    if not TEMPLATE.exists():
        check("template_exists", False, str(TEMPLATE))
        return 1

    # ---- 1. detect_equipment_type mapping (actual API) ----------------
    check_detect("solar", "solar", "Solar PV System")
    check_detect("PV", "solar", "Solar PV System")
    check_detect("photovoltaic", "solar", "Solar PV System")
    # on-grid: NOT in TYPE_TRIGGERS -> unknown-keyword default ("generic", []).
    # Documented behaviour; see module docstring. Change this check if a
    # future TYPE_TRIGGERS edit adds an on-grid trigger.
    check_detect("on-grid", "generic", None)
    check_detect("chiller", "chiller", "Re-circulating Chiller")
    check_detect("cooling", "chiller", "Re-circulating Chiller")
    check_detect("container", "container", "Cold Storage Container")
    check_detect("cold storage", "container", "Cold Storage Container")
    check_detect("cryostat", "cryogenic", "Cryogenic System / Cryostat")
    check_detect("vacuum", "vacuum", "Vacuum System")
    # unknown keyword returns the default ("generic", [])
    check_detect("diesel generator", "generic", None)

    # family names in EQUIPMENT_TYPES match the documented display names
    expected_names = {
        "solar": "Solar PV System",
        "chiller": "Re-circulating Chiller",
        "container": "Cold Storage Container",
        "vacuum": "Vacuum System",
        "cryogenic": "Cryogenic System / Cryostat",
        "piping": "Piping System",
    }
    check("equipment_types_family_names",
          {k: v[0] for k, v in q.EQUIPMENT_TYPES.items()} == expected_names,
          "got=%s" % {k: v[0] for k, v in q.EQUIPMENT_TYPES.items()})

    # ---- 2. Answer coverage contract (leak prevention) ----------------
    tokens = extract_template_tokens()
    check("template_18_distinct_tokens", len(tokens) == 18,
          "got %d tokens: %s" % (len(tokens), ",".join(tokens)))
    check("template_tokens_match_expected", tokens == EXPECTED_18_TOKENS,
          "got=%s" % ",".join(tokens))
    check_coverage_solar_tokens()

    # ---- 3. make_answers_json -----------------------------------------
    tmpdir = tempfile.mkdtemp(prefix="tq_test_")
    out_path = str(Path(tmpdir) / "answers_solar.json")
    try:
        returned = q.make_answers_json("solar", out_path)
        check("make_answers_json_returns_dict",
              returned == q.get_answers("solar"),
              "returned dict differs from get_answers")
        raw = Path(out_path).read_bytes()
        check("make_answers_json_no_bom", not raw.startswith(b"\xef\xbb\xbf"),
              "file starts with UTF-8 BOM")
        check("make_answers_json_utf8", raw.startswith(b"{"),
              "first byte 0x%02x, expected '{'" % (raw[0] if raw else -1))
        parsed = json.loads(raw.decode("utf-8"))
        check("make_answers_json_parses",
              isinstance(parsed, dict) and parsed == returned,
              "json.load result differs from returned dict")
        check("make_answers_json_same_keys",
              set(parsed.keys()) == set(q.get_answers("solar").keys()),
              "key sets differ: only_in_file=%s only_in_get=%s"
              % (sorted(set(parsed) - set(q.get_answers("solar"))),
                 sorted(set(q.get_answers("solar")) - set(parsed))))
    finally:
        try:
            Path(out_path).unlink()
            Path(tmpdir).rmdir()
        except OSError:
            pass  # best-effort cleanup; temp litter is not a test failure

    # ---- 4. every EQUIPMENT_TYPES entry covers all 18 tokens ----------
    for et in q.EQUIPMENT_TYPES:
        check_coverage_type(et)

    return 0 if not _failures else 1


def _finish():
    print("SUMMARY|%d checks failed" % len(_failures))
    for name in _failures:
        print("FAILED_CHECK|%s" % name)


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        _finish()
    sys.exit(rc)
