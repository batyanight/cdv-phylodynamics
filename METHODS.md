# Methods — Phylodynamics of canine distemper virus in North American carnivores

**Status:** analysis in progress. BEAST runs executing at time of writing; sections marked
`[PENDING]` are to be completed from those outputs.

**Scope of this document.** A full record of what was done, why, and what was decided,
including analytical dead ends. Written to be adapted directly into a manuscript methods
section and to let another person reproduce the work from the repository.

---

## 1. Software and reproducibility

| Tool | Version | Used for |
|---|---|---|
| Python | 3.11 | pipeline scripts |
| Biopython | 1.8x | GenBank parsing, sequence handling |
| pandas | 2.x | metadata tables |
| MAFFT | 7.x | multiple sequence alignment |
| IQ-TREE | 2.x | maximum likelihood phylogeny, ModelFinder |
| TempEst | 1.5.3 | root-to-tip temporal signal |
| BEAST | 2.7.7 | Bayesian phylodynamics |
| BEAST_CLASSIC | (BEAST 2.7 package) | ancestral state reconstruction |
| Tracer | 1.7.x | MCMC convergence assessment |

`[FILL IN exact versions from your machine: mafft --version, iqtree2 --version, conda list]`

All pipeline code, configuration files and BEAST XMLs are in the project repository.
Analysis scripts are numbered in execution order (`00_check_env.py` through
`07_make_beast_xml.py`). Every exclusion is logged to `data/interim/exclusions.tsv`
with a machine-readable reason.

**Disclosure.** Pipeline code and analysis scripts were developed with assistance from
an AI assistant (Claude, Anthropic). All analytical decisions, data curation judgements,
and interpretation are the author's. This disclosure is included because bioRxiv and most
journals now require it.

---

## 2. Sequence data acquisition

All canine distemper virus (CDV; *Morbillivirus canis*) nucleotide records were retrieved
from GenBank via the NCBI Entrez API using the query:

```
txid11232[Organism:exp] AND 200:20000[Sequence Length] NOT patent[Properties]
```

`[Organism:exp]` expands the taxonomic node to include all subordinate taxa and strain
designations. The download was performed on `[DATE]` and retrieved `[N]` records. The
raw GenBank flatfile and a companion accession list are archived under `data/raw/` with a
date-stamped filename; GenBank content changes over time, so the dated pull and accession
list constitute the reproducible record of the dataset.

Script: `01_fetch_sequences.py`.

---

## 3. Metadata curation and filtering

Script: `02_curate_metadata.py`. Every record was parsed for accession, host, country,
collection date, strain/isolate designation, and gene content.

### 3.1 Host normalisation

Free-text `/host` qualifiers were mapped to canonical taxa and to functional host groups
(domestic dog, wild canid, wild felid, mustelid, procyonid, pinniped, ursid, ailurid,
viverrid, primate, other) using an ordered pattern table (`config/host_groups.tsv`).
Matching is first-match-wins and order-sensitive: specific patterns precede general ones so
that, for example, "raccoon dog" (*Nyctereutes procyonoides*) is classified as a wild canid
rather than a domestic dog, and *Panthera tigris altaica* retains subspecies identity rather
than collapsing to *Panthera tigris*. Where `/host` was absent, `/isolation_source` was used
as a fallback.

Records whose host string matched no pattern were written to `needs_review.tsv` and
adjudicated manually rather than being silently discarded.

### 3.2 Vaccine strain exclusion

Vaccine and vaccine-derived sequences were identified by pattern matching against
organism, strain, isolate, and description fields using a curated list of classical
attenuated strains (Onderstepoort, Rockborn, Snyder Hill, Lederle, Bussell, CDV3),
commercial product names, and generic vaccine indicators (`config/vaccine_strains.txt`).

**Limitation acknowledged explicitly:** name-based filtering cannot identify unlabelled or
misspelled vaccine-derived sequences. Testing against synthetic records confirmed that a
plausible misspelling (e.g. "Ondersteport") evades the filter. Accordingly, the maximum
likelihood tree was additionally inspected for field isolates clustering within the vaccine
clade. `[STATE OUTCOME: n additional sequences identified and excluded, or none found]`

### 3.3 Collection date parsing

Collection dates were parsed from GenBank's several accepted formats (ISO `YYYY-MM-DD`,
`YYYY-MM`, `DD-Mon-YYYY`, `Mon-YYYY`, bare year, and date ranges) and converted to decimal
years. For month- and year-only dates the interval midpoint was used; ranges were resolved
to the mean of their endpoints. Date precision (day / month / year / range) was retained as
a metadata field so that the effect of imprecise dates can be assessed.

