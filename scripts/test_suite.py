#!/usr/bin/env python3
"""test_suite.py — unified quality-gate runner for the rrcat-tender repo.

Executes every quality gate in the repo in dependency order and prints a
[PASS]/[FAIL] line for each, exiting 0 only when ALL gates pass.

Gates (in order):
  1. python scripts/test_validate_template.py      — permanent regression tests (exit 0)
  2. python scripts/validate_template.py _template.docx — template structural validation (exit 0)
  3. python scripts/regression_test.py             — 22-example end-to-end regression (~3-5 min, 900s timeout)
  4. python scripts/tender_gen.py --equipment solar   --output <tmp>/suite_solar.docx   (exit 0 + 'RESULT: PASS')
  5. python scripts/tender_gen.py --equipment chiller --output <tmp>/suite_chiller.docx (exit 0 + 'RESULT: PASS')
  6. python scripts/tender_learn.py --dry-run Examples/Solar_PV_20kWp_Civil.md (exit 0 + 'DRY-RUN'; SKILL.md must NOT change)
  7. python scripts/sync_skill.py --dry-run        — sync plan without writing (exit 0)
  8. sha256(SKILL.md) before step 6 vs after step 7 must be identical; `git status --short`
     after the run must show no NEW entries vs the baseline captured at start
     (generated outputs live in a temp dir OUTSIDE the repo and are cleaned up).

Stdlib only (Python 3.11). No external dependencies.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
SKILL_MD = REPO / "SKILL.md"
PYTHON = sys.executable

# Per-step timeouts (seconds). Step 3 regression is the long pole (~3-5 min).
TIMEOUTS = {
    "test_validate_template": 300,
    "validate_template": 300,
    "regression_test": 900,
    "tender_gen_solar": 600,
    "tender_gen_chiller": 600,
    "tender_learn_dry_run": 300,
    "sync_skill_dry_run": 120,
}

passed = 0
failed = 0


def run(cmd, timeout, cwd=REPO):
    """Run a subprocess with captured utf-8 output; return (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or b""
        err = exc.stderr or b""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        return "TIMEOUT", out, err


def report(ok, name, detail):
    """Print a [PASS]/[FAIL] line and tally the result."""
    global passed, failed
    if ok:
        passed += 1
        print(f"[PASS] {name}: {detail}")
    else:
        failed += 1
        print(f"[FAIL] {name}: {detail}")


def check_rc(rc):
    """True if rc is the integer 0 (subprocess may return int only)."""
    return isinstance(rc, int) and rc == 0


def sha256(path):
    """Return hex sha256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def git_status():
    """Return the set of `git status --short` lines (relative to REPO)."""
    rc, out, err = run(["git", "status", "--short"], 60)
    if not check_rc(rc):
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


def main():
    baseline = git_status()

    # 1. Permanent regression tests for validate_template
    rc, out, err = run([PYTHON, str(SCRIPTS / "test_validate_template.py")], TIMEOUTS["test_validate_template"])
    report(check_rc(rc), "test_validate_template", f"rc={rc}")

    # 2. Template structural validation (_template.docx)
    rc, out, err = run([PYTHON, str(SCRIPTS / "validate_template.py"), "_template.docx"], TIMEOUTS["validate_template"])
    report(check_rc(rc), "validate_template", f"rc={rc}")

    # 3. Full regression over 22 examples (long-running)
    rc, out, err = run([PYTHON, str(SCRIPTS / "regression_test.py")], TIMEOUTS["regression_test"])
    report(check_rc(rc), "regression_test", f"rc={rc}")

    # 4-5. End-to-end generation for two equipment types; each output in its
    # own temp dir OUTSIDE the repo, removed immediately after the gate.
    for equipment, label in (("solar", "tender_gen_solar"), ("chiller", "tender_gen_chiller")):
        with tempfile.TemporaryDirectory(prefix="rrcat_suite_") as tmp:
            out_docx = Path(tmp) / f"suite_{equipment}.docx"
            rc, out, err = run(
                [PYTHON, str(SCRIPTS / "tender_gen.py"), "--equipment", equipment, "--output", str(out_docx)],
                TIMEOUTS[label],
            )
            ok = check_rc(rc) and "RESULT: PASS" in out
            report(ok, label, f"rc={rc}, 'RESULT: PASS'={'yes' if 'RESULT: PASS' in out else 'NO'}")

    # 6. tender_learn --dry-run: must mention DRY-RUN and MUST NOT modify SKILL.md
    before = sha256(SKILL_MD)
    rc, out, err = run(
        [PYTHON, str(SCRIPTS / "tender_learn.py"), "--dry-run", "Examples/Solar_PV_20kWp_Civil.md"],
        TIMEOUTS["tender_learn_dry_run"],
    )
    report(check_rc(rc) and "DRY-RUN" in out, "tender_learn_dry_run", f"rc={rc}, DRY-RUN={'yes' if 'DRY-RUN' in out else 'NO'}")

    # 7. sync_skill --dry-run: plan only, no writes
    rc, out, err = run([PYTHON, str(SCRIPTS / "sync_skill.py"), "--dry-run"], TIMEOUTS["sync_skill_dry_run"])
    report(check_rc(rc), "sync_skill_dry_run", f"rc={rc}")

    # 8a. SKILL.md must be byte-identical (sha256) after steps 6-7
    after = sha256(SKILL_MD)
    report(before == after, "SKILL.md_unchanged", "sha256 identical" if before == after else "sha256 CHANGED")

    # 8b. Repo must be free of NEW dirt vs the baseline (temp outputs are outside the repo)
    end_status = git_status()
    new_entries = sorted(end_status - baseline)
    report(not new_entries, "git_status_clean", "no new untracked/modified files" if not new_entries else f"new entries: {new_entries}")

    # Summary
    total = passed + failed
    print(f"\n=== SUMMARY: {passed}/{total} passed, {failed} failed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
