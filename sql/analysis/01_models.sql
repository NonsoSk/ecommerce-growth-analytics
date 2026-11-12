-- All views are as-of parameterized without mutating raw snapshots.
CREATE VIEW cohort_sessions AS
SELECT s.*, substr(started_at,1,10) AS session_date,
 CASE WHEN julianday(p.cutoff)-julianday(s.ended_at)>=14.0+5.0/1440
      THEN 1 ELSE 0 END AS refund_window_mature
FROM sessions s CROSS JOIN parameters p
WHERE s.started_at>=p.start_at AND s.started_at<p.end_at AND s.ended_at<p.cutoff;

CREATE VIEW event_audit AS
WITH checked AS (
 SELECT e.*, CASE
  WHEN e.ingested_at>=p.cutoff OR e.occurred_at>=p.cutoff THEN 'not_yet_available'
  WHEN e.ingested_at<e.occurred_at THEN 'ingestion_before_occurrence'
  WHEN s.session_id IS NULL THEN 'unknown_session'
  WHEN e.occurred_at<s.started_at OR e.occurred_at>s.ended_at THEN 'outside_session'
  WHEN e.event_name NOT IN ('session_start','view_item','add_to_cart','begin_checkout','purchase') THEN 'unknown_event'
  WHEN e.event_name='purchase' AND (e.transaction_id IS NULL OR e.transaction_id='') THEN 'missing_transaction_id'
  WHEN e.event_name='purchase' AND o.order_id IS NULL THEN 'unmatched_transaction'
  WHEN e.event_name='purchase' AND (o.session_id<>e.session_id OR o.ordered_at<>e.occurred_at) THEN 'order_event_mismatch'
  WHEN e.event_name<>'purchase' AND e.transaction_id IS NOT NULL THEN 'unexpected_transaction_id'
  ELSE 'candidate' END AS initial_reason,
  CASE WHEN julianday(e.ingested_at)-julianday(e.occurred_at)>1 THEN 1 ELSE 0 END AS late_arrival
 FROM events e CROSS JOIN parameters p
 LEFT JOIN sessions s ON s.session_id=e.session_id
 LEFT JOIN orders o ON o.transaction_id=e.transaction_id
), ranked AS (
 SELECT event_id, ROW_NUMBER() OVER (
  PARTITION BY CASE WHEN event_name='purchase' THEN 'tx:'||transaction_id ELSE 'event:'||event_id END
  ORDER BY ingested_at,event_id) AS delivery_rank
 FROM checked WHERE initial_reason='candidate'
)
SELECT c.*, CASE WHEN initial_reason<>'candidate' THEN initial_reason
 WHEN r.delivery_rank>1 THEN 'duplicate_purchase' ELSE 'accepted' END AS reason
FROM checked c LEFT JOIN ranked r USING(event_id);

CREATE VIEW accepted_events AS SELECT * FROM event_audit WHERE reason='accepted';

CREATE VIEW order_finance AS
WITH items AS (
 SELECT order_id, SUM(quantity*unit_price_cents) AS gross_cents,
 SUM(discount_cents) AS discounts_cents, SUM(net_merchandise_cents) AS merchandise_cents
 FROM order_items GROUP BY order_id
), returns AS (
 SELECT order_id, COUNT(*) AS refund_records, SUM(merchandise_refund_cents) AS refunds_cents
 FROM refunds CROSS JOIN parameters p
 WHERE refunded_at<p.cutoff AND ingested_at<p.cutoff GROUP BY order_id
), ranked_orders AS (
 -- Rank globally before cohort filtering: returning buyers are not reacquired in each slice.
 SELECT o.*, ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY ordered_at,order_id) AS purchase_number
 FROM orders o CROSS JOIN parameters p WHERE ordered_at<p.cutoff
)
SELECT o.*, s.session_date,s.channel,s.campaign_id,s.device,s.refund_window_mature,
 i.gross_cents,i.discounts_cents,i.merchandise_cents,
 COALESCE(r.refund_records,0) AS refund_records, COALESCE(r.refunds_cents,0) AS refunds_cents,
 i.merchandise_cents-COALESCE(r.refunds_cents,0) AS net_revenue_cents,
 CASE WHEN o.purchase_number=1 THEN 1 ELSE 0 END AS first_observed_purchaser
FROM ranked_orders o JOIN cohort_sessions s USING(session_id)
JOIN items i USING(order_id) LEFT JOIN returns r USING(order_id);

CREATE VIEW session_finance AS
WITH outcomes AS (
 SELECT session_id,COUNT(*) AS orders,SUM(merchandise_cents) AS merchandise_cents,
 SUM(refund_records) AS refund_records,SUM(refunds_cents) AS refunds_cents,
 SUM(net_revenue_cents) AS net_revenue_cents,
 SUM(first_observed_purchaser) AS first_observed_purchasers
 FROM order_finance GROUP BY session_id
)
SELECT s.*, COALESCE(o.orders,0) AS orders,
 CASE WHEN o.orders>0 THEN 1 ELSE 0 END AS converting_session,
 COALESCE(o.merchandise_cents,0) AS merchandise_cents,
 COALESCE(o.refund_records,0) AS refund_records,COALESCE(o.refunds_cents,0) AS refunds_cents,
 COALESCE(o.net_revenue_cents,0) AS net_revenue_cents,
 COALESCE(o.first_observed_purchasers,0) AS first_observed_purchasers
FROM cohort_sessions s LEFT JOIN outcomes o USING(session_id);

CREATE VIEW funnel_sessions AS
-- Earliest eligible occurrence after the preceding step; later valid retries can qualify.
-- Same session only; the session_start prefix remains required.
WITH starts AS (
 SELECT s.*, (SELECT MIN(e.occurred_at) FROM accepted_events e WHERE e.session_id=s.session_id AND e.event_name='session_start') AS start_time
 FROM cohort_sessions s
), views AS (
 SELECT s.*, (SELECT MIN(e.occurred_at) FROM accepted_events e WHERE e.session_id=s.session_id AND e.event_name='view_item' AND e.occurred_at>s.start_time) AS view_time FROM starts s
), carts AS (
 SELECT s.*, (SELECT MIN(e.occurred_at) FROM accepted_events e WHERE e.session_id=s.session_id AND e.event_name='add_to_cart' AND e.occurred_at>s.view_time) AS cart_time FROM views s
), checkouts AS (
 SELECT s.*, (SELECT MIN(e.occurred_at) FROM accepted_events e WHERE e.session_id=s.session_id AND e.event_name='begin_checkout' AND e.occurred_at>s.cart_time) AS checkout_time FROM carts s
), purchases AS (
 SELECT s.*, (SELECT MIN(e.occurred_at) FROM accepted_events e WHERE e.session_id=s.session_id AND e.event_name='purchase' AND e.occurred_at>s.checkout_time) AS purchase_time FROM checkouts s
)
SELECT s.*, (SELECT COUNT(*) FROM accepted_events e WHERE e.session_id=s.session_id AND (
 (e.event_name='view_item' AND (start_time IS NULL OR e.occurred_at<=start_time)) OR
 (e.event_name='add_to_cart' AND (view_time IS NULL OR e.occurred_at<=view_time)) OR
 (e.event_name='begin_checkout' AND (cart_time IS NULL OR e.occurred_at<=cart_time)) OR
 (e.event_name='purchase' AND (checkout_time IS NULL OR e.occurred_at<=checkout_time))
)) AS skipped_or_out_of_order_events
FROM purchases s;
