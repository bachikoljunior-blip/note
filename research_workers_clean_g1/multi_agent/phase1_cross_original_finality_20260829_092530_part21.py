#!/usr/bin/env python3
from itertools import product
from collections import defaultdict
import json

REQ={"A":60,"B":40}
ALLOC={
 "CORRECT":[("A","A",60),("B","B",40)],
 "SWAP_AMOUNT":[("A","A",40),("B","B",60)],
 "CROSS_BIND":[("A","B",60),("B","A",40)],
 "A_ONLY100":[("A","A",100)],
 "B_ONLY100":[("B","B",100)],
}

class Sink:
    def __init__(self,sc):
        self.sc=sc; self.current_epoch=1; self.next_id=1; self.records=[]
        self._init()
    def _final(self,slot):
        s=self.sc["late_status"]
        if s=="A_FAIL" and slot=="A" or s=="B_FAIL" and slot=="B": return "FAILED"
        if s=="A_REVERSED" and slot=="A" or s=="B_REVERSED" and slot=="B": return "REVERSED"
        return "SETTLED"
    def _init(self):
        for slot,bound,amt in ALLOC[self.sc["allocation"]]:
            if self.sc["ambig"]==f"{slot}_HIDDEN_NOT_APPLIED": continue
            self.records.append({"id":f"r{self.next_id}","slot":slot,"bound":bound,"amount":amt,
                                 "final":self._final(slot),"key":f"refund:{slot}:full",
                                 "active_idem":self.sc["dedupe"]=="VALID"})
            self.next_id+=1
    def _obs(self,recs):
        out=[dict(r) for r in recs]
        if self.sc["dup_obs"]=="YES" and out: out.append(dict(out[0]))
        return out
    def response(self,slot):
        if self.sc["ambig"].startswith(slot+"_HIDDEN"): return None
        return self._obs([r for r in self.records if r["slot"]==slot])
    def status(self,slot):
        if self.sc["status"]!="YES": return None
        return self._obs([r for r in self.records if r["slot"]==slot])
    def retry(self,slot,epoch):
        if self.sc["verifier"]!="AVAILABLE": return {"ok":False,"reason":"verifier_outage","obs":None}
        if epoch!=self.current_epoch: return {"ok":False,"reason":"stale","obs":None}
        k=f"refund:{slot}:full"
        for r in reversed(self.records):
            if r["key"]==k and r["active_idem"]:
                return {"ok":True,"reason":"idempotent","obs":self._obs([r])}
        r={"id":f"r{self.next_id}","slot":slot,"bound":slot,"amount":REQ[slot],"final":"SETTLED",
           "key":k,"active_idem":True}
        self.next_id+=1; self.records.append(r)
        return {"ok":True,"reason":"applied","obs":self._obs([r])}
    def replacement(self,slot,old_id,epoch):
        if self.sc["verifier"]!="AVAILABLE" or epoch!=self.current_epoch: return False
        r={"id":f"r{self.next_id}","slot":slot,"bound":slot,"amount":REQ[slot],"final":"SETTLED",
           "key":f"replacement:{old_id}","active_idem":True}
        self.next_id+=1; self.records.append(r); return True
    def truth(self):
        by=defaultdict(int)
        for r in self.records:
            if r["final"]=="SETTLED": by[r["bound"]]+=r["amount"]
        exact=all(by[o]==REQ[o] for o in REQ)
        return {"settled_A":by["A"],"settled_B":by["B"],"settled_total":sum(by.values()),
                "exact_vector":exact,"over":any(by[o]>REQ[o] for o in REQ),
                "under":any(by[o]<REQ[o] for o in REQ)}

def uniq(recs):
    d={}
    for r in recs or []: d[r["id"]]=r
    return list(d.values())

def weak(policy,sc):
    s=Sink(sc); epoch=2 if sc["takeover"]=="YES" else 1
    if epoch==2: s.current_epoch=2
    obs=[]
    for slot in ("A","B"):
        r=s.response(slot)
        if r is not None: obs += r
        else:
            st=s.status(slot)
            if st: obs += st
            else:
                q=s.retry(slot,epoch)
                if q["ok"] and q["obs"]: obs += q["obs"]
    if sc["repeat_kind"]=="YES":
        for slot in ("A","B"):
            q=s.retry(slot,epoch)
            if q["ok"] and q["obs"]: obs += q["obs"]
    u=uniq(obs)
    if policy=="PARENT":
        terminal=sum(r["amount"] for r in u)==100
    elif policy=="PER_INTENDED":
        by=defaultdict(int)
        for r in u: by[r["slot"]]+=r["amount"]
        terminal=all(by[o]==REQ[o] for o in REQ)
    else:
        by=defaultdict(int)
        for r in u: by[r["bound"]]+=r["amount"]
        terminal=all(by[o]==REQ[o] for o in REQ)
    return {"terminal":terminal,**s.truth()}