### 3.4 Gene extraction

Haemagglutinin (H) gene sequences were extracted preferentially from CDS/gene feature
annotations, accepting the variant labels used across GenBank (`H`, `HA`, `hemagglutinin`,
`haemagglutinin`, `attachment protein`). For records lacking usable annotation, a length
heuristic was applied to records whose description indicated H content (full-length H is
~1824 nt). Sequences recovered by heuristic rather than annotation were flagged for manual
review and retained only after inspection. Records whose annotated H length was
implausible — chiefly complete genomes with an H feature spanning the entire record — were
excluded pending manual correction.

### 3.5 Exclusion criteria

Records were excluded, in order of precedence, if they were: vaccine or vaccine-derived;
lacking an identifiable H sequence; shorter than 400 nt of H; lacking a parseable collection
date; of unresolved host; or of implausible annotated H length. Exclusion counts by reason
are in `data/interim/exclusions.tsv`.

`[INSERT the exclusion table from your run]`

---

## 4. Alignment and quality control

Sequences were aligned with MAFFT (`--auto --adjustdirection`). Sequences reverse
complemented by MAFFT were noted and inspected.

Alignment quality was assessed with `04_alignment_qc.py`, which computes per-sequence gap
and ambiguity fractions, identity to the alignment consensus, per-column coverage, and
internal stop codons. Reading frame was inferred at the dataset level as the frame
minimising total internal stops across all sequences; individual sequences with internal
stops in that frame were flagged as possible frameshifts, wrong-strand entries, or
sequencing errors.

Sequences below 80% identity to consensus were inspected individually and excluded where
they proved to be misaligned or non-H. Ragged terminal columns below 50% coverage were
trimmed.

`[STATE: final alignment length, number of sequences, number excluded at QC]`

---

## 5. Maximum likelihood phylogeny

An ML tree was inferred in IQ-TREE with ModelFinder (`-m MFP`) for substitution model
selection, 1000 ultrafast bootstrap replicates, and 1000 SH-aLRT replicates.

`[STATE: selected model, e.g. GTR+F+I+G4; log-likelihood; n sites]`

Tip labels were formatted `ACCESSION|host_group|decimal_year` throughout, so that host and
date travel with the sequence through every downstream tool.

The resulting tree contained **1761 tips** spanning **1982.1–2026.5**, with the following
host composition:

| Host group | n | % |
|---|---|---|
| domestic_dog | 915 | 52.0 |
| wild_canid | 386 | 21.9 |
| mustelid | 203 | 11.5 |
| procyonid | 144 | 8.2 |
| wild_felid | 63 | 3.6 |
| other | 16 | 0.9 |
| ailurid | 9 | 0.5 |
| pinniped | 8 | 0.5 |
| primate | 7 | 0.4 |
| viverrid | 6 | 0.3 |
| ursid | 4 | 0.2 |

Wild carnivores comprised 823 sequences (46.7%).

---

## 6. Clade delineation

Script: `05_tree_summary.py`. The ML tree was midpoint-rooted and partitioned into major
groups by iteratively splitting the largest remaining clade at its deepest internal division
until approximately 20 groups were obtained. Each group was characterised by size, bootstrap
support, temporal span, and host composition.

**This is a structural partition of the tree, not formal lineage assignment.** Assignment to
named CDV lineages (America-1/2, Europe wildlife, Arctic-like, Asia-1 to 4, etc.) requires
reference sequences with published lineage designations in the alignment. See §11.1.

Groups of interest:

| Group | n | Wild | Span | Dominant hosts |
|---|---|---|---|---|
| clade_2 | 409 | 262 (64%) | 1998–2025 | wild canid 175, dog 147, mustelid 77 |
| **clade_3** | **204** | **195 (96%)** | **1992–2024** | **procyonid 112, wild canid 38, mustelid 33** |
| clade_1 | 430 | 96 (22%) | 2004–2026 | dog 334 |
| clade_5 | 111 | 47 (42%) | 1994–2026 | dog 50, wild felid 34 |
| clade_8 | 72 | 39 (54%) | 1982–2023 | dog 33, mustelid 29, pinniped 6 |

**clade_3 was selected as the focus of the phylodynamic analysis.** At 96% wild hosts with
only 9 domestic dog sequences across a 31-year span, it is a candidate wildlife-maintained
lineage rather than a lineage sustained by repeated spillover from dogs.

---

## 7. Temporal signal assessment

