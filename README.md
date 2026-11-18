# E-commerce Growth Analytics

**Private release candidate — synthetic demonstration, final Tableau acceptance pending.** Open `release/SYNTHETIC_Growth_REVIEW.twbx`. Read [the case study](docs/PORTFOLIO_CASE_STUDY.md), [evidence index](release/EVIDENCE_INDEX.md), and [remaining acceptance checks](dashboard/INTERACTION_CHECKS.md).

**Status: in development — SQLite analysis and live BigQuery synthetic-data parity verified (96/96 comparisons).**

A portfolio project for a fictional direct-to-consumer mattress retailer. The goal is to analyze acquisition spend and customer journeys, identify conversion problems, reconcile purchases and revenue, and recommend prioritized experiments.

An explicitly labeled synthetic dataset and local SQL analysis report are now available. There are no real datasets, real business findings or measured improvements. BigQuery was used and verified for this synthetic demonstration on November 13, 2026; current cloud availability is not asserted; real source integrations remain planned. Synthetic patterns are not evidence about Puffy or real customers.

## Run locally

The initial setup uses Python 3.14.8 and the standard library only. No external packages are required. Apple's Python 3.9.6 is left unchanged.

```sh
# Recreate the environment if needed; do not commit .venv
python3.14 -m venv .venv
source .venv/bin/activate
python scripts/verify_environment.py
python -m pip check
```

Activation makes `python` use this project's isolated environment. You can also run `.venv/bin/python scripts/verify_environment.py` directly. `deactivate` exits it.

## Milestone 1: measurement and synthetic data

Generate the default 90-day baseline from the repository root:

```sh
.venv/bin/python scripts/generate_sample.py
```

Run the automated tests:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Optional generator arguments: `--seed 7 --sessions 900 --start 2026-02-01`. The default is seed 42, 2,700 sessions, starting 2026-01-01. Output goes to ignored `data/generated/baseline/`, with eight linked JSON tables and a manifest containing row counts, file hashes and monetary control totals. Repeating the same configuration on the verified Python environment produces identical bytes. No new dependencies are required.

The default has 1,496 visitor identities, 2,700 sessions, 7,170 events, 377 orders, 377 order items, 79 partial refunds, four campaigns and 360 campaign-day spend rows. These are simulation counts, not business results. Separate quality fixtures cover duplicate purchases, missing transaction IDs and late events. Only a small linked illustration is committed; bulk output stays local.

Read the [measurement plan](docs/MEASUREMENT_PLAN.md), [data dictionary](docs/DATA_DICTIONARY.md), [simulation assumptions](docs/SIMULATION_ASSUMPTIONS.md) and [fixture handling rules](docs/QUALITY_FIXTURES.md). The rules distinguish sessions, orders and customers, original payments and refunds, and attributed performance from causal impact. Advertising spend is never repeated on individual event rows.

The current generator assumes perfect identity linking, fixed journey steps, same-session attribution and simplified prices/refunds. It does not model all real tracking gaps or order lifecycles. Real source ingestion, real-data findings and executed experiments remain absent. Local dashboards are built with final acceptance pending.

## Milestone 2: reproducible local SQL analysis

Run the complete local pipeline, including all tests:

```sh
.venv/bin/python scripts/run_analysis.py
```

The pipeline verifies existing baseline hashes (or generates the default baseline if absent), loads an explicit SQLite schema, runs separate SQL analyses, exports dashboard-ready CSVs and renders a report. Outputs stay ignored under `data/generated/analysis/`. Reruns replace validated outputs rather than append rows; raw baseline files remain unchanged. No additional dependency or external service is required.

Read the reviewed [synthetic analysis report](reports/MILESTONE_2_ANALYSIS.md), [measurement review](docs/MEASUREMENT_REVIEW.md) and [SQL pipeline guide](docs/SQL_PIPELINE.md). The default seed-42 run has 1,496 observed visitors, 331 purchasing visitors, 377 orders across 377 converting sessions, 13.96% order conversion and $330,922.95 net merchandise revenue. These are computed simulation outputs, not measured retailer performance. The latest recorded local suite has 51 passing tests; spend and revenue reconcile with zero differences. Migration workflow mocks are local tests, not proof of BigQuery execution.

The SQL distinguishes ledger orders from tracked funnel purchases, first observed from lifetime-new purchasers, and original merchandise revenue from refund-adjusted revenue. Conversion counts distinct buying sessions even when a session has multiple orders. Same-session attribution is descriptive, not causal: direct has no paid campaign assignment and can include missing attribution or prior paid exposure; organic does not imply zero acquisition cost. Landing-page analysis is unavailable because that field does not exist. Earlier cutoffs (`--cutoff YYYY-MM-DD`) flag incomplete refund observation and defer unavailable events. The synthetic analysis has also been verified in BigQuery; the local dashboard candidate is built with acceptance pending.

## Milestone 3: verified BigQuery demonstration

Prepare the upload files, GoogleSQL and SQLite parity expectations locally:

```sh
.venv/bin/python scripts/bigquery_migrate.py prepare
```

This makes **zero cloud requests**. Eight explicit schemas, typed GoogleSQL models and 12 output/control queries are prepared for eight parity scenarios. Generated files remain ignored. The driver restricts uploads to 40 explicitly named, ownership-labelled demonstration tables, skips unchanged verified uploads, supports server dry runs and applies a configurable maximum-bytes-billed limit to every query job.

