#!/usr/bin/env python3
from itertools import product
import json

REL=["same_effect","conflicting_effects","disjoint_effects"]
OWNER=["both_alive","owner_crash","owner_slow_late"]
GEN=[0,1]
ROLE_ADD=[0,1]
RETRY=[0,1]
INTERFERENCE=["none","finite4","unbounded"]
RATE=["none","before_apply","after_apply_response_loss"]
STRATEGIES=[
    "symmetric_any_worker_no_sink",
    "static_owner_no_failover",
    "timeout_takeover_no_fence",
    "durable_idempotent_effect_id_sink",
    "conflict_key_epoch_fenced_sink",
    "partitioned_role_local_only",
    "branch_conflict_only",
]

def evaluate(sc, st):
    rel,owner,gen,role_add,retry,interference,rate=sc
    after=(rate=="after_apply_response_loss")
    two_may_act=owner in {"both_alive","owner_slow_late"}
    newer_authority=bool(gen or role_add)
    r=dict(
        unsafe_duplicate=False, unsafe_conflict=False, unsafe_stale_epoch=False,
        finite_progress=False, fail_closed=False, response_loss_ambiguous=False,
        starvation_unproven=False, uses_only_clean_coordination_observations=False,
        requires_shared_authoritative_sink=False, supported_effect_class=True,
        rate_recovery_required=(rate!="none"), phase1_general_acceptance=False,
    )

    if st=="symmetric_any_worker_no_sink":
        r["uses_only_clean_coordination_observations"]=True
        r["finite_progress"]=True
        if rel=="same_effect" and two_may_act:
            r["unsafe_duplicate"]=True
        if rel=="conflicting_effects" and two_may_act:
            r["unsafe_conflict"]=True
        if newer_authority and owner=="owner_slow_late" and rel!="disjoint_effects":
            r["unsafe_stale_epoch"]=True
        if after and retry and rel!="disjoint_effects":
            r["unsafe_duplicate"]=True
            r["response_loss_ambiguous"]=True

    elif st=="static_owner_no_failover":
        r["uses_only_clean_coordination_observations"]=True
        if owner=="owner_crash":
            r["fail_closed"]=True
        else:
            r["finite_progress"]=True
        if newer_authority and owner=="owner_slow_late" and rel!="disjoint_effects":
            r["unsafe_stale_epoch"]=True
        if after and retry and rel!="disjoint_effects":
            r["unsafe_duplicate"]=True
            r["response_loss_ambiguous"]=True

    elif st=="timeout_takeover_no_fence":
        r["uses_only_clean_coordination_observations"]=True
        r["finite_progress"]=True
        if owner=="owner_slow_late" and rel=="same_effect":
            r["unsafe_duplicate"]=True
        if owner=="owner_slow_late" and rel=="conflicting_effects":
            r["unsafe_conflict"]=True
        if newer_authority and owner=="owner_slow_late" and rel!="disjoint_effects":
            r["unsafe_stale_epoch"]=True
        if after and retry and rel!="disjoint_effects":
            r["unsafe_duplicate"]=True
            r["response_loss_ambiguous"]=True

    elif st=="durable_idempotent_effect_id_sink":
        r["requires_shared_authoritative_sink"]=True
        r["finite_progress"]=True
        if rel=="conflicting_effects" and two_may_act:
            r["unsafe_conflict"]=True
        if newer_authority and owner=="owner_slow_late" and rel!="disjoint_effects":
            r["unsafe_stale_epoch"]=True

    elif st=="conflict_key_epoch_fenced_sink":
        r["requires_shared_authoritative_sink"]=True
        r["finite_progress"]=True
        # Sink atomically validates conflict-key epoch/current generation and durable effect id.

    elif st=="partitioned_role_local_only":
        r["uses_only_clean_coordination_observations"]=True
        if rel=="disjoint_effects":
            r["finite_progress"]=True
        else:
            r["supported_effect_class"]=False
            r["fail_closed"]=True

    elif st=="branch_conflict_only":
        # Non-force ref conflict is a storage serialization signal, not a semantic conflict-key fence.
        if rel=="disjoint_effects":
            r["finite_progress"]=(interference!="unbounded")
            r["starvation_unproven"]=(interference=="unbounded")
        else:
            if retry:
                if rel=="same_effect":
                    r["unsafe_duplicate"]=True
                else:
                    r["unsafe_conflict"]=True
            if newer_authority and owner=="owner_slow_late":
                r["unsafe_stale_epoch"]=True
            r["finite_progress"]=(interference!="unbounded")
            r["starvation_unproven"]=(interference=="unbounded")
            if after and retry:
                r["response_loss_ambiguous"]=True
    return r

