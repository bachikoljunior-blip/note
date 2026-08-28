#!/usr/bin/env python3
"""Fail-closed capability evidence checker v5.

v5 distinguishes authorization from effect success.  A server-side access
review can prove that the current principal is authorized for exact request
attributes *at the time of the review*.  It is not a lease: authorization can
change before the subsequent call, and later admission/validation/quota gates
can still reject a mutation.  Only a successful exact operation response proves
the tested invocation's effect/result at that time.

The checker also keeps tool-surface freshness and dynamic resource-scope
freshness separate; neither observation is a CAS token.
"""
from __future__ import annotations
import json, sys

SURFACE_MISSING = "SURFACE_MISSING"
STALE_SURFACE = "STALE_CAPABILITY_UNKNOWN"
STALE_SCOPE = "STALE_AUTHORIZATION_SCOPE_UNKNOWN"
AUTHZ_UNPROVEN = "AUTHORIZATION_UNPROVEN"
RESOURCE_ROLE_PROVED = "RESOURCE_ROLE_PROVED"
RESOURCE_SCOPE_PROVED = "RESOURCE_SCOPE_PROVED"
AUTH_ALLOWED = "OPERATION_AUTH_ALLOWED_AT_OBSERVATION"
AUTH_DENIED = "OPERATION_AUTH_DENIED_AT_OBSERVATION"
EFFECT_PROVED = "PROVED_EFFECT_FOR_TESTED_INVOCATION"
UNKNOWN = "UNKNOWN"


def check(doc):
    if doc.get("schema_version") != 5:
        return {"verdict": UNKNOWN, "reason": "unsupported schema_version"}
    op = doc.get("operation") or {}
    tool = op.get("tool")
    mutation = op.get("mutation") is True
    if not tool:
        return {"verdict": UNKNOWN, "reason": "operation.tool missing"}

    enum = doc.get("effective_enumeration") or {}
    tools = enum.get("tool_names")
    if not isinstance(tools, list):
        return {"verdict": UNKNOWN, "reason": "effective runtime enumeration missing"}
    sem = doc.get("server_semantics") or {}
    if mutation and sem.get("registry_can_change_at_runtime") is True \
            and enum.get("pre_action_reenumerated") is not True:
        return {"verdict": STALE_SURFACE,
                "reason": "dynamic mutation surface needs pre-action enumeration; observation is not a lease"}
    if tool not in tools:
        return {"verdict": SURFACE_MISSING,
                "reason": "tool absent from effective runtime enumeration",
                "scope": "tested connected/runtime surface only"}

    scope = doc.get("authorization_scope") or {}
    scope_dynamic = scope.get("can_change_at_runtime") is True
    if mutation and scope_dynamic and scope.get("pre_action_observed") is not True:
        return {"verdict": STALE_SCOPE,
                "reason": "dynamic resource scope needs pre-action observation; observation is not a lease"}
    target_scope_bound = (
        scope.get("target_bound") is True
        and scope.get("server_enforcement_proved") is True
        and scope.get("observation_authoritative_for_server") is True
    )
    if target_scope_bound and scope.get("target_in_scope") is False:
        return {"verdict": AUTH_DENIED,
                "reason": "server-enforced resource scope excludes exact target",
                "authorization_only": True}

    effect = doc.get("effect_evidence") or {}
    if (
        effect.get("exact_operation_bound") is True
        and effect.get("successful_response_observed") is True
        and effect.get("result_readback_bound") is True
    ):
        return {"verdict": EFFECT_PROVED,
                "reason": "successful exact invocation plus bound result/readback is observed",
                "reusable_permission_lease": False}

    auth = doc.get("authorization_evidence") or {}
    auth_bound = (
        auth.get("current_principal_bound") is True
        and auth.get("resource_and_operation_bound") is True
        and auth.get("request_attributes_exact") is True
        and auth.get("server_authoritative") is True
        and auth.get("observation_fresh") is True
    )
    decision = auth.get("decision")
    if auth_bound and decision == "denied":
        return {"verdict": AUTH_DENIED,
                "reason": "authoritative exact-operation authorization review denied at observation time",
                "reusable_permission_lease": False}
    if auth_bound and decision == "allowed":
        return {"verdict": AUTH_ALLOWED,
                "reason": "authoritative exact-operation authorization review allowed at observation time",
                "reusable_permission_lease": False,
                "later_authorization_drift_possible": True,
                "post_authorization_gates_may_still_reject": auth.get("post_authorization_gates_exist") is True,
                "evaluation_error": auth.get("evaluation_error")}

    if target_scope_bound and scope.get("target_in_scope") is True:
        return {"verdict": RESOURCE_SCOPE_PROVED,
                "reason": "exact target is inside proven server-enforced observed scope; exact operation authorization remains unproved",
                "reusable_permission_lease": False}

    role = auth.get("resource_role_evidence") or {}
    if (
        role.get("principal_bound") is True
        and role.get("resource_bound") is True
        and role.get("read_succeeded") is True
        and isinstance(role.get("role_or_permissions"), (str, list, dict))
    ):
        return {"verdict": RESOURCE_ROLE_PROVED,
                "reason": "principal/resource role evidence is proven but exact operation authorization is not",
                "role_or_permissions": role.get("role_or_permissions")}

    return {"verdict": AUTHZ_UNPROVEN,
            "reason": "surface is visible but exact operation authorization is not proven"}


