# CDV Phylodynamics

**Phylodynamics of a wildlife-maintained canine distemper virus lineage in North American carnivores.**

A reproducible pipeline for analysing canine distemper virus (*Morbillivirus canis*)
hemagglutinin gene sequences from GenBank: curation, alignment QC, maximum likelihood
phylogeny, clade delineation, temporal signal assessment, stratified subsampling, and
Bayesian phylodynamic inference with discrete host-state reconstruction.

**[View the interactive phylogeny →](https://nextstrain.org/community/batyanight/cdv-phylodynamics)**

> **Status: core analysis complete.** Date-randomisation test, directional rate model
> and Nextstrain build outstanding — see [Outstanding work](#outstanding-work).

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

## Pipeline

Scripts run in numbered order. Every exclusion is logged with a machine-readable reason.

| Script | Purpose |
|---|---|
| `00_check_env.py` | Verify Python packages and command-line tools; print install commands for anything missing |
| `01_fetch_sequences.py` | Retrieve all CDV records from GenBank; date-stamped, cached, with accession list |
| `02_curate_metadata.py` | Host normalisation, vaccine-strain filtering, date parsing, H-gene extraction, exclusion logging |
| `03_align_and_tree.py` | Tip relabelling for BEAST/TempEst, MAFFT alignment, IQ-TREE ML phylogeny |
| `04_alignment_qc.py` | Gap/ambiguity/identity statistics, coverage plot, reading-frame inference, duplicate detection |
| `05_tree_summary.py` | Clade delineation and host composition; identifies candidate clades for focused analysis |
| `06_subsample.py` | Stratified subsampling by clade × host × time; deterministic |
| `07_make_beast_xml.py` | BEAST2 XML generation and date-randomised replicates |
| `08_add_references.py` | Fetch published lineage reference sequences for classification |

`notebooks/01_explore_dataset.ipynb` is an interactive companion that imports these scripts
rather than duplicating them.

## Setup

```bash
git clone https://github.com/batyanight/cdv-phylodynamics.git
cd cdv-phylodynamics
conda env create -f environment.yml
conda activate cdv-phylo
python scripts/00_check_env.py
```

Full instructions in [SETUP_MACOS.md](SETUP_MACOS.md). BEAST2, Tracer, TempEst and FigTree
are Java applications installed separately.

## Documentation

- **[METHODS.md](METHODS.md)** — complete methods, including model decisions forced by
  numerical instability, limitations, and the Nextstrain implementation plan
- **[BEAUTI_PROTOCOL.md](BEAUTI_PROTOCOL.md)** — click-by-click BEAUti setup for the
  discrete trait analysis
- **[SETUP_MACOS.md](SETUP_MACOS.md)** — environment setup and compute planning

## Data

All sequence data are public, from GenBank. No restricted or unpublished material is used.
Sequence and BEAST output files are excluded from version control by `.gitignore`; the
pipeline regenerates them from the accession list.

## Outstanding work

- [x] Two MCMC chains of 10⁸ states; combined; MCC tree
- [x] Ancestral host-state reconstruction
- [x] Lineage assignment (America-2) and tree-based vaccine check
- [x] Felid cluster identification and validation against published outbreaks
- [ ] Date-randomisation test (20 replicates) for formal temporal signal assessment
- [ ] Asymmetric trait model without BSSVS, for directional transition rates
- [ ] Investigation of the 4 Danish sequences and one *Meles meles* record
- [ ] Verification of every lineage reference accession against its primary source
- [ ] Nextstrain/Auspice build

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
