#!/usr/bin/env python3
"""Fail-closed effective capability fingerprint checker.

This checker distinguishes:
1) platform capability claims,
2) effective runtime tool visibility,
3) freshness of that visibility, and
4) authorization evidence.

It never treats tool visibility alone as proof that a resource-specific write
will be authorized.
"""
from __future__ import annotations
import json, sys

SURFACE_PRESENT = "SURFACE_PRESENT"
SURFACE_MISSING = "SURFACE_MISSING"
STALE_UNKNOWN = "STALE_CAPABILITY_UNKNOWN"
AUTHZ_UNPROVEN = "AUTHORIZATION_UNPROVEN"
PROVED_CALLABLE = "PROVED_CALLABLE_FOR_TESTED_SCOPE"
DENIED = "AUTHORIZATION_DENIED"
UNKNOWN = "UNKNOWN"

def check(doc):
    if doc.get("schema_version") != 1:
        return {"verdict": UNKNOWN, "reason": "unsupported schema_version"}
    op = doc.get("operation") or {}
    tool = op.get("tool")
    if not tool:
        return {"verdict": UNKNOWN, "reason": "operation.tool missing"}

    enum = doc.get("effective_enumeration") or {}
    tools = enum.get("tool_names")
    if not isinstance(tools, list):
        return {"verdict": UNKNOWN, "reason": "effective tools/list missing"}

    sem = doc.get("server_semantics") or {}
    dynamic = sem.get("registry_can_change_at_runtime")
    notifications = sem.get("tool_change_notifications")
    preaction = enum.get("pre_action_reenumerated") is True
    if dynamic is True and notifications != "enabled" and not preaction:
        return {
            "verdict": STALE_UNKNOWN,
            "reason": "registry may change without reliable notification; pre-action re-enumeration required",
        }

    if tool not in tools:
        return {
            "verdict": SURFACE_MISSING,
            "reason": "tool absent from effective runtime enumeration",
            "scope": "tested connected/runtime surface only; not platform absence",
        }

    auth = doc.get("authorization_evidence") or {}
    decision = auth.get("decision")
    bound = auth.get("resource_and_operation_bound") is True
    if decision == "denied" and bound:
        return {"verdict": DENIED, "reason": "safe bound authorization evidence says denied"}
    if decision == "authorized" and bound:
        return {
            "verdict": PROVED_CALLABLE,
            "reason": "tool is present in fresh effective enumeration and bound authorization evidence is positive",
            "scope": "callability only; does not prove mutation preconditions or effect success",
        }

    visibility = sem.get("tool_visibility_authorization_semantics", "unknown")
    return {
        "verdict": AUTHZ_UNPROVEN,
        "reason": f"tool visible, but resource/operation authorization is not proven; visibility_semantics={visibility}",
        "surface": SURFACE_PRESENT,
    }

def fixture(**kw):
    base = {
        "schema_version": 1,
        "operation": {"tool": "write_file", "mutation": True},
        "effective_enumeration": {
            "tool_names": ["read_file", "write_file"],
            "pre_action_reenumerated": True,
        },
        "server_semantics": {
            "registry_can_change_at_runtime": False,
            "tool_change_notifications": "enabled",
            "tool_visibility_authorization_semantics": "partial",
        },
        "authorization_evidence": {
            "decision": "unknown",
            "resource_and_operation_bound": False,
        },
    }
    def merge(dst, src):
        for k,v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                merge(dst[k], v)
            else:
                dst[k]=v
    merge(base, kw)
    return base

def self_test():
    cases = {}
    cases["github_app_visible_not_authorized"] = (
        fixture(server_semantics={"tool_visibility_authorization_semantics":"api_enforced"}),
        AUTHZ_UNPROVEN,
    )
    cases["classic_pat_filter_fail_open"] = (
        fixture(server_semantics={"tool_visibility_authorization_semantics":"fail_open_possible"}),
        AUTHZ_UNPROVEN,
    )
    cases["k8s_stateless_cached_list"] = (
        fixture(
            effective_enumeration={"pre_action_reenumerated":False},
            server_semantics={
                "registry_can_change_at_runtime":True,
                "tool_change_notifications":"disabled",
                "tool_visibility_authorization_semantics":"cluster_rbac_separate",
            }),
        STALE_UNKNOWN,
    )
    cases["fresh_list_tool_missing"] = (
        fixture(effective_enumeration={"tool_names":["read_file"],"pre_action_reenumerated":True}),
        SURFACE_MISSING,
    )
    cases["bound_safe_auth_positive"] = (
        fixture(authorization_evidence={
            "decision":"authorized","resource_and_operation_bound":True}),
        PROVED_CALLABLE,
    )
    cases["bound_safe_auth_denied"] = (
        fixture(authorization_evidence={
            "decision":"denied","resource_and_operation_bound":True}),
        DENIED,
    )
    out={}
    for name,(doc,expected) in cases.items():
        got=check(doc)["verdict"]
        assert got==expected,(name,got,expected)
        out[name]=got
    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
