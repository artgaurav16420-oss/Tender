# ADR-001: Sync Direction for Examples Between Workspace and Installed Skill

## Status
Accepted (2026-05-25)

## Context
The skill repository exists in two locations:
- **Workspace**: `C:\Users\INP\Desktop\rrcat-tender\` (working copy with PDFs and generated `.md` files)
- **Installed skill**: `~/.agents/skills/rrcat-tender/` (loaded by OpenCode sessions)

The `SKILL.md` originally contained two sync procedures that specified **opposite** file-copy directions for `Examples/*.md`:
- General Sync (line 149): installed → workspace
- Auto-Learn Sync (line 419): workspace → installed

This contradiction could cause data loss — newly converted `.md` files from PDFs would be overwritten by stale installed copies.

## Decision
The canonical direction for `Examples/*.md` is **workspace → installed**:

1. PDFs live in workspace `Examples/`
2. `markitdown` converts PDF → `.md` in workspace
3. Sync copies workspace `.md` → installed skill
4. `SKILL.md` direction: installed → workspace (skill definition authored at installed location)

## Alternatives Considered
- **installed → workspace**: Rejected because markitdown runs in workspace and generates `.md` there. Copying installed → workspace would overwrite newly generated files.
- **Bidirectional (smart merge)**: Rejected — no merge tooling available, adds complexity with no clear benefit for this doc-only repo.
- **Remove sync entirely, use symlink**: Rejected — Windows symlinks are fragile, and the skill must work offline.

## Consequences
- Sync is now a single unambiguous step: workspace → installed for Examples.
- The duplicate General Sync section was removed (T-001).
- A UTF-8 normalization step (T-003) is inserted between conversion and sync to prevent encoding issues.

## Related Tasks
- T-001: Fix sync direction contradiction
- T-003: Add UTF-8 normalization step