Root-to-tip regression was performed in TempEst using best-fitting root selection.

| Dataset | n | Date range | Slope (subs/site/yr) | r | R² | Implied TMRCA | Residual MS |
|---|---|---|---|---|---|---|---|
| Full H tree | 1761 | 1982–2026 | 5.08 × 10⁻⁴ | 0.206 | 0.042 | 477 CE | 2.28 × 10⁻⁴ |
| Global subsample | 400 | 44.4 yr | 4.81 × 10⁻⁴ | 0.221 | 0.049 | −188 CE | 2.56 × 10⁻⁴ |
| **clade_3** | **162** | **31.6 yr** | **7.46 × 10⁻⁴** | **0.765** | **0.586** | **1974.1** | **7.06 × 10⁻⁶** |

**Interpretation.** The global datasets yielded rate estimates consistent with published
morbillivirus H substitution rates but very weak regression fit and biologically impossible
root ages. The near-identical rate estimates from the full tree (5.08 × 10⁻⁴) and a 77%
subsample (4.81 × 10⁻⁴) indicate this is not a sampling-redundancy artefact. The pattern is
consistent with deep inter-lineage divergence dominating root-to-tip distance: linear
extrapolation to zero divergence is unconstrained when the tree spans divergence far older
than the sampling window.

Restricting to clade_3 resolved this. R² rose from 0.049 to 0.586, residual mean squared
fell 36-fold, and the implied TMRCA moved from an impossible pre-medieval date to 1974 — a
biologically plausible origin for a regional lineage.

**Caveat.** Root-to-tip regression is a heuristic, not a statistical test: tip observations
are non-independent by shared ancestry. It is used here to compare relative signal between
datasets and to inform the clock rate prior, not as evidence of temporal signal in itself.
Formal assessment is by date-randomisation (§11.2).

---

## 8. Subsampling

Script: `06_subsample.py`. Two datasets were produced.

**Global (n = 400).** Stratified across clade × host group × 5-year time bin, with each
non-empty stratum guaranteed at least one representative and the remaining budget
distributed proportional to the square root of stratum size. Square-root rather than linear
allocation prevents the domestic-dog-dominated strata (52% of the dataset) from crowding out
rare host groups on which discrete trait inference depends. Within each stratum, sequences
were prioritised by date precision (day > month > year), then by fewer ambiguous bases, then
by greater ungapped length. Wild carnivore representation rose from 46.7% to 50.2%.

**clade_3 (n = 162).** All clade_3 sequences retained after collapsing 42 sets of identical
sequences to a single best-dated representative each (204 → 162). Identical sequences carry
no additional phylogenetic signal and increase MCMC cost.

Selection is fully deterministic (fixed seed); repeated runs produce byte-identical output.

### 8.1 clade_3 composition

| Host group | n | % |
|---|---|---|
| procyonid | 91 | 56.2 |
| wild_canid | 32 | 19.8 |
| mustelid | 23 | 14.2 |
| domestic_dog | 8 | 4.9 |
| wild_felid | 7 | 4.3 |
| ailurid | 1 | 0.6 |
| **wild total** | **154** | **95.1** |

By species: *Procyon lotor* 91, *Canis latrans* 16, *Mephitis mephitis* 14, *Vulpes vulpes*
10, *Canis lupus familiaris* 8, *Panthera tigris* 5, *Neovison vison* 5, *Urocyon
cinereoargenteus* 3, *Martes* sp. 3, *Vulpes* sp. 2, *Panthera leo* 1, *Panthera pardus* 1,
*Canis lupus* 1, *Meles meles* 1, *Ailurus fulgens* 1.

Geographic distribution: Canada 114, USA 44, Denmark 4. Date precision: year-only 126,
day 34, month 2. Temporal span 1992.0–2023.6.

**Notes for interpretation.** The composition is that of the North American mesocarnivore
assemblage — raccoon, coyote, striped skunk, red fox, mink, marten. The felid sequences
(*P. tigris*, *P. leo*, *P. pardus*) are not from wild populations within this range and are
consistent with captive animals infected from local wildlife, a documented pattern in North
American zoological collections. The four Danish sequences and single *Meles meles* are
geographic outliers requiring individual inspection (§11.1).

---

## 9. Bayesian phylodynamic analysis

### 9.1 Sequence partition

- Substitution model: HKY+Γ₄, empirical base frequencies, shape estimated
- Proportion invariant fixed at 0 (not co-estimated with Γ shape, which is
  non-identifiable and degrades mixing)
