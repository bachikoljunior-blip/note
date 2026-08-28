#!/usr/bin/env python3
"""Finite synthetic stress test for effect-vector terminality and recovery-policy archives.

Equal-weight mechanism lattice; counts are not empirical failure rates.
"""
from itertools import product
from collections import Counter, defaultdict
import json

EFFECT_CASES = {
    "prepared_not_seen": {"cap": "PREPARED", "obs": "NOT_SEEN", "actual": False},
    "minted_not_seen": {"cap": "MINTED", "obs": "NOT_SEEN", "actual": False},
    "ambig_not_applied": {"cap": "MINTED", "obs": "AMBIGUOUS", "actual": False},
    "ambig_applied": {"cap": "CONSUMED", "obs": "AMBIGUOUS", "actual": True},
    "applied": {"cap": "CONSUMED", "obs": "APPLIED", "actual": True},
    "failed": {"cap": "CONSUMED", "obs": "FAILED", "actual": False},
    "expired_not_seen": {"cap": "EXPIRED", "obs": "NOT_SEEN", "actual": False},
}

EFFECT_CONTRACTS = {
    "reversible_comp": {"compensatable": True, "irreversible": False},
    "irreversible_comp": {"compensatable": True, "irreversible": True},
    "irreversible_no_comp": {"compensatable": False, "irreversible": True},
}

PROFILES = {
    "strong_current": dict(parent_current=True, auth="irrevocable", single_use=True,
                           effect_idem=True, comp_idem=True, status=True,
                           dispatcher_takeover=False, compensator_takeover=False),
    "strong_takeover": dict(parent_current=True, auth="irrevocable", single_use=True,
                            effect_idem=True, comp_idem=True, status=True,
                            dispatcher_takeover=True, compensator_takeover=True),
    "irrevocable_superseded": dict(parent_current=False, auth="irrevocable", single_use=True,
                                   effect_idem=True, comp_idem=True, status=True,
                                   dispatcher_takeover=True, compensator_takeover=True),
    "revocable_superseded": dict(parent_current=False, auth="revocable", single_use=True,
                                 effect_idem=True, comp_idem=True, status=True,
                                 dispatcher_takeover=False, compensator_takeover=False),
    "no_status_retained": dict(parent_current=True, auth="irrevocable", single_use=True,
                               effect_idem=True, comp_idem=True, status=False,
                               dispatcher_takeover=False, compensator_takeover=False),
    "no_status_pruned_takeover": dict(parent_current=True, auth="irrevocable", single_use=False,
                                      effect_idem=False, comp_idem=False, status=False,
                                      dispatcher_takeover=True, compensator_takeover=True),
    "effect_pruned_no_status": dict(parent_current=True, auth="irrevocable", single_use=False,
                                    effect_idem=False, comp_idem=True, status=False,
                                    dispatcher_takeover=False, compensator_takeover=False),
    "comp_pruned_takeover": dict(parent_current=True, auth="irrevocable", single_use=True,
                                 effect_idem=True, comp_idem=False, status=True,
                                 dispatcher_takeover=False, compensator_takeover=True),
}

COMP_PATTERNS = [
    "all_success",
    "first_ambig_applied",
    "first_ambig_not_applied",
    "first_late_failed",
    "first_reversed",
    "first_late_failed_then_success",
    "first_reversed_then_success",
    "alternating_success_late_failed",
]

SAFE_POLICIES = ["fail_closed_manual", "forward_complete", "greedy_rollback"]
NEGATIVE_POLICIES = ["neg_blind_forward", "neg_terminal_on_comp_accept", "neg_root_boolean"]
POLICIES = SAFE_POLICIES + NEGATIVE_POLICIES


def comp_outcome(pattern, comp_rank):
    if pattern == "all_success":
        return "success", None
    if pattern == "first_ambig_applied":
        return ("ambiguous_applied", None) if comp_rank == 0 else ("success", None)
    if pattern == "first_ambig_not_applied":
        return ("ambiguous_not_applied", None) if comp_rank == 0 else ("success", None)
    if pattern == "first_late_failed":
        return ("late_failed", None) if comp_rank == 0 else ("success", None)
    if pattern == "first_reversed":
        return ("reversed", None) if comp_rank == 0 else ("success", None)
    if pattern == "first_late_failed_then_success":
        return ("late_failed", "success") if comp_rank == 0 else ("success", None)
    if pattern == "first_reversed_then_success":
        return ("reversed", "success") if comp_rank == 0 else ("success", None)
    if pattern == "alternating_success_late_failed":
        return ("success", None) if comp_rank % 2 == 0 else ("late_failed", None)
    raise ValueError(pattern)


