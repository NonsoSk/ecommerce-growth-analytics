# Automated checks

Run `.venv/bin/python -m unittest discover -s tests -v`, or `.venv/bin/python scripts/run_analysis.py` to run tests and the complete analysis pipeline.

The suite contains **29 tests**: 14 original generator checks and 15 SQLite analysis checks. It covers byte determinism, configurable size, keys, relationships, chronology, arithmetic, cumulative refunds, campaign-day cost preservation and exact quality detection. SQL tests use an independent hand-calculated fixture with multiple items/orders/refunds, repeat purchases, invalid funnel ordering, spend-only and conversion-only days, late arrivals and zero denominators. Export reruns, input fingerprints and unchanged raw data are checked as well.

- `fixtures/event_quality.json`: three independent issue cases, four events. Exercised both by the Python detector and the SQLite audit, separately from baseline.
- `fixtures/sql_hand_calculated.json`: five-session hand-authored example, not random generator output. See `docs/SQL_PIPELINE.md` for its expected arithmetic.

These tests validate local synthetic contracts, not real source data, causal effects or production readiness. `scripts/verify_environment.py` remains the standalone environment check.
