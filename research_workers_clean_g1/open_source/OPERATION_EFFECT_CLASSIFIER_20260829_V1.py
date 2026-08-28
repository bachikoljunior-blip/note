#!/usr/bin/env python3
"""Provider-neutral fail-closed operation/effect evidence classifier.

The classifier returns a vector of independent evidence axes. It intentionally
refuses scalar shortcuts such as "green CI => merged" or "submission_id =>
request id".
"""
from __future__ import annotations
import json
import sys

PROVED = "PROVED"
UNKNOWN = "UNKNOWN"
BLOCKED = "BLOCKED"

AXES = (
    "INTENT_HEAD_BOUND",
    "REQUEST_OPERATION_ID_BOUND",
    "QUEUE_OR_TRAIN_ADMITTED",
    "CI_STATE_BOUND",
    "FINAL_TARGET_REF_EFFECT_EXACT",
    "GROUP_CLOSURE_EXACT",
    "POST_EFFECT_GROUP_ID_BOUND",
    "POST_EFFECT_POLICY_EXACT",
)

def _exact_ref_transition(e):
    t = e.get("final_target_ref_transition")
    return (
        isinstance(t, dict)
        and bool(t.get("ref"))
        and bool(t.get("before_sha"))
        and bool(t.get("after_sha"))
        and t.get("before_sha") != t.get("after_sha")
        and t.get("readback_exact") is True
    )

def classify(e):
    if not isinstance(e, dict):
        return {"axes": {a: UNKNOWN for a in AXES}, "warnings": ["invalid evidence"]}

    axes = {a: UNKNOWN for a in AXES}
    warnings = []

    if e.get("exact_intent_revision") is True:
        axes["INTENT_HEAD_BOUND"] = PROVED

    op = e.get("request_operation") or {}
    if (
        isinstance(op, dict)
        and op.get("id")
        and op.get("phase") in ("request", "admission")
        and op.get("intent_verified") is True
    ):
        axes["REQUEST_OPERATION_ID_BOUND"] = PROVED

    if e.get("queue_or_train_admitted") is True:
        axes["QUEUE_OR_TRAIN_ADMITTED"] = PROVED

    ci = e.get("ci_state") or {}
    if isinstance(ci, dict) and ci.get("id") and ci.get("candidate_sha") and ci.get("readback_exact") is True:
        axes["CI_STATE_BOUND"] = PROVED

    if _exact_ref_transition(e):
        axes["FINAL_TARGET_REF_EFFECT_EXACT"] = PROVED

    closure = e.get("group_closure") or {}
    if (
        isinstance(closure, dict)
        and closure.get("complete") is True
        and isinstance(closure.get("members"), list)
        and closure.get("members")
        and closure.get("exact_readback") is True
    ):
        axes["GROUP_CLOSURE_EXACT"] = PROVED

    gid = e.get("post_effect_group") or {}
    if (
        isinstance(gid, dict)
        and gid.get("id")
        and gid.get("phase") == "post_effect"
        and gid.get("readback_exact") is True
    ):
        axes["POST_EFFECT_GROUP_ID_BOUND"] = PROVED

    policy = e.get("post_effect_policy") or {}
    if (
        isinstance(policy, dict)
        and policy.get("readback_exact") is True
        and policy.get("bound_to_final_effect") is True
        and policy.get("status") in ("pass", "bypass", "override", "fail", "evaluate_only")
    ):
        axes["POST_EFFECT_POLICY_EXACT"] = PROVED
        if policy.get("status") in ("bypass", "override"):
            warnings.append("post-effect policy used bypass/override; do not normalize to enforced pass")
        if policy.get("status") == "evaluate_only":
            warnings.append("evaluate-only policy is counterfactual, not active enforcement")

    if e.get("pre_effect_policy_pass") is True and axes["POST_EFFECT_POLICY_EXACT"] != PROVED:
        warnings.append("pre-effect policy pass is not a post-effect policy/effect lease")
    if axes["CI_STATE_BOUND"] == PROVED and axes["FINAL_TARGET_REF_EFFECT_EXACT"] != PROVED:
        warnings.append("CI candidate SHA is not final target-ref effect")
    if axes["QUEUE_OR_TRAIN_ADMITTED"] == PROVED and axes["FINAL_TARGET_REF_EFFECT_EXACT"] != PROVED:
        warnings.append("queue/train admission is not final target-ref effect")
    if axes["POST_EFFECT_GROUP_ID_BOUND"] == PROVED and axes["REQUEST_OPERATION_ID_BOUND"] != PROVED:
        warnings.append("post-effect group ID is not promoted to request-operation ID")
    if e.get("trigger_resource_only") is True and axes["GROUP_CLOSURE_EXACT"] != PROVED:
        warnings.append("single trigger resource is not complete group closure")

    causality = UNKNOWN
    if axes["FINAL_TARGET_REF_EFFECT_EXACT"] == PROVED:
        if axes["REQUEST_OPERATION_ID_BOUND"] == PROVED:
            causality = PROVED
        else:
            causality = "EFFECT_PROVED_REQUEST_CAUSALITY_UNKNOWN"

    return {"axes": axes, "request_to_effect_causality": causality, "warnings": warnings}

