-- Order-side coverage plus every excluded purchase event: no inner join hides unmatched activity.
SELECT 'order' AS record_type,o.order_id AS record_id,o.transaction_id,
 CASE WHEN EXISTS(SELECT 1 FROM accepted_events e WHERE e.transaction_id=o.transaction_id AND e.event_name='purchase')
 THEN 'matched' ELSE 'order_without_accepted_purchase_event' END AS status,
 o.merchandise_cents
FROM order_finance o
UNION ALL
SELECT 'purchase_event',e.event_id,e.transaction_id,e.reason,NULL
FROM event_audit e WHERE e.event_name='purchase' AND e.reason<>'accepted'
ORDER BY record_type,record_id;
