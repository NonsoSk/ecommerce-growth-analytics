# Milestone 2 — SYNTHETIC-DATA ANALYSIS

**In development. Fictional simulation only; not findings about real customers. No causal effects, commercial improvements or successful experiments are claimed.**

## Reproduction and provenance

Run `.venv/bin/python scripts/run_analysis.py` from the repository root. It verifies or generates the baseline, loads a fresh constrained SQLite database, exports CSVs, exercises quality fixtures, renders this report to the ignored output folder and runs the complete test suite. The committed report is a reviewed copy; reruns do not overwrite it.

Seed **42**; configured sessions **2700**; schema/generator version **1**. UTC cohort **[2026-01-01, 2026-04-01)**; exclusive observation cutoff **2026-04-16**. Currency: USD. SQLite **3.50.4**; Python **3.14.8**.

Canonical data SHA-256: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`. This hashes sorted table names and their original row order using the generator's canonical JSON serialization. Per-table input hashes and SQL hashes are recorded in ignored `data/generated/analysis/run_metadata.json`.

Generated CSVs and SQLite database are under `data/generated/analysis/`. Blank ratio cells mean null, not zero. Cohort dates without sessions remain in daily output; future dates are explicitly marked not_yet_observed. See [SQL pipeline documentation](../docs/SQL_PIPELINE.md) for all export grains and caveats.

## Calculated summary

| Metric | Value |
| --- | --- |
| Eligible sessions | 2700 |
| Observed visitors (includes nonbuyers) | 1496 |
| Purchasing visitors | 331 |
| First observed purchasers | 331 |
| Converting sessions (order ledger) | 377 |
| Paid orders | 377 |
| Order-based purchase conversion | 13.96% |
| Merchandise revenue after discounts, before refunds | $345,007.20 |
| Merchandise refunds | $14,084.25 |
| Net merchandise revenue | $330,922.95 |
| Pre-refund merchandise AOV | $915.14 |
| Net revenue per session | $122.56 |
| Paid media spend | $44,259.88 |
| Same-session paid-attributed net revenue | $173,184.63 |
| Paid-attributed first observed purchasers | 180 |
| Net paid ROAS | 3.91x |
| Observed paid-media CAC proxy | $245.89 |
| Sessions with immature refund windows | 0 |

Purchase conversion counts distinct sessions with at least one valid order, not order rows; a session with multiple orders contributes once to conversion and all of its orders to order count. Orders are counted independently of purchase-event delivery. The strict funnel below requires a valid linked purchase event. Their totals agree in the clean baseline; missing tracking would create a visible discrepancy, not erase ledger revenue.

## Ordered, same-session funnel

| Transition | Sessions at prior step | Sessions at next step | Loss count | Step conversion |
| --- | --- | --- | --- | --- |
| Session → product | 2700 | 2380 | 320 | 88.15% |
| Product → cart | 2380 | 1036 | 1344 | 43.53% |
| Cart → checkout | 1036 | 677 | 359 | 65.35% |
| Checkout → purchase | 677 | 377 | 300 | 55.69% |

Skipped/out-of-order sessions: **0**. Repeated steps count once; chronology and the session_start prefix are required. No cross-session stitching is performed.

## Funnel by available dimensions

| Dimension | Segment | Sessions | Views | Carts | Checkouts | Purchases | View → cart | Session → purchase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| device | desktop | 867 | 759 | 375 | 248 | 161 | 49.41% | 18.57% |
| device | mobile | 1833 | 1621 | 661 | 429 | 216 | 40.78% | 11.78% |
| source | direct | 533 | 478 | 218 | 135 | 78 | 45.61% | 14.63% |
| source | google | 809 | 708 | 300 | 193 | 105 | 42.37% | 12.98% |
| source | meta | 684 | 610 | 263 | 180 | 98 | 43.11% | 14.33% |
| source | organic | 674 | 584 | 255 | 169 | 96 | 43.66% | 14.24% |

Landing page is absent from the source schema. No landing-page analysis or invented page labels are included. Source here means channel; source/medium and click IDs are also absent.

## Campaign totals — same-session attribution

| Campaign | Spend | Orders | Net revenue | First observed buyers | Net ROAS | CAC proxy | Days with spend and zero attributed orders |
| --- | --- | --- | --- | --- | --- | --- | --- |
| syn_google_prospecting | $11,356.56 | 49 | $42,447.72 | 42 | 3.74x | $270.39 | 48 |
| syn_google_retargeting | $11,670.38 | 56 | $50,380.26 | 54 | 4.32x | $216.12 | 46 |
| syn_meta_prospecting | $10,091.24 | 41 | $33,420.01 | 35 | 3.31x | $288.32 | 54 |
| syn_meta_retargeting | $11,141.70 | 57 | $46,936.64 | 49 | 4.21x | $227.38 | 47 |

These are ratios of summed values, not averages of daily ratios. CAC includes media cost only, uses first-observed purchasers, and is not lifetime or fully loaded CAC. Missing-spend days suppress campaign aggregate ratios. Spend-only and conversion-only keys are retained; no spend is assigned to individual events or devices.

## Activity not attributed to paid campaigns

| Channel | Sessions | Orders | Net revenue | First observed buyers |
| --- | --- | --- | --- | --- |
| direct | 533 | 78 | $69,532.62 | 67 |
| organic | 674 | 96 | $88,205.70 | 84 |

Direct is not attributed to a paid campaign under the current same-session model; it may include missing attribution or prior paid exposure. Organic does not imply zero acquisition cost: content, SEO and other costs are absent from this dataset. Paid-campaign CAC/ROAS are not assigned to either category. Direct orders stay direct rather than inheriting an earlier paid session.

## First observed versus returning visits

| Visit type | Sessions | Distinct visitors | Purchasing visitors | Orders | First observed purchasers | Conversion |
| --- | --- | --- | --- | --- | --- | --- |
| first_observed_visit | 1496 | 1496 | 214 | 214 | 214 | 14.30% |
| returning_visit | 1204 | 659 | 140 | 163 | 117 | 13.54% |

Visitors can appear in both rows over time; distinct-visitor counts across these rows are not additive. First visit and first purchase are different events. No pre-simulation history exists, so first observed never proves first-ever.

## Data quality and reconciliation

Automated suite: **42 tests, 0 failures, 0 errors**. Independent hand-calculated fixtures supplement source-total and baseline checks.

| Baseline event disposition | Rows |
| --- | --- |
| accepted | 7170 |

| Purchase/order reconciliation status | Rows |
| --- | --- |
| matched | 377 |

| Control (cents for money) | Source | SQL | Difference |
| --- | --- | --- | --- |
| sessions | 2700 | 2700 | 0 |
| orders | 377 | 377 | 0 |
| merchandise_cents | 34500720 | 34500720 | 0 |
| refunds_cents | 1408425 | 1408425 | 0 |
| net_revenue_cents | 33092295 | 33092295 | 0 |
| spend_cents | 4425988 | 4425988 | 0 |
| paid_plus_unpaid_net_cents | 33092295 | 33092295 | 0 |

Baseline late events: **0**. The baseline is deliberately clean; zero detections do not imply real tracking would be complete. Event payloads contain no revenue amount, so transaction matching validates purchase coverage, while money is independently reconciled from items, charges and refunds.

### Separate quality-fixture results

| Case | Raw event | Reason | Disposition |
| --- | --- | --- | --- |
| duplicate_purchase | fixture_dup_a | accepted | included |
| duplicate_purchase | fixture_dup_b | duplicate_purchase | quarantined |
| missing_transaction_id | fixture_missing | missing_transaction_id | quarantined |
| late_arrival | fixture_late | accepted | included_late_restatement |

Raw records are retained. Duplicate delivery is quarantined, missing IDs are quarantined, and late valid records restate the occurrence cohort. The independent SQL fixture proves late reprocessing changes ordered purchases from 1 to 2 after arrival, then stays at 2 on repeated execution; its four ledger orders are unchanged. Its two orders in one session, multiple items and cumulative partial refunds reconcile to 35,000 cents before refunds, 2,500 cents refunds and 32,500 cents net. Separate tests cover skipped steps and spend-only/conversion-only keys.

## Observations to investigate — not recommendations of proven impact

1. **Journey loss:** the largest absolute step loss is Product → cart: 2,380 prior-step sessions, 1,036 next-step sessions, a loss of 1,344 (56.47%). Limitation: progression probabilities are hard-coded and journeys stop at the first failed step. Alternatives include ordinary browsing intent or missing event instrumentation in a future real dataset. Next investigation: validate step coverage and segment product intent before proposing a product-page experiment.

2. **Device difference:** mobile has 216/1833 ordered purchases per session (11.78%); desktop has 161/867 (18.57%). Limitation: the generator explicitly sets different mobile and desktop progression probabilities. Channel mix and chance are alternative explanations for the exact realized gap; this is not proof of a mobile usability defect. Next investigation: compare like-for-like source and repeat-visit cohorts, then validate instrumentation before any usability hypothesis.

3. **Acquisition needs cautious interpretation:** 195 campaign-days incurred positive spend without an attributed order, out of 360 campaign-day keys. Limitation: spend and traffic are independently simulated; this cannot establish waste or incrementality. Alternatives include small daily samples and purchases in later direct sessions under the same-session attribution rule. Next investigation: review cohort maturity and attribution sensitivity; do not move budgets based on this simulation.

## Limits and next scope

The full default refund window is mature only under the invented maximum 14-day delay plus ingestion allowance. Earlier cutoffs are provisional; unfinished sessions are excluded, future event arrivals are deferred, and refunds are included only when available. Orders/spend are static snapshots without ingestion timestamps, so this is not a historical warehouse backtest. Failed payments, cancellations, full returns, true lifetime customer history, landing pages, real consent loss and production-scale validation remain absent.

Historical cloud verification: the synthetic BigQuery demonstration passed 96/96 SQLite comparisons on November 13, 2026. This report does not check current cloud availability; recorded demo-table expiration is November 19, 2026 UTC. Local Tableau dashboards completed documented synthetic-data acceptance on November 18, 2026. GA4, Shopify, Google Ads, Meta Ads and Hotjar ingestion remain unimplemented. No A/B experiment or paid service was activated. See docs/BIGQUERY_VALIDATION.md for dated evidence, dashboard/INTERACTION_CHECKS.md for completed acceptance evidence and docs/FOLLOW_UP_BACKLOG.md for proposed investigations.