- Molecular clock: uncorrelated relaxed lognormal
- Clock rate prior: lognormal, M = 7.46 × 10⁻⁴, S = 1.0, mean in real space — centred on
  the clade_3 root-to-tip estimate and wide enough to be data-dominated
- Tree prior: coalescent, constant population size

**Constant population size was chosen over Bayesian skyline deliberately.** 85 of 91
procyonid sequences derive from the 2010s; a skyline model would produce demographic
estimates for the pre-2010 period that are informed almost entirely by prior rather than
data. Population dynamics are therefore not inferred and no demographic claims are made.

### 9.2 Discrete trait partition (host)

- Ancestral state reconstruction via BEAST_CLASSIC `AncestralStateTreeLikelihood`
- Symmetric substitution model across 5 host states (10 rate parameters)
- Strict clock on the trait partition
- Rate indicators fixed (BSSVS disabled — see §9.3)
- Priors: `relativeGeoRates` Gamma(1, 1); `traitClockRate` Gamma(0.001, 1000)

Host states: procyonid (91), wild_canid (32), mustelid (23), domestic_dog (8),
wild_felid (8).

### 9.3 Model decisions arising from numerical instability

Two modifications were required and both are analytically material, so they are recorded
here in full rather than omitted.

**Merging of the single ailurid sequence.** The initial 6-state model included *Ailurus
fulgens* represented by a single sequence. A single observation cannot inform transition
rate estimation, and runs terminated with
`randomChoiceUnnormalized falls through — negative components in input distribution` in
`AncestralStateTreeLikelihood.redrawAncestralStates` at ~3 × 10⁵ states. The sequence was
merged into the wild_felid category at the alignment level, giving 5 states with a minimum
group size of 8.

*Note on an intermediate error:* an initial attempt merged the state in the XML traitset
only. Because the substitution model retained 6-state dimensionality, this produced a state
with zero observations and the instability persisted (failing later, at ~1.2 × 10⁶ states).
The merge was therefore performed at the FASTA level and the model rebuilt, ensuring model
dimensionality matched the data.

**BSSVS disabled.** Bayesian stochastic search variable selection was initially enabled to
identify supported transitions. BSSVS permits rate indicators to switch to zero; when all
indicators for a state are off, the conditional distribution for ancestral state sampling
has no positive components and the draw fails. Rate indicators were therefore fixed at
true (`estimate="false"`, dimension 10), removing the failure mode.

**Consequence for inference.** With a symmetric model, transition rates are not
directional: dog → wildlife and wildlife → dog cannot be distinguished. Reconstructed
ancestral states, the location and number of host transitions on the tree, and which host
pairs exchange remain estimable. Directional inference is listed as future work (§11.3).

### 9.4 MCMC

Two independent chains of 10⁷ states each, seeds 12345 and 54321, sampling every 10⁴ states
(1000 samples per chain). Run in BEAST 2.7.7 without BEAGLE (BEAGLE library unavailable on
the analysis machine; Java `BeerLikelihoodCore` used instead, affecting speed only).

**Chain length.** An initial pair of chains at 10⁷ states gave adequate mixing for trait
parameters but not for tree and clock parameters (Tree.height ESS 15). The operator
schedule was inspected and found complete, including the relaxed-clock UpDownOperator, so
chains were rerun at 10⁸ states.

### 9.5 Correction: inverted time axis

**An initial set of 10⁸-state chains was run with the tip date direction reversed and has
been discarded.** BEAUti had written `traitname="date-backward"`, causing BEAST to
interpret calendar years as time before present: the 1992 sequences were treated as the
most recent and the 2023 sequences as the oldest.

*Detection.* Annotated tip heights in the MCC tree were compared against sampling dates.
For a correctly specified analysis, tip height must equal (most recent sampling date −
tip date). Instead, heights equalled (tip date − oldest date): the sequence dated 1992.000
carried height 0. Corroborating signals, not initially recognised as such, were a Bayesian
TMRCA of 1913 against a root-to-tip estimate of 1974, an implausibly wide TMRCA interval
(1844–1953), inflated among-branch rate variation (ucldStdev 0.85, coefficient of variation
0.97), and poor mixing of tree height.

*Correction.* `traitname` was changed to `date-forward` and both chains rerun. The
corrected analysis gives ucldStdev 0.45 (CoV 0.47), a TMRCA of 1976 with a 23-year
interval, and every parameter converging on a single chain. Both the erroneous and
corrected outputs are retained in the repository (`run100M/` and `run100M_fixed/`).

*Preventive check.* `07_make_beast_xml.py` and the launch procedure now assert
`traitname="date-forward"` before a chain starts, and MCC trees are verified against
sampling dates before interpretation.

