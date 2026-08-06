# RRCAT Tender Specification Generator

Generate procurement tender specifications for RRCAT, Indore, following Indian government open-tendering rules. Runs in OpenCode via the `rrcat-tender` skill.

## How to Use

1. Open OpenCode in your project directory.
2. Load the skill:
   ```
   skill rrcat-tender
   ```
3. Describe the equipment you need a tender for:
   ```
   Generate a tender specification for [describe your equipment here]
   ```
4. The agent will ask you questions one at a time from the Mandatory Review Checklist, with recommended answers. Answer each question in as much detail as you can.
5. After all questions are confirmed, the agent generates the complete tender specification in Markdown.
6. The agent converts the Markdown to `.docx` using officecli (preserving RRCAT template formatting).

> **Tip:** Answer every question in as much detail as you can. Vague answers produce weak tenders with "To Be Confirmed by RRCAT" placeholders. The more specific you are about ratings, materials, standards, and quantities, the tighter the generated spec.

## Tips for Best Results

- **Be specific with numbers** — capacity, pressure, temperature, dimensions, flow rate. "About 500L" is weaker than "500 L minimum working capacity".
- **Name the standards you expect** — IS 2825, ASME Sec VIII, ISO 21029, etc. If you don't know, say "Indian Standard equivalent" and the agent will suggest options.
- **Describe the end-use clearly** — "For LN2 storage in cryogenic lab" tells the agent more than "Storage tank".
- **Mention operating conditions** — indoor/outdoor, ambient temperature range, available utilities (415V 3-phase, cooling water, compressed air).
- **Specify safety requirements** — overpressure relief, emergency stop, explosion-proof rating, PESO certification if applicable.
- **Don't worry if unsure** — the agent will ask one question at a time and suggest recommended values. Pick the closest option or provide your own.

## What You'll Be Asked

The agent will ask ~31 questions across 7 sections, one at a time (with recommended answers). For experienced users, a grouped confirmation mode batches each section so you can accept or override items in fewer round-trips:

| Section | What's covered |
|---|---|
| 1. Scope of Supply | Item description, quantity, application, accessories, spares, ITC, training, civil works |
| 2. Bidder Qualification (BQC) | OEM experience, similar installations, certifications, OEM authorization, govt/PSU past performance |
| 3. Technical Requirements | Ratings, materials, standards, operating environment, interfaces, tolerances, safety, finish |
| 4. Bid Evaluation Criteria | Scoring parameters, technical/commercial weightage, disqualification criteria |
| 5. Acceptance Criteria | PDI tests, site tests, pass/fail criteria, rejection warning |
| 6. Delivery Terms | Delivery timeline, packaging, warranty |
| 7. Vendor Compliance Sheet | (Not an interview item — generated automatically as the mandatory Section 7) |

## Equipment Types Covered

The skill includes 22 real RRCAT tender examples covering:

- Solar PV systems with civil works (20 kWp, mounting shed, ALMM)
- Cold storage containers (40 ft, 4 TR, refrigeration)
- Cryogenic systems (dewars, LN2 containers, VJ hoses, cryostats, cryomodules)
- Vacuum equipment (TMP modules, gauges, DTL tanks, piping systems)
- Precision mechanics (EOT cranes, rail systems, tank assemblies)
- Lasers & optics (coated lenses, mirrors)
- Utilities (chillers, UHP argon gas supply, axial fans)
- Safety equipment (cryogenic PPE)

## Adding New Equipment Types

The skill learns from new tenders. If your equipment type isn't listed above, the generation will still work — the agent adapts the checklist to your equipment.

## Converting to Word (.docx)

The agent handles `.docx` generation automatically using officecli and the bundled RRCAT template (`_template.docx`). No manual conversion needed.

## License

MIT