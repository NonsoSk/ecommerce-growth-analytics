> This records the earlier release build. The adopted-layout build and exact source manifest are documented in [ACCEPTANCE.md](ACCEPTANCE.md); earlier pending UI statements below are historical.

# Release build validation — recorded November 18, 2026

**Synthetic-only local release candidate. Tableau final acceptance remains pending. No cloud request, BigQuery reload, publication or paid service was part of this build.**

## Exact tested source version

The successful run used an isolated source-only export of the staged index based on commit `548dd24912e03fd7a15a7378a8d3618b9a58e545`, with one correction applied before success: `scripts/build_dashboard_release.py` uses `Path.absolute()` instead of `Path.resolve()` for `--hyper-python`. Resolving the interpreter symlink bypassed the virtual environment and caused the first attempt to fail importing tableauhyperapi. The correction retains the environment interpreter. The corrected script was present in the successful build and is included in the local release commit.

[TESTED_SOURCE_MANIFEST.json](TESTED_SOURCE_MANIFEST.json) records SHA-256 values for all 63 included Python/SQL/schema/template/dependency/fixture files. Source-set digest: `8a62dc39d465a8077287bbf7de7b55b8d766a2ecff9f7cd146245ccc511ee1cd`. Cleanup compared all 63 files byte-for-byte with the successful build directory; all matched. Subsequent edits concern documentation/evidence only, not executable sources. The full commit containing this document is the release version; the manifest identifies the exact executable source snapshot without a circular self-referencing commit hash.

This was an index-only clean-checkout-equivalent export, not a clone from GitHub. It contained no ignored original draft, probe, baseline, extracts or Python environment. A previously installed, pinned Hyper environment was explicitly supplied as a tool dependency; fresh dependency installation/network availability was not tested. Tested host: Python 3.14.8, macOS ARM64; optional Hyper 0.0.26479, cffi 2.1.1, pycparser 3.12.

## Recorded checks

| Check | Actual result |
|---|---|
| Local regression suite after report/build changes | 51 tests passed in 5.432 seconds; report renderer agrees with reviewed Markdown |
| Source-only build | Completed with exit code 0; baseline generated, aggregates exported, extracts created; no ignored template dependency |
| SQL/Hyper checks | Eight full/filtered cases passed; all 90 Overview + 1,187 Funnel + 360 Acquisition rows equal |
| Workbook calculations and references | 50 formula/filter comparisons passed; 29 worksheets / 3 dashboards |
| Package validation | Seven unique archive members, relative data paths, successful archive integrity check |
| Relocated data | All 1,637 extract rows match included CSVs when unpacked to unrelated temporary directory |
| Finalization repeatability | Rerunning finalization produced byte-identical TWB |
| Workbook equivalence | Canonical XML of rebuilt package equals existing REVIEW package after removing insignificant whitespace |
| Preservation | 11 original workbook/extract artifact hashes unchanged; release REVIEW is byte-identical to existing REVIEW |

The source-only run was performed under `/private/tmp/ecommerce-clean-release-20261118`. The first corrected attempt was blocked by the execution sandbox's local Hyper socket restriction; the authorized local-socket run completed successfully. These resolved environment issues are not numerical discrepancies. No expectations or simulated values were changed. The unexplained long interruption of the assistant session is not attributed to a build failure: logs and the completed process session report success.

Command used (project paths omitted here for portability):

```sh
.venv/bin/python /path/to/source-only-checkout/scripts/build_dashboard_release.py \
  --hyper-python /path/to/existing/pinned-hyper-environment/bin/python
```

See [dashboard/README.md](../dashboard/README.md) for the normal clean-checkout command and dependency setup. The successful build produced a separate `SYNTHETIC_Growth_REBUILD.twbx`; it did not replace the reviewed candidate. Hyper binaries may differ across fresh creations; logical data and workbook structure are the comparison targets.

## Deliverable and exclusions

Permanent private release candidate: [SYNTHETIC_Growth_REVIEW.twbx](SYNTHETIC_Growth_REVIEW.twbx), SHA256 `182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c`.

Automated relocation is **not** Tableau close/reopen acceptance. Remaining UI evidence is in [INTERACTION_CHECKS.md](../dashboard/INTERACTION_CHECKS.md). BigQuery parity is historical November 13 evidence, with recorded expiration November 19 UTC; current cloud availability was not checked. No repeated build or cloud validation was needed for the final documentation/staging cleanup.