def base_doc():
    return {
        "schema_version": 5,
        "operation": {"tool": "write_file", "mutation": True, "target": "/workspace/a"},
        "effective_enumeration": {"tool_names": ["write_file"], "pre_action_reenumerated": True},
        "server_semantics": {"registry_can_change_at_runtime": False},
        "authorization_scope": {
            "can_change_at_runtime": False,
            "pre_action_observed": False,
            "target_bound": False,
            "target_in_scope": None,
            "server_enforcement_proved": False,
            "observation_authoritative_for_server": False
        },
        "authorization_evidence": {
            "decision": "unknown",
            "current_principal_bound": False,
            "resource_and_operation_bound": False,
            "request_attributes_exact": False,
            "server_authoritative": False,
            "observation_fresh": False,
            "post_authorization_gates_exist": False,
            "evaluation_error": None,
            "resource_role_evidence": {
                "principal_bound": False, "resource_bound": False,
                "read_succeeded": False, "role_or_permissions": None
            }
        },
        "effect_evidence": {
            "exact_operation_bound": False,
            "successful_response_observed": False,
            "result_readback_bound": False
        }
    }


def merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            merge(dst[k], v)
        else:
            dst[k] = v


def fixture(**kw):
    d = json.loads(json.dumps(base_doc()))
    merge(d, kw)
    return d


def self_test():
    ssar = {
        "decision": "allowed",
        "current_principal_bound": True,
        "resource_and_operation_bound": True,
        "request_attributes_exact": True,
        "server_authoritative": True,
        "observation_fresh": True,
        "post_authorization_gates_exist": True,
        "evaluation_error": None
    }
    cases = {
        "kubernetes_ssar_allowed_is_not_effect_success": (
            fixture(authorization_evidence=ssar), AUTH_ALLOWED),
        "kubernetes_ssar_allowed_with_evaluation_error_still_auth_only": (
            fixture(authorization_evidence={**ssar, "evaluation_error": "partial authorizer error"}), AUTH_ALLOWED),
        "exact_auth_denied": (
            fixture(authorization_evidence={**ssar, "decision": "denied"}), AUTH_DENIED),
        "successful_exact_effect": (
            fixture(authorization_evidence=ssar,
                    effect_evidence={"exact_operation_bound": True,
                                     "successful_response_observed": True,
                                     "result_readback_bound": True}), EFFECT_PROVED),
        "repository_admin_role_is_not_operation_auth": (
            fixture(authorization_evidence={
                "resource_role_evidence": {
                    "principal_bound": True, "resource_bound": True,
                    "read_succeeded": True,
                    "role_or_permissions": {"admin": True, "push": True}}}),
            RESOURCE_ROLE_PROVED),
        "dynamic_scope_cached": (
            fixture(authorization_scope={"can_change_at_runtime": True,
                                         "pre_action_observed": False}), STALE_SCOPE),
    }
    out = {}
    for name, (doc, expect) in cases.items():
        got = check(doc)["verdict"]
        assert got == expect, (name, got, expect)
        out[name] = got
    return out


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
