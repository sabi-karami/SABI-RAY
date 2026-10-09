'''Local readiness server. Does not expose credentials or internal error details.'''
from http.server import BaseHTTPRequestHandler, HTTPServer
import json,os,pathlib,socket,urllib.request,urllib.error
from .profiles import selected
from .advanced import listener_ports

def ready():
    data=pathlib.Path(os.getenv('SABI_DATA_DIR','/var/lib/pasarguard'))
    if not (data/'sabi-ready.json').exists():return False
    try:
        state=json.loads((data/'sabi-installation.json').read_text())
        try:
            with urllib.request.urlopen('http://127.0.0.1:8000/api/system',timeout=1) as r:code=r.status
        except urllib.error.HTTPError as e:code=e.code
        if code not in (200,401,403):return False
        ports=[] if state['control_only'] else [62050]+[p.port for p in selected(','.join(state['profiles']))]+listener_ports(state.get('advanced',{}))
        for port in ports:
            with socket.create_connection(('127.0.0.1',port),timeout=.3):pass
        return True
    except (OSError,ValueError,KeyError):return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/healthz':self.send_error(404);return
        good=ready();data=json.dumps({'status':'ready' if good else 'not_ready'}).encode()
        self.send_response(200 if good else 503);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def log_message(self,*args):pass
if __name__=='__main__':HTTPServer(('127.0.0.1',8001),Handler).serve_forever()
