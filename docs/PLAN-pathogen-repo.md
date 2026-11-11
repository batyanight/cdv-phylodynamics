# Plan: cdv-phylodynamics as a pathogen repo on top of wildphylo

Status: **draft, phase 2 of the wildphylo restructuring.** Decided 2026-11-10
by interview; see `wildphylo/docs/PLAN-stages.md` for phase 1. Starts once
wildphylo tags `v0.2.0`.

## Decisions

| Question | Decision |
|---|---|
| Role of this repo | Dataset and analysis repo for CDV. The pipeline is wildphylo, installed as a dependency. |
| Published code | `v1.0.0` is the Zenodo release (2026-08-30). Three later commits (host table fix, BEAST manifest, staging cleanup) are untagged: tag HEAD `v1.0.1` before anything is removed, so the last state of the standalone pipeline is citable. |
| Dependency | `environment.yml` gets `pip: - "wildphylo @ git+https://github.com/batyanight/wildphylo@v0.2.0"`. Bumping the tag is a reviewed change. |
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
builds/<YYYYMMDD>/                 audit trail per build (provenance, checks, qc, temporal, clades, build_comparison)
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
2. wildphylo: tag `v0.2.0`; confirm the Snakefile runs against a config outside its checkout.
3. Move `cdv.yaml` and the tables here; `wildphylo config validate config/cdv.yaml`.
4. `environment.yml` + lock with the pinned wildphylo; `Snakefile` wrapper; dry run.
5. Remove scripts, data/processed, crashed and previous BEAST runs, working files; update README and CITATION (new version, pipeline citation).
6. Full build; `wildphylo gates compare` against the served dataset; publish only on `ok`.
7. Run the two outstanding analyses (date randomisation, asymmetric trait model) through wildphylo's gates.
