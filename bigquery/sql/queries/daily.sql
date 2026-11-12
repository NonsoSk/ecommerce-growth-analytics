-- One row per cohort date, including no-traffic dates. Merchandise is after discounts, before refunds.
WITH calendar AS (
 SELECT day FROM parameters,
 UNNEST(GENERATE_DATE_ARRAY(DATE(start_at), DATE_SUB(DATE(end_at), INTERVAL 1 DAY))) AS day
), totals AS (
 SELECT session_date,COUNT(*) AS sessions,SUM(converting_session) AS converting_sessions,
 SUM(orders) AS orders,SUM(merchandise_cents) AS merchandise_cents,
 SUM(refund_records) AS refund_records,SUM(refunds_cents) AS refunds_cents,
 SUM(net_revenue_cents) AS net_revenue_cents,
 SUM(1-refund_window_mature) AS refund_immature_sessions
 FROM session_finance GROUP BY session_date
)
SELECT day AS session_date, COALESCE(sessions,0) AS sessions,
 CASE WHEN day>=(SELECT DATE(cutoff) FROM parameters)
 THEN 'not_yet_observed' ELSE 'observed_through_cutoff' END AS observation_status,
 COALESCE(converting_sessions,0) AS converting_sessions,COALESCE(orders,0) AS orders,
 COALESCE(merchandise_cents,0) AS merchandise_cents,COALESCE(refund_records,0) AS refund_records,
 COALESCE(refunds_cents,0) AS refunds_cents,COALESCE(net_revenue_cents,0) AS net_revenue_cents,
 COALESCE(refund_immature_sessions,0) AS refund_immature_sessions,
 SAFE_DIVIDE(CAST(converting_sessions AS FLOAT64), sessions) AS order_conversion_rate,
 SAFE_DIVIDE(CAST(merchandise_cents AS FLOAT64), orders) AS aov_cents,
 SAFE_DIVIDE(CAST(net_revenue_cents AS FLOAT64), sessions) AS revenue_per_session_cents,
 CASE WHEN COALESCE(sessions,0)=0 THEN 'no_eligible_sessions' END AS session_ratio_null_reason,
 CASE WHEN COALESCE(orders,0)=0 THEN 'no_eligible_orders' END AS aov_null_reason
FROM calendar LEFT JOIN totals ON session_date=day ORDER BY day;
