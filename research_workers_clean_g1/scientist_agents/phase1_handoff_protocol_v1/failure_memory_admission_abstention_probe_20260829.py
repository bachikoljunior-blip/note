#!/usr/bin/env python3
"""Additive semantic probe for receiver-memory admission abstention.

This does not replace failure_memory_validator_v2.py. It tests a distinct runtime
invariant: a record rejected/held by receiver applicability logic must not be
forced into the runtime-selected memory set by a non-empty fallback policy.
"""


def validate_memory_admission(candidates, runtime_selected_ids, require_nonempty=False):
    decision = {c["record_id"]: c["receiver_decision"] for c in candidates}
    codes = []
    for record_id in runtime_selected_ids:
        if decision.get(record_id) != "adopt":
            if "FORCED_MEMORY_AFTER_ABSTENTION" not in codes:
                codes.append("FORCED_MEMORY_AFTER_ABSTENTION")
    if require_nonempty and not any(v == "adopt" for v in decision.values()) and runtime_selected_ids:
        if "FORCED_MEMORY_AFTER_ABSTENTION" not in codes:
            codes.append("FORCED_MEMORY_AFTER_ABSTENTION")
    return codes


def main():
    cases = [
        ("all_reject_empty_pass", [{"record_id": "m1", "receiver_decision": "reject"}], [], True, []),
        ("all_reject_forced_start_fail", [{"record_id": "m1", "receiver_decision": "reject"}], ["m1"], True, ["FORCED_MEMORY_AFTER_ABSTENTION"]),
        ("hold_forced_fail", [{"record_id": "m1", "receiver_decision": "hold"}], ["m1"], True, ["FORCED_MEMORY_AFTER_ABSTENTION"]),
        ("adopt_selected_pass", [{"record_id": "m1", "receiver_decision": "adopt"}], ["m1"], True, []),
        ("mixed_select_rejected_fail", [{"record_id": "m1", "receiver_decision": "adopt"}, {"record_id": "m2", "receiver_decision": "reject"}], ["m2"], False, ["FORCED_MEMORY_AFTER_ABSTENTION"]),
    ]
    passed = 0
    for name, candidates, selected, require_nonempty, expected in cases:
        codes = validate_memory_admission(candidates, selected, require_nonempty)
        ok = codes == expected
        print(f"{'PASS' if ok else 'FAIL'} {name}: {codes}")
        passed += int(ok)
    print(f"{passed}/{len(cases)} tests passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
