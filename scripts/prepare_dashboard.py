"""Reproduce baseline-only portable dashboard data without BigQuery access."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.dashboard import export
if __name__=='__main__':
    data,evidence=export()
    (ROOT/'dashboard/data/preview_data.js').write_text('window.dashboardData='+json.dumps(data,separators=(',',':'))+';\n')
    print(json.dumps({'rows':{k:len(v) for k,v in data.items()},'sql_filter_checks':len(evidence['filtered_validation']),'tableau_workbook_status':evidence['tableau_workbook_status']},indent=2))
