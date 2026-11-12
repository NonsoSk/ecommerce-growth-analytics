# Separate event-quality fixtures

`tests/fixtures/event_quality.json` contains **three independent synthetic cases and four event rows**. They are deliberately tiny detector inputs, not complete linked datasets; `fixture_session` and `fixture_tx` are fixture-only identifiers. Do not run the full baseline foreign-key validator on them or append them to baseline tables.

| Case | Deliberate issue | Expected detector output | Intended handling |
| --- | --- | --- | --- |
| duplicate_purchase | Two different event IDs share one transaction ID | duplicate_purchase = [fixture_dup_b] | Preserve raw records. Count only one reconciled transaction/order; choose earliest ingestion then event ID as canonical candidate. Investigate conflicting payloads rather than selecting silently. |
| missing_transaction_id | Purchase has null transaction ID | missing_transaction_id = [fixture_missing] | Quarantine from verified purchase counts and revenue attribution; do not invent an order match. Independently report valid orders and reconciliation gaps. |
| late_arrival | A product view arrives 72 hours after occurrence | late_arrival = [fixture_late] | Retain occurrence time; before ingestion cutoff it is unavailable, afterward restate the original occurrence cohort. Do not move it to the ingestion day. |

All other issue lists are empty per case. Late means strictly **more than 24 hours**, a project monitoring threshold, not a GA4 guarantee; exactly 24 hours is not flagged. Duplicate detection processes ingestion time then event ID, so input row order cannot choose the canonical record. The detector returns IDs without mutating or deleting input. Actual quarantine, reconciliation dashboards and incremental backfill are planned, not implemented.

Tests assert the exact expected IDs, zero baseline detections, boundary behavior and unchanged input. Separate corruption tests also prove the baseline validator rejects broken keys, invalid order/event relationships, chronology errors, money discrepancies and cumulative over-refunds.
