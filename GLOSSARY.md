# Glossary

The terms used in this repository (build, stage, step, gate, verdict, audit trail,
pathogen config, host group, trait state, clade, lineage reference, anchor, DTA, BSSVS,
ESS and the rest) are wildphylo's. Their definitions are in
[wildphylo's GLOSSARY.md](https://github.com/batyanight/wildphylo/blob/main/GLOSSARY.md)
and are not repeated here. This file lists only the CDV-specific terms.

- **America-2** — the CDV H-gene lineage this analysis is about, assigned by placement against the lineage references (METHODS.md §9.10). A75/17 (AF164967) is its reference. The scheme followed is the original nine-lineage one (Martella et al. 2006; Nikolin et al. 2012); current classifications recognise 17–19.
- **clade 3** (`clade_3`) — the group cut from the ML tree of the full H dataset that is the focus of the analysis: 204 sequences, 96% from wild hosts, 1992–2024; 162 after collapsing identical sequences (METHODS.md §6, §8). A structural partition of the tree, not a named lineage.
- **H gene / hemagglutinin** — the CDV attachment-protein gene, the single locus analysed (`locus.name: H`). Full length is 1824 nt; GenBank records annotated "H" can run longer, so annotated length is checked against 1824 nt with a 2% over-length tolerance.
- **A75/17 coordinates** — the numbering used for every annotation position (nucleotide and amino acid): that of the reference record A75/17, AF164967.1 (America-2), in which the H gene is 7059..9004 and the H CDS is 7079..8902, set in `locus.coordinate_reference` as `cds: [7079, 8902]` and verified against the GenBank record. Never alignment columns, which shift whenever the dataset changes, and never the 1..1824 numbering of the served Auspice JSON, which is an alignment coordinate. The earlier value `[21, 1844]` numbered the same CDS from the first base of the H gene feature.
- **dta_states** — the map from host group to the host states of the discrete trait analysis (`hosts.dta_states` in `config/cdv.yaml`). The twelve host groups would give 66 symmetric rates, more than the host transitions observed can identify, so the map keeps five: `procyonid`, `wild_canid`, `mustelid`, `wild_felid`, `domestic_dog`. Groups it does not list, `ailurid` among them, are excluded (`dta_other: null`) and their tips enter the trait as `?`, ambiguous across all states.
- **procyonid** — dta_states state: raccoons (*Procyon lotor*), the reservoir candidate (`hosts.reservoir_candidates`); 91 of the 162 clade 3 sequences.
- **wild_canid** — dta_states state: coyote, red fox, grey fox and other non-domestic canids.
- **mustelid** — dta_states state: skunks (*Mephitis mephitis*), mink (*Neovison vison*), martens and other mustelids.
- **domestic_dog** — dta_states state: *Canis lupus familiaris*.
- **felid** — dta_states state in `config/cdv.yaml`, pooling `wild_felid` and `domestic_cat`. The published run (METHODS.md §9.2) used `wild_felid`, with the single ailurid sequence merged into it at the alignment level (§9.3); its five states are procyonid, wild_canid, mustelid, domestic_dog and wild_felid.
- **wild groups** — `wild_felid`, `wild_canid`, `mustelid`, `procyonid`, `ailurid`, `ursid`, `viverrid`: the host groups counted as wildlife (`hosts.wild_groups`) for subsampling and reporting.
- **lineage references** — the published reference sequences of the CDV lineages in `config/lineage_references.tsv` (America-1, America-2, Asia-1 to 4, Europe, Europe-Wildlife, Arctic-like, Africa-1, South-America-1). Entered as anchors so clades can be named. Every row is to be verified against its primary source before publication (see Outstanding work in the README); AF259552, listed as America-2 in a patent filing, was excluded as mislabelled (METHODS.md §9.10).
- **captive felid cluster** — a well-supported felid clade on the MCC tree matching a documented captive outbreak: ~1992 (lion and leopard) and ~2015 (four tigers, Indiana) (METHODS.md §9.9).
