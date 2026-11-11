import copy
import time
import unittest
from unittest.mock import patch
import app

class PaperRiskTests(unittest.TestCase):
    def test_future_cannot_be_bought(self):
        d=copy.deepcopy(app.DEFAULT)
        d['cash']=500
        self.assertFalse(app.product_is_allowed('MNQ1!',d))
        with self.assertRaises(ValueError): app.execute_buy(d,'MNQ1!',20000,50)
        self.assertEqual(d['cash'],500)
        self.assertEqual(d['positions'],[])

    def test_seven_percent_does_not_force_sale(self):
        d=copy.deepcopy(app.DEFAULT)
        d['cash']=0
        d['positions']=[{'symbol':'AAPL','entry':100,'peak_price':107,'qty':1,'cost':100,'auto_manage':True,'source':'Automatik'}]
        now=time.time()
        quote={'symbol':'AAPL','price':107,'seen':now,'candle_ts':now,'score':80}
        with patch.object(app,'product_is_allowed',return_value=True):
            _,rows=app.portfolio(d,[quote])
        self.assertNotEqual(rows[0]['decision'],'VERKAUFEN')
        self.assertEqual(d['positions'][0]['peak_price'],107)

    def test_trailing_stop_recommends_sale(self):
        d=copy.deepcopy(app.DEFAULT)
        d['positions']=[{'symbol':'AAPL','entry':100,'peak_price':110,'qty':1,'cost':100,'auto_manage':True,'source':'Automatik'}]
        now=time.time()
        quote={'symbol':'AAPL','price':106,'seen':now,'candle_ts':now,'score':80}
        with patch.object(app,'product_is_allowed',return_value=True):
            _,rows=app.portfolio(d,[quote])
        self.assertEqual(rows[0]['decision'],'VERKAUFEN')
        self.assertIn('Gewinnsicherung',rows[0]['reason'])

if __name__=='__main__':unittest.main()
