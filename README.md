# GPMR reproducibility package

This package contains the public implementation and frozen result summaries for
Graph Posterior Mass Rebalancing (GPMR). It intentionally excludes exploratory
predecessors and development-only methods.

Copyright (c) 2026 Zhengqi Liu. The GPMR implementation is released under the
MIT License; see `LICENSE`. Third-party methods and datasets retain their own
licenses and are not redistributed where permission was not verified.

## Install

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[test,figures]"
```

## Data layout

Download the 15 public datasets from the sources reported in the manuscript and
place each processed numeric table at the path in `config/datasets.json`. Every
CSV must contain a `target` column and numeric predictor columns. Dataset
download/preparation scripts or immutable archive links must be added before
this package is cited as a one-command reproduction archive.

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
default GPMR settings are `k=7`, `rounds=16`, bounded mass, and linear
same-class realization.

## Verify frozen claims

```powershell
.venv\Scripts\python.exe scripts/verify_frozen_results.py
```

The `results/public_comparison` directory contains only GPMR, 11 public
resampling baselines, and No resampling. Baseline provenance and exact settings
are documented alongside the CSV files.

## Reproducibility boundary

The frozen aggregate comparison results and GPMR runner are included. Exact
one-command regeneration of every third-party baseline additionally requires
redistribution/license review of the referenced author implementations. Until
that review and dataset preparation scripts are complete, this is a minimal
verification package rather than a complete archival reproduction bundle.

See `THIRD_PARTY_LICENSE_AUDIT.md` and `LICENSE_DECISION_REQUIRED.md` before
publishing or redistributing any third-party source or processed dataset.
