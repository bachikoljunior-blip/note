#!/usr/bin/env python3
"""Local-HTTP crash boundary acceptance test for optimizer evaluation dispatch.

The provider is a separate HTTP process with its own durable SQLite effect log.
The controller is a separate process with a durable pre-dispatch intent. Tests
cover controller death after provider commit/before response read, provider death
after commit/before response send, and pre-wire death. No network beyond loopback.
"""
from __future__ import annotations
import argparse,json,os,signal,sqlite3,subprocess,sys,tempfile,time,urllib.error,urllib.parse,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

CTRL='''
CREATE TABLE IF NOT EXISTS attempt(id TEXT PRIMARY KEY,state TEXT NOT NULL,incumbent TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS eval_intent(eval_id TEXT PRIMARY KEY,state TEXT NOT NULL,candidate TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS outcome(eval_id TEXT PRIMARY KEY,score REAL NOT NULL);
'''
PROV='''
CREATE TABLE IF NOT EXISTS effect(id INTEGER PRIMARY KEY AUTOINCREMENT,eval_id TEXT NOT NULL,candidate TEXT NOT NULL,score REAL NOT NULL);
CREATE TABLE IF NOT EXISTS call_log(id INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT NOT NULL,eval_id TEXT NOT NULL);
'''

def db(path):
 c=sqlite3.connect(path,timeout=30);c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL');return c
def init(ctrl,prov):
 c=db(ctrl);c.executescript(CTRL);c.commit();c.close();p=db(prov);p.executescript(PROV);p.commit();p.close()
def write_atomic(path,text):
 p=Path(path);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(text,encoding='utf-8');os.replace(tmp,p)
def wait_file(path,timeout=10):
 end=time.time()+timeout
 while time.time()<end:
  if Path(path).exists():return
  time.sleep(.01)
 raise TimeoutError(path)
def wait_proc_exit(proc,timeout=10):
 end=time.time()+timeout
 while time.time()<end:
  rc=proc.poll()
  if rc is not None:return rc
  time.sleep(.01)
 raise TimeoutError('process did not exit')

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def _json(self,code,obj):
  body=json.dumps(obj,sort_keys=True).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  q=urllib.parse.urlparse(self.path)
  if q.path!='/reconcile':self._json(404,{'error':'not-found'});return
  eid=urllib.parse.parse_qs(q.query).get('eval_id',[''])[0]
  p=db(self.server.prov);p.execute('INSERT INTO call_log(kind,eval_id) VALUES(?,?)',('reconcile',eid));p.commit()
  if self.server.mode=='neither':p.close();self._json(405,{'error':'unsupported'});return
  row=p.execute('SELECT score,candidate FROM effect WHERE eval_id=? ORDER BY id LIMIT 1',(eid,)).fetchone();p.close()
  if row is None:self._json(404,{'found':False})
  else:self._json(200,{'found':True,'score':row[0],'candidate':row[1]})
 def do_POST(self):
  if self.path!='/execute':self._json(404,{'error':'not-found'});return
  n=int(self.headers.get('Content-Length','0'));obj=json.loads(self.rfile.read(n));eid=obj['eval_id'];cand=obj['candidate']
  p=db(self.server.prov);p.execute('INSERT INTO call_log(kind,eval_id) VALUES(?,?)',('execute',eid))
  if self.server.mode=='reconcilable':
   row=p.execute('SELECT score FROM effect WHERE eval_id=? ORDER BY id LIMIT 1',(eid,)).fetchone()
   if row is None:score=.95;p.execute('INSERT INTO effect(eval_id,candidate,score) VALUES(?,?,?)',(eid,cand,score))
   else:score=row[0]
  else:
   score=.95;p.execute('INSERT INTO effect(eval_id,candidate,score) VALUES(?,?,?)',(eid,cand,score))
  p.commit();p.close();write_atomic(self.server.marker,'committed')
  if self.server.behavior=='crash_after_commit':os._exit(93)
  if self.server.behavior=='hold_after_commit':
   wait_file(self.server.release,timeout=20)
  try:self._json(200,{'score':score,'eval_id':eid})
  except (BrokenPipeError,ConnectionResetError):pass

def serve(prov,mode,behavior,marker,release,portfile):
 srv=ThreadingHTTPServer(('127.0.0.1',0),Handler);srv.prov=prov;srv.mode=mode;srv.behavior=behavior;srv.marker=marker;srv.release=release
 write_atomic(portfile,str(srv.server_address[1]));srv.serve_forever()
def get_json(url):
 try:
  with urllib.request.urlopen(url,timeout=5) as r:return r.status,json.loads(r.read())
 except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
