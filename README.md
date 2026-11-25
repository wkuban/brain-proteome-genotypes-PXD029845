# Reading donor genotypes from a public brain proteome

Open re-analysis of the post-mortem prefrontal cortex proteome of suicide decedents and controls (Kim et al. 2022, PRIDE **PXD029845**), from raw spectra to figures.

Preliminary work for the MOSAIC-S project (*Multi-Omic Signatures Across the prefrontal–limbic Circuit in medication-naïve Suicide*).

## Why

Proteomic studies of suicide compare small groups of donors. Any inherited difference between donors that happens to be unevenly distributed between the groups can look like a disease marker. This repository shows, on public data, that

1. common germline variants can be read directly from a bulk brain proteome, donor by donor, and
2. one protein reported as a potential suicide marker (GSTT1) varies between donors mainly because of a common gene deletion.

## Main results

**ALDH2\*2 (rs671) carriers identified from the proteome, two independent ways.**
Protein abundance alone predicted 10 carriers among 36 donors. A variant-aware re-search of the raw spectra then identified the variant-specific peptide in all four TMT sets; its reporter ions single out the same 10 donors, with no overlap with the other 26. Carrier status is unrelated to group (5/23 suicide, 5/13 control).

![ALDH2 variant peptide](results/fig_ALDH2_variant_peptide.png)

**GSTT1.** Abundance is bimodal and all GSTT1 peptides shift together, as expected for the common gene deletion. The cluster explains 87% of the variance between donors and 60% of the reported suicide–control difference.

![GSTT1](results/fig_GSTT1_deletion.png)

**The re-analysis reproduces the original one.** 93% of the genes of the original analysis are recovered; donor-level quantities agree (median per-gene correlation 0.75).

![QC](results/fig_qc_agreement.png)

## Data

| | |
|---|---|
| Dataset | Kim MJ et al. *Transl Psychiatry* 12:142 (2022), doi:10.1038/s41398-022-01896-z; PRIDE PXD029845 |
| Samples | prefrontal cortex (BA9/10); 23 suicide decedents, 13 sudden-death controls |
| Design | 4 × TMT 10-plex, 24 high-pH fractions each, Q-Exactive, MS2 quantification; channel 131N = pooled reference |
| Raw files | 96 files, 200 GB, verified against PRIDE SHA-1 checksums |

## Workflow

| Notebook | Step |
|---|---|
| `00_environment_check` | hardware and software report |
| `01_download_raw_data` | download with resume, SHA-1 verification, one folder per TMT set |
| `02_authors_table_sample_map_and_genotype_like_proteins` | TMT set, channel and sex of every sample recovered from the published tables; proteome-wide scan for two-cluster proteins |
| `03_variant_aware_sequence_database` | Swiss-Prot human + 84,003 curated single amino-acid variants (UniProt humsavar) + contaminants + decoys |
| `04_fragpipe_search_setup` | channel annotation, FragPipe workflow, manifests, launchers |
| `05_quality_control_vs_original_analysis` | identifications and donor-level agreement with the original analysis |
| `06_ALDH2_variant_peptide_confirmation` | ALDH2\*2 carriers from reporter ions of the variant peptide |
| `07_GSTT1_deletion_vs_reported_marker` | GSTT1 bimodality, peptide-level consistency, group comparison |

Search: FragPipe 24.0 (MSFragger 4.4.1, MSBooster, Percolator, Philosopher 5.1.3, IonQuant 1.11.20, TMT-Integrator 6.1.3), stock `TMT10` workflow with the database of notebook 03 and the pooled channel as reference. Settings: `config/MOSAIC_TMT10_variants.workflow`.
Run time on a desktop PC (Intel i5-13500, 32 GB RAM): 2 h 26 min for all 96 files, plus 28 min for quantification.

## Reproduce

```
conda env create -f environment.yml
conda activate mosaic-reanalysis
jupyter lab                      # run notebooks 00-04
RUN_SEARCH_ALL_SETS.bat          # FragPipe, headless (Windows)
jupyter lab                      # run notebooks 05-07
```

Paths with spaces break some FragPipe tools; keep the project in a folder such as `C:\MOSAIC_reanaliza_PXD029845`. About 300 GB of free disk space is needed.

## Layout

| Path | Content | In Git |
|---|---|---|
| `notebooks/` | numbered Jupyter notebooks with outputs | yes |
| `config/` | PRIDE file manifest, FragPipe workflow and manifests | yes |
| `results/` | small tables and figures | yes |
| `tools/` | checksum verification, download repair, notebook runner | yes |
| `data_raw/`, `data_external/`, `database/`, `results_large/` | raw files, reference files, FASTA, search output | no (re-created by the notebooks) |

## Limits

- Genotypes are inferred from the proteome; no DNA data exist for this cohort.
- MS2-level TMT quantification compresses ratios, so non-carriers show a background signal and zygosity cannot be assigned.
- The cohort is small and its two groups differ in sex and circumstances of death.

## Authors

Wojciech Kuban — Maj Institute of Pharmacology, Polish Academy of Sciences, Kraków.

## Licence

Code is released under the MIT Licence (`LICENSE`). The public dataset re-analysed here remains under the terms set by its original depositors and must be cited directly (Kim et al. 2022; PRIDE PXD029845).

## Citation

See `CITATION.cff`.
