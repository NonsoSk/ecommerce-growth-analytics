"""Generate ignored, deterministic synthetic data from the repository root."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ecommerce_growth.synthetic import serialize, write_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--sessions', type=int, default=2700)
    parser.add_argument('--start', default='2026-01-01', help='First UTC date; always 90 days')
    args = parser.parse_args()
    # Fixed ignored destination prevents accidentally exporting bulk data into tracked samples.
    print(serialize(write_dataset(ROOT / 'data/generated/baseline', args.seed, args.sessions, args.start)))


if __name__ == '__main__':
    main()
