from itertools import product
from collections import Counter, defaultdict
import json

TASK_KINDS = ["structural_local", "deterministic_local", "external_fact", "all_roles_complete"]
DIMS = [
    "semantics_valid", "tuple_current", "evidence_complete", "duplicate_replay",
    "role_added_after", "all_roles_complete_now", "response_loss", "hash_matches", "schema_valid"
]
STRATEGIES = [
    "plain_content_hash", "schema_hash_tuple", "deterministic_local_predicate_proof",
    "self_contained_proof_contract", "cross_role_all_certificates_baseline"
]


def scenarios():
    for task_kind in TASK_KINDS:
        for vals in product([False, True], repeat=len(DIMS)):
            s = dict(zip(DIMS, vals))
            s["task_kind"] = task_kind
            yield s


def valid_useful_outcome(s):
    if not (s["hash_matches"] and s["schema_valid"] and s["semantics_valid"] and s["tuple_current"]):
        return False
    if s["task_kind"] in ("deterministic_local", "external_fact") and not s["evidence_complete"]:
        return False
    if s["task_kind"] == "all_roles_complete":
        return s["all_roles_complete_now"] and not s["role_added_after"]
    return True


def evaluate(name, s):
    kind = s["task_kind"]
    terminal = dedupe = reconcile = forbidden = unsupported = False

    if name == "plain_content_hash":
        terminal = s["hash_matches"]
    elif name == "schema_hash_tuple":
        terminal = s["hash_matches"] and s["schema_valid"] and s["tuple_current"]
    elif name == "deterministic_local_predicate_proof":
        if kind == "structural_local":
            terminal = s["hash_matches"] and s["schema_valid"] and s["tuple_current"] and s["semantics_valid"]
        elif kind == "deterministic_local":
            terminal = (s["hash_matches"] and s["schema_valid"] and s["tuple_current"]
                        and s["semantics_valid"] and s["evidence_complete"])
        else:
            unsupported = True
    elif name == "self_contained_proof_contract":
        dedupe = reconcile = True
        if kind == "structural_local":
            terminal = s["hash_matches"] and s["schema_valid"] and s["tuple_current"] and s["semantics_valid"]
        elif kind == "deterministic_local":
            terminal = (s["hash_matches"] and s["schema_valid"] and s["tuple_current"]
                        and s["semantics_valid"] and s["evidence_complete"])
        else:
            unsupported = True
    elif name == "cross_role_all_certificates_baseline":
        dedupe = reconcile = True
        if kind == "structural_local":
            terminal = s["hash_matches"] and s["schema_valid"] and s["tuple_current"] and s["semantics_valid"]
        elif kind == "deterministic_local":
            terminal = (s["hash_matches"] and s["schema_valid"] and s["tuple_current"]
                        and s["semantics_valid"] and s["evidence_complete"])
        elif kind == "all_roles_complete":
            forbidden = True
            terminal = (s["hash_matches"] and s["schema_valid"] and s["tuple_current"]
                        and s["semantics_valid"] and s["all_roles_complete_now"]
                        and not s["role_added_after"])
        else:
            unsupported = True
    else:
        raise ValueError(name)

    valid = valid_useful_outcome(s)
    false_terminal = terminal and not valid
    duplicate_integration = terminal and (s["duplicate_replay"] or s["response_loss"]) and not (dedupe and reconcile)
    unsafe_effect = false_terminal or duplicate_integration
    return {
        "terminal": terminal,
        "valid": valid,
        "false_terminal": false_terminal,
        "duplicate_integration": duplicate_integration,
        "unsafe_effect": unsafe_effect,
        "false_exclusion": valid and not terminal,
        "response_unreconciled": s["response_loss"] and terminal and not reconcile,
        "forbidden": forbidden,
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
                by_kind[s["task_kind"]][k] += int(v)
            total["evaluations"] += 1
            by_kind[s["task_kind"]]["evaluations"] += 1
        out["strategies"][name] = {"total": dict(total), "by_task_kind": {k: dict(v) for k, v in by_kind.items()}}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
