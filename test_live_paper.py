import copy
import time
import unittest
from unittest.mock import patch
import app

class LivePaperTests(unittest.TestCase):
    def setUp(self):
        self.now=time.time()
        self.data=copy.deepcopy(app.DEFAULT)
        self.data.update(auto=True,cash=1000.0,budget=1000.0,per_trade=100.0,
                         positions=[],scan_results={})
        self.saved=[]
        app.LIVE_QUOTES.clear()
        app.LIVE_PEAKS.clear()
        app.LIVE_SAMPLES.clear()
        app.LIVE_LAST_ACTION.clear()
        app.LIVE_LAST_TICK.clear()
        app.LIVE_STATUS.update(connected=True)
        self.patches=[
            patch.object(app,'in_auto_window',return_value=True),
            patch.object(app,'load',side_effect=lambda:self.data),
            patch.object(app,'save',side_effect=lambda d:self.saved.append(copy.deepcopy(d))),
        ]
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
    def tick(self,price,symbol='AAPL',seconds=0):
        app.LIVE_QUOTES[symbol]={'price':price,'seen':time.time()+seconds}
        app.live_paper_step()
    def hold(self,entry=100.0):
        self.data['positions']=[{'symbol':'AAPL','entry':entry,'peak_price':entry,'qty':1.0,'cost':entry}]
        self.data['cash']=900.0
    def test_stop_loss(self):
        self.hold()
        self.tick(95.0)
        self.assertEqual(self.data['positions'],[])
        self.assertAlmostEqual(self.data['cash'],995.0)
        self.assertEqual(len(self.saved),1)
    def test_profit_runs_until_trailing_stop(self):
        self.hold()
        self.tick(108.0)
        self.assertEqual(len(self.data['positions']),1)
        self.assertEqual(self.data['positions'][0]['peak_price'],108.0)
        self.tick(104.0,seconds=1)
        self.assertEqual(self.data['positions'],[])
    def test_no_trade_on_disconnected(self):
        self.hold()
        app.LIVE_STATUS['connected']=False
        self.tick(90.0)
        self.assertEqual(len(self.data['positions']),1)
    def test_no_trade_on_stale(self):
        self.hold()
        app.LIVE_QUOTES['AAPL']={'price':90.0,'seen':time.time()-50}
        app.live_paper_step()
        self.assertEqual(len(self.data['positions']),1)
    def test_duplicate_tick_not_processed_twice(self):
        self.hold()
        self.tick(100.0)
        self.assertEqual(len(self.saved),0)
        self.tick(100.0,seconds=0)
        self.assertEqual(len(self.saved),0)
    def test_no_buy_on_stale_scanner(self):
        self.data['scan_results']['AAPL']={'price':100,'seen':time.time()-2000,'candle_ts':time.time()-2000,'score':95,'mom':2}
        self.tick(100)
        self.assertEqual(self.data['positions'],[])
    def test_no_buy_on_missing_score(self):
        self.data['scan_results']['AAPL']={'price':100,'seen':time.time(),'candle_ts':time.time(),'mom':2}
        self.tick(100)
        self.assertEqual(self.data['positions'],[])
    def test_live_view_stale_filter(self):
        app.LIVE_QUOTES['AAPL']={'price':100,'seen':time.time()-120}
        self.assertNotIn('AAPL',app.live_view()['quotes'])

if __name__=='__main__':
    unittest.main()
