# Automated checks

Run `.venv/bin/python -m unittest discover -s tests -v`, or `.venv/bin/python scripts/run_analysis.py` to run tests and the complete analysis pipeline.

The suite contains **45 tests**: 14 original generator checks, 15 SQLite analysis checks, 15 offline BigQuery preparation/guard tests and one report-regeneration check. It covers byte determinism, configurable size, keys, relationships, chronology, arithmetic, cumulative refunds, campaign-day cost preservation and exact quality detection. SQL tests use an independent hand-calculated fixture with multiple items/orders/refunds, repeat purchases, invalid funnel ordering, spend-only and conversion-only days, late arrivals and zero denominators. Export reruns, input fingerprints and unchanged raw data are checked as well.

BigQuery tests exercise explicit schema mapping, read-only query structure, allowlisted ownership/location checks, cost-cap commands, idempotent mocked loads, dry-run/execute orchestration and a comparator that rejects cent/null/key/duplicate mismatches. These mocks **do not parse or execute GoogleSQL on Google Cloud**. The separate live cloud run passed 96/96 comparisons; see `docs/BIGQUERY_VALIDATION.md`. Receipt tests reject changed inputs/schema/remote versions and prevent unnecessary reloads; bounded concurrency tests preserve failure status. The report check regenerates default results and compares the reviewed report, excluding only the run-specific test-count line.

- `fixtures/event_quality.json`: three independent issue cases, four events. Exercised both by the Python detector and the SQLite audit, separately from baseline.
- `fixtures/sql_hand_calculated.json`: five-session hand-authored example, not random generator output. See `docs/SQL_PIPELINE.md` for its expected arithmetic.

These tests validate local synthetic contracts, not real source data, causal effects or production readiness. `scripts/verify_environment.py` remains the standalone environment check.
