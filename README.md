# CDV Phylodynamics

**Question:** How have canine distemper virus lineages moved between domestic dogs and wild carnivore hosts, and is host-jump history associated with variation at the hemagglutinin receptor-binding interface?

Reproducible analysis of publicly available CDV sequence data. All data from GenBank; no restricted or unpublished material.

---

## Status

- [x] Phase 1 — repo, environment, fetch + curation scripts
- [ ] Phase 2 — data pull and human review of ambiguous records
- [ ] Phase 3 — alignment, ML phylogeny, reproduce-published-result check
- [ ] Phase 4 — BEAST2 phylodynamics, HyPhy selection analysis
- [ ] Phase 5 — pipeline packaging, preprint

## Quick start

```bash
conda env create -f environment.yml
conda activate cdv-phylo

# see how many records match before committing to a download
python scripts/01_fetch_sequences.py --email you@example.com --dry-run

# full pull (a few minutes with an API key)
python scripts/01_fetch_sequences.py --email you@example.com --api-key $NCBI_API_KEY

# parse, normalize, filter
python scripts/02_curate_metadata.py --gb data/raw/cdv_YYYYMMDD.gb

# --- after you've worked through needs_review.tsv ---

# relabel + align, then STOP and look at the alignment
python scripts/03_align_and_tree.py \
    --fasta data/processed/sequences_H.fasta \
    --metadata data/processed/metadata_clean.tsv \
    --stop-after align

# happy with it? build the tree
python scripts/03_align_and_tree.py \
    --fasta data/processed/sequences_H.fasta \
    --metadata data/processed/metadata_clean.tsv
```

Get a free NCBI API key at https://www.ncbi.nlm.nih.gov/account/ — it triples the download rate limit.

## Scripts

| Script | Does |
|---|---|
| `01_fetch_sequences.py` | Pulls all CDV nucleotide records (taxid 11232) from GenBank. Batched, retries on failure, caches by date, safe to re-run. |
| `02_curate_metadata.py` | Parses records; normalizes host names to functional groups; flags vaccine strains; parses collection dates to decimal years; extracts H gene sequences; writes exclusion log and a human-review queue. |
| `03_align_and_tree.py` | Relabels tips for BEAST/TempEst, aligns with MAFFT, optional trimAl, ML tree in IQ-TREE with ModelFinder + UFBoot + SH-aLRT, writes a TempEst date file. |

## Notebook

`notebooks/01_explore_dataset.ipynb` — interactive companion for reviewing ambiguous
records, plotting dataset composition, and making the scope decision. It **imports**
the functions from `scripts/` rather than duplicating them, so there is one source of
truth. Pipeline logic belongs in `scripts/`; the notebook is for looking and deciding.

```bash
pip install jupyterlab matplotlib
jupyter lab notebooks/01_explore_dataset.ipynb
```

## Config — edit these, they are the scientific choices

| File | Purpose |
|---|---|
| `config/vaccine_strains.txt` | Patterns identifying vaccine and vaccine-derived sequences. **Vaccine strains will corrupt a phylodynamic analysis.** The list is a starting point — also check for sequences clustering with the vaccine clade in your first ML tree and add what you find. |
| `config/host_groups.tsv` | Maps GenBank `/host` strings to canonical taxa and functional groups. Order matters: first match wins, so "raccoon dog" sits above "dog". |

## The loop you'll actually run

1. Run `02_curate_metadata.py`
2. Open `data/interim/needs_review.tsv`
3. For each ambiguous record: add a pattern to `host_groups.tsv`, or accept the exclusion
4. Re-run. Repeat until what remains is genuinely unusable.

This is the human-judgment step. It sets dataset quality and can't be automated away.

## Outputs

```
data/interim/metadata_all.tsv      every record parsed, nothing dropped
data/interim/needs_review.tsv      ambiguous — review by hand
data/interim/exclusions.tsv        what was excluded and why
data/processed/metadata_clean.tsv  analysis-ready
data/processed/sequences_H.fasta   H gene sequences
```

## Reproducibility notes

- GenBank changes. Downloads are stamped by date and accompanied by an accession list; never overwrite a previous pull.
- Every exclusion is logged with a reason. The exclusion log is part of the methods.
- Sanity check the vaccine filter with `--keep-vaccines` on a test run to confirm it catches what it should.

## Scope

Ideas that are not this project live in `NEXT_PROJECTS.md` and stay there.

## Key references

- Seimon TA, Miquelle DG, Chang TY, Newton AL, Korotkova I, Ivanchuk G, Lyubchenko E, Tupikov A, Slabe E, McAloose D (2013). Canine distemper virus: an emerging disease in wild endangered Amur tigers (*Panthera tigris altaica*). *mBio* 4(4):e00410-13.
- Gilbert M et al. (2020). Distemper, extinction, and vaccination of the Amur tiger. *PNAS* 117:31954–31962.
- Quigley KS et al. (2010). Morbillivirus infection in a wild Siberian tiger in the Russian Far East. *J Wildl Dis* 46:1252–1256.
