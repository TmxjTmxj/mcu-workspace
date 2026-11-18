"""Loopback-only simulation control UI; runs actual Renode jobs."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,threading
from report import generate,ROOT
from workflow import check
from simulate import run
job={'busy':False,'result':None};lock=threading.Lock()
def worker(case,target):
    try:
        if not check(): raise RuntimeError('Rebuild STM32 firmware first')
        result=run(case,target); generate()
    except Exception as error:result={'status':'FAIL','reason':str(error)}
    with lock:job.update(busy=False,result=result)
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'logs'),**kwargs)
    def do_GET(self):
        if self.path=='/job':
            with lock: payload=json.dumps(job).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(payload)
        else:super().do_GET()
    def do_POST(self):
        if self.path!='/run': self.send_error(404);return
        if self.headers.get('Origin') not in (None,'http://127.0.0.1:8766','http://localhost:8766'):
            self.send_error(403);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<200:raise ValueError('Invalid request length')
            body=json.loads(self.rfile.read(length));case=body['case'];target=int(body['target'])
            if case not in ['normal','commands','sensor','overheat','stall','estop','wrong_pwm'] or not 2500<=target<=5000:raise ValueError('Invalid parameters')
            with lock:
                if job['busy']:self.send_error(409,'A simulation is running');return
                job.update(busy=True,result=None)
            threading.Thread(target=worker,args=(case,target),daemon=True).start()
            self.send_response(202);self.end_headers();self.wfile.write(b'RUNNING_REAL_STM32')
        except (ValueError,KeyError,TypeError): self.send_error(400)
if __name__=='__main__':
    generate();print('http://127.0.0.1:8766 — live job control, recorded results',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
