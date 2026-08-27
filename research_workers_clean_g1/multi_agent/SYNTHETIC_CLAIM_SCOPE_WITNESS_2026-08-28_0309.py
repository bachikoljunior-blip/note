from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from collections import Counter
import json

ROUTE_RANK = {"BLOCK": 0, "WHOLE_REDRAW": 1, "ENLARGED": 2, "LOCAL": 3}

@dataclass(frozen=True)
class Evidence:
    live_scope: bool
    record_sig_ok: bool
    presented_chain_internal_ok: bool
    trusted_live_head_match: bool
    checkpoint_authenticated: bool
    checkpoint_tail_consistent: bool
    transparency_monitored_consistent: bool
    epoch_match: bool
    topology_match: bool
    surface_manifest_complete: bool
    mandatory_mediation_complete: bool
    runtime_dep_exact: bool
    static_dep_overapprox_complete: bool
    obligations_clear: bool
    effects_reconciled: bool
    unknown_surface_effectless_proved: bool
    attended_state_rebound: bool

def split_scope_policy(e: Evidence) -> str:
    if not e.record_sig_ok or not e.obligations_clear or not e.effects_reconciled:
        return "BLOCK"
    if e.live_scope:
        history_ok = e.presented_chain_internal_ok and e.trusted_live_head_match
    else:
        history_ok = (
            e.presented_chain_internal_ok
            and e.checkpoint_authenticated
            and e.checkpoint_tail_consistent
            and e.transparency_monitored_consistent
        )
    if not history_ok:
        return "BLOCK"
    capture_ok = (
        e.epoch_match
        and e.topology_match
        and e.surface_manifest_complete
        and e.mandatory_mediation_complete
    )
    if not capture_ok or not e.attended_state_rebound:
        return "WHOLE_REDRAW" if e.unknown_surface_effectless_proved else "BLOCK"
    if e.runtime_dep_exact:
        return "LOCAL"
    if e.static_dep_overapprox_complete:
        return "ENLARGED"
    return "WHOLE_REDRAW" if e.unknown_surface_effectless_proved else "BLOCK"

def global_everywhere_policy(e: Evidence) -> str:
    if not e.record_sig_ok or not e.obligations_clear or not e.effects_reconciled:
        return "BLOCK"
    history_ok = (
        e.presented_chain_internal_ok
        and e.checkpoint_authenticated
        and e.checkpoint_tail_consistent
        and e.transparency_monitored_consistent
    )
    if e.live_scope:
        history_ok = history_ok and e.trusted_live_head_match
    if not history_ok:
        return "BLOCK"
    capture_ok = (
        e.epoch_match
        and e.topology_match
        and e.surface_manifest_complete
        and e.mandatory_mediation_complete
    )
    if not capture_ok or not e.attended_state_rebound:
        return "WHOLE_REDRAW" if e.unknown_surface_effectless_proved else "BLOCK"
    if e.runtime_dep_exact:
        return "LOCAL"
    if e.static_dep_overapprox_complete:
        return "ENLARGED"
    return "WHOLE_REDRAW" if e.unknown_surface_effectless_proved else "BLOCK"

def absence_as_safe_policy(e: Evidence) -> str:
    if not e.record_sig_ok or not e.obligations_clear or not e.effects_reconciled:
        return "BLOCK"
    if not e.epoch_match or not e.topology_match:
        return "WHOLE_REDRAW"
    if e.runtime_dep_exact:
        return "LOCAL"
    if e.static_dep_overapprox_complete:
        return "ENLARGED"
    return "LOCAL"

def modeled_max_route(e: Evidence) -> str:
    return split_scope_policy(e)

def evaluate(policy):
    fields = list(Evidence.__dataclass_fields__)
    result = Counter()
    route_counts = Counter()
    for bits in product((False, True), repeat=len(fields)):
        e = Evidence(**dict(zip(fields, bits)))
        got = policy(e)
        truth = modeled_max_route(e)
        route_counts[got] += 1
        if ROUTE_RANK[got] > ROUTE_RANK[truth]:
            result["unsafe"] += 1
        elif ROUTE_RANK[got] < ROUTE_RANK[truth]:
            result["overconservative"] += 1
        else:
            result["exact"] += 1
        result["states"] += 1
    return {
        "states": result["states"],
        "unsafe": result["unsafe"],
        "overconservative": result["overconservative"],
        "exact": result["exact"],
        "route_counts": dict(route_counts),
    }

