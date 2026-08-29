#!/usr/bin/env python3
"""Source-equivalent crash model for OpenHands fenced HEAD-marker recovery.

Target source examined:
- OpenHands/software-agent-sdk v1.44.1
- commit 9d143aac35c2dcec9cbb046ff9f35ac5eb072f6a
- ConversationState autosaves each public-field mutation outside `with state:`.
- Candidate R6 `_save_base_state` increments persistence_generation and removes
  all markers from older generations.

This model demonstrates a recovery-time crash counterexample in R6:
for a two-event pending chain, adopting event 1 mutates `leaf_event_id`;
because reconciliation runs outside a ConversationState context, that assignment
autosaves immediately, advances the generation, and cleans *both* event markers.
A crash before event 2 is adopted leaves event 2 durable but markerless.

The corrected shape is two-phase:
(1) validate and plan the entire marker chain without mutating durable HEAD;
(2) commit the final reconstructed HEAD once, then clean stale markers.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(eq=True)
class Store:
    persisted_head: str
    generation: int
    markers: dict[str, dict[str, object]]
    events: dict[str, dict[str, object]]


def r6_first_adoption_then_crash(store: Store) -> None:
    """Model the R6 recovery ordering through its first public-field assignment."""
    pending = deepcopy(store.markers)
    candidates = [
        event_id
        for event_id, marker in pending.items()
        if marker["expected_head"] == store.persisted_head
    ]
    assert candidates == ["e1"]
    event_id = candidates[0]

    # `self.leaf_event_id = event_id` outside a state context autosaves now.
    store.persisted_head = event_id
    store.generation += 1

    # Candidate `_save_base_state` cleans every marker with older base_generation.
    store.markers = {
        event_id: marker
        for event_id, marker in store.markers.items()
        if int(marker["base_generation"]) >= store.generation
    }
    # Simulated process death here, before the second pending event is adopted.


def two_phase_reconcile(store: Store, *, crash_after_commit: bool = False) -> None:
    """Validate the complete chain first, then persist one HEAD transition."""
    pending = deepcopy(store.markers)
    virtual_head = store.persisted_head
    plan: list[str] = []

    while pending:
        candidates = [
            event_id
            for event_id, marker in pending.items()
            if marker["expected_head"] == virtual_head
            and int(marker["base_generation"]) == store.generation
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                f"fail closed: candidates={candidates}, pending={list(pending)}"
            )

        event_id = candidates[0]
        event = store.events.get(event_id)
        if event is None or event["parent"] != virtual_head:
            raise RuntimeError("missing or parent-mismatched event")

        plan.append(event_id)
        virtual_head = event_id
        pending.pop(event_id)

    if not plan:
        return

    # Single durable base-state commit for the reconstructed chain.
    store.persisted_head = virtual_head
    store.generation += 1

    if crash_after_commit:
        return

    store.markers = {
        event_id: marker
        for event_id, marker in store.markers.items()
        if int(marker["base_generation"]) >= store.generation
    }


def restart_cleanup(store: Store) -> None:
    """Idempotent cleanup after base commit won but marker deletion lost."""
    store.markers = {
        event_id: marker
        for event_id, marker in store.markers.items()
        if int(marker["base_generation"]) >= store.generation
    }


def chain_store() -> Store:
    return Store(
        persisted_head="h0",
        generation=0,
        markers={
            "e1": {"base_generation": 0, "expected_head": "h0"},
            "e2": {"base_generation": 0, "expected_head": "e1"},
        },
        events={"e1": {"parent": "h0"}, "e2": {"parent": "e1"}},
    )


def run() -> list[str]:
    passed: list[str] = []

    s = chain_store()
    r6_first_adoption_then_crash(s)
    assert s.persisted_head == "e1"
    assert s.markers == {}
    assert "e2" in s.events
    passed.append("r6_partial_recovery_cleanup_orphans_second_event")

    s = chain_store()
    two_phase_reconcile(s)
    assert s.persisted_head == "e2"
    assert s.generation == 1
    assert s.markers == {}
    passed.append("two_phase_chain_single_commit")

    s = Store(
        persisted_head="h0",
        generation=0,
        markers={"e1": {"base_generation": 0, "expected_head": "h0"}},
        events={"e1": {"parent": "h0"}},
    )
    two_phase_reconcile(s, crash_after_commit=True)
    assert s.persisted_head == "e1"
    assert s.generation == 1
    assert "e1" in s.markers
    restart_cleanup(s)
    assert s.markers == {}
    passed.append("commit_before_cleanup_restart_is_idempotent")

    s = Store(
        persisted_head="h0",
        generation=0,
        markers={
            "e1": {"base_generation": 0, "expected_head": "h0"},
            "eX": {"base_generation": 0, "expected_head": "h0"},
        },
        events={"e1": {"parent": "h0"}, "eX": {"parent": "h0"}},
    )
    before = deepcopy(s)
    try:
        two_phase_reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("ambiguous branch must fail closed")
    assert s == before
    passed.append("ambiguity_has_no_partial_write")

    s = Store(
        persisted_head="h0",
        generation=0,
        markers={
            "e1": {"base_generation": 0, "expected_head": "h0"},
            "e2": {"base_generation": 0, "expected_head": "other"},
        },
        events={"e1": {"parent": "h0"}, "e2": {"parent": "other"}},
    )
    before = deepcopy(s)
    try:
        two_phase_reconcile(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("unreachable marker must fail closed")
    assert s == before
    passed.append("unreachable_chain_has_no_partial_write")

    return passed


if __name__ == "__main__":
    passed = run()
    print(f"PASS {len(passed)}/{len(passed)}")
    for name in passed:
        print(name)