**Verified live:** the synthetic baseline and isolated fixtures were loaded into `premium-silicon-514522-e8.ecommerce_growth_demo` in `US`; all **96 BigQuery-versus-SQLite comparisons passed**, with zero monetary/count reconciliation differences and no duplicate baseline keys. Billing was disabled with no account linked at the November 13 verification; current account/cloud state is not inferred from that historical check. The first attempt stopped after 81 passes on a non-reproduced CLI error; the complete rerun passed at two workers without reloading data or changing expectations.

With the authenticated CLI on PATH and the existing ignored `bigquery/config.local.json`, reproduce the analysis:

```sh
.venv/bin/python scripts/bigquery_migrate.py execute --config bigquery/config.local.json --acknowledge-cloud-actions --workers 2
```

See the [validation evidence](docs/BIGQUERY_VALIDATION.md) for row counts, hashes, quality cases and actual cloud results, and the [migration guide](docs/BIGQUERY_MIGRATION.md) for loading, permissions and sandbox limits. Demo tables expire after seven days (observed expiration: 2026-11-19 UTC); keep local sources and evidence. No real GA4, Shopify, advertising or Hotjar sources are connected. The [follow-up backlog](docs/FOLLOW_UP_BACKLOG.md) keeps attribution/device investigations and independent real-data evidence separate from simulation validation. Tableau local dashboards are built; final acceptance remains pending.

## Project layout

| Location | Purpose |
| --- | --- |
| `src/ecommerce_growth/` | Reusable Python analysis code |
| `sql/` | Explicit SQLite schema, analytical views and separate report queries |
| `bigquery/` | Explicit schemas, GoogleSQL and placeholder migration configuration; live synthetic parity verified |
| `notebooks/` | Exploration with reviewed, sanitized outputs |
| `tests/` | Generator checks, SQL regression tests and independent hand-calculated fixtures |
| `scripts/` | Local verification, generation and complete SQL pipeline commands |
| `docs/` | Definitions, integration plans and validation records |
| `reports/` | Reviewed synthetic SQL report; other generated outputs ignored |
| `data/sample/` | Small reviewed synthetic illustration |
| `data/generated/` | Ignored generated baseline and manifest |
| `data/private/` | Ignored local datasets; never commit |

## Planned tools

Python and SQLite now handle local synthetic analysis. BigQuery historically ran the validated synthetic demonstration; GA4 and Shopify are planned behavioral and order sources; Google Ads and Meta Ads are planned acquisition sources. Tableau Public runs the local synthetic dashboards; Hotjar remains a proposed qualitative source. AI-assisted work must be independently validated. Real source integrations remain planned and disconnected; BigQuery access is limited to the authorized synthetic demonstration.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for milestones, [docs/VALIDATION.md](docs/VALIDATION.md) for evidence standards, and [PROGRESS.md](PROGRESS.md) for current status.

## Data and Git safety

Keep credentials in ignored local configuration or outside this repository. `.env.example` contains placeholders only and is not automatically loaded by Python. Real customer data, raw exports and sensitive notebook output must not be committed. Ignore rules are a guardrail, not a substitute for reviewing staged files.

Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`. GitHub access was verified as `NonsoSk` on 2026-11-12, and the repository was confirmed private. Inspection and fetch found no existing remote branches or commits, so no merge was needed. The reviewed initial project, including this README, was uploaded on `main`, which tracks `origin/main`; the initial local and remote commit hashes matched. Continue reviewing staged files and fetching remote history before future pushes. Preserve existing work and never force-push.

## Interview explanation

“I defined the metrics before writing SQL, then used fictional data to test the analysis. I separated visitor identities, buying sessions and orders, and aggregated items and refunds before joining so revenue could not multiply. I verified the results with small examples I could calculate by hand. The report shows synthetic patterns worth investigating, not real business improvements.”

## Dashboard milestone — local build awaiting visual acceptance

Three synthetic Tableau dashboards (Overview, Funnel, Acquisition) and 29 worksheets are generated in a separate local workbook. Tableau Public successfully loaded the extract-backed copy; the earlier revenue probe was visually confirmed at $330,922.95. The original draft is preserved. All 51 local tests, eight SQL/Hyper aggregate checks and 50 workbook-expression checks pass. Baseline, representative combinations, empty cases and resets have screenshot evidence. Reverse-isolation sequence confirmation, two tooltip values and relocated close/reopen evidence remain pending. This is not a completed-dashboard claim. Nothing has been published.

See [dashboard reproduction and validation](dashboard/README.md). Optional Hyper tooling is isolated from the existing project environment. Baseline-only CSVs and local extracts preserve the dashboard data after cloud expiration. Real customer integrations, real business findings and experiment results remain unimplemented.

## Reproducible private release

The core analysis uses only Python standard-library modules. Optional Tableau Hyper tooling has pinned dependencies in `dashboard/requirements-hyper.txt`, isolated from `.venv`. See [the dashboard guide](dashboard/README.md) for a clean-checkout build. The release package uses embedded baseline-only data and needs no BigQuery account. Cloud execution was verified historically; table expiration does not invalidate local outputs or establish current cloud availability.

The [experiment protocol](docs/EXPERIMENT_PROTOCOL.md) is explicitly **unexecuted**. Source integration settings are placeholders, not ingestion connectors. No causal lift or real commercial result is claimed. Release work is committed locally only; dashboard artifacts are not claimed uploaded until a separately authorized private push is verified.
