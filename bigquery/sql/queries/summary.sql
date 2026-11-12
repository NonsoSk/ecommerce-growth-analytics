SELECT COUNT(*) AS sessions,COUNT(DISTINCT customer_id) AS visitors,
 COUNT(DISTINCT CASE WHEN orders>0 THEN customer_id END) AS purchasing_visitors,
 COUNT(DISTINCT CASE WHEN orders>0 THEN session_id END) AS converting_sessions,
 COALESCE(SUM(orders),0) AS orders,
 COALESCE(SUM(merchandise_cents),0) AS merchandise_cents,COALESCE(SUM(refunds_cents),0) AS refunds_cents,
 COALESCE(SUM(net_revenue_cents),0) AS net_revenue_cents,
 COALESCE(SUM(first_observed_purchasers),0) AS first_observed_purchasers,
 COALESCE(SUM(1-refund_window_mature),0) AS refund_immature_sessions
FROM session_finance;
