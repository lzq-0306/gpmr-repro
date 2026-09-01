# Public-baseline provenance audit

The main comparison admits a baseline only when its algorithm is publicly
published and the experiment uses a public implementation or an explicitly
identified reconstruction of a published method. Compatibility adapters may bridge
obsolete Python APIs, but may not replace the algorithm body.

| Experiment key | Method | Implementation used | Decision |
|---|---|---|---|
| `none` | No resampling | scikit-learn training pipeline | Keep |
| `ros` | Random over-sampling | imbalanced-learn | Keep |
| `rus` | Random under-sampling | imbalanced-learn | Keep |
| `allknn` | AllKNN | imbalanced-learn | Keep |
| `smote` | SMOTE | imbalanced-learn | Keep |
| `borderline_smote` | Borderline-SMOTE | imbalanced-learn | Keep |
| `global_cs` | Global-CS | public-toolbox `multi-imbalance` source | Keep |
| `mdo` | MDO | public-toolbox `multi-imbalance` source | Keep |
| `soup` | SOUP | public-toolbox `multi-imbalance` source | Keep |
| `mc_ccr` | MC-CCR | authors' public MC-CCR repository | Keep |
| `gmm_sampling` | GMMSampling | authors' public `multi-imbalance` GMM branch, commit recorded by the adapter | Keep |
| `gdhs_lc_official` | GDHS-LC | authors' repository plus disclosed all-zero-weight numerical guard | Keep |
| `mc_mbrc_reconstructed` | MC-MBRC | independent reconstruction of published Algorithms 1--4 and Equations (5)--(9) | Keep with reconstruction label |
| `gpmr_v3` | GPMR | proposed method | Keep |
| `kde_reconstructed` | KDE sampling | independent implementation following the published method description; original comparator source was unavailable | Keep, explicitly labelled as an independent reproduction |

Only the methods listed above are present when ranks, Friedman statistics, and
Holm-adjusted paired tests are computed.
