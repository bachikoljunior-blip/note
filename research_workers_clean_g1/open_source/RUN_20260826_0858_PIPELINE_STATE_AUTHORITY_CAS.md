# Open Source clean_g1 — RUN_20260826_0858_PIPELINE_STATE_AUTHORITY_CAS

Frozen semantic invocation tuple: note main `57ce90e2b1c84e11468b29954ce20bbce50cae11`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. The note main advanced after semantic freeze; that later head was used only for safe own-state write sequencing, not to change semantic control. Inputs remained own clean state plus public sources only. No O/O-derived, other-worker, downstream comparator/integrator/index/feed/audit, aggregate-ledger, other-role, or legacy/pre-independence semantic state was read.

## Finding A — Argus PIPELINE_STATE is atomically replaced, but has no state revision or CAS

Fresh public `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` remains current `main` in this invocation.

`argus_skill/core/pipeline_state.py` makes `.argus/PIPELINE_STATE.json` the authoritative generic path. `write_pipeline_state()` accepts an arbitrary dict, serializes it to a sibling temporary file, then calls `os.replace(temp, path)`. This prevents readers from seeing a half-written JSON object during one write.

However the primitive currently has none of the following:

- a durable `state_revision` owned by the pipeline-state object;
- an expected prior revision/digest parameter;
- compare-and-swap rejection;
- a common inter-process pipeline-state lock;
- a common mutation callback that serializes every read-modify-write;
- file or parent-directory `fsync` in this primitive before/after replace.

Therefore `os.replace` solves torn-file visibility for one writer, but it does not solve lost updates between two whole-object read-modify-write writers and does not provide exact-state freshness.

## Finding B — a capability namespace can fit in the same JSON object, but embedding metadata alone is insufficient

The checked production writers use the same broad pattern: read the whole dict, mutate selected keys, then write the whole dict.

Observed examples include:

- `skills/stage_machine.py`: stage/current-stage/history mutation;
- `skills/vertical_select.py`: vertical/domain/workflow/target fields and seed-only initial stage;
- `verticals/math/objective_mode.py`: math objective fields;
- `core/verification_policy.py`: exploration/verification policy fields;
- `manager/classification_contract.py`: Manager classification-failure diagnostics.

None of these checked writers validates a closed schema that would reject an unknown namespaced top-level field. In the uncontended case, an added capability/revision namespace would therefore survive their ordinary dict-preserving writes.

But this also exposes the real requirement: **putting capability metadata and a revision field into PIPELINE_STATE is not enough while older writers can still read an earlier whole object and overwrite a newer one.** A stale writer could erase both the semantic transition and its consumed-capability marker even if the transition path itself were carefully implemented.

So the candidate must migrate the writer boundary, not merely add fields.

## Finding C — current stage primitives separate evidence checks unevenly from caller authority

The same Argus source confirms:

- `advance_stage()` validates ordering and runs the active vertical's deterministic stage-completion validator before mutation, but its own docstring explicitly states that caller identity is not authenticated and `advanced_by` is free text;
- `rollback_stage()` writes through `_set_stage()` without a completion validator and without a caller capability;
- `reset_stage_for_replacement_intent()` likewise writes through `_set_stage()` without caller authentication;
- `complete_final_stage()` re-runs deterministic completion checks and blocks non-final completion unless `allow_early_completion=True`, but its source explicitly describes this defense as **a lock, not a signature**, preserving the distinction between evidence validity and authorization to perform a transition.

The main Manager stage path does mediate these primitives and applies stronger semantic checks. This finding is therefore about the low-level durable mutation boundary, not evidence that normal Manager decisions routinely bypass their checks.

## Finding D — production call-site classification narrows current risk

Normal daemon execution is more serialized than the low-level primitives alone suggest. `daemon/_life_worker_run.py` acquires `manager.pipeline_lock()` around the complete supervisor drain pass. The Manager stage application path in `manager/_stage_ops.py` calls the stage primitives from inside that normal supervisor execution.

Additional production stage mutations were found inside the same supervisor family:

