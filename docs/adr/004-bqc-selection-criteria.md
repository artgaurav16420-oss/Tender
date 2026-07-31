# ADR-004: BQC Question Selection Criteria

## Status
Accepted (2026-07-31)

## Context
The Mandatory Review Checklist contains 25 questions across 6 sections. Each question must have a clear rationale: what loophole it closes, what evidence it demands, and why its recommended answer is the default. Without documented criteria, questions become arbitrary and new equipment types get inconsistent BQC coverage.

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

### The 25 Questions by Category

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

**Section 5: QA & Documentation (Questions 5.1-5.5)**
- PDI tests must be witnessable at vendor facility
- Third-party inspection (TPI) only for high-value/complex items
- Bid documents require verifiable make/model (OEM website check)
- FAT/SAT protocols required unless off-the-shelf

**Section 6: Commercial Terms (Questions 6.1-6.3)**
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
- **More questions (30+)**: Rejected — diminishing returns; 25 covers all 4 vulnerability categories. Additional questions add fatigue without new gatekeeping.

## Consequences
- Every generated tender has defensible BQC tailored to the specific equipment
- Skipped questions are documented in the output (not silently omitted)
- Recommended answers are starting points, not mandates — user can override with justification
- New equipment types automatically get appropriate BQC coverage via the same framework