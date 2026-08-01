# Tender Skill — Agent Instructions

This is a **document-generation skill** repo, not a codebase. No build, test, lint, or CI commands exist.

## Purpose

Generate procurement tender specifications for RRCAT (Raja Ramanna Centre for Advanced Technology), Indore following government open-tendering rules.

## Sources of Truth

- **`SKILL.md`** — canonical skill definition. Read this first.
- **`docs/adr/`** — architecture decision records.
- **`Examples/*.md`** — text-extracted tender specs (AI-readable reference).

## Installed Skill

The skill is installed at `~/.agents/skills/rrcat-tender/`. Any OpenCode session can load it via `skill rrcat-tender` or it will auto-match when you mention RRCAT tenders.

## Sync Direction (critical — ADR-001)

Sync after every operation. Direction differs by file type:

- `SKILL.md` → **installed → workspace** (skill definition authored at installed location)
- `Examples/*.md` → **workspace → installed** (markitdown generates `.md` in workspace; reverse would overwrite new conversions)
- **UTF-8 normalization** required before sync to prevent encoding issues:
  ```powershell
  Get-ChildItem Examples/*.md | ForEach-Object {
      $c = [System.IO.File]::ReadAllText($_.FullName)
      [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
  }
  ```

## Core Workflow

1. **Read `SKILL.md`** before generating any document.
2. **Follow the Mandatory Review Checklist** in `SKILL.md` — do NOT generate until all items confirmed.
3. Output a Markdown document following the **7-section structure** defined in `SKILL.md`.
4. Run **Post-Generation Verification** checklist in `SKILL.md` before presenting.
5. Build the `.docx` with **officecli** from `_template.docx` (do NOT use pandoc — see ADR-002).

> All behavioral rules, constraints, boilerplate, and templates are in `SKILL.md` — this file is just a quick reference.

## Auto-Learn Command (`/tender-learn`)

Drop a new RRCAT tender PDF into `Examples/` and run `/tender-learn`. The agent will:
1. Convert the PDF to searchable `.md` in `Examples/`
2. Extract BQC style, table format, and notable clauses
3. Add a row to the **Learned Pattern Library** in `SKILL.md`
4. Update the Reference Examples list

Over time, the skill learns from every new tender and improves future generation quality.

## Example Reference

`Examples/*.md` are real RRCAT specs (PDFs are not currently bundled in the repo). Use the `.md` files for AI-readable content during generation.
