#!/usr/bin/env python3
"""Source-equivalent model for an OpenHands R7 recovery commit seam.

This models a startup-only helper after pure marker-chain validation:
(1) construct the final base snapshot without mutating public state,
(2) write BASE_STATE exactly once under the existing write guard,
(3) synchronize trusted primitive bookkeeping into memory without __setattr__,
(4) clear recovery markers only after the base snapshot is durable.

It intentionally does not claim an upstream patch was applied or executed.
"""
from dataclasses import dataclass, field
from copy import deepcopy

class Crash(RuntimeError):
    pass

class ValidationError(RuntimeError):
    pass

class WriteError(RuntimeError):
    pass

@dataclass(frozen=True)
class Marker:
    generation: int
    expected_old_head: str | None
    final_head: str
    final_last_user_message_id: str | None

@dataclass
class ModelState:
    public: dict = field(default_factory=lambda: {
        "leaf_event_id": "old",
        "head_is_empty": False,
        "last_user_message_id": "u0",
        "execution_status": "idle",
    })
    persisted: dict = field(default_factory=lambda: {
        "leaf_event_id": "old",
        "head_is_empty": False,
        "last_user_message_id": "u0",
        "execution_status": "idle",
    })
    marker: Marker | None = None
    generation: int = 7
    autosave_writes: int = 0
    callbacks: int = 0
    guarded_snapshot_writes: int = 0

    def ordinary_setattr(self, name, value):
        self.public[name] = value
        # Mirrors the relevant source behavior: public assignment autosaves when
        # not inside the save-depth context and may emit callbacks for non-HEAD fields.
        self.persisted = deepcopy(self.public)
        self.autosave_writes += 1
        if name not in ("leaf_event_id", "head_is_empty"):
            self.callbacks += 1

    def validate_plan(self, marker: Marker) -> dict:
        if marker.generation != self.generation:
            raise ValidationError("generation mismatch")
        if self.public["leaf_event_id"] != marker.expected_old_head:
            # Idempotent recovery after the snapshot already committed is handled
            # by a separate exact-new-state check below.
            if self.public["leaf_event_id"] == marker.final_head:
                return {
                    **self.public,
                    "leaf_event_id": marker.final_head,
                    "head_is_empty": False,
                    "last_user_message_id": marker.final_last_user_message_id,
                }
            raise ValidationError("expected old HEAD mismatch")
        return {
            **self.public,
            "leaf_event_id": marker.final_head,
            "head_is_empty": False,
            "last_user_message_id": marker.final_last_user_message_id,
        }

    def commit_recovery(self, *, crash_at: str | None = None, fail_write: bool = False):
        marker = self.marker
        if marker is None:
            raise ValidationError("no recovery marker")

        # Pure planning: no public mutation before the full plan validates.
        target = self.validate_plan(marker)
        before_public = deepcopy(self.public)
        if crash_at == "before_write":
            assert self.public == before_public
            raise Crash("before_write")

        # Dedicated one-snapshot persistence path; conceptually uses the existing
        # write guard but serializes `target`, not `self` after incremental mutation.
        if fail_write:
            raise WriteError("base snapshot write failed")
        self.persisted = deepcopy(target)
        self.guarded_snapshot_writes += 1
        if crash_at == "after_write_before_memory":
            raise Crash("after_write_before_memory")

        # One bypass update for already-validated primitive recovery bookkeeping.
        # In upstream this would avoid ConversationState.__setattr__, hence no
        # intermediate autosave and no state-change callback emission.
        self.public.update({
            "leaf_event_id": target["leaf_event_id"],
            "head_is_empty": target["head_is_empty"],
            "last_user_message_id": target["last_user_message_id"],
        })
        if crash_at == "after_memory_before_cleanup":
            raise Crash("after_memory_before_cleanup")

        self.marker = None


def fresh_with_marker(**kwargs):
    s = ModelState(**kwargs)
    s.marker = Marker(7, "old", "e2", "e2")
    return s


