"""Package only synthetic local data; original workbooks remain unchanged."""
from pathlib import Path,PurePosixPath
import xml.etree.ElementTree as E
import hashlib,json,zipfile,argparse
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'dashboard/workbooks'
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=base/'SYNTHETIC_Growth_REVIEW.twb');parser.add_argument('--output',type=Path,default=base/'SYNTHETIC_Growth_REVIEW.twbx');args=parser.parse_args()
source=args.source;target=args.output
assert target.resolve().parent==base.resolve() and target.suffix=='.twbx'
workbook_name=target.stem+'.twb'
r=E.parse(source).getroot();r.set('xmlns:user','http://www.tableausoftware.com/xml/user')
for key in list(r.attrib):
 if 'Fingerprinting' in key:del r.attrib[key]
files={};replaced=[]
for c in r.iter('connection'):
 if c.get('class')=='textscan':
  old=Path(c.get('directory'))/c.get('filename');dest='Data/'+old.name
  assert old.resolve().parent==(ROOT/'dashboard/data').resolve()
  files[dest]=old.read_bytes();replaced.append(str(old));c.set('directory','Data')
 elif c.get('class')=='hyper':
  old=Path(c.get('dbname'));assert old.resolve().parent==(base/'extracts').resolve()
  dest='Data/'+old.name;files[dest]=old.read_bytes();replaced.append(str(old));c.set('dbname',dest)
E.indent(r);files[workbook_name]=E.tostring(r,encoding='utf-8',xml_declaration=True)
assert b'/Users/' not in files[workbook_name]
assert b'/var/folders/' not in files[workbook_name]
# Target chosen explicitly above.
if target.exists():
 old=target.read_bytes();b=base/'backups'/('PORTABLE_'+hashlib.sha256(old).hexdigest()[:12]+'.twbx')
 b.parent.mkdir(exist_ok=True)
 if not b.exists():b.write_bytes(old)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(files.items()):
  info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==7
 for name,data in files.items():assert z.read(name)==data
 for c in r.iter('connection'):
  path=c.get('dbname') if c.get('class')=='hyper' else str(PurePosixPath(c.get('directory'))/c.get('filename')) if c.get('class')=='textscan' else None
  if path:assert not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and path in files
report={'status':'package_integrity_passed_tableau_reopen_not_verified','files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},'replaced_absolute_paths':replaced,'package_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(base/(target.stem+'_manifest.json')).write_text(json.dumps(report,indent=2));print(target);print('7 entries verified: workbook, 3 CSVs, 3 Hyper extracts; all data paths relative.')
