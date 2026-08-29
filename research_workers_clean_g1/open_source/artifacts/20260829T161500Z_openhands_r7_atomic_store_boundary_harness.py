from dataclasses import dataclass
import hashlib
import json


class Crash(Exception):
    pass


@dataclass
class Marker:
    generation: int
    expected_old_leaf: str | None
    new_leaf: str
    last_user_message_id: str | None
    snapshot_sha256: str


def canonical_snapshot(state: dict) -> str:
    return json.dumps(state, sort_keys=True, separators=(",", ":"))


class AtomicStore:
    """Source-equivalent store with explicit all-old/all-new snapshot writes."""

    atomic_snapshot_capable = True

    def __init__(self, initial: str):
        self.base = initial
        self.marker = None

    def write_marker(self, marker: Marker) -> None:
        self.marker = marker

    def write_base(self, payload: str) -> None:
        self.base = payload

    def clear_marker(self) -> None:
        self.marker = None


class TearingStore:
    """Valid abstract-FileStore-shaped negative control whose write can tear."""

    atomic_snapshot_capable = False

    def __init__(self, initial: str):
        self.base = initial
        self.marker = None

    def write_marker(self, marker: Marker) -> None:
        self.marker = marker

    def write_base(self, payload: str) -> None:
        self.base = payload[: max(1, len(payload) // 2)]
        raise Crash("torn write")

    def clear_marker(self) -> None:
        self.marker = None


def prepare(old_state: dict, generation: int, new_leaf: str, last_user: str):
    final_state = dict(old_state)
    final_state["leaf_event_id"] = new_leaf
    final_state["last_user_message_id"] = last_user
    payload = canonical_snapshot(final_state)
    marker = Marker(
        generation=generation,
        expected_old_leaf=old_state.get("leaf_event_id"),
        new_leaf=new_leaf,
        last_user_message_id=last_user,
        snapshot_sha256=hashlib.sha256(payload.encode()).hexdigest(),
    )
    return marker, payload


def recover(store, current_generation: int, current_state: dict, marker: Marker, final_payload: str, crash_at: str | None = None) -> None:
    """R7 source-equivalent recovery gate.

    The important property is that all validation happens before any durable base
    mutation, and a generic store is rejected unless snapshot atomicity is an
    explicit capability. This models the current OpenHands FileStore contract,
    which promises write/read/list/delete/exists/path/lock but not atomic replace.
    """

    assert current_generation == marker.generation
    assert current_state.get("leaf_event_id") == marker.expected_old_leaf
    assert hashlib.sha256(final_payload.encode()).hexdigest() == marker.snapshot_sha256

    if not getattr(store, "atomic_snapshot_capable", False):
        raise RuntimeError("atomic snapshot capability required")

    if crash_at == "before_write":
        raise Crash("before write")

    store.write_base(final_payload)

    if crash_at == "after_write":
        raise Crash("after write")

    # A real helper would silently sync validated primitive bookkeeping in memory
    # here without invoking public __setattr__/autosave callbacks. Restart safety
    # comes from the durable snapshot, not that in-memory step.
    if crash_at == "before_cleanup":
        raise Crash("before cleanup")

    store.clear_marker()


def parse_base(store) -> dict:
    return json.loads(store.base)


def run() -> None:
    old = {"leaf_event_id": "e0", "last_user_message_id": "u0", "head_is_empty": False}
    marker, payload = prepare(old, 7, "e1", "e1")
    tests = []

    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 7, old, marker, payload, crash_at="before_write")
    except Crash:
        pass
    tests.append(("atomic_crash_before_write_old_survives", parse_base(s)["leaf_event_id"] == "e0"))

    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 7, old, marker, payload, crash_at="after_write")
    except Crash:
        pass
    tests.append(("atomic_crash_after_write_new_survives", parse_base(s)["leaf_event_id"] == "e1"))

    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 7, old, marker, payload, crash_at="before_cleanup")
    except Crash:
        pass
    tests.append(("atomic_crash_before_cleanup_idempotent_base", parse_base(s)["leaf_event_id"] == "e1" and s.marker is not None))

    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    recover(s, 7, old, marker, payload)
    tests.append(("atomic_success_marker_cleared", parse_base(s)["leaf_event_id"] == "e1" and s.marker is None))

    s = TearingStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 7, old, marker, payload)
        ok = False
    except RuntimeError:
        ok = parse_base(s)["leaf_event_id"] == "e0"
    tests.append(("non_atomic_store_rejected_before_write", ok))

    # Negative control: if the atomicity gate is omitted, an implementation that
    # still satisfies the abstract write() signature can leave corrupt JSON.
    s = TearingStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        s.write_base(payload)
    except Crash:
        pass
    try:
        json.loads(s.base)
        ok = False
    except json.JSONDecodeError:
        ok = True
    tests.append(("negative_generic_write_can_torn_snapshot", ok))

    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 8, old, marker, payload)
        ok = False
    except AssertionError:
        ok = parse_base(s)["leaf_event_id"] == "e0"
    tests.append(("generation_mismatch_fail_closed", ok))

    tampered = payload.replace('"e1"', '"e2"', 1)
    s = AtomicStore(canonical_snapshot(old))
    s.write_marker(marker)
    try:
        recover(s, 7, old, marker, tampered)
        ok = False
    except AssertionError:
        ok = parse_base(s)["leaf_event_id"] == "e0"
    tests.append(("snapshot_digest_mismatch_fail_closed", ok))

    for name, ok in tests:
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
    passed = sum(ok for _, ok in tests)
    print(f"TOTAL {passed}/{len(tests)}")
    assert passed == len(tests)


if __name__ == "__main__":
    run()
