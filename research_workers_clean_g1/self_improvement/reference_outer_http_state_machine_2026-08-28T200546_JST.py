from __future__ import annotations
import argparse, hashlib, http.server, json, os, signal, sqlite3, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

def j(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def h(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def db(p:Path):
 c=sqlite3.connect(p,timeout=30,isolation_level=None);c.row_factory=sqlite3.Row;c.execute('pragma journal_mode=wal');c.execute('pragma synchronous=full');return c
def init_local(p:Path):
 c=db(p);c.executescript('''create table if not exists attempts(id text primary key,digest text not null,mode text not null,state text not null,cert text);create table if not exists cells(attempt text,id text,digest text,payload text,idem text,state text,outcome text,primary key(attempt,id));''');c.close()
def init_provider(p:Path):
 c=db(p);c.executescript('''create table if not exists effects(k text primary key,cell text,digest text,outcome text);create table if not exists calls(n integer primary key autoincrement,kind text,cell text,digest text,k text);''');c.close()
@dataclass(frozen=True)
class Req:
 candidate:str;evaluator:str;dataset:str;cells:tuple[str,...]
 def payload(self):return {'candidate':self.candidate,'evaluator':self.evaluator,'dataset':self.dataset,'split':'OUTER','cells':list(self.cells)}
def aid(r:Req):
 d=h(j(r.payload()));return 'outer-'+d[:24],d
def cell(r:Req,k:str):return {'candidate':r.candidate,'evaluator':r.evaluator,'dataset':r.dataset,'split':'OUTER','cell':k}
def idem(cid,d):return 'outer-http-'+h(cid+':'+d)
class Unknown(RuntimeError):pass

def httpj(url,body,headers=None,timeout=20):
 q=urllib.request.Request(url,data=j(body).encode(),method='POST',headers={'Content-Type':'application/json',**(headers or {})})
 try:
  with urllib.request.urlopen(q,timeout=timeout) as r:return json.loads(r.read().decode())
 except urllib.error.HTTPError as e:
  if e.code==404:return None
  raise

def persist(c,attempt,cid,out):
 s=j(out);c.execute('begin immediate');row=c.execute('select state,outcome from cells where attempt=? and id=?',(attempt,cid)).fetchone()
 if row['state']=='COMPLETED' and row['outcome']!=s:c.execute('rollback');raise RuntimeError('conflicting outcome')
 c.execute("update cells set state='COMPLETED',outcome=? where attempt=? and id=?",(s,attempt,cid));c.execute('commit')

def certify(local:Path,base:str,r:Req,mode:str):
 if mode not in ('idempotent_reconcile','nonidempotent_no_reconcile'):raise ValueError(mode)
 attempt,digest=aid(r);c=db(local);a=c.execute('select * from attempts where id=?',(attempt,)).fetchone()
 if a:
  if a['digest']!=digest or a['mode']!=mode:c.close();raise RuntimeError('semantic identity mismatch')
  if a['state']=='SEALED':out=json.loads(a['cert']);c.close();return out
 else:
  c.execute('begin immediate');c.execute("insert into attempts values(?,?,?,'RUNNING',null)",(attempt,digest,mode))
  for k in r.cells:
   p=cell(r,k);d=h(j(p));cid='cell-'+d[:24];ik=idem(cid,d) if mode=='idempotent_reconcile' else None;c.execute("insert into cells values(?,?,?,?,?,'PLANNED',null)",(attempt,cid,d,j(p),ik))
  c.execute('commit')
 for x in c.execute('select * from cells where attempt=? order by id',(attempt,)).fetchall():
  if x['state']=='COMPLETED':continue
  if x['state']=='UNKNOWN':c.close();raise Unknown('unknown provider outcome')
  p=json.loads(x['payload']);out=None
  if x['state']=='DISPATCHING':
   if mode=='nonidempotent_no_reconcile':
    c.execute('begin immediate');c.execute("update cells set state='UNKNOWN' where attempt=? and id=?",(attempt,x['id']));c.execute('commit');c.close();raise Unknown('post-dispatch outcome unknown; blind retry forbidden')
   out=httpj(base+'/reconcile',{'cell_id':x['id'],'request_digest':x['digest'],'idempotency_key':x['idem']})
  else:
   c.execute('begin immediate');c.execute("update cells set state='DISPATCHING' where attempt=? and id=? and state='PLANNED'",(attempt,x['id']));c.execute('commit')
  if out is None:
   headers={'Idempotency-Key':x['idem']} if x['idem'] else {}
   out=httpj(base+'/execute',{'cell_id':x['id'],'request_digest':x['digest'],'payload':p},headers,60)
  persist(c,attempt,x['id'],out)
 rows=c.execute('select id,outcome from cells where attempt=? order by id',(attempt,)).fetchall()
 if len(rows)!=len(r.cells) or any(x['outcome'] is None for x in rows):c.close();raise RuntimeError('incomplete')
 cert={'attempt_id':attempt,'request_digest':digest,'scores':[json.loads(x['outcome'])['score'] for x in rows]};cert['mean_score']=sum(cert['scores'])/len(cert['scores'])
 c.execute('begin immediate');c.execute("update attempts set state='SEALED',cert=? where id=?",(j(cert),attempt));c.execute('commit');c.close();return cert

def counts(p:Path):
 c=db(p);r={x['kind']:x['n'] for x in c.execute('select kind,count(*) n from calls group by kind')};r['effects']=c.execute('select count(*) n from effects').fetchone()['n'];c.close();return {'execute':r.get('execute',0),'reconcile':r.get('reconcile',0),'effects':r['effects']}
def states(p:Path):
 c=db(p);r=[{'id':x['id'],'state':x['state']} for x in c.execute('select id,state from cells order by id')];c.close();return r
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def reply(self,n,obj):
  b=j(obj).encode();self.send_response(n);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def body(self):return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))).decode())
 def do_POST(self):
  q=self.body();p=Path(self.server.provider_db);c=db(p)
  if self.path=='/reconcile':
   k=q['idempotency_key'];c.execute("insert into calls(kind,cell,digest,k) values('reconcile',?,?,?)",(q['cell_id'],q['request_digest'],k));row=c.execute('select * from effects where k=?',(k,)).fetchone();c.close();return self.reply(404,{}) if not row else self.reply(200,json.loads(row['outcome']))
  if self.path!='/execute':c.close();return self.reply(404,{})
  mode=self.server.mode;key=self.headers.get('Idempotency-Key') if mode=='idempotent_reconcile' else None;k=key or 'effect-'+str(time.time_ns())
  c.execute('begin immediate');c.execute("insert into calls(kind,cell,digest,k) values('execute',?,?,?)",(q['cell_id'],q['request_digest'],k));row=c.execute('select * from effects where k=?',(k,)).fetchone()
  if row:out=json.loads(row['outcome'])
  else:
   score=int(h(j(q['payload']))[:8],16)%1000/1000;out={'cell_id':q['cell_id'],'score':score};c.execute('insert into effects values(?,?,?,?)',(k,q['cell_id'],q['request_digest'],j(out)))
  c.execute('commit');c.close();self.server.accepted+=1
  if self.server.hold_first and self.server.accepted==1:
   m=Path(self.server.marker);m.mkdir(parents=True,exist_ok=True);(m/'accepted-1').write_text('1');release=m/'release-first'
   while not release.exists():time.sleep(.01)
  self.reply(200,out)

