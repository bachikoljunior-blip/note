#!/usr/bin/env python3
"""Fail-closed effective capability fingerprint checker v4.

v4 separates three independently stale dimensions:
1. effective tool surface;
2. resource authorization scope (for example a server-enforced filesystem
   allowlist that can be replaced at runtime);
3. exact operation authorization.

Neither MCP tools/list nor MCP Roots is a lease/CAS. MCP Roots is protocol
context; a server implementation must independently prove that it enforces the
derived scope on every relevant operation before roots can be treated as
authorization evidence.
"""
from __future__ import annotations
import json, sys

SURFACE_MISSING = "SURFACE_MISSING"
STALE_SURFACE = "STALE_CAPABILITY_UNKNOWN"
STALE_SCOPE = "STALE_AUTHORIZATION_SCOPE_UNKNOWN"
AUTHZ_UNPROVEN = "AUTHORIZATION_UNPROVEN"
RESOURCE_ROLE_PROVED = "RESOURCE_ROLE_PROVED"
RESOURCE_SCOPE_PROVED = "RESOURCE_SCOPE_PROVED"
PROVED_CALLABLE = "PROVED_CALLABLE_FOR_TESTED_SCOPE"
DENIED = "AUTHORIZATION_DENIED"
UNKNOWN = "UNKNOWN"

def check(doc):
    if doc.get("schema_version") != 4:
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
    if mutation and sem.get("registry_can_change_at_runtime") is True \
            and enum.get("pre_action_reenumerated") is not True:
        return {
            "verdict": STALE_SURFACE,
            "reason": "dynamic mutation surface requires pre-action enumeration; cached tools/list is not a lease",
        }
    if tool not in tools:
        return {
            "verdict": SURFACE_MISSING,
            "reason": "tool absent from effective runtime enumeration",
            "scope": "tested connected/runtime surface only; not platform absence",
        }

    scope = doc.get("authorization_scope") or {}
    scope_dynamic = scope.get("can_change_at_runtime") is True
    if mutation and scope_dynamic and scope.get("pre_action_observed") is not True:
        return {
            "verdict": STALE_SCOPE,
            "reason": "dynamic authorization scope requires a pre-action observation; cached scope is not a lease",
            "call_time_drift_must_be_handled": True,
        }

    target_scope_bound = (
        scope.get("target_bound") is True
        and scope.get("server_enforcement_proved") is True
        and scope.get("observation_authoritative_for_server") is True
    )
    in_scope = scope.get("target_in_scope")
    if target_scope_bound and in_scope is False:
        return {
            "verdict": DENIED,
            "reason": "server-enforced resource scope excludes the exact target",
        }

    auth = doc.get("authorization_evidence") or {}
    decision = auth.get("decision")
    op_bound = auth.get("resource_and_operation_bound") is True
    if decision == "denied" and op_bound:
        return {
            "verdict": DENIED,
            "reason": "safe resource-and-operation-bound authorization evidence says denied",
        }
    if decision == "authorized" and op_bound:
        return {
            "verdict": PROVED_CALLABLE,
            "reason": "fresh surface plus resource-and-operation-bound authorization evidence",
            "scope": "callability only; observations are not CAS and effect success remains unproved",
            "call_time_surface_drift_must_be_handled": sem.get("registry_can_change_at_runtime") is True,
            "call_time_scope_drift_must_be_handled": scope_dynamic,
        }

    if target_scope_bound and in_scope is True:
        return {
            "verdict": RESOURCE_SCOPE_PROVED,
            "reason": "exact target is inside a server-enforced observed scope, but exact operation authorization is not proven",
            "operation_authorization_proved": False,
            "call_time_scope_drift_must_be_handled": scope_dynamic,
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
        }

    return {
        "verdict": AUTHZ_UNPROVEN,
        "reason": "tool visible but exact authorization is not proven",
        "tool_visibility_authorization_semantics": sem.get(
            "tool_visibility_authorization_semantics", "unknown"
        ),
    }

def base_doc():
    return {
        "schema_version": 4,
        "operation": {
            "tool": "write_file",
            "mutation": True,
            "target": "/workspace/file.txt",
        },
        "effective_enumeration": {
            "tool_names": ["read_file", "write_file"],
            "pre_action_reenumerated": True,
        },
        "server_semantics": {
            "registry_can_change_at_runtime": False,
            "tool_visibility_authorization_semantics": "partial",
        },
        "authorization_scope": {
            "can_change_at_runtime": False,
            "pre_action_observed": False,
            "target_bound": False,
            "target_in_scope": None,
            "server_enforcement_proved": False,
            "observation_authoritative_for_server": False,
            "source": None,
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
            dst[k] = v

def fixture(**kw):
    d = json.loads(json.dumps(base_doc()))
    merge(d, kw)
    return d

def self_test():
    fs_scope = {
        "can_change_at_runtime": True,
        "pre_action_observed": True,
        "target_bound": True,
        "target_in_scope": True,
        "server_enforcement_proved": True,
        "observation_authoritative_for_server": True,
        "source": "server_list_allowed_directories",
    }
    cases = {
        "dynamic_tool_registry_cached": (
            fixture(
                effective_enumeration={"pre_action_reenumerated":False},
                server_semantics={"registry_can_change_at_runtime":True}),
            STALE_SURFACE),
        "filesystem_roots_scope_cached": (
            fixture(authorization_scope={**fs_scope, "pre_action_observed":False}),
            STALE_SCOPE),
        "protocol_roots_hint_not_enforcement": (
            fixture(authorization_scope={
                **fs_scope,
                "server_enforcement_proved":False,
                "source":"mcp_roots_protocol_only"}),
            AUTHZ_UNPROVEN),
        "server_scope_allows_target_role_only": (
            fixture(authorization_scope=fs_scope),
            RESOURCE_SCOPE_PROVED),
        "server_scope_denies_target": (
            fixture(authorization_scope={**fs_scope, "target_in_scope":False}),
            DENIED),
        "repo_admin_is_role_only": (
            fixture(authorization_evidence={
                "resource_role_evidence":{
                    "principal_bound":True,
                    "resource_bound":True,
                    "read_succeeded":True,
                    "role_or_permissions":{"admin":True,"push":True},
                }}),
            RESOURCE_ROLE_PROVED),
        "operation_bound_authorized": (
            fixture(
                authorization_scope=fs_scope,
                authorization_evidence={
                    "decision":"authorized",
                    "resource_and_operation_bound":True,
                }),
            PROVED_CALLABLE),
    }
    out = {}
    for name,(doc,expect) in cases.items():
        got = check(doc)["verdict"]
        assert got == expect, (name, got, expect)
        out[name] = got
    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
