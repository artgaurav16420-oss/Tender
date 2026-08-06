#!/usr/bin/env python3
"""tender_gen.py - CLI wrapper that generates a filled tender .docx from the
rrcat-tender _template.docx.

Usage:
    python scripts/tender_gen.py --equipment "solar" --output out.docx
    python scripts/tender_gen.py --equipment "chiller" --output out.docx --answers answers.json

Flow:
  1. answers = questionnaire.get_answers(equipment)  (overridden by --answers)
  2. copy _template.docx -> output
  3. officecli dump output /body -> find every [CONFIRMED_*] occurrence
     (full text from dump; concrete paragraph paths from officecli query)
  4. build batch ops: set each placeholder paragraph's text (token replaced
     by answer value, with spacing fixups for template authoring artifacts)
  5. inject equipment-type defensive pattern clauses as new paragraphs
     immediately after the ISO certification line (BQC section)
  6. officecli batch --input <json> then officecli close
  7. verify via verify_generated.verify_document; print summary; exit 0/1
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import questionnaire  # noqa: E402
import verify_generated  # noqa: E402

DEFAULT_TEMPLATE = Path("D:/Software Development/rrcat-tender/_template.docx")
TOKEN_RE = re.compile(r"\[CONFIRMED_[A-Z_0-9]+\]")


def run_officecli(args):
    """Run officecli, return (returncode, stdout)."""
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout


def smart_replace(text, answers):
    """Replace [CONFIRMED_X] tokens with answer values, then fix the
    template's missing-space authoring artifacts (byte-verified: the template
    embeds tokens like 'minimumCONFIRMED_YEARSyears')."""
    def repl(m):
        token = m.group(0)
        name = token[1:-1]  # strip brackets
        return str(answers.get(name, token))

    out = TOKEN_RE.sub(repl, text)
    # spacing fixups for embedded tokens
    out = re.sub(r"(\d+ No)(sets|weeks|months)\b", r"\1 \2", out)  # "1 Nosets" -> "1 No sets"
    out = re.sub(r"(\d+)(sets|weeks|months)\b", r"\1 \2", out)     # "16weeks"  -> "16 weeks"
    out = re.sub(r"\b(minimum)\s*(\d+)\s*(years)\b", r"\1 \2 \3", out)   # "minimum3years"
    out = re.sub(r"\b(least)\s*(\d+)\s*(units)\b", r"\1 \2 \3", out)     # "least1units"
    out = re.sub(r"\b(ISO)\s*(\S+?)\s*(certification)\b", r"\1 \2 \3", out)  # "ISO9001:2015certification"
    return out


def query_token_paragraphs(docx_path):
    """Return list of (path, token_set) for every paragraph containing a
    [CONFIRMED_*] token, in document order."""
    rc, out = run_officecli(["officecli", "query", docx_path, "paragraph", "--find", "[CONFIRMED_", "--compact"])
    if rc != 0:
        raise RuntimeError(f"officecli query failed: {out[:300]}")
    items = []
    for line in out.splitlines():
        line = line.rstrip("\r")
        if line.startswith("total:"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        path = parts[0].strip()
        text = parts[2].strip('"')
        tokens = frozenset(TOKEN_RE.findall(text))
        if tokens:
            items.append((path, tokens))
    return items


def collect_dump_occurrences(dump_ops):
    """Return list of (full_text, tokens, is_add_op) in dump/document order,
    plus the index of the ISO certification paragraph op (for pattern
    injection)."""
    occurrences = []
    iso_op_index = None
    for i, op in enumerate(dump_ops):
        if not isinstance(op, dict):
            continue
        props = op.get("props") or {}
        text = props.get("text")
        if not isinstance(text, str):
            continue
        tokens = frozenset(TOKEN_RE.findall(text))
        if not tokens:
            continue
        is_add = op.get("command") == "add"
        occurrences.append((text, tokens, is_add))
        if "CONFIRMED_STANDARD" in text and not "CONFIRMED_STANDARD_REF" in text and "certification" in text:
            iso_op_index = len(occurrences) - 1
    return occurrences, iso_op_index


def generate(equipment, output, answers_json=None, template=DEFAULT_TEMPLATE):
    """Run the full generation flow. Returns (results, summary_dict)."""
    summary = {
        "output": str(output),
        "equipment": equipment,
        "answers_source": "defaults",
        "tokens_replaced": 0,
        "patterns_injected": 0,
        "batch_ok": False,
        "verification": None,
    }

    # 1. answers
    answers = questionnaire.get_answers(equipment)
    if answers_json:
        with open(answers_json, encoding="utf-8") as f:
            overrides = json.load(f)
        answers.update(overrides)
        summary["answers_source"] = answers_json
    type_key, patterns = questionnaire.detect_equipment_type(equipment)
    summary["type"] = type_key
    summary["patterns"] = patterns

    # 2. copy template (release any stale resident doc first, then fresh copy)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        run_officecli(["officecli", "close", str(output)])  # release resident handle
        output.unlink()
    shutil.copy2(template, output)

    # 3. dump the copy
    rc, out = run_officecli(["officecli", "dump", str(output), "/body"])
    if rc != 0:
        raise RuntimeError(f"officecli dump failed on copy: {out[:300]}")
    dump_ops = json.loads(out)

    occurrences, iso_op_index = collect_dump_occurrences(dump_ops)
    query_items = query_token_paragraphs(str(output))

    if len(occurrences) != len(query_items):
        raise RuntimeError(
            f"alignment mismatch: {len(occurrences)} dump occurrences vs "
            f"{len(query_items)} queried paragraphs"
        )

    # 4. build set ops (alignment: dump order == document order)
    batch_ops = []
    for (text, tokens, is_add), (path, qtokens) in zip(occurrences, query_items):
        if tokens != qtokens:
            raise RuntimeError(f"token mismatch at paragraph {path}: {tokens} vs {qtokens}")
        new_text = smart_replace(text, answers)
        if new_text == text:
            continue  # nothing to replace (shouldn't happen)
        batch_ops.append({"command": "set", "path": path, "props": {"text": new_text}})
        summary["tokens_replaced"] += len(tokens)

    # 5. inject equipment-type patterns after the ISO certification line
    if patterns and iso_op_index is not None:
        iso_path = query_items[iso_op_index][0]
        batch_ops.append({
            "command": "add",
            "parent": "/body",
            "after": iso_path,
            "type": "p",
            "props": {"style": "Body Text", "text": "\n".join(patterns)},
        })
        summary["patterns_injected"] = len(patterns)

    # 6. apply batch
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as tf:
        json.dump(batch_ops, tf, ensure_ascii=False)
        batch_file = tf.name
    try:
        rc, out = run_officecli(
            ["officecli", "batch", str(output), "--input", batch_file, "--json"]
        )
        if rc != 0:
            raise RuntimeError(f"officecli batch failed: {out[:600]}")
        parsed = json.loads(out)
        ok = parsed.get("success") is True
        summary["batch_ok"] = ok
        if not ok:
            raise RuntimeError(f"officecli batch reported failure: {out[:600]}")
    finally:
        Path(batch_file).unlink(missing_ok=True)

    # close (batch leaves doc resident)
    run_officecli(["officecli", "close", str(output)])

    # 7. verify
    results = verify_generated.verify_document(output, expected_patterns=patterns)
    summary["verification"] = results
    # leave no resident doc behind
    run_officecli(["officecli", "close", str(output)])
    return results, summary


def main():
    parser = argparse.ArgumentParser(description="Generate a filled RRCAT tender .docx")
    parser.add_argument("--equipment", required=True, help="equipment keyword, e.g. 'solar'")
    parser.add_argument("--output", required=True, help="output .docx path")
    parser.add_argument("--answers", default=None, help="optional answers JSON to override defaults")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="template docx (default _template.docx)")
    args = parser.parse_args()

    try:
        results, summary = generate(args.equipment, args.output, args.answers, args.template)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print("=== GENERATION SUMMARY ===")
    print(f"output: {summary['output']}")
    print(f"equipment: {summary['equipment']} (type: {summary['type']})")
    print(f"answers source: {summary['answers_source']}")
    print(f"placeholders replaced: {summary['tokens_replaced']}")
    print(f"defensive clauses injected: {summary['patterns_injected']}")
    print(f"batch applied: {'PASS' if summary['batch_ok'] else 'FAIL'}")
    print("=== VERIFICATION ===")
    verify_generated.print_results(results)

    if results["issues"]:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
