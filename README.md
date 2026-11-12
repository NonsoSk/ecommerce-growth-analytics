# E-commerce Growth Analytics

**Status: in development — measurement definitions and reproducible synthetic data implemented.**

A portfolio project for a fictional direct-to-consumer mattress retailer. The goal is to analyze acquisition spend and customer journeys, identify conversion problems, reconcile purchases and revenue, and recommend prioritized experiments.

An explicitly labeled synthetic dataset is now available locally through the generator. There are no real datasets, business findings, measured improvements or completed analytics integrations. Synthetic patterns are not evidence about Puffy or real customers.

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

The current generator assumes perfect identity linking, fixed journey steps, same-session attribution and simplified prices/refunds. It does not model all real tracking gaps or order lifecycles. Real source connections, analytical findings, dashboards and experiments remain planned.

## Project layout

| Location | Purpose |
| --- | --- |
| `src/ecommerce_growth/` | Reusable Python analysis code |
| `sql/` | SQL transformations and reconciliation queries |
| `notebooks/` | Exploration with reviewed, sanitized outputs |
| `tests/` | Automated synthetic-data checks and separate quality fixtures |
| `scripts/` | Local verification and synthetic generation commands |
| `docs/` | Definitions, integration plans and validation records |
| `reports/` | Reviewed analysis summaries; generated outputs ignored |
| `data/sample/` | Small reviewed synthetic illustration |
| `data/generated/` | Ignored generated baseline and manifest |
| `data/private/` | Ignored local datasets; never commit |

## Planned tools

Python and SQL will handle analysis. BigQuery will be the planned warehouse; GA4 and Shopify will supply behavioral and order records; Google Ads and Meta Ads will supply acquisition data. Tableau will support dashboards, and Hotjar will support qualitative journey review. AI-assisted work must be independently validated. All external integrations remain planned and disconnected.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for milestones, [docs/VALIDATION.md](docs/VALIDATION.md) for evidence standards, and [PROGRESS.md](PROGRESS.md) for current status.

## Data and Git safety

Keep credentials in ignored local configuration or outside this repository. `.env.example` contains placeholders only and is not automatically loaded by Python. Real customer data, raw exports and sensitive notebook output must not be committed. Ignore rules are a guardrail, not a substitute for reviewing staged files.

Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`. GitHub access was verified as `NonsoSk` on 2026-11-12, and the repository was confirmed private. Inspection and fetch found no existing remote branches or commits, so no merge was needed. The reviewed initial project, including this README, was uploaded on `main`, which tracks `origin/main`; the initial local and remote commit hashes matched. Continue reviewing staged files and fetching remote history before future pushes. Preserve existing work and never force-push.

## Interview explanation

“I started by creating a reproducible local workspace and separating code from private data. I will define how each source measures purchases and revenue before comparing them, validate the joins and totals, then use verified evidence to prioritize experiments. This project is still in development, so I am not claiming results yet.”
