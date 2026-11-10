import io
import unittest
import urllib.error
from unittest.mock import patch
import app

class QuotaCircuitTests(unittest.TestCase):
    def setUp(self):
        self.url_patch=patch.object(app,'SUPABASE_URL','https://example.invalid')
        self.url_patch.start()
        self.old=app.REMOTE_QUOTA_UNTIL
        app.REMOTE_QUOTA_UNTIL=0.
    def tearDown(self):
        app.REMOTE_QUOTA_UNTIL=self.old
        self.url_patch.stop()
    def test_402_pauses_requests(self):
        exc=urllib.error.HTTPError('https://example.invalid',402,'quota',{},io.BytesIO(b''))
        with patch.object(app.urllib.request,'urlopen',side_effect=exc) as req:
            with self.assertRaisesRegex(RuntimeError,'402'):app.remote_request('GET')
            with self.assertRaisesRegex(RuntimeError,'402'):app.remote_request('GET')
            self.assertEqual(req.call_count,1)
    def test_retry_after_pause(self):
        exc=urllib.error.HTTPError('https://example.invalid',402,'quota',{},io.BytesIO(b''))
        with patch.object(app.urllib.request,'urlopen',side_effect=[exc,io.BytesIO(b'[]')]) as req:
            with self.assertRaises(RuntimeError):app.remote_request('GET')
            app.REMOTE_QUOTA_UNTIL=0.
            self.assertEqual(app.remote_request('GET'),[])
            self.assertEqual(req.call_count,2)
    def test_closed_market_skips_auto(self):
        # run_auto_check must not be invoked when exchange is closed.
        with patch.object(app,'in_auto_window',return_value=False):
            self.assertFalse(app.in_auto_window())

if __name__=='__main__':unittest.main()
