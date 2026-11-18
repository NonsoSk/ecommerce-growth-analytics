"""Offline reproducible build. Requires the optional pinned Hyper environment; no cloud calls."""
from pathlib import Path
import argparse,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--hyper-python',type=Path,required=True)
a=p.parse_args();hyper=a.hyper_python.absolute()
def run(script,*args,python=None):
 subprocess.run([str(python or sys.executable),str(ROOT/'scripts'/script),*map(str,args)],cwd=ROOT,check=True)
if not (ROOT/'data/generated/baseline/manifest.json').exists():run('generate_sample.py')
run('prepare_dashboard.py')
run('prepare_tableau_extracts.py',python=hyper)
run('build_tableau_dashboard.py')
run('finalize_tableau_review.py')
workbook=ROOT/'dashboard/workbooks/SYNTHETIC_Growth_REBUILD.twb'
package=workbook.with_suffix('.twbx')
run('validate_tableau_workbook.py','--workbook',workbook,python=hyper)
run('package_tableau_dashboard.py','--source',workbook,'--output',package)
run('validate_portable_tableau.py','--package',package,python=hyper)
print('Build verified; Tableau UI acceptance is separate:',package)
