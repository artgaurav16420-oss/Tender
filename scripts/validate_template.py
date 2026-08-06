#!/usr/bin/env python3
"""
Template Validator for _template.docx
Validates 7-section structure, table counts, page breaks, and placeholder presence.

NOTE: expected heading texts below are the ACTUAL texts found in _template.docx
(verified byte-level). They differ from SKILL.md's documented titles:
  - template: "1. Scope of Supply"          vs SKILL.md "1. Scope Supply"
  - template: "2. Bidder Qualification Criteria (BQC)" vs SKILL.md "2. Bidder QualificationCriteria (BQC)"
  - template: "7. Vendor Compliance Sheet (Mandatory)" vs SKILL.md "7. Vendor ComplianceSheet (Mandatory)"
When SKILL.md and template disagree, the template is authoritative for generated docs.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def run_officecli(cmd):
    """Run officecli command and return stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"officecli failed: {result.stderr}")
    return result.stdout


def norm(s):
    """Collapse whitespace for tolerant text comparison."""
    return re.sub(r'\s+', ' ', s).strip()


def parse_outline(output):
    """Parse officecli view outline output."""
    lines = output.strip().split('\n')
    headings = []
    tables = 0
    for line in lines:
        line = line.replace('\r', '')
        if 'heading 1' in line:
            headings.append(('h1', line))
        elif 'heading 3' in line:
            headings.append(('h3', line))
        elif '[Table:' in line or 'tables' in line.lower():
            match = re.search(r'(\d+)\s+tables', line, re.IGNORECASE)
            if match:
                tables = int(match.group(1))
    return headings, tables


def get_page_breaks(docx_path):
    """Get paragraphs with pageBreakBefore=true."""
    output = run_officecli(f'officecli query "{docx_path}" \'paragraph[pageBreakBefore=true]\'')
    return output.strip()


def get_paragraph_styles(docx_path):
    """Get all paragraph styles from annotated view."""
    output = run_officecli(f'officecli view "{docx_path}" annotated')
    return output


