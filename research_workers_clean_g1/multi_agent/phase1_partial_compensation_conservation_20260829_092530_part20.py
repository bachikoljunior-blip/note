#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

UNIVERSE=frozenset(range(100))

def segs(plan):
    if plan=="FULL100": return [frozenset(range(100))]
    if plan=="SPLIT40_60": return [frozenset(range(40)),frozenset(range(40,100))]
    if plan=="REPART60_40": return [frozenset(range(60)),frozenset(range(60,100))]
    raise ValueError(plan)

def post_plan(initial,replan):
    b=segs(initial)
    return b if replan=="SAME" else list(reversed(b)) if replan=="REORDER" else segs("REPART60_40")

def contiguous(units):
    xs=sorted(units)
    if not xs: return []
    out=[]; s=p=xs[0]
    for x in xs[1:]:
        if x==p+1: p=x
        else: out.append(frozenset(range(s,p+1))); s=p=x
    out.append(frozenset(range(s,p+1)))
    return out

class Sink:
    def __init__(self,sc):
        self.first_dedupe_valid=sc["dedupe"]=="VALID"
        self.status_available=sc["status"]=="YES"
        self.verifier_available=sc["verifier"]=="AVAILABLE"
        self.resource_mode=sc["resource_mode"]
        self.dup_obs=sc["dup_obs"]=="YES"
        self.current_epoch=1
        self.apps=[]; self.idem=[]; self.next_id=1

    def _resources(self,units):
        xs=sorted(units)
        if not xs: return []
        chunks=[frozenset(xs)]
        if self.resource_mode=="TWO" and len(xs)>=2:
            m=len(xs)//2
            chunks=[frozenset(xs[:m]),frozenset(xs[m:])]
        out=[]
        for ch in chunks:
            out.append({"id":f"r{self.next_id}","units":ch,"amount":len(ch)})
            self.next_id+=1
        return out

    def _obs(self,recs):
        out=list(recs)
        if self.dup_obs and out: out.append(out[0])
        return out

    def special_first(self,key,contract,outcome):
        if outcome=="AMBIG_NOT_APPLIED":
            return {"confirmed":False,"ambiguous":True,"obs":None}
        if outcome=="AMBIG_PARTIAL":
            xs=sorted(contract); applied=frozenset(xs[:max(1,len(xs)//2)])
        else:
            applied=contract
        recs=self._resources(applied)
        self.apps.append({"key":key,"contract":contract,"applied":applied,"resources":recs,"epoch":1})
        self.idem.append({"key":key,"contract":contract,"resources":recs,"active":self.first_dedupe_valid})
        if outcome=="CONFIRMED_APPLIED":
            return {"confirmed":True,"ambiguous":False,"obs":self._obs(recs)}
        return {"confirmed":False,"ambiguous":True,"obs":None}

    def status(self,key):
        if not self.status_available: return None
        recs=[]
        for a in self.apps:
            if a["key"]==key: recs += a["resources"]
        return self._obs(recs)

    def apply(self,key,contract,epoch):
        if not self.verifier_available: return {"ok":False,"reason":"verifier_outage","obs":None}
        if epoch!=self.current_epoch: return {"ok":False,"reason":"stale_epoch","obs":None}
        for rec in reversed(self.idem):
            if rec["key"]==key and rec["active"]:
                if rec["contract"]!=contract:
                    return {"ok":False,"reason":"idempotency_payload_mismatch","obs":None}
                return {"ok":True,"reason":"idempotent_replay","obs":self._obs(rec["resources"])}
        recs=self._resources(contract)
        self.apps.append({"key":key,"contract":contract,"applied":contract,"resources":recs,"epoch":epoch})
        self.idem.append({"key":key,"contract":contract,"resources":recs,"active":True})
        return {"ok":True,"reason":"applied","obs":self._obs(recs)}

    def truth(self):
        c=Counter()
        for a in self.apps:
            for u in a["applied"]: c[u]+=1
        missing=sum(c[u]==0 for u in UNIVERSE)
        dup=sum(c[u]>1 for u in UNIVERSE)
        total=sum(len(a["applied"]) for a in self.apps)
        return {"missing_units":missing,"duplicated_units":dup,"total_applied_amount":total,
                "exact_once": missing==0 and dup==0 and total==100}

def key(policy,contract,ordinal,epoch):
    if policy=="FULL": return "orig:refund"
    if policy=="ORDINAL": return f"orig:refund:ord{ordinal}"
    xs=sorted(contract); base=f"orig:refund:{xs[0]}-{xs[-1]+1}"
    return base+f":e{epoch}" if policy=="RANGE_EPOCH" else base

def unique_obs(obs):
    if obs is None: return None
    d={}
    for r in obs: d[r["id"]]=r
    return list(d.values())

def cov(obs,dedupe=True):
    if obs is None: return None
    recs=unique_obs(obs) if dedupe else obs
    out=set()
    for r in recs: out.update(r["units"])
    return frozenset(out)

def run_weak(policy,sc):
    sink=Sink(sc); init=segs(sc["initial"]); first=init[0]
    k0=key(policy,first,0,1); fr=sink.special_first(k0,first,sc["first_outcome"])
    done=set()
    if fr["confirmed"]: done.add(k0)
    epoch=2 if sc["takeover"]=="YES" else 1
    if epoch==2: sink.current_epoch=2
    if sc["repeat_kind"]=="YES" and epoch==2:
        sink.apply(key(policy,first,0,1),first,1)
    if sc["verifier"]!="AVAILABLE":
        return {"terminal":False,**sink.truth(),"raw_dup_false_terminal":False}
    if fr["ambiguous"] and sc["status"]=="YES":
        st=sink.status(k0)
        if st: done.add(k0)
    plan=post_plan(sc["initial"],sc["replan"]) if epoch==2 else init
    blocked=False
    for _ in range(2 if sc["repeat_kind"]=="YES" else 1):
        for i,contract in enumerate(plan):
            k=key(policy,contract,i,epoch)
            if k in done: continue
            rr=sink.apply(k,contract,epoch)
            if rr["ok"] and rr["obs"]: done.add(k)
            elif rr["reason"]=="idempotency_payload_mismatch": blocked=True
    req={key(policy,c,i,epoch) for i,c in enumerate(plan)}
    terminal=req.issubset(done) and not blocked
    obs=fr["obs"] if fr["obs"] else sink.status(k0) if sc["status"]=="YES" else None
    raw_false=False
    if obs:
        raw=sum(r["amount"] for r in obs); unique=len(cov(obs,True))
        raw_false=raw>=100 and unique<100
    return {"terminal":terminal,**sink.truth(),"raw_dup_false_terminal":raw_false}

def run_ledger(sc,blind=False):
    sink=Sink(sc); init=segs(sc["initial"]); first=init[0]
    k0=key("RANGE",first,0,1); fr=sink.special_first(k0,first,sc["first_outcome"])
    known=cov(fr["obs"],True) if fr["confirmed"] else frozenset()
    epoch=2 if sc["takeover"]=="YES" else 1
    if epoch==2: sink.current_epoch=2
    if sc["repeat_kind"]=="YES" and epoch==2:
        sink.apply(k0,first,1)
    if sc["verifier"]!="AVAILABLE":
        return {"terminal":False,**sink.truth(),"failclosed":True}
    unresolved=False
    if fr["ambiguous"]:
        if sc["status"]=="YES":
            st=sink.status(k0)
            if st: known=cov(st,True)
            else:
                rr=sink.apply(k0,first,epoch)
                known=cov(rr["obs"],True) if rr["ok"] and rr["obs"] else known
                unresolved=not (rr["ok"] and rr["obs"])
        elif sc["dedupe"]=="VALID":
            rr=sink.apply(k0,first,epoch)
            known=cov(rr["obs"],True) if rr["ok"] and rr["obs"] else known
            unresolved=not (rr["ok"] and rr["obs"])
        elif blind:
            rr=sink.apply(k0,first,epoch)
            known=cov(rr["obs"],True) if rr["ok"] and rr["obs"] else known
            unresolved=not (rr["ok"] and rr["obs"])
        else:
            unresolved=True
    if unresolved:
        return {"terminal":False,**sink.truth(),"failclosed":True}
    remaining=set(UNIVERSE)-set(known)
    plan=post_plan(sc["initial"],sc["replan"]) if epoch==2 else init
    scheduled=set(); residual=[]
    for s in plan:
        part=(set(s)&remaining)-scheduled
        for r in contiguous(part): residual.append(r); scheduled.update(r)
    for r in contiguous(remaining-scheduled): residual.append(r); scheduled.update(r)
    observed=set(known); issued=[]
    for i,contract in enumerate(residual):
        k=key("RANGE",contract,i,epoch); rr=sink.apply(k,contract,epoch)
        if not rr["ok"] or rr["obs"] is None: unresolved=True; break
        observed.update(cov(rr["obs"],True)); issued.append((k,contract))
    if not unresolved and sc["repeat_kind"]=="YES":
        for k,contract in issued:
            rr=sink.apply(k,contract,epoch)
            if not rr["ok"]: unresolved=True; break
    terminal=not unresolved and frozenset(observed)==UNIVERSE
    return {"terminal":terminal,**sink.truth(),"failclosed":not terminal}

AXES={
 "initial":["FULL100","SPLIT40_60"],
 "replan":["SAME","REORDER","REPART60_40"],
 "first_outcome":["CONFIRMED_APPLIED","AMBIG_APPLIED","AMBIG_NOT_APPLIED","AMBIG_PARTIAL"],
 "dedupe":["VALID","EXPIRED"],
 "status":["YES","NO"],
 "takeover":["NO","YES"],
 "verifier":["AVAILABLE","OUTAGE"],
 "resource_mode":["ONE","TWO"],
 "dup_obs":["NO","YES"],
 "repeat_kind":["NO","YES"],
}
SCENARIOS=[dict(zip(AXES,vals)) for vals in product(*AXES.values())]

def summarize(rows):
    return {
      "terminal":sum(r["terminal"] for r in rows),
      "false_terminal":sum(r["terminal"] and not r["exact_once"] for r in rows),
      "exact_once_terminal":sum(r["terminal"] and r["exact_once"] for r in rows),
      "overcomp_terminal":sum(r["terminal"] and r["duplicated_units"]>0 for r in rows),
      "undercomp_terminal":sum(r["terminal"] and r["missing_units"]>0 for r in rows),
      "any_duplicate_effect":sum(r["duplicated_units"]>0 for r in rows),
    }

DETAIL={}
for p in ("FULL","ORDINAL","RANGE","RANGE_EPOCH"):
    DETAIL[p]=[run_weak(p,s) for s in SCENARIOS]
DETAIL["LEDGER_STRONG"]=[run_ledger(s,False) for s in SCENARIOS]
DETAIL["LEDGER_BLIND"]=[run_ledger(s,True) for s in SCENARIOS]

OUT={"scenario_count":len(SCENARIOS),"policies":{p:summarize(r) for p,r in DETAIL.items()}}

def inds(**kw):
    return [i for i,s in enumerate(SCENARIOS) if all(s[k]==v for k,v in kw.items())]
def slice_stats(p,ii):
    r=DETAIL[p]
    return {"n":len(ii),"terminal":sum(r[i]["terminal"] for i in ii),
            "false_terminal":sum(r[i]["terminal"] and not r[i]["exact_once"] for i in ii),
            "duplicate_effect":sum(r[i]["duplicated_units"]>0 for i in ii),
            "undercomp":sum(r[i]["terminal"] and r[i]["missing_units"]>0 for i in ii)}

ii=inds(initial="SPLIT40_60",first_outcome="CONFIRMED_APPLIED",verifier="AVAILABLE")
OUT["slices"]={"full_key_split_confirmed":slice_stats("FULL",ii)}

ii=[i for i,s in enumerate(SCENARIOS) if s["initial"]=="SPLIT40_60" and s["replan"]=="REPART60_40" and s["takeover"]=="YES" and s["verifier"]=="AVAILABLE" and s["first_outcome"] in ("CONFIRMED_APPLIED","AMBIG_APPLIED")]
OUT["slices"]["ordinal_repartition_takeover_applied"]=slice_stats("ORDINAL",ii)
OUT["slices"]["range_repartition_takeover_applied"]=slice_stats("RANGE",ii)

ii=[i for i,s in enumerate(SCENARIOS) if s["takeover"]=="YES" and s["verifier"]=="AVAILABLE" and s["first_outcome"]=="AMBIG_APPLIED" and s["replan"]=="SAME" and s["status"]=="NO"]
OUT["slices"]["range_epoch_takeover_ambiguous_same_plan"]=slice_stats("RANGE_EPOCH",ii)

ii=[i for i,s in enumerate(SCENARIOS) if s["first_outcome"] in ("AMBIG_APPLIED","AMBIG_NOT_APPLIED","AMBIG_PARTIAL") and s["dedupe"]=="EXPIRED" and s["status"]=="NO" and s["verifier"]=="AVAILABLE"]
OUT["slices"]["strong_ambiguous_expired_no_status"]=slice_stats("LEDGER_STRONG",ii)
OUT["slices"]["blind_ambiguous_expired_no_status"]=slice_stats("LEDGER_BLIND",ii)

ii=inds(dup_obs="YES",first_outcome="AMBIG_PARTIAL",initial="FULL100",verifier="AVAILABLE",resource_mode="ONE",status="YES")
OUT["slices"]["raw_resource_duplicate_observation"]={
  "n":len(ii),
  "naive_raw_amount_false_terminal":sum(DETAIL["RANGE"][i]["raw_dup_false_terminal"] for i in ii),
  "strong_unique_resource_id_false_terminal":sum(DETAIL["LEDGER_STRONG"][i]["terminal"] and not DETAIL["LEDGER_STRONG"][i]["exact_once"] for i in ii),
}

ii=inds(repeat_kind="YES",verifier="AVAILABLE")
OUT["slices"]["strong_repeat_same_kind"] = slice_stats("LEDGER_STRONG",ii)

OUT["interpretation"]={
 "scope":"Synthetic finite mechanism lattice; counts are not production failure rates.",
 "strong_rule":"Freeze an attempted segment contract until it is reconciled; dedupe resource observations by durable resource ID; replan only the proven remaining obligation into disjoint immutable ranges; keep claim epoch separate from logical segment identity; fail closed when ambiguous application outlives both durable status and idempotency.",
 "protected_boundary":"An authoritative compensation sink must atomically enforce current writer authority and remaining-obligation conservation, and expose durable enough effect identity/status to reconcile ambiguous partial application."
}
print(json.dumps(OUT,indent=2,sort_keys=True))
