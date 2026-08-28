#!/usr/bin/env python3
"""Finite synthetic model: late publication-path/sink admission after retirement.

All scenarios are post-repair-finality. The retired generation is g1 and current
minimum generation is g3. Equal-weight counts are mechanism counts, not probabilities.
"""
from itertools import product
from collections import Counter
import json

PATHS = ["queue", "direct_api", "restore_archive"]
NEW_PATH = [False, True]
SINK_KIND = ["existing", "new"]
CERT_STATE = ["current_valid", "old_valid", "invalid", "none"]
REGISTRY_STATE = ["current", "stale"]
LOCAL_FLOOR = ["current", "missing"]
GLOBAL_WATERMARK = [False, True]
MESSAGE_KIND = ["old_g1", "current"]
BYPASS_ENROLLMENT = [False, True]

POLICIES = [
    "registry_admission_only",
    "cert_bootstrap_no_pin",
    "inherited_sink_floor_only",
    "enrollment_cert_pinned_floor",
    "shared_publish_watermark",
    "permanent_tombstone",
]

SCENARIOS = list(product(
    PATHS, NEW_PATH, SINK_KIND, CERT_STATE, REGISTRY_STATE, LOCAL_FLOOR,
    GLOBAL_WATERMARK, MESSAGE_KIND, BYPASS_ENROLLMENT
))

def evaluate(policy, path, new_path, sink_kind, cert_state, registry_state,
             local_floor, global_watermark, message_kind, bypass_enrollment):
    old = message_kind == "old_g1"
    current = message_kind == "current"
    msg_generation = 1 if old else 3
    enrolled = True
    publish_authority_reads = 0
    retained = 0.25  # compact floor/certificate root, synthetic state unit

    if policy == "registry_admission_only":
        # Admission-time registry check configures the new path, but bypass/stale
        # admission creates a permissive path with no sink-local remembered floor.
        if new_path and not bypass_enrollment and registry_state == "current":
            floor = 3
        else:
            floor = 1
        accepted = msg_generation >= floor

    elif policy == "cert_bootstrap_no_pin":
        # A signature authenticates the presented certificate, but without a
        # remembered version/floor an older still-valid cert can bootstrap g1.
        if cert_state == "current_valid":
            floor = 3
        elif cert_state == "old_valid":
            floor = 1
        else:
            enrolled = False
            floor = 3
        accepted = enrolled and msg_generation >= floor

    elif policy == "inherited_sink_floor_only":
        # Existing sink state is safe only when inherited. A new/missing sink
        # instance comes up permissive if there is no explicit enrollment proof.
        if sink_kind == "existing" and local_floor == "current":
            floor = 3
        else:
            floor = 1
        accepted = msg_generation >= floor

    elif policy == "enrollment_cert_pinned_floor":
        # Existing current floor continues without a remote lookup. New/missing
        # sink state may serve only after a current certificate is checked against
        # a durable global watermark and the current floor is pinned locally.
        if sink_kind == "existing" and local_floor == "current":
            floor = 3
        elif global_watermark and cert_state == "current_valid" and not bypass_enrollment:
            floor = 3
        else:
            enrolled = False
            floor = 3
        accepted = enrolled and msg_generation >= floor

    elif policy == "shared_publish_watermark":
        # Every publication consults the protected watermark. If unavailable or
        # bypassed, fail closed rather than serve from a blank/rolled-back sink.
        publish_authority_reads = 1
        if global_watermark and not bypass_enrollment:
            floor = 3
            accepted = msg_generation >= floor
        else:
            accepted = False

    elif policy == "permanent_tombstone":
        retained = 1.0
        accepted = current

    else:
        raise ValueError(policy)

    return {
        "accepted": accepted,
        "unsafe_old": old and accepted,
        "blocked_current": current and not accepted,
        "unsafe_new_path_or_sink": (new_path or sink_kind == "new") and old and accepted,
        "publish_authority_reads": publish_authority_reads,
        "retained": retained,
    }

aggregate = {}
for policy in POLICIES:
    c = Counter()
    retained = 0.0
    reads = 0
    for s in SCENARIOS:
        r = evaluate(policy, *s)
        c["scenarios"] += 1
        c["unsafe_old"] += int(r["unsafe_old"])
        c["blocked_current"] += int(r["blocked_current"])
        c["unsafe_new_path_or_sink"] += int(r["unsafe_new_path_or_sink"])
        retained += r["retained"]
        reads += r["publish_authority_reads"]
    c["retained_state_units"] = retained
    c["publish_authority_reads"] = reads
    aggregate[policy] = dict(c)

def targeted(predicate, policy, field):
    denom = 0
    numer = 0
    for s in SCENARIOS:
        if predicate(*s):
            denom += 1
            numer += int(evaluate(policy, *s)[field])
    return {"numerator": numer, "denominator": denom}

slices = {
    "signed_old_cert_bootstrap": targeted(
        lambda path,newp,sink,cert,reg,local,gwm,msg,bypass:
            msg == "old_g1" and cert == "old_valid",
        "cert_bootstrap_no_pin", "unsafe_old"
    ),
    "new_sink_without_inherited_floor": targeted(
        lambda path,newp,sink,cert,reg,local,gwm,msg,bypass:
            msg == "old_g1" and sink == "new",
        "inherited_sink_floor_only", "unsafe_old"
    ),
    "strong_enrollment_old_replay": targeted(
        lambda path,newp,sink,cert,reg,local,gwm,msg,bypass:
            msg == "old_g1",
        "enrollment_cert_pinned_floor", "unsafe_old"
    ),
    "strong_enrollment_current_liveness": targeted(
        lambda path,newp,sink,cert,reg,local,gwm,msg,bypass:
            msg == "current",
        "enrollment_cert_pinned_floor", "blocked_current"
    ),
    "shared_watermark_current_liveness": targeted(
        lambda path,newp,sink,cert,reg,local,gwm,msg,bypass:
            msg == "current",
        "shared_publish_watermark", "blocked_current"
    ),
}

out = {
    "schema_version": 1,
    "model": "late_path_sink_admission_after_retirement",
    "scenario_count": len(SCENARIOS),
    "equal_weight_synthetic": True,
    "aggregate": aggregate,
    "targeted_slices": slices,
    "retained_state_unit_definition": {
        "permanent_per_incarnation_tombstone": 1.0,
        "compacted_watermark_certificate_root": 0.25,
        "note": "Synthetic comparison unit only; not a byte estimate."
    },
    "scope": [
        "post-repair-finality only",
        "one retired generation g1 and one current minimum generation g3",
        "one publication at a time",
        "new/existing path and new/existing sink instance",
        "no Byzantine signer, quorum, network partition, or multi-region consensus"
    ]
}
print(json.dumps(out, indent=2, sort_keys=True))
