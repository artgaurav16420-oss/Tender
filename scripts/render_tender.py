#!/usr/bin/env python3
"""Render a tender JSON document into the canonical 7-section Markdown and an
officecli merge payload.

Usage:
  python3 scripts/render_tender.py templates/tender.example.json -o out/

Writes:
  out/<slug>.md                  — full 7-section tender Markdown (canonical output)
  out/<slug>.officecli-data.json — flat {{key}} -> value map for `officecli merge`
  out/<slug>.officecli-notes.md  — notes for building the .docx from _template.docx

The rendered Markdown must pass `bash scripts/verify_tender.sh out/<slug>.md`
before it is presented or converted to .docx.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REJECTION_WARNING = (
    "Failing to the below acceptance criteria will result in rejection of the "
    "delivered product. RRCAT will not bear any cost associated with the "
    "rejected product, including transportation, freight, handling, or return "
    "shipment charges."
)

INSTRUCTIONS = (
    "Instructions: Bidders must indicate compliance clearly for every "
    "parameter. **'Yes/No/Complied' NOT ALLOWED.** Attach supporting documents "
    "for each claim. Bids with incomplete or unsigned sheets may be summarily "
    "rejected. Supporting documents shall be attached for each claim as "
    "applicable."
)

SIGNATURE_BLOCK = [
    "Signature of Bidder:",
    "Name & Designation:",
    "Company Seal:",
    "Date:",
    "Place:",
]


def slugify(text):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_").lower()
    return slug or "tender"


def md_table(header, rows, aligns=None):
    """Render a Markdown table. rows = list of lists of str."""
    aligns = aligns or []
    lines = ["| " + " | ".join(header) + " |"]
    sep = []
    for i in range(len(header)):
        a = aligns[i] if i < len(aligns) else "left"
        sep.append({"left": ":---", "center": ":---:", "right": "---:"}[a])
    lines.append("| " + " | ".join(sep) + " |")
    for row in rows:
        cells = [(str(c) if c is not None else "") for c in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render(doc):
    m = doc["metadata"]
    lines = []
    lines.append(f"# TENDER SPECIFICATION FOR {m['item']}")
    lines.append("")
    lines.append(f"**Tender Ref.:** {m['ref']} | **Date:** {m['date']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Scope of Supply
    lines.append("### 1. Scope of Supply")
    lines.append("")
    lines.append(f"Procurement of {m['item']} for {m['application']} at RRCAT, Indore.")
    lines.append("")
    scope_rows = [[r["item_no"], r["category"], r["description"], r["key_spec"], r["qty"]]
                  for r in doc["scope"]]
    lines.append(md_table(["Item No.", "Category", "Item Description", "Key Specifications", "Qty"],
                          scope_rows, ["left", "left", "left", "left", "center"]))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 2. BQC
    bqc = doc["bqc"]
    lines.append("### 2. Bidder Qualification Criteria (BQC)")
    lines.append("")
    lines.append("**2.1 Main Equipment Manufacturer:**")
    lines.append("- The OEM must have minimum " + bqc["years_experience"] + " years of experience in manufacturing similar equipment. Supporting documents (Purchase Orders / Completion Certificates) must be provided as verifiable evidence.")
    lines.append("- Must have supplied at least " + bqc["similar_installations"] + " units of similar capacity to government / PSU / reputed organizations in the past 5 years. Supporting documents (Purchase Orders / Completion Certificates) must be provided as verifiable evidence.")
    lines.append("- Must hold valid " + ", ".join(bqc["certifications"]) + " certification(s). Copies of valid certificates must be enclosed with the bid.")
    lines.append("")
    lines.append("**2.2 Accessories / Subcomponents Sourcing:**")
    lines.append("- Subcomponents must be sourced from ISO-certified manufacturers.")
    lines.append("- Bidder must submit OEM authorization certificate for main equipment" +
                 (" on OEM letterhead." if bqc.get("oem_auth") else "."))
    if bqc.get("govt_past_performance"):
        lines.append("- Past performance certificates from government / PSU clients are preferred.")
    for reg in bqc.get("regulatory", []) or []:
        lines.append(f"- Regulatory compliance: {reg}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 3. Technical Requirements
    tech = doc["technical"]
    lines.append("### 3. Technical Requirements")
    lines.append("")
    lines.append("**3.1 Main Equipment**")
    lines.append("")
    main_rows = [[r["param"], r["spec"], r["standard"]] for r in tech["main"]]
    lines.append(md_table(["Parameter", "Specification", "Standard"], main_rows,
                          ["left", "left", "center"]))
    if tech.get("accessories"):
        lines.append("")
        lines.append("**3.2 Accessories & Ancillaries**")
        lines.append("")
        acc_rows = [[r["item"], r["spec"], r["standard"]] for r in tech["accessories"]]
        lines.append(md_table(["Item", "Specification", "Standard"], acc_rows,
                              ["left", "left", "center"]))
    if tech.get("safety"):
        lines.append("")
        lines.append("**3.3 Safety Features**")
        lines.append("")
        safe_rows = [[r["feature"], r["requirement"]] for r in tech["safety"]]
        lines.append(md_table(["Feature", "Requirement"], safe_rows))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 4. Bid Evaluation Criteria
    ev = doc["evaluation"]
    lines.append("### 4. Bid Evaluation Criteria")
    lines.append("")
    lines.append("The bidder must provide following documents/information for bid evaluation:")
    for i, d in enumerate(ev["documents"]):
        lines.append(f"{chr(97 + i)}) {d}")
    lines.append("")
    lines.append(f"**Weightage:** {ev['weightage']}")
    if ev.get("disqualification"):
        lines.append("")
        lines.append("**Mandatory disqualification criteria:**")
        for d in ev["disqualification"]:
            lines.append(f"- {d}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 5. Acceptance Criteria
    acc = doc["acceptance"]
    lines.append("### 5. Acceptance Criteria:")
    lines.append("")
    if acc.get("rejection_warning"):
        lines.append("> " + REJECTION_WARNING)
        lines.append("")
    acc_rows = [[t["system"], t["protocol"], t["criteria"]] for t in acc["tests"]]
    lines.append(md_table(["System", "Test Protocol", "Acceptance Criteria"], acc_rows))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 6. Delivery Terms (6.1) + Financial & Commercial Terms (6.2)
    deliv = doc["delivery"]
    comm = doc.get("commercial") or {}
    lines.append("### 6. Delivery Terms")
    lines.append("")
    lines.append("**6.1 Delivery Terms**")
    lines.append("")
    deliv_rows = [
        ["Delivery Timeline", f"{deliv['timeline_weeks']} weeks from Purchase Order date"],
        ["Packaging", deliv["packaging"]],
        ["Warranty", f"{deliv['warranty_months']} months from final acceptance against design defects, material flaws, and workmanship for complete assembly and all supplied hardware/software"],
    ]
    lines.append(md_table(["Term", "Detail"], deliv_rows))
    if comm:
        lines.append("")
        lines.append("**6.2 Financial & Commercial Terms**")
        lines.append("")
        comm_rows = []
        if comm.get("emd"):
            comm_rows.append(["Earnest Money Deposit (EMD)", comm["emd"]])
        if comm.get("pbg_percent"):
            comm_rows.append(["Performance Bank Guarantee (PBG)", f"{comm['pbg_percent']}% of contract value, valid until warranty expiry + 60 days"])
        if comm.get("bid_validity_days"):
            comm_rows.append(["Bid Validity", f"{comm['bid_validity_days']} days from bid opening"])
        if comm.get("ld_rate_percent"):
            comm_rows.append(["Liquidated Damages", f"{comm['ld_rate_percent']}% of the value of the delayed portion per week of delay, subject to a maximum of {comm.get('ld_cap_percent', '')}% of contract value"])
        if comm.get("payment_terms"):
            comm_rows.append(["Payment Terms", comm["payment_terms"] + (" (GST extra as applicable)" if "GST" not in comm["payment_terms"] else "")])
        if comm.get("arbitration"):
            comm_rows.append(["Arbitration", comm["arbitration"]])
        lines.append(md_table(["Term", "Detail"], comm_rows))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 7. Vendor Compliance Sheet (Mandatory)
    lines.append("### 7. Vendor Compliance Sheet (Mandatory)")
    lines.append("")
    lines.append("> " + INSTRUCTIONS)
    lines.append("")
    comp_rows = []
    sr = 1
    for row in doc["compliance"]["rows"]:
        if "group" in row:
            comp_rows.append([f"**{row['group']}**", "", "", ""])
        else:
            comp_rows.append([str(sr), row["param"], row["requirement"], ""])
            sr += 1
    lines.append(md_table(["Sr. No.", "Parameter", "Requirement", "Vendor Compliance"],
                          comp_rows))
    lines.append("")
    for label in SIGNATURE_BLOCK:
        lines.append(f"**{label}** \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_")
    lines.append("")
    return "\n".join(lines)


def officecli_data(doc):
    """Flat {{key}} -> value map for officecli merge."""
    m = doc["metadata"]
    deliv = doc["delivery"]
    comm = doc.get("commercial") or {}
    data = {
        "tender_ref": m["ref"],
        "date": m["date"],
        "equipment": m["item"],
        "purpose": m["application"],
        "quantity": m["quantity"],
        "delivery_weeks": str(deliv["timeline_weeks"]),
        "packaging": deliv["packaging"],
        "warranty_months": str(deliv["warranty_months"]),
    }
    for key in ("emd", "pbg_percent", "bid_validity_days", "ld_rate_percent",
                "ld_cap_percent", "payment_terms", "arbitration"):
        if comm.get(key):
            data[key] = str(comm[key])
    return data


def officecli_notes(slug, out_dir):
    return f"""# officecli build notes — {slug}

