# ADR-005: Defensive Procurement Principles

## Status
Accepted (2026-07-31)

## Context
RRCAT tenders must protect public money and prevent retendering caused by unqualified bidders winning contracts. Historical tenders show that "compliant on paper" bidders frequently lack actual capability, leading to failed deliveries, quality rejections, and wasted time. The skill encodes four core behavioral rules that act as a defensive writing framework.

## Decision
Every generated tender must embody these four principles. Agents using this skill MUST enforce them during generation.

### 1. Vendor Neutrality
**Rule:** Never use brand names, model numbers, or proprietary specifications.
**Implementation:**
- Use generic descriptors: "High-Precision Multimeter" not "Fluke 8508A"
- Specify performance parameters: "±0.005% DC voltage accuracy" not "equivalent to Fluke 8508A"
- Require make/model in bid evaluation (verifiable on OEM website) — this is the bidder's commitment, not the spec's constraint
**Loophole prevented:** Brand-name specs allow incumbent vendors to lock out competition; generic specs force all bidders to prove equivalence.

### 2. Zero Assumptions
**Rule:** Never auto-calculate safety margins, tolerances, deratings, or ratings. Every value comes from the user.
**Implementation:**
- If user says "500 L", the spec says "500 L minimum working capacity" — no automatic 10% margin
- If user says "SS 304", the spec says "SS 304 per ASTM A240" — no automatic upgrade to 316L
- If user doesn't know a value, the agent STOPS and asks — never fills in a "reasonable default"
**Loophole prevented:** Assumed margins become bidder's design target. If spec says "500 L (with 10% margin)", bidder builds 550 L and claims compliance. If spec says "500 L minimum", bidder must deliver ≥500 L.

### 3. Mandatory Clarification Pause
**Rule:** If any critical variable is missing or vague, STOP and ask. Do not proceed with placeholders.
**Implementation:**
- The Mandatory Review Checklist is a hard gate — generation does not start until all 31 questions are confirmed
- Incomplete answers trigger a 3-strike retry loop:
  - 1st: restate with recommended range + rationale
  - 2nd: offer concrete default: "Shall I proceed with [default]?"
  - 3rd: flag as "To Be Confirmed by RRCAT" in output + cover note
**Loophole prevented:** Vague specs ("adequate capacity", "suitable material") are unenforceable. Bidders interpret them minimally.

### 4. Defensive Specification Writing
**Rule:** Every clause must make it harder for unqualified bidders to fake compliance. If a requirement can be bypassed with "Yes/No/Complied" without evidence, rewrite it to demand verifiable proof.
**Implementation Patterns:**
| Weak Clause | Defensive Rewrite | Evidence Demanded |
|---|---|---|
| "Bidder must have ISO 9001" | "Bidder must submit valid ISO 9001 certificate (certificate number verifiable on accreditation body website)" | Certificate copy + accreditation body verification |
| "OEM experience 5 years" | "OEM must have manufactured similar equipment for ≥5 years. Submit PO copies for 3 installations in last 5 years with client contact details" | PO copies + completion certificates + client contacts |
| "Material: SS 304" | "Material of construction: SS 304 per ASTM A240. Submit CMTRs from NABL-accredited lab for each heat lot" | CMTRs + lab accreditation proof |
| "Warranty 12 months" | "Comprehensive replacement warranty against design defects, material flaws, and workmanship for 12 months from final acceptance at RRCAT facility. Warranty clock starts at acceptance, not delivery" | Warranty certificate with acceptance-date trigger |
| "Compliance: Yes/No" | **"Yes/No/Complied NOT ALLOWED."** Parameter-specific compliance with document references | Signed compliance sheet + supporting docs per row |

### Anti-Loophole Scanning (Mandatory Pre-Generation)
Before finalizing each generated section, the agent MUST scan for these loophole patterns:

1. **Evidence-Free Compliance** — Any requirement accepting "Complied" without document reference → rewrite to demand specific doc
2. **Unverifiable Claims** — "Bidder shall have..." without "Submit proof of..." → add evidence demand
3. **Ambiguous Standards** — "As per relevant standards" → cite exact standard (IS/ISO/ASME + year)
4. **Open-Ended Documentation** — "Documents to be enclosed" → list exact documents (GA drawing, datasheet, OEM auth, test cert)
4. **Missing Rejection Language** — No consequence for non-compliance → add "Bids with incomplete/unsigned sheets may be summarily rejected"
5. **Export Restriction** — No clause preventing equipment export for servicing → add "Export of equipment out of India for servicing not acceptable"
6. **Right to Audit** — No plant visit right → add "RRCAT reserves right to physically visit OEM plant and reject bid in case of incompetency"
7. **Traceable Part Numbers** — No requirement for OEM website verifiable make/model → add "Make & model number must be verifiable from manufacturer's website"
8. **Catalog vs Spec Copy** — "Catalog acceptable" → "Signed spec copy NOT accepted as catalogue; original product catalogue mandatory"

### Post-Generation Verification Checklist
The skill includes an 18-item verification checklist that explicitly encodes these anti-loophole checks. Every item must pass before presenting the tender.

## Alternatives Considered
- **Rely on RRCAT evaluators to catch gaps**: Rejected — evaluators review 20+ bids; systematic gaps in the spec itself cannot be caught at evaluation stage.
- **Add more mandatory clauses universally**: Rejected — over-specification increases cost and reduces bidder pool. Defensive writing targets specific vulnerabilities per equipment.
- **Use a "compliance matrix" template for all tenders**: Rejected — each equipment type has unique vulnerabilities. The Learned Pattern Library captures equipment-specific defenses.

## Consequences
- Every generated tender has embedded anti-loophole clauses specific to its equipment type
- Agents cannot "rush through" generation — the checklist and retry loop enforce completeness
- Vague user answers are flagged explicitly in the output, not hidden
- The Learned Pattern Library grows with each `/tender-learn`, compounding defensive knowledge