# Contributing to the RRCAT Tender Skill

Thanks for contributing! This repo is a **document-generation skill**, not an
application codebase. Contributions improve the quality and defensibility of
generated RRCAT tender specifications.

## Ways to contribute

| Contribution | How | Process |
|---|---|---|
| **New tender example** (real RRCAT spec, PDF) | Drop the PDF in `Examples/` and run `/tender-learn` | Converts to `.md`, updates the Learned Pattern Library and Reference Examples in `SKILL.md` |
| **Checklist / output format change** | Propose via an Architecture Decision Record (ADR) | New `docs/adr/00X-*.md` following the existing ADR format; reference it from `SKILL.md` |
| **Scripts & tooling** | Fix or extend `scripts/`, `templates/`, CI | Keep zero-runtime-dependency (bash + Python stdlib); update docs that reference the scripts |
| **Docs** | README, glossary, ADRs, comments | Follow existing tone and structure |

## Prerequisites

- `officecli` (required for `.docx` generation): `officecli install`
- Python with `markitdown[all]` (only for `/tender-learn` PDF conversion):
  `pip install 'markitdown[all]'`

## Development workflow

1. Clone / open the workspace (Freebuff or GitHub).
2. Make your changes. **Do not edit `_template.docx` structure casually** — it
   is the formatting contract (see ADR-002).
3. Sync discipline (ADR-001): after any change, run the sync script from the
   repo root:
   - Linux/macOS/Git-Bash: `bash scripts/sync.sh` (first run:
     `bash scripts/sync.sh --install`)
   - Windows PowerShell:
     `powershell -ExecutionPolicy Bypass -File scripts/sync.ps1`
4. Validate before opening a PR (see checklist below).
5. Open a pull request through the Freebuff Changes panel or GitHub.

## PR checklist

- [ ] `bash scripts/verify_repo.sh` exits 0
- [ ] `bash scripts/verify_tender.sh <generated>.md` passes on any new generated
      example you include
- [ ] `npx markdownlint-cli2 "**/*.md"` reports no new violations
- [ ] New `Examples/*.md` files are UTF-8 (no BOM) and **referenced** in
      `SKILL.md` (Learned Pattern Library + Reference Examples)
- [ ] Pattern Library rows have all 6 columns
- [ ] Checklist / output-format changes include an ADR and are referenced from
      `SKILL.md`
- [ ] `SKILL.md` `changelog:` frontmatter and `CHANGELOG.md` updated for skill
      version bumps

## ADR process

Substantive decisions (output format, checklist changes, tooling direction)
follow the ADR pattern already used in `docs/adr/`:

1. New file `docs/adr/00X-<short-title>.md` with Status / Context / Decision /
   Alternatives Considered / Consequences.
2. Number sequentially after the highest existing ADR.
3. Reference it from the relevant `SKILL.md` section.

## Notes

- **Vendor neutrality:** never add brand-name-dependent language to the skill
  output (negative examples exist to be studied, not copied).
- **Zero assumptions:** every numeric value in generated tenders must come from
  the user. Recommended answers in the checklist are ranges/options, never
  silent defaults.
- The `scripts/brand-list.txt` wordlist is a heuristic for vendor-neutrality
  warnings — extend it as new examples are learned.
