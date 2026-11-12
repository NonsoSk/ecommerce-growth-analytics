"""Keep the reviewed report aligned with computed output and attribution caveats."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ecommerce_growth.analysis import run_analysis
from ecommerce_growth.synthetic import write_dataset


class ReportReviewTests(unittest.TestCase):
    def test_committed_report_matches_regeneration_and_corrections(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)/'baseline'; output=Path(directory)/'analysis'
            write_dataset(base)
            run_analysis(base,output)
            regenerated=(output/'MILESTONE_2_ANALYSIS.md').read_text()
        committed=(ROOT/'reports/MILESTONE_2_ANALYSIS.md').read_text()
        # Test count is run metadata, not a metric; standalone rendering does not run the suite.
        def comparable(text):return '\n'.join(line for line in text.splitlines() if not line.startswith('Automated suite'))
        self.assertEqual(comparable(committed),comparable(regenerated))
        for text in (committed,regenerated):
            self.assertNotIn('known unpaid',text)
            self.assertNotIn('Paid days / no orders',text)
            self.assertIn('Days with spend and zero attributed orders',text)
            self.assertIn('missing attribution or prior paid exposure',text)
            self.assertIn('Organic does not imply zero acquisition cost',text)
            self.assertIn('distinct sessions with at least one valid order',text)


if __name__=='__main__':unittest.main()
