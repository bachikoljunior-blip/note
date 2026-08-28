from itertools import product
from collections import Counter
import json
import hashlib
import numpy as np
from scipy.optimize import linprog

BASE_COSTS = {"wait":3,"retry":1,"status":1,"webhook_wait":2,"compensate":4}
COST_PROFILES = {
    "baseline": BASE_COSTS,
    "latency_heavy_wait":{"wait":6,"retry":1,"status":1,"webhook_wait":2,"compensate":4},
    "mutation_heavy":{"wait":3,"retry":1,"status":1,"webhook_wait":2,"compensate":8},
    "lookup_expensive":{"wait":3,"retry":2,"status":2,"webhook_wait":3,"compensate":4},
}
STRATEGIES=["block","wait","retry_status","key_boolean_retry","webhook_wait","status_only","ignore"]
FILL_MODES=["never","fill_cert"]
FINALITY_MODES=["proof","trust"]


def build_worlds():
    worlds=[]
    wid=0
    for r in [0,50,100]:
        provisional_opts=[False] if r==0 else [False,True]
        for provisional in provisional_opts:
            for w in [0,50,100]:
                outcome_opts=["none"] if w==0 else ["no_effect","apply"]
                for old_outcome in outcome_opts:
                    retry_opts=[False] if w==0 else [False,True]
                    for retry_cert in retry_opts:
                        dup_opts=[False] if (w==0 or retry_cert) else [False,True]
                        for uncert_retry_dup in dup_opts:
                            for webhook_auth in [False,True]:
                                for new_comp_cert in [False,True]:
                                    wid += 1
                                    worlds.append({
                                        "id":wid,
                                        "initial_refunded":r,
                                        "initial_refund_provisional":provisional,
                                        "old_writer_amount":w,
                                        "old_writer_outcome":old_outcome,
                                        "old_retry_contract_certified":retry_cert,
                                        "uncertified_retry_duplicates":uncert_retry_dup,
                                        "webhook_terminal_signal_authoritative":webhook_auth,
                                        "new_compensation_contract_certified":new_comp_cert,
                                    })
    return worlds


def eval_policy(world, strategy, fill_mode, finality_mode, costs):
    init_amount=world["initial_refunded"]
    init_alive=True
    provisional_unresolved=world["initial_refund_provisional"]
    writer_unresolved=world["old_writer_amount"]>0
    old_applied=False
    duplicate_retry_amount=0
    new_amount=0
    actions=[]
    blocked=False

    def observed_total():
        return ((init_amount if init_alive else 0)
                + (world["old_writer_amount"] if old_applied else 0)
                + duplicate_retry_amount + new_amount)

    def resolve_provisional():
        nonlocal init_alive, provisional_unresolved
        if provisional_unresolved:
            init_alive=False
            provisional_unresolved=False

    def resolve_writer():
        nonlocal writer_unresolved, old_applied
        if writer_unresolved:
            if world["old_writer_outcome"]=="apply":
                old_applied=True
            writer_unresolved=False

    def resolve_all():
        resolve_provisional(); resolve_writer()

    if strategy=="block":
        if writer_unresolved or provisional_unresolved:
            blocked=True
    elif strategy=="wait":
        if writer_unresolved or provisional_unresolved:
            actions.append("wait"); resolve_all()
    elif strategy=="retry_status":
        if writer_unresolved:
            if world["old_retry_contract_certified"]:
                actions += ["retry","status"]
                resolve_writer()
            else:
                blocked=True
        if not blocked and finality_mode=="proof" and provisional_unresolved:
            actions.append("wait"); resolve_provisional()
    elif strategy=="key_boolean_retry":
        if writer_unresolved:
            actions += ["retry","status"]
            if world["old_retry_contract_certified"]:
                resolve_writer()
            else:
                if world["uncertified_retry_duplicates"]:
                    duplicate_retry_amount += world["old_writer_amount"]
    elif strategy=="webhook_wait":
        if writer_unresolved or provisional_unresolved:
            actions.append("webhook_wait")
            if world["webhook_terminal_signal_authoritative"]:
                resolve_all()
            elif finality_mode=="proof":
                blocked=True
    elif strategy=="status_only":
        if writer_unresolved or provisional_unresolved:
            actions.append("status")
            if finality_mode=="proof":
                blocked=True
    elif strategy=="ignore":
        pass
    else:
        raise ValueError(strategy)

    if not blocked and finality_mode=="proof" and (writer_unresolved or provisional_unresolved):
        blocked=True

    if not blocked:
        obs=observed_total()
        if obs>100:
            blocked=True
        elif obs<100:
            if fill_mode=="fill_cert" and world["new_compensation_contract_certified"]:
                actions.append("compensate")
                new_amount += 100-obs
            else:
                blocked=True

    terminal=(not blocked and observed_total()==100)
    if terminal:
        resolve_all()
        final_total=observed_total()
        safe=(final_total==100)
    else:
        safe=None
        resolve_all()
        final_total=observed_total()

    return {
        "terminal":terminal,
        "safe":safe,
        "final_total":final_total,
        "actions":actions,
        "weighted_cost":sum(costs[a] for a in actions),
        "irreversible_issuance":actions.count("compensate"),
    }


