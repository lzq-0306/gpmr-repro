# Public release readiness

Audit date: 28 August 2026.

## Verified

- The package installs as an editable Python package from `pyproject.toml`.
- The sampler unit test passes.
- The frozen public comparison verifies 13 conditions, 45
  dataset--classifier blocks, and 12 significant paired contrasts.
- Internal V1--V12, HEO, and CFSE implementations and results are excluded.
- The MC-CCR implementation and unlicensed source datasets are not redistributed.

## License decision

The copyright holder approved the MIT License on 28 August 2026. Copyright is
held by Zhengqi Liu. The full license text and package metadata are present.

## Remaining release actions

The public repository was created at
`https://github.com/lzq-0306/gpmr-repro`. The `main` branch, MIT license, and
release commit were verified after publication. The manuscript data-availability
statement was updated to cite the repository.

An immutable Zenodo release remains optional but is recommended before final
publication so the paper can cite a versioned DOI rather than only a mutable
GitHub branch.
