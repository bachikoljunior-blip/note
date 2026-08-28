"""Source-equivalent crash/recovery classifier for Phase-1 open_source.

This is a small semantic model, not an execution of OpenHands or an MCP server.
It encodes only the exact source/spec branches cited in the accompanying checkpoint:

OpenHands v1.44.1 / 9d143aac35c2dcec9cbb046ff9f35ac5eb072f6a:
- persisted non-null leaf_event_id is authoritative on cold load;
- event persistence precedes leaf_event_id snapshot flush;
- Agent Server startup repairs RUNNING + unmatched ActionEvent by attaching an
  AgentErrorEvent directly under that action.

MCP Tasks 2026-07-28 extension:
- taskId is durable only after the server creates the task;
- no tasks/list recovery surface;
- ttlMs can expire/change;
- cancel ACK is cooperative intent, not stop proof;
- completed + tool isError is protocol completion, not logical success.

The fixtures intentionally classify boundaries instead of claiming product defects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Event:
    id: str
    kind: str
    parent_id: Optional[str] = None
    executable: bool = False
    tool_call_id: Optional[str] = None


ARTIFACT_KINDS = {"state_update", "conversation_error"}


def effective_parent(events: list[Event], idx: int) -> Optional[str]:
    event = events[idx]
    if event.parent_id == "__root__":
        return None
    if event.parent_id is not None:
        return event.parent_id
    if idx == 0:
        return None
    return events[idx - 1].id


def path_to_root(events: list[Event], leaf: Optional[str]) -> list[str]:
    if leaf is None:
        return []
    by_id = {event.id: i for i, event in enumerate(events)}
    chain: list[str] = []
    seen: set[str] = set()
    current = leaf
    while current is not None:
        if current in seen:
            raise AssertionError(f"cycle at {current}")
        seen.add(current)
        idx = by_id[current]
        chain.append(current)
        current = effective_parent(events, idx)
    return list(reversed(chain))


def resolve_active_leaf(
    events: list[Event],
    persisted_leaf: Optional[str],
    *,
    head_is_empty: bool = False,
) -> Optional[str]:
    # Exact relevant OpenHands rule: a non-null persisted leaf wins.
    if persisted_leaf is not None:
        return persisted_leaf
    if head_is_empty:
        return None
    for event in reversed(events):
        if event.kind not in ARTIFACT_KINDS:
            return event.id
    return None


def get_unmatched_actions(events: list[Event]) -> list[Event]:
    observed_action_ids: set[str] = set()
    observed_tool_call_ids: set[str] = set()
    unmatched: list[Event] = []
    for event in reversed(events):
        if event.kind in {"observation", "user_reject"}:
            if event.parent_id is not None:
                observed_action_ids.add(event.parent_id)
        elif event.kind == "agent_error" and event.tool_call_id:
            observed_tool_call_ids.add(event.tool_call_id)
        elif event.kind == "action" and event.executable:
            if (
                event.id not in observed_action_ids
                and event.tool_call_id not in observed_tool_call_ids
            ):
                unmatched.insert(0, event)
    return unmatched


def agent_server_start(
    events: list[Event], persisted_leaf: Optional[str], persisted_status: str
) -> tuple[list[Event], Optional[str], str]:
    """Model only EventService.start's relevant crash-recovery branch."""
    events = list(events)
    runtime_leaf = persisted_leaf
    status = persisted_status
    if status == "RUNNING":
        status = "ERROR"
        unmatched = get_unmatched_actions(events)
        if unmatched:
            action = unmatched[0]
            already_observed = any(
                event.kind in {"observation", "user_reject"}
                and event.tool_call_id == action.tool_call_id
                for event in events
            )
            if not already_observed:
                recovery = Event(
                    "recovery-error",
                    "agent_error",
                    parent_id=action.id,
                    tool_call_id=action.tool_call_id,
                )
                events.append(recovery)
                # _on_event -> append_event advances and persists the runtime HEAD.
                runtime_leaf = recovery.id
    return events, runtime_leaf, status


