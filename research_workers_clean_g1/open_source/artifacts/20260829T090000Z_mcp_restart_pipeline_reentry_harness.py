#!/usr/bin/env python3
"""Source-equivalent model of MCP C# Tasks restart/re-entry boundary.

Exact SDK target:
- modelcontextprotocol/csharp-sdk v2.2.0
- commit 6fa3825973949a9c4f0cd8af344e15a8db09dc35

The model separates:
1) initial Tasks wrapper, which creates a durable task then captures `next`;
2) ordinary policy filters + primitive tool execution;
3) process restart, where the captured delegate no longer exists.

It demonstrates why direct primitive replay is not equivalent to pipeline replay,
why a fresh normal CallTool creates a new task, and what a safe supported
"resume existing task" seam would need to do.
"""

from dataclasses import dataclass


@dataclass
class Task:
    task_id: str
    status: str = "working"
    generation: int = 0
    intent: str = "pay:42"
    result: str | None = None


@dataclass
class State:
    tasks: dict[str, Task]
    scheduled: list[str]
    effects: list[tuple[str, int]]
    policy_allowed: bool = True
    next_id: int = 1


def create_task(s: State) -> Task:
    tid = f"t{s.next_id}"
    s.next_id += 1
    task = Task(tid)
    s.tasks[tid] = task
    return task


def ordinary_pipeline(s: State, task: Task, generation: int) -> str:
    # Represents current CallToolFilters / current authorization.
    if not s.policy_allowed:
        return "blocked"
    # Effect boundary is modeled with task+generation as identity.
    s.effects.append((task.task_id, generation))
    return "ok"


def initial_with_tasks(s: State, *, crash_before_schedule: bool = False) -> str:
    task = create_task(s)  # durable CreateTaskAsync must complete first
    if crash_before_schedule:
        return task.task_id
    s.scheduled.append(task.task_id)
    outcome = ordinary_pipeline(s, task, task.generation)
    task.status = "completed" if outcome == "ok" else "failed"
    task.result = outcome
    return task.task_id


def direct_primitive_replay(s: State, task_id: str) -> str:
    # Models calling McpServerTool.InvokeAsync directly: no ordinary policy filters.
    task = s.tasks[task_id]
    s.effects.append((task.task_id, task.generation))
    return "ok"


def fresh_normal_retry(s: State) -> str:
    # Re-entering the public normal request path hits WithTasks again -> new unique task.
    return initial_with_tasks(s)


def resume_existing_supported_seam(
    s: State, task_id: str, expected_generation: int
) -> str:
    """Hypothetical missing seam: skip creation only, rerun ordinary pipeline."""
    task = s.tasks[task_id]
    if task.status != "working" or task.generation != expected_generation:
        return "stale"
    outcome = ordinary_pipeline(s, task, expected_generation)
    task.status = "completed" if outcome == "ok" else "failed"
    task.result = outcome
    return outcome


def claim_generation(s: State, task_id: str) -> int:
    task = s.tasks[task_id]
    task.generation += 1
    return task.generation


def generation_cas_complete(
    s: State, task_id: str, generation: int, result: str
) -> bool:
    task = s.tasks[task_id]
    if task.generation != generation or task.status != "working":
        return False
    task.status = "completed"
    task.result = result
    return True


def run() -> list[str]:
    passed: list[str] = []

    s = State({}, [], [])
    task_id = initial_with_tasks(s)
    assert task_id == "t1" and s.effects == [("t1", 0)]
    assert s.tasks[task_id].status == "completed"
    passed.append("initial_task_runs_ordinary_policy_pipeline")

    s = State({}, [], [])
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    assert task_id == "t1" and s.tasks[task_id].status == "working"
    assert not s.scheduled and not s.effects
    passed.append("durable_create_before_schedule_crash_leaves_working_task")

    s = State({}, [], [], policy_allowed=False)
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    direct_primitive_replay(s, task_id)
    assert s.effects == [("t1", 0)]
    passed.append("direct_primitive_replay_bypasses_revoked_policy_negative")

    s = State({}, [], [])
    old_task = initial_with_tasks(s, crash_before_schedule=True)
    new_task = fresh_normal_retry(s)
    assert old_task == "t1" and new_task == "t2"
    assert set(s.tasks) == {"t1", "t2"} and ("t2", 0) in s.effects
    passed.append("fresh_normal_retry_creates_new_task_not_existing_resume")

    s = State({}, [], [], policy_allowed=False)
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    outcome = resume_existing_supported_seam(s, task_id, 0)
    assert outcome == "blocked" and not s.effects
    assert s.tasks[task_id].status == "failed"
    passed.append("hypothetical_resume_existing_reruns_current_policy")

    s = State({}, [], [])
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    generation = claim_generation(s, task_id)
    assert generation == 1
    outcome = resume_existing_supported_seam(s, task_id, generation)
    assert outcome == "ok" and s.effects == [(task_id, 1)]
    passed.append("claimed_existing_task_runs_same_task_once")

    s = State({}, [], [])
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    first_generation = claim_generation(s, task_id)
    second_generation = claim_generation(s, task_id)
    assert not generation_cas_complete(s, task_id, first_generation, "old")
    assert generation_cas_complete(s, task_id, second_generation, "new")
    passed.append("stale_generation_terminal_write_rejected")

    # Generation alone cannot retract an external effect already in flight.
    s = State({}, [], [])
    task_id = initial_with_tasks(s, crash_before_schedule=True)
    first_generation = claim_generation(s, task_id)
    s.effects.append((task_id, first_generation))
    second_generation = claim_generation(s, task_id)
    s.effects.append((task_id, second_generation))
    assert s.effects == [(task_id, first_generation), (task_id, second_generation)]
    passed.append("attempt_generation_alone_does_not_deduplicate_external_effect")

    return passed


if __name__ == "__main__":
    passed = run()
    print(f"PASS {len(passed)}/{len(passed)}")
    for name in passed:
        print(name)
