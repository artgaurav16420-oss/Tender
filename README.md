# RRCAT Tender Specification Generator

Generate procurement tender specifications for RRCAT, Indore, following Indian government open-tendering rules.

## How to Use

### Interactive (skill-loaded)
```bash
skill rrcat-tender
```
Then: "Generate a tender specification for [your equipment]"

### One-command CLI (direct)
```bash
cd D:/Software Development/rrcat-tender
python scripts/tender_gen.py --equipment "solar" --output out.docx
python scripts/tender_gen.py --equipment "chiller" --output out.docx --answers answers.json
```

### Scripts Reference

| Script | Purpose | Exact Command | Exit Codes |
|--------|---------|---------------|------------|
| `tender_gen.py` | Generate filled tender .docx | `python scripts/tender_gen.py --equipment "solar" --output out.docx` | 0=OK, 1=verification failed |
| `questionnaire.py` | Default answers + equipment detection | `python -c "import questionnaire; print(questionnaire.get_answers('solar'))"` | 0=OK |
| `tender_learn.py` | Learn from new PDF/MD | `python scripts/tender_learn.py Examples/new.pdf` or `--dry-run` | 0=OK |
| `sync_skill.py` | Sync workspace ↔ installed | `python scripts/sync_skill.py [--dry-run|--check]` | 0=in sync, 1=drift/mismatch |
| `validate_template.py` | Template structure check | `python scripts/validate_template.py _template.docx` | 0=valid |
| `verify_generated.py` | Post-generation verification | `python scripts/verify_generated.py out.docx` | 0=PASS |
| `regression_test.py` | 22-example full regression | `python scripts/regression_test.py` | 0=22/22 passed |
| `test_suite.py` | All gates single runner | `python scripts/test_suite.py` | 0=all PASS |
| `test_validate_template.py` | Template unit tests | `python scripts/test_validate_template.py` | 0=PASS |
| `test_questionnaire.py` | Detection/coverage tests | `python scripts/test_questionnaire.py` | 0=PASS |
| `test_learn_real_mode.py` | Reversible real-mode learning test | `python scripts/test_learn_real_mode.py` | 0=PASS |

### Quality Gates (run before presenting to user)
```bash
# Fast checks (CI: ~2 min)
python -m py_compile scripts/*.py
python scripts/test_questionnaire.py
python scripts/validate_template.py _template.docx
python scripts/sync_skill.py --dry-run
python scripts/tender_learn.py --dry-run Examples/Solar_PV_20kWp_Civil.md

# Full gates (regression + generation + learn + sync)
python scripts/test_suite.py

# Single gate
python scripts/regression_test.py          # 22-example full regression
python scripts/verify_generated.py out.docx  # Post-generation checks
python scripts/sync_skill.py --check       # Drift detection (CI gate)
```

### Learning new equipment types
```bash
# Dry-run (safe preview)
python scripts/tender_learn.py --dry-run Examples/new_tender.pdf

# Real mode (updates workspace SKILL.md, human review recommended)
python scripts/tender_learn.py Examples/new_tender.pdf

# With custom workspace (for testing)
python scripts/tender_learn.py --workspace /tmp/test_ws --output-skill /tmp/test_ws/SKILL.md Examples/new_tender.pdf

# Run reversible fixture test
python scripts/test_learn_real_mode.py
```

### Prerequisites
- Python 3.11
- officecli: `npm install -g officecli`
- MarkItDown (for /tender-learn): `pip install 'markitdown[all]'`

### Environment Variables (optional overrides)
```bash
RRCAT_SKILL_TARGET=...    # Installed skill directory for sync
RRCAT_OFFICECLI=...       # officecli executable path
RRCAT_MARKITDOWN=...      # markitdown executable path
```

## Tips for Best Results

- **Be specific with numbers** — capacity, pressure, temperature, dimensions, flow rate
- **Name the standards** — IS 2825, ASME Sec VIII, ISO 21029, etc.
- **Describe end-use clearly** — "For LN2 storage in cryogenic lab"
- **Mention operating conditions** — indoor/outdoor, ambient range, utilities
- **Specify safety requirements** — relief valves, emergency stop, PESO certification

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

```bash
python scripts/tender_learn.py Examples/your_new_tender.pdf
```

## Converting to Word (.docx)

Handled automatically by `tender_gen.py` using `officecli` and `_template.docx`.

## Running Quality Gates

```bash
# All gates (regression + generation + learn + sync)
python scripts/test_suite.py

# Fast checks only (no full regression)
python -m py_compile scripts/*.py
python scripts/test_questionnaire.py
python scripts/validate_template.py _template.docx
python scripts/sync_skill.py --dry-run
python scripts/tender_learn.py --dry-run Examples/Solar_PV_20kWp_Civil.md
```

## License

MIT