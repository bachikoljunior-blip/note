#!/usr/bin/env python3
"""
Synthetic mechanism study: evidence/capture epochs/rollback proof axes.

Purpose:
- separate artifact validity, presented-chain completeness, capture-scope completeness,
  dependency-edge completeness, and descendant-closure completeness;
- inject self-report omission, receiver suppression, transparency suppression/equivocation,
  unregistered dynamic surfaces, and topology mutation without capture-epoch rollover;
- compare detection layers and rollback policies under deterministic matched distributions.

NOT a production benchmark. Numeric thresholds are not generalizable.
"""

import random
from collections import defaultdict, Counter

SURFACES = [
    "handoff","shared_memory","reducer","conditional_routing",
    "dynamic_tool","custom_wrapper","runtime_tool","reflection"
]
SURFACE_W = {
    "handoff":0.22,"shared_memory":0.18,"reducer":0.14,"conditional_routing":0.12,
    "dynamic_tool":0.11,"custom_wrapper":0.10,"runtime_tool":0.08,"reflection":0.05
}
RUNTIME_RECALL = {
    "handoff":0.995,"shared_memory":0.99,"reducer":0.985,"conditional_routing":0.94,
    "dynamic_tool":0.90,"custom_wrapper":0.78,"runtime_tool":0.92,"reflection":0.72
}
STATIC_RECALL = {
    "handoff":0.99,"shared_memory":0.985,"reducer":0.98,"conditional_routing":0.995,
    "dynamic_tool":0.91,"custom_wrapper":0.80,"runtime_tool":0.76,"reflection":0.62
}

def sample_surface(rng):
    x=rng.random(); c=0.0
    for s,w in SURFACE_W.items():
        c += w
        if x < c: return s
    return "handoff"

def closure(src, adj):
    seen=set(); stack=[src]
    while stack:
        u=stack.pop()
        for v in adj.get(u,()):
            if v not in seen:
                seen.add(v); stack.append(v)
    return seen

def make_dag(seed,n=32):
    rng=random.Random(seed)
    edges=[]; adj=defaultdict(set)
    for i in range(n-1):
        if rng.random()<0.78:
            j=rng.randint(i+1,min(n-1,i+4))
            s=sample_surface(rng)
            edges.append((i,j,s)); adj[i].add(j)
    for i in range(n):
        for j in range(i+2,n):
            if rng.random()<0.032:
                s=sample_surface(rng)
                edges.append((i,j,s)); adj[i].add(j)
    src=rng.randint(0,7)
    true_cl=closure(src,adj)
    if not true_cl:
        j=src+1; edges.append((src,j,"handoff")); adj[src].add(j)
        true_cl=closure(src,adj)
    return n,edges,src,true_cl

