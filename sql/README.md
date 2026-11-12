# Local SQL analysis

`analysis/00_schema.sql` defines the constrained SQLite snapshot; `01_models.sql` defines parameterized analytical views. Separate readable queries produce daily ledger metrics, strict ordered funnels, device/source segments, funnel exceptions, campaign-day and campaign-summary outcomes, activity not attributed to a paid campaign, transaction reconciliation, visit types and raw event quality dispositions.

Run `.venv/bin/python scripts/run_analysis.py` from the repository root. See `docs/SQL_PIPELINE.md` for inputs, grains, rerun behavior and planned BigQuery migration. No BigQuery implementation or connection exists.
