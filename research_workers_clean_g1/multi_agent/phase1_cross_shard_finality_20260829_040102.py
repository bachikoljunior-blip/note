#!/usr/bin/env python3
from itertools import product, permutations
from collections import Counter
import json

WIDTHS=["small80","wide120"]
OVERLAPS=["disjoint","one_shard","multi_shard"]
ROOT_PRE=["PENDING","STAGING"]
RACES=["none","shard1_takeover_after_verify","shard2_expiry_after_verify","shard3_takeover_after_verify","parent_supersede_before_root_commit","coordinator_takeover_before_root_commit"]
OUTCOMES=["ok","ambiguous_applied","ambiguous_not_applied"]
TOKENS=["fresh","expired"]
RESTARTS=["full_state","reservation_only"]
CLEANUPS=["none","partial_cleanup_then_overlap"]

def scenarios():
    keys=["width","overlap","root_pre","race","outcome","token","restart","cleanup"]
    return [dict(zip(keys,v)) for v in product(WIDTHS,OVERLAPS,ROOT_PRE,RACES,OUTCOMES,TOKENS,RESTARTS,CLEANUPS)]

def base():
    return dict(terminal=False,unsafe_terminal=False,duplicate_effect=False,orphan=False,structural_block=False,race_exposure=False,recovery_reads=0,recovery_writes=0,parallel_effect_admit=False,serialized_effect_admit=False,stale_root_committed=False)

def neg_root_committed_trust(s):
    r=base()
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=1
    if s["outcome"]=="ambiguous_not_applied": r["recovery_writes"]+=1
    r["terminal"]=True
    if s["overlap"]=="disjoint": r["parallel_effect_admit"]=True
    if s["race"]!="none":
        r["race_exposure"]=r["unsafe_terminal"]=r["stale_root_committed"]=True
        if s["cleanup"]=="partial_cleanup_then_overlap" and s["overlap"]!="disjoint" and s["race"].startswith("shard"):
            r["duplicate_effect"]=True
    return r

def atomic_compare_root_commit(s):
    r=base()
    if s["width"]=="wide120": r["structural_block"]=True; return r
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=1
    if s["race"]!="none": return r
    if s["outcome"]=="ambiguous_not_applied": r["recovery_writes"]+=1
    r["terminal"]=True
    if s["overlap"]=="disjoint": r["parallel_effect_admit"]=True
    return r

def hierarchical_naive_cert(s):
    r=base()
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=2
    if s["outcome"]=="ambiguous_not_applied": r["recovery_writes"]+=1
    if s["race"] in ("parent_supersede_before_root_commit","coordinator_takeover_before_root_commit"): return r
    r["terminal"]=True
    if s["overlap"]=="disjoint": r["parallel_effect_admit"]=True
    if s["race"].startswith("shard"):
        r["race_exposure"]=r["unsafe_terminal"]=r["stale_root_committed"]=True
        if s["cleanup"]=="partial_cleanup_then_overlap" and s["overlap"]!="disjoint": r["duplicate_effect"]=True
    return r

def hierarchical_fenced_cert(s):
    r=base()
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=2
    if s["race"]!="none": return r
    if s["outcome"]=="ambiguous_not_applied": r["recovery_writes"]+=1
    r["terminal"]=True
    if s["overlap"]=="disjoint": r["parallel_effect_admit"]=True
    return r

def sink_time_revalidate(s):
    r=base()
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=1
    if s["race"]!="none": r["recovery_reads"]+=3; return r
    r["terminal"]=True
    if s["overlap"]=="disjoint": r["parallel_effect_admit"]=True
    return r

def staged_fenced_integrator(s):
    r=base()
    if s["outcome"]!="ok" or s["restart"]=="reservation_only": r["recovery_reads"]+=1
    if s["race"]=="parent_supersede_before_root_commit": return r
    if s["race"]=="coordinator_takeover_before_root_commit": r["recovery_reads"]+=1
    r["terminal"]=True; r["serialized_effect_admit"]=True
    return r