def effect_vector(sc,blind=False):
    s=Sink(sc); epoch=2 if sc["takeover"]=="YES" else 1
    if epoch==2: s.current_epoch=2
    if sc["status"]!="YES":
        if not blind: return {"terminal":False,**s.truth(),"failclosed":True}
        obs=[]
        for slot in ("A","B"):
            q=s.retry(slot,epoch)
            if not q["ok"]: return {"terminal":False,**s.truth(),"failclosed":True}
            obs += q["obs"] or []
        by=defaultdict(int)
        for r in uniq(obs): by[r["bound"]]+=r["amount"]
        terminal=all(by[o]==REQ[o] for o in REQ)
        return {"terminal":terminal,**s.truth(),"failclosed":not terminal}

    recs=[]
    for slot in ("A","B"):
        recs += s.status(slot) or []
    u=uniq(recs); settled=defaultdict(int); wrong=False
    for r in u:
        if r["final"]=="SETTLED":
            settled[r["bound"]]+=r["amount"]
            if r["bound"]!=r["slot"]: wrong=True
    if wrong or any(settled[o]>REQ[o] for o in REQ):
        return {"terminal":False,**s.truth(),"failclosed":True}

    for slot in ("A","B"):
        if settled[slot]==REQ[slot]: continue
        if settled[slot]!=0: return {"terminal":False,**s.truth(),"failclosed":True}
        if sc["verifier"]!="AVAILABLE": return {"terminal":False,**s.truth(),"failclosed":True}
        q=s.retry(slot,epoch)
        if not q["ok"]: return {"terminal":False,**s.truth(),"failclosed":True}
        got=uniq(q["obs"])
        if got and got[0]["final"] in ("FAILED","REVERSED"):
            if not s.replacement(slot,got[0]["id"],epoch):
                return {"terminal":False,**s.truth(),"failclosed":True}
    t=s.truth()
    return {"terminal":t["exact_vector"],**t,"failclosed":not t["exact_vector"]}

AXES={
 "allocation":["CORRECT","SWAP_AMOUNT","CROSS_BIND","A_ONLY100","B_ONLY100"],
 "late_status":["STABLE","A_FAIL","B_FAIL","A_REVERSED","B_REVERSED"],
 "ambig":["NONE","A_HIDDEN_APPLIED","A_HIDDEN_NOT_APPLIED","B_HIDDEN_APPLIED","B_HIDDEN_NOT_APPLIED"],
 "status":["YES","NO"],
 "dedupe":["VALID","EXPIRED"],
 "takeover":["NO","YES"],
 "verifier":["AVAILABLE","OUTAGE"],
 "dup_obs":["NO","YES"],
 "repeat_kind":["NO","YES"],
}
SC=[dict(zip(AXES,v)) for v in product(*AXES.values())]
D={
 "PARENT":[weak("PARENT",x) for x in SC],
 "PER_INTENDED":[weak("PER_INTENDED",x) for x in SC],
 "PER_BOUND_PROVISIONAL":[weak("PER_BOUND_PROVISIONAL",x) for x in SC],
 "EFFECT_VECTOR_STRONG":[effect_vector(x,False) for x in SC],
 "EFFECT_VECTOR_BLIND":[effect_vector(x,True) for x in SC],
}
def summary(rows):
    return {"terminal":sum(r["terminal"] for r in rows),
            "false_terminal":sum(r["terminal"] and not r["exact_vector"] for r in rows),
            "exact_terminal":sum(r["terminal"] and r["exact_vector"] for r in rows)}
def ii(pred): return [i for i,x in enumerate(SC) if pred(x)]
def ss(p,ind):
    r=D[p]
    return {"n":len(ind),"terminal":sum(r[i]["terminal"] for i in ind),
            "false_terminal":sum(r[i]["terminal"] and not r[i]["exact_vector"] for i in ind),
            "exact_terminal":sum(r[i]["terminal"] and r[i]["exact_vector"] for i in ind)}

OUT={"scenario_count":len(SC),"policies":{p:summary(r) for p,r in D.items()}}

ind=ii(lambda x:x["allocation"] in ("SWAP_AMOUNT","CROSS_BIND","A_ONLY100","B_ONLY100") and x["late_status"]=="STABLE" and x["ambig"]=="NONE" and x["status"]=="YES" and x["verifier"]=="AVAILABLE" and x["repeat_kind"]=="NO")
OUT["slices"]={"parent_correct_total_wrong_original":ss("PARENT",ind),
               "strong_wrong_allocation_failclosed":ss("EFFECT_VECTOR_STRONG",ind)}

ind=ii(lambda x:x["allocation"]=="CROSS_BIND" and x["late_status"]=="STABLE" and x["ambig"]=="NONE" and x["status"]=="YES" and x["verifier"]=="AVAILABLE" and x["repeat_kind"]=="NO")
OUT["slices"]["crossbind_per_intended"]=ss("PER_INTENDED",ind)
OUT["slices"]["crossbind_per_bound"]=ss("PER_BOUND_PROVISIONAL",ind)

ind=ii(lambda x:x["allocation"]=="CORRECT" and x["late_status"] in ("A_FAIL","B_FAIL","A_REVERSED","B_REVERSED") and x["ambig"]=="NONE" and x["status"]=="YES" and x["verifier"]=="AVAILABLE")
OUT["slices"]["late_failure_provisional"]=ss("PER_BOUND_PROVISIONAL",ind)
OUT["slices"]["late_failure_strong_replacement"]=ss("EFFECT_VECTOR_STRONG",ind)

ind=ii(lambda x:x["allocation"]=="CORRECT" and x["status"]=="NO" and x["dedupe"]=="EXPIRED" and x["verifier"]=="AVAILABLE")
OUT["slices"]["blind_no_status_expired"]=ss("EFFECT_VECTOR_BLIND",ind)
OUT["slices"]["strong_no_status_expired"]=ss("EFFECT_VECTOR_STRONG",ind)

OUT["interpretation"]={
 "scope":"Synthetic finite mechanism lattice; counts are not production failure rates.",
 "strong_rule":"Terminality is a per-original vector over unique sink-bound resource IDs in final SETTLED state. Provisional APPLIED, intended routing metadata, parent-level amount totals, and ambiguous retries are not finality proofs.",
 "protected_boundary":"The authoritative sink/status domain must expose final resource status and authoritative original-effect binding, and any replacement must be current-writer fenced and keyed to the failed/reversed resource identity."
}
print(json.dumps(OUT,indent=2,sort_keys=True))
