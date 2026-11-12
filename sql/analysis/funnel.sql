WITH counts AS (
 SELECT COUNT(*) AS sessions, COUNT(start_time) AS session_starts,COUNT(view_time) AS product_views,
 COUNT(cart_time) AS carts,COUNT(checkout_time) AS checkouts,COUNT(purchase_time) AS purchases,
 COALESCE(SUM(skipped_or_out_of_order_events>0),0) AS skipped_or_out_of_order_sessions
 FROM funnel_sessions
)
SELECT *,1.0*carts/NULLIF(product_views,0) AS view_to_cart_rate,
 1.0*checkouts/NULLIF(carts,0) AS cart_to_checkout_rate,
 1.0*purchases/NULLIF(checkouts,0) AS checkout_to_purchase_rate FROM counts;
