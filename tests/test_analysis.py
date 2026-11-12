"""Hand-calculated SQL expectations, independent of the random generator."""
from copy import deepcopy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.analysis import load_database, query, summary, reconciliation_controls, QUERIES, fixture_demo, run_analysis
from ecommerce_growth.synthetic import write_dataset


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tables=json.loads((ROOT/'tests/fixtures/sql_hand_calculated.json').read_text())['tables']
        self.db=load_database(self.tables,end='2026-01-06',cutoff='2026-01-20')

    def tearDown(self):
        self.db.close()

    def test_hand_calculated_multiple_items_refunds_and_orders(self):
        s=summary(self.db)
        self.assertEqual((s['sessions'],s['visitors'],s['purchasing_visitors'],s['orders'],s['converting_sessions']), (5,3,2,4,3))
        self.assertEqual((s['merchandise_cents'],s['refunds_cents'],s['net_revenue_cents']), (35000,2500,32500))
        daily=query(self.db,'daily')
        self.assertEqual(len(daily),5)
        self.assertEqual((daily[0]['orders'],daily[0]['converting_sessions'],daily[0]['net_revenue_cents']), (2,1,18000))
        self.assertEqual(daily[0]['aov_cents'],10000)
        self.assertEqual(daily[0]['order_conversion_rate'],1.0) # 1 buying session / 1, not 2 orders / 1.
        self.assertIsNone(daily[3]['order_conversion_rate'])
        self.assertEqual(daily[3]['sessions'],0)

    def test_ordered_funnel_and_skipped_steps(self):
        f=query(self.db,'funnel')[0]
        self.assertEqual((f['sessions'],f['product_views'],f['carts'],f['checkouts'],f['purchases']), (5,4,3,2,2))
        self.assertEqual(f['skipped_or_out_of_order_sessions'],2)
        self.assertEqual({r['session_id'] for r in query(self.db,'funnel_exceptions')},{'fixture_s3','fixture_s5'})
        self.assertEqual(f['view_to_cart_rate'],.75)
        self.assertEqual(f['cart_to_checkout_rate'],2/3)
        self.assertEqual(f['checkout_to_purchase_rate'],1)

    def test_repeated_valid_step_after_bad_step(self):
        event=deepcopy(next(e for e in self.tables['events'] if e['session_id']=='fixture_s3' and e['event_name']=='add_to_cart'))
        event.update(event_id='fixture_retry',occurred_at='2026-01-02T12:02:30Z',ingested_at='2026-01-02T12:02:35Z')
        self.tables['events'].append(event)
        other=load_database(self.tables,end='2026-01-06',cutoff='2026-01-20')
        try:
            f=query(other,'funnel')[0]
            self.assertEqual((f['product_views'],f['carts'],f['checkouts'],f['purchases']),(4,4,3,3))
            self.assertEqual(f['skipped_or_out_of_order_sessions'],2) # bad original still reported
        finally: other.close()

    def test_spend_only_conversion_only_and_zero_denominators(self):
        rows={(r['campaign_id'],r['day']):r for r in query(self.db,'campaign_daily')}
        a1=rows['fixture_a','2026-01-01']
        self.assertEqual((a1['spend_cents'],a1['attributed_orders'],a1['first_observed_purchasers']), (1000,2,1))
        self.assertEqual((a1['net_roas'],a1['observed_paid_cac_cents']),(18,1000))
        self.assertEqual(rows['fixture_a','2026-01-02']['coverage'],'spend_only')
        self.assertIsNone(rows['fixture_a','2026-01-02']['observed_paid_cac_cents'])
        self.assertEqual(rows['fixture_a','2026-01-03']['roas_null_reason'],'zero_spend')
        b2=rows['fixture_b','2026-01-02']
        self.assertEqual((b2['coverage'],b2['net_revenue_cents']),('missing_spend',8000))
        self.assertIsNone(b2['spend_cents'])
        self.assertIsNone(b2['net_roas'])
        self.assertIsNone(b2['observed_paid_cac_cents'])
        self.assertIsNone(next(r for r in query(self.db,'campaign_summary') if r['campaign_id']=='fixture_b')['net_roas'])
        self.assertEqual(sum(r['spend_cents'] or 0 for r in rows.values()),3500)
        unpaid=query(self.db,'unattributed')
        self.assertEqual(sum(r['net_revenue_cents'] for r in unpaid),6500)

    def test_first_observed_purchase_is_not_first_visit_or_order_count(self):
        visits={r['visit_type']:r for r in query(self.db,'visitors')}
        self.assertEqual((visits['first_observed_visit']['sessions'],visits['returning_visit']['sessions']),(3,2))
        self.assertEqual((visits['first_observed_visit']['first_observed_purchasers'],visits['returning_visit']['first_observed_purchasers']),(2,0))
        self.assertEqual(summary(self.db)['first_observed_purchasers'],2)
        # Change cohort to day 2: c1's repeat purchase does not become a new acquisition.
        self.db.execute("UPDATE parameters SET start_at='2026-01-02T00:00:00Z'")
        self.assertEqual(summary(self.db)['first_observed_purchasers'],1)

    def test_original_quality_fixtures_through_sql(self):
        with tempfile.TemporaryDirectory() as output:
            rows=fixture_demo(output)
        statuses={r['event_id']:r for r in rows}
        self.assertEqual(statuses['fixture_dup_a']['reason'],'accepted')
        self.assertEqual(statuses['fixture_dup_b']['reason'],'duplicate_purchase')
        self.assertEqual(statuses['fixture_missing']['reason'],'missing_transaction_id')
        self.assertEqual(statuses['fixture_late']['disposition'],'included_late_restatement')

    def test_late_reprocessing_preserves_raw_and_does_not_double_count(self):
        before=[tuple(r) for r in self.db.execute('SELECT * FROM events ORDER BY event_id')]
        self.db.execute("UPDATE parameters SET cutoff='2026-01-03T00:00:00Z'")
        self.assertEqual(query(self.db,'funnel')[0]['purchases'],1)
        self.assertEqual(summary(self.db)['orders'],4) # ledger remains independent of event delivery
        self.assertEqual(summary(self.db)['refunds_cents'],1500)
        self.assertGreater(summary(self.db)['refund_immature_sessions'],0)
        self.assertEqual(query(self.db,'daily')[2]['observation_status'],'not_yet_observed')
        self.db.execute("UPDATE parameters SET cutoff='2026-01-20T00:00:00Z'")
        first=query(self.db,'funnel'); second=query(self.db,'funnel')
        self.assertEqual(first,second)
        self.assertEqual(first[0]['purchases'],2)
        self.assertEqual(summary(self.db)['refunds_cents'],2500)
        self.assertEqual(before,[tuple(r) for r in self.db.execute('SELECT * FROM events ORDER BY event_id')])

    def test_missing_and_duplicate_purchase_do_not_change_ledger(self):
        self.db.execute("UPDATE events SET transaction_id=NULL WHERE transaction_id='fixture_tx'")
        self.assertEqual(summary(self.db)['net_revenue_cents'],32500)
        rows=query(self.db,'reconciliation')
        self.assertEqual(next(r for r in rows if r['record_id']=='fixture_o1')['status'],'order_without_accepted_purchase_event')
        self.assertEqual(next(r for r in rows if r['record_type']=='purchase_event')['status'],'missing_transaction_id')
        self.assertEqual(summary(self.db)['converting_sessions'],3)
        # Append a second delivery of another purchase, preserving both raw IDs.
        event=next(e for e in self.tables['events'] if e['transaction_id']=='fixture_tx2').copy()
        event['event_id']='fixture_duplicate'
        event['ingested_at']='2026-01-01T12:05:06Z'
        columns=list(event)
        self.db.execute(f'INSERT INTO events ({",".join(columns)}) VALUES ({",".join("?" for _ in columns)})', list(event.values()))
        self.assertEqual(sum(r['reason']=='duplicate_purchase' for r in query(self.db,'quality')),1)
        self.assertEqual(summary(self.db)['orders'],4)

    def test_no_cross_session_funnel_stitching(self):
        self.db.execute("DELETE FROM events WHERE session_id='fixture_s2' AND event_name='view_item'")
        # Prior session product views belonging to the same visitor cannot fill this missing step.
        self.assertEqual(query(self.db,'funnel')[0]['purchases'],1)

    def test_invalid_early_event_does_not_suppress_valid_match(self):
        event=deepcopy(next(e for e in self.tables['events'] if e['transaction_id']=='fixture_tx'))
        event.update(event_id='fixture_bad_early',session_id='fixture_s2',ingested_at='2026-01-01T12:04:01Z')
        self.tables['events'].append(event)
        other=load_database(self.tables,end='2026-01-06',cutoff='2026-01-20')
        try:
            rows={r['event_id']:r for r in query(other,'quality')}
            self.assertEqual(rows['fixture_bad_early']['disposition'],'quarantined')
            self.assertEqual(next(r for r in query(other,'reconciliation') if r['record_id']=='fixture_o1')['status'],'matched')
            self.assertEqual(query(other,'funnel')[0]['purchases'],2)
        finally: other.close()

    def test_constraints_and_invalid_financial_inputs(self):
        for table,field,value in [('order_items','order_id','unknown'),('orders','total_paid_cents',1),('refunds','merchandise_refund_cents',999999),('ad_spend_daily','spend_cents',-1)]:
            broken=deepcopy(self.tables); broken[table][0][field]=value
            with self.subTest(table=table), self.assertRaises((sqlite3.IntegrityError,ValueError)):
                load_database(broken,end='2026-01-06',cutoff='2026-01-20')
        broken=deepcopy(self.tables); broken['sessions'].append(broken['sessions'][0])
        with self.assertRaises(sqlite3.IntegrityError): load_database(broken)

    def test_source_control_totals(self):
        outputs={name:query(self.db,name) for name in QUERIES}
        controls=reconciliation_controls(self.db,self.tables,outputs)
        self.assertTrue(all(r['difference']==0 for r in controls.values()))
        outputs['daily'][0]['net_revenue_cents']+=1
        with self.assertRaises(ValueError): reconciliation_controls(self.db,self.tables,outputs)

    def test_idempotent_reload_and_no_raw_mutation(self):
        original=deepcopy(self.tables)
        other=load_database(self.tables,end='2026-01-06',cutoff='2026-01-20')
        try:
            for name in QUERIES: self.assertEqual(query(self.db,name),query(other,name))
        finally: other.close()
        self.assertEqual(original,self.tables)

    def test_partial_observation_excludes_unfinished_session(self):
        self.db.execute("UPDATE parameters SET cutoff='2026-01-01T12:05:00Z'")
        self.assertEqual(summary(self.db)['sessions'],0)
        self.assertEqual(summary(self.db)['orders'],0)
        self.assertEqual(query(self.db,'daily')[0]['orders'],0)

    def test_complete_export_rerun_and_input_fingerprint_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline=Path(directory)/'baseline'; output=Path(directory)/'analysis'
            write_dataset(baseline,sessions=137)
            original={p.name:p.read_bytes() for p in baseline.iterdir()}
            first=run_analysis(baseline,output)
            exported={p.name:p.read_bytes() for p in output.iterdir() if p.suffix!='.sqlite'}
            second=run_analysis(baseline,output)
            self.assertEqual(first,second)
            self.assertEqual(exported,{p.name:p.read_bytes() for p in output.iterdir() if p.suffix!='.sqlite'})
            self.assertEqual(original,{p.name:p.read_bytes() for p in baseline.iterdir()})
            with closing(sqlite3.connect(output/'analysis.sqlite')) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0],137)
            (baseline/'sessions.json').write_text('[]')
            with self.assertRaisesRegex(ValueError,'fingerprint mismatch'):
                run_analysis(baseline,output)
            self.assertEqual(exported,{p.name:p.read_bytes() for p in output.iterdir() if p.suffix!='.sqlite'})


if __name__=='__main__': unittest.main()