def auth_valid_for_fresh_effect(case, profile):
    cap = case["cap"]
    if cap == "EXPIRED":
        return False
    if cap == "PREPARED":
        return profile["parent_current"]
    if cap == "MINTED":
        return profile["auth"] == "irrevocable" or profile["parent_current"]
    if cap == "CONSUMED":
        return False
    return False


def forward_one(case, profile, safe=True):
    """Return metrics for settling one required original effect to APPLIED."""
    r = Counter()
    obs, actual = case["obs"], case["actual"]
    if obs == "APPLIED":
        r["settled"] = 1
        return r

    if obs == "AMBIGUOUS":
        if profile["status"]:
            r["actions"] += 1
            r["status_lookups"] += 1
            if actual:
                r["settled"] = 1
                return r
            can_auth = auth_valid_for_fresh_effect(case, profile)
            if not can_auth:
                if safe:
                    r["unresolved"] += 1
                    return r
                r["actions"] += 1
                r["new_effects"] += 1
                r["stale_auth"] += 1
                r["settled"] = 1
                return r
            if safe and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
                r["unresolved"] += 1
                return r
            r["actions"] += 1
            r["new_effects"] += 1
            if (not safe) and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
                r["dup_effect"] += 1
            r["settled"] = 1
            return r

        if actual:
            if profile["single_use"] or profile["effect_idem"]:
                r["actions"] += 1
                r["settled"] = 1
                return r
            if safe:
                r["unresolved"] += 1
                return r
            r["actions"] += 1
            r["dup_effect"] += 1
            r["settled"] = 1
            return r

        can_auth = auth_valid_for_fresh_effect(case, profile)
        if not can_auth:
            if safe:
                r["unresolved"] += 1
                return r
            r["actions"] += 1
            r["new_effects"] += 1
            r["stale_auth"] += 1
            r["settled"] = 1
            return r
        if safe and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
            r["unresolved"] += 1
            return r
        r["actions"] += 1
        r["new_effects"] += 1
        if (not safe) and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
            r["dup_effect"] += 1
        r["settled"] = 1
        return r

    if obs in ("NOT_SEEN", "FAILED"):
        can_auth = auth_valid_for_fresh_effect(case, profile)
        if obs == "FAILED" and case["cap"] == "CONSUMED":
            can_auth = profile["parent_current"]
        if not can_auth:
            if safe:
                r["unresolved"] += 1
                return r
            r["actions"] += 1
            r["new_effects"] += 1
            r["stale_auth"] += 1
            r["settled"] = 1
            return r
        if safe and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
            r["unresolved"] += 1
            return r
        r["actions"] += 1
        r["new_effects"] += 1
        if (not safe) and profile["dispatcher_takeover"] and not (profile["single_use"] or profile["effect_idem"]):
            r["dup_effect"] += 1
        r["settled"] = 1
        return r

    r["unresolved"] += 1
    return r


def rollback_one(case, contract, profile, pattern, comp_rank, safe=True, terminal_on_accept=False):
    """Return metrics for settling one original effect toward a rollback disposition."""
    r = Counter()
    obs, actual = case["obs"], case["actual"]

    if obs == "AMBIGUOUS":
        if profile["status"]:
            r["actions"] += 1
            r["status_lookups"] += 1
        elif safe:
            r["unresolved"] += 1
            return r

    if not actual:
        r["settled"] = 1
        return r

    if not contract["compensatable"]:
        r["unresolved"] += 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    if safe and profile["compensator_takeover"] and not profile["comp_idem"]:
        r["unresolved"] += 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    r["actions"] += 1
    r["comp_issued"] += 1
    r["comp_depth"] = 1
    if (not safe) and profile["compensator_takeover"] and not profile["comp_idem"]:
        r["dup_comp"] += 1
        r["stale_comp"] += 1

    first, second = comp_outcome(pattern, comp_rank)

    if terminal_on_accept and first in ("success", "ambiguous_applied", "late_failed", "reversed"):
        r["settled"] = 1
        if first != "success":
            r["false_terminal_event"] += 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    if first == "success":
        r["settled"] = 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    if first in ("ambiguous_applied", "ambiguous_not_applied"):
        if profile["status"] and profile["comp_idem"]:
            r["actions"] += 1
            r["status_lookups"] += 1
            if first == "ambiguous_not_applied":
                r["actions"] += 1
                r["comp_issued"] += 1
            r["settled"] = 1
            if contract["irreversible"]:
                r["residual_exposure"] += 1
            return r
        r["unresolved"] += 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    if first in ("late_failed", "reversed"):
        if second == "success":
            if safe and profile["compensator_takeover"] and not profile["comp_idem"]:
                r["unresolved"] += 1
                if contract["irreversible"]:
                    r["residual_exposure"] += 1
                return r
            r["actions"] += 1
            r["comp_issued"] += 1
            r["comp_depth"] = 2
            if (not safe) and profile["compensator_takeover"] and not profile["comp_idem"]:
                r["dup_comp"] += 1
                r["stale_comp"] += 1
            r["settled"] = 1
            if contract["irreversible"]:
                r["residual_exposure"] += 1
            return r
        r["unresolved"] += 1
        if contract["irreversible"]:
            r["residual_exposure"] += 1
        return r

    r["unresolved"] += 1
    return r


