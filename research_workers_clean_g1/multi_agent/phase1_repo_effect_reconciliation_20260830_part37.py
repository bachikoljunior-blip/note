from itertools import product
from collections import Counter
import json

AXES = {
    "shape": ["single", "multi"],
    "authority_event": ["none", "cancel", "supersede"],
    "unrelated_advance": [False, True],
    "response_lost": [False, True],
    "post_descendant": [False, True],
    "marker_overwritten": [False, True],
}
STRATEGIES = [
    "separate_precheck_blind_retry",
    "separate_marker_fail_closed_if_missing",
    "single_object_cas_with_applied_floor",
    "git_ref_fast_forward_with_ancestry",
    "git_ref_fast_forward_exact_sha_retry",
    "fail_closed_on_ambiguity",
]

def evaluate(strategy, s):
    out = dict(supported=True, unsafe_stale=0, duplicate=0, false_block=0, extra_conflict=0, reconciled=0, terminal=0, pending=0)
    authority_changed = s["authority_event"] != "none"
    if strategy == "separate_precheck_blind_retry":
        if authority_changed:
            out["unsafe_stale"] = 1
        out["terminal"] = 1
        if s["response_lost"] and not authority_changed:
            out["duplicate"] = 1
    elif strategy == "separate_marker_fail_closed_if_missing":
        if authority_changed:
            out["unsafe_stale"] = 1
            out["terminal"] = 1
        elif s["response_lost"]:
            if s["marker_overwritten"]:
                out["false_block"] = 1
                out["pending"] = 1
            else:
                out["reconciled"] = 1
                out["terminal"] = 1
        else:
            out["terminal"] = 1
    elif strategy == "single_object_cas_with_applied_floor":
        if s["shape"] != "single":
            out["supported"] = False
            return out
        if authority_changed:
            out["pending"] = 1
        else:
            out["terminal"] = 1
            if s["response_lost"]:
                out["reconciled"] = 1
    elif strategy == "git_ref_fast_forward_with_ancestry":
        pre_advance = authority_changed or s["unrelated_advance"]
        if pre_advance:
            out["pending"] = 1
            if s["unrelated_advance"] and not authority_changed:
                out["extra_conflict"] = 1
        else:
            out["terminal"] = 1
            if s["response_lost"]:
                out["reconciled"] = 1
    elif strategy == "git_ref_fast_forward_exact_sha_retry":
        pre_advance = authority_changed or s["unrelated_advance"]
        if pre_advance:
            out["pending"] = 1
            if s["unrelated_advance"] and not authority_changed:
                out["extra_conflict"] = 1
        else:
            out["terminal"] = 1
            if s["response_lost"] and s["post_descendant"]:
                out["duplicate"] = 1
    elif strategy == "fail_closed_on_ambiguity":
        if authority_changed:
            out["pending"] = 1
        elif s["response_lost"]:
            out["false_block"] = 1
            out["pending"] = 1
        else:
            out["terminal"] = 1
    return out

def run():
    scenarios = [dict(zip(AXES, vals)) for vals in product(*AXES.values())]
    aggregate = {}
    for strategy in STRATEGIES:
        c = Counter()
        supported = 0
        for s in scenarios:
            o = evaluate(strategy, s)
            if not o["supported"]:
                continue
            supported += 1
            for k, v in o.items():
                if k != "supported":
                    c[k] += v
        aggregate[strategy] = {"supported_scenarios": supported, **dict(c)}
    return {
        "scenario_count": len(scenarios),
        "strategy_evaluations": sum(v["supported_scenarios"] for v in aggregate.values()),
        "axes": AXES,
        "aggregate": aggregate,
        "interpretation": {
            "separate_authority_target": "A precheck of a separate authority file does not fence a cancellation/supersession that lands before the target write.",
            "single_object": "When authority and canonical repository effect are co-located, the effect/status transition is one current-blob CAS; response loss is reconciled by transition identity/applied-through state.",
            "git_ref": "For multi-path publication, a proposal commit based on B plus update_ref(force=false) rejects any intervening branch advance as non-fast-forward. This is safe but coarse: unrelated advances also conflict.",
            "response_loss": "After successful ref publication followed by a descendant commit, exact ref equality is insufficient; ancestry/compare or a persistent transition identity is required before retry.",
            "scope_limit": "Results exclude complete same-domain force rewind; Part 36 keeps that as an unresolved capability boundary."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
