"""Source-equivalent crash harness for the OpenHands fenced-HEAD marker candidate.

Target inspected: OpenHands/software-agent-sdk v1.44.1 / commit
9d143aac35c2dcec9cbb046ff9f35ac5eb072f6a.

This does not import or execute OpenHands. It models the exact persistence ordering
that matters for the candidate: autosave on public ConversationState field writes,
persistence-generation cleanup, pending marker binding, and one-shot repaired base
snapshot. It intentionally demonstrates a correctness bug in the R6 candidate and
then exercises the corrected single-commit recovery protocol.
"""

from dataclasses import dataclass, field
from typing import Optional


class Crash(Exception):
    pass


class FailClosed(Exception):
    pass


@dataclass
class Event:
    id: str
    parent_id: Optional[str]
    source: str = "user"
    digest: str = ""


@dataclass
class Marker:
    base_generation: int
    expected_leaf: Optional[str]
    expected_empty: bool
    event_id: str
    parent_id: Optional[str]
    digest: str


@dataclass
class Durable:
    generation: int = 0
    leaf: Optional[str] = None
    head_empty: bool = False
    last_user: Optional[str] = None
    markers: dict[str, Marker] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)


def cleanup_old(d: Durable) -> None:
    for key, marker in list(d.markers.items()):
        if marker.base_generation < d.generation:
            del d.markers[key]


def commit_snapshot(
    d: Durable,
    *,
    leaf: Optional[str],
    head_empty: bool,
    last_user: Optional[str],
) -> None:
    d.generation += 1
    d.leaf = leaf
    d.head_empty = head_empty
    d.last_user = last_user
    cleanup_old(d)


def r6_reconcile_trace(d: Durable, *, crash_after_leaf: bool = False) -> None:
    """Model the R6 candidate with upstream autosave still enabled.

    In exact OpenHands source, public field assignment outside a ConversationState
    context immediately calls _save_base_state(). The R6 candidate mutates
    leaf_event_id and last_user_message_id independently during startup recovery,
    so the first assignment commits a newer generation and deletes the pending
    marker before all recovered fields are durable.
    """
    leaf = d.leaf
    head_empty = d.head_empty
    last_user = d.last_user
    candidates = [
        marker
        for marker in d.markers.values()
        if marker.base_generation == d.generation
        and marker.expected_leaf == leaf
        and marker.expected_empty == head_empty
    ]
    if len(candidates) != 1:
        raise FailClosed("expected exactly one candidate")
    marker = candidates[0]
    event = d.events[marker.event_id]
    if event.parent_id != marker.parent_id or event.digest != marker.digest:
        raise FailClosed("binding mismatch")

    leaf = event.id
    commit_snapshot(d, leaf=leaf, head_empty=head_empty, last_user=last_user)
    if crash_after_leaf:
        raise Crash("process dies after leaf autosave, before last_user autosave")

    if head_empty:
        head_empty = False
        commit_snapshot(d, leaf=leaf, head_empty=head_empty, last_user=last_user)
    if event.source == "user":
        last_user = event.id
        commit_snapshot(d, leaf=leaf, head_empty=head_empty, last_user=last_user)

    # R6 also performs an explicit final _save_base_state().
    commit_snapshot(d, leaf=leaf, head_empty=head_empty, last_user=last_user)


def r7_reconcile(d: Durable, *, crash_before_commit: bool = False) -> list[str]:
    """Corrected protocol: reconstruct in memory, then commit one base snapshot."""
    leaf = d.leaf
    head_empty = d.head_empty
    last_user = d.last_user
    pending = dict(d.markers)
    adopted: list[str] = []

    for key, marker in list(pending.items()):
        if marker.base_generation < d.generation:
            d.markers.pop(key, None)
            pending.pop(key, None)
            continue
        if marker.base_generation > d.generation:
            raise FailClosed("future generation")
        event = d.events.get(marker.event_id)
        if event is None:
            # marker-before-event crash
            d.markers.pop(key, None)
            pending.pop(key, None)
            continue
        if event.parent_id != marker.parent_id or event.digest != marker.digest:
            raise FailClosed("binding mismatch")

    while pending:
        candidates = [
            marker
            for marker in pending.values()
            if marker.expected_leaf == leaf and marker.expected_empty == head_empty
        ]
        if not candidates:
            break
        if len(candidates) != 1:
            raise FailClosed("ambiguous")

        marker = candidates[0]
        event = d.events[marker.event_id]
        leaf = event.id
        if head_empty:
            head_empty = False
        if event.source == "user":
            last_user = event.id
        adopted.append(event.id)
        pending.pop(marker.event_id)

    if pending:
        raise FailClosed("unreachable")

    if adopted:
        if crash_before_commit:
            raise Crash("process dies before the single repaired base snapshot")
        commit_snapshot(d, leaf=leaf, head_empty=head_empty, last_user=last_user)
    return adopted


