#!/usr/bin/env python3
from itertools import product
import json

MISSING=[0,1]
DUPLICATE_CROSS_NAMESPACE=[0,1]
STALE_GENERATION=[0,1]
MEMBERSHIP_CHANGE=["none","add","remove"]
RESPONSE_LOSS=[0,1]
CONCURRENT_DISJOINT_WRITE=[0,1]
MALICIOUS_VALID_HASH_PAYLOAD=[0,1]
DYNAMIC_OUTPUT=[0,1]
STRATEGIES=[
    "snapshot_commit_sha_only",
    "opaque_tree_hash_as_terminal_negative",
    "precommitted_exact_tree_hash",
    "expected_path_tree_scan",
    "hypothetical_sanitized_merkle_proofs",
    "semantic_reducer_baseline",
    "role_local_only_no_global_claim",
]

def evaluate(sc,st):
    miss,dupx,stale,mem,resp,conc,mal,dynamic=sc
    adverse=bool(miss or dupx or stale or mem!="none" or mal)
    r=dict(
        snapshot_identity=False,inclusion_certified=False,exact_bytes_certified=False,
        required_completeness_certified=False,current_generation_certified=False,
        semantic_correctness_certified=False,aggregate_value_computed=False,
        terminal_claim=False,false_terminal=False,false_exclusion=False,
        response_loss_reconciled=False,clean_boundary_compatible=False,
        requires_other_role_metadata=False,requires_custom_proof_surface=False,
        requires_other_role_contents=False,dynamic_output_supported=True,
    )
    if st=="snapshot_commit_sha_only":
        r["snapshot_identity"]=True
        r["clean_boundary_compatible"]=True
        r["response_loss_reconciled"]=not (resp and conc)
    elif st=="opaque_tree_hash_as_terminal_negative":
        r["snapshot_identity"]=True
        r["terminal_claim"]=True
        r["clean_boundary_compatible"]=True
        r["false_terminal"]=adverse
        r["response_loss_reconciled"]=not (resp and conc)
    elif st=="precommitted_exact_tree_hash":
        r["snapshot_identity"]=True
        r["dynamic_output_supported"]=not dynamic
        r["clean_boundary_compatible"]=True
        if dynamic:
            r["false_exclusion"]=True
        else:
            exact_match=not adverse and not conc
            r["exact_bytes_certified"]=exact_match
            r["inclusion_certified"]=exact_match
            r["required_completeness_certified"]=exact_match
            r["current_generation_certified"]=exact_match
            r["semantic_correctness_certified"]=exact_match
            r["terminal_claim"]=exact_match
            r["false_exclusion"]=not exact_match
            r["response_loss_reconciled"]=not (resp and conc)
    elif st=="expected_path_tree_scan":
        r["snapshot_identity"]=True
        r["requires_other_role_metadata"]=True
        r["inclusion_certified"]=not miss
        r["required_completeness_certified"]=not miss and mem=="none"
        r["current_generation_certified"]=not stale and mem=="none"
        r["semantic_correctness_certified"]=not mal and not dupx
        r["terminal_claim"]=r["required_completeness_certified"] and r["current_generation_certified"] and r["semantic_correctness_certified"]
        r["response_loss_reconciled"]=not (resp and conc)
    elif st=="hypothetical_sanitized_merkle_proofs":
        r["snapshot_identity"]=True
        r["requires_custom_proof_surface"]=True
        r["inclusion_certified"]=not miss
        r["required_completeness_certified"]=not miss and mem=="none"
        r["current_generation_certified"]=not stale and mem=="none"
        # Inclusion of an unknown hash does not prove semantics of a dynamic output.
        r["semantic_correctness_certified"]=not mal and not dupx and not dynamic
        r["terminal_claim"]=r["required_completeness_certified"] and r["current_generation_certified"] and r["semantic_correctness_certified"]
        r["response_loss_reconciled"]=not (resp and conc)
    elif st=="semantic_reducer_baseline":
        r["snapshot_identity"]=True
        r["requires_other_role_metadata"]=True
        r["requires_other_role_contents"]=True
        r["inclusion_certified"]=not miss
        r["required_completeness_certified"]=not miss
        r["current_generation_certified"]=not stale
        r["semantic_correctness_certified"]=not mal
        r["aggregate_value_computed"]=not miss and not stale and not mal
        r["terminal_claim"]=r["aggregate_value_computed"]
        r["response_loss_reconciled"]=True
    elif st=="role_local_only_no_global_claim":
        r["clean_boundary_compatible"]=True
        r["response_loss_reconciled"]=True
    return r

def slice_count(rows,st,pred,rpred):
    subset=[r for sc,s,r in rows if s==st and pred(sc)]
    return {"matching":sum(1 for r in subset if rpred(r)),"cases":len(subset)}

def main():
    scenarios=list(product(MISSING,DUPLICATE_CROSS_NAMESPACE,STALE_GENERATION,MEMBERSHIP_CHANGE,RESPONSE_LOSS,CONCURRENT_DISJOINT_WRITE,MALICIOUS_VALID_HASH_PAYLOAD,DYNAMIC_OUTPUT))
    rows=[(sc,st,evaluate(sc,st)) for sc in scenarios for st in STRATEGIES]
    keys=["snapshot_identity","inclusion_certified","exact_bytes_certified","required_completeness_certified",
          "current_generation_certified","semantic_correctness_certified","aggregate_value_computed","terminal_claim",
          "false_terminal","false_exclusion","response_loss_reconciled","clean_boundary_compatible",
          "requires_other_role_metadata","requires_custom_proof_surface","requires_other_role_contents","dynamic_output_supported"]
    aggregates={}
    for st in STRATEGIES:
        rs=[r for sc,s,r in rows if s==st]
        aggregates[st]={k:sum(int(r[k]) for r in rs) for k in keys}
        aggregates[st]["scenario_count"]=len(rs)
    targeted={
        "opaque_tree_hash_false_terminal":slice_count(rows,"opaque_tree_hash_as_terminal_negative",lambda sc:True,lambda r:r["false_terminal"]),
        "snapshot_sha_response_loss_plus_concurrent_write_unreconciled":slice_count(rows,"snapshot_commit_sha_only",lambda sc:sc[4]==1 and sc[5]==1,lambda r:not r["response_loss_reconciled"]),
        "precommitted_exact_tree_dynamic_output_unsupported":slice_count(rows,"precommitted_exact_tree_hash",lambda sc:sc[7]==1,lambda r:not r["dynamic_output_supported"] and r["false_exclusion"]),
        "precommitted_exact_tree_terminal":slice_count(rows,"precommitted_exact_tree_hash",lambda sc:True,lambda r:r["terminal_claim"]),
        "tree_scan_requires_other_role_metadata":slice_count(rows,"expected_path_tree_scan",lambda sc:True,lambda r:r["requires_other_role_metadata"]),
        "merkle_proof_dynamic_semantics_not_certified":slice_count(rows,"hypothetical_sanitized_merkle_proofs",lambda sc:sc[7]==1,lambda r:not r["semantic_correctness_certified"]),
        "semantic_reducer_requires_forbidden_cross_role_reads":slice_count(rows,"semantic_reducer_baseline",lambda sc:True,lambda r:r["requires_other_role_metadata"] and r["requires_other_role_contents"]),
    }
    print(json.dumps({"scenario_count":len(scenarios),"strategy_evaluations":len(rows),"aggregates":aggregates,"targeted_slices":targeted},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