def monotonicity_check():
    fields = [f for f in Evidence.__dataclass_fields__ if f != "live_scope"]
    violations = 0
    checks = 0
    for live in (False, True):
        for bits in product((False, True), repeat=len(fields)):
            d = dict(zip(fields, bits))
            d["live_scope"] = live
            e = Evidence(**d)
            before = split_scope_policy(e)
            for f in fields:
                if getattr(e, f):
                    d2 = dict(d)
                    d2[f] = False
                    after = split_scope_policy(Evidence(**d2))
                    checks += 1
                    if ROUTE_RANK[after] > ROUTE_RANK[before]:
                        violations += 1
    return {"one_bit_positive_evidence_removals": checks, "violations": violations}

def named_cases():
    base = dict(live_scope=True,record_sig_ok=True,presented_chain_internal_ok=True,trusted_live_head_match=True,checkpoint_authenticated=False,checkpoint_tail_consistent=False,transparency_monitored_consistent=False,epoch_match=True,topology_match=True,surface_manifest_complete=True,mandatory_mediation_complete=True,runtime_dep_exact=True,static_dep_overapprox_complete=True,obligations_clear=True,effects_reconciled=True,unknown_surface_effectless_proved=False,attended_state_rebound=True)
    cases=[]
    def add(name, **changes):
        d=dict(base); d.update(changes); e=Evidence(**d)
        cases.append({"name":name,"split":split_scope_policy(e),"global_everywhere":global_everywhere_policy(e),"absence_as_safe":absence_as_safe_policy(e),"modeled_max":modeled_max_route(e)})
    add("live_trusted_head_no_global_transparency")
    add("live_suffix_suppression_detected", trusted_live_head_match=False)
    add("stale_capture_epoch_effectless", epoch_match=False, unknown_surface_effectless_proved=True)
    add("unregistered_effect_capable_surface", surface_manifest_complete=False, mandatory_mediation_complete=False)
    add("unregistered_effectless_surface", surface_manifest_complete=False, mandatory_mediation_complete=False, unknown_surface_effectless_proved=True)
    add("runtime_dep_missing_static_complete", runtime_dep_exact=False, static_dep_overapprox_complete=True)
    add("runtime_and_static_dep_unknown_effectless", runtime_dep_exact=False, static_dep_overapprox_complete=False, unknown_surface_effectless_proved=True)
    add("attended_state_not_rebound_effectless", attended_state_rebound=False, unknown_surface_effectless_proved=True)
    add("ambiguous_external_effect", effects_reconciled=False)
    add("authorization_or_obligation_conflict", obligations_clear=False)
    off=dict(base); off.update(live_scope=False,trusted_live_head_match=False,checkpoint_authenticated=True,checkpoint_tail_consistent=True,transparency_monitored_consistent=True)
    for name, changes in [("offline_checkpoint_plus_monitored_transparency",{}),("offline_checkpoint_conflict",{"checkpoint_tail_consistent":False}),("offline_no_equivocation_monitor",{"transparency_monitored_consistent":False})]:
        d=dict(off); d.update(changes); e=Evidence(**d)
        cases.append({"name":name,"split":split_scope_policy(e),"global_everywhere":global_everywhere_policy(e),"absence_as_safe":absence_as_safe_policy(e),"modeled_max":modeled_max_route(e)})
    return cases

if __name__ == "__main__":
    print(json.dumps({"split_scope":evaluate(split_scope_policy),"global_everywhere":evaluate(global_everywhere_policy),"absence_as_safe":evaluate(absence_as_safe_policy),"evidence_monotonicity":monotonicity_check(),"named_cases":named_cases(),"scope":["Finite Boolean mechanism model, not a deployment probability model.","Positive evidence bits are assumed truthful; forgery/collusion are not modeled.","The modeled maximum route is defined by the same explicit safety semantics as split_scope_policy, so zero unsafe there is a structural consistency check, not empirical validation.","Counts over the full Boolean cube are not operational rates or thresholds."]}, indent=2, sort_keys=True))
