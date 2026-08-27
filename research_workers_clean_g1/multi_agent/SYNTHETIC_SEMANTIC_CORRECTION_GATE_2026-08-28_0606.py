#!/usr/bin/env python3
import json, math
from collections import OrderedDict
import numpy as np

BASE_SEED = 202608280602

def simulate_condition(n, seed, src_err, rho_cross, same_copy=0.8,
                       tpr_diag=0.82, fpr_diag=0.12, cand_acc=0.88,
                       same_tpr=0.92, same_fpr=0.30,
                       ind_tpr=0.92, ind_fpr=0.10,
                       base_cost=10.0, replay_cost=6.0):
    rng=np.random.default_rng(seed)
    initial_correct = rng.random(n) >= src_err
    u = rng.random(n)
    diagnose = np.where(initial_correct, u < fpr_diag, u < tpr_diag)
    cand_correct = np.zeros(n, dtype=bool)
    idx=(~initial_correct) & diagnose
    cand_correct[idx]=rng.random(idx.sum()) < cand_acc

    fresh_same = rng.random(n) < np.where(cand_correct, same_tpr, same_fpr)
    same_confirm = np.where(rng.random(n) < same_copy, True, fresh_same)

    fresh_ind = rng.random(n) < np.where(cand_correct, ind_tpr, ind_fpr)
    ind_confirm = np.where(rng.random(n) < rho_cross, same_confirm, fresh_ind)

    policy_apply = OrderedDict([
        ("destructive_single", diagnose),
        ("provisional_same_repeat", diagnose & same_confirm),
        ("abstain", np.zeros(n, dtype=bool)),
        ("independent_escalation", diagnose & ind_confirm),
    ])
    extra = {
        "destructive_single": np.zeros(n,dtype=np.int8),
        "provisional_same_repeat": diagnose.astype(np.int8),
        "abstain": np.zeros(n,dtype=np.int8),
        "independent_escalation": diagnose.astype(np.int8),
    }

    arrs, metrics = {}, {}
    for name, apply in policy_apply.items():
        final_correct=np.where(apply, cand_correct, initial_correct)
        harmful=apply & (~cand_correct)
        success=(~initial_correct) & final_correct
        safe_abst=diagnose & (~cand_correct) & (~apply)
        missed=diagnose & cand_correct & (~apply)
        replay=apply.astype(np.int8)
        cost=base_cost + 1 + extra[name] + replay*replay_cost
        arrs[name]=(final_correct.astype(np.int8), harmful.astype(np.int8), cost)
        metrics[name]={
            "endpoint_accuracy": float(final_correct.mean()),
            "harmful_replacement_rate": float(harmful.mean()),
            "successful_repair_rate": float(success.mean()),
            "safe_abstain_rate": float(safe_abst.mean()),
            "missed_good_correction_rate": float(missed.mean()),
            "apply_rate": float(apply.mean()),
            "diagnosis_rate": float(diagnose.mean()),
            "candidate_wrong_among_diagnosed": float(
                ((diagnose & ~cand_correct).sum()/diagnose.sum()) if diagnose.sum() else 0
            ),
            "avg_total_cost": float(cost.mean()),
            "correct_per_100k_cost": float(final_correct.sum()/cost.sum()*100_000),
        }

    comparisons={}
    for a,b in [
        ("independent_escalation","abstain"),
        ("independent_escalation","destructive_single"),
        ("provisional_same_repeat","abstain"),
        ("provisional_same_repeat","destructive_single")
    ]:
        d=arrs[a][0]-arrs[b][0]
        mean=float(d.mean())
        se=float(d.std(ddof=1)/math.sqrt(n))
        comparisons[f"{a}_minus_{b}"]={
            "accuracy_diff":mean,
            "se":se,
            "ci95":[mean-1.96*se,mean+1.96*se]
        }

    return {
        "params":{
            "n":n,"seed":seed,"src_err":src_err,"rho_cross":rho_cross,
            "same_copy":same_copy,"tpr_diag":tpr_diag,"fpr_diag":fpr_diag,
            "cand_acc":cand_acc,"same_tpr":same_tpr,"same_fpr":same_fpr,
            "ind_tpr":ind_tpr,"ind_fpr":ind_fpr,
            "base_cost":base_cost,"replay_cost":replay_cost
        },
        "metrics":metrics,
        "comparisons":comparisons
    }

def main():
    results={
        "study":"semantic_correction_gate_before_repair_witness",
        "interpretation_scope":[
            "Synthetic mechanism study only; not a deployment failure-rate estimate.",
            "Repair provenance/admissibility is assumed perfect after a correction is selected.",
            "The experiment isolates semantic correction error before provenance-safe replay.",
            "rho_cross is an explicit mixture that copies the same-verifier confirmation verdict; it is not a measured real-model correlation coefficient."
        ],
        "conditions":[],
        "same_repeat_correlation_sweep":[],
        "rho_efficiency_sweep_src_err_025":[]
    }

    for i,src_err in enumerate([0.10,0.25,0.40]):
        for j,rho in enumerate([0.0,0.5,0.9]):
            results["conditions"].append(simulate_condition(
                n=600_000, seed=BASE_SEED+i*100+j,
                src_err=src_err, rho_cross=rho, same_copy=0.8
            ))

    for i,src_err in enumerate([0.10,0.25]):
        for j,sc in enumerate([0.0,0.25,0.5,0.75,0.9,1.0]):
            c=simulate_condition(
                n=350_000, seed=BASE_SEED+1000+i*100+j,
                src_err=src_err, rho_cross=0.0, same_copy=sc
            )
            m=c["metrics"]["provisional_same_repeat"]
            results["same_repeat_correlation_sweep"].append({
                "src_err":src_err,"same_copy":sc,
                "endpoint_accuracy":m["endpoint_accuracy"],
                "harmful_replacement_rate":m["harmful_replacement_rate"],
                "correct_per_100k_cost":m["correct_per_100k_cost"]
            })

    dense=[]
    for k,rho in enumerate(np.linspace(0,1,41)):
        c=simulate_condition(
            n=250_000, seed=BASE_SEED+2000+k,
            src_err=.25, rho_cross=float(rho), same_copy=.8
        )
        ind=c["metrics"]["independent_escalation"]["correct_per_100k_cost"]
        abst=c["metrics"]["abstain"]["correct_per_100k_cost"]
        dense.append({"rho":float(rho),"ind_eff":ind,"abst_eff":abst,"diff":ind-abst})
    results["rho_efficiency_sweep_src_err_025"]=dense
    crossing=None
    for a,b in zip(dense[:-1],dense[1:]):
        if a["diff"]>=0 and b["diff"]<0:
            crossing=[a["rho"],b["rho"]]
            break
    results["observed_efficiency_crossing_bracket_src_err_025"]=crossing

    print(json.dumps(results, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
