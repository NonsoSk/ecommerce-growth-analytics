"""Local SQLite analysis. Raw inputs remain unchanged; no external service calls."""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3

from ecommerce_growth.synthetic import TABLE_KEYS, parse, serialize

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / 'sql/analysis'
QUERIES = ('daily', 'funnel', 'funnel_segments', 'funnel_exceptions', 'campaign_daily', 'campaign_summary', 'unattributed',
           'reconciliation', 'visitors', 'quality')
LOAD_ORDER = ('campaigns', 'customers', 'sessions', 'orders', 'order_items', 'refunds', 'ad_spend_daily', 'events')


def query(db, name):
    return [dict(row) for row in db.execute((SQL / f'{name}.sql').read_text())]


def load_database(tables, start='2026-01-01', end='2026-04-01', cutoff='2026-04-16', destination=':memory:'):
    """Create a fresh database, never append. Caller uses a fresh temporary destination."""
    if destination != ':memory:' and Path(destination).exists():
        raise ValueError('Load requires a fresh destination; replace only after validation')
    if not start < end or cutoff <= start:
        raise ValueError('Require start < end and cutoff > start')
    db = sqlite3.connect(destination)
    db.row_factory = sqlite3.Row
    try:
        db.executescript((SQL / '00_schema.sql').read_text())
        with db:
            db.execute('INSERT INTO parameters VALUES (1,?,?,?)', tuple(v+'T00:00:00Z' for v in (start,end,cutoff)))
            for name in LOAD_ORDER:
                columns = [r['name'] for r in db.execute(f'PRAGMA table_info({name})')]
                for row in tables[name]:
                    if set(row) != set(columns):
                        raise ValueError(f'{name}: unexpected columns')
                    for key, value in row.items():
                        if key.endswith('_at'):
                            if parse(value).utcoffset().total_seconds() != 0 or not value.endswith('Z'):
                                raise ValueError('Expected UTC timestamp with Z')
                    db.execute(f'INSERT INTO {name} ({",".join(columns)}) VALUES ({",".join("?" for _ in columns)})', [row[c] for c in columns])
        checks = {
            'order_item_reconciliation': '''SELECT COUNT(*) FROM orders o LEFT JOIN
                (SELECT order_id,SUM(quantity*unit_price_cents) g,SUM(discount_cents) d FROM order_items GROUP BY order_id) i USING(order_id)
                WHERE i.g IS NULL OR o.gross_merchandise_cents<>i.g OR o.discount_cents<>i.d''',
            'refund_merchandise_limits': '''SELECT COUNT(*) FROM
                (SELECT order_item_id,SUM(merchandise_refund_cents) r FROM refunds GROUP BY order_item_id) r
                JOIN order_items i USING(order_item_id) WHERE r.r>i.net_merchandise_cents''',
            'refund_charge_limits': '''SELECT COUNT(*) FROM
                (SELECT order_id,SUM(tax_refund_cents) t,SUM(shipping_refund_cents) s FROM refunds GROUP BY order_id) r
                JOIN orders o USING(order_id) WHERE r.t>o.tax_cents OR r.s>o.shipping_cents''',
            'refund_time': '''SELECT COUNT(*) FROM refunds r JOIN orders o USING(order_id) WHERE r.refunded_at<o.ordered_at''',
            'order_time': '''SELECT COUNT(*) FROM orders o JOIN sessions s USING(session_id) WHERE o.ordered_at<s.started_at OR o.ordered_at>s.ended_at''',
            'campaign_channel': '''SELECT COUNT(*) FROM sessions s JOIN campaigns c USING(campaign_id) WHERE s.channel<>c.channel''',
            'visitor_time': '''SELECT COUNT(*) FROM sessions s JOIN customers c USING(customer_id) WHERE s.started_at<c.first_seen_at''',
        }
        for label, sql in checks.items():
            if db.execute(sql).fetchone()[0]:
                raise ValueError(label)
        db.executescript((SQL / '01_models.sql').read_text())
        db.executescript('CREATE VIEW campaign_per_day AS\n' + (SQL / 'campaign_daily.sql').read_text())
        return db
    except Exception:
        db.close()
        raise


def fingerprint(tables):
    return hashlib.sha256(serialize({k:tables[k] for k in sorted(TABLE_KEYS)}).encode()).hexdigest()


