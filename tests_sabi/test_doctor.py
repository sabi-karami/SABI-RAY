import json,pathlib,tempfile,unittest
from unittest.mock import patch
from sabi_ray.doctor import report
class DoctorTests(unittest.TestCase):
    def test_empty(self):
        with tempfile.TemporaryDirectory() as d:self.assertFalse(report(d)['state_readable'])
    def test_corrupt(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d)/'sabi-installation.json').write_text('nope');self.assertFalse(report(d)['state_readable'])
    def test_no_keys_or_domains(self):
        with tempfile.TemporaryDirectory() as d,patch('sabi_ray.doctor.socket.create_connection',side_effect=OSError):
            (pathlib.Path(d)/'sabi-installation.json').write_text(json.dumps({'domain':'private.example.com','installation_id':'secret-id','control_only':False,'profiles':['vless-ws']}))
            text=json.dumps(report(d));self.assertNotIn('private.example.com',text);self.assertNotIn('secret-id',text)
    def test_no_raw_database_error(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d)/'db.sqlite3').write_text('secret-corrupted-file');self.assertEqual(report(d)['database'],'unavailable')
