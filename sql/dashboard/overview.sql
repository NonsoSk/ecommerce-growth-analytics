-- One row per session-cohort UTC day. Spend is aggregated to day BEFORE this join.
WITH daily AS (
 SELECT session_date,COUNT(*) sessions,SUM(converting_session) converting_sessions,
 SUM(orders) orders,SUM(net_revenue_cents) net_revenue_cents,SUM(refunds_cents) refunds_cents
 FROM session_finance GROUP BY session_date
), spend AS (
 SELECT day,SUM(spend_cents) spend_cents,SUM(coverage='missing_spend') missing_spend_days
 FROM campaign_per_day GROUP BY day
), days AS (SELECT session_date AS day FROM daily UNION SELECT day FROM spend)
SELECT day,COALESCE(sessions,0) sessions,COALESCE(converting_sessions,0) converting_sessions,
 COALESCE(orders,0) orders,COALESCE(net_revenue_cents,0) net_revenue_cents,
 COALESCE(refunds_cents,0) refunds_cents,spend_cents,
 COALESCE(missing_spend_days,0) missing_spend_days
FROM days LEFT JOIN daily ON session_date=day LEFT JOIN spend USING(day) ORDER BY day;
