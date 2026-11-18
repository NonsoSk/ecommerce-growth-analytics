-- One row per campaign-day. Numerators/denominators only: never average daily ratios.
SELECT day,campaign_id,channel,spend_cents,attributed_orders,net_revenue_cents,
 first_observed_purchasers,CASE WHEN coverage='missing_spend' THEN 1 ELSE 0 END missing_spend_days,
 CASE WHEN spend_cents>0 AND attributed_orders=0 THEN 1 ELSE 0 END days_with_spend_zero_orders,
 coverage
FROM campaign_per_day ORDER BY day,campaign_id;
