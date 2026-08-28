#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

SINKS=["non_idempotent","finite_idempotency","durable_effect_id","cooperative_authority_epoch"]
TOKEN=["fresh","expired"]
OUTCOMES=["ok","ambiguous_applied","ambiguous_not_applied"]
CRASHES=["none","after_effect_before_local_record"]
REVOCATIONS=["none","before_sink_check","after_sink_check_before_call"]
TAKEOVERS=["none","dispatcher_takeover"]
WIDTHS=["one_sink","two_sinks"]
SECOND=["ok","blocked"]
REL=["disjoint","overlap"]

def scenarios():
    ks=["sink","token","outcome","crash","revocation","takeover","width","second","relation"]
    return [dict(zip(ks,v)) for v in product(SINKS,TOKEN,OUTCOMES,CRASHES,REVOCATIONS,TAKEOVERS,WIDTHS,SECOND,REL)]

def base():
    return dict(terminal=False,unsafe=False,duplicate_effect=False,stale_effect=False,ambiguous_effect=False,partial_effect=False,structural_block=False,recovery_reads=0,recovery_writes=0,parallel_dispatch=False,serialized_dispatch=False)

def finite_dedup(s): return s["sink"]=="finite_idempotency" and s["token"]=="fresh"
def durable_dedup(s): return s["sink"] in ("durable_effect_id","cooperative_authority_epoch")
def ambiguous(s): return s["outcome"]!="ok" or s["crash"]=="after_effect_before_local_record"
def first_applied(s): return s["outcome"] in ("ok","ambiguous_applied")
def multisink(r,s,first):
    if s["width"]=="two_sinks" and s["second"]=="blocked" and first:
        r["partial_effect"]=True; return False
    return True

def direct_blind_retry(s):
    r=base(); first=first_applied(s)
    if s["revocation"]!="none" and first: r["stale_effect"]=r["unsafe"]=True
    if ambiguous(s):
        r["recovery_writes"]+=1
        if first and not (finite_dedup(s) or durable_dedup(s)): r["duplicate_effect"]=r["unsafe"]=True
    if s["takeover"]!="none" and first and not (finite_dedup(s) or durable_dedup(s)): r["duplicate_effect"]=r["unsafe"]=True
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def tx_outbox_only(s):
    r=base(); first=first_applied(s)
    r["recovery_reads"]+=int(ambiguous(s) or s["takeover"]!="none")
    if s["revocation"]!="none" and first: r["stale_effect"]=r["unsafe"]=True
    if (ambiguous(s) or s["takeover"]!="none") and first and not durable_dedup(s): r["duplicate_effect"]=r["unsafe"]=True
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def outbox_finite_transport(s):
    r=base(); first=first_applied(s)
    r["recovery_reads"]+=int(ambiguous(s) or s["takeover"]!="none")
    if s["revocation"]!="none" and first: r["stale_effect"]=r["unsafe"]=True
    if (ambiguous(s) or s["takeover"]!="none") and first and not (finite_dedup(s) or durable_dedup(s)): r["duplicate_effect"]=r["unsafe"]=True
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def fenced_recheck(s,fail_closed=False):
    r=base(); first=first_applied(s)
    if s["takeover"]!="none": r["recovery_reads"]+=1
    if s["revocation"]=="before_sink_check": return r
    if s["revocation"]=="after_sink_check_before_call" and first: r["stale_effect"]=r["unsafe"]=True
    if ambiguous(s):
        r["recovery_reads"]+=1
        if first and not (finite_dedup(s) or durable_dedup(s)):
            r["ambiguous_effect"]=True
            if fail_closed: return r
            r["duplicate_effect"]=r["unsafe"]=True
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def durable_effect_id_sink(s):
    r=base()
    if s["sink"] not in ("durable_effect_id","cooperative_authority_epoch"): r["structural_block"]=True; return r
    first=first_applied(s)
    if s["revocation"]=="before_sink_check": return r
    if s["revocation"]=="after_sink_check_before_call" and first: r["stale_effect"]=r["unsafe"]=True
    if ambiguous(s) or s["takeover"]!="none": r["recovery_reads"]+=1
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def cooperative_sink(s):
    r=base()
    if s["sink"]!="cooperative_authority_epoch": r["structural_block"]=True; return r
    first=first_applied(s)
    if s["revocation"]!="none": return r
    if ambiguous(s) or s["takeover"]!="none": r["recovery_reads"]+=1
    if multisink(r,s,first): r["terminal"]=True
    if s["relation"]=="disjoint" and s["width"]=="two_sinks": r["parallel_dispatch"]=True
    return r

