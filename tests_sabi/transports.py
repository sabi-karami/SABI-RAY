'''CI loopback transport test. Verifies data transfer, not external TLS or ISP ping.'''
import json,subprocess
CLIENT_SCRIPT=r'''
import json,sys,pathlib,tempfile,subprocess,time,urllib.request,os
from sabi_ray.profiles import PROFILES,route_path
payload=json.load(sys.stdin)
state=json.loads(pathlib.Path('/var/lib/pasarguard/sabi-installation.json').read_text())
results=[]
for profile in PROFILES:
    credential=payload['proxy_settings'][profile.protocol]
    if profile.protocol=='trojan':settings={'servers':[{'address':'127.0.0.1','port':8080,'password':credential['password']}]}
    else:
        user={'id':credential['id']}
        if profile.protocol=='vless':user['encryption']='none'
        else:user.update(security='auto',alterId=0)
        settings={'vnext':[{'address':'127.0.0.1','port':8080,'users':[user]}]}
    stream={'network':profile.transport,'security':'none'}
    key={'ws':'wsSettings','httpupgrade':'httpupgradeSettings','xhttp':'xhttpSettings'}[profile.transport]
    stream[key]={'path':route_path(profile,state['installation_id'])}
    if profile.transport=='xhttp':stream[key]['mode']='packet-up'
    config={'log':{'loglevel':'none'},'inbounds':[{'listen':'127.0.0.1','port':18081,'protocol':'http','settings':{}}],
            'outbounds':[{'protocol':profile.protocol,'settings':settings,'streamSettings':stream}]}
    fd,path=tempfile.mkstemp(suffix='.json');os.fchmod(fd,0o600)
    with os.fdopen(fd,'w') as f:json.dump(config,f)
    process=subprocess.Popen(['/usr/local/bin/xray','run','-config',path],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    good=False
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:18081'}))
        for attempt in range(8):
            if process.poll() is not None:break
            try:
                with opener.open('https://example.com/',timeout=12) as response:good=response.status==200 and b'Example Domain' in response.read(8192)
                if good:break
            except Exception:time.sleep(2)
        results.append({'profile':profile.key,'data_transfer':good})
    finally:
        process.terminate()
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        pathlib.Path(path).unlink(missing_ok=True)
print(json.dumps(results))
sys.exit(0 if all(i['data_transfer'] for i in results) else 1)
'''
def run_transport_tests(container,user):
    result=subprocess.run(['docker','exec','-i',container,'python','-c',CLIENT_SCRIPT],input=json.dumps({'proxy_settings':user['proxy_settings']}),text=True,capture_output=True,timeout=600)
    if result.returncode:
        try:print('Transport results:',json.loads(result.stdout))
        except Exception:print('Transport test process failed')
        raise RuntimeError('One or more loopback transport data-transfer tests failed')
    print('PASS loopback transport data transfer:',result.stdout.strip())
