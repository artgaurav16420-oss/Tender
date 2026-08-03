# Changelog

All notable changes to this repository. The authoritative skill-version log
remains in the `changelog:` frontmatter of `SKILL.md`; this file mirrors it at
repo level.

## 2026-08-02 — Skill v1.10 (tooling & automation)

- Added cross-platform sync scripts `scripts/sync.sh` / `scripts/sync.ps1` —
  one-command ADR-001 sync (UTF-8 normalization, copy directions, SHA256 +
  count verification; `--install` bootstraps the installed skill directory).
- Added automated verification: `scripts/verify_tender.sh` (generated tenders)
  and `scripts/verify_repo.sh` (repo integrity).
- Added GitHub Actions CI (`.github/workflows/ci.yml`) and
  `.markdownlint-cli2.yaml`.
- Added structured generation: `templates/tender-schema.json`,
  `templates/tender.example.json`, `scripts/validate_tender_json.py`,
  `scripts/render_tender.py`.
- Added `docs/standards-glossary.md`, `CONTRIBUTING.md`, `CHANGELOG.md`,
  `LICENSE`.
- Generalised the MarkItDown prerequisite path (no longer Windows-only).

## Skill v1.0 → v1.9

Mirrored from `SKILL.md` frontmatter — see the `changelog:` field there for
1.0 (2026-06-02) through 1.9 (2026-08-01).
