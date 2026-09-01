# GPMR reproducibility package

This package contains the implementation and frozen result summaries for
Graph Posterior Mass Rebalancing (GPMR). It intentionally excludes exploratory
predecessors and development-only methods.

Copyright (c) 2026 Zhengqi Liu. The GPMR implementation is released under the
MIT License; see `LICENSE`. Third-party methods and datasets retain their own
licenses and are not redistributed where permission was not verified.

Public repository: <https://github.com/lzq-0306/gpmr-repro>

## Install

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[test,figures]"
```

## Data layout

Download the 15 public datasets from the sources reported in the manuscript and
place each processed numeric table at the path in `config/datasets.json`. Every
CSV must contain a `target` column and numeric predictor columns. Preparation
routes are listed below; the third-party baseline and redistribution boundaries
still prevent describing this as a complete one-command reproduction archive.

After obtaining the processed files, verify them with:

```powershell
.venv\Scripts\python.exe scripts/audit_datasets.py
```

The expected dimensions, provenance descriptions, and SHA-256 values are in
`config/dataset_checksums.json`.

Preparation routes are intentionally separated by provenance:

```powershell
# Page Blocks and Statlog Landsat from the official UCI API
.venv\Scripts\python.exe scripts/prepare_uci_numeric.py --dataset all

# Dry Bean from the official UCI ZIP downloaded by the user
.venv\Scripts\python.exe scripts/prepare_dry_bean.py --archive PATH_TO_ZIP --output data/dry-bean

# Twelve exact KEEL-style benchmark files acquired from the MC-CCR author repository
.venv\Scripts\python.exe scripts/prepare_mcccr_data.py --source PATH_TO_ORIGINAL_DAT_DIRECTORY --output data
```

The MC-CCR repository identified by the original paper is
`https://github.com/michalkoziarski/MC-CCR`. Its source snapshot did not contain
an explicit license during this audit, so this package does not mirror or
redistribute those files.

## Run GPMR

```powershell
.venv\Scripts\python.exe scripts/run_gpmr_benchmark.py
```

This executes 10 repeats of stratified five-fold cross-validation with CART,
kNN, and random forest. Scaling is fitted only on each training fold. The
categorical feature vocabulary is fixed when the benchmark CSV is prepared,
before the cross-validation splits; it is not a fold-fitted encoder. The
default GPMR settings are `k=7`, `rounds=16`, bounded mass, and linear
same-class realization.

## Verify frozen claims

```powershell
.venv\Scripts\python.exe scripts/verify_frozen_results.py
```

The `results/public_comparison` directory contains GPMR, 13 documented
comparison methods, and No resampling. Baseline provenance and exact settings
are documented alongside the CSV files.

`holm_45_blocks.csv` records the dependent 45-block analysis.
`holm_dataset_level.csv` and `friedman_dataset_level.csv` record the primary
15-dataset analysis. The verification command recomputes the latter from the
frozen block scores: six of 14 Holm comparisons are significant. It must not be
read as superiority over every baseline.

`results/component_ablation` separately contains component block scores and
Holm comparisons at 45-block and 15-dataset levels. The same command recomputes
both; no component comparison survives correction. These variants never enter
the public-method ranks. `results/matched_profile_control` contains the stricter
within-class mass-permutation control; its dataset-level result is directional
but not significant (`p=0.0730`). Re-run it with:

```powershell
.venv\Scripts\python.exe scripts/run_matched_profile_control.py
```

## Reproducibility boundary

The frozen aggregate comparison results and GPMR runner are included. Exact
one-command regeneration of every third-party baseline additionally requires
redistribution/license review of the referenced author implementations. Until
that review and end-to-end reproduction validation are complete, this is a minimal
verification package rather than a complete archival reproduction bundle.

See `THIRD_PARTY_LICENSE_AUDIT.md` before redistributing any third-party source
or processed dataset.
