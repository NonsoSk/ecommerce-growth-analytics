"""Normalize period notes idempotently in a separate build candidate; never edit REVIEW."""
from pathlib import Path
import xml.etree.ElementTree as E
import hashlib
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'dashboard/workbooks'
source=base/'SYNTHETIC_Growth_BUILD.twb';target=base/'SYNTHETIC_Growth_REBUILD.twb'
r=E.parse(source).getroot();r.set('xmlns:user','http://www.tableausoftware.com/xml/user')
old='Jan 1–Mar 31, 2026 UTC • USD •'
new='Available data: Jan 1–Mar 31, 2026 UTC. Selected period: date controls below. USD •'
notes=0
for run in r.findall('./dashboards/dashboard/zones/zone/formatted-text/run'):
 if run.text and run.text.startswith(old):run.text=new+run.text[len(old):]
 if run.text and run.text.startswith(new):notes+=1
assert notes==3
assert len(r.findall('./worksheets/worksheet'))==29
assert len(r.findall('./dashboards/dashboard'))==3
E.indent(r);data=E.tostring(r,encoding='utf-8',xml_declaration=True)
if target.exists() and target.read_bytes()!=data:
 previous=target.read_bytes();backup=base/'backups'/('REBUILD_'+hashlib.sha256(previous).hexdigest()[:12]+'.twb')
 backup.parent.mkdir(exist_ok=True)
 if not backup.exists():backup.write_bytes(previous)
target.write_bytes(data)
print(target)