def staged_serial(s):
    r=base(); first=first_applied(s); r["serialized_dispatch"]=True
    if s["revocation"]=="before_sink_check": return r
    if s["revocation"]=="after_sink_check_before_call" and first: r["stale_effect"]=r["unsafe"]=True
    if ambiguous(s):
        r["recovery_reads"]+=1
        if first and not durable_dedup(s): r["ambiguous_effect"]=True; r["duplicate_effect"]=r["unsafe"]=True
    if multisink(r,s,first) and not r["unsafe"]: r["terminal"]=True
    return r

P={
 "NEG_direct_blind_retry":direct_blind_retry,
 "transactional_outbox_only":tx_outbox_only,
 "outbox_finite_transport_idemp":outbox_finite_transport,
 "fenced_dispatcher_sink_recheck":lambda s:fenced_recheck(s,False),
 "fenced_dispatcher_fail_closed":lambda s:fenced_recheck(s,True),
 "durable_effect_id_sink":durable_effect_id_sink,
 "cooperative_sink_authority_epoch":cooperative_sink,
 "staged_serial_integrator":staged_serial,
}

def summary(rows):
    out={}
    for n,f in P.items():
        c=Counter(); sums=Counter()
        for s in rows:
            for k,v in f(s).items():
                if isinstance(v,bool): c[k]+=int(v)
                else: sums[k]+=v
        out[n]={**c,**{f"sum_{k}":v for k,v in sums.items()}}
    return out

def sl(rows,p):
    ss=[s for s in rows if p(s)]; return {"count":len(ss),"protocols":summary(ss)}

def main():
    rows=scenarios()
    print(json.dumps({
      "scenario_count":len(rows),
      "protocol_summary":summary(rows),
      "targeted_slices":{
        "nonidempotent_ambiguous_applied_crash":sl(rows,lambda s:s["sink"]=="non_idempotent" and s["outcome"]=="ambiguous_applied" and s["crash"]=="after_effect_before_local_record" and s["revocation"]=="none" and s["takeover"]=="none"),
        "finite_idemp_expired_ambiguous":sl(rows,lambda s:s["sink"]=="finite_idempotency" and s["token"]=="expired" and s["outcome"]=="ambiguous_applied" and s["crash"]=="after_effect_before_local_record" and s["revocation"]=="none"),
        "revocation_after_check":sl(rows,lambda s:s["revocation"]=="after_sink_check_before_call" and s["outcome"] in ("ok","ambiguous_applied")),
        "two_sink_second_blocked":sl(rows,lambda s:s["width"]=="two_sinks" and s["second"]=="blocked" and s["outcome"] in ("ok","ambiguous_applied")),
        "nominal":sl(rows,lambda s:s["revocation"]=="none" and s["takeover"]=="none" and s["outcome"]=="ok" and s["crash"]=="none" and (s["width"]=="one_sink" or s["second"]=="ok"))},
      "scope_notes":["Synthetic equal-weight mechanism counts, not production probabilities.","Transactional outbox is durable local intent only; it does not inherit exactly-once external side effects.","Finite transport idempotency protects only while the sink honors the key within its retention window.","Durable effect ID at sink closes duplicate retry ambiguity but not authority revocation after a separate local check.","Cooperative sink authority epoch assumes authority validation and durable effect-ID consumption are atomic with effect application.","Partial multi-sink effects are measured separately from duplicate/stale effects."]},indent=2,sort_keys=True))
if __name__=="__main__": main()
