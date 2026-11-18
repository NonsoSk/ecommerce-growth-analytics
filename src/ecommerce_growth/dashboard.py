"""Baseline-only portable dashboard exports. No cloud calls or Tableau claims."""
import csv
import hashlib
import json
from pathlib import Path
from ecommerce_growth.analysis import ROOT, load_database, fingerprint, query
from ecommerce_growth.synthetic import TABLE_KEYS, serialize

FINGERPRINT='e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da'
GRAINS={'overview':('day',),'funnel':('day','device','channel','visit_type'),
        'acquisition':('day','campaign_id')}
FILTERS={'overview':(), 'funnel':('device','channel','visit_type'), 'acquisition':('channel','campaign_id')}
NUMBERS={'overview':('sessions','converting_sessions','orders','net_revenue_cents','refunds_cents','spend_cents','missing_spend_days'),
'funnel':('sessions','session_starts','product_views','carts','checkouts','purchases','skipped_or_out_of_order_sessions'),
'acquisition':('spend_cents','attributed_orders','net_revenue_cents','first_observed_purchasers','missing_spend_days','days_with_spend_zero_orders')}


def ratio(a,b): return a/b if b else None


def totals(rows,name):
    out={k:sum(r[k] for r in rows if r[k] is not None) for k in NUMBERS[name]}
    if not rows: out={k:0 for k in NUMBERS[name]}
    if name=='overview':
        out['conversion_rate']=ratio(out['converting_sessions'],out['sessions'])
    if name=='acquisition':
        out['net_roas']=ratio(out['net_revenue_cents'],out['spend_cents']) if not out['missing_spend_days'] else None
        out['first_observed_paid_cac_proxy_cents']=ratio(out['spend_cents'],out['first_observed_purchasers']) if not out['missing_spend_days'] else None
    if name=='funnel':
        out['ordered_conversion_rate']=ratio(out['purchases'],out['sessions'])
        for a,b in [('session_starts','product_views'),('product_views','carts'),('carts','checkouts'),('checkouts','purchases')]:
            out[a+'_to_'+b+'_rate']=ratio(out[b],out[a])
            out[a+'_to_'+b+'_dropoff']=out[a]-out[b]
    return out


def select(rows,name,start='2026-01-01',end='2026-03-31',**filters):
    if set(filters)-set(FILTERS[name]): raise ValueError('Unsupported filter for this grain')
    return [r for r in rows if start<=r['day']<=end and all(r[k]==v for k,v in filters.items())]


def aggregate(db):
    data={name:[dict(r) for r in db.execute((ROOT/'sql/dashboard'/f'{name}.sql').read_text())] for name in GRAINS}
    for name,rows in data.items():
        keys=[tuple(r[k] for k in GRAINS[name]) for r in rows]
        if len(keys)!=len(set(keys)): raise ValueError('Duplicate aggregate key')
    return data