def summarize(worlds, costs):
    out=[]
    for strategy,fill_mode,finality in product(STRATEGIES,FILL_MODES,FINALITY_MODES):
        rows=[eval_policy(w,strategy,fill_mode,finality,costs) for w in worlds]
        terminal=sum(r["terminal"] for r in rows)
        unsafe=sum(r["terminal"] and not r["safe"] for r in rows)
        out.append({
            "strategy":strategy,"fill_mode":fill_mode,"finality":finality,
            "terminal":terminal,"unsafe_terminal":unsafe,
            "safe_terminal":terminal-unsafe,
            "terminal_coverage":terminal/len(worlds),
            "safe_terminal_coverage":(terminal-unsafe)/len(worlds),
            "avg_weighted_cost_per_world":sum(r["weighted_cost"] for r in rows)/len(worlds),
            "avg_irreversible_compensations_per_world":sum(r["irreversible_issuance"] for r in rows)/len(worlds),
            "avg_actions_per_world":sum(len(r["actions"]) for r in rows)/len(worlds),
        })
    return out


def pareto(items):
    front=[]
    for i,a in enumerate(items):
        dominated=False
        for j,b in enumerate(items):
            if i==j: continue
            if (b["safe_terminal_coverage"]>=a["safe_terminal_coverage"]
                and b["avg_weighted_cost_per_world"]<=a["avg_weighted_cost_per_world"]
                and b["avg_irreversible_compensations_per_world"]<=a["avg_irreversible_compensations_per_world"]
                and (b["safe_terminal_coverage"]>a["safe_terminal_coverage"]
                     or b["avg_weighted_cost_per_world"]<a["avg_weighted_cost_per_world"]
                     or b["avg_irreversible_compensations_per_world"]<a["avg_irreversible_compensations_per_world"])):
                dominated=True; break
        if not dominated: front.append(a)
    return front


def dedupe_behavior(front):
    rep={}
    strategy_order={"wait":0,"retry_status":1,"webhook_wait":2,"block":3,"ignore":4,"status_only":5,"key_boolean_retry":6}
    for x in front:
        key=(round(x["safe_terminal_coverage"],12),round(x["avg_weighted_cost_per_world"],12),round(x["avg_irreversible_compensations_per_world"],12))
        rank=(0 if x["finality"]=="proof" else 1,strategy_order.get(x["strategy"],9),0 if x["fill_mode"]=="fill_cert" else 1)
        if key not in rep or rank<rep[key][0]:
            rep[key]=(rank,x)
    return [v[1] for v in rep.values()]


def linear_scalar_supported(reps, idx):
    i=reps[idx]
    A=[]; b=[]
    for j in reps:
        if j is i: continue
        dc=j["avg_weighted_cost_per_world"]-i["avg_weighted_cost_per_world"]
        di=j["avg_irreversible_compensations_per_world"]-i["avg_irreversible_compensations_per_world"]
        dcover=j["safe_terminal_coverage"]-i["safe_terminal_coverage"]
        A.append([-dc,-di]); b.append(-dcover)
    res=linprog(c=[0,0],A_ub=np.asarray(A),b_ub=np.asarray(b),bounds=[(0,None),(0,None)],method="highs")
    return bool(res.success)