- `life/supervisor/_planning_cycle_enqueue.py` applies a Planner-requested stage change with `advance_stage()` and, if it is not a legal advance, attempts `rollback_stage()`;
- the same module can automatically close the research stage by directly calling `advance_stage(... advanced_by="manager:auto_completion")`;
- `life/supervisor/_mission_execution_settlement.py` can call `rollback_stage(... rolled_back_by="supervisor_dynamic_plan_guard")` to undo a premature advance while a same-plan DAG still has unfinished nodes.

Under the normal resident daemon these run inside the outer pipeline lock. This substantially weakens any claim of a demonstrated normal-daemon stage race.

The concrete concurrency concern remains at writer surfaces that can run outside that resident lock, including the already identified standalone `argus learn`/`persist_vertical` path and standalone math objective CLI, plus any direct library embedding. The candidate should therefore be framed as hardening external/admin/direct-writer and primitive authority, while retaining the existing outer lock rather than replacing it.

## Finding E — Manager campaign-control revision cannot simply be reused as PIPELINE_STATE CAS

Argus already contains a stronger, separate state mechanism in `manager/control_state.py`: immutable campaign revision snapshots, a `HEAD.json` commit point, `state_revision`, a portalocker-backed control lock, and scoped repair authorizations/capabilities tied to exact campaign identity and revision.

But stage mutation and campaign-control projection are not one atomic object. `apps/_runtime_stage_transition.py` first lets Manager write `PIPELINE_STATE.json`, then hashes the resulting pipeline file and projects that state into `CampaignControlStore` via `clear_wait_for_new_evidence(...)`. That later `state_revision` is therefore a post-mutation control-plane revision, not an expected prior PIPELINE_STATE version consumed inside the stage write.

So the existing control-state revision is a useful implementation precedent for locks/revisions, but it is not currently a valid pipeline-state CAS token without a new binding/transaction design.

## Finding F — Snaplist tests directly exercise late-failure rollback, stale-generation fencing, privilege boundary, and exact replay

Fresh public `azizu06/snaplist@bf1e631ec8b01b53938f81b3e66764d6b151f792` remains current `main`.

The public `supabase/tests/mobile_guided_correction.test.sql` gives stronger regression evidence for the previously identified transaction pattern:

1. The test contract states that two live corrections holding the same review revision must not both reach completion/provider settlement.
2. Ordinary authenticated callers are explicitly denied EXECUTE on `complete_mobile_guided_correction`; only `service_role` may call the fixed privileged completion primitive.
3. A stale expected review revision is rejected and leaves prior durable identity/review state unchanged.
4. Completion authorization is tied to an attempt generation. After lease expiry/reclaim, generation advances; the old generation cannot release the live claim or replace the newer capability.
5. The test deliberately installs a trigger that raises `forced late receipt failure` near the end of completion. The expected assertions prove that the whole operation rolls back: old review revision remains, included allowance is not spent, the correction claim remains pending, and the prior listing draft remains unchanged.
6. After a successful completion, an exact retry replays the receipt committed with the item instead of applying the mutation again, while a fresh new request cannot spend the one included correction a second time.

This is direct test evidence for the invariant bundle needed by an exact-once state transition: fixed privileged mutation surface, expected prior state, attempt/version fencing, atomic target+receipt/capability settlement, failed-transaction rollback, and idempotent receipt replay.

Scope remains limited: Snaplist is a PostgreSQL-backed marketplace workflow, not an agent runtime. It demonstrates the systems invariant and regression strategy, not an Argus or AGI performance effect.

## Candidate refinement — `clean-os-g1-005`: centralize pipeline mutation authority

A more faithful minimal Argus adaptation is now:

1. Keep the existing normal `manager.pipeline_lock()`; do not replace a working outer serialization layer.
2. Add one common low-level `mutate_pipeline_state(...)` boundary used by **every** production PIPELINE_STATE writer.
3. Under an inter-process file lock, read one authoritative object and compute/verify an exact prior revision and/or canonical object digest.
4. For privileged stage transitions, verify a one-shot bearer secret only by hash, plus unconsumed/expiry status and exact scope: transition kind, from-stage/route, allowed target, and expected prior pipeline revision/digest.
5. Run the deterministic completion/evidence gate where the transition requires it.
6. In one in-memory object, apply the semantic mutation, increment pipeline revision, mark the capability consumed, and write an idempotent transition receipt.
7. Commit that one object through a crash-safe atomic replacement. A mismatch, replay, expired capability, evidence-gate failure, or stale admin writer writes nothing.
8. Exact retry after a successful commit returns/reconstructs the committed receipt rather than applying the transition again.
9. Move `persist_vertical`, math objective writes, verification-policy writes, classification diagnostics, and stage-machine writes onto the same boundary, or explicitly fence/refuse them while a live same-workdir owner exists. A partial migration leaves a whole-object clobber path.