def simulate(seed):
    rng=random.Random(seed*1_000_003+911)
    n,edges,src,true_cl=make_dag(seed)
    active_surfaces={s for _,_,s in edges}

    # Capture epoch / topology mutation.
    topology_mutates = rng.random()<0.18
    topology_change = rng.choice(["split","merge"]) if topology_mutates else "none"
    epoch_rollover = (not topology_mutates) or (rng.random()<0.92)
    epoch_current = epoch_rollover

    # Mandatory registry intended, but dynamic registration may still be bypassed.
    registered={"handoff","shared_memory","reducer","conditional_routing"}
    mediated=set(registered)
    unknown=set()
    for s in ("dynamic_tool","custom_wrapper","runtime_tool","reflection"):
        if s not in active_surfaces: continue
        p_reg={"dynamic_tool":0.985,"custom_wrapper":0.96,
               "runtime_tool":0.975,"reflection":0.95}[s]
        if rng.random()<p_reg:
            registered.add(s); mediated.add(s)
        else:
            unknown.add(s)

    observed=defaultdict(set)
    static=defaultdict(set)
    captured=[]
    true_pairs={(u,v) for u,v,_ in edges}
    for idx,(u,v,s) in enumerate(edges):
        rp=RUNTIME_RECALL[s] if (s in mediated and epoch_current) else 0.0
        if rng.random()<rp:
            observed[u].add(v); captured.append((idx,u,v,s))
        if rng.random()<STATIC_RECALL[s]:
            static[u].add(v)
    # Conservative static overcapture.
    for u in range(n):
        for v in range(u+1,n):
            if (u,v) not in true_pairs and rng.random()<0.006:
                static[u].add(v)

    # Receipt sequence numbers are scoped to the governed/mediated boundary.
    # Unmediated activity therefore does NOT create a gap in the self-reported chain.
    mediated_events=[e for e in edges if e[2] in mediated and epoch_current]
    mediated_ids=list(range(len(mediated_events)))

    # Self-reported chain defects.
    self_ids=list(mediated_ids)
    defect_flags=set()
    r=rng.random()
    if self_ids:
        if r<0.05:
            defect_flags.add("middle_self_omission")
            k=rng.choice(self_ids[1:-1] or self_ids); self_ids.remove(k)
        elif r<0.10:
            defect_flags.add("tail_self_suppression")
            cut=max(1,int(len(self_ids)*rng.uniform(0.05,0.20)))
            self_ids=self_ids[:-cut]
        elif r<0.13:
            defect_flags.add("duplicate")
            self_ids.insert(rng.randrange(len(self_ids)),rng.choice(self_ids))
        elif r<0.16:
            defect_flags.add("reorder")
            if len(self_ids)>=2:
                a=rng.randrange(len(self_ids)-1)
                self_ids[a],self_ids[a+1]=self_ids[a+1],self_ids[a]

    # Receiver-attested receipts. Receiver-side suppression remains possible.
    receiver_ids=list(mediated_ids)
    if receiver_ids and rng.random()<0.035:
        defect_flags.add("receiver_suppression")
        receiver_ids.remove(rng.choice(receiver_ids))

    # Transparency publication / checkpoint.
    log_ids=list(receiver_ids)
    if log_ids and rng.random()<0.025:
        defect_flags.add("transparency_suppression")
        log_ids.remove(rng.choice(log_ids))
    witness_equivocation = rng.random()<0.015
    if witness_equivocation:
        defect_flags.add("equivocation")

    self_close = rng.random()<0.88
    witness_close = rng.random()<0.96

    if unknown: defect_flags.add("unregistered_surface")
    if topology_mutates and not epoch_rollover:
        defect_flags.add("stale_capture_epoch")

    # Presented self-chain structure.
    self_unique=len(self_ids)==len(set(self_ids))
    self_ordered=all(self_ids[i]<self_ids[i+1] for i in range(len(self_ids)-1))
    self_contiguous=(self_ids==list(range(self_ids[0],self_ids[-1]+1))) if self_ids else True
    artifact_valid=self_unique and self_ordered
    presented_chain_complete=artifact_valid and self_contiguous

    signals=set()
    if not artifact_valid or not presented_chain_complete:
        signals.add("self_chain_invalid")
    if self_close and self_ids and mediated_ids and max(self_ids)!=max(mediated_ids):
        signals.add("self_close_head_mismatch")
    if set(self_ids)!=set(receiver_ids):
        signals.add("receiver_mismatch")
    if set(log_ids)!=set(receiver_ids):
        signals.add("transparency_log_mismatch")
    if witness_close and set(log_ids)!=set(receiver_ids):
        signals.add("witness_checkpoint_mismatch")
    if witness_equivocation and rng.random()<0.93:
        signals.add("equivocation_detected")

    # Coarse external activity sentinel: detects capture bypass, with false positives.
    if unknown or (topology_mutates and not epoch_rollover):
        if rng.random()<0.90:
            signals.add("unmatched_activity")
    elif rng.random()<0.025:
        signals.add("sentinel_false_positive")

    if unknown: signals.add("unknown_surface")
    if topology_mutates and not epoch_rollover: signals.add("stale_epoch")

    obs_cl=closure(src,observed)
    st_cl=closure(src,static)
    union_cl=obs_cl|st_cl

    # Five proof axes.
    capture_scope_complete=(
        not unknown and epoch_current and self_close and witness_close and
        len(receiver_ids)==len(mediated_ids) and
        len(log_ids)==len(receiver_ids) and
        not witness_equivocation
    )
    observed_pairs={(u,v) for u,vs in observed.items() for v in vs}
    dependency_edges_complete=true_pairs.issubset(observed_pairs)
    descendant_closure_complete=true_cl.issubset(union_cl)

    # An intentionally weaker epoch-blind pseudo-manifest.
    epoch_blind_manifest=(
        not unknown and self_close and witness_close and
        len(receiver_ids)==len(mediated_ids) and
        len(log_ids)==len(receiver_ids) and
        not witness_equivocation
    )

    return {
        "n":n,"src":src,"true_cl":true_cl,"obs_cl":obs_cl,"union_cl":union_cl,
        "defect_flags":defect_flags,"signals":signals,
        "artifact_valid":artifact_valid,
        "presented_chain_complete":presented_chain_complete,
        "capture_scope_complete":capture_scope_complete,
        "dependency_edges_complete":dependency_edges_complete,
        "descendant_closure_complete":descendant_closure_complete,
        "epoch_blind_manifest":epoch_blind_manifest,
        "topology_mutates":topology_mutates,
        "epoch_rollover":epoch_rollover,
    }

DETECTION_MODES={
    "self_chain":{
        "self_chain_invalid","self_close_head_mismatch"
    },
    "receiver_attested":{
        "self_chain_invalid","self_close_head_mismatch","receiver_mismatch"
    },
    "transparency":{
        "self_chain_invalid","self_close_head_mismatch","receiver_mismatch",
        "transparency_log_mismatch","witness_checkpoint_mismatch","equivocation_detected"
    },
    "combined_plus_sentinel":{
        "self_chain_invalid","self_close_head_mismatch","receiver_mismatch",
        "transparency_log_mismatch","witness_checkpoint_mismatch","equivocation_detected",
        "unmatched_activity","unknown_surface","stale_epoch","sentinel_false_positive"
    }
}

