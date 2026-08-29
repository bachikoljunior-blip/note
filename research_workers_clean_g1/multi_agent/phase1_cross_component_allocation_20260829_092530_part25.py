#!/usr/bin/env python3
from itertools import product
import json

RES=("R1","R2")
ALLOC1={"R1":30,"R2":30}
ALLOC2={
    "SWAP":{"R1":20,"R2":40},
    "SHIFT":{"R1":40,"R2":20},
    "ABA":{"R1":30,"R2":30},
}
EVENTS=["NONE"]+[f"{stage}_{kind}" for stage in ("BEFORE_FIRST","BETWEEN","AFTER_SECOND") for kind in ("SWAP","SHIFT","ABA")]
AXES={
    "event":EVENTS,
    "order":["R1_FIRST","R2_FIRST"],
    "gen_verifier":["AVAILABLE","OUTAGE"],
    "takeover":["NO","YES"],
    "cas":["CONFIRMED_APPLIED","AMBIG_APPLIED","AMBIG_NOT_APPLIED"],
    "repeat":["NO","YES"],
}
SCENARIOS=[dict(zip(AXES,v)) for v in product(*AXES.values())]


def parse_event(ev):
    if ev=="NONE": return None,None
    for kind in ("SWAP","SHIFT","ABA"):
        if ev.endswith("_"+kind): return ev[:-(len(kind)+1)],kind
    raise ValueError(ev)


def change(state,kind):
    state["gen"]=2
    state["alloc"]=dict(ALLOC2[kind])


def token(resource,state):
    return {
        "resource":resource,
        "amount":state["alloc"][resource],
        "allocation_generation":state["gen"],
        "allocation_digest":tuple(state["alloc"][r] for r in RES),
    }


def truth(tokens,state):
    by={t["resource"]:t["amount"] for t in tokens}
    values_ok=all(by.get(r)==state["alloc"][r] for r in RES)
    generation_ok=all(t["allocation_generation"]==state["gen"] for t in tokens)
    return values_ok and generation_ok,values_ok,generation_ok


def repository_terminal(decide,safe,sc):
    if not decide:
        return {"terminal":False,"unsafe_terminal":False,"repo_writes":0}
    if sc["cas"] in ("CONFIRMED_APPLIED","AMBIG_APPLIED"):
        return {"terminal":True,"unsafe_terminal":not safe,"repo_writes":1}
    if sc["repeat"]=="YES":
        return {"terminal":True,"unsafe_terminal":not safe,"repo_writes":1}
    return {"terminal":False,"unsafe_terminal":False,"repo_writes":0}


def local_only(sc):
    state={"gen":1,"alloc":dict(ALLOC1)}
    stage,kind=parse_event(sc["event"])
    order=RES if sc["order"]=="R1_FIRST" else tuple(reversed(RES))
    if stage=="BEFORE_FIRST": change(state,kind)
    tokens=[token(order[0],state)]
    if stage=="BETWEEN": change(state,kind)
    tokens.append(token(order[1],state))
    if stage=="AFTER_SECOND": change(state,kind)
    safe,values_ok,generation_ok=truth(tokens,state)
    out=repository_terminal(True,safe,sc)
    out.update({"values_ok":values_ok,"generation_ok":generation_ok})
    return out


def value_digest_only(sc):
    state={"gen":1,"alloc":dict(ALLOC1)}
    stage,kind=parse_event(sc["event"])
    order=RES if sc["order"]=="R1_FIRST" else tuple(reversed(RES))
    if stage=="BEFORE_FIRST": change(state,kind)
    tokens=[token(order[0],state)]
    if stage=="BETWEEN": change(state,kind)
    tokens.append(token(order[1],state))
    if stage=="AFTER_SECOND": change(state,kind)
    safe,values_ok,generation_ok=truth(tokens,state)
    if sc["gen_verifier"]!="AVAILABLE":
        out=repository_terminal(False,safe,sc)
    else:
        current_digest=tuple(state["alloc"][r] for r in RES)
        out=repository_terminal(all(t["allocation_digest"]==current_digest for t in tokens),safe,sc)
    out.update({"values_ok":values_ok,"generation_ok":generation_ok})
    return out


def generation_bound_recheck(sc):
    state={"gen":1,"alloc":dict(ALLOC1)}
    stage,kind=parse_event(sc["event"])
    order=RES if sc["order"]=="R1_FIRST" else tuple(reversed(RES))
    if stage=="BEFORE_FIRST": change(state,kind)
    tokens=[token(order[0],state)]
    if stage=="BETWEEN": change(state,kind)
    tokens.append(token(order[1],state))
    if stage=="AFTER_SECOND": change(state,kind)
    safe,values_ok,generation_ok=truth(tokens,state)
    if sc["gen_verifier"]!="AVAILABLE":
        out=repository_terminal(False,safe,sc)
    else:
        current_digest=tuple(state["alloc"][r] for r in RES)
        decide=all(t["allocation_generation"]==state["gen"] and t["allocation_digest"]==current_digest for t in tokens)
        out=repository_terminal(decide,safe,sc)
    out.update({"values_ok":values_ok,"generation_ok":generation_ok})
    return out


