#!/usr/bin/env python3
"""Source-equivalent two-phase recovery model for OpenHands HEAD markers.

This model is intentionally smaller than OpenHands. It exercises the recovery
state machine needed by an R7 candidate after exact-source audit of v1.44.1
(commit 9d143aac35c2dcec9cbb046ff9f35ac5eb072f6a).

Safety property: validate the whole marker/event chain with local variables
before the first durable HEAD mutation. Only one base-state generation is
committed for a recovered chain; marker cleanup happens after that commit.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

ROOT = "__root__"


@dataclass(eq=True)
class Store:
    leaf: str | None
    head_is_empty: bool
    last_user: str | None
    generation: int
    markers: dict[str, dict[str, object]]
    events: dict[str, dict[str, object]]


def event(parent: str | None, kind="message", source="user", digest="d"):
    return {"parent": parent, "kind": kind, "source": source, "digest": digest}


def marker(
    base_generation: int,
    expected_leaf: str | None,
    expected_empty: bool,
    parent: str | None,
    digest="d",
):
    return {
        "base_generation": base_generation,
        "expected_leaf": expected_leaf,
        "expected_empty": expected_empty,
        "parent": parent,
        "digest": digest,
    }


def reconcile(store: Store, *, crash_after_base: bool = False) -> None:
    # Cleanup that is safe without changing HEAD: old-generation residue and a
    # marker whose event never reached durable storage.
    work: dict[str, dict[str, object]] = {}
    for event_id, item in list(store.markers.items()):
        base_generation = int(item["base_generation"])
        if base_generation < store.generation:
            del store.markers[event_id]
            continue
        if base_generation > store.generation:
            raise RuntimeError("future marker generation")
        if event_id not in store.events:
            del store.markers[event_id]
            continue

        persisted = store.events[event_id]
        if persisted["parent"] != item["parent"]:
            raise RuntimeError("parent mismatch")
        if persisted["digest"] != item["digest"]:
            raise RuntimeError("digest mismatch")
        work[event_id] = deepcopy(item)

    if not work:
        return

    # Pure planning phase: no HEAD mutation, no generation advance.
    virtual_leaf = store.leaf
    virtual_empty = store.head_is_empty
    virtual_last_user = store.last_user

    while work:
        candidates = [
            event_id
            for event_id, item in work.items()
            if item["expected_leaf"] == virtual_leaf
            and bool(item["expected_empty"]) == virtual_empty
        ]
        if len(candidates) != 1:
            raise RuntimeError("ambiguous or unreachable marker chain")

        event_id = candidates[0]
        persisted = store.events[event_id]
        if virtual_empty:
            if persisted["parent"] != ROOT:
                raise RuntimeError("event after empty HEAD must be an explicit root")
        elif virtual_leaf is not None and persisted["parent"] != virtual_leaf:
            raise RuntimeError("event parent does not match planned HEAD")

        virtual_leaf = event_id
        virtual_empty = False
        if persisted["kind"] == "message" and persisted["source"] == "user":
            virtual_last_user = event_id
        work.pop(event_id)

    # Atomic-base phase in the model. Real source should serialize a snapshot
    # containing these final values and generation+1, write base_state.json once,
    # then update in-memory fields without triggering intermediate autosaves.
    store.leaf = virtual_leaf
    store.head_is_empty = virtual_empty
    store.last_user = virtual_last_user
    store.generation += 1

    if crash_after_base:
        return

    for event_id, item in list(store.markers.items()):
        if int(item["base_generation"]) < store.generation:
            del store.markers[event_id]


def run() -> list[str]:
    passed: list[str] = []

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {
            "e1": marker(0, "h0", False, "h0", "d1"),
            "e2": marker(0, "e1", False, "e1", "d2"),
        },
        {"e1": event("h0", digest="d1"), "e2": event("e1", digest="d2")},
    )
    reconcile(s)
    assert s.leaf == "e2" and s.last_user == "e2" and not s.markers
    passed.append("two_event_chain_single_commit")

    s = Store(
        "h0", False, "h0", 0, {"e1": marker(0, "h0", False, "h0", "d1")}, {}
    )
    reconcile(s)
    assert s.leaf == "h0" and s.generation == 0 and not s.markers
    passed.append("marker_before_event_cleanup")

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {"e1": marker(0, "h0", False, "h0", "d1")},
        {"e1": event("h0", digest="d1")},
    )
    reconcile(s, crash_after_base=True)
    assert s.leaf == "e1" and s.generation == 1 and "e1" in s.markers
    reconcile(s)
    assert s.leaf == "e1" and not s.markers
    passed.append("base_commit_before_marker_cleanup")

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {
            "e1": marker(0, "h0", False, "h0", "d1"),
            "eX": marker(0, "h0", False, "h0", "dx"),
        },
        {"e1": event("h0", digest="d1"), "eX": event("h0", digest="dx")},
    )
    before = deepcopy(s)
    try:
        reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("ambiguous chain must fail closed")
    assert s == before
    passed.append("ambiguous_chain_no_partial_head_write")

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {"e1": marker(0, "other", False, "other", "d1")},
        {"e1": event("other", digest="d1")},
    )
    before = deepcopy(s)
    try:
        reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("unreachable chain must fail closed")
    assert s == before
    passed.append("unreachable_chain_no_partial_head_write")

    s = Store(
        None,
        True,
        None,
        3,
        {"e1": marker(3, None, True, ROOT, "d1")},
        {"e1": event(ROOT, digest="d1")},
    )
    reconcile(s)
    assert s.leaf == "e1" and s.head_is_empty is False
    passed.append("explicit_empty_head_root_adoption")

    s = Store(
        "h0",
        False,
        "u0",
        0,
        {
            "e1": marker(0, "h0", False, "h0", "d1"),
            "e2": marker(0, "e1", False, "e1", "d2"),
            "e3": marker(0, "e2", False, "e2", "d3"),
        },
        {
            "e1": event("h0", "action", "agent", "d1"),
            "e2": event("e1", "message", "user", "d2"),
            "e3": event("e2", "observation", "environment", "d3"),
        },
    )
    reconcile(s)
    assert s.leaf == "e3" and s.last_user == "e2"
    passed.append("mixed_chain_last_user_bookkeeping")

    s = Store("h0", False, "h0", 0, {}, {"orphan": event("h0", digest="do")})
    reconcile(s)
    assert s.leaf == "h0"
    passed.append("markerless_orphan_not_adopted")

    s = Store(
        "navigated",
        False,
        "u0",
        2,
        {"e1": marker(1, "old", False, "old", "d1")},
        {"e1": event("old", digest="d1")},
    )
    reconcile(s)
    assert s.leaf == "navigated" and s.generation == 2 and not s.markers
    passed.append("stale_marker_after_navigation_is_cleanup_only")

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {"e1": marker(0, "h0", False, "h0", "expected")},
        {"e1": event("h0", digest="actual")},
    )
    before = deepcopy(s)
    try:
        reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("digest mismatch must fail closed")
    assert s == before
    passed.append("digest_mismatch_no_head_write")

    s = Store(
        "h0",
        False,
        "h0",
        0,
        {"e1": marker(1, "h0", False, "h0", "d1")},
        {"e1": event("h0", digest="d1")},
    )
    before = deepcopy(s)
    try:
        reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("future generation must fail closed")
    assert s == before
    passed.append("future_generation_no_head_write")

    return passed


if __name__ == "__main__":
    passed = run()
    print(f"PASS {len(passed)}/{len(passed)}")
    for name in passed:
        print(name)
