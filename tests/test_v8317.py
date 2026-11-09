import unittest
import app

class TrailingExitTests(unittest.TestCase):
    def lot(self):
        return {'symbol':'NVDA','entry':100.,'peak_price':100.,'qty':1.,'cost':100.,'auto_manage':True}
    def test_no_fixed_take_profit(self):
        lots=[self.lot()]
        self.assertIsNone(app.trailing_exit(lots,107))
        self.assertEqual(lots[0]['peak_price'],107)
        self.assertIsNone(app.trailing_exit(lots,110))
    def test_trailing_exit_after_profit(self):
        lots=[self.lot()]
        app.trailing_exit(lots,110)
        self.assertIsNotNone(app.trailing_exit(lots,106.6))
    def test_strong_momentum_has_more_room(self):
        lots=[self.lot()]
        app.trailing_exit(lots,115)
        self.assertIsNone(app.trailing_exit(lots,111))
        self.assertIsNotNone(app.trailing_exit(lots,110.3))
    def test_stop_loss_stays(self):
        self.assertIsNotNone(app.trailing_exit([self.lot()],95))
    def test_peak_is_persisted_in_lot(self):
        lot=self.lot()
        app.trailing_exit([lot],112)
        self.assertEqual(lot['peak_price'],112)
        self.assertIsNone(app.trailing_exit([lot],110))
    def test_manual_lot_never_sold_by_auto(self):
        d={'cash':0.,'positions':[self.lot(),self.lot()],'history':[],'event_log':[]}
        d['positions'][0]['auto_manage']=False
        app.execute_sell(d,'NVDA',110,auto_only=True)
        self.assertEqual(len(d['positions']),1)
        self.assertFalse(d['positions'][0]['auto_manage'])

if __name__=='__main__':unittest.main()