def self_test():
    out = {}

    gerrit_post = classify({
        "exact_intent_revision": True,
        "post_effect_group": {"id":"123-topic","phase":"post_effect","readback_exact":True},
        "final_target_ref_transition": {"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True},
    })
    assert gerrit_post["axes"]["POST_EFFECT_GROUP_ID_BOUND"] == PROVED
    assert gerrit_post["axes"]["REQUEST_OPERATION_ID_BOUND"] == UNKNOWN
    out["post_effect_group_not_request_id"] = PROVED

    ci_only = classify({"ci_state":{"id":1,"candidate_sha":"x","readback_exact":True}})
    assert ci_only["axes"]["CI_STATE_BOUND"] == PROVED
    assert ci_only["axes"]["FINAL_TARGET_REF_EFFECT_EXACT"] == UNKNOWN
    out["ci_sha_not_final_effect"] = PROVED

    queue = classify({"queue_or_train_admitted":True})
    assert queue["axes"]["QUEUE_OR_TRAIN_ADMITTED"] == PROVED
    assert queue["axes"]["FINAL_TARGET_REF_EFFECT_EXACT"] == UNKNOWN
    out["queue_admission_not_final_effect"] = PROVED

    prepolicy = classify({"pre_effect_policy_pass":True})
    assert prepolicy["axes"]["POST_EFFECT_POLICY_EXACT"] == UNKNOWN
    out["pre_policy_not_effect_lease"] = PROVED

    trigger = classify({"trigger_resource_only":True})
    assert trigger["axes"]["GROUP_CLOSURE_EXACT"] == UNKNOWN
    out["trigger_not_group_closure"] = PROVED

    actual_unknown_cause = classify({
        "final_target_ref_transition":{"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True}
    })
    assert actual_unknown_cause["axes"]["FINAL_TARGET_REF_EFFECT_EXACT"] == PROVED
    assert actual_unknown_cause["request_to_effect_causality"] == "EFFECT_PROVED_REQUEST_CAUSALITY_UNKNOWN"
    out["effect_without_request_id_keeps_causality_unknown"] = PROVED

    github = classify({
        "exact_intent_revision":True,
        "request_operation":{"id":"uuid","phase":"request","intent_verified":True},
        "queue_or_train_admitted":True,
        "ci_state":{"id":7,"candidate_sha":"mg","readback_exact":True},
        "final_target_ref_transition":{"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True},
        "group_closure":{"complete":True,"members":[1,2],"exact_readback":True},
        "post_effect_group":{"id":"uuid","phase":"post_effect","readback_exact":True},
        "post_effect_policy":{"readback_exact":True,"bound_to_final_effect":True,"status":"pass"},
    })
    assert all(v == PROVED for v in github["axes"].values())
    out["github_full_vector"] = PROVED

    gitlab_pending = classify({
        "exact_intent_revision":True,
        "request_operation":{"id":267,"phase":"admission","intent_verified":True},
        "queue_or_train_admitted":True,
        "ci_state":{"id":273,"candidate_sha":"train","readback_exact":True},
    })
    assert gitlab_pending["axes"]["FINAL_TARGET_REF_EFFECT_EXACT"] == UNKNOWN
    out["gitlab_train_ci_not_final"] = PROVED

    gerrit_full = classify({
        "exact_intent_revision":True,
        "final_target_ref_transition":{"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True},
        "group_closure":{"complete":True,"members":["I1","I2"],"exact_readback":True},
        "post_effect_group":{"id":"submission-1","phase":"post_effect","readback_exact":True},
        "post_effect_policy":{"readback_exact":True,"bound_to_final_effect":True,"status":"override"},
    })
    assert gerrit_full["axes"]["REQUEST_OPERATION_ID_BOUND"] == UNKNOWN
    assert gerrit_full["axes"]["FINAL_TARGET_REF_EFFECT_EXACT"] == PROVED
    assert any("bypass/override" in w for w in gerrit_full["warnings"])
    out["gerrit_full_effect_without_request_id"] = PROVED

    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(classify(json.load(sys.stdin)), indent=2, sort_keys=True))
