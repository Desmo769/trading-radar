import copy
import unittest
from unittest.mock import patch
import app

class SupabaseBandwidthTests(unittest.TestCase):
    def setUp(self):
        self.saved=copy.deepcopy(app.REMOTE_CACHE)
        app.REMOTE_CACHE.update(data=None,read_at=0)
        self.remote=patch.object(app,'REMOTE_ENABLED',True)
        self.remote.start()
    def tearDown(self):
        self.remote.stop()
        app.REMOTE_CACHE.clear()
        app.REMOTE_CACHE.update(self.saved)
    def test_repeated_load_uses_cache(self):
        d=copy.deepcopy(app.DEFAULT)
        with patch.object(app,'remote_request',return_value=[{'data':d}]) as request:
            a=app.load()
            b=app.load()
            self.assertEqual(request.call_count,1)
            self.assertIsNot(a,b)
    def test_unchanged_state_does_not_write(self):
        d=copy.deepcopy(app.DEFAULT)
        with patch.object(app,'remote_request',return_value=[{'data':d}]) as request:
            state=app.load()
            app.save(state)
            self.assertEqual(request.call_count,1)
    def test_changed_state_written_once(self):
        d=copy.deepcopy(app.DEFAULT)
        with patch.object(app,'remote_request',return_value=[{'data':d}]) as request:
            state=app.load()
            state['cash']+=1
            app.save(state)
            app.save(state)
            self.assertEqual([c.args[0] for c in request.call_args_list],['GET','POST'])
    def test_failed_read_never_creates_empty_portfolio(self):
        with patch.object(app,'remote_request',side_effect=RuntimeError('quota exceeded')):
            with self.assertRaises(RuntimeError):
                app.load()
            self.assertIsNone(app.REMOTE_CACHE['data'])
    def test_failed_write_does_not_poison_cache(self):
        d=copy.deepcopy(app.DEFAULT)
        def remote(method,payload=None):
            if method=='GET':return [{'data':d}]
            raise RuntimeError('quota exceeded')
        with patch.object(app,'remote_request',side_effect=remote):
            state=app.load()
            state['cash']+=1
            with self.assertRaises(RuntimeError):app.save(state)
            self.assertNotEqual(app.REMOTE_CACHE['data']['cash'],state['cash'])

if __name__=='__main__':unittest.main()
