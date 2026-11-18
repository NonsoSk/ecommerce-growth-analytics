"""Independent hand-calculated checks for dashboard aggregation semantics."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from ecommerce_growth.dashboard import totals,select,NUMBERS

def row(group,**values):return dict(dict.fromkeys(NUMBERS[group],0),**values)
class DashboardTests(unittest.TestCase):
 def test_conversion_counts_sessions_not_orders(self):
  result=totals([row('overview',sessions=2,converting_sessions=1,orders=3)],'overview')
  self.assertEqual(result['conversion_rate'],.5);self.assertEqual(result['orders'],3)
 def test_ratio_is_weighted(self):
  result=totals([row('overview',sessions=1,converting_sessions=1),row('overview',sessions=9,converting_sessions=0)],'overview')
  self.assertEqual(result['conversion_rate'],.1)
 def test_campaign_totals_and_cac(self):
  result=totals([row('acquisition',spend_cents=1000,net_revenue_cents=3000,first_observed_purchasers=2),row('acquisition',spend_cents=3000,net_revenue_cents=5000,first_observed_purchasers=0)],'acquisition')
  self.assertEqual(result['net_roas'],2);self.assertEqual(result['first_observed_paid_cac_proxy_cents'],2000)
 def test_zero_and_missing_denominators(self):
  self.assertIsNone(totals([row('overview')],'overview')['conversion_rate'])
  self.assertIsNone(totals([row('acquisition')],'acquisition')['net_roas'])
  self.assertIsNone(totals([row('acquisition',spend_cents=100,first_observed_purchasers=1,missing_spend_days=1)],'acquisition')['first_observed_paid_cac_proxy_cents'])
 def test_funnel_dropoffs(self):
  result=totals([row('funnel',sessions=10,session_starts=10,product_views=8,carts=4,checkouts=3,purchases=2)],'funnel')
  self.assertEqual(result['product_views_to_carts_dropoff'],4);self.assertEqual(result['product_views_to_carts_rate'],.5)
 def test_filter_bounds_and_scope(self):
  rows=[{'day':'2026-01-01','device':'mobile'},{'day':'2026-01-31','device':'mobile'},{'day':'2026-02-01','device':'mobile'}]
  self.assertEqual(len(select(rows,'funnel','2026-01-01','2026-01-31',device='mobile')),2)
  with self.assertRaises(ValueError):select(rows,'acquisition',device='mobile')
  with self.assertRaises(ValueError):select(rows,'overview',channel='google')
