# BigQuery migration preparation

**Prepared locally; live execution and parity unverified.** Read [the migration guide](../docs/BIGQUERY_MIGRATION.md) before any cloud operation.

- `schemas/`: eight explicit raw schemas; no automatic field inference.
- `sql/models.sql`: typed GoogleSQL model CTEs, preserving the validated measurement rules.
- `sql/queries/`: separate analytical outputs, summary and raw controls.
- `config.example.json`: placeholder identifiers plus cost/retention limits. Copy to ignored `config.local.json` only when actual project/location are supplied.

Offline command: `.venv/bin/python scripts/bigquery_migrate.py prepare`.

This creates only ignored local artifacts. It does not authenticate, enable billing, create a dataset or execute BigQuery. Cloud load/dry-run/execute are separate explicit stages. No source data, credentials or tokens belong here.
