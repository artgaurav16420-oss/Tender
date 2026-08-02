# ADR-003: Compliance Sheet Format

## Status
Accepted (2026-07-31)

## Context
The Vendor Compliance Sheet (Section 7 of every tender) is the primary anti-loophole mechanism. It forces bidders to provide verifiable evidence for every requirement rather than vague 'Yes/No/Complied' responses. The format must be unambiguous, auditable, and enforceable.

RRCAT's historical tenders showed inconsistent compliance sheet designs: some had no compliance sheet at all (negative examples: Flexible VJ Hose, Self-Pressurized LN2 Container, Water Chiller draft), some had inconsistent numbering, some used 3-column instead of 4-column layouts, and some allowed "Complied" as a valid response.

## Decision
The compliance sheet **must** use the following format for every generated tender:

### Table Structure
- **4 columns**: Sr. No. | Parameter | Requirement | Vendor Compliance
- **Table style**: Table Grid (single border all sides, 4pt)
- **Cell margins**: Top=0, Left=108dxa (5.4pt), Bottom=0, Right=108dxa

### Section Header Rows
- Merged single cell spanning all 4 columns
- Bold text, height 490dxa
- Named by equipment group (e.g., "Main Equipment Group", "40 ft ISO Dry Shipping Container", "Solar Power Plant", "Civil Work")
- **NOT numbered** — they are category dividers only

### Numbering
- Sr. No. values: sequential integers (1, 2, 3, ... N) with **NO gaps**
- Do not carry over original numbering from reference examples if rows are removed or reordered

### Instruction Text
- Must appear before the table
- Bold label: **Instructions:**
- Body: "Bidders must indicate compliance clearly for every parameter. **'Yes/No/Complied' NOT ALLOWED.** Attach supporting documents for each claim. Bids with incomplete or unsigned sheets may be summarily rejected. Supporting documents shall be attached for each claim as applicable."
- Style: `Block Text` (Aptos 12pt Bold, Indent Left/Right=480, SpaceBefore/After=5pt)

### Signature Block
- After the table, 5 bold-labeled lines:
  - **Signature of Bidder:** _______________
  - **Name & Designation:** _______________
  - **Company Seal:** _______________
  - **Date:** _______________
  - **Place:** _______________

### Mandatory Inclusion
- Section 7 is **never omitted** — every generated tender includes it
- Post-Generation Verification explicitly checks for presence and format compliance

## Alternatives Considered
- **3-column (Parameter, Requirement, Compliance)**: Rejected — Sr. No. is essential for cross-referencing and audit trails.
- **Allow 'Yes/No/Complied' with evidence**: Rejected — "Complied" is a checkbox, not evidence. The phrase itself signals a loophole; explicit rejection forces narrative responses with document references.
- **Optional compliance sheet for simple items**: Rejected — even simple items need traceable evidence (make/model, certifications, test reports). Omission creates a gap spurious bidders exploit.

## Consequences
- Every tender has a consistent, auditable compliance matrix
- RRCAT evaluators can compare bids side-by-side by Sr. No.
- Bidders cannot submit "all complied" sheets without evidence
- Signature/seal/date blocks create legal accountability