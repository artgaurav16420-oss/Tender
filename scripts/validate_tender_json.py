#!/usr/bin/env python3
"""Validate a tender JSON document against the rrcat-tender rules.

Zero-dependency (Python stdlib only). The checks mirror the requirements in
templates/tender-schema.json (kept here so the validator needs no `jsonschema`
package).

Usage:  python3 scripts/validate_tender_json.py <tender.json>
Exit codes: 0 = valid, 1 = invalid (errors are printed).
"""
import json
import re
import sys


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def check(cond, msg, errors):
    if not cond:
        errors.append(msg)


def validate(doc, path_label):
    errors = []
    if not isinstance(doc, dict):
        return [f"{path_label}: top level must be an object"]

    required = ["metadata", "scope", "bqc", "technical", "evaluation",
                "acceptance", "delivery", "commercial", "compliance"]
    # Extract every section defensively: a missing or mistyped section must
    # produce collected diagnostics, never a KeyError/AttributeError traceback.
    m = doc.get("metadata")
    if not isinstance(m, dict):
        check(isinstance(m, dict), f"{path_label}: metadata must be an object", errors)
        m = {}
    scope = doc.get("scope")
    if not isinstance(scope, list):
        check(isinstance(scope, list), f"{path_label}: scope must be an array", errors)
        scope = []
    bqc = doc.get("bqc")
    if not isinstance(bqc, dict):
        check(isinstance(bqc, dict), f"{path_label}: bqc must be an object", errors)
        bqc = {}
    tech = doc.get("technical")
    if not isinstance(tech, dict):
        check(isinstance(tech, dict), f"{path_label}: technical must be an object", errors)
        tech = {}
    ev = doc.get("evaluation")
    if not isinstance(ev, dict):
        check(isinstance(ev, dict), f"{path_label}: evaluation must be an object", errors)
        ev = {}
    acc = doc.get("acceptance")
    if not isinstance(acc, dict):
        check(isinstance(acc, dict), f"{path_label}: acceptance must be an object", errors)
        acc = {}
    deliv = doc.get("delivery")
    if not isinstance(deliv, dict):
        check(isinstance(deliv, dict), f"{path_label}: delivery must be an object", errors)
        deliv = {}
    comm = doc.get("commercial")
    if not isinstance(comm, dict):
        check(isinstance(comm, dict), f"{path_label}: commercial must be an object", errors)
        comm = {}
    comp = doc.get("compliance")
    if not isinstance(comp, dict):
        check(isinstance(comp, dict), f"{path_label}: compliance must be an object", errors)
        comp = {}

    check(isinstance(m.get("item"), str) and len(m.get("item", "")) >= 3,
          f"{path_label}: metadata.item must be a string (>= 3 chars)", errors)
    check(isinstance(m.get("quantity"), str) and m.get("quantity"),
          f"{path_label}: metadata.quantity must be a non-empty string", errors)
    check(isinstance(m.get("application"), str) and len(m.get("application", "")) >= 3,
          f"{path_label}: metadata.application must be a string (>= 3 chars)", errors)
    check(bool(re.fullmatch(r"RRCAT/\d{4}/PUR/\d{3}", m.get("ref", ""))),
          f"{path_label}: metadata.ref must match RRCAT/YYYY/PUR/XXX", errors)
    check(bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", m.get("date", ""))),
          f"{path_label}: metadata.date must be DD/MM/YYYY", errors)

    check(isinstance(scope, list) and len(scope) >= 1,
          f"{path_label}: scope must be a non-empty array", errors)
    for i, row in enumerate(scope):
        prefix = f"{path_label}: scope[{i}]"
        check(isinstance(row, dict), f"{prefix} must be an object", errors)
        if not isinstance(row, dict):
            continue
        check(row.get("item_no") == i + 1,
              f"{prefix}: item_no must be {i + 1} (sequential)", errors)
        check(row.get("category") in ("Main Equipment", "Accessories", "Mandatory Spares", "Documentation"),
              f"{prefix}: category must be Main Equipment/Accessories/Mandatory Spares/Documentation", errors)
        check(row.get("description"), f"{prefix}: description required", errors)
        check(row.get("key_spec") is not None, f"{prefix}: key_spec required", errors)
        check(row.get("qty"), f"{prefix}: qty required", errors)

    for key in ("years_experience", "similar_installations"):
        check(bqc.get(key), f"{path_label}: bqc.{key} required", errors)
    check(isinstance(bqc.get("certifications", []), list) and bqc.get("certifications"),
          f"{path_label}: bqc.certifications must be a non-empty array", errors)
    check(isinstance(bqc.get("oem_auth"), bool), f"{path_label}: bqc.oem_auth must be boolean", errors)
    check(isinstance(bqc.get("govt_past_performance"), bool),
          f"{path_label}: bqc.govt_past_performance must be boolean", errors)

    def tech_rows(rows, key, required, nonempty):
        """Validate technical table rows against the renderer's contract.

        The renderer indexes every listed field, so all must be present
        strings; fields in `nonempty` must additionally be non-empty.
        """
        if not isinstance(rows, list):
            check(False, f"{path_label}: technical.{key} must be an array", errors)
            return
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                check(False, f"{path_label}: technical.{key}[{i}] must be an object", errors)
                continue
            for f in required:
                check(isinstance(row.get(f), str),
                      f"{path_label}: technical.{key}[{i}].{f} must be a string", errors)
            for f in nonempty:
                check(isinstance(row.get(f), str) and row.get(f).strip(),
                      f"{path_label}: technical.{key}[{i}].{f} must be a non-empty string", errors)

    tech_rows(tech.get("main"), "main", ["param", "spec", "standard"], ["param", "spec"])
    if tech.get("accessories") is not None:
        tech_rows(tech.get("accessories"), "accessories", ["item", "spec", "standard"], ["item", "spec"])
    if tech.get("safety") is not None:
        tech_rows(tech.get("safety"), "safety", ["feature", "requirement"], ["feature", "requirement"])

    check(isinstance(ev.get("documents"), list) and ev.get("documents"),
          f"{path_label}: evaluation.documents must be a non-empty array", errors)
    check(ev.get("weightage"), f"{path_label}: evaluation.weightage required", errors)

    check(isinstance(acc.get("rejection_warning"), bool),
          f"{path_label}: acceptance.rejection_warning must be boolean", errors)
    tests = acc.get("tests")
    check(isinstance(tests, list) and tests,
          f"{path_label}: acceptance.tests must be a non-empty array", errors)
    if isinstance(tests, list):
        for i, t in enumerate(tests):
            if not isinstance(t, dict):
                check(False, f"{path_label}: acceptance.tests[{i}] must be an object", errors)
                continue
            for f in ("system", "protocol", "criteria"):
                check(isinstance(t.get(f), str) and t.get(f).strip(),
                      f"{path_label}: acceptance.tests[{i}].{f} must be a non-empty string", errors)

    check(isinstance(deliv.get("timeline_weeks"), int) and deliv.get("timeline_weeks", 0) >= 1,
          f"{path_label}: delivery.timeline_weeks must be a positive integer", errors)
    check(deliv.get("packaging"), f"{path_label}: delivery.packaging required", errors)
    check(isinstance(deliv.get("warranty_months"), int) and deliv.get("warranty_months", 0) >= 1,
          f"{path_label}: delivery.warranty_months must be a positive integer", errors)

    for key in ("emd", "pbg_percent", "ld_rate_percent", "ld_cap_percent", "payment_terms"):
        check(comm.get(key), f"{path_label}: commercial.{key} required", errors)
    check(isinstance(comm.get("bid_validity_days"), int) and comm.get("bid_validity_days", 0) >= 30,
          f"{path_label}: commercial.bid_validity_days must be >= 30", errors)

    rows = comp.get("rows")
    check(isinstance(rows, list) and rows,
          f"{path_label}: compliance.rows must be a non-empty array", errors)
    if isinstance(rows, list):
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                check(False, f"{path_label}: compliance.rows[{i}] must be an object", errors)
                continue
            has_group = "group" in row
            has_data = "param" in row and "requirement" in row
            check(has_group != has_data,
                  f"{path_label}: compliance.rows[{i}] must be either a {{group}} header or a {{param, requirement}} row", errors)
            # First row should be a group header per the compliance sheet format
            if i == 0 and not has_group:
                check(False, f"{path_label}: compliance.rows[0] should be a {{group}} header row", errors)

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate_tender_json.py <tender.json>", file=sys.stderr)
        return 2
    try:
        doc = load(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: cannot read file: {exc}", file=sys.stderr)
        return 1

    errors = validate(doc, sys.argv[1])
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        print(f"RESULT: FAIL ({len(errors)} error(s))")
        return 1
    print(f"RESULT: PASS — {sys.argv[1]} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
