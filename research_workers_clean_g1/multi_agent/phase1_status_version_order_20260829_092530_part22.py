#!/usr/bin/env python3
from itertools import product
import json

DELIVERIES={
 "IN_ORDER":[(1,"PENDING"),(2,"SETTLED"),("V3",None)],
 "REVERSE":[("V3",None),(2,"SETTLED"),(1,"PENDING")],
 "LATE_STALE_SETTLED":[(1,"PENDING"),("V3",None),(2,"SETTLED")],
 "MISSING_V3":[(1,"PENDING"),(2,"SETTLED")],
 "ONLY_V2":[(2,"SETTLED")],
 "V3_ONLY":[("V3",None)],
 "DUP_V3_LATE_STALE":[(1,"PENDING"),("V3",None),("V3",None),(2,"SETTLED")],
}
def events(sc):
    return [(3,sc["truth"]) if v=="V3" else (v,s) for v,s in DELIVERIES[sc["delivery"]]]
def witness(sc):
    return None if sc["durable"]=="NONE" else (2,"SETTLED") if sc["durable"]=="V2" else (3,sc["truth"])
def read(sc):
    return None if sc["read"]=="UNAVAILABLE" else (2,"SETTLED") if sc["read"]=="STALE_V2" else (3,sc["truth"])

def finish(status,sc,claim_epoch=False):
    keys=set(); reps=0
    runs=2 if sc["repeat_recovery"]=="YES" else 1
    for run in range(runs):
        epoch=2 if sc["takeover"]=="YES" and run==runs-1 else 1
        if status in ("FAILED","REVERSED") and sc["verifier"]=="AVAILABLE":
            k=f"repl:A:rA:v3:e{epoch}" if claim_epoch else "repl:A:rA:v3"
            if k not in keys: keys.add(k); reps+=1
    old=60 if sc["truth"]=="SETTLED" else 0
    afinal=old+60*reps
    return {"terminal":status=="SETTLED" or (status in ("FAILED","REVERSED") and reps>=1),
            "exact":afinal==60,"replacement_count":reps,"A_final":afinal}

def last_arrival(sc):
    ev=events(sc); st=ev[-1][1] if ev else None
    return {"terminal":False,"exact":sc["truth"]=="SETTLED","replacement_count":0,"A_final":60 if sc["truth"]=="SETTLED" else 0} if st in (None,"PENDING") else finish(st,sc)

def monotonic(sc):
    ev=events(sc)
    if not ev: return {"terminal":False,"exact":False,"replacement_count":0,"A_final":0}
    _,st=max(ev,key=lambda x:x[0])
    return {"terminal":False,"exact":False,"replacement_count":0,"A_final":0} if st=="PENDING" else finish(st,sc)

def read_string(sc):
    r=read(sc)
    if r is None: return last_arrival(sc)
    return finish(r[1],sc)

def max_seen(sc):
    e=events(sc)
    w=witness(sc)
    if w: e.append(w)
    r=read(sc)
    if r: e.append(r)
    _,st=max(e,key=lambda x:x[0])
    return finish(st,sc)

def strong(sc,claim_epoch=False):
    proof=(3,sc["truth"]) if sc["read"]=="CURRENT_V3" or sc["durable"]=="V3" else None
    if proof is None:
        old=60 if sc["truth"]=="SETTLED" else 0
        return {"terminal":False,"exact":old==60,"replacement_count":0,"A_final":old}
    return finish(proof[1],sc,claim_epoch)

