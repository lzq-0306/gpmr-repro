# Reproducible baseline configuration

All preprocessing is fitted only on the standardized training fold. The shared
protocol is 5-fold stratified cross-validation repeated 10 times with split
seed 42. A method seed of `42 + split_index` is used when the implementation is
stochastic. The target strategy is the implementation's multiclass default
unless an explicit setting is shown below.

| Key | Original method/source | Code actually executed | Frozen experimental settings |
|---|---|---|---|
| `none` | No resampling | No sampler | Training fold unchanged |
| `ros` | Random over-sampling; standard baseline | imbalanced-learn 0.14.2 `RandomOverSampler` | `sampling_strategy='auto'`, seeded per split |
| `rus` | Random under-sampling; standard baseline | imbalanced-learn 0.14.2 `RandomUnderSampler` | `sampling_strategy='auto'`, seeded per split |
| `allknn` | Repeated edited-nearest-neighbor cleaning (Tomek, 1976; Wilson, 1972) | imbalanced-learn 0.14.2 `AllKNN` | `n_neighbors=3`, `kind_sel='all'`, `allow_minority=True` |
| `smote` | Chawla et al. (2002), DOI 10.1613/jair.953 | imbalanced-learn 0.14.2 `SMOTE` | `k_neighbors=3`, `sampling_strategy='auto'`, seeded per split |
| `borderline_smote` | Han et al. (2005), Borderline-SMOTE | imbalanced-learn 0.14.2 `BorderlineSMOTE` | `k_neighbors=3`; remaining library defaults (`m_neighbors=10`, kind 1), seeded per split |
| `global_cs` | Zhou and Liu (2006), *On Multi-Class Cost-Sensitive Learning* | authors' `multi-imbalance` 0.0.14 source via compatibility adapter | `shuffle=True` |
| `mdo` | Abdi and Hashemi (2016), DOI 10.1109/TKDE.2015.2458858 | authors' `multi-imbalance` 0.0.14 source via compatibility adapter | `k=5`, `k1_frac=0.4`, `prop=1`, seeded per split |
| `soup` | Janicka et al. (2019), DOI 10.2478/amcs-2019-0057 | authors' `multi-imbalance` 0.0.14 source via compatibility adapter | `k=7`, `shuffle=True`, automatic majority/intermediate/minority division |
| `mc_ccr` | Koziarski et al. (2021), arXiv:2004.03406 / authors' MC-CCR repository | authors' archived `algorithms.py` via compatibility adapter | `energy=0.25`, `cleaning_strategy='translate'`, `selection_strategy='proportional'`, `p_norm=1`, `method='sampling'`, seeded per split |
| `gmm_sampling` | Naglik and Lango (2024), DOI 10.1007/s10994-023-06416-8 | authors' `multi-imbalance` GMM branch, commit `aff0cafe` | author defaults: likelihood 0, `k_neighbors=7`, undersampling on, components 1--automatic, validation fraction 0.25, full covariance, `n_init=10`, seeded per split |
| `kde_reconstructed` | KDE comparator described by Naglik and Lango (2024) | independent reproduction retained in the experimental archive | classwise Gaussian KDE; Scott bandwidth `n^(-1/(d+4))`; each class grown to largest-class size; seeded per split |

## Source identities

- Runtime: Python environment in `environment-freeze.txt`; imbalanced-learn
  0.14.2, scikit-learn 1.9.0, NumPy 2.5.2, SciPy 1.18.1, pandas 2.3.3.
- The vendored `multi-imbalance` snapshot identifies itself as package 0.0.14.
  Its upstream repository is <https://github.com/damian-horna/multi-imbalance>.
- The local archive did not preserve Git metadata for `multi-imbalance` or
  MC-CCR. Reproducibility therefore relies on vendored source plus SHA-256,
  rather than claiming an unrecoverable commit identifier.
- SHA-256: Global-CS `E153036177463915B3257C399D5B6A679E66124C7256351279BD6241659F3F41`;
  MDO `C33B830D61D7B6787882D1F6592B377AE345BF34796E684EA83AD19172402F19`;
  SOUP `62AE15EABB89EDE9DB4996407E355AA99DFACEED8AB021A2B903B5BCA3FC0EA7`;
  MC-CCR `A500844B0D0535F083CB4117BE93275347147A4D8C08F66D313C32DBD86FCABE`;
  GMMSampling `5134A5FFF4FBC77E2F32D7C9AA570B6158E91297B166624E38BB808E07A4DF9E`;
  KDE reproduction `99C3CCC2206E427432D9EED96496031B88A9126C2F39E9550D51F9D805E3FB92`.

## Fairness note

The `kde_reconstructed` implementation is not represented as author code. It
is an independent implementation of the published comparator concept. The
other advanced methods execute preserved author algorithm bodies; adapters
only bridge obsolete package APIs and restore deterministic random-state use.
