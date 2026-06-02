# RRCAT Tender Specification Generator

Generate procurement tender specifications for RRCAT, Indore, following Indian government open-tendering rules. Works on Gemini web — no software to install.

## How to Use

1. Open [gemini.google.com](https://gemini.google.com) in your browser.
2. Click the `+` button → **Upload Code** → paste this URL:
   ```
   https://github.com/artgaurav16420-oss/Tender.git
   ```
   Press Enter. The repo attaches to the chat like a file.
3. Paste this prompt:
   ```
   I've attached the RRCAT Tender Skill repo. Read SKILL.md and follow the Mandatory Review Checklist one question at a time, with recommended answers. After all questions are confirmed, generate the complete tender specification in Markdown. Equipment: [describe your equipment here]
   ```
4. Answer each question Gemini asks. Be as detailed as you can.
5. After generation, copy the Markdown output and save it as a `.md` file.

> **Tip:** Answer every question in as much detail as you can. Vague answers produce weak tenders with "To Be Confirmed by RRCAT" placeholders. The more specific you are about ratings, materials, standards, and quantities, the tighter the generated spec.

## Tips for Best Results

- **Be specific with numbers** — capacity, pressure, temperature, dimensions, flow rate. "About 500L" is weaker than "500 L minimum working capacity".
- **Name the standards you expect** — IS 2825, ASME Sec VIII, ISO 21029, etc. If you don't know, say "Indian Standard equivalent" and Gemini will suggest options.
- **Describe the end-use clearly** — "For LN2 storage in cryogenic lab" tells Gemini more than "Storage tank".
- **Mention operating conditions** — indoor/outdoor, ambient temperature range, available utilities (415V 3-phase, cooling water, compressed air).
- **Specify safety requirements** — overpressure relief, emergency stop, explosion-proof rating, PESO certification if applicable.
- **Don't worry if unsure** — Gemini will ask one question at a time and suggest recommended values. Pick the closest option or provide your own.

## What You'll Be Asked

Gemini will ask ~15-20 questions across these areas, one at a time:

| Area | What's covered |
|---|---|
| Basic Info | What equipment, how many, what's it for |
| Scope of Supply | Main items, accessories, spares, installation, training |
| Bidder Qualification (BQC) | OEM experience needed, past installations, certifications |
| Technical Requirements | Ratings, materials, standards, environment, safety features |
| Quality Assurance | Tests, inspections, documents to submit |
| Commercial Terms | Delivery timeline, packaging, warranty period |

## Equipment Types Covered

The skill includes 20+ real RRCAT tender examples covering:

- Cryogenic systems (dewars, LN2 containers, VJ hoses, cryostats, cryomodules)
- Vacuum equipment (TMP modules, gauges, DTL tanks, piping systems)
- Precision mechanics (EOT cranes, rail systems, tank assemblies)
- Lasers & optics (coated lenses, mirrors)
- Utilities (chillers, UHP argon gas supply, axial fans)
- Safety equipment (cryogenic PPE)

## Adding New Equipment Types

The skill learns from new tenders. If your equipment type isn't listed above, the generation will still work — Gemini adapts the checklist to your equipment.

## Converting to Word (.docx)

Gemini outputs Markdown text. If you need a `.docx` file, install Pandoc and run:
```
pandoc filename.md -o filename.docx
```

## License

MIT
