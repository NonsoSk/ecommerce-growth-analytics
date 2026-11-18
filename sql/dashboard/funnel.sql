-- One row per day/device/channel/observed visit type; no campaign spend in this source.
WITH visits AS (
 SELECT session_id,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY started_at,session_id) visit_number
 FROM sessions
)
SELECT f.session_date AS day,f.device,f.channel,
 CASE WHEN v.visit_number=1 THEN 'first_observed_visit' ELSE 'returning_visit' END visit_type,
 COUNT(*) sessions,COUNT(start_time) session_starts,COUNT(view_time) product_views,
 COUNT(cart_time) carts,COUNT(checkout_time) checkouts,COUNT(purchase_time) purchases,
 SUM(skipped_or_out_of_order_events>0) skipped_or_out_of_order_sessions
FROM funnel_sessions f JOIN visits v USING(session_id)
GROUP BY day,device,channel,visit_type ORDER BY day,device,channel,visit_type;
