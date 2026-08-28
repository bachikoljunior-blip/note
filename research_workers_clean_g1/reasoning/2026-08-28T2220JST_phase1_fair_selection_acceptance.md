# Phase 1 follow-up — deterministic repeated-run fairness

Status: role-local Phase-1 continuation under frozen semantic tuple `4632516483a5fb873c0ebc4b1709cb8505a9271a` / control rev 16 / reasoning config rev 6. This follows the causal-DAG latest-state checkpoint. No post-freeze repository semantics were adopted.

## Result

The earlier stable-priority greedy maximal-independent-set selector is **safe and maximal per invocation but not live across invocations**. If a higher-ranked conflicting action is recreated every run, a lower-ranked continuously eligible action can be starved forever.

The repair is to separate immutable **hard precedence** from durable **fairness age**:

`order(a) = (hard_priority_class(a), -wait_credit[fairness_key(a)], stable_action_key(a))`

Within one hard priority class, run the same greedy conflict-graph independent-set selector in this order. After a successful selection epoch:

- selected continuously eligible key: `wait_credit = 0`;
- eligible but unselected key: `wait_credit += 1`;
- newly eligible key: `wait_credit = 0`;
- key that becomes ineligible: remove/reset its continuous-eligibility age;
- the fairness epoch advances from durable checkpoint state, never from wall-clock time.

`fairness_key` must identify the same logical recurring action across invocations, for example a canonical `(task_key, action_class, exclusive_scope)` whose semantic equivalence is verified. A transient invocation id is not a valid fairness identity because it would reset waiting age every run.

Hard precedence remains outside the fairness layer. Therefore the liveness claim applies only to continuously eligible actions in the **same hard class**. A deliberately higher class may preempt a lower class indefinitely; that is explicit policy, not hidden starvation. In the current Phase-1 overlay, the preserved pre-Phase-1 base continuation is not an eligible fairness competitor at all.

## Existing-solution audit

Linux CFS's classic design uses a per-task virtual runtime and prefers the runnable task that has received less CPU time relative to the ideal share. That supports the generic architectural pattern “persist service history; do not use wall-clock arrival order as fairness.” Source: https://docs.kernel.org/6.10/scheduler/sched-design-CFS.html

Deficit Round Robin keeps per-flow deficit state so previously underserved flows retain service credit across rounds; the original work emphasizes fair throughput at low scheduler complexity. This independently supports durable deficit/credit rather than fixed repeated priority. Source: https://openscholarship.wustl.edu/cse_research/339/

The present action scheduler differs from CPU/packet scheduling because one selected action can conflict with several actions simultaneously. Thus the service-history idea transfers, but the conflict-safe action set is still computed by the explicit independent-set rule.

## Proof obligations

### FQ1 conflict safety is unchanged
Fairness changes only vertex order. The greedy insertion condition is unchanged: an action is selected only if it has no conflict edge to an already selected action. Therefore every round remains an independent set.

### FQ2 per-round maximality is unchanged
Every rejected action was rejected when an already selected conflicting action preceded it; selected actions are never removed later in the round. Therefore every unselected eligible action has a selected conflict witness.

### FQ3 deterministic ordering
For equal frozen evidence, `hard_priority_class`, durable integer credit, and stable canonical key define a total deterministic order. Wall-clock race order is not an input.

### FQ4 bounded first service for a fixed cohort
Assume a fixed finite conflict graph of `n` actions, one hard class, all continuously eligible, and a new fairness epoch starting with credit zero. At any round with an unserved action, every never-served action has strictly greater credit than every action served in an earlier round, except possible same-round initial ties resolved by stable key. Hence at least one never-served action is selected each round. Every action is first-served within at most `n` rounds.

### FQ5 repeated-service starvation freedom for a fixed graph
After action `v` is served, any neighbor that later blocks `v` is itself selected and resets to zero. Such a neighbor cannot outrank the still-waiting `v` a second time before `v` is served again. Therefore each neighbor can block `v` at most once between two services of `v`, giving the fixed-graph recurrence bound `service_gap(v) <= degree(v) + 1` rounds.

This bound does **not** automatically extend to changing hard priorities, changing conflict graphs, changing semantic identities, repeated fairness resets, or unbounded creation of previously high-credit actions. Those cases require separate assumptions/tests.

## Finite property model

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2220JST_phase1_fair_selection_properties.py`.

The model exhaustively checks every undirected conflict graph for `n <= 6`:

- **33,867 fixed conflict graphs**;
- **808,052 selection rounds** across four `n`-round service windows per graph;
- every selected set is conflict-free;
- every selected set is maximal;
- every vertex starting a fairness epoch at credit zero is first-served by round `n`;
- every observed repeat-service gap is at most `degree(v)+1`.

The worst observed first-service round and repeat-service gap are both 6, attained by a six-vertex clique. No checked invariant failed. This is finite model evidence for the stated fixed-graph scope, not an implementation proof for a dynamic distributed scheduler.

## Stale/missing fairness metadata

Fairness metadata is liveness state, not authority state. Corruption or loss must never weaken the conflict predicate, ownership CAS, or fencing rules.

Fail-closed recovery:
1. reconstruct the action set and hard precedence from semantic source-of-truth checkpoints;
2. if fairness metadata has a valid digest/predecessor chain, resume it;
3. if missing/inconsistent, start a new deterministic `fairness_epoch` with credit zero for the currently eligible same-class cohort and record `FAIRNESS_EPOCH_RESET(reason)`;
4. do not invent age from timestamps or filenames;
5. after reset, claim only the bounded-first-service guarantee from that reset onward;
6. repeated resets invalidate starvation-freedom claims and must be surfaced as a liveness failure signal.

This preserves safety under damaged scheduling metadata while making the liveness loss explicit.

## Dynamic-arrival scope

A new same-class action enters with zero credit, so it cannot outrank an already waiting action with positive credit merely by arriving later. However, a general dynamic-graph liveness theorem requires stable canonical fairness identities and a finite/bounded set of conflicting incumbents. The current proof intentionally stops at the fixed continuously eligible cohort plus the simple no-credit-injection rule for new arrivals.

## Current Phase-1 architecture coverage

The generic reasoning architecture now has explicit contracts and finite model checks for:
- frozen semantic control and clean role boundary;
- causal latest-state reconstruction despite stale `LATEST`;
- conflict-safe/maximal action selection;
- repeated-run fixed-cohort liveness within a hard priority class;
- direct-solution-first before blocker decomposition;
- transversal alternatives after branch overrun;
- crash-safe immutable checkpoint publication and guarded pointer promotion;
- generation-CAS/fencing exclusive handoff;
- handoff crash/replay idempotency;
- explicit fail-closed negative paths.

Global cross-role ownership/exclusivity remains unclaimed because this clean role has no authorized shared claim surface.

## Exact next Phase-1 action

Audit the remaining **dynamic-selection boundary**: action arrivals/departures, evolving conflict edges, fairness-key migration, and hard-priority changes. Define the minimal conditions under which the fixed-cohort liveness result can be extended, and otherwise require an explicit `LIVENESS_UNPROVEN_DYNAMIC_SET` status rather than silently claiming fairness. Then consolidate the Phase-1 reasoning proof obligations into an inspectable acceptance table mapping each invariant to positive test, counterexample, fail-closed response, and recovery evidence.

Keep `2026-08-28T1807JST_budget_conditioned_joint_value.md` as base restoration metadata only while Phase 1 remains active.

Termination for this leaf: repeated-run fixed-cohort selection liveness completed; Phase-1 parent remains open with the dynamic-selection/acceptance-table leaf above.
