# Phase-1 multi_agent checkpoint — zero-global-write finite-inflight witness (Part 43)

## Frozen semantic tuple

- frozen authority commit: `302327074272033f246c5d8f555df61004e3802f`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- presemantic liveness witness: `automation_control/receipts/multi_agent/20260830T043701+0900-presemantic-c26-c8-7b31f2.json`
- predecessor: `PHASE1_TICKET_RECOVERY_20260830_013535_PART42.md`

Part 42 proved that a cooperative wide REQUESTED ticket only gets a finite starvation bound when the amount of already-admitted work is itself bounded by protocol; configured role count alone was not such a proof. This leaf asks whether the recurring-Chat pool can create that bound without putting every local admission through one global root write.

Executable model: `research_workers_clean_g1/multi_agent/phase1_zero_write_inflight_20260830_part43.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_zero_write_inflight_20260830_part43.json`

The finite lattice contains `1,728` scenario shapes and `10,368` strategy evaluations across role counts 1/3/11, same-role overlap 1/2/3, scheduler replay, crash-before-release, takeover/no-takeover, late release, slot delete/recreate, repository interruption before admission or after admission response loss, and a wide-ticket scan before or after pre-ticket admission slips. Counts are mechanism counts, not deployment probabilities.

## Public-source observation — current Scheduled Tasks docs do not provide the needed mutual-exclusion proof

The current OpenAI Scheduled Tasks help page found in this run documents active-task limits and says tasks cannot run more than once per hour, and also says plan usage limits apply to tasks. I did **not** find on that page a guarantee that one recurring task can never have overlapping in-flight invocations, nor a pool-wide `max_inflight` mutual-exclusion contract.

Source:
- https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt

Therefore this leaf does not use configured role count, active-task count, or run frequency as a correctness bound. Those are scheduling/product limits, not a documented one-authoritative-operation-per-role protocol.

## Result 1 — role count alone remains an invalid bound

The `scheduler_role_count_only` negative control assumes `max_inflight = number_of_roles` without a repository admission discipline.

When transport is available and same-role overlap is 2 or 3, the assumption is violated in **768/768** tested cases. Scheduler replay creates duplicate logical admission in **576/576** replay cases. If an admission response is lost and no durable admission record exists, all **576** response-loss cases are ambiguous.

Across the full lattice this baseline has 960 bound violations and zero scenarios with a protocol-proved finite bound.

This does not prove that the runtime *does* overlap every role. It proves only that role count cannot be promoted to a finite-inflight theorem without a mutual-exclusion mechanism or a documented runtime guarantee.

## Result 2 — scanning dynamic PREPARED records is a snapshot, not a structural bound

`dynamic_prepared_scan` gives every distinct operation its own deterministic PREPARED record, so replay of the same operation ID can be reconciled. But a wide owner that writes REQUESTED and then scans currently visible PREPARED records can still miss invocations that read the old ticket state before REQUESTED and create PREPARED afterward.

In all **576/576** `scan_before_slip` cases with transport available, at least one new PREPARED admission can appear after the scan. The largest finite test instance has 33 such unseen distinct operations (`11 roles * 3 overlapping invocations`).

Because distinct same-role operations are not bounded by this protocol, the scan cannot provide a generic finite `max_inflight`. It is useful state reconstruction, not a liveness bound.

## Result 3 — one current admission slot per role turns role count into a protocol bound

The positive candidate uses one deterministic current slot per role:

`IDLE -> PREPARED(operation_id, slot_incarnation, epoch) -> RELEASED`

All invocations for a role contend on that one current file/record. Only the slot head may be authoritative PREPARED. A same-role loser fails closed or joins a bounded non-authoritative queue; it does not create a second authoritative PREPARED operation.

GitHub's repository Contents API requires the blob `sha` of the file being replaced for updates and exposes `409 Conflict`; that is the storage primitive used by the model for the current-slot CAS:
- https://docs.github.com/en/rest/repos/contents

Under this discipline, the authoritative in-flight bound is **the number of current role slots**, not because the scheduler guarantees one invocation per role, but because the protocol only permits one authoritative PREPARED head per role.

`fixed_role_slot_incarnation` proves that structural bound in **1,728/1,728** modeled scenarios with zero bound violations and zero duplicate logical admissions. If a wide-ticket scan happens before all pre-ticket readers finish their slot CAS, the scan may still miss admissions, but the number of unseen slips never exceeds the structural role-slot bound in **576/576** such cases; the maximum is 11 in the 11-slot slice.

This is the missing Part-42 liveness contract. A wide ticket can use `max_inflight = current_slot_count` **only after** every authoritative local operation is required to acquire exactly one of those current slots.

