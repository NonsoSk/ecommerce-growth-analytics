SELECT event_id,session_id,event_name,transaction_id,occurred_at,ingested_at,reason,late_arrival,
 CASE WHEN reason='accepted' AND late_arrival=1 THEN 'included_late_restatement'
 WHEN reason='accepted' THEN 'included'
 WHEN reason='not_yet_available' THEN 'deferred' ELSE 'quarantined' END AS disposition
FROM event_audit ORDER BY event_id;
