# Automated checks

Run `.venv/bin/python -m unittest discover -s tests -v` from the repository root. Standard-library tests check byte-for-byte regeneration, configuration, required default patterns, unique keys, foreign keys, ordered journeys, transaction matching, monetary reconciliation, cumulative refund limits, campaign-day spend preservation and exact quality-fixture detection. Corruption tests deliberately break valid data to check that validation fails.

`fixtures/event_quality.json` is separate from the clean baseline. Its four events test duplicate purchases, missing transaction IDs and late arrival. They are independent detector inputs, not complete customer/order datasets. See `docs/QUALITY_FIXTURES.md` for handling expectations.

These tests validate synthetic contracts, not business conclusions, live source data or production readiness. `scripts/verify_environment.py` remains the standalone environment check.