AXES={
 "truth":["SETTLED","FAILED","REVERSED"],
 "delivery":list(DELIVERIES),
 "read":["CURRENT_V3","STALE_V2","UNAVAILABLE"],
 "durable":["NONE","V2","V3"],
 "takeover":["NO","YES"],
 "verifier":["AVAILABLE","OUTAGE"],
 "repeat_recovery":["NO","YES"],
}
SC=[dict(zip(AXES,v)) for v in product(*AXES.values())]
D={
 "LAST_ARRIVAL":[last_arrival(x) for x in SC],
 "MONOTONIC_EVENT":[monotonic(x) for x in SC],
 "READ_STRING":[read_string(x) for x in SC],
 "MAX_SEEN_VERSION":[max_seen(x) for x in SC],
 "CURRENT_PROOF_STRONG":[strong(x,False) for x in SC],
 "CURRENT_PROOF_CLAIM_EPOCH_REPL":[strong(x,True) for x in SC],
}
def summary(rows):
    return {"terminal":sum(r["terminal"] for r in rows),
            "false_terminal":sum(r["terminal"] and not r["exact"] for r in rows),
            "exact_terminal":sum(r["terminal"] and r["exact"] for r in rows),
            "duplicate_replacement":sum(r["replacement_count"]>1 for r in rows)}
def ii(pred): return [i for i,x in enumerate(SC) if pred(x)]
def ss(p,ind):
    r=D[p]
    return {"n":len(ind),"terminal":sum(r[i]["terminal"] for i in ind),
            "false_terminal":sum(r[i]["terminal"] and not r[i]["exact"] for i in ind),
            "duplicate_replacement":sum(r[i]["replacement_count"]>1 for i in ind)}
OUT={"scenario_count":len(SC),"policies":{p:summary(r) for p,r in D.items()}}

ind=ii(lambda x:x["truth"] in ("FAILED","REVERSED") and x["delivery"]=="LATE_STALE_SETTLED" and x["verifier"]=="AVAILABLE")
OUT["slices"]={"late_stale_last_arrival":ss("LAST_ARRIVAL",ind)}

ind=ii(lambda x:x["truth"] in ("FAILED","REVERSED") and x["delivery"] in ("MISSING_V3","ONLY_V2") and x["verifier"]=="AVAILABLE")
OUT["slices"]["missing_v3_monotonic_event"]=ss("MONOTONIC_EVENT",ind)

ind=ii(lambda x:x["truth"] in ("FAILED","REVERSED") and x["read"]=="STALE_V2" and x["verifier"]=="AVAILABLE")
OUT["slices"]["stale_read_string"]=ss("READ_STRING",ind)

ind=ii(lambda x:x["truth"] in ("FAILED","REVERSED") and x["delivery"] in ("MISSING_V3","ONLY_V2") and x["read"]!="CURRENT_V3" and x["durable"]!="V3" and x["verifier"]=="AVAILABLE")
OUT["slices"]["max_seen_without_current_proof"]=ss("MAX_SEEN_VERSION",ind)
OUT["slices"]["strong_without_current_proof"]=ss("CURRENT_PROOF_STRONG",ind)

ind=ii(lambda x:x["truth"] in ("FAILED","REVERSED") and x["takeover"]=="YES" and x["repeat_recovery"]=="YES" and x["verifier"]=="AVAILABLE" and (x["read"]=="CURRENT_V3" or x["durable"]=="V3"))
OUT["slices"]["claim_epoch_replacement_identity"]=ss("CURRENT_PROOF_CLAIM_EPOCH_REPL",ind)
OUT["slices"]["stable_failed_version_replacement_identity"]=ss("CURRENT_PROOF_STRONG",ind)

OUT["interpretation"]={
 "scope":"Synthetic finite mechanism lattice with current truth fixed at resource status version 3; counts are not production failure rates.",
 "strong_rule":"Webhook/event order is advisory. Terminality requires a durable proof of the current resource version/status (authoritative current read or previously persisted current-v3 witness), then replacement identity is stable over {resource_id, failed_status_version} and separate from claim epoch.",
 "protected_boundary":"The sink/status authority must expose a current-version/freshness primitive or an absorbing finality token; CLEAN can process versioned events and durable witnesses but cannot make a stale replica or missing webhook authoritative."
}
print(json.dumps(OUT,indent=2,sort_keys=True))
