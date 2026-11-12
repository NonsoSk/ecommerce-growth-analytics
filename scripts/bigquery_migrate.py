"""Prepare offline by default. Cloud load, dry-run and execution are explicit stages."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.bigquery_migration import prepare,cloud_run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('prepare','load','dry-run','execute'),nargs='?',default='prepare')
    parser.add_argument('--config',type=Path,default=ROOT/'bigquery/config.example.json')
    parser.add_argument('--acknowledge-cloud-actions',action='store_true')
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    baseline=ROOT/'data/generated/baseline'; output=ROOT/'data/generated/bigquery'
    if args.mode=='prepare':
        plan=prepare(config,baseline,output)
        print(json.dumps({'status':plan['status'],'owned_tables':len(plan['tables']),
                          'scenarios':len(plan['scenarios']),'cloud_requests':0},indent=2))
    else:
        result=cloud_run(args.mode,config,baseline,output,args.acknowledge_cloud_actions)
        print(json.dumps({'status':result['status'],'completed':len(result['completed'])},indent=2))


if __name__=='__main__': main()