def evaluate(policy, cases, contracts, profile, pattern):
    r = Counter()
    if policy in ("forward_complete", "neg_blind_forward"):
        safe = policy == "forward_complete"
        settled_all = True
        for case in cases:
            x = forward_one(case, profile, safe=safe)
            settled_all = settled_all and bool(x["settled"])
            for k, v in x.items():
                if k != "settled":
                    r[k] += v
        r["terminal"] = int(settled_all)
        r["terminal_forward"] = int(settled_all)
        if settled_all:
            r["residual_exposure"] += sum(1 for c in contracts if c["irreversible"])
        r["unsafe"] = int(r["dup_effect"] > 0 or r["stale_auth"] > 0)
        r["false_terminal_scenario"] = int(r["terminal"] and r["unsafe"])
        return r

    if policy in ("greedy_rollback", "neg_terminal_on_comp_accept"):
        safe = policy == "greedy_rollback"
        terminal_on_accept = policy == "neg_terminal_on_comp_accept"
        comp_rank_by_effect = {}
        rank = 0
        for i, (case, contract) in enumerate(zip(cases, contracts)):
            if case["actual"] and contract["compensatable"]:
                comp_rank_by_effect[i] = rank
                rank += 1
        settled_all = True
        max_depth = 0
        for i, (case, contract) in enumerate(zip(cases, contracts)):
            x = rollback_one(case, contract, profile, pattern,
                             comp_rank_by_effect.get(i, 0), safe=safe,
                             terminal_on_accept=terminal_on_accept)
            settled_all = settled_all and bool(x["settled"])
            max_depth = max(max_depth, x["comp_depth"])
            for k, v in x.items():
                if k not in ("settled", "comp_depth"):
                    r[k] += v
        r["comp_depth"] = max_depth
        r["terminal"] = int(settled_all)
        r["terminal_rollback"] = int(settled_all)
        r["unsafe"] = int(r["dup_comp"] > 0 or r["stale_comp"] > 0 or r["false_terminal_event"] > 0)
        r["false_terminal_scenario"] = int(r["terminal"] and r["unsafe"])
        return r

    if policy == "fail_closed_manual":
        all_applied = all(case["obs"] == "APPLIED" for case in cases)
        r["terminal"] = int(all_applied)
        r["terminal_forward"] = int(all_applied)
        r["unresolved"] = sum(1 for case in cases if case["obs"] != "APPLIED")
        if all_applied:
            r["residual_exposure"] = sum(1 for c in contracts if c["irreversible"])
        return r

    if policy == "neg_root_boolean":
        if all(case["obs"] == "APPLIED" for case in cases):
            r["terminal"] = 1
            r["terminal_forward"] = 1
            r["residual_exposure"] = sum(1 for c in contracts if c["irreversible"])
            return r
        for i, (case, contract) in enumerate(zip(cases, contracts)):
            if case["obs"] == "AMBIGUOUS":
                r["unresolved"] += 1
                r["false_terminal_event"] += 1
            if case["actual"]:
                if contract["compensatable"]:
                    r["actions"] += 1
                    r["comp_issued"] += 1
                    if profile["compensator_takeover"] and not profile["comp_idem"]:
                        r["dup_comp"] += 1
                        r["stale_comp"] += 1
                    comp_rank = sum(1 for j in range(i) if cases[j]["actual"] and contracts[j]["compensatable"])
                    first, _ = comp_outcome(pattern, comp_rank)
                    if first != "success":
                        r["false_terminal_event"] += 1
                    if contract["irreversible"]:
                        r["residual_exposure"] += 1
                else:
                    r["false_terminal_event"] += 1
                    if contract["irreversible"]:
                        r["residual_exposure"] += 1
        r["terminal"] = 1
        r["terminal_rollback"] = 1
        r["unsafe"] = int(r["dup_comp"] > 0 or r["stale_comp"] > 0 or r["false_terminal_event"] > 0)
        r["false_terminal_scenario"] = int(r["unsafe"])
        return r

    raise ValueError(policy)


