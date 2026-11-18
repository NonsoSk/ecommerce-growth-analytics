# Private portfolio release — evidence index

**Synthetic only; Tableau synthetic-scope acceptance completed November 18, 2026. No publication, real-source ingestion or executed experiment.**

| Evidence | What it establishes | Limit |
|---|---|---|
| [Measurement plan](../docs/MEASUREMENT_PLAN.md), [review](../docs/MEASUREMENT_REVIEW.md) | Metric definitions, grains, cutoffs, attribution limits | Not real tracking validation |
| [Synthetic validation](../docs/MILESTONE_1_VALIDATION.md) and tests/test_synthetic.py | Determinism, keys, relationships and refund arithmetic | Invented behaviour |
| [SQL report](../reports/MILESTONE_2_ANALYSIS.md), tests/fixtures/sql_hand_calculated.json | Independent expected values and zero reconciliation differences | Synthetic results only |
| [BigQuery validation](../docs/BIGQUERY_VALIDATION.md) | Historical Nov 13 live 96/96 parity with billing disabled | Current cloud availability not checked; recorded expiration Nov 19 UTC |
| [Progress](../PROGRESS.md) and [screenshot review](../dashboard/SCREENSHOT_REVIEW.md) | Dated Tableau rendering/interaction evidence and historical repairs | Later progress supersedes older pending notes |
| [Final checklist](../dashboard/INTERACTION_CHECKS.md) | Passed combinations, resets, empty cases, both isolation directions and relocated close/reopen | User runtime evidence; automated checks separately identified |
| [Build validation](BUILD_VALIDATION.md) | Successful isolated source-only build; 63-file tested-source manifest | Not Tableau UI validation |
| [Case study](../docs/PORTFOLIO_CASE_STUDY.md), [decision report](../dashboard/DECISION_REPORT.md), [protocol](../docs/EXPERIMENT_PROTOCOL.md) | Evidence-linked interpretation and explicitly unexecuted test design | No real causal effect |

## Deliverable and provenance

`SYNTHETIC_Growth_REVIEW.twbx` is the adopted, sanitized, self-contained release. SHA256 `0b14c29630ad70db635e32ea18872a81f70871d2c5868c388a28de2e403e3f9b`. It contains the accepted layout, three baseline CSVs and three byte-identical user-reopened extracts; all data paths are relative. Previous release preserved in `backups/SYNTHETIC_Growth_REVIEW_182481c1f06f.twbx`. See [ACCEPTANCE.md](ACCEPTANCE.md) for provenance, new build checks and limitations.

Baseline fingerprint: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`; seed 42; 90 days; UTC/USD. Core Python is standard-library only; optional Hyper dependencies are pinned separately. Sources for independent verification are included; cloud receipts remain local ignored records. User screenshots are referenced by attachment identifiers in PROGRESS; they are not falsely claimed embedded in this release.

AI assistance: code, SQL, prose and workbook XML were drafted/repaired with assistant support. Independent hand fixtures, executable regression checks, live SQL parity and user UI screenshots review those contributions. No private customer data were used. This is a practical evidence trail, not a claim of an automated AI integration or exhaustive model-level audit.
