import io,json,os,pathlib,sqlite3,tempfile,unittest
from unittest.mock import patch
from sabi_ray import runtime,health
from sabi_ray.backup import backup

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)
        self.env=patch.dict(os.environ,{'PUBLIC_DOMAIN':'panel.example.com','DEPLOY_MODE':'docker','SABI_PROFILES':'vless-ws,trojan-ws','SABI_INITIAL_PASSWORD':'Temporary-Test-Only-123!'},clear=True)
        self.env.start();self.data=patch.object(runtime,'DATA',self.path);self.data.start()
    def tearDown(self):self.data.stop();self.env.stop();self.tmp.cleanup()
    def test_wait_node_registration(self):
        with patch.object(runtime,'must',side_effect=[{'status':'connecting'},{'status':'connected'}]) as call,patch.object(runtime.time,'sleep'):
            runtime.wait_node_connected(1,'synthetic-token');self.assertEqual(call.call_count,2)
    def test_wait_node_timeout(self):
        with self.assertRaises(TimeoutError):runtime.wait_node_connected(1,'synthetic-token',timeout=0)
    def test_first_install_state(self):
        s,_=runtime.preflight();self.assertEqual(len(s['installation_id']),32)
    def test_stable_id(self):
        a,_=runtime.preflight();b,_=runtime.preflight();self.assertEqual(a,b)
    def test_no_password_in_state(self):
        runtime.preflight();self.assertNotIn(os.environ['SABI_INITIAL_PASSWORD'],(self.path/'sabi-installation.json').read_text())
    def test_state_file_permissions(self):
        runtime.preflight();self.assertEqual((self.path/'sabi-installation.json').stat().st_mode&0o777,0o600)
    def test_refuse_silent_domain_change(self):
        runtime.preflight();os.environ['PUBLIC_DOMAIN']='other.example.com'
        with self.assertRaises(ValueError):runtime.preflight()
    def test_refuse_silent_profile_change(self):
        runtime.preflight();os.environ['SABI_PROFILES']='vmess-ws'
        with self.assertRaises(ValueError):runtime.preflight()
    def test_railway_warns_without_blocking(self):
        os.environ['DEPLOY_MODE']='railway'
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO) as log:
            state,_=runtime.preflight()
        self.assertIn('WARNING',log.getvalue())
        self.assertEqual(state['domain'],'panel.example.com')
        self.assertNotIn('RAILWAY_APPROVAL_CONFIRMED',os.environ)
    def test_detect_actual_railway_warns(self):
        os.environ['RAILWAY_ENVIRONMENT_ID']='example'
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO) as log:
            runtime.preflight()
        self.assertIn('Railway deployment detected',log.getvalue())
    def test_legacy_railway_acknowledgement_is_ignored(self):
        os.environ['DEPLOY_MODE']='railway'
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO) as log:
            for value in ['false','true','','not-a-boolean']:
                os.environ['RAILWAY_APPROVAL_CONFIRMED']=value
                state,_=runtime.preflight()
                self.assertEqual(os.environ['RAILWAY_APPROVAL_CONFIRMED'],value)
                self.assertNotIn('approval',json.dumps(state).lower())
        self.assertEqual(log.getvalue().count('Railway deployment detected'),4)
    def test_railway_restart_preserves_state_without_initial_password(self):
        os.environ['DEPLOY_MODE']='railway'
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO):
            runtime.preflight()
            before=(self.path/'sabi-installation.json').read_bytes()
            os.environ.pop('SABI_INITIAL_PASSWORD')
            runtime.preflight()
        self.assertEqual(before,(self.path/'sabi-installation.json').read_bytes())
    def test_railway_public_domain_fallback(self):
        os.environ['DEPLOY_MODE']='railway'
        os.environ['RAILWAY_PUBLIC_DOMAIN']='sabi-test.up.railway.app'
        os.environ.pop('PUBLIC_DOMAIN')
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO):state,_=runtime.preflight()
        self.assertEqual(state['domain'],'sabi-test.up.railway.app')
    def test_railway_still_requires_initial_password(self):
        os.environ['DEPLOY_MODE']='railway';os.environ.pop('SABI_INITIAL_PASSWORD')
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO),self.assertRaises(ValueError):runtime.preflight()
        self.assertFalse((self.path/'sabi-installation.json').exists())
    def test_railway_still_rejects_invalid_domain(self):
        os.environ['DEPLOY_MODE']='railway';os.environ['PUBLIC_DOMAIN']='https://bad.example.com/path'
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO),self.assertRaises(ValueError):runtime.preflight()
    def test_railway_still_rejects_direct_profiles(self):
        os.environ.update(DEPLOY_MODE='railway',SABI_ADVANCED='reality',SABI_DIRECT_DOMAIN='direct.example.com',SABI_REALITY_TARGET='origin.example.com:443')
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO),self.assertRaisesRegex(ValueError,'Automatic direct profiles'):runtime.preflight()
    def test_non_railway_has_no_policy_warning(self):
        with patch.object(runtime.sys,'stderr',new_callable=io.StringIO) as log:runtime.preflight()
        self.assertEqual(log.getvalue(),'')
    def test_unknown_mode(self):
        os.environ['DEPLOY_MODE']='magic'
        with self.assertRaises(ValueError):runtime.preflight()
    def test_restart_does_not_recreate_owner(self):
        (self.path/'sabi-ready.json').write_text('{}')
        with patch.object(runtime,'must') as request:
            runtime.setup({},[]);request.assert_not_called()
    def test_restart_without_initial_password(self):
        runtime.preflight();os.environ.pop('SABI_INITIAL_PASSWORD');runtime.preflight()
    def test_missing_initial_password(self):
        os.environ.pop('SABI_INITIAL_PASSWORD')
        with self.assertRaises(ValueError):runtime.preflight()
    def test_health_missing_setup(self):
        with patch.dict(os.environ,{'SABI_DATA_DIR':str(self.path)}):self.assertFalse(health.ready())
    def test_health_corrupt_state(self):
        (self.path/'sabi-ready.json').write_text('{}');(self.path/'sabi-installation.json').write_text('bad')
        with patch.dict(os.environ,{'SABI_DATA_DIR':str(self.path)}):self.assertFalse(health.ready())
    def test_sqlite_backup(self):
        source=self.path/'source.sqlite';dest=self.path/'backup.sqlite'
        with sqlite3.connect(source) as db:db.execute('CREATE TABLE t (n)');db.execute('INSERT INTO t VALUES (42)')
        backup(source,dest)
        with sqlite3.connect(dest) as db:self.assertEqual(db.execute('SELECT n FROM t').fetchone()[0],42)
        self.assertEqual(dest.stat().st_mode&0o777,0o600)
    def test_backup_refuses_overwrite(self):
        s=self.path/'s';d=self.path/'d';s.touch();d.touch()
        with self.assertRaises(ValueError):backup(s,d)
    def test_backup_refuses_missing_source(self):
        with self.assertRaises(FileNotFoundError):backup(self.path/'missing',self.path/'b')
if __name__=='__main__':unittest.main()
