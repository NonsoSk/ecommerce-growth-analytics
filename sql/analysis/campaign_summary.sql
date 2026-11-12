-- Recompute ratios from summed numerators/denominators; never average daily ratios.
WITH totals AS (
 SELECT campaign_id,channel,SUM(spend_cents) AS spend_cents,SUM(sessions) AS sessions,
 SUM(attributed_orders) AS attributed_orders,SUM(net_revenue_cents) AS net_revenue_cents,
 SUM(first_observed_purchasers) AS first_observed_purchasers,
 SUM(coverage='missing_spend') AS missing_spend_days,
 SUM(attributed_orders=0 AND spend_cents>0) AS paid_days_without_orders
 FROM campaign_per_day GROUP BY campaign_id,channel
)
SELECT *,CASE WHEN missing_spend_days=0 THEN 1.0*net_revenue_cents/NULLIF(spend_cents,0) END AS net_roas,
 CASE WHEN missing_spend_days=0 THEN 1.0*spend_cents/NULLIF(first_observed_purchasers,0) END AS observed_paid_cac_cents
FROM totals ORDER BY campaign_id;