def post_json(url,obj):
 b=json.dumps(obj,sort_keys=True).encode();req=urllib.request.Request(url,data=b,headers={'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=15) as r:return r.status,json.loads(r.read())

def controller(ctrl,base,mode,phase):
 c=db(ctrl);aid='attempt-1';eid='eval-transversal-v1';cand='transversal-v1'
 c.execute('INSERT OR IGNORE INTO attempt(id,state,incumbent) VALUES(?,?,?)',(aid,'RUNNING','direct-v1'));c.commit()
 done=c.execute('SELECT score FROM outcome WHERE eval_id=?',(eid,)).fetchone()
 state=c.execute('SELECT state FROM attempt WHERE id=?',(aid,)).fetchone()[0]
 if done is not None or state in ('COMPLETE','BLOCKED_UNKNOWN'):c.close();return state
 c.execute('INSERT OR IGNORE INTO eval_intent(eval_id,state,candidate) VALUES(?,?,?)',(eid,'INTENT',cand));c.commit()
 if phase=='prewire_kill':os.kill(os.getpid(),signal.SIGKILL)
 if phase=='resume' and mode=='neither':
  c.execute("UPDATE eval_intent SET state='UNKNOWN' WHERE eval_id=?",(eid,));c.execute("UPDATE attempt SET state='BLOCKED_UNKNOWN' WHERE id=?",(aid,));c.commit();c.close();return 'BLOCKED_UNKNOWN'
 score=None
 if mode=='reconcilable':
  code,obj=get_json(base+'/reconcile?eval_id='+urllib.parse.quote(eid))
  if code==200 and obj.get('found'):score=float(obj['score'])
 if score is None:
  c.execute("UPDATE eval_intent SET state='DISPATCHING' WHERE eval_id=?",(eid,));c.commit()
  _,obj=post_json(base+'/execute',{'eval_id':eid,'candidate':cand});score=float(obj['score'])
 if phase=='after_response_kill':os.kill(os.getpid(),signal.SIGKILL)
 c.execute('INSERT OR IGNORE INTO outcome(eval_id,score) VALUES(?,?)',(eid,score));c.execute("UPDATE eval_intent SET state='COMPLETE' WHERE eval_id=?",(eid,));c.execute("UPDATE attempt SET state='COMPLETE',incumbent=? WHERE id=?",(cand,aid));c.commit();c.close();return 'COMPLETE'

def inspect(ctrl,prov):
 c=db(ctrl);p=db(prov)
 a=c.execute('SELECT state,incumbent FROM attempt').fetchone();i=c.execute('SELECT eval_id,state FROM eval_intent').fetchall();o=c.execute('SELECT eval_id,score FROM outcome').fetchall();effects=p.execute('SELECT eval_id,candidate,score FROM effect ORDER BY id').fetchall();calls=p.execute('SELECT kind,eval_id,count(*) FROM call_log GROUP BY kind,eval_id ORDER BY kind,eval_id').fetchall();c.close();p.close();return {'attempt':a,'intents':i,'outcomes':o,'effects':effects,'calls':calls}
def count_calls(s,kind):return sum(x[2] for x in s['calls'] if x[0]==kind)
def start_server(prov,mode,behavior,td):
 marker=td+'/marker';release=td+'/release';portfile=td+'/port';
 for p in (marker,release,portfile):
  try:os.unlink(p)
  except FileNotFoundError:pass
 proc=subprocess.Popen([sys.executable,__file__,'server',prov,mode,behavior,marker,release,portfile]);wait_file(portfile);port=int(Path(portfile).read_text());return proc,'http://127.0.0.1:'+str(port),marker,release
def run_child(ctrl,base,mode,phase):return subprocess.Popen([sys.executable,__file__,'controller',ctrl,base,mode,phase])
def terminal_no_call(ctrl,base,mode,prov):
 before=inspect(ctrl,prov);subprocess.run([sys.executable,__file__,'controller',ctrl,base,mode,'resume'],check=True);after=inspect(ctrl,prov);return count_calls(after,'execute')==count_calls(before,'execute') and count_calls(after,'reconcile')==count_calls(before,'reconcile')

def case_controller_kill(mode):
 td=tempfile.mkdtemp(prefix='http-ctrlkill-');ctrl=td+'/c.db';prov=td+'/p.db';init(ctrl,prov);srv,base,marker,release=start_server(prov,mode,'hold_after_commit',td);ch=run_child(ctrl,base,mode,'initial');wait_file(marker);os.kill(ch.pid,signal.SIGKILL);wait_proc_exit(ch);Path(release).write_text('go');time.sleep(.05);mid=inspect(ctrl,prov);subprocess.run([sys.executable,__file__,'controller',ctrl,base,mode,'resume'],check=True);fin=inspect(ctrl,prov);terminal=terminal_no_call(ctrl,base,mode,prov);srv.terminate();srv.wait(timeout=5)
 if mode=='reconcilable':ok=fin['attempt']==('COMPLETE','transversal-v1') and len(fin['effects'])==1 and count_calls(fin,'execute')==1 and len(fin['outcomes'])==1 and terminal
 else:ok=fin['attempt']==('BLOCKED_UNKNOWN','direct-v1') and len(fin['effects'])==1 and count_calls(fin,'execute')==1 and count_calls(fin,'reconcile')==0 and len(fin['outcomes'])==0 and terminal
 return {'case':'controller_kill_after_provider_commit_before_response_read','mode':mode,'mid':mid,'final':fin,'terminal_second_resume_zero_provider_delta':terminal,'pass':ok}
def case_provider_crash(mode):
 td=tempfile.mkdtemp(prefix='http-provcrash-');ctrl=td+'/c.db';prov=td+'/p.db';init(ctrl,prov);srv,base,marker,release=start_server(prov,mode,'crash_after_commit',td);ch=run_child(ctrl,base,mode,'initial');wait_file(marker);wait_proc_exit(srv);wait_proc_exit(ch);mid=inspect(ctrl,prov);srv2,base2,_,_=start_server(prov,mode,'normal',td);subprocess.run([sys.executable,__file__,'controller',ctrl,base2,mode,'resume'],check=True);fin=inspect(ctrl,prov);terminal=terminal_no_call(ctrl,base2,mode,prov);srv2.terminate();srv2.wait(timeout=5)
 if mode=='reconcilable':ok=fin['attempt']==('COMPLETE','transversal-v1') and len(fin['effects'])==1 and count_calls(fin,'execute')==1 and len(fin['outcomes'])==1 and terminal
 else:ok=fin['attempt']==('BLOCKED_UNKNOWN','direct-v1') and len(fin['effects'])==1 and count_calls(fin,'execute')==1 and count_calls(fin,'reconcile')==0 and len(fin['outcomes'])==0 and terminal
 return {'case':'provider_crash_after_commit_before_response_send','mode':mode,'mid':mid,'final':fin,'terminal_second_resume_zero_provider_delta':terminal,'pass':ok}
def case_prewire(mode):
 td=tempfile.mkdtemp(prefix='http-prewire-');ctrl=td+'/c.db';prov=td+'/p.db';init(ctrl,prov);srv,base,_,_=start_server(prov,mode,'normal',td);ch=run_child(ctrl,base,mode,'prewire_kill');wait_proc_exit(ch);mid=inspect(ctrl,prov);subprocess.run([sys.executable,__file__,'controller',ctrl,base,mode,'resume'],check=True);fin=inspect(ctrl,prov);terminal=terminal_no_call(ctrl,base,mode,prov);srv.terminate();srv.wait(timeout=5)
 if mode=='reconcilable':ok=fin['attempt']==('COMPLETE','transversal-v1') and len(fin['effects'])==1 and count_calls(fin,'execute')==1 and len(fin['outcomes'])==1 and terminal
 else:ok=fin['attempt']==('BLOCKED_UNKNOWN','direct-v1') and len(fin['effects'])==0 and count_calls(fin,'execute')==0 and count_calls(fin,'reconcile')==0 and len(fin['outcomes'])==0 and terminal
 return {'case':'prewire_crash_after_durable_intent','mode':mode,'mid':mid,'final':fin,'terminal_second_resume_zero_provider_delta':terminal,'pass':ok}
def test(report):
 cases=[]
 for fn in (case_prewire,case_controller_kill,case_provider_crash):
  for mode in ('reconcilable','neither'):cases.append(fn(mode))
 out={'schema_version':1,'test_id':'OPT-HTTP-ACCEPT-v1','cases':cases,'all_passed':all(x['pass'] for x in cases),'scope':'loopback HTTP + separate provider/controller processes + durable SQLite; does not prove arbitrary remote provider semantics'};Path(report).write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8');print(json.dumps({'all_passed':out['all_passed'],'cases':[{'case':x['case'],'mode':x['mode'],'pass':x['pass'],'final':x['final']} for x in cases]},indent=2))
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);s=sub.add_parser('server');s.add_argument('prov');s.add_argument('mode');s.add_argument('behavior');s.add_argument('marker');s.add_argument('release');s.add_argument('portfile');c=sub.add_parser('controller');c.add_argument('ctrl');c.add_argument('base');c.add_argument('mode');c.add_argument('phase');t=sub.add_parser('test');t.add_argument('--report',required=True);a=ap.parse_args()
 if a.cmd=='server':serve(a.prov,a.mode,a.behavior,a.marker,a.release,a.portfile)
 elif a.cmd=='controller':controller(a.ctrl,a.base,a.mode,a.phase)
 else:test(a.report)
if __name__=='__main__':main()
