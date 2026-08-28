#!/usr/bin/env python3
"""Provider-neutral fail-closed operation/effect/provenance classifier V2.

Adds POLICY_PROVENANCE_ROOTS_EXACT as a separate axis from an observed
POST_EFFECT_POLICY_EXACT result. A server can authoritatively report a policy
outcome even when a client lacks enough version roots to replay *why* that
outcome occurred later.
"""
from __future__ import annotations
import json
import sys

PROVED = "PROVED"
UNKNOWN = "UNKNOWN"

AXES = (
    "INTENT_HEAD_BOUND",
    "REQUEST_OPERATION_ID_BOUND",
    "QUEUE_OR_TRAIN_ADMITTED",
    "CI_STATE_BOUND",
    "FINAL_TARGET_REF_EFFECT_EXACT",
    "GROUP_CLOSURE_EXACT",
    "POST_EFFECT_GROUP_ID_BOUND",
    "POST_EFFECT_POLICY_EXACT",
    "POLICY_PROVENANCE_ROOTS_EXACT",
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

def _policy_roots_exact(e):
    p = e.get("policy_provenance_roots")
    if not isinstance(p, dict):
        return False, "policy provenance roots absent"

    if p.get("change_meta_required") is True and not p.get("change_meta_sha"):
        return False, "required change metadata root missing"

    if p.get("project_config_required") is True:
        configs = p.get("project_config_shas")
        if not isinstance(configs, list) or not configs:
            return False, "required project config root(s) missing"
        if p.get("inheritance_closure_complete") is not True:
            return False, "project config inheritance closure incomplete"

    if p.get("plugins_participate") is True:
        plugins = p.get("plugin_provenance")
        if not isinstance(plugins, list) or not plugins:
            return False, "plugin policy participates but plugin provenance missing"
        if not all(isinstance(x, dict) and x.get("name") and x.get("version_or_digest") for x in plugins):
            return False, "plugin policy provenance incomplete"
    elif p.get("plugins_participate") is not False:
        return False, "plugin participation is unknown"

    if p.get("other_authority_roots_complete") is not True:
        return False, "other effective policy authority roots not proved complete"

    return True, None

def classify(e):
    axes = {a: UNKNOWN for a in AXES}
    warnings = []
    if not isinstance(e, dict):
        return {"axes": axes, "warnings": ["invalid evidence"]}

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

    roots_ok, roots_reason = _policy_roots_exact(e)
    if roots_ok:
        axes["POLICY_PROVENANCE_ROOTS_EXACT"] = PROVED
    elif e.get("policy_provenance_roots") is not None:
        warnings.append(roots_reason)

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
        causality = PROVED if axes["REQUEST_OPERATION_ID_BOUND"] == PROVED else "EFFECT_PROVED_REQUEST_CAUSALITY_UNKNOWN"

    replay = UNKNOWN
    if axes["POST_EFFECT_POLICY_EXACT"] == PROVED:
        replay = (
            "OUTCOME_OBSERVED_AND_POLICY_ROOTS_CAPTURED"
            if axes["POLICY_PROVENANCE_ROOTS_EXACT"] == PROVED
            else "OUTCOME_OBSERVED_POLICY_REPLAY_ROOTS_INCOMPLETE"
        )

    return {
        "axes": axes,
        "request_to_effect_causality": causality,
        "policy_replayability": replay,
        "warnings": warnings,
    }

def self_test():
    out = {}

    change_meta_only = classify({
        "policy_provenance_roots": {
            "change_meta_required": True,
            "change_meta_sha": "m",
            "project_config_required": True,
            "project_config_shas": [],
            "inheritance_closure_complete": False,
            "plugins_participate": False,
            "other_authority_roots_complete": True,
        }
    })
    assert change_meta_only["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == UNKNOWN
    out["change_meta_only_not_policy_universe"] = PROVED

    config_only = classify({
        "policy_provenance_roots": {
            "change_meta_required": True,
            "project_config_required": True,
            "project_config_shas": ["c"],
            "inheritance_closure_complete": True,
            "plugins_participate": False,
            "other_authority_roots_complete": True,
        }
    })
    assert config_only["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == UNKNOWN
    out["config_only_not_change_state"] = PROVED

    roots = {
        "change_meta_required": True,
        "change_meta_sha": "m",
        "project_config_required": True,
        "project_config_shas": ["project","all-projects"],
        "inheritance_closure_complete": True,
        "plugins_participate": False,
        "other_authority_roots_complete": True,
    }
    exact = classify({"policy_provenance_roots": roots})
    assert exact["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == PROVED
    out["multi_root_policy_provenance"] = PROVED

    plugin_missing = json.loads(json.dumps(roots))
    plugin_missing["plugins_participate"] = True
    plugin_missing["plugin_provenance"] = []
    x = classify({"policy_provenance_roots": plugin_missing})
    assert x["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == UNKNOWN
    out["plugin_policy_without_version_unknown"] = PROVED

    plugin_exact = json.loads(json.dumps(roots))
    plugin_exact["plugins_participate"] = True
    plugin_exact["plugin_provenance"] = [{"name":"submit-rule-x","version_or_digest":"sha256:abc"}]
    x = classify({"policy_provenance_roots": plugin_exact})
    assert x["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == PROVED
    out["plugin_policy_with_digest_proved"] = PROVED

    observed_no_roots = classify({
        "final_target_ref_transition":{"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True},
        "post_effect_policy":{"readback_exact":True,"bound_to_final_effect":True,"status":"pass"},
    })
    assert observed_no_roots["axes"]["POST_EFFECT_POLICY_EXACT"] == PROVED
    assert observed_no_roots["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == UNKNOWN
    assert observed_no_roots["policy_replayability"] == "OUTCOME_OBSERVED_POLICY_REPLAY_ROOTS_INCOMPLETE"
    out["observed_outcome_independent_of_replay_roots"] = PROVED

    full = classify({
        "exact_intent_revision":True,
        "request_operation":{"id":"u","phase":"request","intent_verified":True},
        "final_target_ref_transition":{"ref":"refs/heads/main","before_sha":"a","after_sha":"b","readback_exact":True},
        "group_closure":{"complete":True,"members":[1],"exact_readback":True},
        "post_effect_group":{"id":"g","phase":"post_effect","readback_exact":True},
        "post_effect_policy":{"readback_exact":True,"bound_to_final_effect":True,"status":"override"},
        "policy_provenance_roots": roots,
    })
    assert full["axes"]["POLICY_PROVENANCE_ROOTS_EXACT"] == PROVED
    assert full["policy_replayability"] == "OUTCOME_OBSERVED_AND_POLICY_ROOTS_CAPTURED"
    out["full_vector_with_policy_roots"] = PROVED

    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(classify(json.load(sys.stdin)), indent=2, sort_keys=True))
