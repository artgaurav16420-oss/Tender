# ADR-004: BQC Question Selection Criteria

## Status
Accepted (2026-07-31)

## Context
The Mandatory Review Checklist contains 31 questions across 7 sections. Each question must have a clear rationale: what loophole it closes, what evidence it demands, and why its recommended answer is the default. Without documented criteria, questions become arbitrary and new equipment types get inconsistent BQC coverage.

## Decision
BQC questions are selected and structured using the following methodology:

### Selection Framework (4 Vulnerability Categories)
Every question must address at least one of these vulnerability categories:

1. **OEM Gatekeeping** — Prevents unauthorized dealers, traders, or assemblers from bidding without OEM backing
2. **Past-Performance Verification** — Blocks bidders who claim experience but cannot produce verifiable PO copies/completion certificates
3. **Quality System Assurance** — Ensures the bidder's manufacturing process meets traceable standards (ISO, ASME, PESO)
4. **Technical Capability Proof** — Demands evidence of specific in-house facilities (welding, leak testing, CMM, He leak detector) rather than claims

### Question Design Rules
- **Recommended answers must be ranges/options, not single values** — allows user to calibrate to their equipment criticality
- **Each question has a "(Skip if: ...)" condition** — avoids irrelevant questions (e.g., spares for consumables, civil works for skid-mounted units)
- **Evidence demand is explicit in the recommended answer** — e.g., "3 installations (PO copies required)" not just "3 installations"
- **No binary Yes/No questions** — every question demands a quantified or documented response

### The 31 Questions by Category

**Section 1-2: Scope & Metadata (Questions 1.1-2.5)**
- Establish what is being bought, for what purpose, and what ancillary services (ITC, training, civil) are in scope
- Drives table row count in Scope of Supply and downstream sections

**Section 3: BQC Core (Questions 3.1-3.5)**
| # | Question | Vulnerability Addressed | Recommended Answer Rationale |
|---|---|---|---|
| 3.1 | OEM years experience | OEM Gatekeeping | 5+ years = minimum to have encountered field failures and iterated designs |
| 3.2 | Similar installations count | Past-Performance | 3 = minimum to show repeatability; <3 = prototype risk |
| 3.3 | Quality certifications | Quality System | ISO 9001 baseline; domain-specific (ISO 14001, ASME, CE) per equipment |
| 3.4 | OEM authorization | OEM Gatekeeping | Blocks traders; required even if bidder is OEM (self-auth) |
| 3.5 | Govt/PSU past performance | Past-Performance | Govt clients = stricter acceptance; verifiable via public records |

**Section 4: Technical Requirements (Questions 4.1-4.9)**
- Each question maps to a row in the Technical Specifications table
- Standards cited must follow Standard Priority rule (IS > ISO/IEEE/ASME/ASTM)
- Material grades require IS/ASTM equivalents — no trade names
- Tolerances/accuracy only asked when critical (Skip if not applicable)

**Section 5: Bid Evaluation Criteria (Questions 5.1-5.3)**
- Technical parameters evaluated in scoring (capacity compliance, efficiency, warranty, delivery, past performance)
- Technical vs. commercial weightage (70/30 recommended for critical equipment)
- Mandatory disqualification criteria (non-compliance with BQC, incomplete documentation, conditional bids)

**Section 6: Acceptance Criteria (Questions 6.1-6.4)**
- PDI tests must be witnessable at vendor facility
- Site acceptance tests at RRCAT after installation
- Quantified pass/fail criteria per parameter
- Rejection warning paragraphs mandatory

**Section 7: Delivery Terms (Questions 7.1-7.3)**
- Delivery timeline drives LD clauses
- Packaging standards only for export/transit-sensitive items
- Warranty minimum 12 months; 24+ for critical equipment

### Conditional Branching
Questions with "(Skip if: ...)" are omitted from the interview flow when the condition is true. This prevents:
- Asking about spares for consumable items
- Asking about ITC scope when supply-only
- Asking about civil works when vendor provides interface requirements only
- Asking about tolerances for standard catalog items

## Alternatives Considered
- **Fixed question set per equipment type**: Rejected — equipment varies; conditional branching handles variation with one universal checklist.
- **Fewer questions with open-ended responses**: Rejected — open-ended responses miss specific evidence demands. Structured questions ensure no gap.
- **More questions (35+)**: Rejected — diminishing returns; 31 covers all 4 vulnerability categories. Additional questions add fatigue without new gatekeeping.

## Consequences
- Every generated tender has defensible BQC tailored to the specific equipment
- Skipped questions are documented in the output (not silently omitted)
- Recommended answers are starting points, not mandates — user can override with justification
- New equipment types automatically get appropriate BQC coverage via the same framework