#!/usr/bin/env python3
"""Finite synthetic model: retirement-barrier bypass/rollback across publication paths.

Scope: one retired generation g1, current generation g3/g4, one publication at a time,
four publication paths, one sink authority domain. Equal-weight lattice counts are
mechanism counts, not production probabilities.
"""
from itertools import product
from collections import Counter
import json

PATHS = ["queue", "direct_api", "retry_worker", "restore_archive"]
REPAIR_STATES = ["FINAL", "PENDING"]
CURRENT_GENS = [3, 4]
MESSAGE_KINDS = ["old_g1", "current"]
COORDINATOR_CHECK = [False, True]
FLOOR_STORAGE = ["current", "rolled_back", "missing"]
CERT_STATE = ["current_valid", "old_valid", "invalid", "none"]
AUTHORITY_PROTECTED = [False, True]

POLICIES = [
    "coordinator_only",
    "sink_floor_compact",
    "signed_cert_only_compact",
    "cert_plus_floor_compact",
    "safe_cert_floor_or_tombstone",
    "permanent_tombstone",
]

def should_accept(repair_state, message_kind):
    if message_kind == "current":
        return True
    return repair_state == "PENDING"

def effective_floor(current_gen, floor_storage, path, authority_protected):
    if floor_storage == "current":
        floor = current_gen
    elif floor_storage == "rolled_back":
        floor = 1
    else:
        floor = 0
    # A restore path can roll an otherwise current floor back to g1 unless the
    # authority root is outside the restore/rollback domain.
    if path == "restore_archive" and not authority_protected:
        floor = min(floor, 1)
    return floor

def evaluate(policy, repair_state, current_gen, message_kind, path,
             coordinator_check, floor_storage, cert_state, authority_protected):
    retired = repair_state == "FINAL"
    msg_gen = 1 if message_kind == "old_g1" else current_gen
    expected = should_accept(repair_state, message_kind)

    if policy == "permanent_tombstone":
        compacted = False
        retained = 1.0
    elif policy == "safe_cert_floor_or_tombstone":
        # Fail closed: compact only when the monotonic sink retirement root is
        # protected from rollback/restore. Otherwise retain the g1 tombstone.
        compacted = retired and authority_protected
        retained = 0.25 if compacted else 1.0
    else:
        compacted = retired
        retained = 0.25 if compacted else 1.0

    # Retirement mechanisms must not block g1 before repair finality.
    if not retired:
        accepted = True
    elif message_kind == "current":
        accepted = True
    elif policy == "coordinator_only":
        accepted = not coordinator_check
    elif policy == "sink_floor_compact":
        accepted = msg_gen >= effective_floor(
            current_gen, floor_storage, path, authority_protected
        )
    elif policy == "signed_cert_only_compact":
        # Signature authenticates an old certificate but does not make it fresh.
        accepted = cert_state == "old_valid"
    elif policy == "cert_plus_floor_compact":
        accepted = (
            cert_state == "old_valid"
            and effective_floor(current_gen, floor_storage, path, authority_protected) <= 1
        )
    elif policy == "safe_cert_floor_or_tombstone":
        # Either protected floor rejects g1, or tombstone remains and rejects g1.
        accepted = False
    elif policy == "permanent_tombstone":
        accepted = False
    else:
        raise ValueError(policy)

    unsafe_old = message_kind == "old_g1" and retired and accepted
    lost_legitimate = expected and not accepted
    bypassed = unsafe_old and (
        not coordinator_check or path in ("direct_api", "restore_archive")
    )
    rollback_aba = unsafe_old and (
        floor_storage in ("rolled_back", "missing")
        or (path == "restore_archive" and not authority_protected)
        or cert_state == "old_valid"
    )
    return {
        "accepted": accepted,
        "unsafe_old": unsafe_old,
        "lost_legitimate": lost_legitimate,
        "compacted": compacted,
        "retained": retained,
        "bypassed_old_generation": bypassed,
        "rollback_aba": rollback_aba,
    }

SCENARIOS = list(product(
    REPAIR_STATES, CURRENT_GENS, MESSAGE_KINDS, PATHS, COORDINATOR_CHECK,
    FLOOR_STORAGE, CERT_STATE, AUTHORITY_PROTECTED
))

aggregate = {}
for policy in POLICIES:
    c = Counter()
    retained = 0.0
    for s in SCENARIOS:
        r = evaluate(policy, *s)
        c["scenarios"] += 1
        c["unsafe_old"] += int(r["unsafe_old"])
        c["lost_legitimate"] += int(r["lost_legitimate"])
        c["compacted"] += int(r["compacted"])
        c["safe_compaction"] += int(
            r["compacted"] and not r["unsafe_old"] and not r["lost_legitimate"]
        )
        c["bypassed_old_generation"] += int(r["bypassed_old_generation"])
        c["rollback_aba"] += int(r["rollback_aba"])
        retained += r["retained"]
    c["retained_state_units"] = retained
    aggregate[policy] = dict(c)

def count_slice(predicate, policy, field):
    denom = 0
    numer = 0
    for s in SCENARIOS:
        if predicate(*s):
            denom += 1
            numer += int(evaluate(policy, *s)[field])
    return {"numerator": numer, "denominator": denom}

targeted = {
    "coordinator_bypass_final_old": count_slice(
        lambda repair,current,msg,path,coord,floor,cert,prot:
            repair == "FINAL" and msg == "old_g1" and not coord,
        "coordinator_only", "unsafe_old"
    ),
    "signed_old_cert_without_floor_memory": count_slice(
        lambda repair,current,msg,path,coord,floor,cert,prot:
            repair == "FINAL" and msg == "old_g1" and cert == "old_valid",
        "signed_cert_only_compact", "unsafe_old"
    ),
    "cert_plus_floor_susceptible": count_slice(
        lambda repair,current,msg,path,coord,floor,cert,prot:
            repair == "FINAL" and msg == "old_g1" and cert == "old_valid"
            and effective_floor(current, floor, path, prot) <= 1,
        "cert_plus_floor_compact", "unsafe_old"
    ),
    "safe_policy_protected_old_replay": count_slice(
        lambda repair,current,msg,path,coord,floor,cert,prot:
            repair == "FINAL" and msg == "old_g1" and prot,
        "safe_cert_floor_or_tombstone", "unsafe_old"
    ),
}
# How many FINAL worlds fail-closed to tombstone because no protected authority root.
strong_noncompact_unprotected = sum(
    1 for s in SCENARIOS
    if s[0] == "FINAL" and not s[-1] and not evaluate("safe_cert_floor_or_tombstone", *s)["compacted"]
)

out = {
    "schema_version": 1,
    "model": "retirement_barrier_bypass_rollback",
    "scenario_count": len(SCENARIOS),
    "equal_weight_synthetic": True,
    "aggregate": aggregate,
    "targeted_slices": targeted,
    "strong_policy_noncompact_unprotected_final_worlds": strong_noncompact_unprotected,
    "retained_state_unit_definition": {
        "detailed_or_permanent_incarnation_witness": 1.0,
        "compacted_monotonic_floor_plus_certificate": 0.25,
        "note": "Synthetic comparison unit only; not a byte estimate."
    },
    "scope": [
        "one historical generation g1 and current generation g3/g4",
        "one publication at a time across queue/direct_api/retry_worker/restore_archive",
        "one sink authority root, boolean protected-from-restore property",
        "no Byzantine signer, no partial-value compensation, no multi-sink quorum"
    ]
}
print(json.dumps(out, indent=2, sort_keys=True))