def test_pure_validation_before_mutation():
    s = fresh_with_marker()
    before = deepcopy(s.public)
    try:
        s.commit_recovery(crash_at="before_write")
    except Crash:
        pass
    assert s.public == before and s.persisted["leaf_event_id"] == "old"


def test_exactly_one_snapshot_write_and_no_autosave_callback():
    s = fresh_with_marker()
    s.commit_recovery()
    assert s.persisted["leaf_event_id"] == "e2"
    assert s.public["leaf_event_id"] == "e2"
    assert s.guarded_snapshot_writes == 1
    assert s.autosave_writes == 0 and s.callbacks == 0


def test_write_failure_does_not_mutate_memory_or_clear_marker():
    s = fresh_with_marker()
    before = deepcopy(s.public)
    try:
        s.commit_recovery(fail_write=True)
    except WriteError:
        pass
    assert s.public == before and s.marker is not None
    assert s.guarded_snapshot_writes == 0


def test_crash_after_write_recovers_from_persisted_snapshot():
    s = fresh_with_marker()
    try:
        s.commit_recovery(crash_at="after_write_before_memory")
    except Crash:
        pass
    assert s.persisted["leaf_event_id"] == "e2" and s.marker is not None
    # Source-equivalent restart loads the committed base snapshot.
    restarted = ModelState(public=deepcopy(s.persisted), persisted=deepcopy(s.persisted), marker=s.marker)
    restarted.commit_recovery()
    assert restarted.public["leaf_event_id"] == "e2" and restarted.marker is None


def test_crash_after_memory_before_cleanup_is_idempotent_on_restart():
    s = fresh_with_marker()
    try:
        s.commit_recovery(crash_at="after_memory_before_cleanup")
    except Crash:
        pass
    assert s.persisted["leaf_event_id"] == "e2" and s.marker is not None
    restarted = ModelState(public=deepcopy(s.persisted), persisted=deepcopy(s.persisted), marker=s.marker)
    restarted.commit_recovery()
    assert restarted.marker is None and restarted.public["leaf_event_id"] == "e2"


def test_stale_expected_head_fails_closed():
    s = fresh_with_marker()
    s.public["leaf_event_id"] = "fork-head"
    s.persisted["leaf_event_id"] = "fork-head"
    try:
        s.commit_recovery()
    except ValidationError:
        pass
    else:
        raise AssertionError("stale marker was accepted")
    assert s.persisted["leaf_event_id"] == "fork-head" and s.marker is not None


def test_generation_mismatch_fails_closed():
    s = fresh_with_marker()
    s.generation = 8
    try:
        s.commit_recovery()
    except ValidationError:
        pass
    else:
        raise AssertionError("old generation marker was accepted")
    assert s.persisted["leaf_event_id"] == "old"


def test_markerless_orphan_not_adopted():
    s = ModelState()
    try:
        s.commit_recovery()
    except ValidationError:
        pass
    else:
        raise AssertionError("markerless recovery occurred")
    assert s.public["leaf_event_id"] == "old"


def test_ordinary_setattr_demonstrates_intermediate_write_hazard():
    s = fresh_with_marker()
    s.ordinary_setattr("leaf_event_id", "e2")
    assert s.autosave_writes == 1 and s.persisted["leaf_event_id"] == "e2"
    # A later field can still be stale if the process dies here.
    assert s.persisted["last_user_message_id"] == "u0"


def test_recovery_updates_last_user_without_callback_event():
    s = fresh_with_marker()
    s.commit_recovery()
    assert s.public["last_user_message_id"] == "e2"
    assert s.callbacks == 0


def test_non_recovery_public_fields_preserved():
    s = fresh_with_marker()
    s.public["execution_status"] = "paused"
    s.persisted["execution_status"] = "paused"
    s.commit_recovery()
    assert s.persisted["execution_status"] == "paused"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"PASS {len(tests)}/{len(tests)}")

if __name__ == "__main__":
    main()
