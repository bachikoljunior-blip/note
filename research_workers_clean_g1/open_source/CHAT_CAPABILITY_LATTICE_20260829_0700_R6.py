from enum import Enum


class Verdict(str, Enum):
    PROVED = "PROVED"
    PARTIAL = "PARTIAL"
    REVALIDATE = "REVALIDATE"
    UNPROVEN = "UNPROVEN"
    BLOCKED = "BLOCKED"


def classify(kind: str, **e) -> Verdict:
    if kind == "mcp_discovery":
        if e.get("capability_explicitly_absent"):
            return Verdict.BLOCKED
        if not e.get("protocol_match") or not e.get("ttl_fresh") or not e.get("scope_match"):
            return Verdict.REVALIDATE
        if e.get("capability_present") and e.get("trusted_source"):
            return Verdict.PROVED
        return Verdict.UNPROVEN

    if kind == "mcp_tool_annotation":
        return Verdict.PARTIAL if e.get("server_trusted") else Verdict.UNPROVEN

    if kind == "openhands_lease":
        if not e.get("generation_fenced") or not e.get("all_persistent_writes_guarded"):
            return Verdict.UNPROVEN
        if e.get("storage_scope") != "supported_local_fs":
            return Verdict.UNPROVEN
        return Verdict.PROVED

    if kind == "openhands_persistence":
        if e.get("multi_file_transaction"):
            return Verdict.PROVED
        if e.get("per_file_atomic"):
            return Verdict.PARTIAL
        return Verdict.UNPROVEN

    if kind == "langgraph_replay":
        if not e.get("external_effect"):
            return Verdict.PARTIAL if e.get("checkpointed") else Verdict.UNPROVEN
        if e.get("effect_idempotency_or_cas"):
            return Verdict.PARTIAL
        return Verdict.UNPROVEN

    if kind == "mcp_task":
        if not e.get("extension_negotiated") or not e.get("durable_handle_before_response"):
            return Verdict.UNPROVEN
        if e.get("terminal_result_observed"):
            return Verdict.PROVED
        return Verdict.PARTIAL

    raise ValueError(kind)


def self_test() -> int:
    fixtures = [
        (
            "discover-good",
            "mcp_discovery",
            dict(
                protocol_match=True,
                ttl_fresh=True,
                scope_match=True,
                capability_present=True,
                trusted_source=True,
            ),
            Verdict.PROVED,
        ),
        (
            "discover-stale",
            "mcp_discovery",
            dict(
                protocol_match=True,
                ttl_fresh=False,
                scope_match=True,
                capability_present=True,
                trusted_source=True,
            ),
            Verdict.REVALIDATE,
        ),
        (
            "discover-wrong-scope",
            "mcp_discovery",
            dict(
                protocol_match=True,
                ttl_fresh=True,
                scope_match=False,
                capability_present=True,
                trusted_source=True,
            ),
            Verdict.REVALIDATE,
        ),
        (
            "discover-absent",
            "mcp_discovery",
            dict(capability_explicitly_absent=True),
            Verdict.BLOCKED,
        ),
        (
            "annotation-untrusted",
            "mcp_tool_annotation",
            dict(server_trusted=False),
            Verdict.UNPROVEN,
        ),
        (
            "annotation-trusted",
            "mcp_tool_annotation",
            dict(server_trusted=True),
            Verdict.PARTIAL,
        ),
        (
            "openhands-local-lease",
            "openhands_lease",
            dict(
                generation_fenced=True,
                all_persistent_writes_guarded=True,
                storage_scope="supported_local_fs",
            ),
            Verdict.PROVED,
        ),
        (
            "openhands-nfs-lease",
            "openhands_lease",
            dict(
                generation_fenced=True,
                all_persistent_writes_guarded=True,
                storage_scope="nfs",
            ),
            Verdict.UNPROVEN,
        ),
        (
            "openhands-per-file",
            "openhands_persistence",
            dict(per_file_atomic=True, multi_file_transaction=False),
            Verdict.PARTIAL,
        ),
        (
            "langgraph-external-no-key",
            "langgraph_replay",
            dict(
                checkpointed=True,
                external_effect=True,
                effect_idempotency_or_cas=False,
            ),
            Verdict.UNPROVEN,
        ),
        (
            "langgraph-external-keyed",
            "langgraph_replay",
            dict(
                checkpointed=True,
                external_effect=True,
                effect_idempotency_or_cas=True,
            ),
            Verdict.PARTIAL,
        ),
        (
            "mcp-task-pending",
            "mcp_task",
            dict(
                extension_negotiated=True,
                durable_handle_before_response=True,
                terminal_result_observed=False,
            ),
            Verdict.PARTIAL,
        ),
        (
            "mcp-task-terminal",
            "mcp_task",
            dict(
                extension_negotiated=True,
                durable_handle_before_response=True,
                terminal_result_observed=True,
            ),
            Verdict.PROVED,
        ),
    ]

    for name, kind, evidence, expected in fixtures:
        got = classify(kind, **evidence)
        if got != expected:
            raise AssertionError(f"{name}: expected {expected}, got {got}")
    return len(fixtures)


if __name__ == "__main__":
    print(f"PASS {self_test()}/13")
