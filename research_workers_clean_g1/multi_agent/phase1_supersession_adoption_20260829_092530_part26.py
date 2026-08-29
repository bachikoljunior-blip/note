#!/usr/bin/env python3
from itertools import product
import json

RES=("R1","R2")
REL=("EXACT","CONTRACT_CHANGED","AMOUNT_CHANGED")
AXES={
    "r1_relation":REL,
    "r2_relation":REL,
    "r1_g1":["SEALED","MISSING"],
    "r2_g1":["SEALED","MISSING"],
    "r1_proof":["ABSORBING","CURRENT_ONLY"],
    "r2_proof":["ABSORBING","CURRENT_ONLY"],
    "late_event":["NONE","R1_INVALIDATE","R2_INVALIDATE"],
    "gen_verifier":["AVAILABLE","OUTAGE"],
    "reseal_available":["YES","NO"],
    "cas":["CONFIRMED_APPLIED","AMBIG_APPLIED","AMBIG_NOT_APPLIED"],
    "repeat":["NO","YES"],
    "takeover":["NO","YES"],
}
SCENARIOS=[dict(zip(AXES,v)) for v in product(*AXES.values())]


def cas_applies(sc):
    return sc["cas"] in ("CONFIRMED_APPLIED","AMBIG_APPLIED") or (sc["cas"]=="AMBIG_NOT_APPLIED" and sc["repeat"]=="YES")


def new_state(sc):
    out={}
    for r in RES:
        low=r.lower()
        out[r]={
            "relation":sc[f"{low}_relation"],
            "old_exists":sc[f"{low}_g1"]=="SEALED",
            "old_active":sc[f"{low}_g1"]=="SEALED",
            "proof":sc[f"{low}_proof"],
            "resealed":False,
            "adopt_record":False,
            "reused_no_record":False,
            "new":False,
        }
    return out


def visible_name_amount_match(x):
    # CONTRACT_CHANGED deliberately keeps the same visible name/amount but changes immutable effect semantics.
    return x["relation"] in ("EXACT","CONTRACT_CHANGED")


def apply_late_event(state,sc):
    if sc["late_event"]=="NONE": return
    r=sc["late_event"].split("_")[0]
    x=state[r]
    if not x["old_exists"]: return
    if x["proof"]=="ABSORBING" or x["resealed"]:
        return
    x["old_active"]=False


def safety(state):
    safe=True
    duplicate=False
    for x in state.values():
        if x["relation"]=="EXACT":
            satisfied=(x["adopt_record"] and x["old_active"]) or x["new"]
            if not satisfied or x["reused_no_record"]:
                safe=False
            if x["new"] and x["old_active"]:
                duplicate=True
                safe=False
        else:
            # Changed contract/amount requires a new current-generation effect.
            if not x["new"]:
                safe=False
        if x["adopt_record"] and x["relation"]!="EXACT":
            safe=False
    return safe,duplicate


def finish(state,decide,sc,partial_adopt=0,protected_ops=0):
    apply_late_event(state,sc)
    safe,duplicate=safety(state)
    terminal=decide and cas_applies(sc)
    return {
        "terminal":terminal,
        "unsafe_terminal":terminal and not safe,
        "safe_terminal":terminal and safe,
        "duplicate_external_effect":duplicate,
        "partial_adopt":partial_adopt,
        "protected_ops":protected_ops,
        "repo_writes":1 if terminal else 0,
        "duplicate_adoption_record":False,
    }


def discard_reexecute(sc):
    state=new_state(sc)
    if sc["gen_verifier"]!="AVAILABLE":
        return finish(state,False,sc)
    for x in state.values():
        x["new"]=True
    return finish(state,True,sc)


def name_amount_adopt(sc):
    state=new_state(sc)
    ok=True; adopted=0
    for x in state.values():
        if x["old_exists"] and visible_name_amount_match(x):
            # Weak adoption creates a g2 record, but does not check full effect contract or make CURRENT_ONLY proof absorbing.
            x["adopt_record"]=True; adopted+=1
        else:
            if sc["gen_verifier"]!="AVAILABLE": ok=False
            else: x["new"]=True
    return finish(state,ok,sc,partial_adopt=adopted)


def exact_contract_reuse_no_adoption(sc):
    state=new_state(sc)
    ok=True
    for x in state.values():
        if x["old_exists"] and x["relation"]=="EXACT":
            x["reused_no_record"]=True
        else:
            if sc["gen_verifier"]!="AVAILABLE": ok=False
            else: x["new"]=True
    return finish(state,ok,sc)


