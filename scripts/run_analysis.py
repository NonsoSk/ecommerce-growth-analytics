"""One local command: tests, baseline verification, SQLite, CSVs and synthetic report."""
import argparse
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.analysis import run_analysis
from ecommerce_growth.synthetic import serialize, write_dataset


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cutoff',help='Exclusive UTC observation date YYYY-MM-DD (default: manifest cutoff)')
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return 1
    baseline=ROOT/'data/generated/baseline'
    if not (baseline/'manifest.json').exists():
        if baseline.exists() and any(baseline.iterdir()):
            raise ValueError('Existing baseline has no manifest; preserve and inspect it before regeneration')
        write_dataset(baseline)
    metadata=run_analysis(baseline,ROOT/'data/generated/analysis',args.cutoff,
                          {'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)})
    print(serialize({'summary':metadata['summary'],'fingerprint':metadata['data_fingerprint'],
                     'tests':metadata['tests'],'outputs':'data/generated/analysis/'}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
