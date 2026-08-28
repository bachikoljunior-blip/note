#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, http.client as http_client, json, os, signal, socket, sqlite3, subprocess, sys, tempfile, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

CLASSES={"idempotent_plus_reconcile","idempotent_only","reconcile_only","neither"}
TERMINAL={"COMPLETE","BLOCKED_UNKNOWN","BLOCKED_MISMATCH","CONFLICT"}

def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def req_digest(provider_class:str,op_id:str,identity_scope:str,target_key:str,expected_base_version:int,intended_value:str)->str:
    return hashlib.sha256(canon({"provider_class":provider_class,"op_id":op_id,"identity_scope":identity_scope,"target_key":target_key,"expected_base_version":int(expected_base_version),"intended_value":intended_value}).encode()).hexdigest()

class ProviderDB:
    def __init__(self,path:Path):
        self.path=path
        with self.cx() as c:
            c.executescript("""
PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
CREATE TABLE IF NOT EXISTS effects(effect_id INTEGER PRIMARY KEY AUTOINCREMENT, provider_class TEXT NOT NULL, op_id TEXT, request_digest TEXT NOT NULL,target_key TEXT NOT NULL,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idem(op_id TEXT PRIMARY KEY,request_digest TEXT NOT NULL,effect_id INTEGER NOT NULL,expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS targets(target_key TEXT PRIMARY KEY,value TEXT NOT NULL,version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS stats(name TEXT PRIMARY KEY,count INTEGER NOT NULL);
INSERT OR IGNORE INTO stats VALUES('execute',0); INSERT OR IGNORE INTO stats VALUES('reconcile',0); INSERT OR IGNORE INTO stats VALUES('effect',0);
""")
    def cx(self): return sqlite3.connect(self.path)
    def inc(self,c,n): c.execute("UPDATE stats SET count=count+1 WHERE name=?",(n,))
    def stats(self):
        with self.cx() as c:return {r[0]:int(r[1]) for r in c.execute("SELECT name,count FROM stats")}
    def seed_target(self,key,value,version):
        with self.cx() as c:c.execute("INSERT OR REPLACE INTO targets VALUES(?,?,?)",(key,value,int(version)))
    def execute(self,b):
        cls=b["provider_class"]; now=float(b["now"]); ttl=float(b.get("ttl",24.0)); op=b.get("op_id",""); d=b["request_digest"]; key=b["target_key"]; val=b["intended_value"]; base=int(b.get("expected_base_version",0))
        with self.cx() as c:
            self.inc(c,"execute")
            if cls in {"idempotent_plus_reconcile","idempotent_only"}:
                row=c.execute("SELECT request_digest,effect_id,expires_at FROM idem WHERE op_id=?",(op,)).fetchone()
                if row is not None and now<=float(row[2]):
                    if row[0]!=d:return {"status":"MISMATCH"}
                    return {"status":"REPLAY","effect_id":int(row[1])}
                cur=c.execute("INSERT INTO effects(provider_class,op_id,request_digest,target_key,value) VALUES(?,?,?,?,?)",(cls,op,d,key,val)); eid=int(cur.lastrowid); self.inc(c,"effect")
                c.execute("INSERT OR REPLACE INTO idem VALUES(?,?,?,?)",(op,d,eid,now+ttl)); return {"status":"CREATED","effect_id":eid}
            if cls=="reconcile_only":
                row=c.execute("SELECT value,version FROM targets WHERE target_key=?",(key,)).fetchone(); ver=0 if row is None else int(row[1])
                if ver!=base:return {"status":"CONFLICT","current_version":ver}
                cur=c.execute("INSERT INTO effects(provider_class,op_id,request_digest,target_key,value) VALUES(?,?,?,?,?)",(cls,None,d,key,val)); eid=int(cur.lastrowid); self.inc(c,"effect")
                c.execute("INSERT OR REPLACE INTO targets VALUES(?,?,?)",(key,val,ver+1)); return {"status":"CREATED","effect_id":eid,"version":ver+1}
            if cls=="neither":
                cur=c.execute("INSERT INTO effects(provider_class,op_id,request_digest,target_key,value) VALUES(?,?,?,?,?)",(cls,None,d,key,val)); eid=int(cur.lastrowid); self.inc(c,"effect"); return {"status":"CREATED","effect_id":eid}
            raise ValueError(cls)
    def reconcile_op(self,op):
        with self.cx() as c:
            self.inc(c,"reconcile"); row=c.execute("SELECT effect_id,request_digest,target_key,value FROM effects WHERE op_id=? ORDER BY effect_id LIMIT 1",(op,)).fetchone()
            return None if row is None else {"effect_id":int(row[0]),"request_digest":row[1],"target_key":row[2],"value":row[3]}
    def reconcile_target(self,key):
        with self.cx() as c:
            self.inc(c,"reconcile"); row=c.execute("SELECT value,version FROM targets WHERE target_key=?",(key,)).fetchone(); return None if row is None else {"value":row[0],"version":int(row[1])}

