"""Offline preparation/guard tests only. Mocks do not validate GoogleSQL or cloud parity."""
from copy import deepcopy
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.bigquery_migration import (
 BQ_QUERIES, GROUPS, OWNER_KEY, OWNER_VALUE, config_check, table_name, schemas,
 schema_validate, prepare, render_sql, compare_rows, metadata_guard, query_command, cloud_run,
 estimated_bytes,
)
from ecommerce_growth.synthetic import write_dataset, TABLE_KEYS


class FakeBQ:
    """In-memory CLI responses for workflow tests, never a SQL execution engine."""
    def __init__(self,config,output,plan,populated=True):
        self.config,self.output,self.plan=config,Path(output),plan
        self.calls=[]
        self.tables={name:{'type':'TABLE','labels':{OWNER_KEY:OWNER_VALUE},'numRows':str(item['rows'])}
                     for name,item in plan['tables'].items()} if populated else {}
        self.sql_lookup={render_sql(config,group,name):(group,name) for group in GROUPS for name in BQ_QUERIES}
    def __call__(self,args):
        self.calls.append(args)
        if 'show' in args:
            target=args[-1]
            if '.' not in target:
                return json.dumps({'location':self.config['location'],'labels':{OWNER_KEY:OWNER_VALUE}})
            return json.dumps(self.tables[target.split('.')[-1]])
        if 'ls' in args: return json.dumps([{'tableReference':{'tableId':name}} for name in self.tables])
        if 'mk' in args:
            name=args[-2].split('.')[-1]
            self.tables[name]={'type':'TABLE','labels':{OWNER_KEY:OWNER_VALUE},'numRows':'0'}
            return '{}'
        if 'load' in args:
            name=args[-3].split('.')[-1]
            assert '--replace=true' in args
            self.tables[name]['numRows']=str(len(Path(args[-2]).read_text().splitlines()))
            return '{}'
        if 'query' in args:
            if '--dry_run=true' in args: return 'Mock validation only'
            group,name=self.sql_lookup[args[-1]]
            cutoff=next(v for v in args if v.startswith('--parameter=cutoff:TIMESTAMP:')).split('TIMESTAMP:')[1]
            scenario=next(k for k,v in self.plan['scenarios'].items() if v['group']==group and v['cutoff']==cutoff)
            result=json.loads((self.output/'expected'/f'{scenario}.json').read_text())[name]
            # Simulate JSON CLI integer strings; parity comparator must still enforce exactness.
            return json.dumps([{k:str(v) if type(v) is int else v for k,v in row.items()} for row in result])
        raise AssertionError('Unexpected command')


class BigQueryPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.base=Path(cls.temp.name)/'baseline'; cls.out=Path(cls.temp.name)/'prepared'
        write_dataset(cls.base,sessions=137)
        cls.config={'project_id':'example-project','dataset_id':'ecommerce_growth_demo','location':'EU',
                    'maximum_bytes_billed':1000000000,'table_expiration_seconds':604800}
        cls.plan=prepare(cls.config,cls.base,cls.out)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_explicit_schemas_match_existing_fields_and_minor_units(self):
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript((ROOT/'sql/analysis/00_schema.sql').read_text())
            for name,fields in schemas().items():
                self.assertEqual({r[1] for r in db.execute(f'PRAGMA table_info({name})')},{f['name'] for f in fields})
                for f in fields:
                    if f['name'].endswith('_cents'): self.assertEqual(f['type'],'INTEGER')
                    if f['name'].endswith('_at'): self.assertEqual(f['type'],'TIMESTAMP')
        tables={k:json.loads((self.base/f'{k}.json').read_text()) for k in TABLE_KEYS}
        schema_validate(tables)
        tables['orders'][0]['total_paid_cents']=2**63
        with self.assertRaises(ValueError): schema_validate(tables)

    def test_rendered_queries_are_single_read_only_native_sql(self):
        for name in BQ_QUERIES:
            sql=render_sql(self.config,'baseline',name)
            clean=re.sub(r'--[^\n]*','',sql)
            self.assertEqual(clean.count(';'),1)
            self.assertNotRegex(clean,r'(?i)\b(PRAGMA|STRICT|julianday|CREATE|DROP|DELETE|INSERT|UPDATE|MERGE|TRUNCATE)\b')
            self.assertEqual(clean.count('('),clean.count(')'))
            self.assertIn('@cutoff',sql)
            self.assertIn('TIMESTAMP_ADD',sql)
            self.assertNotIn('SUM(skipped_or_out_of_order_events>0)',sql)
        self.assertIn('SAFE_DIVIDE',render_sql(self.config,'baseline','daily'))
        self.assertIn('UNION DISTINCT',render_sql(self.config,'baseline','campaign_daily'))

    def test_prepare_is_deterministic_and_never_calls_cloud(self):
        before={p.name:p.read_bytes() for p in self.base.iterdir()}
        with patch('subprocess.run',side_effect=AssertionError('No cloud or shell calls allowed')):
            one=prepare(self.config,self.base,self.out);two=prepare(self.config,self.base,self.out)
        self.assertEqual(one,two)
        self.assertEqual(len(one['tables']),40);self.assertEqual(len(one['scenarios']),8)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.base.iterdir()})
        self.assertEqual(json.loads((self.out/'verification_status.json').read_text())['status'],'not_verified_in_bigquery')

    def test_identifier_and_cost_guards(self):
        for key,value in [('project_id','bad`project'),('dataset_id','a;DROP TABLE x'),('maximum_bytes_billed',0),('maximum_bytes_billed',True),('table_expiration_seconds',-1),('table_expiration_seconds',3599)]:
            config={**self.config,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError): config_check(config)
        with self.assertRaises(ValueError): table_name('production','orders')
        with self.assertRaises(ValueError): table_name('baseline','all_tables')
        with self.assertRaises(ValueError): config_check({**self.config,'location':'CHOOSE_LOCATION'},cloud=True)

    def test_ownership_location_and_table_type_guards(self):
        good={'location':'EU','labels':{OWNER_KEY:OWNER_VALUE}}
        name=table_name('baseline','orders')
        metadata_guard(self.config,good,{name:{'type':'TABLE','labels':{OWNER_KEY:OWNER_VALUE}}})
        for dataset,tables in [({'location':'US','labels':good['labels']},{}),({'location':'EU'},{}),
                               (good,{name:{'type':'TABLE'}}),(good,{name:{'type':'VIEW','labels':good['labels']}}),
                               (good,{name:{'type':'TABLE','labels':good['labels'],'encryptionConfiguration':{'kmsKeyName':'example'}}})]:
            with self.assertRaises(ValueError): metadata_guard(self.config,dataset,tables)

    def test_cloud_writes_require_acknowledgement(self):
        calls=[]
        for mode in ('load','execute'):
            with self.assertRaises(ValueError): cloud_run(mode,self.config,self.base,self.out,runner=lambda a:calls.append(a))
        self.assertEqual(calls,[])

    def test_query_caps_parameters_and_extra_row_detection(self):
        item=self.plan['scenarios']['baseline']
        for dry in (True,False):
            args=query_command(self.config,item,'SELECT 1',dry,100)
            self.assertIn('--maximum_bytes_billed=1000000000',args)
            self.assertIn('--max_rows=101',args)
            self.assertIn('--dry_run='+str(dry).lower(),args)
            self.assertIn('--use_legacy_sql=false',args)
            self.assertIn('--parameter=cutoff:TIMESTAMP:'+item['cutoff'],args)
        self.assertEqual(estimated_bytes('Query will process 12345 bytes of data.'),12345)
        self.assertEqual(estimated_bytes('{"statistics":{"query":{"totalBytesProcessed":"4321"}}}'),4321)
        self.assertIsNone(estimated_bytes('No numeric estimate supplied'))

    def test_parity_rejects_cent_null_key_and_duplicate_errors(self):
        expected=[{'session_date':'2026-01-01','net_revenue_cents':9007199254740993,'rate':.5,'empty':None}]
        actual=[{**expected[0],'net_revenue_cents':'9007199254740993','rate':'0.50000000000001'}]
        compare_rows('daily',expected,actual)
        for rows in [[{**actual[0],'net_revenue_cents':'9007199254740992'}],
                     [{**actual[0],'empty':0}],actual*2,[],[{**actual[0],'extra':0}]]:
            with self.assertRaises(ValueError): compare_rows('daily',expected,rows)
        compare_rows('quality',[{'event_id':'e','occurred_at':'2026-01-01T00:00:00Z'}],
                     [{'event_id':'e','occurred_at':'2026-01-01 00:00:00 UTC'}])

    def test_mock_load_twice_replaces_only_allowlisted_tables(self):
        fake=FakeBQ(self.config,self.out,self.plan,populated=False)
        cloud_run('load',self.config,self.base,self.out,True,runner=fake)
        first=deepcopy(fake.tables)
        cloud_run('load',self.config,self.base,self.out,True,runner=fake)
        self.assertEqual(first,fake.tables)
        self.assertEqual(set(fake.tables),set(self.plan['tables']))
        self.assertEqual(sum('mk' in args for args in fake.calls),40)
        self.assertEqual(sum('load' in args for args in fake.calls),80)
        self.assertFalse(any('rm' in args or '--dataset' in args for args in fake.calls))

    def test_mock_dry_run_never_loads_or_executes_queries(self):
        fake=FakeBQ(self.config,self.out,self.plan)
        status=cloud_run('dry-run',self.config,self.base,self.out,runner=fake)
        self.assertEqual(len(status['completed']),8*len(BQ_QUERIES))
        self.assertFalse(any('load' in args or 'mk' in args for args in fake.calls))
        self.assertTrue(all('--dry_run=true' in args for args in fake.calls if 'query' in args))

    def test_mock_execution_compares_every_scenario_and_query(self):
        fake=FakeBQ(self.config,self.out,self.plan)
        status=cloud_run('execute',self.config,self.base,self.out,True,runner=fake)
        self.assertEqual(len(status['completed']),8*len(BQ_QUERIES))
        queries=[a for a in fake.calls if 'query' in a]
        self.assertEqual(len(queries),16*len(BQ_QUERIES))
        for i in range(0,len(queries),2):
            self.assertIn('--dry_run=true',queries[i]);self.assertIn('--dry_run=false',queries[i+1])

    def test_sqlite_expectations_include_hand_arithmetic_and_late_reprocessing(self):
        def expected(s):return json.loads((self.out/'expected'/f'{s}.json').read_text())
        hand=expected('hand')
        self.assertEqual(hand['summary'][0]['net_revenue_cents'],32500)
        self.assertEqual(hand['summary'][0]['orders'],4)
        self.assertEqual(hand['summary'][0]['converting_sessions'],3)
        self.assertEqual(expected('hand_early')['funnel'][0]['purchases'],1)
        self.assertEqual(hand['funnel'][0]['purchases'],2)
        self.assertEqual(hand,expected('hand_reprocessed'))
        self.assertEqual(expected('duplicate_purchase')['quality'][1]['reason'],'duplicate_purchase')


if __name__=='__main__':unittest.main()
