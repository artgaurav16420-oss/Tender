# ADR-006: Commercial Terms (EMD, PBG, Bid Validity, Liquidated Damages)

## Status
Accepted (2026-08-02)

## Context
The 7-section output template covers scope, BQC, technical, evaluation,
acceptance, delivery and the compliance sheet — but commercial/financial
conditions (Earnest Money Deposit, Performance Bank Guarantee, bid validity,
liquidated damages, payment terms, arbitration) were only addressed ad hoc,
appearing in scattered reference examples (e.g. EMD implied in the DC fan
tender, PBG in the EOT crane tender) with no systematized checklist questions
or boilerplate.

Indian government open-tendering practice (Manual for Procurement of Goods
2017, DAE/PSU usage, geM) treats these clauses as standard protective
mechanisms. Omitting them leaves the tender under-protected and forces
recreation per tender.

## Decision
1. **Checklist:** add four conditional questions to Section 7 (Delivery Terms),
   numbered 7.4–7.8: EMD amount/%, PBG % + validity, bid validity days, LD rate
   + cap, and payment terms. Each carries a recommended range and a
   "(Skip if...)" condition (e.g. EMD exemption for MSME/Startups with a valid
   Udyam certificate, or when the tender value is below the EMD threshold).
2. **Output Template:** extend Section 6 with a **6.2 Financial & Commercial
   Terms** block (2-column Term/Detail table) covering EMD, PBG (valid until
   warranty expiry + 60 days), bid validity, liquidated damages, payment terms,
   and arbitration (Arbitration and Conciliation Act, 1996; seat/venue Indore).
3. **Boilerplate clauses:** add exact EMD forfeiture, PBG, liquidated-damages
   and arbitration sentences to the Boilerplate Clauses section.
4. **Compliance sheet:** add EMD/PBG/LD rows under a "Delivery & Commercial
   Terms" group.
5. **Machine-readable capture:** the commercial block is a required section in
   `templates/tender-schema.json` and rendered by `scripts/render_tender.py`.
6. **Zero-assumptions preserved:** all figures are user-confirmed values with
   recommended ranges — the skill never fills in numbers silently.

## Alternatives Considered
- **Hard-code universal figures (e.g. EMD 2%, PBG 5%, LD 0.5%/wk cap 10%):**
  Rejected — violates the zero-assumptions rule; thresholds vary by tender
  policy, MSME/startup exemption status, and contract value.
- **Leave commercial terms out of the template (status quo):** Rejected —
  inconsistent, under-protective output; contradicts ADR-005's public-money
  protection goal.
- **New standalone Section 8:** Rejected — the 7-section structure is
  established (ADR-003, Formatting Rules); a 6.2 sub-block keeps the page-break
  and compliance-sheet layout intact.

## Consequences
- Every generated tender can now carry enforceable commercial conditions when
  confirmed by the user.
- Bidders must commit to EMD/PBG/LD in the compliance sheet, making the
  commercial offer auditable alongside technical compliance.
- Recommended ranges must be updated if RRCAT's purchasing policy or central
  guidelines change (single place: the checklist rows in SKILL.md).
- The JSON schema and renderer stay in sync with the template (both updated
  together).