def iter_scenarios():
    for n in (2, 3):
        for case_names in product(EFFECT_CASES, repeat=n):
            cases = [EFFECT_CASES[x] for x in case_names]
            for contract_names in product(EFFECT_CONTRACTS, repeat=n):
                contracts = [EFFECT_CONTRACTS[x] for x in contract_names]
                for profile_name, profile in PROFILES.items():
                    for pattern in COMP_PATTERNS:
                        yield n, case_names, contract_names, profile_name, profile, pattern, cases, contracts


def pareto_front(outcomes):
    """Nondominated terminal safe branches. All dimensions are costs."""
    nd = []
    for i, (policy, r) in enumerate(outcomes):
        vec = (r["actions"], r["new_effects"], r["comp_issued"], r["residual_exposure"])
        dominated = False
        for j, (_, r2) in enumerate(outcomes):
            if i == j:
                continue
            vec2 = (r2["actions"], r2["new_effects"], r2["comp_issued"], r2["residual_exposure"])
            if all(a <= b for a, b in zip(vec2, vec)) and any(a < b for a, b in zip(vec2, vec)):
                dominated = True
                break
        if not dominated:
            nd.append((policy, r))
    return nd


def main():
    totals = {p: Counter() for p in POLICIES}
    slices = defaultdict(Counter)
    scenarios = 0
    archive_covered = 0
    archive_pareto_multi = 0
    archive_dual_orientation = 0
    archive_niches = Counter()
    pareto_branch_counts = Counter()
    qd_orientation_branch_counts = Counter()

    for n, case_names, contract_names, profile_name, profile, pattern, cases, contracts in iter_scenarios():
        scenarios += 1
        results = {p: evaluate(p, cases, contracts, profile, pattern) for p in POLICIES}

        for p, r in results.items():
            totals[p]["scenarios"] += 1
            for k, v in r.items():
                totals[p][k] += v
            if r["terminal"]:
                totals[p]["terminal_scenarios"] += 1
            if r["unsafe"]:
                totals[p]["unsafe_scenarios"] += 1
            if r["false_terminal_scenario"]:
                totals[p]["false_terminal_scenarios"] += 1
            if r["dup_effect"]:
                totals[p]["duplicate_effect_scenarios"] += 1
            if r["dup_comp"]:
                totals[p]["duplicate_compensation_scenarios"] += 1
            if r["stale_auth"] or r["stale_comp"]:
                totals[p]["stale_authorization_scenarios"] += 1
            if r["unresolved"]:
                totals[p]["unresolved_scenarios"] += 1
            if r["comp_depth"] >= 2:
                totals[p]["depth2_compensation_scenarios"] += 1

        safe_terminal = [(p, results[p]) for p in SAFE_POLICIES if results[p]["terminal"] and not results[p]["unsafe"]]
        if safe_terminal:
            archive_covered += 1
            orientations = set("forward" if r["terminal_forward"] else "rollback" for _, r in safe_terminal)
            if len(orientations) >= 2:
                archive_dual_orientation += 1
            nd = pareto_front(safe_terminal)
            if len(nd) >= 2:
                archive_pareto_multi += 1
            for policy, r in nd:
                pareto_branch_counts[policy] += 1
                orientation = "forward" if r["terminal_forward"] else "rollback"
                niche = (orientation, min(r["actions"], 4), min(r["new_effects"], 3),
                         min(r["comp_issued"], 3), min(r["comp_depth"], 2),
                         min(r["residual_exposure"], 3))
                archive_niches[str(niche)] += 1
            for orientation in orientations:
                candidates = [(p, r) for p, r in safe_terminal if ("forward" if r["terminal_forward"] else "rollback") == orientation]
                best = min(candidates, key=lambda pr: (pr[1]["actions"], pr[1]["new_effects"], pr[1]["comp_issued"], pr[1]["residual_exposure"], pr[0]))
                qd_orientation_branch_counts[best[0]] += 1

        if profile_name == "revocable_superseded":
            slices["revocable_superseded"]["scenarios"] += 1
            for p, r in results.items():
                slices["revocable_superseded"][p + "_unsafe_scenarios"] += int(r["unsafe"] > 0)
                slices["revocable_superseded"][p + "_stale_events"] += r["stale_auth"] + r["stale_comp"]

        if profile_name == "no_status_pruned_takeover" and "ambig_applied" in case_names:
            slices["ambiguous_pruned_takeover"]["scenarios"] += 1
            for p, r in results.items():
                slices["ambiguous_pruned_takeover"][p + "_duplicate_effect_scenarios"] += int(r["dup_effect"] > 0)
                slices["ambiguous_pruned_takeover"][p + "_unsafe_scenarios"] += int(r["unsafe"] > 0)

        has_compensatable_applied = any(c["actual"] and ct["compensatable"] for c, ct in zip(cases, contracts))
        if pattern in ("first_late_failed", "first_reversed") and has_compensatable_applied:
            slices["late_comp_failure_or_reversal"]["scenarios"] += 1
            for p, r in results.items():
                slices["late_comp_failure_or_reversal"][p + "_false_terminal_scenarios"] += int(r["false_terminal_scenario"] > 0)
                slices["late_comp_failure_or_reversal"][p + "_terminal_scenarios"] += int(r["terminal"] > 0)

        if pattern in ("first_late_failed_then_success", "first_reversed_then_success") and has_compensatable_applied:
            r = results["greedy_rollback"]
            slices["linked_second_compensation_identity"]["scenarios"] += 1
            slices["linked_second_compensation_identity"]["rollback_terminal_scenarios"] += int(r["terminal"] > 0)
            slices["linked_second_compensation_identity"]["rollback_depth2_terminal_scenarios"] += int(r["terminal"] and r["comp_depth"] >= 2)
            slices["linked_second_compensation_identity"]["rollback_unsafe_scenarios"] += int(r["unsafe"] > 0)

    summary = {}
    for p, c in totals.items():
        summary[p] = dict(c)
        summary[p]["terminal_coverage"] = c["terminal_scenarios"] / scenarios
        summary[p]["unsafe_rate"] = c["unsafe_scenarios"] / scenarios
        summary[p]["false_terminal_rate"] = c["false_terminal_scenarios"] / scenarios

    output = {
        "model": {
            "equal_weight_synthetic": True,
            "empirical_rate_claim": False,
            "scenario_count": scenarios,
            "effect_counts": [2, 3],
            "effect_case_count": len(EFFECT_CASES),
            "effect_contract_count": len(EFFECT_CONTRACTS),
            "profile_count": len(PROFILES),
            "compensation_pattern_count": len(COMP_PATTERNS),
            "capability_states": ["PREPARED", "MINTED", "CONSUMED", "EXPIRED"],
            "effect_observation_states": ["NOT_SEEN", "AMBIGUOUS", "APPLIED", "FAILED"],
            "note": "REVOKED_WHERE_SUPPORTED is represented by the revocable_superseded profile's invalid authorization boundary; no provider-generic revoke primitive is assumed."
        },
        "policies": summary,
        "safe_archive": {
            "covered_scenarios": archive_covered,
            "coverage": archive_covered / scenarios,
            "dual_orientation_scenarios": archive_dual_orientation,
            "dual_orientation_rate": archive_dual_orientation / scenarios,
            "multi_nondominated_branch_scenarios": archive_pareto_multi,
            "multi_nondominated_branch_rate": archive_pareto_multi / scenarios,
            "behavior_niche_count": len(archive_niches),
            "pareto_branch_counts": dict(pareto_branch_counts),
            "qd_orientation_branch_counts": dict(qd_orientation_branch_counts),
            "definition": "Per scenario, keep all safe terminal branches on the Pareto front of actions/new-original-effects/compensations/residual exposure, plus one best safe branch per forward-vs-rollback behavior orientation."
        },
        "slices": {k: dict(v) for k, v in slices.items()},
        "scope_limits": [
            "Finite mechanism lattice only; counts are not production frequencies.",
            "Effect application truth is synthetic hidden state used to score policy safety; policies only use modeled observations/status capability.",
            "A successful compensation is an objective-defined rollback disposition, not byte-for-byte restoration; irreversible_comp retains residual exposure.",
            "Second compensation identities are modeled only for selected late-failure/reversal patterns and settle successfully in that branch.",
            "No generic provider capability revocation or sink fencing primitive is assumed beyond the explicit profile contracts."
        ]
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