def detected(run,mode):
    return bool(run["signals"] & DETECTION_MODES[mode])

def replay_set(run,policy):
    whole=set(range(run["n"]))-{run["src"]}
    if policy=="absence_as_safe":
        return set(run["obs_cl"])
    if policy=="warning_only":
        return whole if run["signals"] else set(run["union_cl"])
    if policy=="epoch_blind_manifest":
        return set(run["union_cl"]) if run["epoch_blind_manifest"] else whole
    if policy=="positive_capture_scope":
        return set(run["union_cl"]) if run["capture_scope_complete"] else whole
    if policy=="positive_scope_and_edges":
        ok=run["capture_scope_complete"] and run["dependency_edges_complete"]
        return set(run["union_cl"]) if ok else whole
    if policy=="positive_scope_and_closure":
        ok=run["capture_scope_complete"] and run["descendant_closure_complete"]
        return set(run["union_cl"]) if ok else whole
    if policy=="whole":
        return whole
    raise ValueError(policy)

POLICIES=[
    "absence_as_safe","warning_only","epoch_blind_manifest",
    "positive_capture_scope","positive_scope_and_edges",
    "positive_scope_and_closure","whole"
]

def safe_div(a,b):
    return a/b if b else 0.0

def evaluate(n_runs=50_000):
    det={m:Counter() for m in DETECTION_MODES}
    per_flag={m:defaultdict(lambda:[0,0]) for m in DETECTION_MODES}
    roll={p:[0,0] for p in POLICIES}
    proof=Counter()
    topo=defaultdict(lambda:Counter())

    for seed in range(n_runs):
        run=simulate(seed)
        gt=bool(run["defect_flags"])

        for axis in ("artifact_valid","presented_chain_complete","capture_scope_complete",
                     "dependency_edges_complete","descendant_closure_complete"):
            proof[axis]+=int(run[axis])

        for mode in DETECTION_MODES:
            pred=detected(run,mode)
            if pred and gt: det[mode]["tp"]+=1
            elif pred and not gt: det[mode]["fp"]+=1
            elif not pred and gt: det[mode]["fn"]+=1
            else: det[mode]["tn"]+=1
            for flag in run["defect_flags"]:
                per_flag[mode][flag][1]+=1
                per_flag[mode][flag][0]+=int(pred)

        for p in POLICIES:
            r=replay_set(run,p)
            ok=run["true_cl"].issubset(r)
            roll[p][0]+=int(ok); roll[p][1]+=len(r)
            if run["topology_mutates"]:
                key="rolled" if run["epoch_rollover"] else "stale"
                topo[p][key+"_n"]+=1
                topo[p][key+"_ok"]+=int(ok)

    return det,per_flag,roll,proof,topo

def print_results(n_runs=50_000):
    det,per_flag,roll,proof,topo=evaluate(n_runs)

    print("DETECTION")
    print("mode,precision,recall,false_positive_rate")
    for mode,c in det.items():
        precision=safe_div(c["tp"],c["tp"]+c["fp"])
        recall=safe_div(c["tp"],c["tp"]+c["fn"])
        fpr=safe_div(c["fp"],c["fp"]+c["tn"])
        print(f"{mode},{precision:.6f},{recall:.6f},{fpr:.6f}")

    print("\nDEFECT_RECALL_BY_MODE")
    flags=sorted({f for mode in per_flag.values() for f in mode.keys()})
    print("flag,"+",".join(DETECTION_MODES.keys()))
    for flag in flags:
        vals=[]
        for mode in DETECTION_MODES:
            hit,total=per_flag[mode][flag]
            vals.append(f"{safe_div(hit,total):.6f}")
        print(flag+","+",".join(vals))

    print("\nPROOF_AXIS_PREVALENCE")
    for k,v in proof.items():
        print(f"{k},{v/n_runs:.6f}")

    print("\nROLLBACK")
    print("policy,recovery,mean_replay_cost,correct_endpoints_per_100k_cost")
    for p,(ok,cost) in roll.items():
        rec=ok/n_runs
        mean=cost/n_runs
        eff=safe_div(ok,cost)*100_000
        print(f"{p},{rec:.6f},{mean:.6f},{eff:.3f}")

    print("\nTOPOLOGY_MUTATION_RECOVERY")
    print("policy,proper_rollover,stale_epoch")
    for p,c in topo.items():
        good=safe_div(c["rolled_ok"],c["rolled_n"])
        stale=safe_div(c["stale_ok"],c["stale_n"])
        print(f"{p},{good:.6f},{stale:.6f}")

if __name__=="__main__":
    print_results()
