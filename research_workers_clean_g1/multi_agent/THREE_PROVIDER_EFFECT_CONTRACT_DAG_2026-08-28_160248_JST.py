from __future__ import annotations
from itertools import product
from collections import Counter
import json

PROVIDERS = {
    "stripe_v2": {
        "documented_scope": ["same_idempotency_key", "same_api", "same_account_or_sandbox"],
        "window_kind": "fixed",
        "window_days": 30,
        "notes": "Provider docs define idempotent replay by same key + same API + same account/sandbox + within 30 days.",
    },
    "adyen": {
        "documented_scope": ["same_idempotency_key", "same_company_account", "same_region"],
        "window_kind": "minimum_guarantee",
        "window_days": 7,
        "notes": "Keys are unique at company-account level, valid for a minimum of 7 days, and are not deduplicated across regions.",
    },
    "paypal": {
        "documented_scope": ["same_paypal_request_id", "same_api_call_type", "api_supports_header"],
        "window_kind": "api_specific",
        "window_days": 45,
        "notes": "Support/retention are API-specific; current REST request guidance says IDs can be retained up to 45 days. Same ID must be unique per request and API call type.",
    },
}

SCENARIOS = [
    "valid_same_intent",
    "ambiguous_first_attempt",
    "retention_exceeded",
    "key_reused_new_intent",
    "payload_drift",
    "account_or_scope_migration",
    "api_region_or_calltype_migration",
    "first_use_time_unknown",
    "provider_support_or_retention_unknown",
]


def contract_status(provider: str, scenario: str) -> dict:
    """Conservative controller certification, not a claim about undocumented provider behavior."""
    p = PROVIDERS[provider]
    if scenario == "valid_same_intent":
        return {"status": "CERTIFIED", "retry_admissible": True, "terminal_without_live_proof": False}
    if scenario == "ambiguous_first_attempt":
        return {"status": "CERTIFIED_AMBIGUOUS_EFFECT", "retry_admissible": True, "terminal_without_live_proof": False}
    if scenario in ("key_reused_new_intent", "payload_drift"):
        return {"status": "SAME_INTENT_MISMATCH", "retry_admissible": False, "terminal_without_live_proof": False}
    if scenario == "first_use_time_unknown":
        return {"status": "INSUFFICIENT_TIME_EVIDENCE", "retry_admissible": False, "terminal_without_live_proof": False}
    if scenario == "provider_support_or_retention_unknown":
        return {"status": "INSUFFICIENT_PROVIDER_EVIDENCE", "retry_admissible": False, "terminal_without_live_proof": False}
    if scenario == "retention_exceeded":
        if p["window_kind"] == "fixed":
            status = "OUTSIDE_DOCUMENTED_REPLAY_WINDOW"
        elif p["window_kind"] == "minimum_guarantee":
            status = "BEYOND_MINIMUM_GUARANTEE_UNKNOWN"
        else:
            status = "OUTSIDE_DOCUMENTED_API_RETENTION"
        return {"status": status, "retry_admissible": False, "terminal_without_live_proof": False}
    if scenario == "account_or_scope_migration":
        if provider == "stripe_v2":
            status = "DOCUMENTED_SCOPE_MISMATCH"
        elif provider == "adyen":
            status = "DOCUMENTED_COMPANY_SCOPE_MISMATCH"
        else:
            status = "MERCHANT_CONTEXT_NOT_PROVEN_SAME"
        return {"status": status, "retry_admissible": False, "terminal_without_live_proof": False}
    if scenario == "api_region_or_calltype_migration":
        status = {
            "stripe_v2": "DOCUMENTED_API_SCOPE_MISMATCH",
            "adyen": "DOCUMENTED_REGION_DEDUPE_MISMATCH",
            "paypal": "DOCUMENTED_CALL_TYPE_SCOPE_MISMATCH",
        }[provider]
        return {"status": status, "retry_admissible": False, "terminal_without_live_proof": False}
    raise ValueError(scenario)


def contract_matrix():
    return {p: {s: contract_status(p, s) for s in SCENARIOS} for p in PROVIDERS}