1. Copy the template:  cp _template.docx {slug}.docx   (Windows: Copy-Item)
2. If the template contains {{{{key}}}} placeholders, populate them with:
     officecli merge {slug}.docx {slug}.docx --data '<contents of {slug}.officecli-data.json>'
3. Otherwise populate per the Formatting Rules in SKILL.md, using
   {slug}.md as the authoritative content source (officecli set / batch).
4. officecli close {slug}.docx
5. Verify: officecli view {slug}.docx outline && officecli validate {slug}.docx
6. Gate: bash scripts/verify_tender.sh {slug}.md  (must exit 0)

Note: officecli is not required for rendering; it is only needed to build the
final .docx on a machine where it is installed.
"""


def main():
    ap = argparse.ArgumentParser(description="Render a tender JSON to Markdown + officecli payload")
    ap.add_argument("input", help="tender JSON file")
    ap.add_argument("-o", "--out", default=".", help="output directory (default: current dir)")
    args = ap.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: cannot read {args.input}: {exc}", file=sys.stderr)
        return 1

    slug = slugify(doc["metadata"]["item"])
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / f"{slug}.md"
    md_path.write_text(render(doc), encoding="utf-8")

    data_path = out_dir / f"{slug}.officecli-data.json"
    data_path.write_text(json.dumps(officecli_data(doc), indent=2) + "\n", encoding="utf-8")

    notes_path = out_dir / f"{slug}.officecli-notes.md"
    notes_path.write_text(officecli_notes(slug, out_dir), encoding="utf-8")

    print(f"Rendered: {md_path}")
    print(f"Merge data: {data_path}")
    print(f"Notes: {notes_path}")
    print("Next: bash scripts/verify_tender.sh " + str(md_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
