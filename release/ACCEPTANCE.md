# Accepted private synthetic portfolio release — November 18, 2026

All documented representative Tableau acceptance requirements are satisfied. This is a synthetic portfolio demonstration, not production tracking, causal evidence or an executed experiment. No push, publication, cloud reload or paid service occurred.

## Provenance and preservation

- User-reopened source: `/private/tmp/ecommerce-growth-portability-20261115/SYNTHETIC_Growth_REVIEW.twbx`, SHA256 `7fd815642dfe6dfa524a91ccfcf747dcde7d1457c2365a461159cc1482bf5959`.
- Adopted permanent release: `release/SYNTHETIC_Growth_REVIEW.twbx`, SHA256 `0b14c29630ad70db635e32ea18872a81f70871d2c5868c388a28de2e403e3f9b`.
- Previous release preserved byte-for-byte: `release/backups/SYNTHETIC_Growth_REVIEW_182481c1f06f.twbx`, SHA256 `182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8b79b1f93c3c`.
- Original draft, ignored workbooks and user-relocated source were not modified.

The adopted layout retains the larger Funnel charts, printed Google/Meta labels and repositioned quality/acquisition KPI cards. All 29 worksheet source references, filters, shelf expressions and mark encodings match the preceding release; top-level calculation formulas are unchanged. All three original Hyper extracts are byte-identical. Tableau had pruned unused worksheet dependencies and normalized inferred count types/parameter metadata; those are retained from its working save.

The source save omitted CSV members while retaining text connection references. The release restores the three matching baseline CSVs for refresh, normalizes all six data references to relative `Data/` paths, and removes workstation fingerprint attributes. Canonical XML matches the user-reopened workbook after precisely those path/fingerprint transformations. No calculation, filter, layout, parameter default or synthetic value was changed in packaging. Defaults remain January 1–March 31 and All selectors. Seven unique members; no quality fixtures.

## Actual checks

| Evidence type | Completed checks |
|---|---|
| User Tableau runtime | Full and filtered views, empty cases, resets, both isolation directions, all channel labels, relocated close/reopen without reconnecting or warnings; see dashboard/INTERACTION_CHECKS.md |
| Analytical equivalence | All 29 sheet contracts and top-level formulas unchanged; three accepted extracts byte-identical |
| Isolated source build | Fresh source-only export at `/private/tmp/ecommerce-adopted-release-20261118`, no ignored draft/probe/data dependency; regenerated baseline and all extracts; 8 SQL/Hyper cases passed |
| Generated accepted layout | 50 expression/filter comparisons passed; 29 worksheets / three dashboard references passed; canonical packaged XML equals sanitized accepted template |
| Portable data | All 90 Overview + 1,187 Funnel + 360 Acquisition rows match restored CSVs in unrelated temporary directories; checked rebuilt package and permanent release separately |
| Targeted regressions | Three adoption-contract tests passed (layout permitted, formula/filter changes detected); one report-review test passed after report/generator status reconciliation |
| Repeatability | Repeated finalization produces byte-identical TWB |

Exact build source snapshot: [ADOPTED_SOURCE_MANIFEST.json](ADOPTED_SOURCE_MANIFEST.json), based on local commit `19e385516bbb3f8a00d8fcea1900c3acbf114d78` plus recorded files. The finalizer hash includes the corrected comparison below. Later report-status wording and its single targeted test are separate from this build snapshot. Historical 51-test results remain in BUILD_VALIDATION.md; no claim that the full suite was rerun for documentation-only changes.

The first adoption attempt stopped at an overly strict contract comparison of Tableau-inferred types and captions. Inspection confirmed formulas and filter references were unchanged. The comparison now checks formulas and source/filter/shelf/mark semantics while preserving Tableau's accepted metadata. Only finalization and remaining downstream validation resumed; successful baseline/extract generation was not repeated. All stages then passed. No expected numerical values were altered.

## Reproduction and limits

```sh
.venv/bin/python scripts/build_dashboard_release.py \
  --hyper-python dashboard/workbooks/.venv-hyper/bin/python
```

See dashboard/README.md for the pinned optional Hyper setup. The command writes a separate `dashboard/workbooks/SYNTHETIC_Growth_REBUILD.twbx`; it does not overwrite the accepted release. It generates analyses using the minimal scaffold, checks their analytical contract against committed `dashboard/templates/accepted_workbook.twb`, binds fresh data, validates and packages the accepted layout. Fresh Hyper binaries may differ; logical rows and canonical workbook XML are the reproducibility criteria.

The final normalized ZIP was not separately reopened in Tableau by the agent. Runtime acceptance is transferred from the user-reopened source using exact extract preservation and canonical XML equivalence under the documented path/fingerprint-only changes, plus a complete relocated data/path check. This distinction is explicit rather than claiming a new UI action. Representative checks are not exhaustive across all possible filter combinations or other Tableau versions. Small authoring viewports may require scrolling.

BigQuery verification remains historical (96/96 on November 13; recorded November 19 expiration); current cloud availability was not queried. GA4, Shopify, advertising and Hotjar ingestion remain unimplemented. The experiment protocol is unexecuted. No further user action is required for this documented synthetic portfolio scope.
