"""Check generated Tableau formulas/filter predicates through local Hyper SQL.
This validates expression arithmetic and selected rows, not Tableau UI interactions.
"""
import csv,json,re,sys,math,tempfile,shutil,argparse
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.dashboard import totals,select,NUMBERS
from tableauhyperapi import HyperProcess,Connection,Telemetry
parser=argparse.ArgumentParser();parser.add_argument('--workbook',type=Path,default=ROOT/'dashboard/workbooks/SYNTHETIC_Growth_REVIEW.twb');args=parser.parse_args()
r=E.parse(args.workbook).getroot()
manifest=json.loads((ROOT/'dashboard/data/manifest.json').read_text());receipts=json.loads((ROOT/'dashboard/workbooks/extract_receipt.json').read_text())
refs={w.get('name') for w in r.findall('./worksheets/worksheet')}
for d in r.findall('./dashboards/dashboard'):
 for z in d.findall('./zones/zone'):
  if z.get('name'):assert z.get('name') in refs
for w in r.findall('./windows/window[@class="dashboard"]'):
 names={x.get('name') for x in w.findall('./viewpoints/viewpoint')}
 dashboard=r.find(f'./dashboards/dashboard[@name="{w.get("name")}"]')
 assert names=={z.get('name') for z in dashboard.findall('./zones/zone') if z.get('name')}

def sql(formula,params):
 for key,val in params.items():
  literal="DATE '"+val+"'" if key in ('Start','End') else "'"+val.replace("'","''")+"'"
  formula=formula.replace('[Parameters].['+key+']',literal)
 formula=formula.replace('"All"',"'All'")
 formula=re.sub(r'\[([^]]+)\]',lambda m:'"'+m[1]+'"',formula)
 # Tableau / uses real division; Hyper SQL integer / would truncate.
 formula=re.sub(r'SUM\(([^)]+)\)',r'CAST(SUM(\1) AS DOUBLE PRECISION)',formula)
 if formula.startswith('IF '):formula='CASE WHEN '+formula[3:]
 return formula
mapping={'Sessions':'sessions','Converting sessions':'converting_sessions','Orders':'orders','Purchase conversion':'conversion_rate','Net merchandise revenue USD':'net_revenue_cents','Merchandise refunds USD':'refunds_cents','Advertising spend USD':'spend_cents','Paid spend USD':'spend_cents','Paid-attributed net revenue USD':'net_revenue_cents','Paid-attributed orders':'attributed_orders','Net attributed ROAS':'net_roas','First-observed paid CAC proxy USD':'first_observed_paid_cac_proxy_cents','Days with spend and zero attributed orders':'days_with_spend_zero_orders','Skipped or out-of-order sessions':'skipped_or_out_of_order_sessions', '01 Session starts':'session_starts','02 Product views':'product_views','03 Add to cart':'carts','04 Checkout':'checkouts','05 Ordered purchase':'purchases'}
checks=[]
with tempfile.TemporaryDirectory(prefix='tableau-validation-') as tmp, HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
 for case in manifest['filtered_validation']:
  group=case['dataset']; ds=r.find(f'./datasources/datasource[@name="federated.{group}"]')
  params={'Start':case['start'],'End':case['end_inclusive'],'Device':'All','Traffic':'All','Visit':'All','Paid':'All','Campaign':'All'}
  for field,val in case['filters'].items():params[{'device':'Device','visit_type':'Visit','campaign_id':'Campaign','channel':'Traffic' if group=='funnel' else 'Paid'}[field]]=val
  predicate=sql(ds.find("column[@name='[Eligible]']/calculation").get('formula'),params)
  snapshot=Path(tmp)/f'{group}.hyper'
  if not snapshot.exists():shutil.copy2(receipts[group]['path'],snapshot)
  with Connection(hyper.endpoint,snapshot) as c:
   for col in ds.findall('column'):
    title=col.get('caption');calc=col.find('calculation')
    if title not in mapping or calc is None:continue
    got=c.execute_scalar_query('SELECT '+sql(calc.get('formula'),params)+' FROM "Extract"."Extract" WHERE '+predicate)
    expected=case['values'][mapping[title]]
    if title.endswith('USD') and expected is not None:expected/=100
    assert (got is None and expected is None) or (got is not None and expected is not None and math.isclose(float(got),expected,rel_tol=1e-10,abs_tol=1e-8)),(group,title,got,expected)
    checks.append({'dataset':group,'metric':title,'start':case['start'],'end':case['end_inclusive'],'filters':case['filters'],'expected':expected,'actual':None if got is None else float(got),'pass':True})
report={'workbook':str(args.workbook),'status':'expression_math_verified_in_hyper_not_tableau_ui','checks':checks,'count':len(checks),'dashboard_references':'pass'}
(ROOT/'dashboard/workbooks'/(args.workbook.stem+'_formula_validation.json')).write_text(json.dumps(report,indent=2));print(f'{len(checks)} workbook formula/filter comparisons passed; dashboard references passed. UI behavior remains unverified.')
