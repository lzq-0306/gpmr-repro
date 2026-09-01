# Public release readiness

Audit date: 28 August 2026.

## Verified

- The package installs as an editable Python package from `pyproject.toml`.
- The sampler unit test passes.
- The frozen comparison verifies 15 conditions, 45 dataset--classifier blocks,
  and six of 14 Holm-adjusted dataset-level contrasts.
- Internal V1--V12, HEO, and CFSE implementations and results are excluded.
- The MC-CCR implementation and unlicensed source datasets are not redistributed.

## License decision

The copyright holder approved the MIT License on 28 August 2026. Copyright is
held by Zhengqi Liu. The full license text and package metadata are present.

## Remaining release actions

The public repository is `https://github.com/lzq-0306/gpmr-repro`. The current
release synchronizes the manuscript's comparison, component, and matched-profile
evidence while excluding internal V1--V12, HEO, and CFSE development tracks.

An immutable Zenodo release remains optional but is recommended before final
publication so the paper can cite a versioned DOI rather than only a mutable
GitHub branch.
