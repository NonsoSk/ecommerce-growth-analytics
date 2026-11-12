-- Separate session-level output; never silently classify skipped steps as ordinary drop-off.
SELECT session_id,customer_id,session_date,device,channel,start_time,view_time,cart_time,
 checkout_time,purchase_time,skipped_or_out_of_order_events,
 'missing_or_nonchronological_predecessor' AS reason
FROM funnel_sessions WHERE skipped_or_out_of_order_events>0 ORDER BY session_date,session_id;
