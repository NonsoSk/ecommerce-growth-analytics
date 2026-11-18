# Source code

- `ecommerce_growth/synthetic.py`: unchanged deterministic generation, strict clean-baseline validation and standalone event-quality detection.
- `ecommerce_growth/analysis.py`: constrained SQLite loading, SQL execution, CSV exports, input fingerprints, source-total checks and idempotent output replacement.
- `ecommerce_growth/analysis_report.py`: renders computed simulation tables and carefully limited observations.
- `ecommerce_growth/bigquery_migration.py`: offline preparation, guarded CLI load/query stages and actual-result comparator; historical cloud execution passed 96/96 parity checks.

- `ecommerce_growth/dashboard.py`: baseline-only aggregate exports and SQL-derived filter expectations.

All use Python's standard library. Run `scripts/generate_sample.py` for generation or `scripts/run_analysis.py` for tests and the complete local analysis. No package installation or external service connection is required. Real retailer ingestion remains unimplemented; current cloud availability is not inferred from historical BigQuery execution.
