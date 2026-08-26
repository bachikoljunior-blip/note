# Open Source Systems Scan — immediate-upgrade stale snapshot + exact-state rearm boundary

Invocation started: 2026-08-27T01:03:02+09:00
Checkpointed: 2026-08-27T01:09:38+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `10a2498fbc9c76ab2163a17e11a9616ce17fd797`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`
- public Argus main: `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate execution ledger, or other-role receipts/configs were used. Own sanitized feedback was absent at the frozen snapshot. The note head advanced after semantic freeze; later control was not adopted.

## 1. New concrete race: immediate upgrade can restore a stale campaign over a newer semantic command

The immediate Web upgrade path has a stronger stale-state hazard than the previously identified scheduled-upgrade snapshot.

`upgrade_project_daemon()` reads one `continuous = read_continuous_state(life_dir)` snapshot before stopping the daemon. If the daemon stops immediately, it later checks that old snapshot and, when `continuous.enabled` was true, calls non-CAS `write_continuous_config(enabled=True, objective=continuous.objective)` before restarting.

The lifecycle command itself is serialized by the daemon command execution lock, but the Web `/continuous` endpoint is not part of that lifecycle command protocol. It calls `set_continuous()` directly, and Manager enable/disable paths mutate continuous state under their own Manager/continuous locks instead of the daemon command execution lock.

A source-reachable interleaving is therefore:

1. Upgrade U reads enabled objective A at generation g.
2. A newer semantic command S arrives through `/continuous`: it disables A or Manager-enables a newer objective B/route.
3. U calls `stop_daemon(..., drain=True)`. Drain disables the **current** continuous state, preserving its current objective and writing the exact process-lifecycle reason `operator drain-stop`.
4. U then consults its stale pre-stop snapshot from step 1 and calls `write_continuous_config(enabled=True, objective=A)` with no expected-state CAS.
5. The newer stop/B state can therefore be replaced by stale A, after which U restarts the daemon.

This is not a claim that the race has occurred in production; it is a source-level reachable concurrency/fencing defect against public commit `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`.

## 2. Existing storage primitives are already sufficient for a narrow repair

Argus already has the important machinery:

- `ContinuousConfigState` carries a monotonically increasing `generation`.
- `compare_and_swap_continuous_config()` locks the continuous state, compares the complete expected state including generation, and only then writes generation+1.
- continuous writes already use temp-file write, file fsync, `os.replace`, and parent-directory fsync.
- the process-only resumable reasons are already an exact allowlist: drain-stop and graceful SIGTERM/SIGINT.

So this branch does not need a new transaction database merely to repair process rearm. The key rule is simpler:

> Never re-enable a continuous objective copied from a snapshot taken before a potentially blocking or concurrent operation. Re-arm only the exact **current disabled process-stop record**, using expected-state CAS.

## 3. Immediate upgrade should resume the current drain record, not its pre-stop snapshot

A safer immediate-upgrade sequence is:

1. Request the restart/drain; do not retain semantic authority in an old `continuous` snapshot.
2. `stop_daemon(drain=True)` disables whatever continuous state is current at the drain point and labels it `DRAIN_STOP_REASON`.
3. After the daemon releases its slot, restart with process-rearm intent only.
4. The boot/rearm gate rereads the current continuous state. If it is exactly disabled + objective + `done_reason in RESUMABLE_STOP_REASONS`, CAS that exact record to enabled.
5. If the CAS misses, reread and never resurrect the old record:
   - a newer enabled state is adopted as current;
   - a newer semantic stop/hold/completion remains disabled;
   - a handoff fence goes to Manager reconciliation, not process-only rearm.

This preserves newer B if B existed before the drain, because drain preserves the current objective. It also preserves an explicit semantic stop that arrives after the drain, because that changes the generation and makes the process-rearm CAS fail.

## 4. Boot's exact-reason gate is still non-CAS and should use the same boundary

`_rearm_operator_drain_for_resume()` is semantically much safer than `start_project_daemon()` because it checks the exact `RESUMABLE_STOP_REASONS`. However, it still receives a previously read `ContinuousConfigState` and performs an unconditional `write_continuous_config()`.

Boot does:

`read_continuous_state()` → `_rearm_operator_drain_for_resume(state=boot)`

without holding the continuous lock across both calls. A concurrent semantic command can therefore change the state between the read and the write. This is the same stale-snapshot shape at a smaller boundary. The same exact-state CAS helper should serve boot, immediate upgrade, and any other process rearm.

## 5. Process launch, process rearm, Manager reconciliation, and semantic resume should not share one boolean

The previous run established that `resume_continuous=True` currently conflates several authorities. This run sharpens the minimal boundary:

