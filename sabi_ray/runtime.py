'''Supervised SABI-RAY runtime. Secrets are never printed or included in diagnostics.'''
import json
import os
import pathlib
import secrets
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from .profiles import domain, selected, core_config, host_config, nginx_config, validate_secret

DATA = pathlib.Path(os.getenv('SABI_DATA_DIR','/var/lib/pasarguard'))
BASE = 'http://127.0.0.1:8000'


def atomic_json(path, data):
    path=pathlib.Path(path)
    temp=path.with_name(path.name+'.tmp')
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump(data,f);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)


def request(method,path,body=None,token=None,form=False):
    headers={'Accept':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    if body is None:data=None
    elif form:
        data=urllib.parse.urlencode(body).encode();headers['Content-Type']='application/x-www-form-urlencoded'
    else:
        data=json.dumps(body).encode();headers['Content-Type']='application/json'
    req=urllib.request.Request(BASE+path,data=data,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            raw=response.read()
            return response.status,json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        # Deliberately do not log response bodies: they may contain supplied credentials.
        return error.code,None


def must(method,path,body=None,token=None,form=False):
    code,data=request(method,path,body,token,form)
    if code not in (200,201,204):raise RuntimeError(f'API operation failed ({method} {path}, HTTP {code})')
    return data


def existing_or_create(list_path,key,name,create_path,body,token):
    data=must('GET',list_path,token=token)
    items=data if isinstance(data,list) else data.get(key,[])
    existing=next((i for i in items if i.get('name')==name),None)
    return existing or must('POST',create_path,body,token)


def setup(state,profiles):
    if (DATA/'sabi-ready.json').exists():
        return  # Never reset passwords or overwrite managed core settings on restart.
    user=os.getenv('SABI_ADMIN_USER','owner')
    password=validate_secret(os.environ.get('SABI_INITIAL_PASSWORD',''))
    # One-time key creation uses pinned upstream internals, never a password-hash bypass.
    script='''import asyncio,json
from app.db import GetDB
from app.db.crud.admin import get_owner
from app.db.crud.temp_key import create_temp_key
async def main():
    async with GetDB() as db:
        owner=await get_owner(db)
        if owner is not None: print('SABI_SETUP='+json.dumps({'exists':True}));return
        k=await create_temp_key(db)
        print('SABI_SETUP='+json.dumps({'exists':False,'key':k.key}))
asyncio.run(main())
'''
    result=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True,timeout=90,check=False)
    if result.returncode:raise RuntimeError('One-time owner setup failed; no secret-bearing output logged')
    lines=[line.removeprefix('SABI_SETUP=') for line in result.stdout.splitlines() if line.startswith('SABI_SETUP=')]
    if len(lines)!=1:raise RuntimeError('Unexpected one-time setup response')
    owner=json.loads(lines[0])
    if not owner['exists']:
        must('POST','/api/setup/owner',{'key':owner['key'],'username':user,'password':password})
    token=must('POST','/api/admin/token',{'username':user,'password':password},form=True)['access_token']
    if not state['control_only']:
        core=existing_or_create('/api/cores','cores','SABI-RAY Core','/api/core',{'name':'SABI-RAY Core','config':core_config(profiles,state['installation_id']),'exclude_inbound_tags':[],'fallbacks_inbound_tags':[]},token)
        node_body={'name':'SABI-RAY Local','address':'127.0.0.1','port':62050,'usage_coefficient':1,'connection_type':'grpc','server_ca':(DATA/'sabi-node/cert.pem').read_text(),'keep_alive':30,'core_config_id':core['id'],'api_key':(DATA/'sabi-node/api-key').read_text().strip()}
        existing_or_create('/api/nodes','nodes','SABI-RAY Local','/api/node',node_body,token)
        group=None
        for attempt in range(30):
            try:
                group=existing_or_create('/api/groups','groups','sabi-ray-all','/api/group',{'name':'sabi-ray-all','inbound_tags':['SR-'+p.key.upper() for p in profiles]},token)
                break
            except RuntimeError:
                if attempt==29:raise
                time.sleep(2)
        hosts=must('GET','/api/hosts',token=token)
        hosts=hosts if isinstance(hosts,list) else hosts.get('hosts',[])
        for number,p in enumerate(profiles,1):
            body=host_config(p,state['domain'],state['installation_id'],number)
            existing=[h for h in hosts if h.get('inbound_tag')==body['inbound_tag']]
            # Setup-only update configures upstream automatically created host records; no deletion.
            if existing:
                h=existing[0];must('PUT','/api/host/'+str(h['id']),{**body,'id':h['id']},token)
            else:must('POST','/api/host/',body,token)
        for gb,days in [(10,30),(30,30),(50,30),(100,30),(200,60)]:
            name=f'SABI-RAY {gb}GB / {days}d'
            existing_or_create('/api/user_templates','templates',name,'/api/user_template',{'name':name,'data_limit':gb*1024**3,'expire_duration':days*86400,'group_ids':[group['id']],'status':'active','data_limit_reset_strategy':'no_reset'},token)
    atomic_json(DATA/'sabi-ready.json',{'setup_complete':True,'version':1})
    print('[SABI-RAY] Initial setup complete. No demo accounts were created.',flush=True)


def preflight():
    DATA.mkdir(parents=True,exist_ok=True)
    mode=os.getenv('DEPLOY_MODE','docker')
    if mode not in {'docker','vps','railway'}:raise ValueError('Unknown DEPLOY_MODE')
    if (mode=='railway' or os.getenv('RAILWAY_ENVIRONMENT_ID')) and os.getenv('RAILWAY_APPROVAL_CONFIRMED')!='true':
        raise ValueError('Railway prohibits proxy/anonymization services. Obtain provider approval before deploying; see docs/RAILWAY.md.')
    host=domain(os.getenv('PUBLIC_DOMAIN') or os.getenv('RAILWAY_PUBLIC_DOMAIN') or '')
    profiles=selected(os.getenv('SABI_PROFILES','vless-ws,trojan-ws,vmess-ws'))
    control=os.getenv('SABI_CONTROL_ONLY','false')=='true'
    path=DATA/'sabi-installation.json'
    expected={'domain':host,'profiles':[p.key for p in profiles],'control_only':control}
    if path.exists():
        state=json.loads(path.read_text())
        if any(state.get(k)!=v for k,v in expected.items()):
            raise ValueError('Deployment settings changed. Back up data and follow docs/MIGRATION.md; refusing silent rewrite.')
    else:
        validate_secret(os.environ.get('SABI_INITIAL_PASSWORD',''))
        state={**expected,'installation_id':secrets.token_hex(16),'version':1}
        atomic_json(path,state)
    return state,profiles


def main():
    os.umask(0o077)
    state,profiles=preflight()
    active=[] if state['control_only'] else profiles
    subprocess.run([sys.executable,'-m','alembic','upgrade','head'],check=True)
    node_dir=DATA/'sabi-node';node_dir.mkdir(exist_ok=True)
    if not state['control_only']:
        key=node_dir/'api-key'
        if not key.exists():key.write_text(str(uuid.uuid4()));key.chmod(0o600)
        cert=node_dir/'cert.pem';priv=node_dir/'key.pem'
        if cert.exists()!=priv.exists():raise ValueError('Incomplete node certificate pair; restore backup')
        if not cert.exists():
            subprocess.run(['openssl','req','-x509','-newkey','ec','-pkeyopt','ec_paramgen_curve:prime256v1','-nodes','-days','365','-keyout',str(priv),'-out',str(cert),'-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['openssl','x509','-checkend','0','-noout','-in',str(cert)],check=True,stdout=subprocess.DEVNULL)
    pathlib.Path('/etc/nginx/nginx.conf').write_text(nginx_config(active,state['installation_id'],int(os.getenv('PORT','8080'))))
    subprocess.run(['nginx','-t'],check=True)
    children=[]
    env=os.environ.copy();env.pop('SABI_INITIAL_PASSWORD',None);env.pop('SUDO_USERNAME',None);env.pop('SUDO_PASSWORD',None)
    env.update(UVICORN_HOST='127.0.0.1',UVICORN_PORT='8000',UVICORN_PROXY_HEADERS='True',UVICORN_FORWARDED_ALLOW_IPS='127.0.0.1')
    def launch(args,extra=None):
        child=subprocess.Popen(args,env={**env,**(extra or {})});children.append(child);return child
    def shutdown(*_):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,shutdown);signal.signal(signal.SIGINT,shutdown)
    try:
        if not state['control_only']:
            launch(['/opt/sabi-node/main'],{'SERVICE_PORT':'62050','NODE_HOST':'127.0.0.1','SERVICE_PROTOCOL':'grpc','API_KEY':(node_dir/'api-key').read_text().strip(),'SSL_CERT_FILE':str(node_dir/'cert.pem'),'SSL_KEY_FILE':str(node_dir/'key.pem')})
        launch([sys.executable,'main.py'])
        launch([sys.executable,'-m','sabi_ray.health'])
        launch(['nginx','-g','daemon off;'])
        deadline=time.monotonic()+300
        while True:
            if any(c.poll() is not None for c in children):raise RuntimeError('A supervised process exited during startup')
            try:
                code,_=request('GET','/api/system')
                if code in (200,401,403):break
            except (OSError,ValueError):pass
            if time.monotonic()>deadline:raise TimeoutError('Panel startup timed out')
            time.sleep(2)
        setup(state,profiles)
        os.environ.pop('SABI_INITIAL_PASSWORD',None)
        print('[SABI-RAY] Processes supervised; health endpoint verifies configured listeners.',flush=True)
        while all(c.poll() is None for c in children):time.sleep(1)
        raise RuntimeError('A supervised process exited')
    finally:
        for child in children:
            if child.poll() is None:child.terminate()
        deadline=time.monotonic()+12
        for child in children:
            try:child.wait(timeout=max(.1,deadline-time.monotonic()))
            except subprocess.TimeoutExpired:child.kill();child.wait()

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:sys.exit(0)
    except Exception as error:
        print('[SABI-RAY] Startup stopped:',str(error),file=sys.stderr)
        sys.exit(1)
