from itertools import product
from collections import Counter, defaultdict
import json

POLICY_KINDS = ["unchanged", "compatible_minor", "stricter_new_evidence", "scope_broadens_external"]
DIMS = [
    "current_policy_accepts", "evidence_complete_for_current", "allow_old_version", "allow_old_hash",
    "latest_lookup_authoritative", "same_version_bytes_unchanged", "old_artifact_replay", "response_loss",
    "artifact_hash_matches", "schema_valid"
]
STRATEGIES = [
    "latest_unpinned_policy", "exact_version_allowlist", "exact_hash_allowlist",
    "monotonic_minor_range_negative", "current_hash_bound_reverify",
    "hybrid_hash_allowlist_or_current_reverify"
]


def scenarios():
    for kind in POLICY_KINDS:
        for vals in product([False, True], repeat=len(DIMS)):
            s = dict(zip(DIMS, vals))
            s["policy_change_kind"] = kind
            yield s


def current_reverify_authorized(s):
    return (s["policy_change_kind"] != "scope_broadens_external"
            and s["latest_lookup_authoritative"]
            and s["evidence_complete_for_current"]
            and s["current_policy_accepts"])


def current_authority_valid(s):
    if not (s["artifact_hash_matches"] and s["schema_valid"]):
        return False
    exact_hash_grandfather = s["allow_old_hash"]
    exact_version_grandfather = s["allow_old_version"] and s["same_version_bytes_unchanged"]
    return exact_hash_grandfather or exact_version_grandfather or current_reverify_authorized(s)


def evaluate(name, s):
    kind = s["policy_change_kind"]
    terminal = exact_policy_identity = reconcile = unsupported = False

    if name == "latest_unpinned_policy":
        if kind == "scope_broadens_external":
            unsupported = True
        else:
            terminal = (s["artifact_hash_matches"] and s["schema_valid"] and s["evidence_complete_for_current"]
                        and (s["current_policy_accepts"] if s["latest_lookup_authoritative"] else True))
    elif name == "exact_version_allowlist":
        terminal = s["artifact_hash_matches"] and s["schema_valid"] and s["allow_old_version"]
        exact_policy_identity = s["same_version_bytes_unchanged"]
        reconcile = True
    elif name == "exact_hash_allowlist":
        terminal = s["artifact_hash_matches"] and s["schema_valid"] and s["allow_old_hash"]
        exact_policy_identity = True
        reconcile = True
    elif name == "monotonic_minor_range_negative":
        if kind == "scope_broadens_external":
            unsupported = True
        else:
            terminal = s["artifact_hash_matches"] and s["schema_valid"] and s["latest_lookup_authoritative"]
        exact_policy_identity = kind == "unchanged"
        reconcile = True
    elif name == "current_hash_bound_reverify":
        if kind == "scope_broadens_external":
            unsupported = True
        else:
            terminal = (s["artifact_hash_matches"] and s["schema_valid"] and s["latest_lookup_authoritative"]
                        and s["evidence_complete_for_current"] and s["current_policy_accepts"])
        exact_policy_identity = True
        reconcile = True
    elif name == "hybrid_hash_allowlist_or_current_reverify":
        terminal = (s["artifact_hash_matches"] and s["schema_valid"]
                    and (s["allow_old_hash"] or current_reverify_authorized(s)))
        exact_policy_identity = True
        reconcile = True
    else:
        raise ValueError(name)

    valid = current_authority_valid(s)
    false_terminal = terminal and not valid
    duplicate = terminal and (s["old_artifact_replay"] or s["response_loss"]) and not reconcile
    stale_policy_replay = (terminal and s["old_artifact_replay"]
                           and kind != "unchanged" and not exact_policy_identity)
    return {
        "terminal": terminal,
        "valid": valid,
        "false_terminal": false_terminal,
        "duplicate_integration": duplicate,
        "stale_policy_replay": stale_policy_replay,
        "unsafe_effect": false_terminal or duplicate or stale_policy_replay,
        "false_exclusion": valid and not terminal,
        "unsupported": unsupported,
    }


def main():
    rows = list(scenarios())
    out = {"scenario_count": len(rows), "strategy_evaluations": len(rows) * len(STRATEGIES), "strategies": {}}
    for name in STRATEGIES:
        total = Counter()
        by_kind = defaultdict(Counter)
        for s in rows:
            r = evaluate(name, s)
            for k, v in r.items():
                total[k] += int(v)
                by_kind[s["policy_change_kind"]][k] += int(v)
            total["evaluations"] += 1
            by_kind[s["policy_change_kind"]]["evaluations"] += 1
        out["strategies"][name] = {"total": dict(total), "by_policy_change_kind": {k: dict(v) for k, v in by_kind.items()}}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
