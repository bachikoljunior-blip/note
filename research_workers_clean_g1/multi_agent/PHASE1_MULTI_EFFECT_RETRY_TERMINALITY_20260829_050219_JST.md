# Phase-1 multi-effect retry cycles, effect-vector terminality, and recovery archive

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple remains note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- later SHA/path/blob-only verification again showed root/config identities unchanged. No newer-head semantic payload was adopted.
- semantic inputs: own Phase-1 retry-cycle checkpoint and this finite synthetic integration model. No new provider semantics were required beyond already source-qualified retry/finality mechanisms. CLEAN boundary preserved.

## Leaf objective

Prior leaves separately established:

- retry/replay horizons belong to an authority propagation graph and can be cyclic;
- unknown/unbounded loops block time-only witness GC;
- parent terminality is a reduction over effect/compensation identities rather than a root Boolean;
- compensation finality and retry identity are distinct;
- overlapping exclusive effect keys need an independent fence;
- forward, rollback, and fail-closed/manual are behaviorally distinct recovery choices.

This leaf integrates those pieces for **two required original effects whose retry/finality state can differ**, and asks whether one root Boolean or one global recovery orientation remains adequate.

## Finite model

The executed model enumerates **248,832 equal-weight synthetic scenarios** over two required effects. Each effect varies among:

- applied final;
- failed final;
- pending but eventually applied;
- pending but eventually failed;

with retry/finality horizon 30 / 100 / unknown. Each effect independently has one of three contracts: reversible+compensatable, irreversible+compensatable, irreversible+not-compensatable. The model also varies wait TTL 30/100, compensation horizon 30/100/unknown, compensation outcome success/late-failed, parent authority current/superseded, exclusive-effect-key overlap, effect-key fence present/absent, and compensation dedupe present/absent.

Compared parent dispositions:

1. `neg_root_boolean` — greedily request actions from the current snapshot and mark the root business-DONE even when retry/finality proof, authority, effect-key fencing, or compensation finality is missing.
2. `forward_certificate` — all effects must reach applied/forward disposition under per-effect loop finality, current authority for fresh retries, and effect-key fencing.
3. `rollback_certificate` — applied effects must reach final compensation; unknown retry loops, noncompensatable applied effects, unresolved compensation, and unsafe linked retry block business terminality.
4. `mixed_vector_certificate` — explicit per-effect disposition: final applied effects remain forward, final failed/no-effect branches remain rollback/no-op. This is a separate behavior, not a synonym for all-forward/all-rollback.
5. `manual_fail_closed` — explicit operational/manual-attention terminal state, excluded from business-success/rollback archive coverage.

## Main results

| policy | business-terminal coverage | unsafe business terminals | unresolved/business-blocked |
|---|---:|---:|---:|
| root Boolean negative control | 100% | **205,020 / 248,832 = 82.39%** | 0 |
| all-forward certificate | **33.81%** | **0** | 164,700 |
| all-rollback certificate | **24.42%** | **0** | 188,064 |
| mixed per-effect certificate | **56.94%** | **0** | 107,136 |
| manual/fail-closed | business 0%; operational manual 100% | **0** | n/a |

All percentages are equal-weight synthetic mechanism coverage, not empirical incident frequencies.

## Result 1: one root Boolean becomes even less defensible with heterogeneous retry loops

`neg_root_boolean` claims business terminality in all 248,832 scenarios and is unsafe in **205,020 = 82.39%**. It conflates at least four independent failure mechanisms:

- an effect whose retry/finality loop is still unknown;
- a failed effect that would require a fresh original effect after parent authority was superseded;
- two fresh retries sharing one exclusive effect key without a fence;
- accepted compensation whose late-failure/finality is unresolved.

The correct root business certificate is therefore a vector/reduction over each effect's terminal disposition, current incarnation/effect-key authority, and every compensation attempt's finality.

## Result 2: unknown retry loops block all business terminal orientations, but not explicit manual handling

The `at_least_one_unknown_retry_loop` slice contains **107,136** scenarios. Root Boolean marks every one terminal and unsafe. All three proof-gated business orientations — forward, rollback, and mixed — produce **0 business terminals** because at least one effect's current business truth is not source-qualified final.

`manual_fail_closed` can still place the workflow into an explicit manual-attention operational terminal state without pretending that the business effect vector is fully forward/rollback. This keeps operational liveness separate from semantic finality.

## Result 3: per-effect mixed terminality safely recovers cases where one global orientation is impossible

Under a superseded parent with at least one final failed effect there are **75,600** scenarios:

- all-forward business terminal: **0** because fresh original retry is no longer authorized;
- all-rollback: **27,216**;
- mixed per-effect vector: **53,136**;
- root Boolean: 75,600 terminals, **75,600 unsafe**.

