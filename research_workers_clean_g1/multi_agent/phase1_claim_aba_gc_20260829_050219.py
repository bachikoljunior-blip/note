#!/usr/bin/env python3
"""Finite synthetic stress test for claim/effect ABA after GC and key reuse.
Mechanism counts are not empirical rates.
"""
from itertools import product
from collections import Counter, defaultdict
import json

ACTION=["stale_result","stale_external_effect","stale_release"]
B_PHASE=["new_claim_live","new_integrated_claim_live","new_integrated_claim_gc"]
TOKEN=["unique_per_acquire","reused_key_derived"]
EPOCH=["persistent_monotonic","reset_on_restart"]
PARENT_UID=["unique_new_uid","reused_name_only"]
SPEC=["same_spec","drifted_spec"]
EFFECT=["same_exclusive_effect","disjoint_effect"]
OLD_META_UID=[False,True]
FENCE_WITNESS=[False,True]
POLICIES=["key_only_ttl","random_token_release_only","current_token_sink","epoch_fence","incarnation_epoch_token","immutable_stage_fenced_integrator"]

def ids(token_mode,epoch_mode,uid_mode):
    a_token="T" if token_mode=="reused_key_derived" else "TA"; b_token="T" if token_mode=="reused_key_derived" else "TB"
    a_epoch=1; b_epoch=1 if epoch_mode=="reset_on_restart" else 2
    a_uid="P" if uid_mode=="reused_name_only" else "PA"; b_uid="P" if uid_mode=="reused_name_only" else "PB"
    return a_token,b_token,a_epoch,b_epoch,a_uid,b_uid

def score_accept(r,action,b_phase,effect_mode,spec_mode):
    if action=="stale_result":
        r["stale_result_accept"]+=1;r["aba_accept"]+=1
        if b_phase!="new_claim_live":r["false_terminal_or_overwrite"]+=1
        if spec_mode=="drifted_spec":r["wrong_spec_accept"]+=1
    elif action=="stale_external_effect":
        r["stale_effect_accept"]+=1;r["aba_accept"]+=1
        if effect_mode=="same_exclusive_effect" and b_phase!="new_claim_live":r["duplicate_authoritative_effect"]+=1
    elif action=="stale_release" and b_phase!="new_integrated_claim_gc":
        r["new_claim_deleted"]+=1;r["false_exclusion_or_liveness"]+=1;r["aba_accept"]+=1

def evaluate(policy,action,b_phase,token_mode,epoch_mode,uid_mode,spec_mode,effect_mode,old_meta_uid,fence_witness):
    r=Counter();a_tok,b_tok,a_ep,b_ep,a_uid,b_uid=ids(token_mode,epoch_mode,uid_mode);claim_live=b_phase!="new_integrated_claim_gc"
    if policy=="key_only_ttl":score_accept(r,action,b_phase,effect_mode,spec_mode);return r
    if policy=="random_token_release_only":
        if action=="stale_release":
            if claim_live and a_tok==b_tok:score_accept(r,action,b_phase,effect_mode,spec_mode)
            else:r["stale_release_blocked"]+=1
        else:score_accept(r,action,b_phase,effect_mode,spec_mode)
        return r
    if policy=="current_token_sink":
        if claim_live and a_tok==b_tok:score_accept(r,action,b_phase,effect_mode,spec_mode)
        else:r["stale_action_blocked"]+=1
        return r
    if policy=="epoch_fence":
        highest=None if b_phase=="new_integrated_claim_gc" and not fence_witness else b_ep
        if highest is None or a_ep>=highest:score_accept(r,action,b_phase,effect_mode,spec_mode)
        else:r["stale_action_blocked"]+=1
        return r
    if policy=="incarnation_epoch_token":
        if not old_meta_uid:r["stale_action_blocked"]+=1;r["missing_incarnation_metadata"]+=1;return r
        if a_uid==b_uid and a_tok==b_tok and a_ep>=b_ep:score_accept(r,action,b_phase,effect_mode,spec_mode)
        else:r["stale_action_blocked"]+=1
        return r
    if policy=="immutable_stage_fenced_integrator":
        if action in ("stale_result","stale_external_effect"):r["stale_stage_recorded"]+=1;r["stale_action_blocked"]+=1
        else:
            if claim_live and old_meta_uid and a_uid==b_uid and a_tok==b_tok:score_accept(r,action,b_phase,effect_mode,spec_mode)
            else:r["stale_release_blocked"]+=1
        return r
    raise ValueError(policy)