def count_slice(rows, strategy, predicate, result_predicate):
    subset=[r for sc,s,r in rows if s==strategy and predicate(sc)]
    return {"matching":sum(1 for r in subset if result_predicate(r)),"cases":len(subset)}

def main():
    scenarios=list(product(REL,OWNER,GEN,ROLE_ADD,RETRY,INTERFERENCE,RATE))
    rows=[(sc,st,evaluate(sc,st)) for sc in scenarios for st in STRATEGIES]
    bool_keys=[
        "unsafe_duplicate","unsafe_conflict","unsafe_stale_epoch","finite_progress",
        "fail_closed","response_loss_ambiguous","starvation_unproven",
        "uses_only_clean_coordination_observations","requires_shared_authoritative_sink",
        "supported_effect_class","rate_recovery_required","phase1_general_acceptance",
    ]
    aggregates={}
    for st in STRATEGIES:
        rs=[r for sc,s,r in rows if s==st]
        aggregates[st]={k:sum(int(r[k]) for r in rs) for k in bool_keys}
        aggregates[st]["scenario_count"]=len(rs)

    targeted={
        "static_owner_crash_noncommutative_no_progress": count_slice(
            rows,"static_owner_no_failover",
            lambda sc: sc[0] in {"same_effect","conflicting_effects"} and sc[1]=="owner_crash",
            lambda r: not r["finite_progress"]),
        "timeout_takeover_slow_late_noncommutative_unsafe": count_slice(
            rows,"timeout_takeover_no_fence",
            lambda sc: sc[0] in {"same_effect","conflicting_effects"} and sc[1]=="owner_slow_late",
            lambda r: r["unsafe_duplicate"] or r["unsafe_conflict"] or r["unsafe_stale_epoch"]),
        "idempotent_sink_same_effect_no_duplicate": count_slice(
            rows,"durable_idempotent_effect_id_sink",
            lambda sc: sc[0]=="same_effect",
            lambda r: not r["unsafe_duplicate"]),
        "idempotent_sink_conflicting_effects_unsafe_when_two_may_act": count_slice(
            rows,"durable_idempotent_effect_id_sink",
            lambda sc: sc[0]=="conflicting_effects" and sc[1] in {"both_alive","owner_slow_late"},
            lambda r: r["unsafe_conflict"]),
        "fenced_sink_all_safe_and_live": count_slice(
            rows,"conflict_key_epoch_fenced_sink",lambda sc: True,
            lambda r: r["finite_progress"] and not (r["unsafe_duplicate"] or r["unsafe_conflict"] or r["unsafe_stale_epoch"])),
        "partitioned_disjoint_safe_and_live": count_slice(
            rows,"partitioned_role_local_only",lambda sc: sc[0]=="disjoint_effects",
            lambda r: r["finite_progress"] and not (r["unsafe_duplicate"] or r["unsafe_conflict"] or r["unsafe_stale_epoch"])),
        "partitioned_non_disjoint_fail_closed": count_slice(
            rows,"partitioned_role_local_only",lambda sc: sc[0]!="disjoint_effects",
            lambda r: r["fail_closed"] and not r["supported_effect_class"]),
        "branch_unbounded_interference_starvation_unproven": count_slice(
            rows,"branch_conflict_only",lambda sc: sc[5]=="unbounded",
            lambda r: r["starvation_unproven"]),
    }
    print(json.dumps({
        "scenario_count":len(scenarios),"strategy_evaluations":len(rows),
        "aggregates":aggregates,"targeted_slices":targeted,
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
