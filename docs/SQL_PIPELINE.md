# Local SQLite analysis — Milestone 2

**Synthetic-data analysis; in development. BigQuery remains planned and is not implemented.**

## One command

```sh
.venv/bin/python scripts/run_analysis.py
```

The command runs all tests, creates the default baseline only when it is absent, verifies existing input hashes and counts, loads a fresh SQLite database, exports results, exercises separate quality fixtures and renders a report. Existing baseline JSON is never rewritten. A partial baseline without a manifest or a hash mismatch fails visibly; inspect it rather than silently repairing or overwriting it. To intentionally use a different synthetic configuration, first use the documented generator command, then rerun analysis.

Optional `--cutoff 2026-03-01` sets an exclusive UTC-midnight as-of date. The 90-day cohort remains the manifest cohort. Only ended sessions, available events and available refunds are included. Daily future dates retain a not_yet_observed label; they must not be interpreted as real zero-traffic dates. The default report uses the full modeled refund observation period.

No dependencies were added. Verified runtime: Python 3.14.8 and bundled SQLite 3.50.4. SQL uses SQLite STRICT tables (requires SQLite 3.37+), CTEs and window functions.

## Loading, constraints and reruns

`00_schema.sql` defines every raw column explicitly with primary/foreign keys, unique transaction IDs, USD checks, integer amounts and arithmetic checks. Composite foreign keys enforce matching order/session/customer and refund/item/order relationships. Additional load checks validate line-to-order reconciliation, cumulative refund limits, financial chronology, channel and visitor links. Raw event transaction/session FKs are deliberately not enforced: invalid links must be retained and audited rather than lost during load. Event IDs remain unique; duplicate transaction deliveries have distinct event IDs.

The database is a copied snapshot of raw JSON, not a transformed replacement for it. Temporary databases are built and validated, then replace the prior generated output; records are never appended to an existing database. The loader refuses a nonempty destination file. Reruns produce the same CSV/metadata/report bytes, and database row counts do not grow. Input hashes, output tests and reconciliation run before replacement. An exception leaves prior validated outputs intact, except that file replacement is atomic per file rather than a multi-file transaction.

`01_models.sql` defines parameterized views for complete cohort sessions, raw event dispositions, order finance, session finance and strict ordered funnels. Financial views aggregate items and refunds independently before the order join. Ledger purchases do not depend on event availability. First observed purchases are ranked globally before selecting the reporting cohort.

## Exports (all ignored under data/generated/analysis/)

| Output | Grain / purpose |
| --- | --- |
| analysis.sqlite | Constrained raw snapshot plus SQL views and observation parameters |
| daily.csv | One cohort date; ledger sessions, orders, merchandise after discounts, refunds, net revenue, ratios, maturity and observation status |
| funnel.csv | One whole-cohort row; ordered prefix counts and step rates |
| funnel_segments.csv | Dimension × segment for device and channel; rows across dimensions are not additive |
| funnel_exceptions.csv | One affected session, with missing/nonchronological predecessor reason and eligible step times |
| campaign_daily.csv | Union of spend/outcome campaign-day keys; same-session attributed outcomes and null reasons |
| campaign_summary.csv | Campaign totals; ratios recomputed from summed values, suppressed if spend coverage is incomplete |
| unattributed.csv | Channel not assigned to a paid campaign under the current attribution model |
| reconciliation.csv | One order-side record plus one record per excluded purchase-event delivery; record_type distinguishes grains |
| visitors.csv | First-observed/returning visit type; visitors can appear in both groups |
| quality.csv | One raw event; accepted, deferred or quarantined, reason plus independent late-arrival flag |
| fixture_quality.csv | Case × event for separate hand-authored quality fixtures, never mixed into baseline |
| reconciliation_controls.json | Independent source totals, SQL totals and differences |
| run_metadata.json | Seed, size, dates, versions, table hashes, canonical data fingerprint, SQL hashes, test result and summary |
| MILESTONE_2_ANALYSIS.md | Recomputed report; reviewed default copy is committed under reports/ |

CSV money columns remain integer cents; ratio/mean columns are floating-point display calculations. Blank fields mean SQL null. Zero denominators use `NULLIF`; daily/campaign outputs include explicit reasons, while funnel denominator columns identify empty stages. Paid-campaign CAC/ROAS are not assigned to direct/organic; direct may hide attribution or prior paid exposure, and organic acquisition can have unmeasured costs. Do not average ratios across dates or sum distinct visitors across overlapping visit-type groups.

The audit covers the full raw event snapshot; reporting views restrict to complete cohort sessions. Deferred includes future events outside the as-of view. Audit statuses do not silently delete events. Duplicate purchase deliveries are ranked by ingestion time then event ID **after structural/order-link checks**; an invalid earlier record cannot suppress a valid later one. Missing IDs, unmatched orders, mismatched sessions/times and invalid event chronology are quarantined. Late valid events are included once available and assigned to occurrence/session cohort, never ingestion day.

## Independent fixture arithmetic

`tests/fixtures/sql_hand_calculated.json` is hand-authored, independent of random generation. It has five sessions, three visitors, four orders in three converting sessions, five item lines, four refunds and four spend rows. Original merchandise after discount is 15,000 + 5,000 + 7,000 + 8,000 = **35,000 cents**. Refunds are 1,000 + 500 + 500 + 500 = **2,500 cents**; net is **32,500 cents**. Spend is 1,000 + 2,000 + 0 + 500 = **3,500 cents**.

One Google session has two orders with 18,000 net cents after refunds, but one converting session and one first-observed purchaser; its ROAS is 18 and CAC proxy 1,000 cents. A Meta conversion day deliberately has no spend row, so its ROAS/CAC are null. Strict full-observation funnel counts are 4 views, 3 carts, 2 checkouts, 2 converting funnel sessions. There are two sessions with missing/out-of-order predecessors. An earlier cutoff defers a late view; reprocessing raises funnel purchases from 1 to 2 without duplicating raw records. Ledger orders remain four.

The original event-quality fixtures are loaded unchanged into **separate** databases using this fixture's matching `fixture_session`/`fixture_tx` context. This demonstrates duplicate, missing-ID and late-arrival handling through the same SQL audit used by baseline. These cases are not appended to the baseline or treated as baseline findings.

## BigQuery migration considerations — prepared locally, cloud unverified

Milestone 3 now provides explicit schemas, GoogleSQL and a guarded CLI workflow in `bigquery/`. See [BIGQUERY_MIGRATION.md](BIGQUERY_MIGRATION.md) for prerequisites and actual validation status. No BigQuery execution or parity is claimed.

Preserve the same grains and acceptance fixtures before porting. Map integer cents to INT64, UTC timestamps to TIMESTAMP, day keys to DATE, and ratios to guarded numeric division (for example SAFE_DIVIDE). Replace SQLite date/julianday functions and the recursive calendar with explicit date/timestamp operations and a generated date array or date dimension. Window ordering and same-session rules must stay explicit.

Do not rely on SQLite's enforced constraints to exist automatically in a warehouse: reimplement key, relationship, amount and freshness assertions as validation jobs. Add ingestion metadata for orders, spend and sessions before attempting true historical as-of reporting. Consider partitioning by occurrence/spend date, clustering by frequently joined IDs, late-data reprocessing and cost controls only during a separately authorized warehouse milestone. Validate identical hand-calculated outputs and source control totals before accepting a port. No cloud project, billing or external account has been configured.