def provider(args):
 init_provider(Path(args.provider_db));s=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler);s.provider_db=args.provider_db;s.mode=args.mode;s.marker=args.marker;s.hold_first=args.hold_first;s.accepted=0;Path(args.port_file).write_text(str(s.server_address[1]));s.serve_forever(.05)
def wait(p:Path,t=10):
 end=time.time()+t
 while time.time()<end:
  if p.exists():return
  time.sleep(.01)
 raise TimeoutError(p)
def launch_provider(root:Path,mode):
 pd=root/'provider.sqlite';m=root/'m';port=root/'port';cmd=[sys.executable,__file__,'provider','--provider-db',str(pd),'--marker',str(m),'--mode',mode,'--port-file',str(port),'--port','0','--hold-first'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);wait(port);return p,'http://127.0.0.1:'+port.read_text(),pd,m
def ctl(local,base,mode):return [sys.executable,__file__,'controller','--local-db',str(local),'--base-url',base,'--mode',mode]
def selftest():
 out={'schema_version':1,'test':'http_sigkill_provider_uncertainty'}
 for mode in ('idempotent_reconcile','nonidempotent_no_reconcile'):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);local=root/'local.sqlite';init_local(local);srv,base,pd,m=launch_provider(root,mode);cmd=ctl(local,base,mode);p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);wait(m/'accepted-1');os.kill(p.pid,signal.SIGKILL);p.wait();before=counts(pd);(m/'release-first').write_text('x');time.sleep(.05);r=subprocess.run(cmd,capture_output=True,text=True,timeout=20);after=counts(pd)
   if mode=='idempotent_reconcile':
    if r.returncode:raise AssertionError(r.stderr)
    cert=json.loads(r.stdout.splitlines()[-1]);before2=counts(pd);r2=subprocess.run(cmd,capture_output=True,text=True,check=True);after2=counts(pd);ok=after['effects']==3 and after['execute']==3 and after['reconcile']>=1 and before2==after2 and json.loads(r2.stdout.splitlines()[-1])==cert
    out['idempotent_http']={'controller_exit':p.returncode,'before_resume':before,'after_resume':after,'after_second':after2,'states':states(local),'certificate_digest':h(j(cert)),'effect_count_one_per_cell':after['effects']==3,'execute_count_one_per_cell':after['execute']==3,'reconcile_used':after['reconcile']>=1,'second_certify_provider_delta_zero':before2==after2}
   else:
    ok=r.returncode!=0 and after==before and sum(x['state']=='UNKNOWN' for x in states(local))==1
    out['nonidempotent_fail_closed']={'controller_exit':p.returncode,'resume_exit':r.returncode,'before_resume':before,'after_resume':after,'states':states(local),'blind_retry_provider_delta_zero':after==before,'error_tail':r.stderr.splitlines()[-1] if r.stderr else ''}
   srv.terminate();srv.wait(timeout=3)
   if not ok:raise AssertionError(out)
 out['all_passed']=True;out['scope_note']='Local HTTP+SQLite reference validates controller ordering and provider-contract branching, not arbitrary external-provider exactly-once guarantees.';return out

def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True);p=s.add_parser('provider');p.add_argument('--provider-db',required=True);p.add_argument('--marker',required=True);p.add_argument('--mode',required=True);p.add_argument('--port-file',required=True);p.add_argument('--port',type=int,default=0);p.add_argument('--hold-first',action='store_true');c=s.add_parser('controller');c.add_argument('--local-db',required=True);c.add_argument('--base-url',required=True);c.add_argument('--mode',required=True);s.add_parser('self-test');x=a.parse_args()
 if x.cmd=='provider':provider(x);return 0
 if x.cmd=='controller':print(j(certify(Path(x.local_db),x.base_url,Req('cand:abc','eval:v3','data:outer-v3',('a','b','c')),x.mode)));return 0
 print(json.dumps(selftest(),indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
