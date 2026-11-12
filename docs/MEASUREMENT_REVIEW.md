# Milestone 2 measurement review

The baseline generator and simulated values are unchanged. Definitions were checked against the actual JSON fields before SQL implementation. Regression cases are in `tests/test_analysis.py` and the independent `sql_hand_calculated.json` fixture.

| Review point | Decision / correction | Regression evidence |
| --- | --- | --- |
| `customers` includes nonbuyers | Describe the table as visitor identities. Distinct purchasers require paid orders. Default: 1,496 visitors, 331 purchasing visitors. | Five-session fixture has three visitors, two purchasers. |
| Orders vs converting sessions | Count orders separately; order-based conversion counts a session once if it has one or more valid ledger orders. | Four orders across three converting sessions; two orders occur in one session. |
| Ambiguous “reconciled” conversion definition | Financial eligibility depends on valid ledger links and amounts, **not event delivery**. Order conversion remains valid if tracking is absent. Ordered funnel purchase requires an accepted matched event. Expose gaps in reconciliation. | Removing a transaction ID does not remove order revenue or order conversion; its order is reported without an accepted event. |
| First observed vs first-ever customer | Rank paid orders over all available snapshot history before cohort filtering, by ordered_at then order_id. This is a first-observed paid-media CAC proxy only. | Day-2 slice keeps a repeat purchaser out of the new-customer denominator. |
| New vs returning visits | Rank sessions per visitor over the full snapshot. First visit does not imply first purchase. Distinct visitor counts by visit type overlap. | Three first visits and two returning visits; only two distinct purchasers overall. |
| Attribution window | Same-session only, no multi-day lookback, last-nondirect reassignment or cross-session funnel stitching. Direct remains direct. | Prior-session views cannot fill a later session's missing view. |
| Funnel order | Require session_start before product, then cart, checkout and matched purchase. Use earliest valid next occurrence strictly after the predecessor. Repeated attempts count the session once; invalid attempts remain reported. | Out-of-order cart fails until a later valid cart is added; skipped sessions are exported separately. |
| Refund timing | Sum eligible refunds at order grain as of cutoff, then assign them back to originating session-day. Never join unaggregated items and refunds. | Two items, several partial refunds including two on the same item; 35,000 cents less 2,500 = 32,500. |
| Incomplete observation | Exclude sessions not ended before cutoff; report refund-immature sessions. Default maturity is at least 14 days + five minutes after session end, conservative for this generator only. Future daily rows are not_yet_observed, not evidence of zero demand. | Earlier cutoff defers late events, omits later refunds and flags immaturity; a cutoff during a session excludes it. |
| Spend join keys | Union spend and outcome campaign-day keys, not only spend keys. Missing spend is null, not assumed zero. Aggregate campaign ratios are null if any outcome day has missing spend. | Spend-only, zero-spend and conversion-only days survive and get explicit null reasons. |
| Missing fields | No landing page, source/medium, click ID, event revenue amount, lifetime history or financial-record ingestion timestamps. Do not invent these fields. | Schema checks reject unexpected columns; reports document unsupported breakdowns. |

## Important limits

The 90-day cohort is fixed by the manifest, with an exclusive observation date. The default cutoff is 2026-04-16, enough for the modeled 1–14-day refunds plus ingestion. Earlier cutoffs change available events/refunds and complete sessions, not the raw snapshot. Orders and spend have no ingestion time, so an earlier cutoff is an availability approximation, not a true historical warehouse snapshot.

The raw customer field is retained for compatibility; SQL labels make its visitor meaning explicit. Source means the generated channel. Campaign audience names do not enforce real prospecting/retargeting eligibility. All channel/device differences reflect simulation assumptions, mix and chance. Neither attributed revenue nor simulated ROAS establishes incremental effect or supports moving real budgets.
