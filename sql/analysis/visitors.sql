-- A visitor can appear in both groups across time; group distinct visitors are non-additive.
WITH ranked AS (
 SELECT session_id,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY started_at,session_id) AS visit_number
 FROM sessions
), grouped AS (
 SELECT f.*,CASE WHEN r.visit_number=1 THEN 'first_observed_visit' ELSE 'returning_visit' END AS visit_type
 FROM session_finance f JOIN ranked r USING(session_id)
)
SELECT visit_type,COUNT(*) AS sessions,COUNT(DISTINCT customer_id) AS distinct_visitors,
 COUNT(DISTINCT CASE WHEN orders>0 THEN customer_id END) AS purchasing_visitors,
 SUM(converting_session) AS converting_sessions,SUM(orders) AS orders,
 SUM(first_observed_purchasers) AS first_observed_purchasers,
 SUM(net_revenue_cents) AS net_revenue_cents,
 1.0*SUM(converting_session)/NULLIF(COUNT(*),0) AS order_conversion_rate
FROM grouped GROUP BY visit_type ORDER BY visit_type;
