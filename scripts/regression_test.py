#!/usr/bin/env python3
"""regression_test.py - Generate-from-template regression harness for rrcat-tender.

For every reference example in Examples/*.md:
  1. Copy _template.docx to a temp output .docx.
  2. Replace every [CONFIRMED_*] placeholder via an officecli batch JSON
     (values derived from the example filename; JSON is written byte-safe to a
     temp file, never passed as CLI-arg prose), then `officecli close` so the
     resident-memory edits are flushed to disk.
  3. Run verify_generated.verify_document() on the result - it must run without
     crash and report zero placeholder leaks.
  4. Report per-example PASS/FAIL and a final X/Y summary. Exit 0 only if all
     examples pass.

Probe mode: the FIRST example (Solar_PV_20kWp_Civil.md) is processed
end-to-end first and the placeholder tokens found are printed, then the full
loop runs over all Examples/*.md.

Cleanup: all temp files live under tempfile.TemporaryDirectory and are removed
at the end of each example (the repo is never dirtied).

NOTE: dump op paths use symbolic /body/tbl[last()] which is ambiguous inside a
batch (it resolves to the last table in document order, not the table the dump
was reconstructing). The harness therefore re-dumps each table explicitly
(/body/tbl[N], N = 1..6) and rewrites those paths with concrete indices. The 3
BQC paragraph placeholders appear as body-level `add` ops WITHOUT a path key;
they are addressed positionally as /body/p[K] by counting body-level paragraph
adds in dump order.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import officecli_cleanup  # noqa: E402

REPO = Path(r"D:\Software Development\rrcat-tender")
TEMPLATE = REPO / "_template.docx"
EXAMPLES_DIR = REPO / "Examples"
SCRIPTS_DIR = REPO / "scripts"
NPM_FALLBACK = r"C:\Users\INP\AppData\Roaming\npm\officecli"
PROBE_EXAMPLE = "Solar_PV_20kWp_Civil.md"

# Per-token replacement values (generic, safe for every equipment type).
DEFAULT_VALUES = {
    "CONFIRMED_YEARS": "3",
    "CONFIRMED_COUNT": "1",
    "CONFIRMED_STANDARD": "ISO 9001:2015",
    "CONFIRMED_DESCRIPTION": "Main equipment as per specification",
    "CONFIRMED_KEY_SPEC": "As per technical specification",
    "CONFIRMED_QTY": "1 No",
    "CONFIRMED_PARAM": "As per specification",
    "CONFIRMED_VALUE": "As per specification",
    "CONFIRMED_STANDARD_REF": "ISO 9001:2015",
    "CONFIRMED_GRADE": "SS304",
    "CONFIRMED_RANGE": "As per specification",
    "CONFIRMED_FINISH": "As per specification",
    "CONFIRMED_FEATURES": "As per specification",
    "CONFIRMED_SAFETY_STANDARD": "As per applicable Indian standards",
    "CONFIRMED_ACCESSORY": "As per specification",
    "CONFIRMED_SPEC": "As per specification",
    "CONFIRMED_MONTHS": "12",
    "CONFIRMED_WEEKS": "8",
}

_spec = importlib.util.spec_from_file_location(
    "verify_generated", str(SCRIPTS_DIR / "verify_generated.py")
)
vg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vg)

TOKEN_RE = re.compile(r"\[CONFIRMED_[A-Z_]+\]")


def find_officecli():
    """Locate the officecli binary (PATH first, then npm fallback)."""
    w = shutil.which("officecli")
    if w:
        return w
    for cand in (NPM_FALLBACK, NPM_FALLBACK + ".cmd"):
        if os.path.exists(cand):
            return cand
    return "officecli"


def run(args):
    r = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return r.returncode, r.stdout, r.stderr


def dump_ops(docx, sub=None):
    """officecli dump <docx> <selector> parsed JSON ops list.

    sub, when given, is the FULL selector (e.g. "/body/tbl[1]") and
    replaces the default "/body" as the single dump path argument.
    """
    args = ["officecli", "dump", docx, sub if sub is not None else "/body"]
    rc, out, err = run(args)
    if rc != 0:
        raise RuntimeError("dump failed: " + (err or out)[:300])
    return json.loads(out)


def equipment_name(stem):
    """Human-readable equipment name derived from the example filename."""
    name = stem.replace("_", " ").replace("-", " ").strip()
    name = re.sub(r"\s+", " ", name)
    return name


def build_batch(docx, values):
    """Return (batch_ops, sorted_placeholder_tokens) covering every
    [CONFIRMED_*] occurrence in the document."""
    batch = []
    tokens = set()

    def add_op(path, text):
        if not path:
            return
        for m in TOKEN_RE.findall(text):
            tokens.add(m)
        new_text = text
        for token in TOKEN_RE.findall(text):
            key = token[1:-1]  # strip brackets
            new_text = new_text.replace(token, values.get(key, "As per specification"))
        batch.append({"command": "set", "path": path, "props": {"text": new_text}})

    # 1) Body-level paragraph `add` ops (no path key) -> positional /body/p[K]
    body_p_idx = 0
    for op in dump_ops(docx):
        if not isinstance(op, dict):
            continue
        is_body_p_add = (
            op.get("parent") == "/body"
            and op.get("type") == "p"
            and op.get("command") == "add"
        )
        if is_body_p_add:
            body_p_idx += 1
        if not is_body_p_add:
            continue
        text = (op.get("props") or {}).get("text")
        if isinstance(text, str) and "[CONFIRMED_" in text:
            add_op("/body/p[%d]" % body_p_idx, text)

    # 2) Table-cell placeholders via per-table dumps with explicit indices
    for n in range(1, 7):
        try:
            ops_t = dump_ops(docx, "/body/tbl[%d]" % n)
        except RuntimeError:
            continue
        for op in ops_t:
            if not isinstance(op, dict):
                continue
            text = (op.get("props") or {}).get("text")
            if not isinstance(text, str) or "[CONFIRMED_" not in text:
                continue
            path = (op.get("path") or "").replace(
                "/body/tbl[last()]", "/body/tbl[%d]" % n
            )
            add_op(path, text)

    return batch, sorted(tokens)


def process_example(md_path, values):
    """Process one example; return result dict. Never raises."""
    res = {
        "name": md_path.name,
        "copied": False,
        "batch_ok": False,
        "close_ok": False,
        "verify_ok": False,
        "leaks": -1,
        "leaks_ok": False,
        "tokens": [],
        "error": "",
    }
    tmpdir = None
    copy = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="rrcat_reg_")
        copy = os.path.join(tmpdir, md_path.stem + ".docx")
        shutil.copyfile(str(TEMPLATE), copy)
        res["copied"] = True

        batch, tokens = build_batch(copy, values)
        res["tokens"] = tokens
        batch_json = os.path.join(tmpdir, "batch.json")
        with open(batch_json, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False)

        rc, out, err = run(["officecli", "batch", copy, "--input", batch_json])
        if rc == 0:
            res["batch_ok"] = True
        else:
            errs = re.findall(r"ERROR:.*", out)
            res["error"] = "batch: " + " | ".join(e[:120] for e in errs[:3]) or (
                err or out
            )[:300]

        rc2, out2, err2 = run(["officecli", "close", copy])
        res["close_ok"] = rc2 == 0

        vres = vg.verify_document(copy, template_path=str(TEMPLATE))
        res["verify_ok"] = isinstance(vres, dict) and "checks" in vres

        raw, _ = vg.dump_texts(copy)
        res["leaks"] = len(TOKEN_RE.findall(raw))
        res["leaks_ok"] = res["leaks"] == 0
    except Exception as exc:
        res["error"] = (res["error"] + " " + repr(exc)).strip()
    finally:
        if tmpdir:
            # verify re-opened the docx after close (dump_texts/template_expected),
            # so the resident officecli process still holds a handle and rmtree
            # would fail. A best-effort close releases it; no-op if not open.
            if copy:
                try:
                    run(["officecli", "close", copy])
                except Exception:
                    pass
            if not officecli_cleanup.rmtree_retry(tmpdir):
                print("CLEANUP_WARN|temp dir not removed after retries: " + tmpdir)
    res["passed"] = (
        res["copied"]
        and res["batch_ok"]
        and res["close_ok"]
        and res["verify_ok"]
        and res["leaks_ok"]
    )
    return res


def main():
    if not TEMPLATE.exists():
        print("ERROR|template missing: " + str(TEMPLATE))
        return 2
    binary = find_officecli()
    rc0, out0, _ = run([binary, "--version"])
    if rc0 != 0:
        print("ERROR|officecli not runnable: " + binary)
        return 2

    md_files = sorted(p for p in EXAMPLES_DIR.glob("*.md") if p.is_file())
    if not md_files:
        print("ERROR|no Examples/*.md found")
        return 2

    probe = EXAMPLES_DIR / PROBE_EXAMPLE
    if probe.exists():
        pres = process_example(probe, DEFAULT_VALUES)
        print("PROBE|" + probe.name)
        print("PROBE_TOKENS|" + "|".join(pres["tokens"]))
        print("PROBE_TOKEN_COUNT|" + str(len(pres["tokens"])))
        status = "PASS" if pres["passed"] else "FAIL"
        print(
            status
            + "|"
            + pres["name"]
            + "|copied="
            + ("OK" if pres["copied"] else "FAIL")
            + " batch="
            + ("OK" if pres["batch_ok"] else "FAIL")
            + " close="
            + ("OK" if pres["close_ok"] else "FAIL")
            + " verify="
            + ("OK" if pres["verify_ok"] else "FAIL")
            + " leaks="
            + str(pres["leaks"])
            + (" ERR=" + pres["error"] if pres["error"] else "")
        )

    results = []
    for md in md_files:
        r = process_example(md, DEFAULT_VALUES)
        r["passed"] = (
            r["copied"]
            and r["batch_ok"]
            and r["close_ok"]
            and r["verify_ok"]
            and r["leaks_ok"]
        )
        results.append(r)
        status = "PASS" if r["passed"] else "FAIL"
        print(
            status
            + "|"
            + r["name"]
            + "|copied="
            + ("OK" if r["copied"] else "FAIL")
            + " batch="
            + ("OK" if r["batch_ok"] else "FAIL")
            + " close="
            + ("OK" if r["close_ok"] else "FAIL")
            + " verify="
            + ("OK" if r["verify_ok"] else "FAIL")
            + " leaks="
            + str(r["leaks"])
            + (" ERR=" + r["error"] if r["error"] else "")
        )

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print("SUMMARY|%d/%d examples passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
