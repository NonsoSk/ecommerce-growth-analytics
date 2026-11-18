"""Validate packaged data after unpacking to an unrelated temporary directory.
This is not a Tableau close/reopen or interactive-filter test.
"""
from pathlib import Path
from datetime import date
import csv,zipfile,tempfile,json,argparse
import xml.etree.ElementTree as E
from tableauhyperapi import HyperProcess,Connection,Telemetry
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=ROOT/'dashboard/workbooks/SYNTHETIC_Growth_REVIEW.twbx');args=parser.parse_args();package=args.package
with tempfile.TemporaryDirectory(prefix='tableau-portability-') as tmp, zipfile.ZipFile(package) as z:
 base=Path(tmp)
 for name in z.namelist():
  path=Path(name);assert not path.is_absolute() and '..' not in path.parts
 z.extractall(base)
 workbooks=list(base.glob('*.twb'));assert len(workbooks)==1
 r=E.parse(workbooks[0]).getroot();counts={}
 with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
  for ds in r.findall('./datasources/datasource'):
   if ds.get('name')=='Parameters':continue
   tc=ds.find('./connection/named-connections/named-connection/connection');hc=ds.find('./extract/connection')
   csvpath=base/tc.get('directory')/tc.get('filename');hyperpath=base/hc.get('dbname')
   rows=list(csv.DictReader(csvpath.open()));keys=list(rows[0]);strings={'device','channel','visit_type','campaign_id','coverage'}
   expected=[tuple(v if k in strings or k=='day' else int(v) if v else None for k,v in row.items()) for row in rows]
   with Connection(hyper.endpoint,hyperpath) as c:
    actual=[tuple(str(v) if k=='day' else v for k,v in zip(keys,row)) for row in c.execute_list_query('SELECT * FROM "Extract"."Extract"')]
   assert sorted(actual)==sorted(expected)
   counts[ds.get('name')]=len(actual)
 print(json.dumps({'relocated_all_rows_match':counts,'tableau_close_reopen':'not_verified'},indent=2))