### 9.6 Convergence and posterior estimates

Two independent chains of 10⁸ states (seeds 12345, 54321), sampled every 10⁴, combined in
LogCombiner with 10% burn-in per chain (1802 samples). All parameters exceeded ESS 500.

| Parameter | Median | 95% HPD | ESS |
|---|---|---|---|
| Substitution rate (subs/site/yr) | 8.54 × 10⁻⁴ | 6.70 × 10⁻⁴ – 1.05 × 10⁻³ | 1295 |
| Tree height (years) | 47.7 | 38.9 – 61.2 | 1055 |
| **TMRCA** | **1976** | **1962 – 1985** | — |
| ucldStdev | 0.45 | 0.22 – 0.69 | 1335 |
| Rate coefficient of variation | 0.47 | 0.24 – 0.71 | 546 |
| popSize | 57.6 | 42.5 – 75.8 | 1361 |
| kappa | 6.32 | 5.30 – 7.41 | 1802 |
| gammaShape | 0.50 | 0.38 – 0.62 | 1802 |

The rate estimate is at the upper end of published morbillivirus H-gene values, consistent
with a single recently emerged lineage rather than a cross-lineage average. The
root-to-tip slope for this clade (7.46 × 10⁻⁴) falls within the HPD.

### 9.7 Host transition rates

Relative rates under the symmetric model, all ESS 1802:

| Transition | Median | 95% HPD |
|---|---|---|
| **procyonid ↔ wild_canid** | **3.28** | **1.04 – 6.31** |
| mustelid ↔ wild_canid | 1.12 | 0.0002 – 3.74 |
| mustelid ↔ procyonid | 0.93 | 0.016 – 2.23 |
| domestic_dog ↔ wild_felid | 0.74 | 0.0002 – 2.87 |
| wild_canid ↔ wild_felid | 0.66 | 0.0024 – 2.37 |
| domestic_dog ↔ wild_canid | 0.51 | 0.0006 – 1.77 |
| procyonid ↔ wild_felid | 0.35 | 0.0017 – 1.16 |
| mustelid ↔ wild_felid | 0.30 | 0.00005 – 1.60 |
| domestic_dog ↔ mustelid | 0.29 | 0.00009 – 1.42 |
| **domestic_dog ↔ procyonid** | **0.12** | **0.00005 – 0.60** |

Only two transitions are distinguishable from the average: procyonid ↔ wild_canid, whose
HPD lower bound exceeds 1, and domestic_dog ↔ procyonid, whose upper bound falls below 1.
Their intervals do not overlap. The remaining eight transitions have intervals spanning 1
and are not individually resolved. Claims are therefore restricted to these two.

### 9.8 Ancestral host state reconstruction

MCC tree summarised from the combined host tree posterior (TreeAnnotator, median node
heights, burn-in already removed).

**Resolution declines sharply with node age.** Median state probability by node age:
0–5 yr 0.99 (n=2); 5–10 yr 0.97 (n=82); 10–15 yr 0.99 (n=49); 15–20 yr 0.77 (n=10);
20–30 yr 0.37 (n=9); 30+ yr 0.28 (n=9). The root state is not resolved (procyonid,
p = 0.25, against 0.20 expected by chance under five states).

**No claim is made about the ancestral host of the lineage.** Inference is restricted to
the period in which reconstruction is well supported, approximately the last two decades.

**Directionality.** Although the substitution model is symmetric and does not estimate
directional rates, the reconstruction yields direction through tree topology. Of 13
transitions with both endpoints at probability ≥ 0.8, 10 originate in procyonids:

| Transition | n |
|---|---|
| procyonid → wild_canid | 7 |
| procyonid → mustelid | 3 |
| wild_canid → procyonid | 1 |
| mustelid → wild_canid | 1 |
| wild_canid → domestic_dog | 1 |

### 9.9 Captive felid transmission clusters

Two well-supported felid clades, 23 years apart, each corresponding to a documented
outbreak:

**~1992** (node probability 0.992, clade posterior 1.00): MT932504 (*Panthera leo*,
Sept 1992), MT932511 (*Panthera pardus*, Oct 1992), both USA, from Weckworth et al. 2020.
Contemporaneous with the North American captive felid epizootic described by Appel et al.
1994. A *Procyon lotor* sequence from the same study (MT932505, Jan 1992) is present in the
dataset.

