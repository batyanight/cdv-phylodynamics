# Next steps

Written 2026-11-11, at the point where both repos stop and wait for you.
This is the running order; the reasoning behind each item is in
`docs/PLAN-pathogen-repo.md` and `~/wildphylo/docs/PLAN-stages.md`.

State as of writing: wildphylo `main` is pushed with tags `v0.2.0`, `v0.2.1`
and `v0.3.0`. This repo's work is on branch `pathogen-repo`, 18 commits, **not
pushed**. The served dataset at nextstrain.org is untouched and stays that way
until step 6.

---

## 1. Upload the Zenodo deposit

Everything is built and waiting in `~/zenodo-cdv-phylodynamics-20261111/`:
the archive, a SHA-256 manifest, the metadata in Zenodo's API shape, and
`README-upload.md` with the browser route, the API route and the archive's
checksum.

Reserve the DOI before publishing the deposit, so it can go into the same
commit as step 2.

## 2. Stop tracking what the deposit now holds

One commit, after the DOI exists, in this order:

1. Put the DOI in `METHODS.md` where §9.5 says both the erroneous and the
   corrected outputs are retained in the repository, and in `README.md`.
2. `git rm -r --cached` the paths in `~/zenodo-cdv-phylodynamics-20261111/files.txt`.
   They stay on disk, and they stay in git history: history is not rewritten.
3. Add them to `.gitignore`.
4. Set `version` and `date-released` in `CITATION.cff` to this release, and add
   the dataset DOI as a related identifier.

The order matters only in that METHODS must not describe files the same commit
removes.

## 3. Set the repository secrets

`NCBI_EMAIL` and `NCBI_API_KEY`, on this repository, under Settings → Secrets
and variables → Actions. Without them `.github/workflows/rebuild.yml` fails at
its first step on the 2nd of the month.

## 4. Run the full build

BEAST belongs on real hardware, not a runner. From a clean environment:

```bash
conda-lock install --name cdv-phylo conda-lock.yml
conda activate cdv-phylo
caffeinate -i snakemake --configfile config/cdv.yaml --cores 8
```

Two things to watch:

- **The first 10⁶ states of each chain.** The host map now leaves `ailurid`
  unmapped, so the red panda tip enters the discrete trait as `?` rather than
  being relabelled `wild_felid` as the published run did. That avoids
  asserting an observation nobody made, but it has never been run against the
  crash in `AncestralStateTreeLikelihood.redrawAncestralStates` that forced
  the original merge. If it crashes the same way, the fallback is a
  `dta_states` entry mapping `ailurid` to its own state and accepting the
  extra rates, or the published relabelling with that choice written down.
- **The "reference anchors not present in ..." warning** from
  `curate metadata`. Three of the eight nucleotide references are the US
  patent 8647637 panel and the fetch filter is `NOT patent[Title]`, so a
  missing lineage name points there first.

## 5. Compare against the served dataset

```bash
wildphylo gates compare --pathogen cdv --builds-dir builds/cdv --out comparison.md
```

Expect exactly one intended difference in the trait block: MK487378's host
state. Anything else — a lost sequence, a moved TMRCA, a changed gate verdict
— is a regression until explained. `METHODS.md` §9.5 records the one expected
difference; if the comparison surfaces others, they belong in METHODS too
before anything is published.

## 6. Publish, which is the only step the world sees

Only on a clean comparison, and only by your own push: merge `pathogen-repo`
into `main` and push, with the new `auspice/cdv-phylodynamics.json`.
nextstrain.org/community/batyanight/cdv-phylodynamics serves that file from
`main`, so this is the moment the entry changes. Nothing automated touches it.

## 7. The two outstanding analyses

Both were deferred before the restructuring and both now have pipeline
support:

- **Date randomisation.** `wildphylo beast xml --randomize-dates N` and the
  `drt_run` rule. The flag had never parsed before 2026-11-11, so no replicate
  has ever run through the pipeline.
- **Asymmetric trait model.** `beast.discrete_trait.symmetric: false`, which
  doubles the rate count. `wildphylo config validate` reports the new rate
  count, and the trait-signal gate is the thing to read before trusting it.

## 8. Interface decisions, when you want them

These wait on your approval because they change an interface, not an
implementation:

- **`publish dataset` is not wired into the Snakefile.** Either this repo's
  wrapper calls it with `--pathogen-repo .` after the comparison, or wildphylo
  grows a `nextstrain.publish.pathogen_repo` key.
- **A missing lineage reference is a warning.** It could fail the build, or
  `references.expected_lineages` could be checked in `curate metadata`.
- **`11_annotate_H.py` and `cdv_h_coords.py` come back under `analysis/`**
  once the annotate step is reworked against `locus.coordinate_reference`,
  whose CDS bounds are now the verified genome-relative pair `[7079, 8902]` in
  AF164967.1. The old code assumed a different coordinate system, so it cannot
  be restored unchanged.

---

## On the wildphylo side

Recorded in `~/wildphylo/docs/PLAN-stages.md`; none of it blocks this repo.

- **`drt_run` writes BEAST's posterior log into the working directory**, so a
  chain started from a repo root drops `H_*_drt<N>.log` beside the Snakefile.
  Gitignored, which is a plaster. Relevant to step 7.
- **A smoke fixture that rule `all` can finish** would need chain lengths
  short enough to run, which would then trip the convergence gate on ESS.
- **`beast.py` is about 2000 lines** and is the next consolidation target.
