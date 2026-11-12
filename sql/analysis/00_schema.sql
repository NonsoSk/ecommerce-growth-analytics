PRAGMA foreign_keys = ON;
CREATE TABLE parameters (
 id INTEGER PRIMARY KEY CHECK(id=1), start_at TEXT NOT NULL,
 end_at TEXT NOT NULL, cutoff TEXT NOT NULL, CHECK(start_at < end_at)
) STRICT;
CREATE TABLE campaigns (
 campaign_id TEXT PRIMARY KEY, channel TEXT NOT NULL CHECK(channel IN ('google','meta')),
 audience TEXT NOT NULL, currency TEXT NOT NULL CHECK(currency='USD')
) STRICT;
CREATE TABLE customers (customer_id TEXT PRIMARY KEY, first_seen_at TEXT NOT NULL) STRICT;
CREATE TABLE sessions (
 session_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, customer_id TEXT NOT NULL REFERENCES customers,
 channel TEXT NOT NULL CHECK(channel IN ('google','meta','organic','direct')),
 campaign_id TEXT REFERENCES campaigns, device TEXT NOT NULL CHECK(device IN ('mobile','desktop')),
 ended_at TEXT NOT NULL CHECK(ended_at>started_at), UNIQUE(session_id,customer_id),
 CHECK((channel IN ('google','meta') AND campaign_id IS NOT NULL) OR
       (channel IN ('organic','direct') AND campaign_id IS NULL))
) STRICT;
CREATE TABLE orders (
 order_id TEXT PRIMARY KEY, transaction_id TEXT NOT NULL UNIQUE,
 customer_id TEXT NOT NULL REFERENCES customers, session_id TEXT NOT NULL,
 ordered_at TEXT NOT NULL, currency TEXT NOT NULL CHECK(currency='USD'),
 status TEXT NOT NULL CHECK(status='paid'),
 gross_merchandise_cents INTEGER NOT NULL CHECK(gross_merchandise_cents>=0),
 discount_cents INTEGER NOT NULL CHECK(discount_cents BETWEEN 0 AND gross_merchandise_cents),
 tax_cents INTEGER NOT NULL CHECK(tax_cents>=0), shipping_cents INTEGER NOT NULL CHECK(shipping_cents>=0),
 total_paid_cents INTEGER NOT NULL,
 FOREIGN KEY(session_id,customer_id) REFERENCES sessions(session_id,customer_id),
 CHECK(total_paid_cents=gross_merchandise_cents-discount_cents+tax_cents+shipping_cents)
) STRICT;
CREATE TABLE order_items (
 order_item_id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES orders,
 product_id TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>0),
 unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents>0),
 discount_cents INTEGER NOT NULL CHECK(discount_cents BETWEEN 0 AND quantity*unit_price_cents),
 net_merchandise_cents INTEGER NOT NULL CHECK(net_merchandise_cents=quantity*unit_price_cents-discount_cents),
 currency TEXT NOT NULL CHECK(currency='USD'), UNIQUE(order_item_id,order_id)
) STRICT;
CREATE TABLE refunds (
 refund_id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES orders, order_item_id TEXT NOT NULL,
 refunded_at TEXT NOT NULL, ingested_at TEXT NOT NULL CHECK(ingested_at>=refunded_at),
 merchandise_refund_cents INTEGER NOT NULL CHECK(merchandise_refund_cents>0),
 tax_refund_cents INTEGER NOT NULL CHECK(tax_refund_cents>=0),
 shipping_refund_cents INTEGER NOT NULL CHECK(shipping_refund_cents>=0),
 currency TEXT NOT NULL CHECK(currency='USD'),
 FOREIGN KEY(order_item_id,order_id) REFERENCES order_items(order_item_id,order_id)
) STRICT;
CREATE TABLE ad_spend_daily (
 campaign_id TEXT NOT NULL REFERENCES campaigns, spend_date TEXT NOT NULL,
 spend_cents INTEGER NOT NULL CHECK(spend_cents>=0), currency TEXT NOT NULL CHECK(currency='USD'),
 PRIMARY KEY(campaign_id,spend_date)
) STRICT;
-- Raw events intentionally allow bad transaction/session links for quarantine reporting.
-- Unique event IDs enforce transport identity; repeated transactions remain separate records.
CREATE TABLE events (
 event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, event_name TEXT NOT NULL,
 occurred_at TEXT NOT NULL, ingested_at TEXT NOT NULL, transaction_id TEXT
) STRICT;
CREATE INDEX events_session_time ON events(session_id,occurred_at);
CREATE INDEX events_transaction ON events(transaction_id);
CREATE INDEX orders_session ON orders(session_id);