def unsafe(r):return int(bool(r["stale_result_accept"] or r["stale_effect_accept"] or r["new_claim_deleted"] or r["duplicate_authoritative_effect"] or r["false_terminal_or_overwrite"] or r["wrong_spec_accept"]))

def main():
    totals={p:Counter() for p in POLICIES};slices=defaultdict(Counter);n=0
    for action,b_phase,token_mode,epoch_mode,uid_mode,spec_mode,effect_mode,old_meta_uid,fence_witness in product(ACTION,B_PHASE,TOKEN,EPOCH,PARENT_UID,SPEC,EFFECT,OLD_META_UID,FENCE_WITNESS):
        n+=1;results={}
        for p in POLICIES:
            r=evaluate(p,action,b_phase,token_mode,epoch_mode,uid_mode,spec_mode,effect_mode,old_meta_uid,fence_witness);r["unsafe"]=unsafe(r);results[p]=r;totals[p]["scenarios"]+=1
            for k,v in r.items():totals[p][k]+=v
            if r["unsafe"]:totals[p]["unsafe_scenarios"]+=1
            if r["aba_accept"]:totals[p]["aba_accept_scenarios"]+=1
            if r["duplicate_authoritative_effect"]:totals[p]["duplicate_effect_scenarios"]+=1
            if r["stale_result_accept"]:totals[p]["stale_result_scenarios"]+=1
            if r["new_claim_deleted"]:totals[p]["new_claim_deleted_scenarios"]+=1
        if b_phase=="new_integrated_claim_gc":
            s=slices["after_claim_gc"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_unsafe"]+=int(r["unsafe"]);s[p+"_aba"]+=int(r["aba_accept"])
        if epoch_mode=="reset_on_restart":
            s=slices["epoch_reset_restart"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_unsafe"]+=int(r["unsafe"])
        if token_mode=="unique_per_acquire":
            s=slices["unique_token_supported"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_unsafe"]+=int(r["unsafe"])
        if uid_mode=="unique_new_uid" and token_mode=="unique_per_acquire":
            s=slices["unique_incarnation_and_token"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_unsafe"]+=int(r["unsafe"])
        if token_mode=="reused_key_derived" and epoch_mode=="reset_on_restart" and uid_mode=="reused_name_only":
            s=slices["full_aba_identity_collision"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_unsafe"]+=int(r["unsafe"]);s[p+"_aba"]+=int(r["aba_accept"])
        if action=="stale_external_effect" and effect_mode=="same_exclusive_effect" and b_phase!="new_claim_live":
            s=slices["stale_same_effect_after_new_integration"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_duplicate_effect"]+=int(r["duplicate_authoritative_effect"])
        if spec_mode=="drifted_spec" and action=="stale_result":
            s=slices["same_key_spec_drift"];s["scenarios"]+=1
            for p,r in results.items():s[p+"_wrong_spec"]+=int(r["wrong_spec_accept"])
    out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"dimensions":{"action":ACTION,"new_incarnation_phase":B_PHASE,"acquisition_token":TOKEN,"epoch_persistence":EPOCH,"parent_incarnation":PARENT_UID,"task_spec":SPEC,"effect_overlap":EFFECT,"old_result_has_parent_uid":OLD_META_UID,"fence_witness_retained_after_gc":FENCE_WITNESS}},"policies":{},"slices":{k:dict(v) for k,v in slices.items()},"scope_limits":["Finite mechanism lattice only; not production failure rates.","Unique token and unique UID are modeled as collision-free within their positive capability slices; collision/derivation bugs are separate negative dimensions.","The current-token policy requires the authoritative sink to reject actions when no live current claim exists; it does not grant authority merely because a key is absent.","The strong incarnation policy assumes a retained current-incarnation witness beyond claim-row GC.","Immutable staging prevents direct authoritative side effects by construction; external systems that cannot be mediated by the integrator require their own sink-side fencing/idempotency contract."]}
    for p,c in totals.items():d=dict(c);d["unsafe_rate"]=c["unsafe_scenarios"]/n;d["aba_accept_rate"]=c["aba_accept_scenarios"]/n;out["policies"][p]=d
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
