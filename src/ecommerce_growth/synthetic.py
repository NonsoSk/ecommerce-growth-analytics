"""Deterministic fictional data; standard library only, no external connections."""

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import random

TABLE_KEYS = {
    'campaigns': 'campaign_id', 'customers': 'customer_id', 'sessions': 'session_id',
    'events': 'event_id', 'orders': 'order_id', 'order_items': 'order_item_id',
    'refunds': 'refund_id', 'ad_spend_daily': ('campaign_id', 'spend_date'),
}
STEPS = ('session_start', 'view_item', 'add_to_cart', 'begin_checkout', 'purchase')


def timestamp(value):
    return value.isoformat().replace('+00:00', 'Z')


def parse(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def serialize(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'


def generate(seed=42, sessions=2700, start='2026-01-01'):
    """Return eight linked tables spanning 90 UTC session-start dates."""
    if sessions < 1:
        raise ValueError('sessions must be positive')
    first = datetime.combine(date.fromisoformat(start), datetime.min.time(), timezone.utc)
    rng = random.Random(seed)
    tables = {name: [] for name in TABLE_KEYS}
    for channel in ('google', 'meta'):
        for audience in ('prospecting', 'retargeting'):
            tables['campaigns'].append({
                'campaign_id': f'syn_{channel}_{audience}', 'channel': channel,
                'audience': audience, 'currency': 'USD',
            })
    for day in range(90):
        for campaign in tables['campaigns']:
            tables['ad_spend_daily'].append({
                'campaign_id': campaign['campaign_id'],
                'spend_date': (first + timedelta(days=day)).date().isoformat(),
                'spend_cents': rng.randint(5000, 20000), 'currency': 'USD',
            })
    customer_ids = []
    for i in range(sessions):
        started = first + timedelta(days=i * 90 // sessions, seconds=rng.randint(0, 85000))
        # Process sessions chronologically below so first_seen and repeat identity are consistent.
        tables['sessions'].append({'session_id': f'syn_s{i + 1:06d}', 'started_at': timestamp(started)})
    tables['sessions'].sort(key=lambda row: (row['started_at'], row['session_id']))
    for session in tables['sessions']:
        started = parse(session['started_at'])
        if not customer_ids or rng.random() < .55:
            customer_id = f'syn_c{len(customer_ids) + 1:06d}'
            customer_ids.append(customer_id)
            tables['customers'].append({'customer_id': customer_id, 'first_seen_at': timestamp(started)})
        else:
            customer_id = rng.choice(customer_ids)
        channel = rng.choices(('google', 'meta', 'organic', 'direct'), (.30, .25, .25, .20))[0]
        campaign_id = rng.choice([c['campaign_id'] for c in tables['campaigns'] if c['channel'] == channel]) if channel in ('google', 'meta') else None
        device = rng.choices(('mobile', 'desktop'), (.68, .32))[0]
        session.update(customer_id=customer_id, channel=channel, campaign_id=campaign_id, device=device)
        # Illustrative knobs only; they are not estimates of real customer behavior.
        reach = 1
        probabilities = (.88, .40 if device == 'mobile' else .52, .65, .50 if device == 'mobile' else .65)
        for probability in probabilities:
            if rng.random() >= probability:
                break
            reach += 1
        transaction_id = None
        if reach == 5:
            number = len(tables['orders']) + 1
            order_id, transaction_id = f'syn_o{number:06d}', f'syn_tx{number:06d}'
            ordered = started + timedelta(minutes=4)
            price = rng.choice((59900, 89900, 119900))
            quantity = rng.choices((1, 2), (.95, .05))[0]
            gross = price * quantity
            discount = gross // 10 if rng.random() < .25 else 0
            net = gross - discount
            tax = net * 8 // 100
            tables['orders'].append({
                'order_id': order_id, 'transaction_id': transaction_id,
                'customer_id': customer_id, 'session_id': session['session_id'],
                'ordered_at': timestamp(ordered), 'currency': 'USD', 'status': 'paid',
                'gross_merchandise_cents': gross, 'discount_cents': discount,
                'tax_cents': tax, 'shipping_cents': 0, 'total_paid_cents': net + tax,
            })
            item_id = f'syn_i{number:06d}'
            tables['order_items'].append({
                'order_item_id': item_id, 'order_id': order_id, 'product_id': f'syn_mattress_{price}',
                'quantity': quantity, 'unit_price_cents': price, 'discount_cents': discount,
                'net_merchandise_cents': net, 'currency': 'USD',
            })
            if rng.random() < .18:
                amount = net * rng.choice((10, 20, 30)) // 100
                refunded = ordered + timedelta(days=rng.randint(1, 14))
                tables['refunds'].append({
                    'refund_id': f'syn_r{len(tables["refunds"]) + 1:06d}',
                    'order_id': order_id, 'order_item_id': item_id,
                    'refunded_at': timestamp(refunded),
                    'ingested_at': timestamp(refunded + timedelta(minutes=5)),
                    'merchandise_refund_cents': amount, 'tax_refund_cents': amount * 8 // 100,
                    'shipping_refund_cents': 0, 'currency': 'USD',
                })
        for step in range(reach):
            occurred = started + timedelta(minutes=step)
            tables['events'].append({
                'event_id': f'syn_e{len(tables["events"]) + 1:07d}',
                'session_id': session['session_id'], 'event_name': STEPS[step],
                'occurred_at': timestamp(occurred),
                'ingested_at': timestamp(occurred + timedelta(seconds=5)),
                'transaction_id': transaction_id if step == 4 else None,
            })
        session['ended_at'] = timestamp(started + timedelta(minutes=reach))
    return tables


def detect_event_issues(events, late_hours=24):
    """Return raw event IDs requiring review; never mutate or silently repair input."""
    issues = {'duplicate_purchase': [], 'missing_transaction_id': [], 'late_arrival': []}
    seen = set()
    for event in sorted(events, key=lambda e: (e['ingested_at'], e['event_id'])):
        if parse(event['ingested_at']) - parse(event['occurred_at']) > timedelta(hours=late_hours):
            issues['late_arrival'].append(event['event_id'])
        if event['event_name'] != 'purchase':
            continue
        transaction = event['transaction_id']
        if not transaction:
            issues['missing_transaction_id'].append(event['event_id'])
        elif transaction in seen:
            issues['duplicate_purchase'].append(event['event_id'])
        else:
            seen.add(transaction)
    return issues


def validate(tables):
    """Check the strict baseline contract; raise ValueError on a violated invariant."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    indexes = {}
    for name, key in TABLE_KEYS.items():
        keys = [tuple(r[k] for k in key) if isinstance(key, tuple) else r[key] for r in tables[name]]
        require(len(keys) == len(set(keys)), f'{name}: duplicate key')
        require(all(k is not None and k != '' for k in keys), f'{name}: missing key')
        indexes[name] = dict(zip(keys, tables[name]))
    customers, sessions, orders = (indexes[n] for n in ('customers', 'sessions', 'orders'))
    transactions = {r['transaction_id']: r for r in tables['orders']}
    require(len(transactions) == len(orders) and all(transactions), 'orders: transaction uniqueness')
    for session in sessions.values():
        require(session['customer_id'] in customers, 'session customer FK')
        require(parse(customers[session['customer_id']]['first_seen_at']) <= parse(session['started_at']) < parse(session['ended_at']), 'session time bounds')
        require(session['device'] in ('mobile', 'desktop'), 'device')
        if session['channel'] in ('google', 'meta'):
            campaign = indexes['campaigns'].get(session['campaign_id'])
            require(campaign is not None and campaign['channel'] == session['channel'], 'session campaign FK/channel')
        else:
            require(session['channel'] in ('organic', 'direct') and session['campaign_id'] is None, 'unpaid channel')
    for spend in tables['ad_spend_daily']:
        require(spend['campaign_id'] in indexes['campaigns'], 'spend campaign FK')
        require(spend['currency'] == 'USD' and spend['spend_cents'] >= 0, 'spend amount/currency')
    for session in sessions.values():
        if session['campaign_id']:
            require((session['campaign_id'], session['started_at'][:10]) in indexes['ad_spend_daily'], 'session spend-day coverage')
    event_groups = defaultdict(list)
    purchase_counts = Counter()
    for event in tables['events']:
        require(event['session_id'] in sessions, 'event session FK')
        session = sessions[event['session_id']]
        require(parse(session['started_at']) <= parse(event['occurred_at']) <= parse(session['ended_at']), 'event session bounds')
        require(parse(event['ingested_at']) >= parse(event['occurred_at']), 'event ingestion before occurrence')
        event_groups[event['session_id']].append(event)
        if event['event_name'] == 'purchase':
            order = transactions.get(event['transaction_id'])
            require(order is not None and order['session_id'] == event['session_id'], 'purchase transaction FK')
            require(event['occurred_at'] == order['ordered_at'], 'purchase order timestamp')
            purchase_counts[event['transaction_id']] += 1
        else:
            require(event['transaction_id'] is None, 'nonpurchase transaction')
    for session_id in sessions:
        events = sorted(event_groups[session_id], key=lambda e: e['occurred_at'])
        require(bool(events) and [e['event_name'] for e in events] == list(STEPS[:len(events)]), 'event funnel ordering')
        require(all(parse(a['occurred_at']) < parse(b['occurred_at']) for a, b in zip(events, events[1:])), 'event strict ordering')
    require(all(purchase_counts[t] == 1 for t in transactions), 'one purchase per order')
    require(not any(detect_event_issues(tables['events']).values()), 'baseline event quality')
    item_groups = defaultdict(list)
    for item in tables['order_items']:
        require(item['order_id'] in orders, 'item order FK')
        gross = item['quantity'] * item['unit_price_cents']
        require(item['quantity'] > 0 and item['unit_price_cents'] > 0 and 0 <= item['discount_cents'] <= gross, 'item amount bounds')
        require(item['net_merchandise_cents'] == gross - item['discount_cents'], 'item net reconciliation')
        require(item['currency'] == 'USD', 'item currency')
        item_groups[item['order_id']].append(item)
    for order in orders.values():
        session = sessions.get(order['session_id'])
        require(session is not None and order['customer_id'] == session['customer_id'], 'order session/customer FK')
        require(order['status'] == 'paid' and order['currency'] == 'USD', 'order status/currency')
        items = item_groups[order['order_id']]
        require(bool(items), 'order has items')
        require(order['gross_merchandise_cents'] == sum(i['quantity'] * i['unit_price_cents'] for i in items), 'order gross reconciliation')
        require(order['discount_cents'] == sum(i['discount_cents'] for i in items), 'order discount reconciliation')
        require(order['tax_cents'] >= 0 and order['shipping_cents'] >= 0, 'order charges')
        require(order['total_paid_cents'] == sum(i['net_merchandise_cents'] for i in items) + order['tax_cents'] + order['shipping_cents'], 'order total reconciliation')
    refunded_by_item = Counter()
    refunded_tax, refunded_shipping = Counter(), Counter()
    for refund in tables['refunds']:
        item = indexes['order_items'].get(refund['order_item_id'])
        require(item is not None and item['order_id'] == refund['order_id'], 'refund item/order FK')
        order = orders[refund['order_id']]
        require(parse(order['ordered_at']) <= parse(refund['refunded_at']) <= parse(refund['ingested_at']), 'refund time bounds')
        require(refund['currency'] == 'USD' and refund['merchandise_refund_cents'] > 0 and refund['tax_refund_cents'] >= 0 and refund['shipping_refund_cents'] >= 0, 'refund amount/currency')
        refunded_by_item[refund['order_item_id']] += refund['merchandise_refund_cents']
        refunded_tax[refund['order_id']] += refund['tax_refund_cents']
        refunded_shipping[refund['order_id']] += refund['shipping_refund_cents']
    for item_id, amount in refunded_by_item.items():
        require(amount <= indexes['order_items'][item_id]['net_merchandise_cents'], 'refund merchandise limit')
    for order_id in orders:
        require(refunded_tax[order_id] <= orders[order_id]['tax_cents'] and refunded_shipping[order_id] <= orders[order_id]['shipping_cents'], 'refund charge limit')


def write_dataset(output, seed=42, sessions=2700, start='2026-01-01'):
    tables = generate(seed, sessions, start)
    validate(tables)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        'label': 'SYNTHETIC ONLY — not evidence about Puffy or real customers',
        'generator_version': 1, 'seed': seed, 'sessions': sessions, 'start_date': start,
        'end_date_exclusive': (date.fromisoformat(start) + timedelta(days=90)).isoformat(),
        'observation_cutoff_exclusive': (date.fromisoformat(start) + timedelta(days=105)).isoformat(),
        'currency': 'USD', 'timezone': 'UTC', 'row_counts': {}, 'sha256': {},
    }
    for name, rows in tables.items():
        content = serialize(rows).encode()
        (output / f'{name}.json').write_bytes(content)
        manifest['row_counts'][name] = len(rows)
        manifest['sha256'][name] = hashlib.sha256(content).hexdigest()
    manifest['control_totals_cents'] = {
        'spend': sum(r['spend_cents'] for r in tables['ad_spend_daily']),
        'gross_merchandise': sum(r['gross_merchandise_cents'] for r in tables['orders']),
        'discounts': sum(r['discount_cents'] for r in tables['orders']),
        'total_paid': sum(r['total_paid_cents'] for r in tables['orders']),
        'merchandise_refunds': sum(r['merchandise_refund_cents'] for r in tables['refunds']),
    }
    (output / 'manifest.json').write_text(serialize(manifest))
    return manifest