PROTOCOLS={
 "NEG_root_committed_trust":neg_root_committed_trust,
 "atomic_compare_root_commit<=100":atomic_compare_root_commit,
 "hierarchical_naive_cert":hierarchical_naive_cert,
 "hierarchical_fenced_cert":hierarchical_fenced_cert,
 "sink_time_revalidate":sink_time_revalidate,
 "staged_fenced_integrator":staged_fenced_integrator,
}

def summarize(rows):
    out={}
    for name,fn in PROTOCOLS.items():
        c=Counter(); sums=Counter()
        for s in rows:
            for k,v in fn(s).items():
                if isinstance(v,bool): c[k]+=int(v)
                else: sums[k]+=v
        out[name]={**c,**{f"sum_{k}":v for k,v in sums.items()}}
    return out

def slice_stats(rows,pred):
    ss=[s for s in rows if pred(s)]
    return {"count":len(ss),"protocols":summarize(ss)}

def acquisition_sim(a,b,mode,max_steps=100):
    orders={"A":a,"B":b}; idx={"A":0,"B":0}; held={}; done={"A":False,"B":False}; aborts={"A":0,"B":0}; waits={"A":False,"B":False}
    for t in range(max_steps):
        w="A" if t%2==0 else "B"
        if done[w]: continue
        sh=orders[w][idx[w]]; owner=held.get(sh)
        if owner is None or owner==w:
            held[sh]=w; idx[w]+=1; waits[w]=False
            if idx[w]>=3:
                done[w]=True
                for k in [k for k,v in held.items() if v==w]: del held[k]
                waits["A"]=waits["B"]=False
        elif mode=="hold_wait":
            waits[w]=True
            if waits["A"] and waits["B"]: return "deadlock",sum(aborts.values())
        else:
            aborts[w]+=1
            for k in [k for k,v in held.items() if v==w]: del held[k]
            idx[w]=0; waits[w]=False
        if done["A"] and done["B"]: return "both_done",sum(aborts.values())
    return "incomplete",sum(aborts.values())

def main():
    rows=scenarios()
    slices={
      "verification_to_commit_shard_race":slice_stats(rows,lambda s:s["race"].startswith("shard")),
      "authority_race_all":slice_stats(rows,lambda s:s["race"]!="none"),
      "wide_shard_race_overlap_cleanup":slice_stats(rows,lambda s:s["width"]=="wide120" and s["race"].startswith("shard") and s["overlap"]!="disjoint" and s["cleanup"]=="partial_cleanup_then_overlap"),
      "nominal_no_race":slice_stats(rows,lambda s:s["race"]=="none"),
      "reservation_only_ambiguous":slice_stats(rows,lambda s:s["restart"]=="reservation_only" and s["outcome"]!="ok"),
    }
    ps=list(permutations(["s1","s2","s3"])); micro={}
    for mode in ("hold_wait","abort_on_conflict"):
        counts=Counter(); ah=Counter()
        for a in ps:
            for b in ps:
                st,n=acquisition_sim(a,b,mode); counts[st]+=1; ah[n]+=1
        micro[mode]={"status":dict(counts),"abort_count_histogram":dict(ah)}
    st,n=acquisition_sim(("s1","s2","s3"),("s1","s2","s3"),"hold_wait")
    micro["canonical_global_order"]={"status":st,"aborts":n}
    print(json.dumps({"scenario_count":len(rows),"factors":{"width":WIDTHS,"overlap":OVERLAPS,"root_pre":ROOT_PRE,"race":RACES,"outcome":OUTCOMES,"token":TOKENS,"restart":RESTARTS,"cleanup":CLEANUPS},"protocol_summary":summarize(rows),"targeted_slices":slices,"acquisition_order_microtest":micro,"scope_notes":["Counts are equal-weight synthetic mechanism counts, not incident probabilities.","atomic_compare_root_commit is only positive inside the modeled bounded transaction envelope.","hierarchical_fenced_cert assumes shard authority transition and group-cert invalidation are atomic in one authority domain.","sink_time_revalidate proves current authority at each effect sink but does not prove all-or-nothing external-effect semantics across sinks.","staged_fenced_integrator assumes one current integrator epoch and durable publication identity, as tested in earlier role-local leaves."]},indent=2,sort_keys=True))

if __name__=="__main__": main()