The mixed vector can preserve already-final applied effects as forward while treating final failed/no-effect branches as rollback/no-op, without issuing a fresh stale-authority effect. This is a real behavior niche; it must be selected explicitly by business policy, not silently substituted for an all-forward objective.

## Result 4: shared effect-key fencing can change the feasible recovery orientation

In the **8,856-scenario** slice where both effects are final-failed, share one exclusive effect key, and no fence exists:

- all-forward: **0 business terminals** because two fresh originals would race/duplicate authority;
- all-rollback: **8,856** safe terminals because neither failed effect needs compensation;
- mixed: **8,856** safe terminals;
- root Boolean: **8,856 / 8,856 unsafe**.

Thus the claim/effect fencing layer does not merely affect low-level execution; it changes which parent recovery behaviors are currently feasible.

## Result 5: compensation late failure changes the archive but not forward finality

The `late_comp_failure` slice contains **28,032** scenarios where at least one applied compensatable effect exists and compensation can later fail:

- root Boolean: **28,032 unsafe terminals**;
- all-forward: **14,784** safe business terminals;
- all-rollback: **8,448** safe terminals, only where linked compensation retry/finality gates are satisfied;
- mixed: **21,120** safe terminals.

A failed compensation does not invalidate a previously final original effect's forward state. This is another reason forward and rollback certificates must remain distinct branches rather than mutating one root `DONE`/`UNDONE` flag.

## Result 6: the safe recovery archive preserves behavior diversity that pure cost Pareto can collapse

The safe business-recovery archive covers **141,696 / 248,832 = 56.94%** with unsafe count 0 in-model. There are **115,776 = 46.53%** scenarios with more than one safe behavior orientation available, and **70,848 = 28.47%** with multiple nondominated branches under the synthetic cost vector `{actions, new original effects, compensations, residual irreversible exposure}`.

Pareto branch counts are:

- forward: 35,424;
- rollback: 35,424;
- mixed: 141,696.

The mixed branch often dominates raw action count because it avoids new effects/compensations, but that does **not** mean it is semantically interchangeable with the requested all-forward or all-rollback business goal. The QD archive therefore must index behavior/disposition first and compare costs within behavior rather than letting one cheap mixed branch erase distinct commitments.

## Current integrated candidate protocol

1. Parent state contains an **effect vector**, not a root Boolean. Every original effect has `{effect_id, incarnation, effect-key authority, retry/finality certificate, terminal disposition}`.
2. Every compensation attempt is a distinct linked identity with its own retry graph and finality certificate.
3. Parent business terminality is a reduction that requires every required effect to have an explicit terminal disposition permitted by the chosen business behavior.
4. Unknown/unbounded retry loops keep that effect nonterminal until explicit loop termination, authoritative final status, or a business policy chooses manual attention instead of claiming success/rollback.
5. Fresh original retries require current parent/capability authority and exclusive-effect-key fencing; compensation retry safety is independent.
6. Recovery planning keeps separate behavior niches for at least `all-forward`, `all-rollback`, `mixed-vector`, and `manual/fail-closed`, each with proof requirements and cost/exposure descriptors.
7. Do not rank mixed/forward/rollback solely by one scalar cost before business disposition is chosen.

## Scope limits

- Finite synthetic two-effect lattice only.
- Mixed-vector disposition is only valid when the application/business contract explicitly permits per-effect mixed completion; it is not a hidden fallback for atomic all-or-nothing objectives.
- Pending effect truth is exposed only when its modeled source-qualified horizon is within the wait TTL; real sources need their own status/finality semantics.
- Late compensation retry is a simplified distinct second identity with a modeled successful final branch when dedupe/finality gates hold.
- No empirical rates are claimed.

## Persistence note

The repository result is a compact source-qualified summary of the executed 248,832-scenario model and the repository contains an inspectable executable script. Byte-identical executed-source binding is not claimed; persisted Git blobs plus mechanism counts are the durable evidence.

## Exact Phase-1 continuation

Continue with **business-objective constraints over the recovery archive and parallel recovery execution**.

Next finite grammar:

- objective contract: all-forward required / all-rollback required / atomic-all-or-nothing / mixed permitted / manual permitted;
- two or three safe recovery proposals generated independently;
- proposals may share exclusive effect/compensation keys;
- planner selects one proposal vs executes nonconflicting proposal fragments in parallel;
- stale proposal after parent objective/version change;
- proposal archive behavior descriptors and proof digests;
- compare scalar cheapest-only, objective-first behavior archive, fragment-level parallel composition with effect-key reservations, and early cross-critique that collapses proposal diversity;
- measure objective violation, duplicate authoritative effect/compensation, safe feasible-objective coverage, proposal diversity, parallel latency proxy, and proof-staleness rejection.

This connects the concurrency/claim protocol back to the role's QD/multi-agent bias while remaining inside Phase-1. Keep a nonempty Phase-1 frontier afterward.
