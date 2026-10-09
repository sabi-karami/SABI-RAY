'''SABI-RAY protocol profiles. No credentials and no external side effects.'''
from dataclasses import dataclass
import ipaddress
import re

@dataclass(frozen=True)
class Profile:
    key: str
    protocol: str
    transport: str
    port: int
    title: str

PROFILES = (
    Profile('vless-ws', 'vless', 'ws', 11001, 'VLESS · WebSocket'),
    Profile('trojan-ws', 'trojan', 'ws', 11002, 'Trojan · WebSocket'),
    Profile('vmess-ws', 'vmess', 'ws', 11003, 'VMess · WebSocket'),
    Profile('vless-upgrade', 'vless', 'httpupgrade', 11004, 'VLESS · HTTPUpgrade'),
    Profile('vless-xhttp', 'vless', 'xhttp', 11005, 'VLESS · XHTTP'),
)
CATALOG = [
    {'name': p.title, 'protocol': p.protocol, 'transport': p.transport, 'integration': 'automatic', 'status': 'alpha: client/server integration testing required'} for p in PROFILES
] + [
    {'name': 'VLESS · REALITY · Vision', 'protocol': 'vless', 'transport': 'raw', 'integration': 'opt-in direct', 'requires': 'New VPS/Docker install; TCP 11443, authorized TLS target, compatible client', 'status': 'available via SABI_ADVANCED=reality; disabled by default'},
    {'name': 'Shadowsocks · TCP', 'protocol': 'shadowsocks', 'transport': 'tcp', 'integration': 'opt-in direct', 'requires': 'New VPS/Docker install, direct TCP 11444; not SS2022/UDP', 'status': 'available via SABI_ADVANCED=shadowsocks; disabled by default'},
    {'name': 'Hysteria2', 'protocol': 'hysteria2', 'transport': 'quic/udp', 'integration': 'upstream core editor', 'requires': 'Compatible node/core version, public UDP and TLS certificate', 'status': 'not automatically enabled'},
    {'name': 'WireGuard', 'protocol': 'wireguard', 'transport': 'udp', 'integration': 'upstream WireGuard node', 'requires': 'Separate capable node, public UDP, privileges/TUN as required', 'status': 'not automatically enabled'},
]

def domain(value: str) -> str:
    value = value.strip().rstrip('.').lower()
    try: value = value.encode('idna').decode('ascii')
    except UnicodeError as exc: raise ValueError('Invalid domain') from exc
    if len(value) > 253 or len(value.split('.')) < 2 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', part) for part in value.split('.')):
        raise ValueError('Use a domain name without scheme, port, path or whitespace')
    try: ipaddress.ip_address(value)
    except ValueError: return value
    raise ValueError('PUBLIC_DOMAIN must be a DNS name for TLS, not an IP')

