#!/usr/bin/env python3
"""Fail-closed effective capability fingerprint checker v3.

v3 keeps MCP list-freshness semantics and splits repository/resource role
evidence from exact operation authorization:
- tools/list is an observation, not a versioned lease or mutation precondition;
- listChanged is an invalidation hint, not a CAS token;
- resource-bound principal/role evidence is useful but does not prove that the
  current credential is authorized for the exact mutation;
- only resource+operation-bound authoritative evidence can reach
  PROVED_CALLABLE_FOR_TESTED_SCOPE.
"""
from __future__ import annotations
import json, sys

SURFACE_MISSING = "SURFACE_MISSING"
STALE_UNKNOWN = "STALE_CAPABILITY_UNKNOWN"
AUTHZ_UNPROVEN = "AUTHORIZATION_UNPROVEN"
RESOURCE_ROLE_PROVED = "RESOURCE_ROLE_PROVED"
PROVED_CALLABLE = "PROVED_CALLABLE_FOR_TESTED_SCOPE"
DENIED = "AUTHORIZATION_DENIED"
UNKNOWN = "UNKNOWN"

def check(doc):
    if doc.get("schema_version") != 3:
        return {"verdict": UNKNOWN, "reason": "unsupported schema_version"}
    op = doc.get("operation") or {}
    tool = op.get("tool")
    mutation = op.get("mutation") is True
    if not tool:
        return {"verdict": UNKNOWN, "reason": "operation.tool missing"}

    enum = doc.get("effective_enumeration") or {}
    tools = enum.get("tool_names")
    if not isinstance(tools, list):
        return {"verdict": UNKNOWN, "reason": "effective tools/list missing"}

    sem = doc.get("server_semantics") or {}
    dynamic = sem.get("registry_can_change_at_runtime")
    preaction = enum.get("pre_action_reenumerated") is True

    if mutation and dynamic is True and not preaction:
        return {
            "verdict": STALE_UNKNOWN,
            "reason": "dynamic mutation surface requires pre-action tools/list; cached enumeration is not a lease",
            "list_changed_advertised": sem.get("list_changed_advertised"),
            "notification_path_verified": sem.get("notification_path_verified"),
        }

    if tool not in tools:
        return {
            "verdict": SURFACE_MISSING,
            "reason": "tool absent from effective runtime enumeration",
            "scope": "tested connected/runtime surface only; not platform absence",
        }

    auth = doc.get("authorization_evidence") or {}
    decision = auth.get("decision")
    op_bound = auth.get("resource_and_operation_bound") is True
    if decision == "denied" and op_bound:
        return {"verdict": DENIED, "reason": "safe operation-bound authorization evidence says denied"}
    if decision == "authorized" and op_bound:
        return {
            "verdict": PROVED_CALLABLE,
            "reason": "fresh effective surface plus resource-and-operation-bound authorization evidence",
            "scope": "callability only; list observation is not a CAS and mutation/effect success remains unproved",
            "call_time_drift_must_be_handled": dynamic is True,
        }

    role = auth.get("resource_role_evidence") or {}
    role_proved = (
        role.get("principal_bound") is True
        and role.get("resource_bound") is True
        and role.get("read_succeeded") is True
        and isinstance(role.get("role_or_permissions"), (str, list, dict))
    )
    if role_proved:
        return {
            "verdict": RESOURCE_ROLE_PROVED,
            "reason": "principal/resource role evidence is proven but exact operation authorization is not",
            "role_or_permissions": role.get("role_or_permissions"),
            "operation_authorization_proved": False,
            "call_time_drift_must_be_handled": dynamic is True,
        }

    return {
        "verdict": AUTHZ_UNPROVEN,
        "reason": "tool visible but resource/operation authorization is not proven",
        "visibility_semantics": sem.get("tool_visibility_authorization_semantics", "unknown"),
        "call_time_drift_must_be_handled": dynamic is True,
    }

def base_doc():
    return {
        "schema_version": 3,
        "operation": {"tool": "write_file", "mutation": True},
        "effective_enumeration": {
            "tool_names": ["read_file", "write_file"],
            "pre_action_reenumerated": True,
        },
        "server_semantics": {
            "registry_can_change_at_runtime": False,
            "list_changed_advertised": False,
            "notification_path_verified": False,
            "tool_visibility_authorization_semantics": "partial",
        },
        "authorization_evidence": {
            "decision": "unknown",
            "resource_and_operation_bound": False,
            "resource_role_evidence": {
                "principal_bound": False,
                "resource_bound": False,
                "read_succeeded": False,
                "role_or_permissions": None,
            },
        },
    }

def merge(dst, src):
    for k,v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            merge(dst[k], v)
        else:
            dst[k]=v

def fixture(**kw):
    d=json.loads(json.dumps(base_doc()))
    merge(d,kw)
    return d

def self_test():
    cases = {
        "dynamic_cached_even_with_notifications": (
            fixture(
                effective_enumeration={"pre_action_reenumerated":False},
                server_semantics={
                    "registry_can_change_at_runtime":True,
                    "list_changed_advertised":True,
                    "notification_path_verified":True,
                }),
            STALE_UNKNOWN),
        "fresh_missing_tool": (
            fixture(effective_enumeration={"tool_names":["read_file"],"pre_action_reenumerated":True}),
            SURFACE_MISSING),
        "visible_auth_unknown": (fixture(), AUTHZ_UNPROVEN),
        "repo_admin_is_role_only": (
            fixture(authorization_evidence={
                "resource_role_evidence":{
                    "principal_bound":True,
                    "resource_bound":True,
                    "read_succeeded":True,
                    "role_or_permissions":{"admin":True,"push":True},
                }}),
            RESOURCE_ROLE_PROVED),
        "role_without_principal_binding_is_unproven": (
            fixture(authorization_evidence={
                "resource_role_evidence":{
                    "principal_bound":False,
                    "resource_bound":True,
                    "read_succeeded":True,
                    "role_or_permissions":"admin",
                }}),
            AUTHZ_UNPROVEN),
        "bound_auth_positive": (
            fixture(authorization_evidence={"decision":"authorized","resource_and_operation_bound":True}),
            PROVED_CALLABLE),
        "bound_auth_denied": (
            fixture(authorization_evidence={"decision":"denied","resource_and_operation_bound":True}),
            DENIED),
    }
    out={}
    for name,(doc,expect) in cases.items():
        got=check(doc)["verdict"]
        assert got==expect,(name,got,expect)
        out[name]=got
    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
