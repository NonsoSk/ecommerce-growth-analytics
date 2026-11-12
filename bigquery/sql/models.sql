-- GoogleSQL CTE definitions, composed after typed parameters and allowlisted raw-table aliases.
cohort_sessions AS (
SELECT s.*, DATE(started_at) AS session_date,
 CASE WHEN p.cutoff >= TIMESTAMP_ADD(s.ended_at, INTERVAL 1209900 SECOND)
      THEN 1 ELSE 0 END AS refund_window_mature
FROM sessions s CROSS JOIN parameters p
WHERE s.started_at>=p.start_at AND s.started_at<p.end_at AND s.ended_at<p.cutoff
),
event_audit AS (
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
  CASE WHEN e.ingested_at > TIMESTAMP_ADD(e.occurred_at, INTERVAL 24 HOUR) THEN 1 ELSE 0 END AS late_arrival
 FROM events e CROSS JOIN parameters p
 LEFT JOIN sessions s ON s.session_id=e.session_id
 LEFT JOIN orders o ON o.transaction_id=e.transaction_id
), ranked AS (
 SELECT event_id, ROW_NUMBER() OVER (
  PARTITION BY CASE WHEN event_name='purchase' THEN CONCAT('tx:',transaction_id) ELSE CONCAT('event:',event_id) END
  ORDER BY ingested_at,event_id) AS delivery_rank
 FROM checked WHERE initial_reason='candidate'
)
SELECT c.*, CASE WHEN initial_reason<>'candidate' THEN initial_reason
 WHEN r.delivery_rank>1 THEN 'duplicate_purchase' ELSE 'accepted' END AS reason
FROM checked c LEFT JOIN ranked r USING(event_id)
),
accepted_events AS (
SELECT * FROM event_audit WHERE reason='accepted'
),
order_finance AS (
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
JOIN items i USING(order_id) LEFT JOIN returns r USING(order_id)
),
session_finance AS (
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
FROM cohort_sessions s LEFT JOIN outcomes o USING(session_id)
),
funnel_starts AS (
 SELECT s.session_id, MIN(e.occurred_at) AS start_time
 FROM cohort_sessions s LEFT JOIN accepted_events e
 ON e.session_id=s.session_id AND e.event_name='session_start' GROUP BY s.session_id
),
funnel_views AS (
 SELECT s.session_id,s.start_time,MIN(e.occurred_at) AS view_time
 FROM funnel_starts s LEFT JOIN accepted_events e ON e.session_id=s.session_id
 AND e.event_name='view_item' AND e.occurred_at>s.start_time GROUP BY s.session_id,s.start_time
),
funnel_carts AS (
 SELECT s.session_id,s.start_time,s.view_time,MIN(e.occurred_at) AS cart_time
 FROM funnel_views s LEFT JOIN accepted_events e ON e.session_id=s.session_id
 AND e.event_name='add_to_cart' AND e.occurred_at>s.view_time GROUP BY s.session_id,s.start_time,s.view_time
),
funnel_checkouts AS (
 SELECT s.session_id,s.start_time,s.view_time,s.cart_time,MIN(e.occurred_at) AS checkout_time
 FROM funnel_carts s LEFT JOIN accepted_events e ON e.session_id=s.session_id
 AND e.event_name='begin_checkout' AND e.occurred_at>s.cart_time
 GROUP BY s.session_id,s.start_time,s.view_time,s.cart_time
),
funnel_purchases AS (
 SELECT s.session_id,s.start_time,s.view_time,s.cart_time,s.checkout_time,MIN(e.occurred_at) AS purchase_time
 FROM funnel_checkouts s LEFT JOIN accepted_events e ON e.session_id=s.session_id
 AND e.event_name='purchase' AND e.occurred_at>s.checkout_time
 GROUP BY s.session_id,s.start_time,s.view_time,s.cart_time,s.checkout_time
),
funnel_bad_steps AS (
 SELECT s.session_id,COUNTIF(
 (e.event_name='view_item' AND (start_time IS NULL OR e.occurred_at<=start_time)) OR
 (e.event_name='add_to_cart' AND (view_time IS NULL OR e.occurred_at<=view_time)) OR
 (e.event_name='begin_checkout' AND (cart_time IS NULL OR e.occurred_at<=cart_time)) OR
 (e.event_name='purchase' AND (checkout_time IS NULL OR e.occurred_at<=checkout_time))
 ) AS skipped_or_out_of_order_events
 FROM funnel_purchases s LEFT JOIN accepted_events e USING(session_id) GROUP BY s.session_id
),
funnel_sessions AS (
 SELECT s.*,p.* EXCEPT(session_id),b.skipped_or_out_of_order_events
 FROM cohort_sessions s JOIN funnel_purchases p USING(session_id) JOIN funnel_bad_steps b USING(session_id)
)
