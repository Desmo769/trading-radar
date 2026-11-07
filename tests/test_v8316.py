import unittest
import app

class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.d={'cash':1000.0,'positions':[],'history':[],'event_log':[],'names':{},'verified_stocks':['NVDA'],'weak_trend_checks':{}}
    def test_manual_buy_protected(self):
        app.execute_buy(self.d,'NVDA',100,100,'Manuell')
        self.assertFalse(self.d['positions'][0]['auto_manage'])
        with self.assertRaises(ValueError):
            app.execute_sell(self.d,'NVDA',101,auto_only=True)
        self.assertEqual(len(self.d['positions']),1)
    def test_automatic_only_sells_automatic_lot(self):
        app.execute_buy(self.d,'NVDA',100,100,'Manuell')
        app.execute_buy(self.d,'NVDA',100,100,'Automatik')
        app.execute_sell(self.d,'NVDA',105,auto_only=True)
        self.assertEqual(len(self.d['positions']),1)
        self.assertFalse(self.d['positions'][0]['auto_manage'])
    def test_manual_sale_still_possible(self):
        app.execute_buy(self.d,'NVDA',100,100,'Manuell')
        app.execute_sell(self.d,'NVDA',105)
        self.assertEqual(self.d['positions'],[])
    def test_invalid_buy_price_rejected(self):
        with self.assertRaises(ValueError):
            app.execute_buy(self.d,'NVDA',0,100,'Manuell')

if __name__=='__main__':
    unittest.main()