def mk_pending(
    *,
    generation: int = 0,
    leaf: Optional[str] = "a",
    empty: bool = False,
    last_user: Optional[str] = "a",
    eid: str = "b",
    parent: Optional[str] = "a",
    source: str = "user",
    digest: str = "db",
) -> Durable:
    durable = Durable(
        generation=generation,
        leaf=leaf,
        head_empty=empty,
        last_user=last_user,
    )
    event = Event(eid, parent, source=source, digest=digest)
    durable.events[eid] = event
    durable.markers[eid] = Marker(
        generation,
        leaf,
        empty,
        eid,
        parent,
        digest,
    )
    return durable


def run() -> None:
    results: list[tuple[str, bool]] = []

    d = mk_pending()
    try:
        r6_reconcile_trace(d, crash_after_leaf=True)
    except Crash:
        pass
    results.append(
        (
            "r6_autosave_split_refuted",
            d.leaf == "b"
            and d.last_user == "a"
            and not d.markers
            and d.generation == 1,
        )
    )

    d = mk_pending()
    try:
        r7_reconcile(d, crash_before_commit=True)
    except Crash:
        pass
    results.append(
        (
            "r7_precommit_crash_retriable",
            d.leaf == "a"
            and d.last_user == "a"
            and "b" in d.markers
            and d.generation == 0,
        )
    )

    d = mk_pending()
    adopted = r7_reconcile(d)
    results.append(
        (
            "r7_retry_single_commit",
            adopted == ["b"]
            and d.leaf == "b"
            and d.last_user == "b"
            and d.generation == 1
            and not d.markers,
        )
    )

    d = Durable(generation=4, leaf="a", last_user="a")
    d.markers["b"] = Marker(4, "a", False, "b", "a", "db")
    adopted = r7_reconcile(d)
    results.append(
        (
            "marker_before_event_discard",
            adopted == [] and d.leaf == "a" and not d.markers and d.generation == 4,
        )
    )

    d = Durable(generation=6, leaf="b", last_user="b")
    d.events["b"] = Event("b", "a", digest="db")
    d.markers["b"] = Marker(5, "a", False, "b", "a", "db")
    adopted = r7_reconcile(d)
    results.append(
        (
            "base_before_cleanup_idempotent",
            adopted == [] and d.leaf == "b" and not d.markers and d.generation == 6,
        )
    )

    d = Durable(generation=0, leaf="a", last_user="a")
    for eid in ("b", "c"):
        d.events[eid] = Event(eid, "a", digest=f"d{eid}")
        d.markers[eid] = Marker(0, "a", False, eid, "a", f"d{eid}")
    try:
        r7_reconcile(d)
        ok = False
    except FailClosed as exc:
        ok = "ambiguous" in str(exc)
    results.append(("ambiguous_same_parent_blocked", ok))

    d = Durable(generation=0, leaf="a", last_user="a")
    d.events["orphan"] = Event("orphan", "a", digest="do")
    adopted = r7_reconcile(d)
    results.append(("markerless_orphan_not_adopted", adopted == [] and d.leaf == "a"))

    d = mk_pending()
    d.events["b"].parent_id = "wrong"
    try:
        r7_reconcile(d)
        ok = False
    except FailClosed as exc:
        ok = "binding mismatch" in str(exc)
    results.append(("binding_mismatch_blocked", ok))

    d = mk_pending(
        leaf=None,
        empty=True,
        last_user="old",
        eid="newroot",
        parent="__root__",
        digest="dr",
    )
    adopted = r7_reconcile(d)
    results.append(
        (
            "empty_head_new_root_recovered",
            adopted == ["newroot"]
            and d.leaf == "newroot"
            and not d.head_empty
            and d.last_user == "newroot",
        )
    )

    d = mk_pending(source="agent")
    adopted = r7_reconcile(d)
    results.append(
        (
            "non_user_preserves_last_user",
            adopted == ["b"] and d.last_user == "a",
        )
    )

    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    passed = sum(ok for _, ok in results)
    print(f"PASS {passed}/{len(results)}" if passed == len(results) else f"FAIL {passed}/{len(results)}")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    run()
