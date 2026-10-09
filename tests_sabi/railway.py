"""CI simulation of Railway env vars; never calls Railway or deploys a service there."""
import json,os,pathlib,secrets,subprocess,time,urllib.error,urllib.parse,urllib.request

CONTAINER='sabi-ray-railway-ci'
VOLUME='sabi-ray-railway-ci-state'
HOST='sabi-ci.up.railway.app'
BASE='http://127.0.0.1:18083'
PASSWORD='Ci-Railway-'+secrets.token_hex(20)+'-Aa99!'

def docker(*args,**kwargs):
    return subprocess.run(['docker',*args],check=True,**kwargs)

def request(method,path,body=None,token=None,form=False):
    headers={'Accept':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    if body is None:data=None
    elif form:
        data=urllib.parse.urlencode(body).encode();headers['Content-Type']='application/x-www-form-urlencoded'
    else:
        data=json.dumps(body).encode();headers['Content-Type']='application/json'
    with urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,method=method,headers=headers),timeout=10) as response:
        return json.load(response)

def run_container(initial):
    env=os.environ.copy()
    args=['run','-d','--name',CONTAINER,'-p','127.0.0.1:18083:8080','-v',VOLUME+':/var/lib/pasarguard',
          '-e','DEPLOY_MODE=railway','-e','RAILWAY_ENVIRONMENT_ID=ci-simulation-only',
          '-e','RAILWAY_PUBLIC_DOMAIN='+HOST,'-e','SABI_ADMIN_USER=owner',
          '-e','SABI_PROFILES=vless-ws,trojan-ws,vmess-ws','-e','SABI_ADVANCED=']
    if initial:
        env['SABI_INITIAL_PASSWORD']=PASSWORD
        args+=['-e','SABI_INITIAL_PASSWORD','-e','RAILWAY_APPROVAL_CONFIRMED=false']
    args+=['sabi-ray:test']
    docker(*args,env=env,stdout=subprocess.DEVNULL)

def wait_ready():
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        result=subprocess.run(['docker','inspect','--format','{{.State.Running}}',CONTAINER],text=True,capture_output=True)
        if result.returncode or result.stdout.strip()!='true':raise RuntimeError('Container exited before readiness')
        try:
            if request('GET','/healthz')['status']=='ready':return
        except (OSError,ValueError):pass
        time.sleep(2)
    raise TimeoutError('Readiness timeout')

def login():return request('POST','/api/admin/token',{'username':'owner','password':PASSWORD},form=True)['access_token']

def sanitized_logs():
    result=subprocess.run(['docker','logs','--tail','1000',CONTAINER],capture_output=True,text=True)
    import re
    text=(result.stdout+result.stderr).replace(PASSWORD,'[REDACTED]')
    text=re.sub(r'/sub/[^\s"<>]+','/sub/[REDACTED]',text)
    text=re.sub(r'(?i)(bearer|apikey)\s+[^\s]+',r'\1 [REDACTED]',text)
    return text

def main():
    try:
        docker('volume','create',VOLUME,stdout=subprocess.DEVNULL)
        run_container(True);wait_ready();token=login()
        groups=request('GET','/api/groups',token=token)
        groups=groups if isinstance(groups,list) else groups['groups']
        group=next(x for x in groups if x['name']=='sabi-ray-all')
        user=request('POST','/api/user',{'username':'railway_ci_user','status':'active','group_ids':[group['id']],
            'data_limit':1048576,'expire':int(time.time())+86400},token)
        assert user['username']=='railway_ci_user'
        before=docker('exec',CONTAINER,'cat','/var/lib/pasarguard/sabi-installation.json',capture_output=True).stdout
        assert json.loads(before)['domain']==HOST
        # Assert local code warning, not provider approval and not the original exit message.
        logs=sanitized_logs()
        assert '[SABI-RAY] WARNING: Railway deployment detected.' in logs
        assert 'Startup stopped: Railway prohibits' not in logs
        docker('rm','-f',CONTAINER,stdout=subprocess.DEVNULL)
        # New container, same volume; neither initial password nor obsolete flag present.
        run_container(False);wait_ready();token=login()
        assert request('GET','/api/user/railway_ci_user',token=token)['username']=='railway_ci_user'
        after=docker('exec',CONTAINER,'cat','/var/lib/pasarguard/sabi-installation.json',capture_output=True).stdout
        assert before==after,'Installation state changed on recreate'
        print('PASS: simulated Railway startup with legacy flag=false; public-domain fallback; owner/user; recreate without password/flag; unchanged persistent state.')
        print('NOT TESTED: actual Railway deployment, TLS edge, provider permission or real ISP connectivity.')
    except Exception as error:
        print('Railway simulation failed:',type(error).__name__)
        print('\n'.join(sanitized_logs().splitlines()[-60:]))
        raise SystemExit(1)
    finally:
        subprocess.run(['docker','rm','-f',CONTAINER],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['docker','volume','rm',VOLUME],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

if __name__=='__main__':main()
