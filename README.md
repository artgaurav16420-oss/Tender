# Tender Specification Generator

AI-powered skill for generating watertight procurement tender specifications following Indian government open-tendering rules. Built as an OpenCode skill with a focus on eliminating loopholes, preventing spurious bids, and protecting public procurement.

## Structure

| Path | Description |
|------|-------------|
| `SKILL.md` | Canonical skill definition — templates, checklists, clauses, patterns |
| `AGENTS.md` | Agent instructions for OpenCode sessions |
| `Examples/` | Real tender specs (`.md` AI-readable + `.pdf` original format) |
| `docs/adr/` | Architecture decision records |
| `Tender_Spec_Chiller_20kW.*` | Generated sample: 20kW chiller spec (MD/DOC/DOCX/PDF) |
| `Techical Specification.pdf` | Reference technical specification |

## Workflow

1. Request a tender spec for any equipment type
2. Agent runs a **Mandatory Review Checklist** — all items must be confirmed before generation
3. Output follows a **6-section structure**: Header, Scope, Technical Specs, BQC, Terms, Annexures
4. **Post-Generation Verification** catches gaps before delivery

## Key Features

- **Defensive clauses** — eliminates ambiguity, blocks spurious compliance
- **Compliance sheet** — Yes/No/Complied format with signature, blocks generic "All compliance" responses
- **Vendor-neutral** — no brand names; performance-based specs only
- **Hold points** — PDI witness, inspection gates, testing before dispatch
- **Bidder Qualification Criteria (BQC)** — filters unqualified bidders upfront

## Examples

20+ real tender specs in `Examples/` covering:

- Cryogenic systems (dewars, LN2 containers, vacuum systems)
- Precision mechanics (EOT crane, rail systems, tank assemblies)
- Vacuum equipment (TMP modules, gauges, piping systems)
- Lasers & optics (coated lenses, mirrors)
- Safety equipment (cryogenic safety gears)
- Utilities (chillers, argon gas supply, axial fans)
- Particle accelerator components (cryomodules, drift tube linac parts)

Each example includes a Learned Pattern entry noting strengths (defensive clauses, verification gates) and gaps (missing compliance sheets, brand name violations) for continuous improvement.

## Auto-Learn

Drop a new tender PDF into `Examples/` and run `/tender-learn`. The agent will extract BQC style, table formats, and notable clauses, then add a row to the Learned Pattern Library in `SKILL.md`. Over time, the skill improves from every new tender.

## ADR

See `docs/adr/` for architecture decisions (sync direction, skill structure).

## License

MIT
