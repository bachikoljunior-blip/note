"""Source-equivalent model for rmcp v3.1.4 task/router preflight boundaries.

Exact public-source pin:
  modelcontextprotocol/rust-sdk
  4a738b9dd99eaca418b614afa433a0cbdaf8d056

This is NOT code compiled against rmcp. It models ordering and authority boundaries
observed in the pinned source so counterexamples remain executable and reviewable.
"""

from dataclasses import dataclass, field
import uuid


class Rejected(Exception):
    pass


@dataclass
class Ctx:
    supports_tasks: bool = True
    policy_allows: bool = True
    request_state_valid: bool = True


@dataclass
class Request:
    name: str
    a: object = 1
    b: object = 2
    wants_preflight: bool = False


@dataclass
class StockTaskManager:
    tasks: dict[str, tuple[int, int]] = field(default_factory=dict)

    def spawn(self, a: int, b: int) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = (a, b)
        return task_id


@dataclass
class Router:
    disabled: set[str] = field(default_factory=set)

    def call(self, req: Request, ctx: Ctx, manager: StockTaskManager):
        if req.name in self.disabled:
            raise Rejected("tool not found")
        if req.name != "slow_sum":
            raise Rejected("tool not found")
        if not isinstance(req.a, int) or not isinstance(req.b, int):
            raise Rejected("invalid params")
        return registered_task_handler(req, ctx, manager)


def registered_task_handler(req: Request, ctx: Ctx, manager: StockTaskManager):
    # Safer ordering: standard router/extraction first, then all
    # pre-materialization gates inside the registered handler.
    if not ctx.supports_tasks:
        raise Rejected("tasks capability missing")
    if req.wants_preflight:
        return ("input_required", "signed-request-state")
    if not ctx.request_state_valid:
        raise Rejected("invalid request state")
    if not ctx.policy_allows:
        raise Rejected("policy denied")
    return ("task", manager.spawn(req.a, req.b))


def bundled_direct_branch(req: Request, ctx: Ctx, router: Router, manager: StockTaskManager):
    # Mirrors the important ordering from bundled TaskDemo: task-capable
    # branch occurs before ToolRouter.call().
    if req.name == "slow_sum" and ctx.supports_tasks:
        if not isinstance(req.a, int) or not isinstance(req.b, int):
            raise Rejected("invalid params")
        return ("task", manager.spawn(req.a, req.b))
    return router.call(req, ctx, manager)


def buggy_custom_handler_then_generic_guard(req: Request, ctx: Ctx, manager: StockTaskManager):
    # Models framework-level capability validation that occurs only after a
    # custom call_tool handler has returned a task response.
    response = ("task", manager.spawn(int(req.a), int(req.b)))
    if response[0] == "task" and not ctx.supports_tasks:
        raise Rejected("generic post-handler capability guard")
    return response


def external_effect(counter: list[int]):
    counter[0] += 1


def expect_rejected(fn):
    try:
        fn()
    except Rejected:
        return
    raise AssertionError("expected rejection")


def run():
    passed = 0

    # 1. Counterexample: direct task branch can bypass router-disabled state.
    m = StockTaskManager(); r = Router(disabled={"slow_sum"})
    assert bundled_direct_branch(Request("slow_sum"), Ctx(), r, m)[0] == "task" and len(m.tasks) == 1
    passed += 1

    # 2. Router-first path blocks disabled tool before spawn.
    m = StockTaskManager(); r = Router(disabled={"slow_sum"})
    expect_rejected(lambda: r.call(Request("slow_sum"), Ctx(), m)); assert not m.tasks
    passed += 1

    # 3. Standard extraction rejects malformed args before spawn.
    m = StockTaskManager(); r = Router()
    expect_rejected(lambda: r.call(Request("slow_sum", a="x"), Ctx(), m)); assert not m.tasks
    passed += 1

    # 4. Registered handler can enforce task capability before materialization.
    m = StockTaskManager(); r = Router()
    expect_rejected(lambda: r.call(Request("slow_sum"), Ctx(supports_tasks=False), m)); assert not m.tasks
    passed += 1

    # 5. Framework post-handler guard is too late to undo a buggy spawn.
    m = StockTaskManager()
    expect_rejected(lambda: buggy_custom_handler_then_generic_guard(Request("slow_sum"), Ctx(supports_tasks=False), m))
    assert len(m.tasks) == 1
    passed += 1

    # 6. Side-effect-free preflight returns before spawn.
    m = StockTaskManager(); r = Router()
    assert r.call(Request("slow_sum", wants_preflight=True), Ctx(), m)[0] == "input_required" and not m.tasks
    passed += 1

    # 7. Invalid continuation state rejects before spawn.
    m = StockTaskManager(); r = Router()
    expect_rejected(lambda: r.call(Request("slow_sum"), Ctx(request_state_valid=False), m)); assert not m.tasks
    passed += 1

    # 8. Current policy recheck rejects before spawn.
    m = StockTaskManager(); r = Router()
    expect_rejected(lambda: r.call(Request("slow_sum"), Ctx(policy_allows=False), m)); assert not m.tasks
    passed += 1

    # 9. Valid continuation reaches one task creation.
    m = StockTaskManager(); r = Router()
    assert r.call(Request("slow_sum"), Ctx(), m)[0] == "task" and len(m.tasks) == 1
    passed += 1

    # 10. Lost result + blind retry on stock fresh-ID manager duplicates task creation.
    m = StockTaskManager(); r = Router()
    first = r.call(Request("slow_sum"), Ctx(), m)[1]
    second = r.call(Request("slow_sum"), Ctx(), m)[1]
    assert first != second and len(m.tasks) == 2
    passed += 1

    # 11. In-memory stock manager state is lost across server restart.
    m1 = StockTaskManager(); r = Router(); tid = r.call(Request("slow_sum"), Ctx(), m1)[1]
    m2 = StockTaskManager(); assert tid not in m2.tasks
    passed += 1

    # 12. Task attempt fencing is separate from external-effect idempotency.
    effects = [0]; external_effect(effects); external_effect(effects); assert effects[0] == 2
    passed += 1

    assert passed == 12
    print("12/12 PASS")


if __name__ == "__main__":
    run()
