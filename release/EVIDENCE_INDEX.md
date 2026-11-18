# Private release candidate — evidence index

**Synthetic only; Tableau final acceptance PENDING. No publication, real-source ingestion or executed experiment.**

| Evidence | What it establishes | Limit |
|---|---|---|
| [Measurement plan](../docs/MEASUREMENT_PLAN.md), [review](../docs/MEASUREMENT_REVIEW.md) | Metric definitions, grains, cutoffs, attribution limits | Not real tracking validation |
| [Synthetic validation](../docs/MILESTONE_1_VALIDATION.md) and tests/test_synthetic.py | Determinism, keys, relationships and refund arithmetic | Invented behaviour |
| [SQL report](../reports/MILESTONE_2_ANALYSIS.md), tests/fixtures/sql_hand_calculated.json | Independent expected values and zero reconciliation differences | Synthetic results only |
| [BigQuery validation](../docs/BIGQUERY_VALIDATION.md) | Historical Nov 13 live 96/96 parity with billing disabled | Current cloud availability not checked; recorded expiration Nov 19 UTC |
| [Progress](../PROGRESS.md) and [screenshot review](../dashboard/SCREENSHOT_REVIEW.md) | Dated Tableau rendering/interaction evidence and historical repairs | Later progress supersedes older pending notes |
| [Final checklist](../dashboard/INTERACTION_CHECKS.md) | Remaining reverse-isolation confirmation, two tooltips, relocated close/reopen | Must pass before final dashboard acceptance |
| [Build validation](BUILD_VALIDATION.md) | Successful isolated source-only build; 63-file tested-source manifest | Not Tableau UI validation |
| [Case study](../docs/PORTFOLIO_CASE_STUDY.md), [decision report](../dashboard/DECISION_REPORT.md), [protocol](../docs/EXPERIMENT_PROTOCOL.md) | Evidence-linked interpretation and explicitly unexecuted test design | No real causal effect |

## Deliverable and provenance

`SYNTHETIC_Growth_REVIEW.twbx` in this directory is the exact existing reviewed candidate, SHA256 `182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c`. It embeds the workbook, three baseline CSVs and three Hyper extracts, uses relative paths and excludes quality fixtures. Original draft and backups remain local/ignored. Rebuilds output a separate REBUILD package and do not inherit visual acceptance automatically.

Baseline fingerprint: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`; seed 42; 90 days; UTC/USD. Core Python is standard-library only; optional Hyper dependencies are pinned separately. Sources for independent verification are included; cloud receipts remain local ignored records. User screenshots are referenced by attachment identifiers in PROGRESS; they are not falsely claimed embedded in this release.

AI assistance: code, SQL, prose and workbook XML were drafted/repaired with assistant support. Independent hand fixtures, executable regression checks, live SQL parity and user UI screenshots review those contributions. No private customer data were used. This is a practical evidence trail, not a claim of an automated AI integration or exhaustive model-level audit.