**~2015** (node probability 0.987, clade posterior 0.93): MW984527, MW984530, MW984531,
MW984532 — four tigers from an exotic felid rescue centre in Indiana, USA, sampled
November–December 2015, from Batista Linhares et al. 2021 (*Pathogens* 10:544). Nested
substructure within this clade (probabilities 0.995 and 1.000) indicates onward
transmission among felids. The original investigation independently concluded that felids
sharing a fence or enclosure had significantly elevated risk, and reported H-gene
similarity of up to 99% to contemporaneous regional wildlife strains, including a raccoon
sampled 3.3 km from the facility during the outbreak (MW984535, in this dataset).

**Validation.** The reconstruction recovered both the wildlife source and the within-facility
spread of a documented outbreak using only public sequence data and host labels, and
recovered a second, structurally identical event 23 years earlier. This constitutes an
independent check on the method.

**Caveat.** Both felid clades have procyonid-reconstructed parent nodes, but those parents
are weakly supported (p = 0.535 and 0.392). The raccoon-source interpretation rests on the
combination of transition rate estimates, host composition, and the published outbreak
investigations — not on ancestral state probability alone.

### 9.10 Lineage assignment

Twenty published lineage reference sequences were added and an ML tree rebuilt
(`08_add_references.py`). Patristic distances place **America-2** closest to the query set:
A75/17 (AF164967) at mean distance 0.038 (minimum 0.010), AF112189 at 0.040. Two sequences
already in the dataset (EU716337, KJ123771) are themselves published America-2 reference
strains. The America-2 isolates Black panther A-92 (Z54166) and "America dog" (Z47762) also
fall within the query set.

**Vaccine check.** Onderstepoort (AF378705) and Snyder Hill (JN896987) are the two most
distant references (0.102, 0.106). No query sequence groups with them, confirming that
name-based vaccine filtering (§3.2) did not miss vaccine-derived sequences.

**Reference excluded.** AF259552, listed as America-2 in a patent filing, sat at distance
0.106 — as far as the vaccine strains — indicating its lineage label is incorrect. It was
excluded and the exclusion documented in `config/lineage_references.tsv`.

**Nomenclature.** The original H-gene scheme (Martella et al. 2006; Nikolin et al. 2012)
recognised nine lineages; current classifications recognise 17–19. This work follows the
original scheme; the applicable scheme should be stated and cited in any publication.

## 10. Limitations

1. **Date precision.** 126 of 162 clade_3 sequences have year-only collection dates,
   assigned to the year midpoint. This adds uncertainty to node age estimates.
2. **Sampling bias.** GenBank deposition reflects surveillance and research effort, not
   epidemiological prevalence. The 2010s dominance of procyonid sequences reflects a
   sampling programme, not necessarily an epidemic.
3. **Single locus.** H gene only. Recombination within CDV is reported infrequently but
   whole-genome analysis would be more robust.
4. **Symmetric trait model.** Directional transition *rates* are not estimated (§9.3).
   Direction is recovered from tree topology via ancestral state reconstruction (§9.8),
   which is a weaker form of evidence.
5. **Structural clade definition.** clade_3 is defined by tree topology, not by reference
   lineage assignment (§11.1).
6. **Vaccine filtering is name-based** and cannot be exhaustive (§3.2).
7. **No geographic model.** Country data are available but not modelled; the
   Canada/USA/Denmark split is described, not inferred.
8. **Deep nodes unresolved.** Ancestral state reconstruction is well supported only for
   approximately the last two decades; the root state is not resolved (§9.8). No claim is
   made about the ancestral host of the lineage.
9. **Eight of ten transition rates unresolved.** Only procyonid ↔ wild_canid and
   domestic_dog ↔ procyonid have credible intervals distinguishable from the average
   (§9.7).
10. **Reference accessions require verification.** Several lineage reference sequences were
   compiled from secondary sources; one proved mislabelled (§9.10). Each should be checked
   against its primary GenBank record and depositing publication before publication.

---

## 11. Next steps

### 11.0 Status

Completed: BEAST chains, convergence, MCC tree, ancestral state reconstruction, lineage
assignment (§9.10), vaccine check (§9.10), felid cluster identification and validation
against published outbreak investigations (§9.9).

Outstanding: date-randomisation test (§11.2), directional transition rates (§11.3),
investigation of the Danish sequences and the *Meles meles* record, confirmation of
captive origin for all felid sequences, Nextstrain build (§12).

### 11.1 Validate clade identity and outliers — partly complete

Script: `08_add_references.py`, with accessions in `config/lineage_references.tsv`.

Reference sequences with published lineage designations are merged with the query set,
realigned, and a classification tree built. Lineage assignment follows from which
reference tips fall inside clade_3.

