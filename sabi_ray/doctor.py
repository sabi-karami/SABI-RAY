"""Read-only sanitized deployment diagnostics, safe by construction; no raw configuration."""
import json,os,pathlib,socket,sqlite3
from .advanced import listener_ports
from .profiles import selected

def report(data):
    data=pathlib.Path(data)
    result={'product':'SABI-RAY','state_readable':False,'setup_complete':(data/'sabi-ready.json').is_file(),'listeners':[],'database':'not_checked'}
    try:
        state=json.loads((data/'sabi-installation.json').read_text());result['state_readable']=True
        ports=[8000,8001]+([] if state['control_only'] else [62050]+[p.port for p in selected(','.join(state['profiles']))]+listener_ports(state.get('advanced',{})))
        for port in ports:
            try:
                with socket.create_connection(('127.0.0.1',port),timeout=.4):ok=True
            except OSError:ok=False
            result['listeners'].append({'port':port,'tcp_reachable':ok})
        result['profiles']=state['profiles']
        result['advanced_profiles']=state.get('advanced',{}).get('enabled',[])
    except (OSError,ValueError,KeyError):pass
    db=data/'db.sqlite3'
    if db.is_file():
        try:
            with sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True,timeout=2) as connection:
                result['database']='ok' if connection.execute('PRAGMA quick_check').fetchone()[0]=='ok' else 'check_failed'
        except sqlite3.Error:result['database']='unavailable'
    else:result['database']='no_local_sqlite_file'
    result['limits']='TCP reachability is not protocol connectivity, external TLS or an ISP latency measurement.'
    return result
if __name__=='__main__':print(json.dumps(report(os.getenv('SABI_DATA_DIR','/var/lib/pasarguard')),indent=2))
