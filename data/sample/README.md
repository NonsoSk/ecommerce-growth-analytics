# Synthetic illustrations

`illustrative_journey.json` is a small linked excerpt of the **first paid-channel refunded order** in the default seed-42 baseline: its customer, session, five events, order, item, partial refund, campaign and campaign-day spend. It contains fictional IDs only. It is not a representative sample or a complete reporting dataset; customer first_seen_at may refer to an earlier session outside the excerpt.

Generate the full ignored baseline with `.venv/bin/python scripts/generate_sample.py`. All records are synthetic and provide no evidence about real customers. Separate deliberately invalid event fixtures are in `tests/fixtures/`.
