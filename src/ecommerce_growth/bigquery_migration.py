"""Offline-first BigQuery preparation; cloud operations require explicit modes/config.

No credential loading/token printing, dataset creation, billing changes or broad deletes.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

from ecommerce_growth.analysis import ROOT, QUERIES, load_database, query, summary, fingerprint
from ecommerce_growth.synthetic import TABLE_KEYS, serialize

BQ_ROOT=ROOT/'bigquery'
OWNER_KEY='portfolio_project'
OWNER_VALUE='ecommerce_growth_analytics'
GROUPS=('baseline','hand','duplicate_purchase','missing_transaction_id','late_arrival')
BQ_QUERIES=(*QUERIES,'summary','raw_controls')
KEYS={
 'daily':('session_date',),'funnel':(), 'funnel_segments':('dimension','segment'),
 'funnel_exceptions':('session_id',),'campaign_daily':('day','campaign_id'),
 'campaign_summary':('campaign_id',),'unattributed':('channel',),
 'reconciliation':('record_type','record_id'),'visitors':('visit_type',),'quality':('event_id',),'summary':(),
 'raw_controls':('table_name',),
}


def config_check(config, cloud=False):
    if set(config)!={'project_id','dataset_id','location','maximum_bytes_billed','table_expiration_seconds'}:
        raise ValueError('Use only the documented configuration fields')
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]',config['project_id']):
        raise ValueError('Invalid project ID')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,1023}',config['dataset_id']):
        raise ValueError('Invalid dataset ID')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',config['location']):
        raise ValueError('Explicit location required')
    for field in ('maximum_bytes_billed','table_expiration_seconds'):
        if type(config[field]) is not int or config[field]<=0:
            raise ValueError(f'{field} must be a positive integer')
    if config['table_expiration_seconds']<3600:
        raise ValueError('Table expiration must be at least 3600 seconds')
    if cloud and (config['project_id']=='your-project-id' or config['location']=='CHOOSE_LOCATION'):
        raise ValueError('Replace project/location placeholders before cloud operations')


def table_name(group,table):
    if group not in GROUPS or table not in TABLE_KEYS:
        raise ValueError('Destination is not an explicitly owned demonstration table')
    return f'eg_demo_{group}_{table}'


def schemas():
    return {name:json.loads((BQ_ROOT/'schemas'/f'{name}.json').read_text()) for name in TABLE_KEYS}


def schema_validate(tables):
    for name,fields in schemas().items():
        for row in tables[name]:
            if set(row)!={f['name'] for f in fields}: raise ValueError(f'{name}: schema fields differ')
            for field in fields:
                value=row[field['name']]
                if value is None:
                    if field['mode']=='REQUIRED': raise ValueError(f'{name}: required field is null')
                    continue
                if field['type']=='INTEGER':
                    if type(value) is not int or not -(2**63)<=value<2**63: raise ValueError('Invalid INT64')
                elif not isinstance(value,str): raise ValueError('Expected string/date/timestamp encoding')


def scenario_inputs(baseline):
    baseline=Path(baseline)
    manifest=json.loads((baseline/'manifest.json').read_text())
    tables={}
    for name in TABLE_KEYS:
        blob=(baseline/f'{name}.json').read_bytes()
        if hashlib.sha256(blob).hexdigest()!=manifest['sha256'][name]: raise ValueError('Baseline fingerprint mismatch')
        tables[name]=json.loads(blob)
        if len(tables[name])!=manifest['row_counts'][name]: raise ValueError('Baseline count mismatch')
    hand=json.loads((ROOT/'tests/fixtures/sql_hand_calculated.json').read_text())['tables']
    groups={'baseline':tables,'hand':hand}
    scenarios={
      'baseline':('baseline',manifest['start_date'],manifest['end_date_exclusive'],manifest['observation_cutoff_exclusive']),
      'hand':('hand','2026-01-01','2026-01-06','2026-01-20'),
      'hand_early':('hand','2026-01-01','2026-01-06','2026-01-03'),
      'hand_reprocessed':('hand','2026-01-01','2026-01-06','2026-01-20'),
    }
    cases=json.loads((ROOT/'tests/fixtures/event_quality.json').read_text())['cases']
    for case in cases:
        groups[case['name']]={**deepcopy(hand),'events':deepcopy(case['events'])}
        scenarios[case['name']]=(case['name'],'2026-01-01','2026-01-06','2026-01-20')
    scenarios['late_before']=('late_arrival','2026-01-01','2026-01-06','2026-01-03')
    return manifest,groups,scenarios


def render_sql(config,group,name):
    config_check(config)
    if name not in BQ_QUERIES: raise ValueError('Unknown query')
    aliases=['parameters AS (SELECT @start_at AS start_at, @end_at AS end_at, @cutoff AS cutoff)']
    for table in TABLE_KEYS:
        target=f"{config['project_id']}.{config['dataset_id']}.{table_name(group,table)}"
        aliases.append(f'{table} AS (SELECT * FROM `{target}`)')
    models=(BQ_ROOT/'sql/models.sql').read_text().strip()
    campaign=(BQ_ROOT/'sql/queries/campaign_daily.sql').read_text().strip().rstrip(';')
    body=(BQ_ROOT/'sql/queries'/f'{name}.sql').read_text().strip().rstrip(';')
    sql='WITH '+',\n'.join(aliases)+',\n'+models+',\ncampaign_per_day AS (\n'+campaign+'\n)\nSELECT * FROM (\n'+body+'\n) AS report_result;\n'
    # Read-only query contract; no scripts or persistent SQL side effects.
    clean=re.sub(r'--[^\n]*','',sql)
    if clean.count(';')!=1 or re.search(r'\b(CREATE|DROP|DELETE|INSERT|UPDATE|MERGE|TRUNCATE|EXPORT|CALL)\b',clean,re.I):
        raise ValueError('Only a single read-only GoogleSQL statement is allowed')
    return sql


def prepare(config,baseline,output):
    """No cloud tooling required. Build upload files and SQLite parity expectations."""
    config_check(config)
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    manifest,groups,scenarios=scenario_inputs(baseline)
    plan={'status':'prepared_locally_not_bigquery_verified','config':config,
          'seed':manifest['seed'],'baseline_fingerprint':fingerprint(groups['baseline']),
          'tables':{},'scenarios':{},'schemas':{}}
    for table,fields in schemas().items():
        path=output/'schemas'/f'{table}.json';path.parent.mkdir(exist_ok=True);path.write_text(serialize(fields))
        plan['schemas'][table]=hashlib.sha256(path.read_bytes()).hexdigest()
    for group,tables in groups.items():
        schema_validate(tables)
        for table,rows in tables.items():
            name=table_name(group,table)
            path=output/'load'/f'{name}.ndjson';path.parent.mkdir(exist_ok=True)
            path.write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows))
            plan['tables'][name]={'group':group,'table':table,'rows':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    for scenario,(group,start,end,cutoff) in scenarios.items():
        db=load_database(groups[group],start,end,cutoff)
        try:
            expectations={name:query(db,name) for name in QUERIES}
            expectations['summary']=[summary(db)]
            amounts={'orders':'total_paid_cents','order_items':'net_merchandise_cents',
                     'refunds':'merchandise_refund_cents','ad_spend_daily':'spend_cents'}
            expectations['raw_controls']=[{
                'table_name':name,'row_count':len(groups[group][name]),'duplicate_keys':0,
                'duplicate_transaction_ids':0,
                'money_total_cents':sum(r[amounts[name]] for r in groups[group][name]) if name in amounts else None,
            } for name in sorted(TABLE_KEYS)]
        finally: db.close()
        path=output/'expected'/f'{scenario}.json';path.parent.mkdir(exist_ok=True);path.write_text(serialize(expectations))
        item={'group':group,'start_at':start+'T00:00:00Z','end_at':end+'T00:00:00Z','cutoff':cutoff+'T00:00:00Z',
              'expected_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'query_sha256':{}}
        for name in BQ_QUERIES:
            path=output/'sql'/group/f'{name}.sql';path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(render_sql(config,group,name))
            item['query_sha256'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
        plan['scenarios'][scenario]=item
    (output/'plan.json').write_text(serialize(plan))
    (output/'verification_status.json').write_text(serialize({
        'status':'not_verified_in_bigquery','plan_sha256':hashlib.sha256(serialize(plan).encode()).hexdigest()}))
    return plan


def compare_rows(name,expected,actual):
    """Check row keys, multiplicity, nulls and exact integers; tolerate only float rounding."""
    keys=KEYS[name]
    def keyed(rows):
        result={}
        for row in rows:
            key=tuple(row[k] for k in keys)
            if key in result: raise ValueError(f'{name}: duplicate result key')
            result[key]=row
        return result
    left,right=keyed(expected),keyed(actual)
    if left.keys()!=right.keys(): raise ValueError(f'{name}: missing or extra row keys')
    for key,row in left.items():
        other=right[key]
        if row.keys()!=other.keys(): raise ValueError(f'{name}: column mismatch')
        for column,value in row.items():
            got=other[column]
            if value is None:
                equal=got is None
            elif isinstance(value,int):
                try: equal=got is not None and Decimal(str(got))==value
                except InvalidOperation: equal=False
            elif isinstance(value,float):
                try: equal=got is not None and math.isclose(value,float(got),rel_tol=1e-10,abs_tol=1e-8)
                except (TypeError,ValueError): equal=False
            elif column.endswith(('_at','_time')):
                def moment(text):
                    t=datetime.fromisoformat(text.replace(' UTC','+00:00').replace('Z','+00:00'))
                    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)
                equal=got is not None and moment(value)==moment(got)
            else: equal=value==got
            if not equal: raise ValueError(f'{name}: value mismatch in {column}')


def bq_base(config):
    config_check(config,cloud=True)
    return ['bq','--bigqueryrc='+os.devnull,'--quiet','--format=json',
            '--project_id='+config['project_id'],'--location='+config['location']]


def query_command(config,scenario,sql,dry_run,rows):
    args=bq_base(config)+['query','--use_legacy_sql=false','--use_cache=false',
          '--maximum_bytes_billed='+str(config['maximum_bytes_billed']),
          '--max_rows='+str(max(1,rows+1)), '--dry_run='+str(dry_run).lower()]
    args += [f'--parameter={key}:TIMESTAMP:{scenario[key]}' for key in ('start_at','end_at','cutoff')]
    return args+[sql]


def call_bq(args):
    result=subprocess.run(args,capture_output=True,text=True,check=False)
    if result.returncode:
        # Never dump authentication diagnostics or tokens into logs.
        raise RuntimeError('bq operation failed; inspect authentication/permissions with Google Cloud CLI locally. Raw diagnostics suppressed.')
    return result.stdout


def estimated_bytes(output):
    """Extract only a numeric estimate; never persist raw authentication diagnostics."""
    try:
        job=json.loads(output)
        value=job.get('statistics',{}).get('query',{}).get('totalBytesProcessed')
        if value is None: value=job.get('statistics',{}).get('totalBytesProcessed')
        if value is not None: return int(value)
    except (ValueError,TypeError,AttributeError):
        pass
    match=re.search(r'process\s+([0-9]+)\s+bytes',output,re.I)
    return int(match.group(1)) if match else None


def metadata_guard(config,dataset,tables):
    if dataset.get('location','').lower()!=config['location'].lower(): raise ValueError('Dataset location mismatch')
    if dataset.get('labels',{}).get(OWNER_KEY)!=OWNER_VALUE: raise ValueError('Dataset lacks project ownership label')
    allowed={table_name(g,t) for g in GROUPS for t in TABLE_KEYS}
    for name,meta in tables.items():
        if name not in allowed: raise ValueError('Unexpected mutation target')
        if meta.get('type')!='TABLE' or meta.get('labels',{}).get(OWNER_KEY)!=OWNER_VALUE:
            raise ValueError('Existing demonstration table lacks ownership label or is not a base table')
        if meta.get('encryptionConfiguration'):
            raise ValueError('Refusing replacement of a customer-managed-key table without an encryption migration plan')


def cloud_run(mode,config,baseline,output,acknowledge=False,runner=call_bq,workers=1):
    """Explicit load / dry-run / execute stages; no dataset creation or deletion commands."""
    if type(workers) is not int or not 1<=workers<=4: raise ValueError('Use 1 to 4 query workers')
    if mode not in ('load','dry-run','execute'): raise ValueError('Unknown cloud mode')
    config_check(config,cloud=True)
    if mode in ('load','execute') and not acknowledge: raise ValueError('Explicit --acknowledge-cloud-actions required')
    if runner is call_bq and not shutil.which('bq'): raise RuntimeError('bq CLI is not installed; cloud execution is unverified')
    output=Path(output)
    plan=prepare(config,baseline,output) # Always recompute from verified source + reviewed SQL, not mutable plans.
    status_path=output/f'{mode}_status.json'
    status={'mode':mode,'status':'in_progress_not_verified','completed':[],'dry_run_estimates':{},
            'plan_sha256':hashlib.sha256(serialize(plan).encode()).hexdigest()}
    status_path.write_text(serialize(status))
    base=bq_base(config); dataset_ref=f"{config['project_id']}:{config['dataset_id']}"
    dataset=json.loads(runner(base+['show',dataset_ref]))
    listed=json.loads(runner(base+['ls','--max_results=10000',dataset_ref]) or '[]')
    if len(listed)>=10000: raise ValueError('Dataset inventory may be truncated; use a dedicated small dataset')
    existing={r['tableReference']['tableId'] for r in listed}
    metadata={name:json.loads(runner(base+['show',dataset_ref+'.'+name])) for name in plan['tables'] if name in existing}
    metadata_guard(config,dataset,metadata)
    # Only noncredential metadata is persisted; ACLs and raw CLI diagnostics are omitted.
    fields=('type','labels','numRows','numBytes','creationTime','expirationTime','etag')
    snapshot={'dataset':{k:dataset.get(k) for k in ('location','labels','defaultTableExpirationMs')},
              'tables':{name:{k:meta.get(k) for k in fields} for name,meta in metadata.items()}}
    (output/'cloud_metadata.json').write_text(serialize(snapshot))
    if mode=='load':
        receipt_path=output/'load_receipts.json'
        receipts=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        status['skipped_unchanged']=[]
        for name,item in plan['tables'].items():
            target=dataset_ref+'.'+name; schema=str(output/'schemas'/f"{item['table']}.json")
            receipt_key=target
            source={'sha256':item['sha256'],'schema_sha256':plan['schemas'][item['table']]}
            if name in existing:
                remote=metadata[name]
                receipt=receipts.get(receipt_key,{})
                if (remote.get('etag') and receipt=={**source,'etag':remote['etag']}
                        and int(remote['numRows'])==item['rows']):
                    status['skipped_unchanged'].append(name)
                    status['completed'].append(name)
                    status_path.write_text(serialize(status))
                    continue
                if int(remote['numRows'])!=0:
                    raise ValueError('Refusing automatic replacement of a nonempty table without a matching input/schema/remote-version receipt')
            if name not in existing:
                runner(base+['mk','--table',f'--label={OWNER_KEY}:{OWNER_VALUE}',
                             '--expiration='+str(config['table_expiration_seconds']),target,schema])
            runner(base+['load','--replace=true','--source_format=NEWLINE_DELIMITED_JSON',
                         '--autodetect=false','--max_bad_records=0','--ignore_unknown_values=false',
                         target,str(output/'load'/f'{name}.ndjson'),schema])
            loaded=json.loads(runner(base+['show',target]))
            metadata_guard(config,dataset,{name:loaded})
            if int(loaded['numRows'])!=item['rows']: raise ValueError('Loaded row count mismatch')
            if not loaded.get('etag'): raise ValueError('Missing remote version for load receipt')
            receipts[receipt_key]={**source,'etag':loaded['etag']}
            receipt_path.write_text(serialize(receipts))
            status['completed'].append(name)
            status_path.write_text(serialize(status))
        status['status']='loaded_only_parity_not_verified'
    else:
        if set(plan['tables'])-existing: raise ValueError('Required demonstration tables missing; cloud dry runs do not load data')
        def check_query(scenario,item,name):
            expected=json.loads((output/'expected'/f'{scenario}.json').read_text())
            sql=(output/'sql'/item['group']/f'{name}.sql').read_text()
            estimate=estimated_bytes(runner(query_command(config,item,sql,True,len(expected[name]))))
            if estimate is not None and estimate>config['maximum_bytes_billed']:
                raise ValueError('Dry-run estimate exceeds configured bytes cap')
            if mode=='execute':
                actual=json.loads(runner(query_command(config,item,sql,False,len(expected[name]))))
                compare_rows(name,expected[name],actual)
                path=output/'actual'/scenario/f'{name}.json';path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(serialize(actual))
            return scenario+'/'+name,estimate
        tasks=[(scenario,item,name) for scenario,item in plan['scenarios'].items() for name in BQ_QUERIES]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(check_query,*task):task for task in tasks}
            for future in as_completed(futures):
                try:
                    key,estimate=future.result()
                except Exception:
                    for pending in futures: pending.cancel()
                    scenario,_,name=futures[future]
                    status['status']='failed_not_verified'
                    status['failed_comparison']=scenario+'/'+name
                    status_path.write_text(serialize(status))
                    raise
                status['dry_run_estimates'][key]=estimate
                status['completed'].append(key)
                status_path.write_text(serialize(status))
        status['completed'].sort()
        status['status']='google_dry_runs_passed_execution_unverified' if mode=='dry-run' else 'live_bigquery_parity_passed'
    status_path.write_text(serialize(status))
    (output/'verification_status.json').write_text(serialize(status))
    return status