def can_strong_adopt(x,sc):
    if not (x["old_exists"] and x["relation"]=="EXACT"):
        return False,None
    if x["proof"]=="ABSORBING":
        return True,"existing_absorbing"
    if sc["reseal_available"]=="YES":
        return True,"reseal"
    return False,"blocked"


def per_resource_adoption(sc):
    state=new_state(sc)
    if sc["gen_verifier"]!="AVAILABLE":
        return finish(state,False,sc)
    adopted=0; ops=0; ok=True
    for r in RES:
        x=state[r]
        if x["old_exists"] and x["relation"]=="EXACT":
            good,mode=can_strong_adopt(x,sc)
            if not good:
                ok=False
                break
            if mode=="reseal":
                x["resealed"]=True; ops+=1
            # Stable adoption identity H(g2, old_resource_id, old_final_version, allocation_digest).
            x["adopt_record"]=True; adopted+=1; ops+=1
        else:
            # Changed or absent old work requires one new current-generation external effect.
            x["new"]=True; ops+=1
    return finish(state,ok,sc,partial_adopt=adopted,protected_ops=ops)


def vector_adoption(sc):
    state=new_state(sc)
    if sc["gen_verifier"]!="AVAILABLE":
        return finish(state,False,sc)
    plan=[]
    for r in RES:
        x=state[r]
        if x["old_exists"] and x["relation"]=="EXACT":
            good,mode=can_strong_adopt(x,sc)
            if not good:
                return finish(state,False,sc,partial_adopt=0,protected_ops=1)
            plan.append((r,"adopt",mode))
        else:
            plan.append((r,"new",None))
    adopted=0; ops=1
    for r,kind,mode in plan:
        x=state[r]
        if kind=="adopt":
            if mode=="reseal":
                x["resealed"]=True; ops+=1
            x["adopt_record"]=True; adopted+=1
        else:
            x["new"]=True; ops+=1
    return finish(state,True,sc,partial_adopt=adopted,protected_ops=ops)


DETAIL={
    "DISCARD_REEXECUTE":[discard_reexecute(s) for s in SCENARIOS],
    "NAME_AMOUNT_ADOPT":[name_amount_adopt(s) for s in SCENARIOS],
    "EXACT_CONTRACT_REUSE_NO_ADOPTION":[exact_contract_reuse_no_adoption(s) for s in SCENARIOS],
    "G2_PER_RESOURCE_ADOPTION":[per_resource_adoption(s) for s in SCENARIOS],
    "G2_VECTOR_ADOPTION":[vector_adoption(s) for s in SCENARIOS],
}


def summarize(rows):
    return {
        "terminal":sum(r["terminal"] for r in rows),
        "unsafe_terminal":sum(r["unsafe_terminal"] for r in rows),
        "safe_terminal":sum(r["safe_terminal"] for r in rows),
        "duplicate_external_effect_scenarios":sum(r["duplicate_external_effect"] for r in rows),
        "partial_adoptions_nonterminal":sum(r["partial_adopt"]>0 and not r["terminal"] for r in rows),
        "duplicate_adoption_record":sum(r["duplicate_adoption_record"] for r in rows),
    }


def select(pred): return [i for i,s in enumerate(SCENARIOS) if pred(s)]
def slice_stats(policy,idx):
    rows=DETAIL[policy]
    return {
        "n":len(idx),
        "terminal":sum(rows[i]["terminal"] for i in idx),
        "unsafe_terminal":sum(rows[i]["unsafe_terminal"] for i in idx),
        "safe_terminal":sum(rows[i]["safe_terminal"] for i in idx),
        "duplicate_external":sum(rows[i]["duplicate_external_effect"] for i in idx),
        "partial_adopt_nonterminal":sum(rows[i]["partial_adopt"]>0 and not rows[i]["terminal"] for i in idx),
    }

OUT={"scenario_count":len(SCENARIOS),"policies":{p:summarize(r) for p,r in DETAIL.items()},"slices":{}}

