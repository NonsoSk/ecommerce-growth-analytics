"""Bind regenerated baseline data to the accepted layout, checking analytical equivalence."""
from pathlib import Path
import xml.etree.ElementTree as E
import hashlib
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'dashboard/workbooks'
source=base/'SYNTHETIC_Growth_BUILD.twb';target=base/'SYNTHETIC_Growth_REBUILD.twb'

def canonical(e):
 return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(canonical(c) for c in e))

def contract(root):
 """Layout/style and unused dependency pruning must not change analytics or filter scope."""
 calculations={}
 for ds in root.findall('./datasources/datasource'):
  calculations[ds.get('name')]={c.get('name'):canonical(c.find('calculation')) for c in ds.findall('column') if c.find('calculation') is not None}
 sheets={w.get('name'):{p:tuple(canonical(e) for e in w.findall(p)) for p in ('.//filter','.//table/rows','.//table/cols','.//encodings')} for w in root.findall('./worksheets/worksheet')}
 for w in root.findall('./worksheets/worksheet'):
  sheets[w.get('name')]['sources']=tuple(d.get('name') for d in w.findall('.//view/datasources/datasource'))
 return calculations,sheets

if __name__=='__main__':
 generated=E.parse(source).getroot()
 r=E.parse(ROOT/'dashboard/templates/accepted_workbook.twb').getroot()
 assert contract(generated)==contract(r), 'Accepted layout analytics/filter contract differs from generated workbook'
 # Rebind only file paths; all accepted worksheet/dashboard layout stays intact.
 for ds in r.findall('./datasources/datasource'):
  reference=generated.find('./datasources/datasource[@name="'+ds.get('name')+'"]')
  for c in ds.iter('connection'):
   kind=c.get('class')
   if kind not in ('textscan','hyper'):continue
   matches=[v for v in reference.iter('connection') if v.get('class')==kind]
   assert len(matches)==1
   for key in (('directory','filename') if kind=='textscan' else ('dbname',)):c.set(key,matches[0].get(key))
 r.set('xmlns:user','http://www.tableausoftware.com/xml/user')
 assert len(r.findall('./worksheets/worksheet'))==29 and len(r.findall('./dashboards/dashboard'))==3
 E.indent(r);data=E.tostring(r,encoding='utf-8',xml_declaration=True)
 if target.exists() and target.read_bytes()!=data:
  previous=target.read_bytes();backup=base/'backups'/('REBUILD_'+hashlib.sha256(previous).hexdigest()[:12]+'.twb')
  backup.parent.mkdir(exist_ok=True)
  if not backup.exists():backup.write_bytes(previous)
 target.write_bytes(data);print(target)