**Nomenclature.** The original H-gene scheme (Martella et al. 2006; Nikolin et al. 2012)
recognised nine lineages: America-1, America-2, Asia-1, Asia-2, Arctic-like, South
America, Southern Africa, Europe, Europe wildlife. Current classifications recognise 17,
with some authors using 19. State which scheme is followed and cite it.

**Expected assignment.** America-2 is the most likely match: it is a North American
lineage associated with raccoons, and published work reports America-2 and America-3
co-circulating in raccoon populations in Colorado. A75/17 (AF164967) is the standard
America-2 reference. Work on raccoons around a Chicago-area zoo attributed 2000-2001
epizootics to the A75/17 lineage, which is directly relevant to the captive felid
sequences in clade_3.

**America-3 reference sequence still needed** — it is the most plausible alternative
assignment and no accession was located in the sources consulted.

**Secondary use: tree-based vaccine check.** The reference panel includes America-1 /
vaccine lineage sequences (Onderstepoort AF378705, Snyder Hill JN896987). Any query
sequence falling inside that clade is vaccine-derived and was missed by name-based
filtering (§3.2). Such sequences must be added to `config/vaccine_strains.txt` and the
pipeline re-run from step 02.

**Verification requirement.** Reference accessions in `config/lineage_references.tsv`
were compiled from published literature and a patent filing; several were read from
secondary sources. Each must be verified against its primary GenBank record and
depositing publication before the lineage call is published.

Separately, inspect individually:
- the 4 Denmark sequences and the *Meles meles* record — geographic outliers
- the 8 *Canis lupus familiaris* sequences — potential spillback into dogs; check whether
  they are phylogenetically nested among wildlife sequences or basal
- the 7 felid sequences — confirm captive origin from the source publications
- the 14 sequences with unresolved host group in the wider dataset

### 11.2 Date-randomisation test

Generate 20 replicates with tip dates shuffled (`07_make_beast_xml.py --randomize-dates 20`)
and run at reduced chain length. Temporal signal is demonstrated if the 95% HPD of the real
`ucldMean` estimate does not overlap the distribution of randomised estimates. This is the
defensible test of temporal signal and substitutes for arguing from R².

### 11.3 Directional transition rates

Attempt an asymmetric trait model with BSSVS disabled. This recovers directionality while
avoiding the zero-rate failure mode. If numerically stable, it directly addresses whether
domestic dogs are a source or a sink for this lineage.

### 11.4 Post-processing

1. **LogCombiner** — merge chains if individual ESS is inadequate; 10% burn-in.
2. **TreeAnnotator** — MCC tree from combined `.trees`, 10% burn-in, median node heights,
   keeping annotations from `clade3_5state.host.trees` for ancestral states.
3. **FigTree** — verify branch colouring by reconstructed host state before export.

---

## 12. Nextstrain / Auspice implementation

Two routes. Route A is the correct one for a time-calibrated Bayesian tree.

### 12.1 Route A — import the BEAST MCC tree (recommended)

Augur can ingest a BEAST MCC tree directly, preserving node dates and annotations.

```bash
conda install -c conda-forge -c bioconda augur auspice   # or: pip install nextstrain-augur

augur import beast \
    --mcc beast/clade3/clade3_5state.host.mcc.tree \
    --output-tree      nextstrain/tree.nwk \
    --output-node-data nextstrain/branch_lengths.json \
    --recursion-limit 10000
```

`augur import beast` converts BEAST's annotated Newick into a Newick tree plus a node-data
JSON containing node dates and any annotations present (including reconstructed host
states, if the MCC tree was annotated from the host tree file).

Build a metadata TSV keyed on the tip labels:

```python
import pandas as pd
from pathlib import Path

d = pd.read_csv("data/processed/H_clade_3_metadata.tsv", sep="\t")
clean = pd.read_csv("data/processed/metadata_clean.tsv", sep="\t")
clean["acc_base"] = clean["accession"].astype(str).str.split(".").str[0]
m = d.merge(clean[["acc_base", "country", "collection_date", "host_canonical",
                   "strain", "description"]],
            left_on="accession", right_on="acc_base", how="left")

out = pd.DataFrame({
    "strain":  m["label"],                    # MUST match tip labels exactly
    "date":    m["collection_date"].fillna(m["decimal_year"].round(0).astype("Int64").astype(str)),
    "host":    m["host_group"],
    "species": m["host_canonical"],
    "country": m["country"],
    "accession": m["accession"],
})
Path("nextstrain").mkdir(exist_ok=True)
out.to_csv("nextstrain/metadata.tsv", sep="\t", index=False)
print(out.head())
```

