# Third-party license audit

Audit date: 28 August 2026.

| Component | Frozen use | License evidence | Release decision |
|---|---|---|---|
| imbalanced-learn 0.14.2 | ROS, RUS, AllKNN, SMOTE, Borderline-SMOTE | Upstream package metadata and repository identify the MIT License | Install as a dependency; do not vendor |
| multi-imbalance 0.0.14 | Global-CS, MDO, SOUP | MIT `LICENSE` is present in the preserved source | May be redistributed only with copyright and MIT notice retained |
| multi-imbalance GMM branch | GMMSampling | Preserved branch contains the same MIT `LICENSE` | May be redistributed only with copyright and MIT notice retained; retain the frozen source identity |
| MC-CCR author snapshot | MC-CCR | No license file was present in the preserved repository snapshot and no explicit software license was verified | Do not redistribute the implementation without author permission; provide retrieval instructions or request permission |
| Independent KDE implementation | KDE comparison | Locally written from the published description rather than copied author code | May be released under the authors' chosen license, with the independent-implementation disclosure retained |
| GPMR | Proposed method | Author-owned code | Authors must choose a repository license before public release |

Absence of an explicit license is not permission to redistribute source code.
Consequently, the public package currently contains results and configuration
for MC-CCR but not its algorithm body. The same rule applies to processed data
copied from an unlicensed third-party repository: checksums and acquisition
instructions may be published, but redistribution requires a separate data or
repository license determination.