def frozen_allocation_contract(sc):
    # The allocation contract is precommitted immutable for this parent generation.
    # Attempts to reallocate the same generation are rejected; legitimate reallocation must create a new generation.
    state={"gen":1,"alloc":dict(ALLOC1)}
    order=RES if sc["order"]=="R1_FIRST" else tuple(reversed(RES))
    tokens=[token(r,state) for r in order]
    safe,values_ok,generation_ok=truth(tokens,state)
    out=repository_terminal(True,safe,sc)
    out.update({"values_ok":values_ok,"generation_ok":generation_ok})
    return out


def vector_allocation_seal(sc):
    state={"gen":1,"alloc":dict(ALLOC1)}
    stage,kind=parse_event(sc["event"])
    # Changes before the one vector seal are incorporated; after sealing they are rejected for this generation.
    if stage in ("BEFORE_FIRST","BETWEEN"): change(state,kind)
    tokens=[token(r,state) for r in RES]
    safe,values_ok,generation_ok=truth(tokens,state)
    out=repository_terminal(True,safe,sc)
    out.update({"values_ok":values_ok,"generation_ok":generation_ok})
    return out


DETAIL={
    "PER_RESOURCE_LOCAL_ONLY":[local_only(s) for s in SCENARIOS],
    "VALUE_DIGEST_ONLY":[value_digest_only(s) for s in SCENARIOS],
    "GENERATION_BOUND_RECHECK":[generation_bound_recheck(s) for s in SCENARIOS],
    "FROZEN_ALLOCATION_CONTRACT":[frozen_allocation_contract(s) for s in SCENARIOS],
    "VECTOR_ALLOCATION_SEAL":[vector_allocation_seal(s) for s in SCENARIOS],
}


def summarize(rows):
    return {
        "terminal":sum(r["terminal"] for r in rows),
        "unsafe_terminal":sum(r["unsafe_terminal"] for r in rows),
        "safe_terminal":sum(r["terminal"] and not r["unsafe_terminal"] for r in rows),
        "duplicate_repository_transition":sum(r["repo_writes"]>1 for r in rows),
    }


def select(pred): return [i for i,s in enumerate(SCENARIOS) if pred(s)]
def slice_stats(policy,idx):
    rows=DETAIL[policy]
    return {
        "n":len(idx),
        "terminal":sum(rows[i]["terminal"] for i in idx),
        "unsafe_terminal":sum(rows[i]["unsafe_terminal"] for i in idx),
        "safe_terminal":sum(rows[i]["terminal"] and not rows[i]["unsafe_terminal"] for i in idx),
    }

OUT={"scenario_count":len(SCENARIOS),"policies":{p:summarize(r) for p,r in DETAIL.items()},"slices":{}}

idx=select(lambda s:s["event"] in ("BETWEEN_SWAP","BETWEEN_SHIFT") and s["gen_verifier"]=="AVAILABLE" and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["between_reallocation_local_only"]=slice_stats("PER_RESOURCE_LOCAL_ONLY",idx)
OUT["slices"]["between_reallocation_generation_bound"]=slice_stats("GENERATION_BOUND_RECHECK",idx)

idx=select(lambda s:s["event"]=="AFTER_SECOND_ABA" and s["gen_verifier"]=="AVAILABLE" and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["aba_value_digest_only"]=slice_stats("VALUE_DIGEST_ONLY",idx)
OUT["slices"]["aba_generation_bound"]=slice_stats("GENERATION_BOUND_RECHECK",idx)

idx=select(lambda s:s["event"].startswith("BEFORE_FIRST") and s["gen_verifier"]=="AVAILABLE" and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["new_generation_before_work_generation_bound"]=slice_stats("GENERATION_BOUND_RECHECK",idx)
OUT["slices"]["new_generation_before_work_vector_seal"]=slice_stats("VECTOR_ALLOCATION_SEAL",idx)

idx=select(lambda s:s["cas"] in ("AMBIG_APPLIED","AMBIG_NOT_APPLIED") and s["repeat"]=="YES")
OUT["slices"]["ambiguous_repo_cas_repeat"]={
    "n":len(idx),
    "max_repository_writes":max(DETAIL["GENERATION_BOUND_RECHECK"][i]["repo_writes"] for i in idx),
    "duplicate_repository_transition":sum(DETAIL["GENERATION_BOUND_RECHECK"][i]["repo_writes"]>1 for i in idx),
}

OUT["interpretation"]={
    "scope":"Synthetic finite cross-component allocation lattice; counts are not production failure rates.",
    "strong_rule":"Independently absorbing resource seals compose only relative to one immutable allocation contract. Bind every resource proof to {parent_generation, allocation_contract_digest}; recheck current generation at parent terminal CAS. Value equality alone is ABA-unsafe. A vector sink transaction is unnecessary for this allocation invariant when the allocation contract is immutable/current-fenced in the repository authority domain and every sink seal binds that digest.",
    "protected_boundary":"The sink still must enforce the per-resource absorbing seal against the supplied immutable allocation digest. No additional vector-level sink primitive is required in the tested decomposable scope if parent generation/allocation immutability is authoritative and current-fenced; if allocation itself is mutable only in an external authority domain, vector-level atomic finalization remains required."
}
print(json.dumps(OUT,indent=2,sort_keys=True))
