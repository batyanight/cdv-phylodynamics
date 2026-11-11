# Plan: cdv-phylodynamics as a pathogen repo on top of wildphylo

Status: **phase 2 of the wildphylo restructuring, in progress on branch
`pathogen-repo`.** Decided 2026-11-10 by interview; see
`wildphylo/docs/PLAN-stages.md` for phase 1. wildphylo `v0.2.0` and `v0.2.1`
are pushed; the pin is `v0.3.0`.

## Decisions

| Question | Decision |
|---|---|
| Role of this repo | Dataset and analysis repo for CDV. The pipeline is wildphylo, installed as a dependency. |
| Published code | `v1.0.0` is the Zenodo release (2026-08-30). Three later commits (host table fix, BEAST manifest, staging cleanup) are untagged: tag HEAD `v1.0.1` before anything is removed, so the last state of the standalone pipeline is citable. |
| Dependency | `environment.yml` gets `pip: - "wildphylo @ git+https://github.com/batyanight/wildphylo@v0.3.0"`. Bumping the tag is a reviewed change. |
| Config home | `config/cdv.yaml` moves here from `wildphylo/config/pathogen/cdv.yaml`. wildphylo keeps `cdv-smoke` as a test fixture only. The three tables (`host_groups.tsv`, `lineage_references.tsv`, `vaccine_strains.txt`) are taken from wildphylo, whose copies are a superset of the ones here (jackals, bat-eared fox, a Cerdocyon misspelling, six reverse-genetics vaccine patterns). |
| Tracked files | wildphylo's audit-trail convention: provenance, accession snapshots, QC and temporal reports, clade summaries, the final BEAST XMLs for the published runs, build comparison, the served Auspice JSON. Crashed and previous runs, `.trees`, logs and processed FASTA go to a Zenodo deposit and are removed going forward; history is not rewritten. |
| Working files | `METHODS.md` and `BEAST_MANIFEST.md` stay. The notebook, `SETUP_MACOS.md` and `NEXT_PROJECTS.md` move to the vault. |
| Scripts | All removed. `11_annotate_H.py` and `cdv_h_coords.py` are the only CDV-specific analysis code; their lint-cleaned versions are in wildphylo history (commit `0a4b5e4^`) and come back here under `analysis/` once the annotate step is reworked against `locus.coordinate_reference`. |
| Nextstrain entry | Unchanged until a new `auspice/cdv-phylodynamics.json` is pushed to `main`. The regenerated dataset must pass `wildphylo gates compare` against the served one first. |

## Target layout

```
config/cdv.yaml                    the pathogen config (from wildphylo)
config/host_groups.tsv             (from wildphylo)
config/lineage_references.tsv
config/vaccine_strains.txt
auspice/cdv-phylodynamics.json     the served dataset; written by `wildphylo publish dataset`
builds/cdv/<YYYYMMDD>/             audit trail per build (provenance, checks, qc, temporal, clades, build_comparison)
beast/clade3/run100M_fixed/        the published runs' XMLs and manifest only
analysis/                          CDV-specific post-processing (H annotation), later
environment.yml                    conda env with wildphylo pinned by tag
conda-lock.yml
Snakefile                          thin: `include` wildphylo's workflow with this config
README.md, METHODS.md, BEAST_MANIFEST.md, CITATION.cff, LICENSE, GLOSSARY.md (links to wildphylo's)
```

## Verified against wildphylo `stage-cli`

- The Snakefile runs from outside its checkout: from a directory holding only
  `config/cdv.yaml` and the three tables,
  `snakemake -s ~/wildphylo/workflow/Snakefile --configfile config/cdv.yaml -n`
  resolves the 9-job CDV DAG, `builds/` lands under the current directory, and
  `wildphylo config validate config/cdv.yaml` passes. No wildphylo change needed.
- Still open: `wildphylo publish dataset` is not wired into the Snakefile. The
  wrapper here can call it directly with `--pathogen-repo .` after
  `gates compare`, or wildphylo grows `nextstrain.publish.pathogen_repo`.

## Order of work

1. Tag `v1.0.1` here. Create the Zenodo deposit for the BEAST runs that leave git.
2. wildphylo: tag `v0.2.0` (done; pin is now `v0.2.1`); confirm the Snakefile runs against a config outside its checkout.
3. Move `cdv.yaml` and the tables here; `wildphylo config validate config/cdv.yaml`.
4. `environment.yml` + lock with the pinned wildphylo; `Snakefile` wrapper; dry run.
5. Remove scripts, data/processed, crashed and previous BEAST runs, working files; update README and CITATION (new version, pipeline citation).
6. Full build; `wildphylo gates compare` against the served dataset; publish only on `ok`.
7. Add a scheduled-rebuild workflow here (monthly `wildphylo publish check-updates`
   then the build, as wildphylo's `rebuild.yml` did for CDV; wildphylo's own
   scheduler now skips smoke configs and defaults to btv).
