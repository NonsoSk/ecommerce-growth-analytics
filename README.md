# E-commerce Growth Analytics

**Status: in development — reproducible local SQLite analysis of synthetic data implemented.**

A portfolio project for a fictional direct-to-consumer mattress retailer. The goal is to analyze acquisition spend and customer journeys, identify conversion problems, reconcile purchases and revenue, and recommend prioritized experiments.

An explicitly labeled synthetic dataset and local SQL analysis report are now available. There are no real datasets, real business findings, measured improvements or completed external analytics integrations. Synthetic patterns are not evidence about Puffy or real customers.

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

The current generator assumes perfect identity linking, fixed journey steps, same-session attribution and simplified prices/refunds. It does not model all real tracking gaps or order lifecycles. Real source connections, real-data findings, dashboards and experiments remain planned.

## Milestone 2: reproducible local SQL analysis

Run the complete local pipeline, including all tests:

```sh
.venv/bin/python scripts/run_analysis.py
```

The pipeline verifies existing baseline hashes (or generates the default baseline if absent), loads an explicit SQLite schema, runs separate SQL analyses, exports dashboard-ready CSVs and renders a report. Outputs stay ignored under `data/generated/analysis/`. Reruns replace validated outputs rather than append rows; raw baseline files remain unchanged. No additional dependency or external service is required.

Read the reviewed [synthetic analysis report](reports/MILESTONE_2_ANALYSIS.md), [measurement review](docs/MEASUREMENT_REVIEW.md) and [SQL pipeline guide](docs/SQL_PIPELINE.md). The default seed-42 run has 1,496 observed visitors, 331 purchasing visitors, 377 orders across 377 converting sessions, 13.96% order conversion and $330,922.95 net merchandise revenue. These are computed simulation outputs, not measured retailer performance. All 29 tests pass; spend and revenue reconcile with zero differences.

The SQL distinguishes ledger orders from tracked funnel purchases, first observed from lifetime-new purchasers, and original merchandise revenue from refund-adjusted revenue. Same-session attribution is descriptive, not causal. Landing-page analysis is unavailable because that field does not exist. Earlier cutoffs (`--cutoff YYYY-MM-DD`) flag incomplete refund observation and defer unavailable events. BigQuery remains a planned cloud migration; no cloud warehouse or dashboard has been implemented.

## Project layout

| Location | Purpose |
| --- | --- |
| `src/ecommerce_growth/` | Reusable Python analysis code |
| `sql/` | Explicit SQLite schema, analytical views and separate report queries |
| `notebooks/` | Exploration with reviewed, sanitized outputs |
| `tests/` | Generator checks, SQL regression tests and independent hand-calculated fixtures |
| `scripts/` | Local verification, generation and complete SQL pipeline commands |
| `docs/` | Definitions, integration plans and validation records |
| `reports/` | Reviewed synthetic SQL report; other generated outputs ignored |
| `data/sample/` | Small reviewed synthetic illustration |
| `data/generated/` | Ignored generated baseline and manifest |
| `data/private/` | Ignored local datasets; never commit |

## Planned tools

Python and SQLite now handle local synthetic analysis. BigQuery is the planned cloud warehouse; GA4 and Shopify are planned behavioral and order sources; Google Ads and Meta Ads are planned acquisition sources. Tableau is planned for dashboards and Hotjar for qualitative journey review. AI-assisted work must be independently validated. All external analytics integrations remain planned and disconnected.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for milestones, [docs/VALIDATION.md](docs/VALIDATION.md) for evidence standards, and [PROGRESS.md](PROGRESS.md) for current status.

## Data and Git safety

Keep credentials in ignored local configuration or outside this repository. `.env.example` contains placeholders only and is not automatically loaded by Python. Real customer data, raw exports and sensitive notebook output must not be committed. Ignore rules are a guardrail, not a substitute for reviewing staged files.

Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`. GitHub access was verified as `NonsoSk` on 2026-11-12, and the repository was confirmed private. Inspection and fetch found no existing remote branches or commits, so no merge was needed. The reviewed initial project, including this README, was uploaded on `main`, which tracks `origin/main`; the initial local and remote commit hashes matched. Continue reviewing staged files and fetching remote history before future pushes. Preserve existing work and never force-push.

## Interview explanation

“I defined the metrics before writing SQL, then used fictional data to test the analysis. I separated visitor identities, buying sessions and orders, and aggregated items and refunds before joining so revenue could not multiply. I verified the results with small examples I could calculate by hand. The report shows synthetic patterns worth investigating, not real business improvements.”