def validate_secret(value: str) -> str:
    if len(value) < 16 or len(value.encode('utf-8')) > 72:
        raise ValueError('Initial password needs at least 16 characters and at most 72 UTF-8 bytes')
    if any(c in value for c in ['"', '\r', '\n', '\x00']):
        raise ValueError('Password cannot contain double quotes, line breaks or null bytes')
    if any(len(re.findall(pattern,value)) < 2 for pattern in (r'[A-Z]',r'[a-z]',r'\d')):
        raise ValueError('Password needs at least two uppercase, two lowercase letters and two digits')
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{}|;:,.<>?/~`]',value):
        raise ValueError('Password needs an accepted special character')
    return value


def selected(keys: str):
    requested=[k.strip() for k in keys.split(',') if k.strip()]
    if not requested or len(requested) != len(set(requested)): raise ValueError('Choose one or more unique profiles')
    known={p.key:p for p in PROFILES}
    unknown=set(requested)-known.keys()
    if unknown: raise ValueError('Unsupported automatic profiles: '+','.join(sorted(unknown)))
    return [known[k] for k in requested]

def route_path(p: Profile, installation_id: str) -> str:
    if not re.fullmatch(r'[a-f0-9]{32}',installation_id):raise ValueError('Invalid installation identifier')
    return '/connect/'+installation_id+'/'+p.key+('/' if p.transport=='xhttp' else '')

def core_config(profiles, installation_id):
    inbounds=[]
    for p in profiles:
        transport={'network':p.transport,'security':'none'}
        key={'ws':'wsSettings','httpupgrade':'httpupgradeSettings','xhttp':'xhttpSettings'}[p.transport]
        transport[key]={'path':route_path(p,installation_id)}
        if p.transport=='xhttp': transport[key]['mode']='packet-up'
        settings={'clients':[]}
        if p.protocol=='vless':settings['decryption']='none'
        inbounds.append({'tag':'SR-'+p.key.upper(),'listen':'127.0.0.1','port':p.port,'protocol':p.protocol,'settings':settings,'streamSettings':transport})
    return {'log':{'loglevel':'warning'},'inbounds':inbounds,
            'outbounds':[{'protocol':'freedom','tag':'DIRECT'},{'protocol':'blackhole','tag':'BLOCK'}],
            'routing':{'domainStrategy':'IPIfNonMatch','rules':[{'type':'field','ip':['geoip:private'],'outboundTag':'BLOCK'}]}}

def host_config(p, host, installation_id, priority):
    host=domain(host)
    result={'remark':'SABI-RAY | '+p.title,'inbound_tag':'SR-'+p.key.upper(),'address':[host],'port':443,
            'sni':[host],'host':[host],'path':route_path(p,installation_id),'security':'tls',
            'alpn':['http/1.1'],'fingerprint':'chrome','allowinsecure':False,'priority':priority,'is_disabled':False}
    if p.transport=='xhttp': result['transport_settings']={'xhttp_settings':{'mode':'packet-up'}}
    return result

def reality_template(target, server_name, private_key, short_id, port=1443):
    server_name=domain(server_name)
    if target != server_name+':443':raise ValueError('Use the same authorized domain on port 443')
    if not re.fullmatch(r'[A-Za-z0-9_-]{43}',private_key):raise ValueError('Expected generated X25519 private key')
    if not re.fullmatch(r'(?:[a-f0-9]{2}){1,8}',short_id):raise ValueError('Short ID must be even-length hexadecimal')
    if not isinstance(port,int) or not 1024 <= port <= 65535:raise ValueError('Use an unprivileged port')
    return {'tag':'SR-VLESS-REALITY','listen':'0.0.0.0','port':port,'protocol':'vless','settings':{'clients':[],'decryption':'none'},
            'streamSettings':{'network':'raw','security':'reality','realitySettings':{'show':False,'target':target,'serverNames':[server_name],'privateKey':private_key,'shortIds':[short_id]}}}

def nginx_config(profiles, installation_id, port=8080):
    if not isinstance(port,int) or not 1024 <= port <= 65535:raise ValueError('PORT must be between 1024 and 65535')
    locations=[]
    for p in profiles:
        path=route_path(p,installation_id)
        match=('^~ '+path) if p.transport=='xhttp' else ('= '+path)
        locations.append(f'''    location {match} {{
      proxy_pass http://127.0.0.1:{p.port};
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_buffering off; proxy_request_buffering off;
      proxy_read_timeout 3600s; proxy_send_timeout 3600s;
      client_max_body_size 16m;
    }}''')
    return '''user www-data;
worker_processes auto;
pid /run/nginx.pid;
events { worker_connections 4096; }
http {
  include /etc/nginx/mime.types;
  access_log off;
  error_log /dev/stderr warn;
  server_tokens off;
  map $http_upgrade $connection_upgrade { default upgrade; '' ''; }
  limit_req_zone $binary_remote_addr zone=auth:10m rate=30r/m;
  server {
    listen '''+str(port)+''';
    client_max_body_size 8m;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy no-referrer always;
    add_header X-Frame-Options SAMEORIGIN always;
    location = /healthz { proxy_pass http://127.0.0.1:8001/healthz; }
    location ~ ^/api/(admin/token|setup/owner)(/|$) {
      limit_req zone=auth burst=10 nodelay;
      limit_req_status 429;
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto https;
      proxy_set_header X-Forwarded-For $remote_addr;
    }
'''+ '\n'.join(locations)+'''
    location / {
      proxy_pass http://127.0.0.1:8000;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto https;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_read_timeout 300s;
    }
  }
}
'''
