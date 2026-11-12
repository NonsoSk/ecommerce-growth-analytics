# Data dictionary — synthetic schema v1

All identifiers are fictional strings; no names, emails, addresses, IPs or device fingerprints exist. Baseline files are UTF-8 JSON arrays under ignored `data/generated/baseline/`. JSON null means not applicable; it is not an empty string. Every timestamp is UTC ISO 8601 with `Z`; every date is `YYYY-MM-DD`. Monetary columns ending `_cents` are nonnegative integers in USD. Quantity is a positive integer. These are local simulation contracts, not actual GA4 or Shopify exports.

## Relationships and grain

| Table | One row represents | Primary key | Foreign keys |
| --- | --- | --- | --- |
| customers | One observed synthetic visitor identity, including nonbuyers | customer_id | None |
| sessions | One visit with one channel/device | session_id | customer_id → customers; nullable campaign_id → campaigns |
| events | One observed action | event_id | session_id → sessions; purchase transaction_id → orders.transaction_id |
| orders | One paid order | order_id; transaction_id is also unique | customer_id → customers; session_id → sessions |
| order_items | One product line on an order | order_item_id | order_id → orders |
| refunds | One partial refund allocated to one order item | refund_id | order_item_id → order_items; order_id → orders, must match the item |
| ad_spend_daily | Spend for one campaign on one UTC day | (campaign_id, spend_date) | campaign_id → campaigns |
| campaigns | One synthetic paid campaign (supporting dimension) | campaign_id | None |

Customers → sessions → events are one-to-many. Customers and sessions → orders, orders → items, and items → refunds are one-to-many contracts even though v1 generates at most one order per session, one item line per order and one refund per item. There is exactly one baseline purchase event per order. Events have no spend column. Repeating an order’s total on item rows or a campaign’s spend on events is forbidden.

## Columns

### customers

| Column | Type / meaning |
| --- | --- |
| customer_id | String PK, `syn_c…`; visitor identity, not evidence of a buyer |
| first_seen_at | Timestamp of earliest generated session, not account registration or lifetime acquisition |

### sessions

| Column | Type / meaning |
| --- | --- |
| session_id | String PK, `syn_s…` |
| customer_id | Non-null customer FK |
| started_at / ended_at | Occurrence timestamps; all session events fall within these bounds |
| channel | `google`, `meta`, `organic` or `direct` |
| campaign_id | Paid campaign FK for google/meta; null for organic/direct |
| device | `mobile` or `desktop`; a synthetic category, not a physical device ID |

### events

| Column | Type / meaning |
| --- | --- |
| event_id | String PK, `syn_e…`; transport identity, distinct from transaction identity |
| session_id | Non-null session FK; customer and acquisition dimensions come through session |
| event_name | `session_start`, `view_item`, `add_to_cart`, `begin_checkout`, `purchase` |
| occurred_at | When the visitor action occurred; determines behavior ordering |
| ingested_at | When the record became available; determines as-of visibility; baseline occurrence + 5 seconds |
| transaction_id | Order’s unique transaction key on purchase; null on all other events. Missing purchase IDs are invalid in baseline but intentional in fixtures. |

### orders

| Column | Type / meaning |
| --- | --- |
| order_id | String PK, `syn_o…` |
| transaction_id | Non-null unique string `syn_tx…`; cross-source purchase reconciliation key |
| customer_id / session_id | Non-null FKs; customer must match the session’s customer |
| ordered_at | Paid-order occurrence timestamp, equal to its purchase event’s occurred_at |
| currency / status | Always `USD` / `paid` in v1 |
| gross_merchandise_cents | Sum(quantity × unit_price_cents) across items |
| discount_cents | Sum of item discounts, allocated once at line level |
| tax_cents / shipping_cents | Original charges; tax is floor(8% × merchandise after discount); shipping is zero |
| total_paid_cents | Gross merchandise − discounts + tax + shipping, before refunds |

### order_items

| Column | Type / meaning |
| --- | --- |
| order_item_id / order_id | String PK `syn_i…` / order FK |
| product_id | Fictional mattress SKU derived from price tier; no separate product table in v1 |
| quantity / unit_price_cents | Positive integer quantity / per-unit gross price |
| discount_cents | Discount for the entire line, not per unit |
| net_merchandise_cents | quantity × unit_price_cents − discount_cents; **before refunds** |
| currency | `USD`, consistent with parent order |

### refunds

| Column | Type / meaning |
| --- | --- |
| refund_id | String PK, `syn_r…` |
| order_id / order_item_id | Non-null consistent order and item FKs |
| refunded_at | Refund occurrence, after original order; can fall beyond the traffic window |
| ingested_at | Availability time, refunded_at + 5 minutes |
| merchandise_refund_cents | Positive refund of merchandise after discounts; accumulated item refunds cannot exceed item net merchandise |
| tax_refund_cents / shipping_refund_cents | Separately refunded charges; accumulated amounts cannot exceed original order charges |
| currency | `USD`, consistent with parent order |

Refunds are monetary adjustments, not returned-unit counts. Net merchandise revenue is derived after aggregating merchandise refunds; the order’s original payment is never overwritten. The validator enforces cumulative limits, including multiple refund records.

### ad_spend_daily and campaigns

| Table.column | Type / meaning |
| --- | --- |
| ad_spend_daily.campaign_id | Campaign FK; part of composite PK |
| ad_spend_daily.spend_date | UTC activity date; part of composite PK |
| ad_spend_daily.spend_cents | One whole-day media cost; independent of event count |
| ad_spend_daily.currency | `USD` |
| campaigns.campaign_id | String PK, e.g. `syn_google_prospecting` |
| campaigns.channel | `google` or `meta`; must match linked sessions |
| campaigns.audience | `prospecting` or `retargeting`, illustrative label only |
| campaigns.currency | `USD` |

Every campaign has all 90 spend dates, including dates with no attributed sessions/orders. Four campaigns × 90 days = 360 rows at every generated size. No device-level spend exists. Spend is not a function of generated purchases and has no impressions or clicks in this milestone.

## Availability and metadata

Only events and refunds model ingestion timestamps. Customers, sessions, orders, items and spend are complete static synthetic snapshots; they do not model delayed ingestion or evolving order status. Do not infer real extraction freshness from them. `manifest.json` records the seed, generator version, input size, start/end dates, observation cutoff, currency, timezone, row counts, SHA-256 hashes and control totals. There is deliberately no machine time in generated files so identical inputs produce identical bytes on the verified Python 3.14 environment.

## Milestone 2 analytical interpretation

The raw schema and simulated values are unchanged. `customers` means observed visitor identities; purchasing customers are the subset with paid orders. Landing page, source/medium, click IDs and event revenue amounts are absent. SQLite's copied `events` table deliberately retains invalid transaction/session references for audit; the table above describes the clean baseline contract, not a rule that invalid raw events must be discarded. See SQL_PIPELINE.md for explicit load constraints, derived views and output grains.
