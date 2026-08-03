#!/usr/bin/env bash
# Verify a generated RRCAT tender Markdown file against the machine-checkable
# items of the Post-Generation Verification checklist in SKILL.md.
#
# Usage:  bash scripts/verify_tender.sh <tender.md>
# Exit codes: 0 = PASS, 1 = FAIL (must fix), 2 = PASS with warnings
#
# Optional: BRAND_LIST=/path/to/list to override the brand wordlist.
set -u

FILE="${1:?usage: verify_tender.sh <tender.md>}"
[ -f "$FILE" ] || { echo "FAIL: file not found: $FILE"; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

FAILS=0
WARNS=0
fail() { echo "FAIL: $*"; FAILS=$((FAILS+1)); }
warn() { echo "WARN: $*"; WARNS=$((WARNS+1)); }

# 1. Placeholder gate
PLACEHOLDERS=$(grep -Eo '\[CONFIRMED[^]]*\]|\[XXX\]|\{\{[^}]+\}\}|\[DD/MM/YYYY\]' "$FILE" | sort -u | tr '\n' ' ')
if [ -n "$PLACEHOLDERS" ]; then
  fail "placeholders remain: $PLACEHOLDERS"
fi

# 2. TBD / To Be Confirmed (warn — allowed only as the documented fallback)
if grep -Eq 'TBD|To Be Confirmed by RRCAT' "$FILE"; then
  warn "'TBD' / 'To Be Confirmed by RRCAT' present (allowed only as documented fallback)"
fi

# 3. Seven sections present and in order
found=0
prev=-1
while IFS=: read -r ln rest; do
  found=$((found+1))
  if [ "$ln" -le "$prev" ]; then fail "section order problem around line $ln: $rest"; fi
  prev=$ln
done < <(grep -nE '^### (1\. Scope of Supply|2\. Bidder Qualification Criteria|3\. Technical Requirements|4\. Bid Evaluation Criteria|5\. Acceptance Criteria:?|6\. Delivery Terms:?|7\. Vendor Compliance Sheet)' "$FILE")
if [ "$found" -ne 7 ]; then fail "expected exactly 7 section headings, found $found"; fi

# 4. Compliance sheet requirements
grep -q "Instructions:" "$FILE" || fail "compliance sheet missing 'Instructions:'"
grep -q "'Yes/No/Complied' NOT ALLOWED" "$FILE" || fail "missing 'Yes/No/Complied' NOT ALLOWED"
grep -q "Vendor Compliance" "$FILE" || fail "missing 'Vendor Compliance' column"
for sig in "Signature of Bidder" "Name & Designation" "Company Seal" "Date" "Place"; do
  grep -q "$sig" "$FILE" || fail "signature block missing: $sig"
done

# 5. Sr. No. sequence in the compliance table (1..N, no gaps)
# Only lines after the compliance header and before the signature block count.
numbers=$(awk '/Vendor Compliance/{f=1} f && /^\| *[0-9]+ *\|/{gsub(/^\| */, ""); gsub(/ *\|.*/, ""); print} /Signature of Bidder/{f=0}' "$FILE")
if [ -z "$numbers" ]; then
  fail "no numbered compliance rows found"
else
  expect=1
  seq_ok=1
  for n in $numbers; do
    if [ "$n" -ne "$expect" ]; then fail "Sr. No. sequence: expected $expect, found $n"; seq_ok=0; break; fi
    expect=$((expect+1))
  done
  [ "$seq_ok" = 1 ] && echo "ok: Sr. No. sequence 1..$((expect-1))"
fi

# 6. Tender ref format
grep -Eq 'RRCAT/[0-9]{4}/PUR/[0-9]{3}' "$FILE" || fail "Tender Ref not in RRCAT/YYYY/PUR/XXX format"

# 7. Vendor neutrality (warn only — heuristic)
BRANDS="${BRAND_LIST:-$SCRIPT_DIR/brand-list.txt}"
if [ -f "$BRANDS" ]; then
  while IFS= read -r b; do
    [ -z "$b" ] && continue
    case "$b" in \#*) continue;; esac
    if grep -qi "$b" "$FILE"; then warn "possible brand name: $b"; fi
  done < "$BRANDS"
fi

# 8. SI units (warn only)
if grep -Eq '[0-9] *psi\b' "$FILE" && ! grep -Eq 'MPa|[0-9] *bar\b' "$FILE"; then
  warn "imperial 'psi' without SI equivalent (bar/MPa)"
fi
if grep -Eq '[0-9] *°F\b' "$FILE" && ! grep -Eq '°C' "$FILE"; then
  warn "'°F' without '°C' equivalent"
fi

echo "---"
if [ "$FAILS" -gt 0 ]; then echo "RESULT: FAIL ($FAILS fail, $WARNS warn)"; exit 1; fi
if [ "$WARNS" -gt 0 ]; then echo "RESULT: PASS with warnings ($WARNS)"; exit 2; fi
echo "RESULT: PASS"
exit 0
