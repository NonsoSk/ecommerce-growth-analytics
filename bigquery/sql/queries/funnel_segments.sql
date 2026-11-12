-- Source is sessions.channel; no landing-page field exists, so no landing-page breakdown is fabricated.
WITH segments AS (
 SELECT 'device' AS dimension,device AS segment,* FROM funnel_sessions
 UNION ALL SELECT 'source',channel,* FROM funnel_sessions
), totals AS (
 SELECT dimension,segment,COUNT(*) AS sessions,COUNT(view_time) AS product_views,
 COUNT(cart_time) AS carts,COUNT(checkout_time) AS checkouts,COUNT(purchase_time) AS purchases,
 COUNTIF(skipped_or_out_of_order_events>0) AS skipped_or_out_of_order_sessions
 FROM segments GROUP BY dimension,segment
)
SELECT *,SAFE_DIVIDE(CAST(carts AS FLOAT64), product_views) AS view_to_cart_rate,
 SAFE_DIVIDE(CAST(checkouts AS FLOAT64), carts) AS cart_to_checkout_rate,
 SAFE_DIVIDE(CAST(purchases AS FLOAT64), checkouts) AS checkout_to_purchase_rate,
 SAFE_DIVIDE(CAST(purchases AS FLOAT64), sessions) AS ordered_funnel_conversion_rate
FROM totals ORDER BY dimension,segment;
