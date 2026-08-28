# Public-baseline provenance audit

The main comparison admits a baseline only when its algorithm is publicly
published and the experiment uses an authors' implementation or a maintained,
widely used public-library implementation. Compatibility adapters may bridge
obsolete Python APIs, but may not replace the algorithm body.

| Experiment key | Method | Implementation used | Decision |
|---|---|---|---|
| `none` | No resampling | scikit-learn training pipeline | Keep |
| `ros` | Random over-sampling | imbalanced-learn | Keep |
| `rus` | Random under-sampling | imbalanced-learn | Keep |
| `allknn` | AllKNN | imbalanced-learn | Keep |
| `smote` | SMOTE | imbalanced-learn | Keep |
| `borderline_smote` | Borderline-SMOTE | imbalanced-learn | Keep |
| `global_cs` | Global-CS | authors' public `multi-imbalance` source | Keep |
| `mdo` | MDO | authors' public `multi-imbalance` source | Keep |
| `soup` | SOUP | authors' public `multi-imbalance` source | Keep |
| `mc_ccr` | MC-CCR | authors' public MC-CCR repository | Keep |
| `gmm_sampling` | GMMSampling | authors' public `multi-imbalance` GMM branch, commit recorded by the adapter | Keep |
| `gpmr_v3` | GPMR | proposed method | Keep |
| `kde_reconstructed` | KDE sampling | independent implementation following the published method description; original comparator source was unavailable | Keep, explicitly labelled as an independent reproduction |

Only the methods listed above are present when ranks, Friedman statistics, and
Holm-adjusted paired tests are computed.
