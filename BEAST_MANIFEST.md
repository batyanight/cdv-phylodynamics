# BEAST XML manifest

Which XML is which, and which one produced the published result.

Verified by md5 and by parsing each file for chain length, tip-date direction
and trait configuration — not from memory. Every claim below is checkable with
`md5sum` and `grep`.

---

## Canonical — the published analysis

```
beast/clade3/run100M_fixed/seed12345/clade3_5state_fixed.xml
beast/clade3/run100M_fixed/seed54321/clade3_5state_fixed.xml
```

`md5 272a3cdf` · 10⁸ states · `traitname="date-forward"` · 5 host states · no BSSVS

The two seed files are **byte-identical**; the seed is supplied on the command
line (`beast -seed ...`, see `run100M_fixed/run_all.sh`), not written into the
XML. That is expected, not a mistake.

Outputs: `run100M_fixed/clade3_mcc_fixed.tree`,
`run100M_fixed/combined_fixed.log`

**Everything reported in METHODS.md and the Nextstrain build comes from these.**

---

## Superseded — the inverted time axis

```
beast/clade3/run100M/seed12345/clade3_5state.xml
beast/clade3/run100M/seed54321/clade3_5state.xml
```

`md5 3ec1abc8` · 10⁸ states · `traitname="date-backward"`

Retained deliberately as a record of the error described in METHODS.md §9.5.

The entire difference from the canonical pair is **one attribute on one line**:

```diff
- <trait id="dateTrait.t:H_clade_3_5state" ... traitname="date-backward" ...>
+ <trait id="dateTrait.t:H_clade_3_5state" ... traitname="date-forward"  ...>
```

Nothing else differs — file lengths are 375796 and 375795 bytes. That single
attribute inverted every tip height and survived 10⁸ MCMC states without any
sampler diagnostic complaining, because the chain converged perfectly well on
the wrong model.

Its MCC tree, `run100M/clade3_mcc.tree`, is kept as a negative control. Running
`04b_temporal_signal.py` against it returns **FAIL** (non-positive root-to-tip
slope, date-shuffling p = 1.000), against **WEAK** with an implied root of
1975.5 for the corrected tree. Useful for testing any future check.

**Do not cite results from this run.**

---

## Date-randomisation test

```
beast/drt/H_clade_3_clean.xml                       md5 ad8b575e · 2×10⁷ states
beast/drt/date_randomised/H_clade_3_clean_drt1..20.xml   20 replicates
```

The formal temporal-signal test: the real clock-rate HPD must not overlap the
HPDs from the date-randomised replicates. METHODS.md §11 / DRT section.

---

## Exploratory — 10⁷ states, superseded, not cited

Kept for provenance. None of these produced a reported number.

| File | md5 | Chain | Notes |
|---|---|---|---|
| `beast/clade3/clade3_5state.xml` | `237fd6e4` | 10⁷ | `date-backward`; the pilot for the inverted run |
| `beast/clade3/clade3_5state_fixed.xml` | `ec0899d7` | 10⁷ | `date-forward`; pilot for the canonical run |
| `beast/clade3/clade3_dta.xml` | `8212e81f` | 10⁷ | BSSVS enabled |
| `beast/clade3/clade3_dta_final.xml` | `d15e8101` | 10⁷ | BSSVS |
| `beast/clade3/clade3_dta_merged.xml` | `6fc3ed7b` | 10⁷ | BSSVS |
| `beast/clade3/clade3_dta_nobssvs.xml` | `92d6b00e` | 10⁷ | BSSVS off |
| `beast/clade3/H_clade_3.xml` | `2c9d277f` | 10⁸ | sequence-only, no discrete trait |
| `beast/clade3/H_clade_3_dta.xml` | `0b474781` | 10⁶ | short trait pilot |

Despite the names, `clade3_dta_final.xml` and `clade3_dta_merged.xml` are **not**
the final analysis. The canonical files are the two at the top of this document.
The naming is a leftover from an earlier iteration and is why this manifest
exists.

---

## Deleted

| File | Why |
|---|---|
| `beast/clade3_5state.xml` | byte-identical to `beast/clade3/clade3_5state.xml` (`237fd6e4`) |
| `beast/clade3_dta_nobssvs.xml` | byte-identical to `beast/clade3/clade3_dta_nobssvs.xml` (`92d6b00e`) |
| `data/beast:clade3:clade3_dta.xml` | corrupted filename from a failed path join. Differs from `beast/clade3/clade3_dta.xml` only in tree-log frequency (`logEvery` 1000 vs 10000) — no unique science |

---

## Checking this manifest is still true

```bash
# canonical pair identical, and date-forward
md5sum beast/clade3/run100M_fixed/seed*/clade3_5state_fixed.xml
grep -o 'traitname="date-[a-z]*"' beast/clade3/run100M_fixed/seed12345/clade3_5state_fixed.xml

# superseded pair is the date-backward one
grep -o 'traitname="date-[a-z]*"' beast/clade3/run100M/seed12345/clade3_5state.xml
```

Before any future run, confirm `date-forward` **before** the chain starts. It is
a one-second check against a multi-day mistake, and it is the single cheapest
guard in this project.