# Abstract exact lattice after provider-specific contract certification.
# node state = (live effect evidence, full contract certified, historical success record, compensation available)
LIVE = ("P", "A", "U")  # proven-present, proven-absent, unknown
BOOL = (False, True)
NODE_STATES = list(product(LIVE, BOOL, BOOL, BOOL))
N = 3


def hidden_counts(lives):
    opts = []
    for live in lives:
        opts.append((1,) if live == "P" else (0,) if live == "A" else (0, 1))
    return product(*opts)


def comp_outcomes(state3):
    opts = []
    for _live, _cert, _record, comp in state3:
        opts.append((True, False) if comp else (None,))
    return product(*opts)


def forward_proof(state3, counts):
    final = list(counts)
    dispatches = 0
    for i, (live, cert, _record, _comp) in enumerate(state3):
        if live == "P":
            continue
        if not cert:
            return False, False, dispatches, tuple(final)
        dispatches += 1
        # Certified same-intent retry: no duplicate; post-action read proves intended effect present.
        final[i] = 1
    terminal = all(x == 1 for x in final)
    return terminal, False, dispatches, tuple(final)


def forward_key_boolean(state3, counts):
    final = list(counts)
    dispatches = 0
    # Stress policy: treats mere key existence as timeless/scope-free proof and trusts dispatch completion.
    for i, (live, cert, _record, _comp) in enumerate(state3):
        if live == "P":
            continue
        dispatches += 1
        if cert:
            final[i] = 1
        else:
            final[i] += 1  # hidden prior success can become a duplicate when the real contract does not apply
    terminal = True
    unsafe = not all(x == 1 for x in final)
    return terminal, unsafe, dispatches, tuple(final)


def forward_trust_record(state3, counts):
    final = list(counts)
    dispatches = 0
    # Stress policy: substitutes historical success for current physical-effect proof.
    for i, (live, cert, record, _comp) in enumerate(state3):
        if live == "P":
            continue
        if live == "U" and record:
            continue
        if not cert:
            return False, False, dispatches, tuple(final)
        dispatches += 1
        final[i] = 1
    terminal = True
    unsafe = not all(x == 1 for x in final)
    return terminal, unsafe, dispatches, tuple(final)


def rollback_proof_reverse(state3, counts, comp_success):
    # Unknown current state is not destructive-action authority.
    if any(s[0] == "U" for s in state3):
        return False, False, 0, False, tuple(counts)
    final = list(counts)
    actions = 0
    dep_violation = False
    for i in reversed(range(N)):
        live, _cert, _record, comp = state3[i]
        if live != "P":
            continue
        if not comp:
            return False, False, actions, dep_violation, tuple(final)
        if any(final[j] > 0 for j in range(i + 1, N)):
            dep_violation = True
        actions += 1
        if comp_success[i]:
            final[i] = 0
        else:
            # Verified compensation failure: stop pending; do not compensate predecessors.
            return False, False, actions, dep_violation, tuple(final)
    terminal = all(x == 0 for x in final) and not dep_violation
    return terminal, False, actions, dep_violation, tuple(final)


def rollback_blind_reverse(state3, counts, comp_success):
    final = list(counts)
    actions = 0
    dep_violation = False
    suspected = [live == "P" or (live == "U" and record) for live, _cert, record, _comp in state3]
    blocked = False
    for i in reversed(range(N)):
        if not suspected[i]:
            continue
        comp = state3[i][3]
        if not comp:
            blocked = True
            break
        if any(final[j] > 0 for j in range(i + 1, N)):
            dep_violation = True
        actions += 1
        if comp_success[i]:
            final[i] = 0
        # failure is not verified; policy continues and later terminalizes on assumption
    terminal = not blocked
    unsafe = terminal and (dep_violation or not all(x == 0 for x in final))
    return terminal, unsafe, actions, dep_violation, tuple(final)


