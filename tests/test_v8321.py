import unittest
import time
from unittest.mock import patch
import app

class LiveSelectionTests(unittest.TestCase):
    def test_candidates_prioritized_over_watch(self):
        now=time.time()
        d={'positions':[{'symbol':'MSFT'}], 'watch':['AAPL']*40, 'scan_results':{'NVDA':{'symbol':'NVDA','price':100,'score':85,'mom':2,'seen':now,'candle_ts':now,'risk':'Niedrig'}}}
        with patch.object(app,'product_is_allowed',return_value=True):
            self.assertEqual(app.select_live_symbols(d)[:3],['MSFT','NVDA','AAPL'])

    def test_stale_candidates_rejected(self):
        now=time.time()
        self.assertFalse(app.live_candidate({'price':100,'score':85,'mom':2,'seen':now-2000,'candle_ts':now}))

    def test_daily_realized_loss_limit(self):
        day=app.berlin_now().strftime('%d.%m.%Y')
        d={'cash':485,'positions':[],'history':[{'time':day+' 16:00','pnl':-15}]}
        self.assertEqual(app.daily_risk(d),(-15,15))
        self.assertTrue(app.daily_buy_blocked(d))
        d['history']=[]
        self.assertFalse(app.daily_buy_blocked(d))

if __name__=='__main__':unittest.main()