Then export for Auspice:

```bash
augur export v2 \
    --tree nextstrain/tree.nwk \
    --metadata nextstrain/metadata.tsv \
    --node-data nextstrain/branch_lengths.json \
    --color-by-metadata host species country \
    --title "CDV clade_3: a wildlife-maintained lineage in North American carnivores" \
    --maintainers "Batya Nightingale" \
    --output auspice/cdv_clade3.json

auspice view --datasetDir auspice
```

Opens at `http://localhost:4000`.

**Auspice config** (`nextstrain/auspice_config.json`) to control colouring and ordering:

```json
{
  "title": "CDV clade_3: a wildlife-maintained lineage in North American carnivores",
  "maintainers": [{"name": "Batya Nightingale"}],
  "colorings": [
    {"key": "host",    "title": "Host group", "type": "categorical"},
    {"key": "species", "title": "Host species", "type": "categorical"},
    {"key": "country", "title": "Country", "type": "categorical"}
  ],
  "display_defaults": {"color_by": "host", "branch_label": "none"},
  "filters": ["host", "species", "country"],
  "panels": ["tree", "entropy"]
}
```

Pass with `--auspice-config nextstrain/auspice_config.json`.

### 12.2 Route B — native Augur pipeline (alternative)

If you would rather have a fully Nextstrain-native, Snakemake-driven build (useful if the
dataset will be updated periodically), the standard chain is:

```bash
augur index    --sequences data/processed/H_clade_3.fasta --output nextstrain/index.tsv
augur filter   --sequences data/processed/H_clade_3.fasta --metadata nextstrain/metadata.tsv \
               --sequence-index nextstrain/index.tsv --output nextstrain/filtered.fasta
augur align    --sequences nextstrain/filtered.fasta --output nextstrain/aligned.fasta --fill-gaps
augur tree     --alignment nextstrain/aligned.fasta --output nextstrain/tree_raw.nwk
augur refine   --tree nextstrain/tree_raw.nwk --alignment nextstrain/aligned.fasta \
               --metadata nextstrain/metadata.tsv --timetree --coalescent const \
               --clock-rate 7.46e-4 --date-confidence \
               --output-tree nextstrain/tree.nwk --output-node-data nextstrain/branch_lengths.json
augur traits   --tree nextstrain/tree.nwk --metadata nextstrain/metadata.tsv \
               --columns host --confidence --output-node-data nextstrain/traits.json
augur ancestral --tree nextstrain/tree.nwk --alignment nextstrain/aligned.fasta \
               --output-node-data nextstrain/nt_muts.json
augur export v2 --tree nextstrain/tree.nwk --metadata nextstrain/metadata.tsv \
               --node-data nextstrain/branch_lengths.json nextstrain/traits.json nextstrain/nt_muts.json \
               --auspice-config nextstrain/auspice_config.json \
               --output auspice/cdv_clade3.json
```

**Note:** `augur refine` uses TreeTime, which is maximum-likelihood dating, not Bayesian.
Results will differ from BEAST and carry no posterior support. Use Route B for a fast
interactive view or a periodically-updated build; use Route A for the figures that go in
the paper.

### 12.3 Fastest possible preview

For a look before investing in a full build, `auspice.us` accepts a drag-and-drop Newick
tree plus a metadata TSV in the browser, with no installation. Useful for checking that
tip labels and metadata line up before running the pipeline.

### 12.4 Publication

- Archive the repository on Zenodo for a DOI
- Deposit the Auspice JSON alongside it; Nextstrain community builds can be served from a
  public GitHub repository at `nextstrain.org/community/batyanight/cdv-phylodynamics`
- Include the BEAST XML, the MCC tree, and the exclusion log as supplementary material

---

## 13. Outstanding items checklist

- [ ] Both BEAST chains complete; ESS > 200 for all parameters
- [ ] Chains agree; combined in LogCombiner if needed
- [ ] MCC tree annotated with host states
- [ ] Date-randomisation test run and reported
- [ ] Reference lineage sequences added; clade_3 formally identified
- [ ] Denmark / *Meles meles* outliers resolved
- [ ] 8 domestic dog sequences examined for spillback
- [ ] Felid sequences confirmed as captive from source publications
- [ ] Asymmetric-without-BSSVS attempt for directionality
- [ ] Auspice build rendering correctly
- [ ] Software versions recorded exactly
- [ ] Repository archived on Zenodo
