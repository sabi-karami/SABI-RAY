'''CI-only integration test. Synthetic credentials stay in process environment.'''
import json,os,secrets,subprocess,time,urllib.error,urllib.parse,urllib.request
password='Ci-'+secrets.token_hex(20)+'-Aa9!'
container='sabi-ray-ci'

def docker(*args,**kw):return subprocess.run(['docker',*args],check=True,**kw)
def req(method,path,body=None,token=None,form=False):
    headers={'Accept':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    if body is None:data=None
    elif form:headers['Content-Type']='application/x-www-form-urlencoded';data=urllib.parse.urlencode(body).encode()
    else:headers['Content-Type']='application/json';data=json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:18080'+path,data=data,method=method,headers=headers),timeout=20) as response:
        raw=response.read()
        return json.loads(raw) if 'application/json' in response.headers.get('Content-Type','') and raw else raw

def wait_ready():
    for i in range(180):
        try:
            if req('GET','/healthz')['status']=='ready':return
        except Exception:pass
        time.sleep(2)
    raise RuntimeError('Readiness did not become healthy')

try:
    env=os.environ.copy();env['SABI_INITIAL_PASSWORD']=password
    docker('run','-d','--name',container,'-p','127.0.0.1:18080:8080','-e','PUBLIC_DOMAIN=panel.example.test','-e','SABI_ADMIN_USER=owner','-e','SABI_INITIAL_PASSWORD','-e','SABI_PROFILES=vless-ws,trojan-ws,vmess-ws,vless-upgrade,vless-xhttp','sabi-ray:test',env=env,stdout=subprocess.DEVNULL)
    wait_ready()
    assert b'SABI-RAY' in req('GET','/dashboard/')
    token=req('POST','/api/admin/token',{'username':'owner','password':password},form=True)['access_token']
    cores=req('GET','/api/cores',token=token);cores=cores if isinstance(cores,list) else cores['cores'];assert any(c['name']=='SABI-RAY Core' for c in cores)
    groups=req('GET','/api/groups',token=token);groups=groups if isinstance(groups,list) else groups['groups'];gid=next(g['id'] for g in groups if g['name']=='sabi-ray-all')
    user=req('POST','/api/user',{'username':'sabi_ci_user','group_ids':[gid],'status':'active','data_limit':1024**3,'expire':int(time.time())+86400,'data_limit_reset_strategy':'no_reset'},token)
    assert user['username']=='sabi_ci_user'
    subpath=urllib.parse.urlsplit(user['subscription_url']).path
    assert subpath.startswith('/sub/')
    assert req('GET',subpath)
    from transports import run_transport_tests
    run_transport_tests(container,user)
    docker('restart',container,stdout=subprocess.DEVNULL)
    wait_ready()
    token=req('POST','/api/admin/token',{'username':'owner','password':password},form=True)['access_token']
    assert req('GET','/api/user/sabi_ci_user',token=token)['username']=='sabi_ci_user'
    settings=req('GET','/api/settings',token=token)
    assert settings['subscription']['profile_title']=='SABI-RAY'
    assert settings['subscription']['support_url']=='https://t.me/SAHEBKARAMI'
    from browser import run_browser
    run_browser('http://127.0.0.1:18080','owner',password)
    print('PASS: branded dashboard, readiness including 5 listeners, owner login, core/group, user/subscription, persisted restart.')
    print('NOT TESTED: external TLS edge, real ISP latency, advanced UDP/direct-TCP profiles.')
except Exception as error:
    # Error strings may include a subscription URL. Do not print request errors verbatim.
    print('Integration test failed:',type(error).__name__)
    result=subprocess.run(['docker','logs','--tail','120',container],capture_output=True,text=True)
    output=(result.stdout+result.stderr).replace(password,'[REDACTED]')
    # Subscription paths and keys must not end up in public CI logs.
    import re
    output=re.sub(r'/sub/[^\s"<>]+','/sub/[REDACTED]',output)
    output=re.sub(r'(?i)(bearer|apikey)\s+[^\s]+',r'\1 [REDACTED]',output)
    print(output)
    raise SystemExit(1)
finally:subprocess.run(['docker','rm','-f',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
