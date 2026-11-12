-- Exact raw counts/keys and independent monetary totals supplement analytical parity.
SELECT 'campaigns' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT campaign_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, CAST(NULL AS INT64) AS money_total_cents FROM campaigns
UNION ALL
SELECT 'customers' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT customer_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, CAST(NULL AS INT64) AS money_total_cents FROM customers
UNION ALL
SELECT 'sessions' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT session_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, CAST(NULL AS INT64) AS money_total_cents FROM sessions
UNION ALL
SELECT 'events' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT event_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, CAST(NULL AS INT64) AS money_total_cents FROM events
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT order_id) AS duplicate_keys,
 COUNT(*)-COUNT(DISTINCT transaction_id) AS duplicate_transaction_ids, COALESCE(SUM(total_paid_cents),0) AS money_total_cents FROM orders
UNION ALL
SELECT 'order_items' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT order_item_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, COALESCE(SUM(net_merchandise_cents),0) AS money_total_cents FROM order_items
UNION ALL
SELECT 'refunds' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT refund_id) AS duplicate_keys,
 0 AS duplicate_transaction_ids, COALESCE(SUM(merchandise_refund_cents),0) AS money_total_cents FROM refunds
UNION ALL
SELECT 'ad_spend_daily' AS table_name, COUNT(*) AS row_count,
 COUNT(*)-COUNT(DISTINCT TO_JSON_STRING(STRUCT(campaign_id,spend_date))) AS duplicate_keys,
 0 AS duplicate_transaction_ids, COALESCE(SUM(spend_cents),0) AS money_total_cents FROM ad_spend_daily
ORDER BY table_name;
