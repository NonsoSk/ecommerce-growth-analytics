WITH counts AS (
 SELECT COUNT(*) AS sessions, COUNT(start_time) AS session_starts,COUNT(view_time) AS product_views,
 COUNT(cart_time) AS carts,COUNT(checkout_time) AS checkouts,COUNT(purchase_time) AS purchases,
 COALESCE(COUNTIF(skipped_or_out_of_order_events>0),0) AS skipped_or_out_of_order_sessions
 FROM funnel_sessions
)
SELECT *,SAFE_DIVIDE(CAST(carts AS FLOAT64), product_views) AS view_to_cart_rate,
 SAFE_DIVIDE(CAST(checkouts AS FLOAT64), carts) AS cart_to_checkout_rate,
 SAFE_DIVIDE(CAST(purchases AS FLOAT64), checkouts) AS checkout_to_purchase_rate FROM counts;
