"""Direct profiles tested against a local TLS target controlled by the CI job."""
import subprocess,json
SCRIPT=r"""
import json,sys,pathlib,tempfile,subprocess,time,urllib.request,os
payload=json.load(sys.stdin)
state=json.loads(pathlib.Path('/var/lib/pasarguard/sabi-installation.json').read_text())
keys=json.loads(pathlib.Path('/var/lib/pasarguard/sabi-reality.json').read_text())
from sabi_ray.advanced import ensure_keys
assert ensure_keys('/var/lib/pasarguard')==keys
assert (pathlib.Path('/var/lib/pasarguard/sabi-reality.json').stat().st_mode & 0o777)==0o600
proxies=payload['proxy_settings']
configs=[('reality',{'protocol':'vless','settings':{'vnext':[{'address':'127.0.0.1','port':11443,'users':[{'id':proxies['vless']['id'],'encryption':'none','flow':'xtls-rprx-vision'}]}]},
 'streamSettings':{'network':'raw','security':'reality','realitySettings':{'serverName':state['advanced']['server_name'],'fingerprint':'chrome','publicKey':keys['public_key'],'shortId':keys['short_id']}}}),
 ('shadowsocks',{'protocol':'shadowsocks','settings':{'servers':[{'address':'127.0.0.1','port':11444,'method':proxies['shadowsocks']['method'],'password':proxies['shadowsocks']['password']}]}})]
results=[]
for name,outbound in configs:
    config={'log':{'loglevel':'none'},'inbounds':[{'listen':'127.0.0.1','port':18082,'protocol':'http','settings':{}}],'outbounds':[outbound]}
    fd,path=tempfile.mkstemp(suffix=".json");os.fchmod(fd,0o600)
    with os.fdopen(fd,'w') as f:json.dump(config,f)
    check=subprocess.run(['/usr/local/bin/xray','run','-test','-config',path],capture_output=True,text=True)
    if check.returncode:
        message=(check.stdout+check.stderr)[-1200:]
        import re
        for item in [keys['private_key'],keys['public_key'],keys['short_id'],proxies['vless']['id'],proxies['shadowsocks']['password']]:message=message.replace(item,'[REDACTED]')
        print('Client config validation:',name,message,file=sys.stderr)
    p=subprocess.Popen(['/usr/local/bin/xray','run','-config',path],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ok=False
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:18082'}))
        for _ in range(10):
            if p.poll() is not None:break
            try:
                with opener.open('https://example.com/',timeout=12) as response:ok=response.status==200 and b'Example Domain' in response.read(8192)
                if ok:break
            except Exception:time.sleep(2)
    finally:
        p.terminate()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait()
        pathlib.Path(path).unlink(missing_ok=True)
    results.append({'profile':name,'data_transfer':ok})
print(json.dumps(results));sys.exit(0 if all(x['data_transfer'] for x in results) else 1)
"""
def run_direct(container,user):
    res=subprocess.run(['docker','exec','-i',container,'python','-c',SCRIPT],input=json.dumps({'proxy_settings':user['proxy_settings']}),capture_output=True,text=True,timeout=400)
    try:print('Direct profile results:',json.loads(res.stdout))
    except Exception:print('Direct profile test produced no structured result')
    if res.returncode:
        print(res.stderr[-1500:])
        raise RuntimeError('Direct profile transfer failed')
    print('PASS: REALITY/Vision and Shadowsocks TCP actual data transfer; locally controlled REALITY TLS target.')
