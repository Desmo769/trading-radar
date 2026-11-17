import unittest,time
from unittest.mock import patch
import app
class StrategyTests(unittest.TestCase):
    def test_filters(self):
        now=time.time()
        d={'scan_results':{'SPY':{'price':100,'seen':now,'candle_ts':now,'mom':0}}}
        self.assertTrue(app.strategy_gate(d,{'dollar_volume':1000000}))
        self.assertFalse(app.strategy_gate(d,{'dollar_volume':10}))
        d['scan_results']['SPY']['mom']=-1
        self.assertFalse(app.strategy_gate(d,{'dollar_volume':2000000}))
    def test_size(self):
        self.assertEqual(app.risk_amount({'per_trade':50},{'risk':'Mittel'}),25)
        self.assertEqual(app.risk_amount({'per_trade':80},{'risk':'Niedrig'}),50)
    def test_dynamic_stop(self):
        p={'entry':100,'cost':100,'qty':1,'stop_pct':2,'peak_price':100}
        self.assertIsNone(app.trailing_exit([p],99))
        self.assertTrue(app.trailing_exit([p],98))
    def test_costs(self):
        d={'cash':100,'positions':[],'history':[],'scan_results':{}}
        with patch.object(app,'product_is_allowed',return_value=True):
            app.execute_buy(d,'AAPL',100,50,'IEX Live-Signal')
            app.execute_sell(d,'AAPL',100,'IEX Live-Automatik')
        self.assertLess(d['cash'],100)
        self.assertAlmostEqual(d['cash'],99.85015,places=3)
        self.assertEqual(app.strategy_stats(d)['periods']['Tag']['n'],1)
    def test_learning(self):
        h={'time':app.berlin_now().strftime('%d.%m.%Y %H:%M'),'pnl':2,'strategy':'A'}
        s=app.strategy_stats({'history':[h]*100})
        self.assertEqual(s['periods']['Jahr']['net'],200)
        self.assertIn('Beste Gruppe',s['advice'])
