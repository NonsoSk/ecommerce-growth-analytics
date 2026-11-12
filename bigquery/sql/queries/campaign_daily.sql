-- Same-session attribution. Full key union preserves spend-only and outcome-only days.
WITH outcomes AS (
 SELECT campaign_id,channel,session_date,COUNT(*) AS sessions,
 SUM(orders) AS attributed_orders,SUM(net_revenue_cents) AS net_revenue_cents,
 SUM(first_observed_purchasers) AS first_observed_purchasers
 FROM session_finance WHERE campaign_id IS NOT NULL GROUP BY campaign_id,channel,session_date
), spend AS (
 SELECT a.* FROM ad_spend_daily a,parameters p
 WHERE spend_date>=DATE(p.start_at) AND spend_date<DATE(p.end_at)
 AND spend_date<DATE(p.cutoff) -- full-day spend only; partial cutoff days are unsupported
), keys AS (
 SELECT campaign_id,spend_date AS day FROM spend
 UNION DISTINCT SELECT campaign_id,session_date FROM outcomes
), joined AS (
 SELECT k.day,k.campaign_id,c.channel,s.spend_cents,
 COALESCE(o.sessions,0) AS sessions,COALESCE(o.attributed_orders,0) AS attributed_orders,
 COALESCE(o.net_revenue_cents,0) AS net_revenue_cents,
 COALESCE(o.first_observed_purchasers,0) AS first_observed_purchasers,
 CASE WHEN s.campaign_id IS NULL THEN 'missing_spend' WHEN o.campaign_id IS NULL THEN 'spend_only' ELSE 'matched' END AS coverage
 FROM keys k JOIN campaigns c USING(campaign_id)
 LEFT JOIN spend s ON s.campaign_id=k.campaign_id AND s.spend_date=k.day
 LEFT JOIN outcomes o ON o.campaign_id=k.campaign_id AND o.session_date=k.day
)
SELECT *,SAFE_DIVIDE(CAST(net_revenue_cents AS FLOAT64), spend_cents) AS net_roas,
 SAFE_DIVIDE(CAST(spend_cents AS FLOAT64), first_observed_purchasers) AS observed_paid_cac_cents,
 CASE WHEN spend_cents IS NULL THEN 'missing_spend' WHEN spend_cents=0 THEN 'zero_spend' ELSE NULL END AS roas_null_reason,
 CASE WHEN spend_cents IS NULL THEN 'missing_spend' WHEN first_observed_purchasers=0 THEN 'no_first_observed_purchasers' ELSE NULL END AS cac_null_reason
FROM joined ORDER BY day,campaign_id;
