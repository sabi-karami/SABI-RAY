import unittest
from sabi_ray.profiles import *

class ProfilesTests(unittest.TestCase):
    def setUp(self):self.identifier='ab'*16
    def test_unique_ports(self):self.assertEqual(len(PROFILES),len({p.port for p in PROFILES}))
    def test_unique_tags(self):self.assertEqual(len(PROFILES),len({i['tag'] for i in core_config(PROFILES,self.identifier)['inbounds']}))
    def test_protocol_diversity(self):self.assertEqual({p.protocol for p in PROFILES},{'vless','trojan','vmess'})
    def test_unknown_profile(self):
        with self.assertRaises(ValueError):selected('wireguard')
    def test_empty_profile(self):
        with self.assertRaises(ValueError):selected('')
    def test_duplicate_profile(self):
        with self.assertRaises(ValueError):selected('vless-ws,vless-ws')
    def test_order(self):self.assertEqual(selected('trojan-ws,vless-ws')[0].key,'trojan-ws')
    def test_domain(self):self.assertEqual(domain(' PANEL.Example.COM. '),'panel.example.com')
    def test_reject_domains(self):
        for value in ['https://example.com','example.com:443','a.com/x','a.com;','localhost','a.com\nlocation /','127.0.0.1','-x.com','a..com']:
            with self.subTest(value=value),self.assertRaises(ValueError):domain(value)
    def test_idn(self):self.assertTrue(domain('مثال.ایران').startswith('xn--'))
    def test_paths_stable(self):self.assertEqual(route_path(PROFILES[0],self.identifier),route_path(PROFILES[0],self.identifier))
    def test_paths_separate_installations(self):self.assertNotEqual(route_path(PROFILES[0],self.identifier),route_path(PROFILES[0],'cd'*16))
    def test_installation_path_injection(self):
        with self.assertRaises(ValueError):route_path(PROFILES[0],';evil')
    def test_private_listeners(self):self.assertTrue(all(i['listen']=='127.0.0.1' for i in core_config(PROFILES,self.identifier)['inbounds']))
    def test_no_seed_users(self):self.assertTrue(all(not i['settings']['clients'] for i in core_config(PROFILES,self.identifier)['inbounds']))
    def test_private_destinations_blocked(self):self.assertEqual(core_config(PROFILES,self.identifier)['routing']['rules'][0]['outboundTag'],'BLOCK')
    def test_host_tls(self):
        for p in PROFILES:
            host=host_config(p,'panel.example.com',self.identifier,1)
            self.assertFalse(host['allowinsecure']);self.assertEqual(host['security'],'tls')
    def test_nginx_paths_match(self):
        conf=nginx_config(PROFILES,self.identifier)
        for p in PROFILES:
            self.assertIn(route_path(p,self.identifier),conf)
            self.assertIn('127.0.0.1:'+str(p.port),conf)
    def test_xhttp_prefix(self):
        p=next(p for p in PROFILES if p.transport=='xhttp')
        self.assertTrue(route_path(p,self.identifier).endswith('/'))
        self.assertIn('location ^~ '+route_path(p,self.identifier),nginx_config(PROFILES,self.identifier))
    def test_weak_passwords(self):
        for value in ['admin','A'*30,'lowercasepassword1234','Uppercasepassword1234']:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_secret(value)
    def test_password_policy(self):self.assertTrue(validate_secret('Example-Test-only-99Ab!'))
    def test_base_password_policy(self):
        for value in ['Example-test-only-9Ab!', 'EXample-Only-11!'+('x'*80), 'EXample-Only-11!"']:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_secret(value)
    def test_health_not_static(self):self.assertIn('proxy_pass http://127.0.0.1:8001/healthz',nginx_config(PROFILES,self.identifier))
    def test_dynamic_port(self):self.assertIn('listen 8999;',nginx_config(PROFILES,self.identifier,8999))
    def test_port_injection(self):
        for port in ['8080;evil',80,99999]:
            with self.subTest(port=port),self.assertRaises(ValueError):nginx_config(PROFILES,self.identifier,port)
    def test_reality_requires_key(self):
        with self.assertRaises(ValueError):reality_template('example.com:443','example.com','placeholder','aabb')
    def test_reality_requires_matching_target(self):
        with self.assertRaises(ValueError):reality_template('other.com:443','example.com','a'*43,'aabb')
    def test_reality_direct_tcp(self):self.assertEqual(reality_template('example.com:443','example.com','a'*43,'aabb')['streamSettings']['network'],'raw')
    def test_reality_even_short_id(self):
        with self.assertRaises(ValueError):reality_template('example.com:443','example.com','a'*43,'abc')
if __name__=='__main__':unittest.main()