def policy_row(summary, s, f, fin):
    return next(x for x in summary if (x["strategy"],x["fill_mode"],x["finality"])==(s,f,fin))


def main():
    worlds=build_worlds()
    result={
        "schema_version":1,
        "model_scope":{
            "worlds":len(worlds),
            "capture_target":100,
            "initial_refunded_values":[0,50,100],
            "old_compensation_writer_amounts":[0,50,100],
            "hidden_writer_outcomes":["no_effect","apply"],
            "current_refund_late_failure_axis":True,
            "uncertified_retry_duplicate_axis":True,
            "new_compensation_contract_axis":True,
            "webhook_authoritative_terminal_signal_axis":True,
            "note":"Balanced synthetic mechanism lattice; proportions are not production incident rates."
        },
        "action_cost_profiles":COST_PROFILES,
        "profiles":{},
    }
    for profile,costs in COST_PROFILES.items():
        summary=summarize(worlds,costs)
        safe=[x for x in summary if x["unsafe_terminal"]==0]
        reps=dedupe_behavior(pareto(safe))
        annotated=[]
        for idx,x in enumerate(reps):
            y=dict(x)
            y["supported_by_some_nonnegative_linear_scalarization"]=linear_scalar_supported(reps,idx)
            annotated.append(y)
        result["profiles"][profile]={
            "named_policy_summary":summary,
            "safe_pareto_behavior_representatives":sorted(annotated,key=lambda x:(x["safe_terminal_coverage"],x["avg_weighted_cost_per_world"])),
            "safe_pareto_count":len(annotated),
            "linear_scalar_unsupported_pareto_count":sum(not x["supported_by_some_nonnegative_linear_scalarization"] for x in annotated),
        }

    base=result["profiles"]["baseline"]["named_policy_summary"]
    key_naive=policy_row(base,"key_boolean_retry","fill_cert","trust")
    snapshot=policy_row(base,"ignore","fill_cert","trust")
    status_only=policy_row(base,"status_only","fill_cert","trust")
    wait=policy_row(base,"wait","fill_cert","proof")
    retry_proof=policy_row(base,"retry_status","fill_cert","proof")
    webhook_proof=policy_row(base,"webhook_wait","fill_cert","proof")
    wait_never=policy_row(base,"wait","never","proof")

    slice_rows=[]
    for w in worlds:
        if (not w["initial_refund_provisional"] and w["old_writer_amount"]>0
            and w["old_writer_outcome"]=="apply"
            and not w["old_retry_contract_certified"]
            and w["uncertified_retry_duplicates"]):
            r=eval_policy(w,"key_boolean_retry","fill_cert","trust",BASE_COSTS)
            if r["terminal"]: slice_rows.append(r)
    pure_contract_terminal=len(slice_rows)
    pure_contract_unsafe=sum(not r["safe"] for r in slice_rows)

    result["headline_checks"]={
        "snapshot_ignore_fill_trust":snapshot,
        "fresh_status_only_fill_trust":status_only,
        "key_boolean_retry_fill_trust":key_naive,
        "wait_then_fill_proof":wait,
        "certified_retry_status_fill_proof":retry_proof,
        "authoritative_webhook_fill_proof":webhook_proof,
        "wait_no_new_compensation_proof":wait_never,
        "pure_invalid_retry_contract_slice":{"terminal":pure_contract_terminal,"unsafe_terminal":pure_contract_unsafe},
    }

    assert len(worlds)==260
    assert (snapshot["terminal"],snapshot["unsafe_terminal"])==(182,108)
    assert (status_only["terminal"],status_only["unsafe_terminal"])==(182,108)
    assert (key_naive["terminal"],key_naive["unsafe_terminal"])==(140,70)
    assert (wait["terminal"],wait["unsafe_terminal"])==(150,0)
    assert (retry_proof["terminal"],retry_proof["unsafe_terminal"])==(58,0)
    assert (webhook_proof["terminal"],webhook_proof["unsafe_terminal"])==(79,0)
    assert (wait_never["terminal"],wait_never["unsafe_terminal"])==(76,0)
    assert (pure_contract_terminal,pure_contract_unsafe)==(10,10)
    assert result["profiles"]["baseline"]["safe_pareto_count"]==8
    assert result["profiles"]["baseline"]["linear_scalar_unsupported_pareto_count"]==4

    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
