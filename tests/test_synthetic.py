"""Contract and corruption tests, using only unittest and synthetic input."""
from collections import Counter
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ecommerce_growth.synthetic import generate, validate, write_dataset, detect_event_issues, parse, timestamp


class SyntheticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = generate()

    def test_baseline_contract(self):
        validate(self.data)

    def test_documented_default_counts_and_illustration(self):
        expected = {'campaigns': 4, 'customers': 1496, 'sessions': 2700,
                    'events': 7170, 'orders': 377, 'order_items': 377,
                    'refunds': 79, 'ad_spend_daily': 360}
        self.assertEqual({k: len(v) for k, v in self.data.items()}, expected)
        example = json.loads((ROOT / 'data/sample/illustrative_journey.json').read_text())
        validate(example)
        for table in expected:
            self.assertTrue(example[table])
            for row in example[table]:
                self.assertIn(row, self.data[table])

    def test_byte_deterministic_regeneration_and_hashes(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            manifest = write_dataset(a)
            write_dataset(b)
            for path in Path(a).glob('*.json'):
                self.assertEqual(path.read_bytes(), (Path(b) / path.name).read_bytes())
                if path.stem != 'manifest':
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest['sha256'][path.stem])

    def test_seed_and_configurable_size(self):
        self.assertNotEqual(generate(seed=43), self.data)
        for size in (1, 137, 900):
            data = generate(seed=7, sessions=size, start='2025-12-01')
            self.assertEqual(len(data['sessions']), size)
            self.assertEqual(len(data['ad_spend_daily']), 360)
            validate(data)
        with self.assertRaises(ValueError):
            generate(sessions=0)

    def test_default_coverage(self):
        sessions = self.data['sessions']
        self.assertEqual(len({s['started_at'][:10] for s in sessions}), 90)
        self.assertEqual({s['device'] for s in sessions}, {'mobile', 'desktop'})
        self.assertEqual({s['channel'] for s in sessions}, {'google', 'meta', 'organic', 'direct'})
        self.assertLess(len(self.data['customers']), len(sessions))
        self.assertGreater(max(Counter(o['customer_id'] for o in self.data['orders']).values()), 1)
        counts = Counter(e['session_id'] for e in self.data['events'])
        self.assertEqual(set(counts.values()), {1, 2, 3, 4, 5})
        self.assertTrue(self.data['refunds'])

    def test_duplicate_keys_rejected_for_every_table(self):
        for name in self.data:
            with self.subTest(table=name):
                broken = deepcopy(self.data)
                broken[name].append(deepcopy(broken[name][0]))
                with self.assertRaisesRegex(ValueError, 'duplicate key'):
                    validate(broken)

    def test_broken_foreign_keys_rejected(self):
        for table, field in (('sessions', 'customer_id'), ('events', 'session_id'),
                             ('orders', 'session_id'), ('order_items', 'order_id'),
                             ('refunds', 'order_item_id'), ('ad_spend_daily', 'campaign_id')):
            with self.subTest(table=table):
                broken = deepcopy(self.data)
                broken[table][0][field] = 'nonexistent'
                with self.assertRaises(ValueError):
                    validate(broken)
        broken = deepcopy(self.data)
        next(s for s in broken['sessions'] if s['campaign_id'])['campaign_id'] = 'nonexistent'
        with self.assertRaises(ValueError):
            validate(broken)

    def test_ordering_and_ingestion_rejected(self):
        broken = deepcopy(self.data)
        event = next(e for e in broken['events'] if e['event_name'] == 'add_to_cart')
        event['occurred_at'] = timestamp(parse(event['occurred_at']) - timedelta(seconds=90))
        with self.assertRaisesRegex(ValueError, 'funnel ordering'):
            validate(broken)
        broken = deepcopy(self.data)
        broken['events'][0]['ingested_at'] = '2025-01-01T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'ingestion before'):
            validate(broken)

    def test_independent_money_reconciliation(self):
        # Recalculate from unit prices/quantities rather than trusting stored totals.
        items = self.data['order_items']
        net = sum(i['quantity'] * i['unit_price_cents'] - i['discount_cents'] for i in items)
        paid_less_charges = sum(o['total_paid_cents'] - o['tax_cents'] - o['shipping_cents'] for o in self.data['orders'])
        self.assertEqual(net, paid_less_charges)
        self.assertEqual(net, 34500720)  # Reviewed fixed-seed control, cents, not a business result.
        for table, field in (('orders', 'total_paid_cents'), ('orders', 'gross_merchandise_cents'),
                             ('orders', 'discount_cents'), ('order_items', 'net_merchandise_cents')):
            broken = deepcopy(self.data)
            broken[table][0][field] += 1
            with self.assertRaises(ValueError):
                validate(broken)

    def test_aggregate_refund_limits(self):
        broken = deepcopy(self.data)
        refund = broken['refunds'][0]
        item = next(i for i in broken['order_items'] if i['order_item_id'] == refund['order_item_id'])
        refund['merchandise_refund_cents'] = item['net_merchandise_cents'] // 2 + 1
        another = deepcopy(refund)
        another['refund_id'] = 'syn_extra_refund'
        broken['refunds'].append(another)
        with self.assertRaisesRegex(ValueError, 'refund merchandise limit'):
            validate(broken)
        broken = deepcopy(self.data)
        broken['refunds'][0]['tax_refund_cents'] = 999999999
        with self.assertRaisesRegex(ValueError, 'refund charge limit'):
            validate(broken)

    def test_transaction_link_and_deduplication(self):
        for replacement in (None, 'unknown_transaction'):
            broken = deepcopy(self.data)
            next(e for e in broken['events'] if e['event_name'] == 'purchase')['transaction_id'] = replacement
            with self.assertRaises(ValueError):
                validate(broken)
        events = deepcopy(self.data['events'])
        extra = deepcopy(next(e for e in events if e['event_name'] == 'purchase'))
        extra['event_id'] = 'syn_duplicate_delivery'
        extra['ingested_at'] = timestamp(parse(extra['ingested_at']) + timedelta(seconds=1))
        events.append(extra)
        self.assertEqual(detect_event_issues(events)['duplicate_purchase'], ['syn_duplicate_delivery'])

    def test_fixture_detection_exact_and_nonmutating(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/event_quality.json').read_text())
        for case in fixtures['cases']:
            with self.subTest(case=case['name']):
                original = deepcopy(case['events'])
                self.assertEqual(detect_event_issues(case['events']), case['expected'])
                self.assertEqual(case['events'], original)
        self.assertFalse(any(detect_event_issues(self.data['events']).values()))

    def test_late_arrival_boundary_and_occurrence_date(self):
        event = deepcopy(self.data['events'][0])
        event['ingested_at'] = timestamp(parse(event['occurred_at']) + timedelta(hours=24))
        self.assertEqual(detect_event_issues([event])['late_arrival'], [])
        event['ingested_at'] = timestamp(parse(event['ingested_at']) + timedelta(seconds=1))
        self.assertEqual(detect_event_issues([event])['late_arrival'], [event['event_id']])
        self.assertEqual(event['occurred_at'], self.data['events'][0]['occurred_at'])

    def test_campaign_day_spend_not_event_grain(self):
        spend = self.data['ad_spend_daily']
        self.assertEqual(len(spend), 4 * 90)
        self.assertEqual(sum(r['spend_cents'] for r in spend), 4425988)
        self.assertTrue(all('spend_cents' not in row for row in self.data['events'] + self.data['sessions']))
        # Aggregate traffic first, then make a one-row-per-campaign-day comparison.
        traffic = Counter((s['campaign_id'], s['started_at'][:10]) for s in self.data['sessions'] if s['campaign_id'])
        comparison = [{**r, 'sessions': traffic[(r['campaign_id'], r['spend_date'])]} for r in spend]
        self.assertEqual(sum(r['spend_cents'] for r in comparison), 4425988)
        self.assertEqual(sum(r['sessions'] for r in comparison), sum(s['campaign_id'] is not None for s in self.data['sessions']))


if __name__ == '__main__':
    unittest.main()
