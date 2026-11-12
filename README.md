# E-commerce Growth Analytics

**Status: in development — initial local setup only.**

A portfolio project for a fictional direct-to-consumer mattress retailer. The goal is to analyze acquisition spend and customer journeys, identify conversion problems, reconcile purchases and revenue, and recommend prioritized experiments.

There are no datasets, findings, measured business results or completed integrations yet. Future sample data will be explicitly labeled synthetic; it will not represent a real retailer.

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

## Project layout

| Location | Purpose |
| --- | --- |
| `src/ecommerce_growth/` | Reusable Python analysis code |
| `sql/` | SQL transformations and reconciliation queries |
| `notebooks/` | Exploration with reviewed, sanitized outputs |
| `tests/` | Future checks for data quality and analysis logic |
| `scripts/` | Local setup verification |
| `docs/` | Definitions, integration plans and validation records |
| `reports/` | Reviewed analysis summaries; generated outputs ignored |
| `data/sample/` | Future approved synthetic examples |
| `data/private/` | Ignored local datasets; never commit |

## Planned tools

Python and SQL will handle analysis. BigQuery will be the planned warehouse; GA4 and Shopify will supply behavioral and order records; Google Ads and Meta Ads will supply acquisition data. Tableau will support dashboards, and Hotjar will support qualitative journey review. AI-assisted work must be independently validated. All external integrations remain planned and disconnected.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for milestones, [docs/VALIDATION.md](docs/VALIDATION.md) for evidence standards, and [PROGRESS.md](PROGRESS.md) for current status.

## Data and Git safety

Keep credentials in ignored local configuration or outside this repository. `.env.example` contains placeholders only and is not automatically loaded by Python. Real customer data, raw exports and sensitive notebook output must not be committed. Ignore rules are a guardrail, not a substitute for reviewing staged files.

Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`. Remote inspection requested authentication, so its contents and history remain unknown. Before a future push, fetch and inspect that history; preserve both local and remote work. No push is part of this setup.

## Interview explanation

“I started by creating a reproducible local workspace and separating code from private data. I will define how each source measures purchases and revenue before comparing them, validate the joins and totals, then use verified evidence to prioritize experiments. This project is still in development, so I am not claiming results yet.”