def verified_baseline(path):
    path=Path(path);manifest=json.loads((path/'manifest.json').read_text());tables={}
    for name in TABLE_KEYS:
        raw=(path/f'{name}.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=manifest['sha256'][name]: raise ValueError('Baseline hash mismatch')
        tables[name]=json.loads(raw)
    if fingerprint(tables)!=FINGERPRINT: raise ValueError('Dashboard requires the validated seed-42 baseline; fixtures/other data refused')
    return manifest,tables


def validate(db,data):
    """Compare export rollups to SQL views at full and representative filtered grains."""
    checks=[]
    cases=[('overview','2026-01-01','2026-03-31',{}),('overview','2026-01-01','2026-01-31',{}),
      ('funnel','2026-01-01','2026-03-31',{}),('funnel','2026-01-01','2026-01-31',{'device':'mobile','channel':'google','visit_type':'returning_visit'}),
      ('funnel','2026-02-01','2026-02-28',{'device':'desktop','channel':'organic'}),
      ('acquisition','2026-01-01','2026-03-31',{}),('acquisition','2026-01-01','2026-01-31',{'campaign_id':'syn_google_prospecting'}),
      ('acquisition','2026-02-01','2026-02-28',{'channel':'meta'})]
    for name,start,end,filters in cases:
        got=totals(select(data[name],name,start,end,**filters),name)
        if name=='overview':
            sql='''SELECT COUNT(*) sessions,COALESCE(SUM(converting_session),0) converting_sessions,
            COALESCE(SUM(orders),0) orders,COALESCE(SUM(net_revenue_cents),0) net_revenue_cents,
            COALESCE(SUM(refunds_cents),0) refunds_cents FROM session_finance WHERE session_date BETWEEN ? AND ?'''
            expected=dict(db.execute(sql,(start,end)).fetchone())
            expected['spend_cents']=db.execute('SELECT COALESCE(SUM(spend_cents),0) FROM ad_spend_daily WHERE spend_date BETWEEN ? AND ?',(start,end)).fetchone()[0]
        elif name=='funnel':
            sql='''WITH ranked AS (SELECT session_id,CASE WHEN ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY started_at,session_id)=1 THEN 'first_observed_visit' ELSE 'returning_visit' END visit_type FROM sessions)
            SELECT COUNT(*) sessions,COUNT(start_time) session_starts,COUNT(view_time) product_views,COUNT(cart_time) carts,COUNT(checkout_time) checkouts,COUNT(purchase_time) purchases,
            COALESCE(SUM(skipped_or_out_of_order_events>0),0) skipped_or_out_of_order_sessions
            FROM funnel_sessions JOIN ranked USING(session_id) WHERE session_date BETWEEN ? AND ?'''
            sql+=''.join(' AND '+k+'=?' for k in filters)
            expected=dict(db.execute(sql,(start,end,*filters.values())).fetchone())
        else:
            # Campaign-day is already validated against source spend and order-ledger finance.
            sql='SELECT '+','.join('COALESCE(SUM('+k+'),0) '+k for k in ('spend_cents','attributed_orders','net_revenue_cents','first_observed_purchasers'))+' FROM campaign_per_day WHERE day BETWEEN ? AND ?'
            sql+=''.join(' AND '+k+'=?' for k in filters)
            expected=dict(db.execute(sql,(start,end,*filters.values())).fetchone())
        if any(got[k]!=v for k,v in expected.items()): raise ValueError('Filtered SQL reconciliation failed')
        checks.append({'dataset':name,'start':start,'end_inclusive':end,'filters':filters,'values':got,'sql_differences':{k:got[k]-v for k,v in expected.items()}})
    # Full row-level parity against the established SQLite outputs, not just totals.
    daily={r['session_date']:r for r in query(db,'daily')}
    for row in data['overview']:
        for k in ('sessions','converting_sessions','orders','net_revenue_cents','refunds_cents'):
            assert row[k]==daily[row['day']][k]
    campaigns={(r['day'],r['campaign_id']):r for r in query(db,'campaign_daily')}
    for row in data['acquisition']:
        for k in ('spend_cents','attributed_orders','net_revenue_cents','first_observed_purchasers'):
            assert row[k]==campaigns[(row['day'],row['campaign_id'])][k]
    return checks


def export(baseline=ROOT/'data/generated/baseline',out=ROOT/'dashboard/data'):
    manifest,tables=verified_baseline(baseline)
    db=load_database(tables,manifest['start_date'],manifest['end_date_exclusive'],manifest['observation_cutoff_exclusive'])
    try:
        data=aggregate(db);checks=validate(db,data)
    finally: db.close()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    files={}
    for name,rows in data.items():
        path=out/f'{name}.csv'
        with path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        files[path.name]={'rows':len(rows),'grain':GRAINS[name],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    evidence={'label':'SYNTHETIC DEMONSTRATION ONLY — BASELINE, NO QUALITY FIXTURES',
      'baseline_fingerprint':FINGERPRINT,'seed':42,'start_date':manifest['start_date'],'end_date_exclusive':manifest['end_date_exclusive'],
      'observation_cutoff_exclusive':manifest['observation_cutoff_exclusive'],'currency':'USD','timezone':'UTC',
      'files':files,'sql_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'sql/dashboard').glob('*.sql'))},
      'filtered_validation':checks,'tableau_workbook_status':'data_export_only_see_PROGRESS_for_UI_acceptance'}
    (out/'manifest.json').write_text(serialize(evidence))
    return data,evidence