# Both g1 effects exactly match g2 and have absorbing finality.
idx=select(lambda s:s["r1_relation"]=="EXACT" and s["r2_relation"]=="EXACT"
           and s["r1_g1"]=="SEALED" and s["r2_g1"]=="SEALED"
           and s["r1_proof"]=="ABSORBING" and s["r2_proof"]=="ABSORBING"
           and s["late_event"]=="NONE" and s["gen_verifier"]=="AVAILABLE"
           and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["exact_old_discard_reexecute"]=slice_stats("DISCARD_REEXECUTE",idx)
OUT["slices"]["exact_old_no_adoption_record"]=slice_stats("EXACT_CONTRACT_REUSE_NO_ADOPTION",idx)
OUT["slices"]["exact_old_strong_adoption"]=slice_stats("G2_PER_RESOURCE_ADOPTION",idx)

# Same visible name/amount but changed immutable contract.
idx=select(lambda s:s["r1_relation"]=="CONTRACT_CHANGED" and s["r1_g1"]=="SEALED"
           and s["r1_proof"]=="ABSORBING" and s["r2_relation"]=="AMOUNT_CHANGED"
           and s["r2_g1"]=="MISSING" and s["gen_verifier"]=="AVAILABLE"
           and s["cas"]=="CONFIRMED_APPLIED" and s["late_event"]=="NONE")
OUT["slices"]["visible_match_changed_contract_name_amount"]=slice_stats("NAME_AMOUNT_ADOPT",idx)
OUT["slices"]["visible_match_changed_contract_strong"]=slice_stats("G2_PER_RESOURCE_ADOPTION",idx)

# CURRENT_ONLY g1 proof invalidates after weak adoption; strong protocol fails closed if it cannot reseal.
idx=select(lambda s:s["r1_relation"]=="EXACT" and s["r2_relation"]=="EXACT"
           and s["r1_g1"]=="SEALED" and s["r2_g1"]=="SEALED"
           and s["r1_proof"]=="CURRENT_ONLY" and s["r2_proof"]=="ABSORBING"
           and s["late_event"]=="R1_INVALIDATE" and s["gen_verifier"]=="AVAILABLE"
           and s["reseal_available"]=="NO" and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["late_invalidation_weak_adoption"]=slice_stats("NAME_AMOUNT_ADOPT",idx)
OUT["slices"]["late_invalidation_strong_no_reseal"]=slice_stats("G2_PER_RESOURCE_ADOPTION",idx)

idx=select(lambda s:s["r1_relation"]=="EXACT" and s["r2_relation"]=="EXACT"
           and s["r1_g1"]=="SEALED" and s["r2_g1"]=="SEALED"
           and s["r1_proof"]=="CURRENT_ONLY" and s["r2_proof"]=="ABSORBING"
           and s["late_event"]=="R1_INVALIDATE" and s["gen_verifier"]=="AVAILABLE"
           and s["reseal_available"]=="YES" and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["late_invalidation_strong_with_reseal"]=slice_stats("G2_PER_RESOURCE_ADOPTION",idx)

# Per-resource adoption can durably adopt the safe first component while a second component blocks.
idx=select(lambda s:s["r1_relation"]=="EXACT" and s["r2_relation"]=="EXACT"
           and s["r1_g1"]=="SEALED" and s["r2_g1"]=="SEALED"
           and s["r1_proof"]=="ABSORBING" and s["r2_proof"]=="CURRENT_ONLY"
           and s["reseal_available"]=="NO" and s["gen_verifier"]=="AVAILABLE"
           and s["cas"]=="CONFIRMED_APPLIED")
OUT["slices"]["partial_progress_per_resource_adoption"]=slice_stats("G2_PER_RESOURCE_ADOPTION",idx)
OUT["slices"]["partial_progress_vector_adoption"]=slice_stats("G2_VECTOR_ADOPTION",idx)

idx=select(lambda s:s["cas"] in ("AMBIG_APPLIED","AMBIG_NOT_APPLIED") and s["repeat"]=="YES")
OUT["slices"]["stable_adoption_and_parent_ids_ambiguous_repeat"]={
    "n":len(idx),
    "duplicate_adoption_record":sum(DETAIL["G2_PER_RESOURCE_ADOPTION"][i]["duplicate_adoption_record"] for i in idx),
    "max_repository_terminal_writes":max(DETAIL["G2_PER_RESOURCE_ADOPTION"][i]["repo_writes"] for i in idx),
}

OUT["interpretation"]={
    "scope":"Synthetic finite generation-supersession/adoption lattice. Changed-contract old effects are treated as outside the current requirement rather than modeling their compensation cleanup; counts are not production failure rates.",
    "strong_rule":"Reuse is an authority transition, not a cache hit. A g2 adoption record is required even for byte/contract-identical g1 effects; it binds current g2 generation/allocation digest to the exact old resource/effect contract and only accepts an absorbing old proof or a successful current reseal. Name/amount matching is too weak, and re-executing an already-satisfied exact effect can duplicate the external effect.",
    "protected_boundary":"The sink/status domain must provide absorbing old finality or a no-effect reseal/finality operation so g2 can adopt without replaying the external effect. The repository can perform current-generation adoption CAS, stable IDs, exact contract checks and lineage records; it cannot manufacture sink finality for a CURRENT_ONLY old resource."
}
print(json.dumps(OUT,indent=2,sort_keys=True))
