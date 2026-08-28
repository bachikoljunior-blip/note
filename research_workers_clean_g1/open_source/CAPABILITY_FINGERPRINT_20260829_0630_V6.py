#!/usr/bin/env python3
"""Fail-closed capability/effect fingerprint v6.

v6 adds authorization linearization and long-lived session freshness:
- prior authorization observations are not effect gates;
- ID-only/caller-verified effects are detached even if the verifier is strong;
- long-lived sessions must recheck current auth on each effect-bearing call or
  prove synchronous fail-closed session invalidation;
- request-bound current auth is distinct from proof that the effect succeeded.
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
REQUEST_BOUND_CURRENT_AUTH = "REQUEST_BOUND_CURRENT_AUTH"
VERIFIER_STRONG_EFFECT_DETACHED = "VERIFIER_STRONG_EFFECT_DETACHED"
SESSION_AUTHORIZATION_STALE_RISK = "SESSION_AUTHORIZATION_STALE_RISK"
FAIL_OPEN_CURRENT_AUTH_GATE = "FAIL_OPEN_CURRENT_AUTH_GATE"
EFFECT_PROVED = "PROVED_EFFECT_FOR_TESTED_INVOCATION"
UNKNOWN = "UNKNOWN"


def check(doc):
    if doc.get("schema_version") != 6:
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

    binding = doc.get("authorization_binding") or {}
    long_lived = binding.get("long_lived_session") is True

    if binding.get("current_authority_rechecked") is True \
            and binding.get("state_uncertainty_fails_closed") is False:
        return {"verdict": FAIL_OPEN_CURRENT_AUTH_GATE,
                "reason": "current authorization is consulted but uncertainty/outage can allow the effect",
                "reusable_permission_lease": False}

    if long_lived:
        per_call = binding.get("tool_call_rechecks_current_auth") is True
        invalidates = (
            binding.get("session_revocation_synchronously_invalidates") is True
            and binding.get("revocation_state_freshness_proved") is True
            and binding.get("state_uncertainty_fails_closed") is True
        )
        if not per_call and not invalidates:
            return {"verdict": SESSION_AUTHORIZATION_STALE_RISK,
                    "reason": "authorization is session-bound but current authorization is not proven on the effect-bearing call",
                    "reusable_permission_lease": False}

    if (
        binding.get("verification_occurs_in_effect_path") is True
        and binding.get("credential_consumed_by_effect") is True
        and binding.get("current_authority_rechecked") is True
        and binding.get("state_uncertainty_fails_closed") is True
        and (
            not long_lived
            or binding.get("tool_call_rechecks_current_auth") is True
            or (
                binding.get("session_revocation_synchronously_invalidates") is True
                and binding.get("revocation_state_freshness_proved") is True
            )
        )
    ):
        return {
            "verdict": REQUEST_BOUND_CURRENT_AUTH,
            "reason": "current authorization is enforced on the effect-bearing request path",
            "authorization_linearization_point": binding.get("authorization_linearization_point"),
            "proves_effect_success": False,
            "cross_system_atomic_revision_gate": binding.get("cross_system_atomic_revision_gate") is True,
            "reusable_permission_lease": False,
        }

    if (
        binding.get("auth_id_only") is True
        or (
            binding.get("strong_verifier_available") is True
            and binding.get("verification_occurs_in_effect_path") is not True
            and binding.get("credential_consumed_by_effect") is not True
        )
    ):
        return {
            "verdict": VERIFIER_STRONG_EFFECT_DETACHED,
            "reason": "strong verifier exists but the effect path does not consume/revalidate current credential authority",
            "reusable_permission_lease": False,
        }

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
        "schema_version": 6,
        "operation": {"tool": "tools/call", "mutation": True, "target": "mcp:server/tool:write"},
        "effective_enumeration": {"tool_names": ["tools/call"], "pre_action_reenumerated": True},
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
        "authorization_binding": {
            "strong_verifier_available": False,
            "verification_occurs_in_effect_path": False,
            "credential_consumed_by_effect": False,
            "current_authority_rechecked": False,
            "state_uncertainty_fails_closed": False,
            "auth_id_only": False,
            "long_lived_session": False,
            "tool_call_rechecks_current_auth": False,
            "session_revocation_synchronously_invalidates": False,
            "revocation_state_freshness_proved": False,
            "authorization_linearization_point": None,
            "cross_system_atomic_revision_gate": False
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
        "prior_authorization_review_is_observation_only": (
            fixture(authorization_evidence=ssar), AUTH_ALLOWED),
        "shiftlock_id_only_manager_is_detached": (
            fixture(authorization_binding={
                "strong_verifier_available": True,
                "auth_id_only": True,
                "verification_occurs_in_effect_path": False,
                "credential_consumed_by_effect": False,
            }), VERIFIER_STRONG_EFFECT_DETACHED),
        "session_authorized_only_at_initialize_is_stale_risk": (
            fixture(authorization_binding={
                "long_lived_session": True,
                "strong_verifier_available": True,
                "verification_occurs_in_effect_path": False,
                "credential_consumed_by_effect": False,
                "tool_call_rechecks_current_auth": False,
                "session_revocation_synchronously_invalidates": False,
            }), SESSION_AUTHORIZATION_STALE_RISK),
        "obot_per_post_uncached_acr_recheck": (
            fixture(authorization_binding={
                "long_lived_session": True,
                "verification_occurs_in_effect_path": True,
                "credential_consumed_by_effect": True,
                "current_authority_rechecked": True,
                "state_uncertainty_fails_closed": True,
                "tool_call_rechecks_current_auth": True,
                "authorization_linearization_point": "POST /mcp-connect/{mcp_id} authorizer",
            }), REQUEST_BOUND_CURRENT_AUTH),
        "keycloak_introspection_per_effect_request": (
            fixture(authorization_binding={
                "verification_occurs_in_effect_path": True,
                "credential_consumed_by_effect": True,
                "current_authority_rechecked": True,
                "state_uncertainty_fails_closed": True,
                "authorization_linearization_point": "protected-resource introspection admission",
            }), REQUEST_BOUND_CURRENT_AUTH),
        "contextforge_revocation_lookup_fail_open": (
            fixture(authorization_binding={
                "verification_occurs_in_effect_path": True,
                "credential_consumed_by_effect": True,
                "current_authority_rechecked": True,
                "state_uncertainty_fails_closed": False,
            }), FAIL_OPEN_CURRENT_AUTH_GATE),
        "session_revocation_push_with_proven_sync_invalidation": (
            fixture(authorization_binding={
                "long_lived_session": True,
                "verification_occurs_in_effect_path": True,
                "credential_consumed_by_effect": True,
                "current_authority_rechecked": True,
                "state_uncertainty_fails_closed": True,
                "tool_call_rechecks_current_auth": False,
                "session_revocation_synchronously_invalidates": True,
                "revocation_state_freshness_proved": True,
                "authorization_linearization_point": "session invalidation before next effect",
            }), REQUEST_BOUND_CURRENT_AUTH),
        "session_revocation_push_freshness_unproved": (
            fixture(authorization_binding={
                "long_lived_session": True,
                "verification_occurs_in_effect_path": False,
                "credential_consumed_by_effect": False,
                "current_authority_rechecked": False,
                "state_uncertainty_fails_closed": True,
                "tool_call_rechecks_current_auth": False,
                "session_revocation_synchronously_invalidates": True,
                "revocation_state_freshness_proved": False,
            }), SESSION_AUTHORIZATION_STALE_RISK),
        "successful_exact_effect_still_historical": (
            fixture(effect_evidence={
                "exact_operation_bound": True,
                "successful_response_observed": True,
                "result_readback_bound": True,
            }), EFFECT_PROVED),
        "exact_auth_denied": (
            fixture(authorization_evidence={**ssar, "decision": "denied"}), AUTH_DENIED),
        "dynamic_scope_cached": (
            fixture(authorization_scope={"can_change_at_runtime": True,
                                         "pre_action_observed": False}), STALE_SCOPE),
    }
    out = {}
    for name, (doc, expected) in cases.items():
        got = check(doc)["verdict"]
        assert got == expected, (name, got, expected)
        out[name] = got
    return out


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
