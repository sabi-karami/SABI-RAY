"""Optional direct-TCP profiles. Credentials generated only on the deployment host."""
import base64
import os
import pathlib
import re
import secrets
from .profiles import domain

PORTS = {'reality':11443, 'shadowsocks':11444}

def options(env, control_only=False):
    names=[x.strip() for x in env.get('SABI_ADVANCED','').split(',') if x.strip()]
    if len(set(names))!=len(names) or set(names)-PORTS.keys():
        raise ValueError('SABI_ADVANCED supports unique reality,shadowsocks entries')
    if not names:return {}
    if control_only:raise ValueError('Direct profiles cannot be enabled in control-only mode')
    if env.get('DEPLOY_MODE')=='railway' or env.get('RAILWAY_ENVIRONMENT_ID'):
        raise ValueError('Automatic direct profiles require VPS/Docker, not the Railway HTTP edge')
    result={'enabled':names,'address':domain(env.get('SABI_DIRECT_DOMAIN',''))}
    if 'reality' in names:
        target=env.get('SABI_REALITY_TARGET','')
        host,sep,port=target.rpartition(':')
        if not sep:host,port=target,'443'
        host=domain(host)
        if not port.isdecimal() or not 1<=int(port)<=65535:raise ValueError('Invalid REALITY target port')
        sni=domain(env.get('SABI_REALITY_SERVER_NAME') or host)
        if sni!=host:raise ValueError('Use the same REALITY target hostname and server name')
        if host==result['address']:raise ValueError('Use a distinct TLS origin; avoid REALITY forwarding loops')
        result.update(target=host+':'+str(int(port)),server_name=sni)
    return result

def ensure_keys(data):
    path=pathlib.Path(data)/'sabi-reality.json'
    if path.exists():
        import json
        state=json.loads(path.read_text())
        if any(not re.fullmatch(r'[A-Za-z0-9_-]{43}',state.get(k,'')) for k in ('private_key','public_key')) or not re.fullmatch(r'[a-f0-9]{16}',state.get('short_id','')):
            raise ValueError('Invalid stored REALITY keys; restore a backup, never silently rotate')
        return state
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    import json
    key=X25519PrivateKey.generate()
    def encode(raw):return base64.urlsafe_b64encode(raw).decode().rstrip('=')
    state={'private_key':encode(key.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())),
           'public_key':encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)), 'short_id':secrets.token_hex(8)}
    temp=path.with_suffix('.tmp')
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(state,f);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
    return state

def inbounds(config,keys=None):
    result=[]
    for name in config.get('enabled',[]):
        if name=='reality':
            if not keys:raise ValueError('REALITY keys required')
            result.append({'tag':'SR-VLESS-REALITY','listen':'0.0.0.0','port':PORTS[name],'protocol':'vless',
                'settings':{'clients':[],'decryption':'none','flow':'xtls-rprx-vision'},
                'streamSettings':{'network':'raw','security':'reality','realitySettings':{'show':False,'target':config['target'],'serverNames':[config['server_name']],
                   'privateKey':keys['private_key'],'shortIds':[keys['short_id']]}}})
        elif name=='shadowsocks':
            result.append({'tag':'SR-SHADOWSOCKS','listen':'0.0.0.0','port':PORTS[name],'protocol':'shadowsocks',
                'settings':{'clients':[],'method':'chacha20-ietf-poly1305','network':'tcp'},
                'streamSettings':{'network':'raw','security':'none'}})
    return result

def hosts(config):
    result=[]
    for index,name in enumerate(config.get('enabled',[]),101):
        common={'address':[config['address']],'port':PORTS[name],'priority':index,'is_disabled':False,'allowinsecure':False}
        if name=='reality':common.update(remark='SABI-RAY | VLESS REALITY Vision',inbound_tag='SR-VLESS-REALITY',security='reality',sni=[config['server_name']],fingerprint='chrome')
        else:common.update(remark='SABI-RAY | Shadowsocks TCP',inbound_tag='SR-SHADOWSOCKS',security='none')
        result.append(common)
    return result

def listener_ports(config):return [PORTS[name] for name in config.get('enabled',[])]
