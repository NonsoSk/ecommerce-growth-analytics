# Milestone 3 — BigQuery migration

**In development. Live synthetic-data migration and 96/96 BigQuery-versus-SQLite comparisons verified. Billing remains disabled with no linked account. Only the authorized demo dataset/tables were created. Real source integrations, dashboards and commercial findings remain out of scope.**

See [BIGQUERY_VALIDATION.md](BIGQUERY_VALIDATION.md) for actual results, the interrupted first attempt and successful full rerun, input/result fingerprints and retention dates.

## What is prepared

- Eight explicit JSON schemas in `bigquery/schemas/`, matching the existing raw fields. Money uses INTEGER/INT64 cents; event/refund occurrence and ingestion use TIMESTAMP; campaign-day spend dates use DATE. No landing-page fields were invented.
- `bigquery/sql/models.sql` contains GoogleSQL CTE models; `bigquery/sql/queries/` has the ten existing report analyses plus summary and raw-control queries. Models are composed into a single read-only query per output, with typed start/end/cutoff parameters and validated fully qualified table names.
- `scripts/bigquery_migrate.py` and `src/ecommerce_growth/bigquery_migration.py` prepare NDJSON, render SQL, compute SQLite expectations, and provide explicit load/dry-run/execute stages through the `bq` CLI. Python dependencies remain standard-library only.
- Full-result parity compares every row, column, key and null in 12 queries across eight scenarios: baseline; hand-calculated full, early and reprocessed cutoffs; duplicate purchase; missing transaction ID; late arrival before and after ingestion. Eight scenarios use five separate raw-table groups, **40 explicitly named demonstration tables**. They never mix bad-event fixtures into baseline.

The prepared default and fixture scenarios now pass on Google's live SQL engine. Mocks still test orchestration only; production-scale behavior and empty-file loads have not been established by this run.

## Corrections retained from review

Direct has no paid campaign assignment under the current same-session model; it may contain missing attribution or prior paid exposure. Organic does not imply zero acquisition cost. The report heading is now **Days with spend and zero attributed orders**. Purchase conversion counts distinct converting sessions, with orders separate. The hand fixture proves two orders in one session yield one converting session and 100%, not 200%, daily session conversion. A report-regeneration test prevents divergence between the committed report and its generator.

The [follow-up backlog](FOLLOW_UP_BACKLOG.md) covers attribution sensitivity, comparable device/source/visit cohorts, landing-page measurement and independent real-data analysis. Neither migration parity nor synthetic tests establish business evidence.

## Local preparation — no Google Cloud requests

From the repository root, after the existing baseline is available:

```sh
.venv/bin/python scripts/run_analysis.py
.venv/bin/python scripts/bigquery_migrate.py prepare
```

Preparation uses the placeholder configuration by default and writes only ignored `data/generated/bigquery/`: upload NDJSON, explicit schemas, rendered SQL, per-scenario SQLite expectations, fingerprints and `plan.json`. It validates input hashes and raw fields without modifying baseline JSON. Repeating preparation replaces the same generated files and does not append records.

`verification_status.json` is reset to **not_verified_in_bigquery** on every preparation. Old actual-result files are not evidence for a new plan; inspect the status and matching plan SHA-256. No credential files or tokens are read or printed by this code.

## Configuration and permissions

