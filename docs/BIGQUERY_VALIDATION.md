# BigQuery migration validation — synthetic data only

**In development. Live BigQuery/SQLite parity verified; this is simulation validation, not evidence about Puffy, real customers, causal impact or commercial improvement.**

## Execution record — 2026-11-13

- Project: `premium-silicon-514522-e8`; dataset: `ecommerce_growth_demo`; location: `US`.
- Required ownership label verified on the dataset and all 40 tables: `portfolio_project=ecommerce_growth_analytics`.
- Billing disabled and no account linked before and after execution. No billing/trial, external source integration, dashboard or experiment was activated.
- Official ARM64 CLI: gcloud 593.0.0 / bq 2.1.42. Project Python remains 3.14.8; no Python dependencies added.
- Uploaded 2,312,867 NDJSON bytes: 2,287,858 baseline bytes and 25,009 separate fixture bytes. BigQuery metadata reports 735,612 logical bytes in total; transport and logical storage sizes differ.
- Job metadata confirms 40 load jobs and 180 successful query jobs across both attempts and the isolated diagnostic; zero server-reported job errors. Total processed query bytes across those jobs: 7,622,344. This is processed usage, not a claim about billed bytes or future cost.
- Exactly 40 explicit-schema batch loads, eight baseline tables plus four isolated eight-table validation groups; no baseline contamination or append loads.
- 96/96 full-result comparisons passed, each preceded by a successful server dry run; one additional baseline-summary preflight dry run passed.
- Numeric dry-run estimates: 96/96; largest 583,207 bytes; sum 3,814,741 bytes (estimates, not actual billed usage). Every query retained the 1,000,000,000-byte ceiling; two concurrent read-only comparisons in the successful full run.
- Local automated suite: 45 tests passed. Mocks remain orchestration tests; the separate 96 comparisons used Google’s live SQL engine.
- Plan SHA-256: `8a82b72925851dab85f1e724280d981938162947afb312c66732a28239a1c432`.
- Baseline fingerprint: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`.
- Combined result-file digest: `c979ca1f42a88f3e6fe527b99283981048152820190360fb60f4c3e3833c72e2` (sorted comparison name, colon, file SHA-256, newline; SHA-256 of concatenation).

Seed **42**, 2,700 sessions, traffic cohort **2026-01-01 to 2026-04-01 exclusive**, observation cutoff **2026-04-16 exclusive**, UTC/USD. The raw baseline, measurement rules and SQLite expected values were not changed to obtain parity.

## Baseline row counts

| Table | BigQuery rows | Duplicate primary keys |
| --- | ---: | ---: |
| ad_spend_daily | 360 | 0 |
| campaigns | 4 | 0 |
| customers | 1,496 | 0 |
| events | 7,170 | 0 |
| order_items | 377 | 0 |
| orders | 377 | 0 |
| refunds | 79 | 0 |
| sessions | 2,700 | 0 |

Baseline total: **12,563 rows**. Separate validation groups: hand 47, duplicate purchase 29, missing transaction ID 28, late arrival 28; **12,695 rows** across all tables. Order transaction IDs are unique. Intentional duplicate *purchase deliveries* have different event IDs and remain only in their fixture.

## Calculated baseline metrics

| Metric | BigQuery result |
| --- | ---: |
| Observed visitors | 1496 |
| Purchasing visitors | 331 |
| Sessions | 2700 |
| Distinct converting sessions | 377 |
| Orders | 377 |
| Session purchase conversion | 13.9630% |
| Merchandise before refunds | $345,007.20 |
| Merchandise refunds | $14,084.25 |
| Net merchandise revenue | $330,922.95 |
| Media spend | $44,259.88 |

Ordered same-session funnel: **2,700 → 2,380 → 1,036 → 677 → 377** (start → product view → cart → checkout → purchase). Baseline skipped/out-of-order sessions: 0. Counts, money and nulls match exactly; floating ratios meet the documented tolerance.

## Financial and attribution reconciliation

| Check | Difference (cents, except order count) |
| --- | ---: |
| Pre-refund merchandise vs source gross less discounts | 0 |
| Merchandise refunds vs source | 0 |
| Net merchandise vs source merchandise less refunds | 0 |
| Campaign spend vs source spend | 0 |
| Paid-attributed plus non-paid-assigned revenue vs total | 0 |
| Paid-attributed plus non-paid-assigned orders vs total | 0 |
| Original order payments vs source | 0 |

| Campaign | Spend | Orders | Net attributed revenue | Net ROAS | Days with spend and zero attributed orders |
| --- | ---: | ---: | ---: | ---: | ---: |
| syn_google_prospecting | $11,356.56 | 49 | $42,447.72 | 3.7377 | 48 |
| syn_google_retargeting | $11,670.38 | 56 | $50,380.26 | 4.3169 | 46 |
| syn_meta_prospecting | $10,091.24 | 41 | $33,420.01 | 3.3118 | 54 |
| syn_meta_retargeting | $11,141.70 | 57 | $46,936.64 | 4.2127 | 47 |

Direct and organic activity remains separately reported without paid campaign assignment; their CAC/ROAS is null, not zero. Direct may reflect missing attribution or prior paid exposure. Organic does not imply costless acquisition. Same-session attributed revenue is not incremental revenue.

## Eight scenarios × twelve comparisons

| Scenario | Passed comparisons | Event audit reasons |
| --- | ---: | --- |
| baseline | 12/12 | accepted: 7170 |
| duplicate_purchase | 12/12 | accepted: 1, duplicate_purchase: 1 |
| hand | 12/12 | accepted: 20 |
| hand_early | 12/12 | accepted: 15, not_yet_available: 5 |
| hand_reprocessed | 12/12 | accepted: 20 |
| late_arrival | 12/12 | accepted: 1 |
| late_before | 12/12 | not_yet_available: 1 |
| missing_transaction_id | 12/12 | missing_transaction_id: 1 |

The independent hand example reproduces four orders across three converting sessions and $325.00 net merchandise revenue, including multiple items and partial refunds. Its early cutoff has one strict-funnel purchase; the full/reprocessed cutoff has two. Duplicate deliveries are retained in raw storage and one is excluded analytically; missing IDs are quarantined with a reason. The late view is unavailable before ingestion and accepted afterward. Reprocessing uses unchanged raw tables and does not append data.

## Interrupted attempt and recovery

The initial four-worker run recorded 81 passing comparisons before a CLI error on `late_arrival/quality`. Available job metadata showed no server errors. That same query passed in isolation, then a complete two-worker rerun passed all 96 comparisons. The precise cause of the original CLI failure remains unknown; it was not a demonstrated SQL discrepancy or sandbox rejection. No tables were reloaded and no expected values were changed. The interrupted run and diagnostic retry used additional query allowance beyond the final 96-query run.

## Retention and limits

- Observed table expiration range (UTC): **2026-11-19T22:43:31+00:00** to **2026-11-19T22:49:50+00:00**. Dataset default: seven days; demo tables are temporary.
- Current sandbox limits and rerun precautions are in [the migration guide](BIGQUERY_MIGRATION.md#sandbox-restrictions-and-retention). Successful small-data execution does not establish remaining lifetime quota or production readiness.
- No real GA4, Shopify, Google Ads, Meta Ads, Hotjar or Tableau integration was run. Identity, same-session attribution, absent landing pages and incomplete historical ingestion remain documented simulation limitations.
- No result discrepancies were found. The bundled bq library emitted a compatibility warning; authenticated operations nevertheless succeeded. Empty-file loads and production-scale workloads were not exercised.
- Raw cloud result files, metadata, load receipts and local configuration stay ignored. This reviewed summary is committed; no tokens or credential files are included.

Reproduce with the commands in [BIGQUERY_MIGRATION.md](BIGQUERY_MIGRATION.md#reproducing-the-cloud-workflow). Re-running `prepare` resets local verification status; a past result file alone does not verify a new plan.