def export_query(db, name, directory):
    cursor = db.execute((SQL / f'{name}.sql').read_text())
    rows = [dict(row) for row in cursor]
    with (Path(directory) / f'{name}.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=[c[0] for c in cursor.description])
        writer.writeheader()
        writer.writerows(rows)  # None -> blank; semantics documented in SQL_PIPELINE.md.
    return rows


def summary(db):
    return dict(db.execute('''SELECT COUNT(*) sessions,COUNT(DISTINCT customer_id) visitors,
        COUNT(DISTINCT CASE WHEN orders>0 THEN customer_id END) purchasing_visitors,
        COALESCE(SUM(converting_session),0) converting_sessions, COALESCE(SUM(orders),0) orders,
        COALESCE(SUM(merchandise_cents),0) merchandise_cents,COALESCE(SUM(refunds_cents),0) refunds_cents,
        COALESCE(SUM(net_revenue_cents),0) net_revenue_cents,COALESCE(SUM(first_observed_purchasers),0) first_observed_purchasers,
        COALESCE(SUM(1-refund_window_mature),0) refund_immature_sessions FROM session_finance''').fetchone())


def reconciliation_controls(db, tables, outputs):
    start,end,cutoff = db.execute('SELECT start_at,end_at,cutoff FROM parameters').fetchone()
    session_ids = {s['session_id'] for s in tables['sessions'] if start<=s['started_at']<end and s['ended_at']<cutoff}
    order_ids = {o['order_id'] for o in tables['orders'] if o['session_id'] in session_ids and o['ordered_at']<cutoff}
    # Independent source arithmetic; SQL aggregates are not fed back as expected values.
    merchandise = sum(i['quantity']*i['unit_price_cents']-i['discount_cents'] for i in tables['order_items'] if i['order_id'] in order_ids)
    refunds = sum(r['merchandise_refund_cents'] for r in tables['refunds'] if r['order_id'] in order_ids and r['refunded_at']<cutoff and r['ingested_at']<cutoff)
    spend = sum(s['spend_cents'] for s in tables['ad_spend_daily'] if start[:10]<=s['spend_date']<end[:10] and s['spend_date']<cutoff[:10])
    pairs = {
        'sessions': (len(session_ids),sum(r['sessions'] for r in outputs['daily'])),
        'orders': (len(order_ids),sum(r['orders'] for r in outputs['daily'])),
        'merchandise_cents': (merchandise,sum(r['merchandise_cents'] for r in outputs['daily'])),
        'refunds_cents': (refunds,sum(r['refunds_cents'] for r in outputs['daily'])),
        'net_revenue_cents': (merchandise-refunds,sum(r['net_revenue_cents'] for r in outputs['daily'])),
        'spend_cents': (spend,sum(r['spend_cents'] or 0 for r in outputs['campaign_daily'])),
        'paid_plus_unpaid_net_cents': (merchandise-refunds,sum(r['net_revenue_cents'] for r in outputs['campaign_daily']+outputs['unattributed'])),
    }
    result = {key:{'source':a,'sql':b,'difference':b-a} for key,(a,b) in pairs.items()}
    if any(r['difference'] for r in result.values()):
        raise ValueError(f'Reconciliation failed: {result}')
    return result


def fixture_demo(output):
    """Exercise existing event fixtures in isolated databases, retaining original rows."""
    context = json.loads((ROOT/'tests/fixtures/sql_hand_calculated.json').read_text())['tables']
    cases = json.loads((ROOT/'tests/fixtures/event_quality.json').read_text())['cases']
    rows=[]
    for case in cases:
        tables = {**context, 'events': case['events']}
        with load_database(tables,end='2026-01-06',cutoff='2026-01-20') as db:
            for row in query(db,'quality'):
                rows.append({'case':case['name'],**row})
        db.close()
    with (Path(output)/'fixture_quality.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return rows


def run_analysis(baseline, output, cutoff=None, test_results=None):
    """Verify input hashes, build fresh outputs, then replace prior generated artifacts."""
    import sys
    import tempfile
    from datetime import date
    from ecommerce_growth.analysis_report import render
    baseline,output=Path(baseline),Path(output)
    manifest=json.loads((baseline/'manifest.json').read_text())
    tables={}
    for name in TABLE_KEYS:
        blob=(baseline/f'{name}.json').read_bytes()
        if hashlib.sha256(blob).hexdigest()!=manifest['sha256'][name]:
            raise ValueError(f'Input fingerprint mismatch: {name}')
        tables[name]=json.loads(blob)
        if len(tables[name])!=manifest['row_counts'][name]:
            raise ValueError(f'Input row count mismatch: {name}')
    cutoff=cutoff or manifest['observation_cutoff_exclusive']
    for value in (manifest['start_date'],manifest['end_date_exclusive'],cutoff):
        if date.fromisoformat(value).isoformat()!=value:
            raise ValueError('Date must be YYYY-MM-DD; cutoff is exclusive UTC midnight')
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='analysis-',dir=output.parent) as temporary:
        directory=Path(temporary)
        db=load_database(tables,manifest['start_date'],manifest['end_date_exclusive'],cutoff,str(directory/'analysis.sqlite'))
        try:
            outputs={name:export_query(db,name,directory) for name in QUERIES}
            controls=reconciliation_controls(db,tables,outputs)
            metadata={
                'label':'SYNTHETIC LOCAL SQL ANALYSIS ONLY',
                'seed':manifest['seed'],'configured_sessions':manifest['sessions'],
                'generator_version':manifest['generator_version'],
                'start_date':manifest['start_date'],'end_date_exclusive':manifest['end_date_exclusive'],
                'cutoff':cutoff,'data_fingerprint':fingerprint(tables),
                'input_sha256':manifest['sha256'],'input_row_counts':manifest['row_counts'],
                'sql_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SQL.glob('*.sql'))},
                'python_version':sys.version.split()[0],'sqlite_version':sqlite3.sqlite_version,
                'summary':summary(db),'tests':test_results,
                'excluded_unfinished_or_future_sessions':db.execute('''SELECT COUNT(*) FROM sessions s,parameters p
                    WHERE s.started_at>=p.start_at AND s.started_at<p.end_at AND s.ended_at>=p.cutoff''').fetchone()[0],
            }
            fixtures=fixture_demo(directory)
            (directory/'run_metadata.json').write_text(serialize(metadata))
            (directory/'reconciliation_controls.json').write_text(serialize(controls))
            (directory/'MILESTONE_2_ANALYSIS.md').write_text(render(metadata,outputs,controls,fixtures))
            db.commit()
        finally:
            db.close()
        # No append operations: validated replacements make repeat runs idempotent.
        for path in directory.iterdir():
            path.replace(output/path.name)
    return metadata