8. Run the two outstanding analyses (date randomisation, asymmetric trait model) through wildphylo's gates.

## Decisions settled before the full build (2026-11-11)

All four open items are resolved. The configs and METHODS carry the
resolutions; this section records what was decided and why.

- **Host states.** `hosts.dta_states` now declares the same five states the
  published run used — `procyonid`, `wild_canid`, `mustelid`, `wild_felid`,
  `domestic_dog` — each mapped to itself, and leaves `ailurid` unmapped.
  Two findings drove it. First, the config's `domestic_cat: felid` entry was
  dead: `config/host_groups.tsv` files domestic cat under `other`, so no rule
  produces `domestic_cat` and nothing in any run ever pooled domestic with
  wild felids. wildphylo `validate` now warns on such a key (that is what
  v0.2.1 adds). Second, the published run's "five states with wild_felid and
  ailurid merged" was a relabelling of one tip: MK487378 is *Ailurus fulgens*,
  a red panda, carried in the XML as `wild_felid`. A rebuild instead enters it
  as `?`, ambiguous across all five states, which keeps the tip in the tree
  and the model at five dimensions without asserting a felid observation that
  was never made. `gates compare` against the served dataset will differ on
  that one tip's host state, and on nothing else in the trait block. The `?`
  route has not been run against the BEAST crash that forced the original
  merge, so watch the first 10⁶ states of a rebuild.
  The state name `felid` is gone: the served Auspice dataset colours by the
  raw groups, so `wild_felid` keeps a rebuild's colouring comparable.
- **CDS bounds.** `[21, 1844]` spans the right 1824 nt but numbers the H CDS
  from the first base of the H *gene* feature. AF164967.1 (15690 bp) has gene
  H at 7059..9004 and CDS H at 7079..8902, so the config now carries
  `[7079, 8902]`, which is what `locus.coordinate_reference.cds` claims to
  hold: the CDS in the reference record's own numbering. The 1..1824 numbering
  in the served Auspice JSON is an alignment coordinate and a third system;
  the glossary says so. Only the validator reads these numbers today, so the
  reworked annotate step would have been the first thing to notice, by about
  7 kb.
- **METHODS §9.5.** Reworded. `beast xml` writes `traitname="date-forward"` as
  a fixed value and asserts nothing; the inversion detector in
  `gates temporal` needs a time-scaled tree, so it cannot fire on the
  pre-BEAST ML tree, which is in substitutions per site. Running the gate on
  the MCC tree is manual and no rule does it.
- **Reference anchors.** Confirmed: nothing fetches them. `fetch records`
  downloads whatever the taxon query returns, and `curate metadata` flags the
  records whose accession matches a nucleotide row of
  `config/lineage_references.tsv`. A missing one is a log warning, not an
  error. METHODS now says so. Three of the eight nucleotide references are the
  US patent 8647637 panel and the fetch filter is `NOT patent[Title]`, so
  check the "reference anchors not present in ..." warning on the first full
  build.

## Open

- **`wildphylo publish dataset` is not wired into the Snakefile.** It needs a
  config key for the pathogen repo path. The wrapper here can call it directly
  with `--pathogen-repo .` after `gates compare`, or wildphylo grows
  `nextstrain.publish.pathogen_repo`. An interface decision, so it waits.
- **A missing lineage reference is only a warning.** Making it fail the build,
  or checking `references.expected_lineages` in curate, is a wildphylo feature
  change and an interface decision.
- **Zenodo deposit.** Built and waiting to upload:
  `~/zenodo-cdv-phylodynamics-20261111/` holds the archive (38 files, 9.6 MB
  packed), a SHA-256 manifest, the metadata in Zenodo's API shape, and
  `README-upload.md` with both routes and the exact sequence afterwards. No
  `.trees` or `.state` files survive on disk, so the deposit is logs, the
  superseded XMLs, the erroneous `run100M`, the published run's posterior logs
  and `data/processed`.
  Nothing is removed from tracking yet, deliberately: METHODS §9.5 says both
  the erroneous and the corrected outputs are retained in the repository, so
  the removal and the DOI belong in one commit. Uploading needs your account.
- **Vault moves**: done 2026-11-11. `SETUP_MACOS.md` and `NEXT_PROJECTS.md`
  are in `~/batyas_vault/Bioinformatics/`, the exploration notebook in
  `~/batyas_vault/Bioinformatics/CDV phylodynamics/`. The folder is new; move
  it if the vault grows a better home, but keep the three together.
- **Scheduled rebuild workflow** here, and `conda-lock` against the pinned
  `v0.2.1`.
