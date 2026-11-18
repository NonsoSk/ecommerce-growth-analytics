"""Create content-addressed local Hyper extracts; never publish or append."""
from pathlib import Path
from datetime import date
import csv,hashlib,json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.dashboard import verified_baseline
from tableauhyperapi import HyperProcess,Connection,Telemetry,CreateMode,TableDefinition,TableName,SqlType,Inserter
verified_baseline(ROOT/'data/generated/baseline')
manifest=json.loads((ROOT/'dashboard/data/manifest.json').read_text())
out=ROOT/'dashboard/workbooks/extracts';out.mkdir(parents=True,exist_ok=True)
receipt={}
with tempfile.TemporaryDirectory(prefix='tableau-extract-check-') as tmp, HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
 for name,info in ((k.removesuffix('.csv'),v) for k,v in manifest['files'].items()):
  path=ROOT/'dashboard/data'/f'{name}.csv';digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==info['sha256']
  rows=list(csv.DictReader(path.open()));keys=list(rows[0]);strings={'device','channel','visit_type','campaign_id','coverage'}
  values=[[date.fromisoformat(r[k]) if k=='day' else r[k] if k in strings else int(r[k]) if r[k] else None for k in keys] for r in rows]
  target=out/f'{name}_{digest[:12]}.hyper';exists=target.exists()
  connection_path=target
  if exists:
   connection_path=Path(tmp)/target.name;shutil.copy2(target,connection_path)
  with Connection(hyper.endpoint,connection_path,CreateMode.NONE if exists else CreateMode.CREATE) as c:
   if not exists:
    c.catalog.create_schema('Extract')
    table=TableDefinition(TableName('Extract','Extract'),[TableDefinition.Column(k,SqlType.date() if k=='day' else SqlType.text() if k in strings else SqlType.big_int()) for k in keys])
    c.catalog.create_table(table)
    with Inserter(c,table) as ins:ins.add_rows(values);ins.execute()
   raw=c.execute_list_query('SELECT * FROM "Extract"."Extract" ORDER BY '+','.join('"'+k+'"' for k in info['grain']))
   expected=sorted(values,key=lambda r:tuple(r[keys.index(k)] for k in info['grain']))
   normalize=lambda row:[str(v) if k=='day' else v for k,v in zip(keys,row)]
   assert [normalize(r) for r in raw]==[normalize(r) for r in expected]
   checks=[]
   for check in manifest['filtered_validation']:
    if check['dataset']!=name:continue
    where='"day" BETWEEN DATE \''+check['start']+'\' AND DATE \''+check['end_inclusive']+'\''
    for key,value in check['filters'].items():where+=' AND "'+key+'" = \''+value.replace("'","''")+"'"
    fields=list(check['sql_differences'])
    result=c.execute_list_query('SELECT '+','.join('COALESCE(SUM("'+k+'"),0)' for k in fields)+' FROM "Extract"."Extract" WHERE '+where)[0]
    assert all(v==check['values'][k] for k,v in zip(fields,result))
    checks.append({'start':check['start'],'end':check['end_inclusive'],'filters':check['filters'],'differences':dict.fromkeys(fields,0)})
   receipt[name]={'path':str(target),'csv_sha256':digest,'rows':len(raw),'all_rows_equal':True,'sql_filter_checks':checks}
(ROOT/'dashboard/workbooks/extract_receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:{'rows':v['rows'],'all_rows_equal':v['all_rows_equal'],'sql_checks':len(v['sql_filter_checks'])} for k,v in receipt.items()},indent=2))