def rollback_blind_forward_order(state3, counts, comp_success):
    final = list(counts)
    actions = 0
    dep_violation = False
    suspected = [live == "P" or (live == "U" and record) for live, _cert, record, _comp in state3]
    blocked = False
    for i in range(N):
        if not suspected[i]:
            continue
        comp = state3[i][3]
        if not comp:
            blocked = True
            break
        # A -> B -> C. Removing a predecessor while a dependent descendant still exists violates the DAG invariant.
        if any(final[j] > 0 for j in range(i + 1, N)):
            dep_violation = True
        actions += 1
        if comp_success[i]:
            final[i] = 0
    terminal = not blocked
    unsafe = terminal and (dep_violation or not all(x == 0 for x in final))
    return terminal, unsafe, actions, dep_violation, tuple(final)


def summarize(c):
    term = c["terminal"]
    out = {
        "worlds": c["worlds"],
        "terminal_admissions": term,
        "terminal_rate": term / c["worlds"],
        "unsafe_terminal": c["unsafe_terminal"],
        "unsafe_given_terminal": (c["unsafe_terminal"] / term) if term else None,
    }
    if "dispatches_total" in c:
        out["mean_dispatches_per_world"] = c["dispatches_total"] / c["worlds"]
    if "actions_total" in c:
        out["mean_comp_actions_per_world"] = c["actions_total"] / c["worlds"]
    if "dep_violation" in c:
        out["dependency_violation_worlds"] = c["dep_violation"]
        out["dependency_violation_rate"] = c["dep_violation"] / c["worlds"]
    return out


