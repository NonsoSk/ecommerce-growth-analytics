"""Guard against analytics/filter changes when adopting the user-validated layout."""
import copy
from pathlib import Path
import runpy
import unittest
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
contract=runpy.run_path(str(ROOT/'scripts/finalize_tableau_review.py'))['contract']
class AcceptedLayoutContract(unittest.TestCase):
 def setUp(self):self.root=E.parse(ROOT/'dashboard/templates/accepted_workbook.twb').getroot()
 def test_layout_changes_do_not_change_contract(self):
  changed=copy.deepcopy(self.root)
  changed.find('./dashboards/dashboard/zones/zone').set('x','123')
  self.assertEqual(contract(self.root),contract(changed))
 def test_formula_change_is_detected(self):
  changed=copy.deepcopy(self.root)
  changed.find('./datasources/datasource[@name="federated.overview"]/column/calculation').set('formula','0')
  self.assertNotEqual(contract(self.root),contract(changed))
 def test_filter_scope_change_is_detected(self):
  changed=copy.deepcopy(self.root)
  changed.find('.//worksheets/worksheet/table/view/filter').set('column','[wrong]')
  self.assertNotEqual(contract(self.root),contract(changed))