def validate_template(docx_path):
    """Validate template structure and return results dict."""
    results = {
        "heading1_count": 0,
        "heading3_count": 0,
        "heading3_texts": [],
        "table_count": 0,
        "page_breaks_before": [],
        "placeholders_found": [],
        "issues": [],
        "warnings": [],
    }

    # 1. Check outline structure
    outline = run_officecli(f'officecli view "{docx_path}" outline')
    headings, tables = parse_outline(outline)
    results["table_count"] = tables

    for htype, text in headings:
        if htype == 'h1':
            results["heading1_count"] += 1
        elif htype == 'h3':
            results["heading3_count"] += 1
            match = re.search(r'([\d]\.\s+.+?)"\s*\(heading', text)
            if match:
                results["heading3_texts"].append(match.group(1).strip())
            else:
                match = re.search(r'"([^"]+)"', text)
                if match:
                    results["heading3_texts"].append(match.group(1).strip())

    # 2. Check page breaks
    page_breaks = get_page_breaks(docx_path)
    results["page_breaks_raw"] = page_breaks if page_breaks else ""

    # 3. Check paragraph styles and placeholders
    annotated = get_paragraph_styles(docx_path)
    placeholders = re.findall(r'\[CONFIRMED_[A-Z_]+\]', annotated)
    results["placeholders_found"] = list(set(placeholders))

    malformed = re.findall(r'(?:minimum|least|ISOCONFIRMED)[A-Z_]+', annotated)
    if malformed:
        results["warnings"].append(f"Malformed placeholder text (missing spaces): {malformed}")

    # 4. Validate heading 3 texts match expected 7 sections
    #    (ACTUAL template texts, byte-verified)
    expected_sections = [
        "1. Scope of Supply",
        "2. Bidder Qualification Criteria (BQC)",
        "3. Technical Requirements",
        "4. Bid Evaluation Criteria",
        "5. Acceptance Criteria:",
        "6. Delivery Terms",
        "7. Vendor Compliance Sheet (Mandatory)",
    ]

    for i, expected in enumerate(expected_sections):
        if i < len(results["heading3_texts"]):
            actual = results["heading3_texts"][i]
            if norm(actual) != norm(expected):
                results["issues"].append(f"Section {i+1} mismatch: expected '{expected}', got '{actual}'")
        else:
            results["issues"].append(f"Missing section {i+1}: '{expected}'")

    # 5. Check table count
    if tables != 6:
        results["issues"].append(f"Expected 6 tables, found {tables}")

    # 6. Check page breaks on sections 3, 5, 7 (via dump JSON, query selector
    #    returns empty for this boolean-like prop in some CLI versions)
    pb_sections = []
    try:
        dump_json = run_officecli(f'officecli dump "{docx_path}" /body')
        dump_data = json.loads(dump_json)
        for op in dump_data:
            if op.get('command') == 'add' and isinstance(op.get('props'), dict):
                props = op['props']
                if props.get('pageBreakBefore') == 'true' and 'text' in props:
                    pb_sections.append(props['text'])
    except Exception as e:
        results["warnings"].append(f"Could not parse dump for page breaks: {e}")
    expected_pb = ["3. Technical Requirements", "5. Acceptance Criteria:", "7. Vendor Compliance Sheet (Mandatory)"]
    if not pb_sections:
        results["warnings"].append("No page breaks found - expected before sections 3, 5, 7")
    else:
        missing_pb = [t for t in expected_pb if not any(t in p for p in pb_sections)]
        if missing_pb:
            results["warnings"].append(f"Page breaks missing before: {missing_pb}")
        results["page_breaks_before"] = pb_sections

    # 7. Check BQC bold label prefixes present (style checks are heuristic
    #    because annotated output may mangle; presence of the labels is the gate)
    if "2.1" not in annotated or "Main Equipment Manufacturer" not in annotated:
        results["warnings"].append("BQC label '2.1 Main Equipment Manufacturer:' not found")
    if "2.2" not in annotated or "Accessories / Subcomponents Sourcing" not in annotated:
        results["warnings"].append("BQC label '2.2 Accessories / Subcomponents Sourcing:' not found")

    # 8. Check compliance sheet instruction text (whitespace-tolerant match)
    expected_instruction = expected_instruction = "Instructions: Bidders must indicate compliance clearly for every parameter. 'Yes/No/Complied' NOT ALLOWED. Attach supporting documents for each claim. Bids with incomplete or unsigned sheets may be summarily rejected. Supporting documents shall be attached for each claim as applicable."

    if norm(expected_instruction) not in norm(annotated):
        results["warnings"].append("Compliance sheet instruction text may not match exact reference")

    # 9. Check rejection warning paragraph before acceptance criteria
    #    (exact template text, byte-verified)
    rejection_warning = "Failing to the below acceptance criteria will result in rejection of the delivered product. RRCAT will not bear any cost associated with the rejected product, including transportation, freight, handling, or return shipment charges."
    if norm(rejection_warning) not in norm(annotated):
        results["issues"].append("Rejection warning paragraph missing before Acceptance Criteria table")

    return results


def main():
    docx_path = Path("D:/Software Development/rrcat-tender/_template.docx")
    if not docx_path.exists():
        docx_path = Path("_template.docx")
    if not docx_path.exists():
        print("ERROR: _template.docx not found", file=sys.stderr)
        sys.exit(1)

    print(f"Validating: {docx_path}")
    results = validate_template(str(docx_path))

    print("\n=== VALIDATION RESULTS ===")
    print(f"Heading 1 count: {results['heading1_count']}")
    print(f"Heading 3 count: {results['heading3_count']} (expected 7)")
    print(f"Table count: {results['table_count']} (expected 6)")
    print(f"Placeholders found: {len(results['placeholders_found'])}")
    for p in sorted(results['placeholders_found']):
        print(f"  - {p}")

    if results["issues"]:
        print("\n[ISSUES]")
        for issue in results["issues"]:
            print(f"  - {issue}")
    else:
        print("\n[OK] No structural issues")

    if results["warnings"]:
        print("\n[WARNINGS]")
        for warn in results["warnings"]:
            print(f"  - {warn}")

    if results["issues"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()