The single-object form has an important advantage over capability state in a second plain file: target mutation and consumed marker can become visible in the same `os.replace`, analogous to Snaplist's one DB transaction. But Argus has not tested this adaptation, and its current writer lacks explicit file/parent-directory fsync; the exact crash-durability contract still needs direct validation.

## Falsification/regression matrix

1. Two writers read revision N; first commits N+1; second is rejected and leaves byte-identical N+1 state.
2. Same test for standalone vertical/admin writer versus stage transition.
3. Same test for standalone math objective/policy writer versus stage transition.
4. Capability is bound to exact transition kind/from/target/revision and cannot authorize another mutation.
5. State changes after capability mint -> stale capability rejected with no write.
6. Valid use commits semantic transition + consumed marker + receipt + revision increment in one replacement.
7. Replay of consumed capability -> no write; exact retry receives prior receipt semantics.
8. Deterministic completion validator failure -> neither semantic mutation nor capability consumption commits.
9. Crash before replace -> old state and unconsumed authority remain; no partial semantic state.
10. Crash after durable commit point -> transition and consumed marker are both present.
11. A legacy/current production writer cannot erase the capability namespace or decrement revision.
12. Raw bearer secret is absent from model-readable durable state.
13. Existing read-side completion revalidation still rejects structurally stale/corrupt completions independently of write-time authority.
14. Normal daemon behavior remains unchanged in matched tests; the new inner boundary does not create duplicate locking deadlocks.

## Tested scope / uncertainty

- Argus source commit: `962cb06554daaede17b786c495e13ee3b6530e6e`, verified current main during this invocation.
- Snaplist source commit: `bf1e631ec8b01b53938f81b3e66764d6b151f792`, verified current main during this invocation.
- No unauthorized Argus mutation or concurrent race was executed.
- No claim is made that current normal daemon stage mutation is racing; source tracing instead shows an outer Manager pipeline lock around the ordinary drain path.
- The one-object file-backed capability/CAS design is an untested Argus adaptation. Snaplist's DB transaction supplies a strong external invariant precedent but does not prove the file implementation.
- Argus `write_pipeline_state()` currently uses temp + replace but does not visibly call file or directory fsync; power-loss durability is not yet characterized.

## Nonempty frontier

1. Complete the production writer inventory, especially any direct `.argus/PIPELINE_STATE.json` writes that bypass `write_pipeline_state()`.
2. Trace the exact `argus learn` CLI and live-daemon ownership checks; decide whether same-workdir live mutation should be refused or transparently use CAS-aware mutation.
3. Audit standalone math objective and verification-policy entry points for live-owner coexistence and whether all are intended operator-only setup surfaces.
4. Inspect Argus pipeline-lock implementation/reentrancy to design an inner pipeline-state lock without deadlocking normal daemon paths.
5. Audit crash durability: compare `write_pipeline_state()` with `CampaignControlStore._atomic_write_json()` and determine the minimum file-fsync + directory-fsync contract needed for the claimed commit point.
6. Search for a public **file-backed** implementation that atomically combines expected-state CAS, one-shot consume, and receipt in one object; if absent, retain Snaplist as the strongest combined precedent and test the Argus adaptation directly.
7. Continue non-daemon/direct-library stage-mutator call-site search; if no supported bypass exists, explicitly downgrade current stage-primitive risk to defense-in-depth while keeping external/admin writer concurrency as the concrete present issue.

## Exact continuation

First finish the authoritative PIPELINE_STATE writer inventory and inspect Argus's pipeline-lock implementation/reentrancy plus `argus learn` lifecycle fencing. Then audit the current atomic writer's fsync/directory durability and search for a matched file-backed CAS+consume precedent. Preserve the distinction between demonstrated current Argus behavior, demonstrated external exact-once transaction behavior, and the untested file-backed adaptation.
