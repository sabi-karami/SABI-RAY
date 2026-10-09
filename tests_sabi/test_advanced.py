import unittest,tempfile,pathlib,json,os
from unittest.mock import patch
from sabi_ray import advanced,runtime

class AdvancedTests(unittest.TestCase):
    def env(self):return {'DEPLOY_MODE':'vps','SABI_ADVANCED':'reality,shadowsocks','SABI_DIRECT_DOMAIN':'direct.example.com','SABI_REALITY_TARGET':'origin.example.com:443'}
    def test_disabled_default(self):self.assertEqual(advanced.options({}),{})
    def test_explicit_selection(self):self.assertEqual(advanced.options(self.env())['enabled'],['reality','shadowsocks'])
    def test_target_port(self):self.assertEqual(advanced.options(self.env())['target'],'origin.example.com:443')
    def test_default_target_port(self):
        env=self.env();env['SABI_REALITY_TARGET']='origin.example.com';self.assertEqual(advanced.options(env)['target'],'origin.example.com:443')
    def test_bad_selections(self):
        for selection in ['reality,reality','wireguard','hysteria2']:
            with self.subTest(selection=selection),self.assertRaises(ValueError):advanced.options({**self.env(),'SABI_ADVANCED':selection})
    def test_reject_railway(self):
        with self.assertRaises(ValueError):advanced.options({**self.env(),'DEPLOY_MODE':'railway'})
    def test_detect_railway(self):
        with self.assertRaises(ValueError):advanced.options({**self.env(),'RAILWAY_ENVIRONMENT_ID':'test'})
    def test_control_only(self):
        with self.assertRaises(ValueError):advanced.options(self.env(),True)
    def test_reject_forward_loop(self):
        with self.assertRaises(ValueError):advanced.options({**self.env(),'SABI_REALITY_TARGET':'direct.example.com:11443'})
    def test_reject_bad_port(self):
        for port in ['0','65536','abc','443;quit']:
            with self.subTest(port=port),self.assertRaises(ValueError):advanced.options({**self.env(),'SABI_REALITY_TARGET':'origin.example.com:'+port})
    def test_shadowsocks_without_target(self):self.assertEqual(advanced.options({'SABI_ADVANCED':'shadowsocks','SABI_DIRECT_DOMAIN':'direct.example.com'})['enabled'],['shadowsocks'])
    def test_reality_requires_key(self):
        with self.assertRaises(ValueError):advanced.inbounds(advanced.options(self.env()))
    def test_no_static_clients(self):
        config=advanced.options(self.env());keys={'private_key':'a'*43,'short_id':'ab'*8}
        self.assertTrue(all(x['settings']['clients']==[] for x in advanced.inbounds(config,keys)))
    def test_reality_flow(self):
        config=advanced.options(self.env());keys={'private_key':'a'*43,'short_id':'ab'*8}
        self.assertEqual(advanced.inbounds(config,keys)[0]['settings']['flow'],'xtls-rprx-vision')
    def test_ss_tcp_only(self):
        config=advanced.options(self.env());keys={'private_key':'a'*43,'short_id':'ab'*8}
        self.assertEqual(advanced.inbounds(config,keys)[1]['settings']['network'],'tcp')
    def test_host_ports(self):self.assertEqual([h['port'] for h in advanced.hosts(advanced.options(self.env()))],[11443,11444])
    def test_never_skip_certificate(self):self.assertTrue(all(not h['allowinsecure'] for h in advanced.hosts(advanced.options(self.env()))))
    def test_reality_host_inherits_security(self):self.assertEqual(advanced.hosts(advanced.options(self.env()))[0]['security'],'inbound_default')
    def test_listener_ports(self):self.assertEqual(advanced.listener_ports(advanced.options(self.env())),[11443,11444])
    def test_key_store_reject_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d)/'sabi-reality.json').write_text('{}')
            with self.assertRaises(ValueError):advanced.ensure_keys(d)
    def test_existing_install_backward_compatible(self):
        env={'PUBLIC_DOMAIN':'panel.example.com','SABI_INITIAL_PASSWORD':'Tmp-Example-Only-123!'}
        with tempfile.TemporaryDirectory() as d,patch.object(runtime,'DATA',pathlib.Path(d)),patch.dict(os.environ,env,clear=True):
            state,_=runtime.preflight();state.pop('advanced');state['version']=1
            runtime.atomic_json(pathlib.Path(d)/'sabi-installation.json',state)
            runtime.preflight()
    def test_refuse_unplanned_advanced_change(self):
        env={'PUBLIC_DOMAIN':'panel.example.com','SABI_INITIAL_PASSWORD':'Tmp-Example-Only-123!'}
        with tempfile.TemporaryDirectory() as d,patch.object(runtime,'DATA',pathlib.Path(d)),patch.dict(os.environ,env,clear=True):
            runtime.preflight();os.environ.update(self.env())
            with self.assertRaises(ValueError):runtime.preflight()