## Result 4 — this removes the global hotspot, not every admission write

The result is intentionally narrower than “write-free admission.”

- `fixed_role_slot_incarnation`: zero global-root write per local admission, but one local role-slot CAS per admission; 14,400 local-slot touches across the full lattice.
- `global_root_counter`: zero unseen post-ticket admissions because REQUESTED and every admission share one root authority, but it causes 25,488 global-hotspot touches in the same lattice.

So the accepted property is **zero additional global admission write for the finite-inflight witness**, not zero repository mutation. The local PREPARED/slot transition is still a write and remains the authority fence.

A bounded queue variant with capacity two keeps only the slot head authoritative and therefore preserves the same authoritative bound. Extra queued intents are non-authoritative and overflow fails closed.

## Result 5 — slot identity must be incarnation-sensitive

A logical-name-only fixed slot is vulnerable to delete/recreate ABA. In the exact slice `crash -> takeover -> slot delete/recreate -> late old release`, the name-only control is **72/72 stale-release unsafe**.

The strong slot includes a new `slot_incarnation` in the current bytes and uses a monotonic epoch/takeover transition. A late old release therefore cannot match the recreated current slot in the tested no-complete-rewind scope. Response loss after a winning slot CAS is reconciled by reading the current slot's `operation_id/incarnation/epoch` rather than blindly retrying.

This still inherits the earlier complete-rewind boundary: if the repository and every incarnation/retirement witness are all restored to an older identical state, this repository-local mechanism has no external anti-rollback fact.

## Result 6 — crash safety and finite liveness remain separate

A crash before release leaves the slot occupied. The finite authoritative-inflight bound is still preserved, but the wide operation can remain excluded when no later invocation performs a fenced takeover. The model records 432 such crash/no-takeover cases for each strong slot/root strategy.

Therefore the Part-43 slot discipline supplies the missing finite **count** bound, while Part 42's `REQUESTED -> RECOVERING -> APPLIED/RELEASED` epoch transitions and explicit recovery/retry budgets still supply the finite **time/progress** argument.

Wall-clock expiry alone still does not release a slot.

## Rate-limit / quota-zero assessment

GitHub documents REST rate limits and instructs clients to stop and retry later on 403/429 according to reset/retry guidance:
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

The protocol treats those limits as interruption, not compute:
- interruption before slot CAS: no authority is admitted;
- response loss after slot CAS: read current slot and reconcile operation identity;
- later scheduled invocation may perform fenced takeover/recovery.

No GitHub Actions, Codespaces, artifact/LFS/package storage, cloud compute, external model/API credit, richer-mode arbitration, protected-primary execution, or manual-user step is added. Incremental monetary cost is zero. The mechanism adds no optional monthly/trial/paid quota dependency. Current OpenAI public docs do say plan usage limits apply to Scheduled Tasks, so task-plan limits are **not** used as correctness evidence or as the finite-inflight witness.

## Exact accepted scope

Accepted only under all of these conditions:

1. the current role membership set is finite and every member has exactly one current admission slot;
2. every authoritative local operation must acquire its role's current slot before PREPARED/effect publication;
3. same-role overlapping invocations cannot bypass the slot;
4. slot identity is incarnation-sensitive and takeover/release is epoch-fenced;
5. a wide REQUESTED ticket is observed by cooperative new admissions, while pre-ticket slips are bounded structurally by the slot set;
6. response loss is reconciled from current state;
7. repository transport interruptions fail closed;
8. no complete rollback of every authority/witness state occurs.

Still unresolved:
- how the wide ticket safely binds a **changing role-membership set** without a global root;
- new role/slot creation after REQUESTED as a phantom admission domain;
- noncooperative/legacy workers that can publish without a slot;
- complete authority-domain rewind;
- direct fixed-path consumers and arbitrary external sinks from earlier leaves.

## Exact continuation

Next Phase-1 leaf: **role-membership epoch and phantom-role admission under pool reconfiguration**.

Enumerate:
- role add/remove/re-add;
- role rename;
- slot namespace migration;
- new role appearing after wide REQUESTED;
- disabled-but-stale slot;
- slot creation response loss;
- role-slot delete/recreate;
- control-revision change after semantic freeze;
- overlapping invocation during membership transition;
- rate-limit interruption during membership update.

Compare:
1. fixed 11-slot snapshot;
2. membership-epoch + deterministic slot set;
3. append-only role-incarnation registry with current membership epoch;
4. root membership CAS;
5. global-root admission counter baseline.

Target: either derive a zero-global-per-local-admission proof that a wide ticket can bind a finite current membership/slot set with no post-ticket phantom roles, or isolate the exact reason membership change forces a shared authority transition.
