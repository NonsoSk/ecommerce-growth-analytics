# Milestone 3 — BigQuery migration preparation

**In development. Prepared and tested locally only. No successful BigQuery server validation, upload, execution or live result parity has been observed. No billing, dataset, table or other cloud resource was created during this milestone.**

## What is prepared

- Eight explicit JSON schemas in `bigquery/schemas/`, matching the existing raw fields. Money uses INTEGER/INT64 cents; event/refund occurrence and ingestion use TIMESTAMP; campaign-day spend dates use DATE. No landing-page fields were invented.
- `bigquery/sql/models.sql` contains GoogleSQL CTE models; `bigquery/sql/queries/` has the ten existing report analyses plus summary and raw-control queries. Models are composed into a single read-only query per output, with typed start/end/cutoff parameters and validated fully qualified table names.
- `scripts/bigquery_migrate.py` and `src/ecommerce_growth/bigquery_migration.py` prepare NDJSON, render SQL, compute SQLite expectations, and provide explicit future load/dry-run/execute stages through the `bq` CLI. Python dependencies remain standard-library only.
- Full-result parity compares every row, column, key and null in 12 queries across eight scenarios: baseline; hand-calculated full, early and reprocessed cutoffs; duplicate purchase; missing transaction ID; late arrival before and after ingestion. Eight scenarios use five separate raw-table groups, **40 explicitly named demonstration tables**. They never mix bad-event fixtures into baseline.

Cloud syntax and behavior remain unverified even though local structural checks and mocked CLI workflow tests pass. Mocks test orchestration, not Google's SQL engine.

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

## What must be supplied before a cloud run

1. Install Google Cloud CLI, including `bq`, on this machine, and sign in locally as the intended Google account using `gcloud auth login`. Do not paste tokens, passwords or service-account JSON into chat or the repository. The workflow uses CLI authentication; a Python client/ADC setup is not required for this implementation.
2. Supply the exact existing **Google Cloud project ID**, not its display name or project number. GitHub account `NonsoSk` does not identify a Google Cloud principal or project.
3. Have an administrator prepare/approve a dedicated dataset, proposed ID **`ecommerce_growth_demo`**, in an explicitly chosen location. Supply the exact location string, such as `US`, `EU` or a supported region, based on residency and future source requirements. No location has been selected or inferred from the user's timezone.
4. Apply the dataset ownership label **`portfolio_project=ecommerce_growth_analytics`**. Existing tables with the planned demonstration names must also have that label and be ordinary base tables. Do not relabel unrelated tables to bypass protection.
5. Grant the execution principal **BigQuery Job User (`roles/bigquery.jobUser`) on the job project** and **BigQuery Data Editor (`roles/bigquery.dataEditor`) on only the dedicated dataset**. These cover the workflow's job submission and demonstration-table creation/loading/read/metadata operations; organization policies may impose additional restrictions. Dataset creation/label setup should be performed by its administrator, not by broadening this script's authority. [Official IAM roles](https://docs.cloud.google.com/bigquery/docs/access-control).
6. Confirm BigQuery API availability, the project's existing billing or sandbox constraints, and an approved query-byte ceiling before any live load or execution. This milestone does not enable the API, link billing, buy capacity or create the dataset. A sandbox/restricted project may support only part of the workflow; cloud execution must establish this rather than assuming it.

Copy `bigquery/config.example.json` to ignored `bigquery/config.local.json` and fill in the project/location. The default bytes ceiling is **1,000,000,000 bytes per query job**, configurable as a positive integer. New demonstration tables are set to expire after **604,800 seconds (seven days)**. Existing table expiration is not extended automatically. Config is identifiers and limits only, never credentials.

## Future cloud workflow — prepared, not run

After those prerequisites and explicit authorization to incur any applicable storage/query usage:

```sh
# Creates/replaces only the exact named, project-owned demonstration tables.
.venv/bin/python scripts/bigquery_migrate.py load --config bigquery/config.local.json --acknowledge-cloud-actions

# Contacts BigQuery to validate/estimate queries; does not load or execute data queries.
.venv/bin/python scripts/bigquery_migrate.py dry-run --config bigquery/config.local.json

# Server dry-run before every actual query, then compare real results to SQLite.
.venv/bin/python scripts/bigquery_migrate.py execute --config bigquery/config.local.json --acknowledge-cloud-actions
```

The driver verifies dataset location and ownership before mutations. The complete destination allowlist is the Cartesian product of the five groups (`baseline`, `hand`, `duplicate_purchase`, `missing_transaction_id`, `late_arrival`) and eight schema table names, using **`eg_demo_<group>_<table>`**. It inventories existing tables, rejects incomplete inventories, and refuses to replace an unlabelled table or view. Unrelated dataset objects are untouched. There are no dataset-creation, billing, IAM-update, recursive deletion or broad cleanup commands.

New allowed tables are created with explicit schemas, ownership labels and expiration. Loads use explicit schema, reject bad/unknown fields and replace rather than append. Loaded row counts are checked. Reruns replace the same exact tables; no suffix-based duplicate copies are created. Partial failures are visible; rerun the load stage before executing parity. This is not an atomic 40-table transaction: use a dedicated dataset with no concurrent writers. Live empty-file load behavior and other service-specific constraints remain part of the unverified cloud acceptance gate; the prepared default and hand fixtures have nonempty tables.

Query SQL itself is read-only; result storage uses BigQuery's temporary query results, and returned JSON is written to the ignored local output folder. Identifiers are allowlisted/validated separately because value parameters cannot stand in for table identifiers. `--bigqueryrc` is disabled so unrelated personal CLI defaults cannot silently select destinations. [Parameterized-query documentation](https://docs.cloud.google.com/bigquery/docs/parameterized-queries).

## Cost controls and their limits

Every dry-run and execution query command sets GoogleSQL, an explicit project/location, typed dates, cache disabled and `maximum_bytes_billed`. A recognized numeric dry-run estimate above the cap aborts before execution; an unavailable CLI estimate is stored as null, and the actual job still has the bytes limit. Result-row limits prevent truncated output from passing parity; they are **not** a scan-cost control. [Official CLI reference](https://docs.cloud.google.com/bigquery/docs/reference/bq-cli-reference).

A successful Google dry run validates and estimates; it does not establish result correctness. The full parity stage submits **96 actual query jobs**, each preceded by a dry run. The ceiling is per job, not a daily/project budget or a total-run cap. Multiple runs can accumulate charges. [Query dry runs](https://docs.cloud.google.com/bigquery/docs/running-queries).

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

Observed locally: `gcloud` and `bq` were absent from PATH and checked installation paths; Google Python modules were not installed; `GOOGLE_APPLICATION_CREDENTIALS` was unset; the default ADC file was absent. Credential contents were not opened. This does not establish whether the user has an account or project elsewhere. **Live authentication, project access, dataset location, server SQL validation, loads and BigQuery/SQLite result parity are all unverified.** No Tableau dashboard is being built.

The configurable new-table expiration must be at least one hour; the default remains seven days. The driver also refuses replacement of existing customer-managed-key tables because load replacement can remove their key unless encryption is explicitly handled. That requires a separate reviewed migration plan. [Table creation options](https://docs.cloud.google.com/bigquery/docs/tables), [load replacement semantics](https://docs.cloud.google.com/bigquery/docs/reference/bq-cli-reference).
