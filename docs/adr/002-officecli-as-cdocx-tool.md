# ADR-002: OfficeCLI as Canonical .docx Generation Tool

## Status
Accepted (2026-07-31)

## Context
The skill originally specified `pandoc` for Markdown → .docx conversion in the Post-Generation Verification step (SKILL.md line 136-140), while the Quick Start (step 6) already mandated `officecli` with the RRCAT template (`_template.docx`). This contradiction caused confusion and produced malformed documents when users followed the pandoc path.

RRCAT tenders require precise formatting: specific fonts (Aptos Display/Aptos), page layout (2.54 cm margins), table styles (Table Grid with specific cell margins), paragraph styles (Heading1, Heading3, FirstParagraph, Body Text, Compact, Block Text), bold text rules, merged header rows in compliance tables, and section header formatting. Pandoc cannot preserve these Word-specific styles and layout settings.

OfficeCLI operates directly on the .docx XML, allowing programmatic population of a pre-formatted template while preserving all styles, table formatting, and document properties.

## Decision
OfficeCLI is the **sole** tool for generating .docx output. All pandoc references are removed. The workflow is:

1. Copy `_template.docx` to output filename
2. Use `officecli set` to populate content (tables, headings, paragraphs, bold text)
3. Use `officecli close` to save
4. Use `officecli view outline` to verify structure

## Alternatives Considered
- **Keep both with user choice**: Rejected — pandoc output fails RRCAT formatting requirements; dual-path creates confusion.
- **Use python-docx**: Rejected — requires Python dependency; officecli is a single binary with no runtime dependencies.
- **Generate .docx from scratch via officecli**: Rejected — replicating the full template (styles, fonts, layout, table styles) programmatically is error-prone. Starting from a verified template is more reliable.

## Consequences
- Zero pandoc dependencies
- Generated .docx files are RRCAT-compliant by construction
- Template updates (e.g., font changes) only require replacing `_template.docx`
- Users must have officecli installed (available via npm/npx or as standalone binary)