1. Install Google Cloud CLI, including `bq`, on this machine, and sign in locally as the intended Google account using `gcloud auth login`. Do not paste tokens, passwords or service-account JSON into chat or the repository. The workflow uses CLI authentication; a Python client/ADC setup is not required for this implementation.
2. Supply the exact existing **Google Cloud project ID**, not its display name or project number. GitHub account `NonsoSk` does not identify a Google Cloud principal or project.
3. Have an administrator prepare/approve a dedicated dataset, proposed ID **`ecommerce_growth_demo`**, in an explicitly chosen location. Supply the exact location string, such as `US`, `EU` or a supported region, based on residency and future source requirements. For this authorized run, the user selected project `premium-silicon-514522-e8`, dataset `ecommerce_growth_demo` and location `US`; location was not inferred from timezone.
4. Apply the dataset ownership label **`portfolio_project=ecommerce_growth_analytics`**. Existing tables with the planned demonstration names must also have that label and be ordinary base tables. Do not relabel unrelated tables to bypass protection.
5. Grant the execution principal **BigQuery Job User (`roles/bigquery.jobUser`) on the job project** and **BigQuery Data Editor (`roles/bigquery.dataEditor`) on only the dedicated dataset**. These cover the workflow's job submission and demonstration-table creation/loading/read/metadata operations; organization policies may impose additional restrictions. Dataset creation/label setup should be performed by its administrator, not by broadening this script's authority. [Official IAM roles](https://docs.cloud.google.com/bigquery/docs/access-control).
6. Confirm BigQuery API availability, the project's existing billing or sandbox constraints, and an approved query-byte ceiling before any live load or execution. The driver never enables APIs, links billing or buys capacity. The demo dataset was created separately under explicit user authorization; its batch loads and queries succeeded with billing disabled.

Copy `bigquery/config.example.json` to ignored `bigquery/config.local.json` and fill in the project/location. The default bytes ceiling is **1,000,000,000 bytes per query job**, configurable as a positive integer. New demonstration tables are set to expire after **604,800 seconds (seven days)**. Existing table expiration is not extended automatically. Config is identifiers and limits only, never credentials.

## Reproducing the cloud workflow

After those prerequisites and explicit authorization to incur any applicable storage/query usage:

```sh
# Loads only exact project-owned demonstration tables; skips verified unchanged uploads.
.venv/bin/python scripts/bigquery_migrate.py load --config bigquery/config.local.json --acknowledge-cloud-actions

# Contacts BigQuery to validate/estimate queries; does not load or execute data queries.
.venv/bin/python scripts/bigquery_migrate.py dry-run --config bigquery/config.local.json

# Server dry-run before every actual query, then compare real results to SQLite.
.venv/bin/python scripts/bigquery_migrate.py execute --config bigquery/config.local.json --acknowledge-cloud-actions --workers 2
```

The driver verifies dataset location and ownership before mutations. The complete destination allowlist is the Cartesian product of the five groups (`baseline`, `hand`, `duplicate_purchase`, `missing_transaction_id`, `late_arrival`) and eight schema table names, using **`eg_demo_<group>_<table>`**. It inventories existing tables, rejects incomplete inventories, and refuses to replace an unlabelled table or view. Unrelated dataset objects are untouched. The driver contains no dataset-creation, billing, IAM-update, recursive deletion or broad cleanup commands.

New allowed tables are created with explicit schemas, ownership labels and expiration. Loads use explicit schema, reject bad/unknown fields and never append. Loaded row counts are checked. Ignored local load receipts bind the destination, source SHA-256, schema SHA-256 and BigQuery table etag. Reruns skip uploads only when all of these and the row count still match. Nonempty tables without a matching receipt are refused rather than automatically replaced; investigate changed inputs, missing receipts or remote modifications before a separate reviewed replacement. Empty owned tables can be resumed. Receipts are a rerun optimization, not a substitute for SQL parity. Partial progress is recorded after each completed table/comparison. This is not an atomic 40-table transaction: use a dedicated dataset with no concurrent writers. Empty-file load behavior remains unverified; the successful default and hand fixtures have nonempty tables.

Query SQL itself is read-only; result storage uses BigQuery's temporary query results, and returned JSON is written to the ignored local output folder. Identifiers are allowlisted/validated separately because value parameters cannot stand in for table identifiers. `--bigqueryrc` is disabled so unrelated personal CLI defaults cannot silently select destinations. [Parameterized-query documentation](https://docs.cloud.google.com/bigquery/docs/parameterized-queries).

## Cost controls and their limits

Every dry-run and execution query command sets GoogleSQL, an explicit project/location, typed dates, cache disabled and `maximum_bytes_billed`. A recognized numeric dry-run estimate above the cap aborts before execution; an unavailable CLI estimate is stored as null, and the actual job still has the bytes limit. Result-row limits prevent truncated output from passing parity; they are **not** a scan-cost control. [Official CLI reference](https://docs.cloud.google.com/bigquery/docs/reference/bq-cli-reference).

A successful Google dry run validates and estimates; it does not establish result correctness. The full parity stage submits **96 actual query jobs**, each preceded by a dry run. `--workers 2` uses two concurrent read-only comparisons (accepted range 1–4); default is one, and uploads remain sequential. A failed comparison cancels pending work; already-running jobs can finish, but the run is not marked verified. The ceiling is per job, not a daily/project budget or a total-run cap. Multiple runs can accumulate charges. [Query dry runs](https://docs.cloud.google.com/bigquery/docs/running-queries).

Query-byte limits do **not** cap table storage, retained/time-travel storage, capacity/reservation commitments, transfer/network charges, load/storage-related costs, other jobs/users or taxes. The script uses local batch loads rather than streaming and provisions no reservations. Table expiration is a retention precaution, not a promise of zero storage charges; retained physical storage can outlive a visible table. Billing alerts and project budgets are separate administrative controls and were not activated. [Cost controls](https://docs.cloud.google.com/bigquery/docs/best-practices-costs), [batch loading](https://docs.cloud.google.com/bigquery/docs/batch-loading-data).

## Parity and data integrity acceptance

- No tolerance for integer monetary/count differences, including integers beyond floating-point exact range. Ratios allow only `rel_tol=1e-10` / `abs_tol=1e-8` for floating-point formatting.
- Exact null behavior, result key uniqueness, column sets and row sets. Request one more output row than expected to expose extra rows rather than silently truncating them.
- Date/timestamp formatting is normalized to UTC for comparison. Cohort dates and occurrence/ingestion cutoffs remain distinct.
- Compare complete daily finances, ordered funnels, device/source segments, exceptions, campaign-day and campaign totals, activity without paid campaign assignment, reconciliation, visit types, quality dispositions, summary and raw counts/keys/monetary controls.
- Raw input validation retains SQLite's enforced checks before upload. BigQuery does **not** enforce primary/foreign keys; raw controls and output parity supplement—not replace—production-quality constraints. No informational key constraints are asserted to the optimizer without proof. [BigQuery key constraints](https://docs.cloud.google.com/bigquery/docs/primary-foreign-keys).
- GoogleSQL uses typed timestamps/dates, SAFE_DIVIDE, COUNTIF, explicit UNION DISTINCT for campaign-day key union, and grouped sequential funnel joins instead of complex correlated event subqueries. Each session qualifies at most once per step; skipped steps remain visible. [GoogleSQL query syntax](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax), [timestamp functions](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions), [SAFE_DIVIDE](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/mathematical_functions).

## Documentation and tooling check

Official Google Cloud sources above were checked on **2026-11-12** before BigQuery-specific implementation. Explicit schema formats were checked against [Specify a schema](https://docs.cloud.google.com/bigquery/docs/schemas), and authentication against [Authenticate to BigQuery](https://docs.cloud.google.com/bigquery/docs/authentication).

Initial preparation found no CLI/authentication. Subsequent authorized setup installed Google's official ARM64 archive outside the repository (`~/google-cloud-sdk`), verified its checksum, and authenticated the intended account. CLI versions: gcloud 593.0.0 and bq 2.1.42. Project Python 3.14.8 remains unchanged. BigQuery API and project access were verified; billing was disabled before and after execution. Credential contents and tokens were never printed or committed. No Tableau dashboard is being built.

The configurable new-table expiration must be at least one hour; the default remains seven days. The driver also refuses replacement of existing customer-managed-key tables because load replacement can remove their key unless encryption is explicitly handled. That requires a separate reviewed migration plan. [Table creation options](https://docs.cloud.google.com/bigquery/docs/tables), [load replacement semantics](https://docs.cloud.google.com/bigquery/docs/reference/bq-cli-reference).

## Sandbox restrictions and retention

Google's current [sandbox documentation](https://docs.cloud.google.com/bigquery/docs/sandbox) specifies a **10 GiB lifetime storage allowance that deletion does not restore**, 1 TiB monthly query processing, automatic expiration within 60 days, and no streaming, DML or Data Transfer Service. This workflow uses local batch loads and SELECT queries. Its seven-day table expiration is shorter than the sandbox maximum. Neither expiration nor replacing tables restores the lifetime allowance; avoid unnecessary reloads. Payload size is a preflight estimate, not Google's storage accounting or a measurement of remaining historical quota. The per-query cap is not an aggregate run budget.

Keep local source files and reviewed validation evidence: cloud demo tables are temporary and do not constitute durable production storage. Once expired, queries cannot be reproduced until an authorized reload; do not silently extend retention or enable billing. Remaining sandbox quota and empty-table edge cases are not proven merely by a successful default-data run.

## Dataset setup used for this authorized run

These identifiers are not credentials. Keep the filled config ignored:

```json
{
  "project_id": "premium-silicon-514522-e8",
  "dataset_id": "ecommerce_growth_demo",
  "location": "US",
  "maximum_bytes_billed": 1000000000,
  "table_expiration_seconds": 604800
}
```

The dataset was absent at preflight. It was created once with the command below, then its location, label and expiration were verified. Do not replay creation against an existing dataset or relabel unrelated resources; inspect them first. The driver itself does not create datasets.

```sh
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
bq --bigqueryrc=/dev/null --quiet --project_id=premium-silicon-514522-e8 --location=US mk --dataset --label=portfolio_project:ecommerce_growth_analytics --default_table_expiration=604800 premium-silicon-514522-e8:ecommerce_growth_demo
```

The only uploaded data was synthetic: baseline tables use `eg_demo_baseline_*`; independent hand and intentional quality fixtures use the other explicit group prefixes. Before future loads, recheck billing/sandbox status, remaining quota and input size. This run's 2,312,867-byte NDJSON upload resulted in 735,612 logical bytes in BigQuery; these measures are not interchangeable.

One execution attempt stopped after 81 completed comparisons on a CLI error for `late_arrival/quality`. Available job metadata showed no server errors; the isolated query passed, and the entire suite then passed with two workers. The precise cause of the first CLI failure is unresolved. No SQL, data or expected answers were altered. The ignored `execute_attempt_1.json` preserves partial status; the final `execute_status.json` and `verification_status.json` record all 96 passes. Query reruns consume compute allowance even when no data is reloaded.
