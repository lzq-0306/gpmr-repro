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

1. Run the unit test and frozen-result verifier again.
2. Create the public repository or archival deposit.
3. Verify the public URL from a clean environment.
4. Replace the manuscript's provisional data-availability wording with the
   verified URL and rebuild the submission archive.