class Handler(BaseHTTPRequestHandler):
    db:ProviderDB
    def log_message(self,*a):pass
    def sendj(self,obj,code=200):
        raw=canon(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def body(self): return json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
    def do_GET(self):
        if self.path=="/stats":return self.sendj(self.db.stats())
        return self.sendj({"error":"not_found"},404)
    def do_POST(self):
        b=self.body()
        if self.path=="/seed_target": self.db.seed_target(b["target_key"],b["value"],b["version"]); return self.sendj({"ok":True})
        if self.path=="/reconcile_op": return self.sendj({"found":self.db.reconcile_op(b["op_id"])})
        if self.path=="/reconcile_target": return self.sendj({"found":self.db.reconcile_target(b["target_key"])})
        if self.path=="/execute":
            r=self.db.execute(b)
            if b.get("crash_after_commit"): os._exit(73)
            return self.sendj(r)
        return self.sendj({"error":"not_found"},404)

def serve(db,port):
    Handler.db=ProviderDB(Path(db)); s=ThreadingHTTPServer(("127.0.0.1",port),Handler); s.serve_forever()
def free_port():
    s=socket.socket(); s.bind(("127.0.0.1",0)); p=s.getsockname()[1]; s.close(); return p
class Server:
    def __init__(self,script:Path,db:Path):self.script=script;self.db=db;self.port=free_port();self.p=None
    def start(self):
        self.p=subprocess.Popen([sys.executable,str(self.script),"serve","--db",str(self.db),"--port",str(self.port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(100):
            try: http("GET",self.port,"/stats",None,timeout=.1); return
            except Exception: time.sleep(.02)
        raise RuntimeError("server start failed")
    def stop(self):
        if self.p and self.p.poll() is None:self.p.terminate(); self.p.wait(timeout=2)
    def wait_crash(self):
        if self.p:self.p.wait(timeout=2)

def http(method,port,path,body,timeout=2):
    c=http_client.HTTPConnection("127.0.0.1",port,timeout=timeout); raw=None if body is None else canon(body)
    try:
        c.request(method,path,body=raw,headers={} if raw is None else {"Content-Type":"application/json"}); r=c.getresponse(); data=r.read(); return json.loads(data or b"{}")
    finally:c.close()

class Controller:
    def __init__(self,path:Path,port:int):
        self.path=path;self.port=port
        with self.cx() as c:c.executescript("""PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; CREATE TABLE IF NOT EXISTS attempts(attempt_id TEXT PRIMARY KEY,provider_class TEXT NOT NULL,op_id TEXT NOT NULL,identity_scope TEXT NOT NULL,request_digest TEXT NOT NULL,target_key TEXT NOT NULL,expected_base_version INTEGER NOT NULL,intended_value TEXT NOT NULL,expiry_at REAL,state TEXT NOT NULL,result_json TEXT);""")
    def cx(self):return sqlite3.connect(self.path)
    def create(self,aid,cls,op,scope,key,base,val,expiry):
        if cls not in CLASSES:raise ValueError("unknown provider class")
        d=req_digest(cls,op,scope,key,base,val)
        with self.cx() as c:c.execute("INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?,?,?,NULL)",(aid,cls,op,scope,d,key,int(base),val,expiry,"DISPATCHING"))
        return d
    def load(self,aid):
        with self.cx() as c:r=c.execute("SELECT attempt_id,provider_class,op_id,identity_scope,request_digest,target_key,expected_base_version,intended_value,expiry_at,state,result_json FROM attempts WHERE attempt_id=?",(aid,)).fetchone()
        keys=["attempt_id","provider_class","op_id","identity_scope","request_digest","target_key","expected_base_version","intended_value","expiry_at","state","result_json"];return dict(zip(keys,r))
    def finish(self,aid,state,res):
        with self.cx() as c:c.execute("UPDATE attempts SET state=?,result_json=? WHERE attempt_id=?",(state,canon(res),aid))
        return {"state":state,"result":res}
    def payload(self,a,now,ttl=24,crash=False):return {"provider_class":a["provider_class"],"op_id":a["op_id"],"request_digest":a["request_digest"],"target_key":a["target_key"],"expected_base_version":a["expected_base_version"],"intended_value":a["intended_value"],"now":now,"ttl":ttl,"crash_after_commit":crash}
    def dispatch_once(self,aid,now,ttl=24,crash=False):return http("POST",self.port,"/execute",self.payload(self.load(aid),now,ttl,crash))
    def resume(self,aid,now,ttl=24):
        a=self.load(aid)
        if a["state"] in TERMINAL:return {"state":a["state"],"result":json.loads(a["result_json"] or "{}"),"terminal_cache":True}
        d=req_digest(a["provider_class"],a["op_id"],a["identity_scope"],a["target_key"],a["expected_base_version"],a["intended_value"])
        if d!=a["request_digest"]:return self.finish(aid,"BLOCKED_MISMATCH",{"reason":"local_identity_or_payload_digest_mismatch"})
        cls=a["provider_class"]
        if cls=="idempotent_plus_reconcile":
            f=http("POST",self.port,"/reconcile_op",{"op_id":a["op_id"]})["found"]
            if f is not None:
                if f["request_digest"]!=a["request_digest"] or f["target_key"]!=a["target_key"] or f["value"]!=a["intended_value"]:return self.finish(aid,"BLOCKED_MISMATCH",{"reason":"reconciled_effect_mismatch"})
                return self.finish(aid,"COMPLETE",{"source":"reconcile","effect_id":f["effect_id"]})
            if a["expiry_at"] is not None and now>float(a["expiry_at"]):return self.finish(aid,"BLOCKED_UNKNOWN",{"reason":"idempotency_window_expired_after_reconcile_miss"})
            r=http("POST",self.port,"/execute",self.payload(a,now,ttl));
            if r["status"]=="MISMATCH":return self.finish(aid,"BLOCKED_MISMATCH",{"reason":"provider_idempotency_mismatch"})
            return self.finish(aid,"COMPLETE",{"source":"same_identity_replay","effect_id":r["effect_id"]})
        if cls=="idempotent_only":
            if a["expiry_at"] is None or now>float(a["expiry_at"]):return self.finish(aid,"BLOCKED_UNKNOWN",{"reason":"idempotency_window_expired"})
            r=http("POST",self.port,"/execute",self.payload(a,now,ttl));
            if r["status"]=="MISMATCH":return self.finish(aid,"BLOCKED_MISMATCH",{"reason":"provider_idempotency_mismatch"})
            return self.finish(aid,"COMPLETE",{"source":"same_identity_replay","effect_id":r["effect_id"]})
        if cls=="reconcile_only":
            f=http("POST",self.port,"/reconcile_target",{"target_key":a["target_key"]})["found"]
            base=int(a["expected_base_version"])
            if f is not None and f["version"]==base+1 and f["value"]==a["intended_value"]:return self.finish(aid,"COMPLETE",{"source":"target_reconcile","version":f["version"]})
            if f is not None and f["version"]!=base:return self.finish(aid,"CONFLICT",{"reason":"base_version_changed","current_version":f["version"]})
            r=http("POST",self.port,"/execute",self.payload(a,now,ttl))
            if r["status"]=="CONFLICT":return self.finish(aid,"CONFLICT",{"reason":"cas_conflict","current_version":r["current_version"]})
            return self.finish(aid,"COMPLETE",{"source":"cas_retry","effect_id":r["effect_id"]})
        if cls=="neither":return self.finish(aid,"BLOCKED_UNKNOWN",{"reason":"ambiguous_dispatch_without_recovery_primitive"})
        return self.finish(aid,"BLOCKED_MISMATCH",{"reason":"unknown_provider_class"})

def delta(a,b):return {k:b[k]-a[k] for k in sorted(a)}
def getstats(port):return http("GET",port,"/stats",None)
def seed(port,key,val,ver):http("POST",port,"/seed_target",{"target_key":key,"value":val,"version":ver})

def run_case(script:Path,name:str):
    with tempfile.TemporaryDirectory(prefix="http-prov-v2-") as td:
        root=Path(td); pdb=root/"provider.db"; cdb=root/"controller.db"; srv=Server(script,pdb); srv.start(); c=Controller(cdb,srv.port); now=100.; ttl=24.; aid="a"; op="op"; scope="region-x"; key="target"; val="v1"; base=0; expiry=now+ttl
        expected="COMPLETE"; dispatch_crash=False; advance=0.; expected_effect=None
        if name.startswith("reconcile_"): base=1; seed(srv.port,key,"old",1)
        cls={
            "idpr_response_loss":"idempotent_plus_reconcile","idpr_expired_existing":"idempotent_plus_reconcile","idpr_expired_missing":"idempotent_plus_reconcile","idonly_response_loss":"idempotent_only","idonly_expired_existing":"idempotent_only","idonly_provider_mismatch":"idempotent_only","reconcile_response_loss":"reconcile_only","reconcile_prewire":"reconcile_only","reconcile_conflict":"reconcile_only","neither_response_loss":"neither","local_op_mutation":"idempotent_plus_reconcile","local_class_mutation":"idempotent_plus_reconcile"}[name]
        c.create(aid,cls,op,scope,key,base,val,expiry)
        if name in {"idpr_response_loss","idpr_expired_existing","idonly_response_loss","idonly_expired_existing","reconcile_response_loss","neither_response_loss"}: dispatch_crash=True
        if name=="idpr_expired_missing": expected="BLOCKED_UNKNOWN"; advance=25.; expected_effect=0
        if name in {"idpr_expired_existing","idonly_expired_existing"}: advance=25.
        if name=="idonly_expired_existing": expected="BLOCKED_UNKNOWN"
        if name=="neither_response_loss": expected="BLOCKED_UNKNOWN"
        if name=="reconcile_conflict": seed(srv.port,key,"other",2); expected="CONFLICT"; expected_effect=0
        if name=="local_op_mutation":
            with c.cx() as x:x.execute("UPDATE attempts SET op_id='op-mutated' WHERE attempt_id=?",(aid,)); expected="BLOCKED_MISMATCH"; expected_effect=0
        if name=="local_class_mutation":
            with c.cx() as x:x.execute("UPDATE attempts SET provider_class='idempotent_only' WHERE attempt_id=?",(aid,)); expected="BLOCKED_MISMATCH"; expected_effect=0
        if name=="idonly_provider_mismatch":
            other=req_digest("idempotent_only",op,scope,key,base,"other")
            http("POST",srv.port,"/execute",{"provider_class":"idempotent_only","op_id":op,"request_digest":other,"target_key":key,"expected_base_version":base,"intended_value":"other","now":now,"ttl":ttl}); expected="BLOCKED_MISMATCH"; expected_effect=1
        if dispatch_crash:
            try:c.dispatch_once(aid,now,ttl,True)
            except Exception:pass
            srv.wait_crash(); srv=Server(script,pdb); srv.start(); c.port=srv.port
            if expected_effect is None:expected_effect=1
        before=getstats(srv.port); first=c.resume(aid,now+advance,ttl); after=getstats(srv.port); d1=delta(before,after); before2=getstats(srv.port); second=Controller(cdb,srv.port).resume(aid,now+advance,ttl); after2=getstats(srv.port); d2=delta(before2,after2)
        if expected_effect is None: expected_effect=1 if first["state"]=="COMPLETE" and name not in {"reconcile_conflict"} else after["effect"]
        checks={"first_state":first["state"]==expected,"effect_total":after["effect"]==expected_effect,"second_state_same":second["state"]==expected,"terminal_second_provider_call_free":d2=={"effect":0,"execute":0,"reconcile":0}}
        if name=="idpr_response_loss":checks["reconcile_not_reexecute"]=d1=={"effect":0,"execute":0,"reconcile":1}
        if name=="idpr_expired_existing":checks["expiry_does_not_block_exact_reconcile"]=d1=={"effect":0,"execute":0,"reconcile":1}
        if name=="idpr_expired_missing":checks["expired_miss_no_execute"]=d1=={"effect":0,"execute":0,"reconcile":1}
        if name=="idonly_response_loss":checks["same_key_replay_no_duplicate_effect"]=d1=={"effect":0,"execute":1,"reconcile":0}
        if name=="idonly_expired_existing":checks["expired_no_blind_replay"]=d1=={"effect":0,"execute":0,"reconcile":0}
        if name=="idonly_provider_mismatch":checks["provider_mismatch_no_effect"]=d1=={"effect":0,"execute":1,"reconcile":0}
        if name=="reconcile_response_loss":checks["target_reconcile_no_reexecute"]=d1=={"effect":0,"execute":0,"reconcile":1}
        if name=="reconcile_prewire":checks["cas_after_base_verified"]=d1=={"effect":1,"execute":1,"reconcile":1}
        if name=="reconcile_conflict":checks["conflict_no_execute"]=d1=={"effect":0,"execute":0,"reconcile":1}
        if name=="neither_response_loss":checks["unknown_no_retry"]=d1=={"effect":0,"execute":0,"reconcile":0}
        if name in {"local_op_mutation","local_class_mutation"}:checks["local_digest_guard_before_provider"]=d1=={"effect":0,"execute":0,"reconcile":0}
        srv.stop(); return {"case":name,"first":first,"first_provider_delta":d1,"provider_after_first":after,"second":second,"second_provider_delta":d2,"checks":checks,"pass":all(checks.values())}

def acceptance(script):
    names=["idpr_response_loss","idpr_expired_existing","idpr_expired_missing","idonly_response_loss","idonly_expired_existing","idonly_provider_mismatch","reconcile_response_loss","reconcile_prewire","reconcile_conflict","neither_response_loss","local_op_mutation","local_class_mutation"]
    cs=[run_case(script,n) for n in names];return {"schema_version":2,"harness":"reference_optimizer_provider_http_controller_v2","case_count":len(cs),"pass_count":sum(c["pass"] for c in cs),"all_pass":all(c["pass"] for c in cs),"cases":cs}
def main():
    a=argparse.ArgumentParser(); sub=a.add_subparsers(dest="cmd",required=True); s=sub.add_parser("serve");s.add_argument("--db",required=True);s.add_argument("--port",type=int,required=True); t=sub.add_parser("acceptance");t.add_argument("--output",required=True); ns=a.parse_args()
    if ns.cmd=="serve":return serve(ns.db,ns.port)
    r=acceptance(Path(__file__).resolve()); Path(ns.output).write_text(canon(r)+"\n")
if __name__=="__main__":main()