def run():
    forward_stats = {name: Counter() for name in ("proof_gated", "key_boolean", "trust_record")}
    forward_fns = {
        "proof_gated": forward_proof,
        "key_boolean": forward_key_boolean,
        "trust_record": forward_trust_record,
    }
    ponr = Counter()
    cert_removal_checks = 0
    cert_removal_new_terminal = 0

    for state3 in product(NODE_STATES, repeat=N):
        lives = [s[0] for s in state3]
        for counts in hidden_counts(lives):
            for name, fn in forward_fns.items():
                terminal, unsafe, dispatches, _final = fn(state3, counts)
                st = forward_stats[name]
                st["worlds"] += 1
                st["terminal"] += int(terminal)
                st["unsafe_terminal"] += int(unsafe)
                st["dispatches_total"] += dispatches

            has_ponr = any(counts[i] > 0 and not state3[i][3] for i in range(N))
            if has_ponr:
                ponr["worlds"] += 1
                if forward_proof(state3, counts)[0]:
                    ponr["safe_forward_available"] += 1

            # Evidence monotonicity: remove one certified contract bit; weaker contract evidence must not create a new proof-gated terminal.
            base_terminal = forward_proof(state3, counts)[0]
            for i in range(N):
                if state3[i][1]:
                    weakened = list(state3)
                    live, _cert, record, comp = weakened[i]
                    weakened[i] = (live, False, record, comp)
                    weak_terminal = forward_proof(tuple(weakened), counts)[0]
                    cert_removal_checks += 1
                    if weak_terminal and not base_terminal:
                        cert_removal_new_terminal += 1

    rollback_stats = {name: Counter() for name in ("proof_reverse", "blind_reverse", "blind_forward_order")}
    rollback_fns = {
        "proof_reverse": rollback_proof_reverse,
        "blind_reverse": rollback_blind_reverse,
        "blind_forward_order": rollback_blind_forward_order,
    }
    adaptive = Counter()

    for state3 in product(NODE_STATES, repeat=N):
        lives = [s[0] for s in state3]
        for counts in hidden_counts(lives):
            for comp_success in comp_outcomes(state3):
                for name, fn in rollback_fns.items():
                    terminal, unsafe, actions, dep, _final = fn(state3, counts, comp_success)
                    st = rollback_stats[name]
                    st["worlds"] += 1
                    st["terminal"] += int(terminal)
                    st["unsafe_terminal"] += int(unsafe)
                    st["actions_total"] += actions
                    st["dep_violation"] += int(dep)

                adaptive["worlds"] += 1
                f_terminal, _f_unsafe, f_actions, _ = forward_proof(state3, counts)
                if f_terminal:
                    adaptive["terminal"] += 1
                    adaptive["forward_terminal"] += 1
                    adaptive["actions_total"] += f_actions
                else:
                    r_terminal, _r_unsafe, r_actions, _r_dep, _ = rollback_proof_reverse(state3, counts, comp_success)
                    if r_terminal:
                        adaptive["terminal"] += 1
                        adaptive["rollback_terminal"] += 1
                        adaptive["actions_total"] += r_actions
                    else:
                        adaptive["pending"] += 1

    matrix = contract_matrix()
    retry_certified_counts = {
        provider: sum(1 for scenario, row in scenarios.items() if row["retry_admissible"])
        for provider, scenarios in matrix.items()
    }

    result = {
        "schema_version": 1,
        "mechanism": "explicit-provider-contract + three-node dependency DAG",
        "provider_contracts": PROVIDERS,
        "contract_stress_matrix": matrix,
        "contract_stress_summary": {
            "scenarios_per_provider": len(SCENARIOS),
            "retry_admissible_scenarios_per_provider": retry_certified_counts,
            "rule": "A key alone is never certification. Controller additionally requires same-intent request fingerprint and provider-documented scope/time evidence. Ambiguous effect may authorize retry but never terminalization without live post-action proof.",
        },
        "forward_lattice": {
            "observable_states_per_node": len(NODE_STATES),
            "hidden_worlds": next(iter(forward_stats.values()))["worlds"],
            "max_dispatch_budget": 3,
            "policies": {name: summarize(st) for name, st in forward_stats.items()},
            "contract_evidence_monotonicity": {
                "one_bit_certification_removals": cert_removal_checks,
                "weaker_evidence_created_new_terminal": cert_removal_new_terminal,
            },
        },
        "rollback_lattice": {
            "hidden_worlds_including_compensation_outcome": next(iter(rollback_stats.values()))["worlds"],
            "dependency": "A -> B -> C",
            "max_compensation_budget": 3,
            "policies": {name: summarize(st) for name, st in rollback_stats.items()},
        },
        "adaptive_proof_controller": {
            "worlds": adaptive["worlds"],
            "terminal_admissions": adaptive["terminal"],
            "forward_terminal": adaptive["forward_terminal"],
            "rollback_terminal": adaptive["rollback_terminal"],
            "pending_or_block": adaptive["pending"],
            "terminal_rate": adaptive["terminal"] / adaptive["worlds"],
            "unsafe_terminal": 0,
            "mean_effect_actions_per_world": adaptive["actions_total"] / adaptive["worlds"],
            "routing": "Prefer proven/certified forward completion; otherwise reverse-order proven compensation; otherwise stay nonterminal.",
        },
        "point_of_no_return": {
            "forward_lattice_worlds_with_present_noncompensable_effect": ponr["worlds"],
            "such_worlds_with_safe_proof_gated_forward_completion": ponr["safe_forward_available"],
            "fraction": ponr["safe_forward_available"] / ponr["worlds"],
            "interpretation": "In these balanced worlds clean rollback is structurally impossible, yet certified forward completion can still reach a consistent all-present vector. Compensation should not be the default solely because a failure occurred.",
        },
        "scope": [
            "Synthetic balanced lattice; proportions are not production incident probabilities.",
            "Three binary intended effects in a chain A->B->C; no money amounts, partial captures, async settlement, or duplicate-equivalent object matching.",
            "Certified retry is modeled as exact-once for the intended effect only after provider-contract + same-intent certification; this is a mechanism abstraction, not a universal provider guarantee.",
            "Compensation success/failure is balanced synthetically and only terminal rollback/forward consistency plus transient dependency ordering are evaluated.",
            "PayPal retention/support is API-specific; the 45-day value is used only as the current REST request-documentation example/upper documented retention, not as a universal contract for every PayPal API.",
            "Adyen states validity for a minimum of 7 days; beyond 7 days is treated as unknown, not asserted expired.",
        ],
        "public_sources": [
            "https://docs.stripe.com/api-v2-overview#idempotency",
            "https://docs.stripe.com/api/idempotent_requests",
            "https://docs.adyen.com/development-resources/api-idempotency/",
            "https://developer.paypal.com/reference/guidelines/idempotency/",
            "https://developer.paypal.com/api/rest/requests/",
        ],
    }
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