- **adopt_current**: process launch only. If durable state is already enabled, adopt that exact current state; never write it.
- **process_rearm**: only exact process-stop reasons; reread current state and CAS the exact disabled record to enabled.
- **manager_reconcile**: exact handoff-fence state; run fresh Manager reconciliation while remaining disabled until successful commit.
- **semantic_resume**: a human/operator decision may remain durably accepted, but execution authority is revalidated against current route/lineage before enablement.

A helper such as `reconcile_or_rearm_continuous(...)` should consume the current durable state/expected generation, not a generic old boolean plus copied objective.

## 6. Replacement becomes simpler once process start is non-authoritative

`replace_project_daemon()` does not independently take and later restore a target continuous-objective snapshot. Its current semantic exposure comes from passing `resume_continuous` onward to `start_project_daemon()`, which today performs broad pre-admission re-enable.

If process start stops mutating semantic state and the boot gate only performs exact-state process rearm, replacement does not need its own objective restoration path. A stale caller boolean can at most request the **kind** of boot behavior; it cannot name or restore an old objective.

## 7. Two-CAS Manager handoff fence payload/recovery semantics

The earlier two-CAS fence remains the right repair for Manager route+objective replacement because the route commit and continuous state live in different durable objects.

Minimal sequence:

1. Exact CAS from A enabled at generation g to a disabled fence at g+1 with exact reason `manager handoff reconciliation required`.
2. The fence's `objective` may hold the Manager-clean incoming execution task, but the disabled state is explicitly non-executable. It exists for recovery/reconciliation only.
3. Under the existing pipeline lock, exact CAS from that fence state to B enabled at g+2, with the route commit in the CAS pre-replace callback.
4. If the route callback commits but the final replace fails, the durable combination is route B + **disabled fence**, not route B + enabled A. Recovery therefore fails closed into reconciliation.

The current continuous schema does not preserve unknown metadata across writes, so adding a separate rich pending-handoff object without migrating every writer would create another coherence surface. The smallest safe recovery rule is therefore conservative: if boot finds the fence and cannot prove source-objective/additivity provenance, rerun Manager classification and permit a conservative stage reset rather than reconstructing semantic continuity from partial state.

This is an adaptation proposal, not a measured Argus patch.

## 8. Scheduled upgrade remains a distinct stale-snapshot problem

The scheduled upgrade request persists `resume_continuous` and `objective` and later writes that saved objective back before restart. It should instead persist process-restart identity only and inspect the current continuous state at completion time. A pending upgrade must not own campaign meaning across later semantic commands.

PAUSE remains a positive control for this specific branch because the low-level stop primitive removes a pending upgrade request unless explicitly told to preserve it. The broader fix should nevertheless make stale saved semantic payload unnecessary.

## 9. Regression matrix

High-value tests for the repaired boundary:

1. Immediate upgrade reads A, concurrent `/continuous` disables A, upgrade completes: A must remain disabled; no stale restore.
2. Immediate upgrade reads A, concurrent Manager handoff enables B before drain, drain then restart: B is the only objective eligible for process rearm.
3. Semantic stop arrives after drain record but before rearm CAS: CAS must miss and stop remains authoritative.
4. New enabled B arrives after drain but before rearm CAS: CAS must miss; boot adopts B and never writes A.
5. Boot reads a drain record, concurrent semantic stop changes generation, rearm attempts: stale drain must not be re-enabled.
6. Admission refusal/spawn failure with process-rearm intent: continuous state must remain byte-for-byte unchanged until the boot/rearm gate actually runs.
7. Replacement with stale `resume_continuous=True` against operator hold/completion: must not enable.
8. Scheduled upgrade created under A, later semantic stop/B, later completion: request must not restore saved A.
9. Manager handoff final replace failure after route callback: enabled A + route B must be impossible; disabled fence + B is acceptable fail-closed recovery.
10. Handoff-fence recovery with missing provenance must rerun Manager and may conservatively reset stage; it must never fast-resume solely from old v1-v3 identity.

## Scope

This run inspected only own clean state and public Argus sources at the frozen source head. It did not execute a live exploit, mutate Argus, or claim a production incident. All repair designs above are source-derived candidate adaptations and remain unmeasured until implemented and tested.

## Exact continuation

1. Specify the exact source-level concurrency regressions for immediate upgrade versus concurrent semantic stop/new Manager objective, including the generation assertions before/after drain.
2. Define one exact-state `reconcile_or_rearm` API and map `start_project_daemon`, boot rearm, immediate upgrade, replacement, and operator-decision projection onto its explicit intents; prove no remaining process helper writes a stale copied objective.
3. Finalize two-CAS fence recovery semantics, especially what minimum provenance can safely live in the existing continuous object and when conservative stage reset is mandatory.
4. Complete the v4 canonical route-fingerprint helper/test plan from the prior run and bind semantic resume/reconciliation to it.
5. Design scheduled-upgrade request v2 so it owns process restart identity/fencing but not a stale continuous objective snapshot.
6. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
