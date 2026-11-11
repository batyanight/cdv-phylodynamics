# CDV Phylodynamics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22182061.svg)](https://doi.org/10.5281/zenodo.22182061)

**Phylodynamics of a wildlife-maintained canine distemper virus lineage in North American carnivores.**

The CDV analysis repository: pipeline configuration, the audit trail of each build, the
served Auspice dataset, the published BEAST XMLs and the methods. The pipeline itself
(curation, alignment QC, maximum likelihood phylogeny, clade delineation, temporal signal
assessment, stratified subsampling, Bayesian phylodynamic inference with discrete
host-state reconstruction) is [wildphylo](https://github.com/batyanight/wildphylo);
canine distemper virus (*Morbillivirus canis*) hemagglutinin gene sequences from GenBank
are the input.

**[View the interactive phylogeny →](https://nextstrain.org/community/batyanight/cdv-phylodynamics)**

> **Status: core analysis complete.** Date-randomisation test and directional rate
> model outstanding — see [Outstanding work](#outstanding-work).

---

## Question

Has this lineage been maintained within wild carnivore populations, or is it sustained by
repeated spillover from domestic dogs?

## Findings

**Dataset.** 162 hemagglutinin gene sequences, 1992–2023, 95% from wild hosts —
raccoon (*Procyon lotor*, n=91), coyote (*Canis latrans*, 16), striped skunk
(*Mephitis mephitis*, 14), red fox (*Vulpes vulpes*, 10) — from Canada (114), the USA (44)
and Denmark (4). Assigned to lineage **America-2** by reference sequence placement.

**Evolutionary parameters.** BEAST 2.7.7, two chains of 10⁸ states, HKY+Γ₄, uncorrelated
relaxed lognormal clock, constant-size coalescent. 1802 combined samples, all ESS > 500.

| Parameter | Median | 95% HPD |
|---|---|---|
| Substitution rate | 8.54 × 10⁻⁴ subs/site/yr | 6.70 × 10⁻⁴ – 1.05 × 10⁻³ |
| **TMRCA** | **1976** | **1962 – 1985** |

**Host transition rates.** Only two of ten are distinguishable from the average, and their
credible intervals do not overlap:

| Transition | Median | 95% HPD |
|---|---|---|
| procyonid ↔ wild canid | 3.28 | 1.04 – 6.31 |
| domestic dog ↔ procyonid | 0.12 | 0.00005 – 0.60 |

Raccoon–wild canid transmission is credibly elevated; raccoon–domestic dog transmission is
credibly depressed. Consistent with a lineage maintained within wildlife rather than seeded
repeatedly from dogs.

**Direction of spread.** Of 13 well-supported host transitions on the reconstructed tree,
10 originate in procyonids (7 to wild canids, 3 to mustelids).

**Two captive felid outbreaks recovered.** The reconstruction independently identified two
felid transmission clusters, 23 years apart, each matching a published outbreak
investigation:

- **~1992** (p = 0.992) — a lion and a leopard from the North American captive felid
  epizootic (Weckworth et al. 2020; cf. Appel et al. 1994)
- **~2015** (p = 0.987) — four tigers from an exotic felid rescue centre in Indiana, with
  nested substructure indicating onward felid-to-felid spread
  (Batista Linhares et al. 2021, *Pathogens* 10:544)

The 2015 investigation independently concluded that felids sharing enclosures had elevated
risk and identified a raccoon sampled 3.3 km from the facility as the likely source. Both
conclusions were recovered here from public sequence data and host labels alone.

**Not claimed.** The root state is unresolved (p = 0.25); ancestral state reconstruction is
well supported only for roughly the last two decades. No claim is made about where the
lineage originated. See [limitations](METHODS.md).

---

## What this repo holds

| Path | Contents |
|---|---|
| `config/` | The pathogen config `cdv.yaml` and the tables it points to (`host_groups.tsv`, `lineage_references.tsv`, `vaccine_strains.txt`). Everything CDV-specific lives here; the pipeline holds nothing pathogen-specific |
| `builds/` | The audit trail of each build: provenance, accession snapshots, QC and temporal reports, clade summaries, build comparison. Large intermediate files are not tracked |
| `auspice/cdv-phylodynamics.json` | The Auspice dataset served at the Nextstrain link above |
| `beast/clade3/run100M_fixed/` | The BEAST XMLs of the published runs. [BEAST_MANIFEST.md](BEAST_MANIFEST.md) says which XML produced the published result and which are superseded |
| `METHODS.md` | Complete methods, including model decisions and limitations |
| `GLOSSARY.md` | The CDV-specific terms; all other terms are wildphylo's |

BEAUti settings for the discrete trait analysis are documented in
[METHODS.md](METHODS.md) §9.1–9.4 (sequence partition, trait partition, model
decisions, MCMC).

The BEAST runs under `beast/clade3/previous_runs`, `crashed_run*` and `data/processed`
are tracked today but are scheduled to move to a Zenodo deposit (see
[docs/PLAN-pathogen-repo.md](docs/PLAN-pathogen-repo.md)). They stay in the repository
until then; history is not rewritten.

## Pipeline

The analysis is run by [wildphylo](https://github.com/batyanight/wildphylo), installed
from the tag pinned in `environment.yml` (`v0.2.0`). Every step is a
`wildphylo <stage> <step>` command; the stages are fetch, curate, align, tree, gates, beast,
auspice and publish. Every exclusion is logged with a machine-readable reason, and a gate
that fails stops the run. The gates:

- **Review gate**: refuses while `needs_review.tsv` is non-empty (ambiguous host labels
  are an input to the host-transition analysis).
- **Temporal gate**: root-to-tip regression, date-shuffling permutation test and
  sampling-design diagnostics; on `fail` the BEAST branch is not scheduled.
- **Congruence gate**: segment topology agreement. Segmented pathogens only, so not
  applicable to CDV.
- **Convergence gate**: ESS and between-chain agreement, checked before any number is
  reported.
- **Trait signal gate**: shuffles host labels across the tips of the posterior trees to
  test whether host is associated with the phylogeny at all.
- **Comparison gate**: every build is compared against the previous one
  (`wildphylo gates compare`); a lost sequence or a moved TMRCA is a regression until
  explained.

Terms follow wildphylo's [GLOSSARY.md](https://github.com/batyanight/wildphylo/blob/main/GLOSSARY.md).

**Versions.** The analysis reported in Findings was run with the standalone numbered
scripts that preceded wildphylo. That code is at tag `v1.0.1`; the Zenodo release is
`v1.0.0` (2026-08-30). [METHODS.md §1](METHODS.md) maps each script to the
`wildphylo` step that replaced it.

## Reproduce

```bash
git clone https://github.com/batyanight/cdv-phylodynamics.git
cd cdv-phylodynamics
conda env create -f environment.yml
conda activate cdv-phylo
snakemake --configfile config/cdv.yaml --cores 8
```

The environment installs wildphylo at its pinned tag. BEAST2, Tracer and FigTree are
Java applications installed separately; BEAST chains are the step that would belong on a
cluster. Add `-n` for a dry run that validates the config and resolves the job graph
before anything downloads.

A build writes to `builds/cdv/<YYYYMMDD>/`; the newest date is the current build, and
earlier builds are kept. The audit trail is the tracked subset of that folder. Pin
`--config build_date=<YYYYMMDD>` to resume or reproduce a build.

**The Nextstrain entry only changes when a new `auspice/cdv-phylodynamics.json` is pushed
to `main`.** Rebuilding does not change it. Push a regenerated dataset only after
`wildphylo gates compare` passes against the served one.

## Data

All sequence data are public, from GenBank. No restricted or unpublished material is used.
Each build's accession snapshot (`raw/*.acc`) and provenance record are the reproducible
record of the dataset, because GenBank content changes over time. Until the Zenodo
deposit above exists, three processed files are tracked deliberately because the
published dataset cannot be reproduced without them:
`data/processed/H_clade_3.fasta` (the analysed alignment),
`data/processed/H_clade_3_ref.fasta` (the same alignment with A75/17 added, which
defines every coordinate in the annotation), and `data/processed/metadata_clean.tsv`
(host assignments as used, since these are the field most prone to going stale).

## Outstanding work

- [x] Two MCMC chains of 10⁸ states; combined; MCC tree
- [x] Ancestral host-state reconstruction
- [x] Lineage assignment (America-2) and tree-based vaccine check
- [x] Felid cluster identification and validation against published outbreaks
- [ ] Date-randomisation test (20 replicates) for formal temporal signal assessment
- [ ] Asymmetric trait model without BSSVS, for directional transition rates
- [ ] Investigation of the 4 Danish sequences and one *Meles meles* record
- [ ] Verification of every lineage reference accession against its primary source
- [x] Nextstrain/Auspice build, with H domain annotation in A75/17 coordinates

## Known limitations

Symmetric trait model (directional rates not estimated), single locus (H gene), year-only
dates for 126 of 162 sequences, deep nodes unresolved in the ancestral reconstruction,
eight of ten transition rates not individually distinguishable, and sampling that reflects
surveillance effort rather than prevalence. Fully documented in
[METHODS.md §10](METHODS.md).

An initial analysis was run with an inverted time axis (`date-backward` rather than
`date-forward`), detected by checking annotated tip heights against sampling dates, and
rerun. Both the erroneous and corrected outputs are retained. See
[METHODS.md §9.5](METHODS.md).

## Citation

See [CITATION.cff](CITATION.cff). Licensed under MIT — see [LICENSE](LICENSE).

## Author

Batya Nightingale — [ORCID 0000-0002-0706-8951](https://orcid.org/0000-0002-0706-8951)
