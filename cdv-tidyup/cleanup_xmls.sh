#!/usr/bin/env bash
#
# Remove duplicate and stray BEAST XMLs from cdv-phylodynamics.
#
#   bash cleanup_xmls.sh --check    report only, delete nothing
#   bash cleanup_xmls.sh            delete
#
# Each duplicate is re-verified by checksum immediately before deletion. If a
# file is not what this script expects, it is left alone and reported. Nothing
# is deleted on the strength of an analysis done somewhere else at some other
# time.

set -uo pipefail

CHECK=0
VERB="remove  "
if [[ "${1:-}" == "--check" ]]; then
  CHECK=1
  VERB="would remove"
fi

if [[ ! -d beast/clade3 ]]; then
  echo "run this from the cdv-phylodynamics repository root" >&2
  exit 1
fi

md5of() { md5sum "$1" 2>/dev/null | cut -d' ' -f1; }

removed=0
kept=0

# --- exact duplicates: delete the copy only if it still matches the original --
drop_if_duplicate() {
  local dup="$1" orig="$2"
  if [[ ! -f "$dup" ]]; then
    echo "  skip     $dup (already gone)"
    return
  fi
  if [[ ! -f "$orig" ]]; then
    echo "  KEEP     $dup — the original $orig is missing, so this may be the only copy"
    ((kept++)); return
  fi
  local a b; a=$(md5of "$dup"); b=$(md5of "$orig")
  if [[ "$a" == "$b" ]]; then
    echo "  duplicate of $orig  ($a)"
    if [[ $CHECK -eq 0 ]]; then git rm -q "$dup" 2>/dev/null || rm -f "$dup"; fi
    echo "  $VERB   $dup"
    ((removed++))
  else
    echo "  KEEP     $dup — no longer identical to $orig ($a vs $b); inspect by hand"
    ((kept++))
  fi
}

echo "Duplicate top-level copies:"
drop_if_duplicate "beast/clade3_5state.xml"      "beast/clade3/clade3_5state.xml"
drop_if_duplicate "beast/clade3_dta_nobssvs.xml" "beast/clade3/clade3_dta_nobssvs.xml"

# --- the corrupted filename ------------------------------------------------
# Not a byte-duplicate: it differs from beast/clade3/clade3_dta.xml only in the
# tree logger's logEvery (1000 vs 10000). No unique science, and the filename
# itself is a failed path join. Verify that characterisation before deleting.
echo
echo "Corrupted filename from a failed path join:"
STRAY="data/beast:clade3:clade3_dta.xml"
SIB="beast/clade3/clade3_dta.xml"
if [[ ! -f "$STRAY" ]]; then
  echo "  skip     $STRAY (already gone)"
elif [[ ! -f "$SIB" ]]; then
  echo "  KEEP     $STRAY — sibling $SIB missing; cannot confirm it is redundant"
  ((kept++))
else
  diffcount=$(diff <(tr '>' '\n' < "$STRAY") <(tr '>' '\n' < "$SIB") | grep -c '^[<>]')
  if [[ "$diffcount" -le 4 ]]; then
    echo "  differs from $SIB on $diffcount line(s) — tree logEvery only"
    if [[ $CHECK -eq 0 ]]; then git rm -q "$STRAY" 2>/dev/null || rm -f "$STRAY"; fi
    echo "  $VERB   $STRAY"
    ((removed++))
  else
    echo "  KEEP     $STRAY — differs from $SIB on $diffcount lines, more than expected."
    echo "           Inspect before deleting; it may contain something unique."
    ((kept++))
  fi
fi

# --- confirm the canonical files are untouched ------------------------------
echo
echo "Canonical analysis (must survive):"
CANON_A="beast/clade3/run100M_fixed/seed12345/clade3_5state_fixed.xml"
CANON_B="beast/clade3/run100M_fixed/seed54321/clade3_5state_fixed.xml"
for f in "$CANON_A" "$CANON_B"; do
  [[ -f "$f" ]] && echo "  present  $f  ($(md5of "$f"))" || echo "  MISSING  $f  <-- STOP"
done
if [[ -f "$CANON_A" ]]; then
  dir=$(grep -o 'traitname="date-[a-z]*"' "$CANON_A" | head -1)
  if [[ "$dir" == *"date-forward"* ]]; then
    echo "  ok       tip dates are $dir"
  else
    echo "  WARNING  tip dates are $dir — the canonical run must be date-forward"
  fi
fi

echo
if [[ $CHECK -eq 1 ]]; then
  echo "Check only. $removed file(s) would be removed, $kept kept for inspection."
  echo "Run without --check to apply."
else
  echo "Removed $removed file(s); kept $kept for inspection."
  echo "Review with 'git status', then commit."
fi
