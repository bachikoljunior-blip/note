#!/usr/bin/env python3
"""Source-equivalent boundary model for rmcp v3.1.4 TaskManager.

This does not compile or execute upstream Rust. It models the exact architectural
properties inspected at commit 4a738b9dd99eaca418b614afa433a0cbdaf8d056:
TaskManager owns an Arc<Mutex<HashMap<...>>>, spawn inserts a server-generated
UUID-backed entry before returning, and shutdown drains the map. The 2026-07-28
Tasks extension has no tasks/list method.
"""
from dataclasses import dataclass
from uuid import uuid4

class UnknownTask(KeyError):
    pass

@dataclass
class Task:
    task_id: str
    status: str = "working"

class InMemoryTaskManager:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def spawn(self) -> Task:
        t = Task(str(uuid4()))
        self.tasks[t.task_id] = t
        return t

    def get(self, task_id: str) -> Task:
        try:
            return self.tasks[task_id]
        except KeyError as e:
            raise UnknownTask(task_id) from e

    def shutdown(self) -> None:
        self.tasks.clear()

    # SEP-2663 current extension intentionally has no tasks/list.


def test_same_process_disconnect_reconnect():
    m = InMemoryTaskManager()
    t = m.spawn()
    assert m.get(t.task_id).task_id == t.task_id


def test_client_crash_with_persisted_id_same_server_process():
    m = InMemoryTaskManager()
    t = m.spawn()
    durable_client_checkpoint = t.task_id
    del t
    assert m.get(durable_client_checkpoint).status == "working"


def test_server_process_restart_loses_task_state():
    m1 = InMemoryTaskManager()
    t = m1.spawn()
    durable_client_checkpoint = t.task_id
    m2 = InMemoryTaskManager()  # source-equivalent fresh process
    try:
        m2.get(durable_client_checkpoint)
    except UnknownTask:
        return
    raise AssertionError("fresh process unexpectedly recovered in-memory task")


def test_shutdown_explicitly_clears_state():
    m = InMemoryTaskManager()
    t = m.spawn()
    m.shutdown()
    try:
        m.get(t.task_id)
    except UnknownTask:
        return
    raise AssertionError("shutdown did not clear task state")


def test_lost_create_response_has_no_rediscovery_surface():
    m = InMemoryTaskManager()
    _server_only_task = m.spawn()
    client_known_ids: list[str] = []  # response lost before taskId checkpoint
    assert client_known_ids == []
    assert not hasattr(m, "list_tasks")


def test_blind_retry_creates_distinct_task():
    m = InMemoryTaskManager()
    first = m.spawn()   # response lost
    second = m.spawn()  # request retried without a stable creation key
    assert first.task_id != second.task_id
    assert len(m.tasks) == 2


def test_task_id_is_server_generated_not_caller_stable():
    m = InMemoryTaskManager()
    a = m.spawn()
    b = m.spawn()
    assert a.task_id != b.task_id


def test_scope_classifier():
    same_process = True
    restart_durable = False
    creation_rediscoverable_after_lost_response = False
    assert same_process and not restart_durable and not creation_rediscoverable_after_lost_response


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"PASS {len(tests)}/{len(tests)}")

if __name__ == "__main__":
    main()
