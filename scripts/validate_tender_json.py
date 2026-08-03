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
    for key in required:
        check(key in doc, f"{path_label}: missing required key '{key}'", errors)
    if "metadata" not in doc:
        return errors
    if "scope" not in doc:
        return errors

    m = doc["metadata"]
    check(isinstance(m.get("item"), str) and len(m["item"]) >= 3,
          f"{path_label}: metadata.item must be a string (>= 3 chars)", errors)
    check(isinstance(m.get("quantity"), str) and m.get("quantity"),
          f"{path_label}: metadata.quantity must be a non-empty string", errors)
    check(isinstance(m.get("application"), str) and len(m.get("application", "")) >= 3,
          f"{path_label}: metadata.application must be a string (>= 3 chars)", errors)
    check(bool(re.fullmatch(r"RRCAT/\d{4}/PUR/\d{3}", m.get("ref", ""))),
          f"{path_label}: metadata.ref must match RRCAT/YYYY/PUR/XXX", errors)
    check(bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", m.get("date", ""))),
          f"{path_label}: metadata.date must be DD/MM/YYYY", errors)

    scope = doc["scope"]
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

    bqc = doc["bqc"]
    check(isinstance(bqc, dict), f"{path_label}: bqc must be an object", errors)
    if isinstance(bqc, dict):
        for key in ("years_experience", "similar_installations"):
            check(bqc.get(key), f"{path_label}: bqc.{key} required", errors)
        check(isinstance(bqc.get("certifications", []), list) and bqc.get("certifications"),
              f"{path_label}: bqc.certifications must be a non-empty array", errors)
        check(isinstance(bqc.get("oem_auth"), bool), f"{path_label}: bqc.oem_auth must be boolean", errors)
        check(isinstance(bqc.get("govt_past_performance"), bool),
              f"{path_label}: bqc.govt_past_performance must be boolean", errors)

    tech = doc["technical"]
    check(isinstance(tech.get("main"), list) and tech.get("main"),
          f"{path_label}: technical.main must be a non-empty array", errors)
    if isinstance(tech.get("main"), list):
        for i, row in enumerate(tech["main"]):
            if not isinstance(row, dict) or not row.get("param"):
                check(False, f"{path_label}: technical.main[{i}] must have param/spec/standard", errors)

    ev = doc["evaluation"]
    check(isinstance(ev.get("documents"), list) and ev.get("documents"),
          f"{path_label}: evaluation.documents must be a non-empty array", errors)
    check(ev.get("weightage"), f"{path_label}: evaluation.weightage required", errors)

    acc = doc["acceptance"]
    check(isinstance(acc.get("rejection_warning"), bool),
          f"{path_label}: acceptance.rejection_warning must be boolean", errors)
    check(isinstance(acc.get("tests"), list) and acc.get("tests"),
          f"{path_label}: acceptance.tests must be a non-empty array", errors)

    deliv = doc["delivery"]
    check(isinstance(deliv.get("timeline_weeks"), int) and deliv.get("timeline_weeks", 0) >= 1,
          f"{path_label}: delivery.timeline_weeks must be a positive integer", errors)
    check(deliv.get("packaging"), f"{path_label}: delivery.packaging required", errors)
    check(isinstance(deliv.get("warranty_months"), int) and deliv.get("warranty_months", 0) >= 1,
          f"{path_label}: delivery.warranty_months must be a positive integer", errors)

    comm = doc["commercial"]
    check(isinstance(comm, dict), f"{path_label}: commercial must be an object", errors)
    if isinstance(comm, dict):
        for key in ("emd", "pbg_percent", "ld_rate_percent", "ld_cap_percent", "payment_terms"):
            check(comm.get(key), f"{path_label}: commercial.{key} required", errors)
        check(isinstance(comm.get("bid_validity_days"), int) and comm.get("bid_validity_days", 0) >= 30,
              f"{path_label}: commercial.bid_validity_days must be >= 30", errors)

    comp = doc["compliance"]
    check(isinstance(comp.get("rows"), list) and comp.get("rows"),
          f"{path_label}: compliance.rows must be a non-empty array", errors)
    if isinstance(comp.get("rows"), list):
        for i, row in enumerate(comp["rows"]):
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
