from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


ROOT = "__root__"


@dataclass(frozen=True)
class Event:
    event_id: str
    parent_id: str | None
    source: str = "agent"
    kind: str = "message"
    body: str = ""

    def payload(self) -> str:
        return json.dumps(
            {
                "event_id": self.event_id,
                "parent_id": self.parent_id,
                "source": self.source,
                "kind": self.kind,
                "body": self.body,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def digest(self) -> str:
        return hashlib.sha256(self.payload().encode()).hexdigest()


@dataclass(frozen=True)
class Marker:
    base_generation: int
    expected_leaf: str | None
    expected_head_is_empty: bool
    event_id: str
    parent_id: str | None
    event_sha256: str


class RecoveryError(RuntimeError):
    pass


class State:
    def __init__(self):
        self.persisted_generation = 0
        self.persisted_leaf: str | None = None
        self.persisted_head_is_empty = False
        self.persisted_last_user: str | None = None

        self.leaf = self.persisted_leaf
        self.head_is_empty = self.persisted_head_is_empty
        self.last_user = self.persisted_last_user

        self.events: dict[str, Event] = {}
        self.markers: dict[str, Marker] = {}

    def append_without_base_flush(self, event_id: str, *, source="agent", body="") -> Event:
        parent = self.leaf
        if parent is None and self.events and self.head_is_empty:
            parent = ROOT
        event = Event(event_id, parent, source=source, body=body)
        marker = Marker(
            base_generation=self.persisted_generation,
            expected_leaf=self.leaf,
            expected_head_is_empty=self.head_is_empty,
            event_id=event.event_id,
            parent_id=event.parent_id,
            event_sha256=event.digest(),
        )
        # WAL ordering: marker first, then event.
        self.markers[event_id] = marker
        self.events[event_id] = event
        self.leaf = event_id
        self.head_is_empty = False
        if source == "user":
            self.last_user = event_id
        return event

    def persist_base_then_maybe_crash_before_marker_cleanup(self, cleanup=True):
        next_generation = self.persisted_generation + 1
        self.persisted_leaf = self.leaf
        self.persisted_head_is_empty = self.head_is_empty
        self.persisted_last_user = self.last_user
        self.persisted_generation = next_generation
        if cleanup:
            self.markers = {
                eid: m
                for eid, m in self.markers.items()
                if m.base_generation >= next_generation
            }

    def restart_from_persisted(self):
        self.leaf = self.persisted_leaf
        self.head_is_empty = self.persisted_head_is_empty
        self.last_user = self.persisted_last_user

    def recover_pending(self):
        # Markers from an older generation are known to precede a later committed
        # base snapshot and are stale cleanup leftovers.
        stale = [
            eid
            for eid, m in self.markers.items()
            if m.base_generation < self.persisted_generation
        ]
        for eid in stale:
            self.markers.pop(eid)

        if any(
            m.base_generation > self.persisted_generation
            for m in self.markers.values()
        ):
            raise RecoveryError("future-generation marker")

        pending = dict(self.markers)

        # Validate event identity/content before considering reachability.
        for eid, marker in pending.items():
            event = self.events.get(eid)
            if event is None:
                raise RecoveryError("marker without durable event")
            if event.parent_id != marker.parent_id:
                raise RecoveryError("parent mismatch")
            if event.digest() != marker.event_sha256:
                raise RecoveryError("hash mismatch")

        adopted: list[str] = []
        while pending:
            candidates = [
                (eid, m)
                for eid, m in pending.items()
                if m.expected_leaf == self.leaf
                and m.expected_head_is_empty == self.head_is_empty
            ]
            if not candidates:
                break
            if len(candidates) != 1:
                raise RecoveryError("ambiguous pending branch")
            eid, marker = candidates[0]
            event = self.events[eid]
            # The stamped event parent must also agree with the expected in-memory
            # head represented by the marker.
            expected_parent = marker.expected_leaf
            if expected_parent is None and marker.expected_head_is_empty and self.events:
                expected_parent = ROOT
            if event.parent_id != expected_parent:
                raise RecoveryError("expected-parent mismatch")
            self.leaf = eid
            self.head_is_empty = False
            if event.source == "user":
                self.last_user = eid
            adopted.append(eid)
            pending.pop(eid)

        if pending:
            # Never infer intent from "unique descendants" disconnected from the
            # exact persisted-head + marker chain.
            raise RecoveryError("unreachable pending marker")

        if adopted:
            self.persist_base_then_maybe_crash_before_marker_cleanup(cleanup=True)
        return adopted


def test_single_event_crash_before_base_recovers():
    s = State()
    s.append_without_base_flush("e1", source="user")
    s.restart_from_persisted()
    assert s.leaf is None
    assert s.recover_pending() == ["e1"]
    assert s.persisted_leaf == "e1"
    assert s.persisted_last_user == "e1"


def test_multiple_events_same_generation_recover_as_exact_chain():
    s = State()
    s.append_without_base_flush("e1")
    s.append_without_base_flush("e2", source="user")
    s.restart_from_persisted()
    assert s.recover_pending() == ["e1", "e2"]
    assert s.persisted_leaf == "e2"
    assert s.persisted_last_user == "e2"


def test_crash_after_base_write_before_marker_cleanup_does_not_reapply():
    s = State()
    s.append_without_base_flush("e1")
    s.persist_base_then_maybe_crash_before_marker_cleanup(cleanup=False)
    assert "e1" in s.markers
    s.restart_from_persisted()
    assert s.leaf == "e1"
    assert s.recover_pending() == []
    assert not s.markers


def test_markerless_orphan_is_not_adopted():
    s = State()
    s.events["orphan"] = Event("orphan", None, source="user")
    s.restart_from_persisted()
    assert s.recover_pending() == []
    assert s.leaf is None


def test_ambiguous_same_parent_markers_fail_closed():
    s = State()
    e1 = Event("e1", None)
    e2 = Event("e2", None)
    s.events = {"e1": e1, "e2": e2}
    s.markers = {
        "e1": Marker(0, None, False, "e1", None, e1.digest()),
        "e2": Marker(0, None, False, "e2", None, e2.digest()),
    }
    try:
        s.recover_pending()
    except RecoveryError as exc:
        assert "ambiguous" in str(exc)
        return
    raise AssertionError("ambiguous branch was auto-adopted")


def test_hash_mismatch_blocks():
    s = State()
    e1 = Event("e1", None, body="actual")
    s.events["e1"] = e1
    s.markers["e1"] = Marker(0, None, False, "e1", None, "bad")
    try:
        s.recover_pending()
    except RecoveryError as exc:
        assert "hash" in str(exc)
        return
    raise AssertionError("corrupt marker/event binding accepted")


def test_parent_mismatch_blocks():
    s = State()
    parent = Event("p", None)
    s.events["p"] = parent
    s.leaf = "p"
    s.persisted_leaf = "p"
    child = Event("c", None)  # should have parent p
    s.events["c"] = child
    s.markers["c"] = Marker(0, "p", False, "c", "p", child.digest())
    s.restart_from_persisted()
    try:
        s.recover_pending()
    except RecoveryError as exc:
        assert "parent mismatch" in str(exc)
        return
    raise AssertionError("parent mismatch accepted")


def test_old_generation_marker_is_stale_after_later_base_commit():
    s = State()
    s.append_without_base_flush("e1")
    s.persist_base_then_maybe_crash_before_marker_cleanup(cleanup=False)
    # Simulate another state-only base save (monotonic generation).
    s.persist_base_then_maybe_crash_before_marker_cleanup(cleanup=False)
    s.restart_from_persisted()
    assert s.persisted_generation == 2
    assert s.recover_pending() == []
    assert not s.markers


TESTS = [
    test_single_event_crash_before_base_recovers,
    test_multiple_events_same_generation_recover_as_exact_chain,
    test_crash_after_base_write_before_marker_cleanup_does_not_reapply,
    test_markerless_orphan_is_not_adopted,
    test_ambiguous_same_parent_markers_fail_closed,
    test_hash_mismatch_blocks,
    test_parent_mismatch_blocks,
    test_old_generation_marker_is_stale_after_later_base_commit,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(TESTS)}/{len(TESTS)}")
