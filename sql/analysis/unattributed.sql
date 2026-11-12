-- Organic/direct are known unpaid channels, but not attributable to paid campaigns.
SELECT channel,'not_attributed_to_paid_campaign' AS attribution_status,
 COUNT(*) AS sessions,SUM(orders) AS orders,SUM(net_revenue_cents) AS net_revenue_cents,
 SUM(first_observed_purchasers) AS first_observed_purchasers,
 NULL AS paid_cac_cents,NULL AS paid_roas,'no_paid_campaign_assignment' AS ratio_null_reason
FROM session_finance WHERE campaign_id IS NULL GROUP BY channel ORDER BY channel;