def mcp_task_recovery(
    *,
    task_created: bool,
    create_result_received: bool,
    task_id_persisted: bool,
    expired: bool = False,
    cancel_ack: bool = False,
    completed: bool = False,
    logical_is_error: bool = False,
) -> str:
    if cancel_ack:
        return "ACK_NOT_STOP_PROOF"
    if completed and logical_is_error:
        return "PROTOCOL_COMPLETE_NOT_LOGICAL_SUCCESS"
    if expired:
        return "EXPIRED_UNKNOWN"
    if task_created and not create_result_received and not task_id_persisted:
        return "AMBIGUOUS_UNRECOVERABLE_WITHOUT_APP_IDEMPOTENCY"
    if task_created and create_result_received and task_id_persisted:
        return "RESUMABLE_WITHIN_RETENTION"
    return "UNPROVEN"


def fixtures() -> list[tuple[str, object, object]]:
    action_log = [
        Event("root", "user"),
        Event(
            "act",
            "action",
            parent_id="root",
            executable=True,
            tool_call_id="tc",
        ),
    ]
    repaired, repaired_leaf, _ = agent_server_start(action_log, "root", "RUNNING")

    idle_user_log = [
        Event("root", "user"),
        Event("msg2", "user", parent_id="root"),
    ]
    idle_user, idle_leaf, _ = agent_server_start(idle_user_log, "root", "IDLE")

    running_user, running_leaf, _ = agent_server_start(
        idle_user_log, "root", "RUNNING"
    )

    running_user_with_artifact_log = [
        Event("root", "user"),
        Event("msg2", "user", parent_id="root"),
        Event("sync", "state_update", parent_id="msg2"),
    ]
    running_user_artifact, artifact_leaf, _ = agent_server_start(
        running_user_with_artifact_log, "root", "RUNNING"
    )

    return [
        (
            "openhands_running_unmatched_action_head_lag_is_repaired",
            path_to_root(
                repaired,
                resolve_active_leaf(repaired, repaired_leaf),
            ),
            ["root", "act", "recovery-error"],
        ),
        (
            "openhands_idle_user_message_head_lag_remains_outside_active_branch",
            path_to_root(
                idle_user,
                resolve_active_leaf(idle_user, idle_leaf),
            ),
            ["root"],
        ),
        (
            "openhands_running_user_message_without_unmatched_action_is_not_repaired",
            path_to_root(
                running_user,
                resolve_active_leaf(running_user, running_leaf),
            ),
            ["root"],
        ),
        (
            "openhands_state_update_artifact_does_not_generalize_head_repair",
            path_to_root(
                running_user_artifact,
                resolve_active_leaf(running_user_artifact, artifact_leaf),
            ),
            ["root"],
        ),
        (
            "mcp_taskid_received_and_persisted",
            mcp_task_recovery(
                task_created=True,
                create_result_received=True,
                task_id_persisted=True,
            ),
            "RESUMABLE_WITHIN_RETENTION",
        ),
        (
            "mcp_create_result_lost_before_taskid_persistence",
            mcp_task_recovery(
                task_created=True,
                create_result_received=False,
                task_id_persisted=False,
            ),
            "AMBIGUOUS_UNRECOVERABLE_WITHOUT_APP_IDEMPOTENCY",
        ),
        (
            "mcp_task_retention_expired",
            mcp_task_recovery(
                task_created=True,
                create_result_received=True,
                task_id_persisted=True,
                expired=True,
            ),
            "EXPIRED_UNKNOWN",
        ),
        (
            "mcp_cancel_ack",
            mcp_task_recovery(
                task_created=True,
                create_result_received=True,
                task_id_persisted=True,
                cancel_ack=True,
            ),
            "ACK_NOT_STOP_PROOF",
        ),
        (
            "mcp_completed_tool_error",
            mcp_task_recovery(
                task_created=True,
                create_result_received=True,
                task_id_persisted=True,
                completed=True,
                logical_is_error=True,
            ),
            "PROTOCOL_COMPLETE_NOT_LOGICAL_SUCCESS",
        ),
    ]


def main() -> None:
    cases = fixtures()
    failures = []
    for name, got, expected in cases:
        ok = got == expected
        print(f"{'PASS' if ok else 'FAIL'} {name}: {got!r}")
        if not ok:
            failures.append((name, got, expected))
    if failures:
        raise SystemExit(f"{len(failures)} fixture(s) failed: {failures!r}")
    print(f"PASS {len(cases)}/{len(cases)}")


if __name__ == "__main__":
    main()
