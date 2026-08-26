# Open Source clean_g1 — RUN_20260826_0959_AUTHORITY_PARTITION_AND_DURABILITY

Frozen semantic invocation tuple: note main `4a35c4305c96b5e1e788aa137aff8527b050cf66`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. The note main advanced after semantic freeze; later Note head reads were SHA-only and used only for safe own-state write sequencing. Inputs remained own clean state plus public sources only. No O/O-derived, other-worker, downstream comparator/integrator/index/feed/audit, aggregate-ledger, other-role, or legacy/pre-independence semantic state was read.

Public Argus source remained current `main` at `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` during this invocation.

## Finding A — the authoritative pipeline JSON is intentionally mixed-ownership, including direct model writes

The previous writer inventory focused on Python functions that call `write_pipeline_state()`. Current public source shows that this is not the full authority surface.

`argus_skill/verticals/research/skills/engineer/auto-research-pipeline.md` explicitly defines `.argus/PIPELINE_STATE.json` as the mission ledger and says the Engineer may update descriptive fields such as objective, target venue, and artifact paths, while stage fields remain Manager-owned.

More concretely, `argus_skill/verticals/research/venue_research.py::_build_prompt()` tells the model-run to update the descriptive `target_venue` field directly in `.argus/PIPELINE_STATE.json` and only instructs it not to edit `current_stage` or stage statuses. `research_venue_profile()` executes that prompt with `RunnerOptions(... full_auto=True, live_search=True, working_dir=<project>)`; the host then checks runner success and whether a loadable venue profile exists. It does not itself merge the requested `target_venue` patch through a host mutation primitive.

`argus_skill/verticals/research/library_preparation.py` invokes this venue-research path during ordinary research preparation for non-exploratory paper missions at stages research/plan/benchmark/run/analysis when explicit venue research is needed. Therefore the direct model write is a current product path, not merely an obsolete example.

There is an intentional role contrast: `argus_skill/verticals/research/prompt_policy.py` tells Planner not to edit `.argus/PIPELINE_STATE.json` and that Manager owns rollback. The authority boundary is therefore currently encoded partly as role text over different fields of one writable JSON object.

This is a stronger design constraint than the previous Python-writer inventory: migrating every Python read-modify-write caller to a CAS-aware API would still leave a model-facing raw-file writer unless the product contract or filesystem/tool boundary changes.

Scope: this is source-level reachability and intended capability, not a demonstrated exploit. No model was asked to alter Manager-owned stage state, and no stage corruption was reproduced. Backend sandbox details vary; the solid observation is that this production prompt expects a model-run to update the same authoritative file and the call does not explicitly request a read-only sandbox.

## Finding B — candidate must partition authority, not merely serialize writers

`clean-os-g1-005` therefore needs an authority partition in addition to centralized mutation.

Preferred minimal architecture:

1. Keep host-owned control state separate from model-writable descriptive/evidence state. Host control should contain at least route/vertical/workflow, `current_stage`, per-stage status, pipeline revision/digest, transition authorization state, and committed receipts.
2. Model/Engineer output may write or propose descriptive evidence such as a source-backed venue profile, requested venue key, artifact paths, and annotations, but must not have raw write authority over the host control object.
3. When a descriptive value needs promotion into control state, a narrow host mediator validates an explicit patch schema and expected control revision/digest, then commits it through the same authoritative mutation boundary as stage/route changes.
4. If one physical JSON file is retained, the runtime must deny raw model writes to that file and expose a scoped patch API/tool; prompt text such as “only edit target_venue” is not an authorization primitive.
5. Compatibility migration must preserve existing descriptive data without inheriting the old mixed-write authority contract.

A practical split could resemble `PIPELINE_CONTROL.json` plus a model-writable descriptor/evidence object, but the names/schema are an untested adaptation. The invariant is the separation of semantic control authority from agent-authored evidence, not a particular filename.

## Finding C — the existing Manager pipeline lock has no explicit reentrant contract

`argus_skill/manager/_session_ops.py::manager_pipeline_lock()` uses a portalocker exclusive advisory lock on `.manager_pipeline.lock`. Each context opens the lock file, attempts `LOCK_EX | LOCK_NB` in a retry loop up to the configured timeout, then unlocks on exit. Public portability tests prove exclusion against a real peer process and successful reuse after release.

No owner/thread recursion counter, inherited lock token, or nested/reentrancy contract is present in that implementation, and no nested-lock regression was found in the searched public tests.

This does **not** establish a current deadlock. It establishes a migration constraint: a new `mutate_pipeline_state()` layer should not blindly reacquire `manager_pipeline_lock()` from code already running under the normal daemon's outer pipeline lock. Safer options are either:

- pass/prove an already-held outer lock context into the mutation primitive; or
- introduce a distinct lower-level pipeline-state lock with one documented order, e.g. Manager pipeline lock outer → state-mutation lock inner, and test all call paths for order inversion/nested acquisition.

The existing outer lock should remain because normal daemon execution already benefits from it.

## Finding D — atomic replace is weaker than a crash-durable commit point

Current `argus_skill/core/pipeline_state.py::write_pipeline_state()` writes the same-directory temp with `Path.write_text()` and then `os.replace()`. It does not explicitly flush/fsync the temp file or fsync the parent directory.

Argus's own `manager/control_state.py::_atomic_write_json()` is stronger: it writes a named temp, flushes, calls `os.fsync(handle.fileno())`, then `os.replace()`. Its JSONL append path also flushes and fsyncs. However `_atomic_write_json()` still does not visibly fsync the parent directory after the replace.

On Linux/POSIX-style durability, file fsync alone does not necessarily make the containing directory entry durable; the directory itself must be synced for a stronger rename commit claim. Therefore the candidate should distinguish:

- atomic visibility to concurrent readers;
- process-crash survival after data reaches the filesystem layer;
- power-loss/storage durability of the renamed directory entry.

A stronger Linux-style file-backed commit sequence is: same-directory temp write → flush/file fsync → atomic replace → parent-directory fsync. Platform/filesystem semantics differ, so this should be implemented/tested with explicit portability fallbacks rather than advertised as universal physical durability.

## Finding E — file-backed precedents support pieces, but no public match found for the full invariant bundle

Public implementations found in this pass support parts of the design:

- `g2sidian` uses an in-process write lock, rechecks a filesystem freshness token immediately before replace, writes a same-directory temp, flushes/fsyncs, then replaces. This is useful evidence for stale-write rejection around atomic file replacement, but it is mtime-based, in-process, and lacks one-shot capability consumption/receipt semantics.
- `RunSteward` documents/testing around old-or-new atomic JSON visibility and explicitly limits its claims rather than treating rename as coordination or directory-sync durability.
- Chidori's filesystem backend documentation explicitly treats read-compare-write as advisory when the storage primitive cannot make the comparison and write one atomic operation; stronger enforced CAS is delegated to transactional/serialized backends.

No single public file-backed implementation was found in this pass that combines: inter-process serialization, exact expected-state CAS, one-shot scoped authority consumption, semantic mutation, durable receipt, and exact replay in one authoritative file transaction.

The previously audited Snaplist PostgreSQL path therefore remains the strongest combined external precedent for the **invariant bundle**: expected prior revision, privileged fixed mutation surface, generation fencing, one-shot authority, target+receipt settlement in one transaction, late-failure rollback, and exact receipt replay. That does not prove the proposed Argus file-backed adaptation.

## Candidate refinement — `clean-os-g1-005`: authority-partitioned centralized pipeline mutation

Keep the candidate identity but strengthen its required properties:

1. Preserve existing normal outer `manager_pipeline_lock()` behavior.
2. Separate host control authority from model-writable descriptive/evidence state, or equivalently make raw control-file writes impossible for model processes and expose only a scoped host patch primitive.
3. Route **all** host/control writers — stage machine, vertical routing, objective/policy/diagnostic writers, admin/setup paths, compatibility migration, and descriptive promotion — through one mutation authority.
4. Serialize the mutation boundary across processes with a defined lock order/reentrancy contract.
5. Read one current control object under that boundary; verify exact expected revision/digest before mutation.
6. For privileged transitions, validate a one-shot scope-bound capability without persisting a model-readable bearer secret in the writable descriptor surface.
7. Run deterministic evidence/completion gates required by the transition.
8. Apply semantic mutation, increment revision, mark capability consumed, and write an idempotent receipt in the same authoritative replacement object/transactional commit point.
9. Stale/replayed/expired/mismatched authority or failed evidence validation writes nothing.
10. Exact retry after successful commit returns the already committed receipt rather than applying again.
11. Make the file-backed commit point explicit: file-data sync and directory-entry durability where the platform supports it; document weaker guarantees where it does not.
12. Refuse or CAS-route external/admin writers against a live same-state owner instead of allowing unmanaged whole-object replacement.

## Expanded falsification / regression matrix

1. Model-facing venue research can produce its profile/descriptor without any raw write permission to host control state.
2. A model attempt to alter `current_stage` or control revision through the descriptor channel is rejected and leaves control state byte-identical.
3. A valid `target_venue` proposal is schema-validated and promoted by host without changing unrelated stage/route fields.
4. Two host writers start from revision N; exactly one commits N+1 and the stale one is rejected.
5. Admin `learn`/objective writer versus live stage transition receives the same stale-state protection.
6. One-shot transition capability is bound to kind/from/target/revision and cannot authorize a different patch.
7. State changes after capability mint → stale capability rejected with no write.
8. Successful commit contains transition + revision increment + consumed marker + receipt at one commit point.
9. Exact replay returns prior receipt semantics; no second transition occurs.
10. Evidence validator failure commits neither target mutation nor capability consumption.
11. Crash before replace leaves old control state; crash after the declared durable commit point yields new state including consumed marker/receipt.
12. Fault-inject between file fsync, rename, and directory fsync to document actual platform guarantees.
13. Legacy model-writable or Python writer cannot erase/decrement control revision because it has no raw control-write route.
14. Normal daemon matched behavior remains unchanged and no nested-lock deadlock is introduced.
15. Cross-process lock tests cover outer Manager lock plus inner mutation boundary and every permitted lock order.
16. Existing read-side completion revalidation remains independent of write-time authorization.

## Tested scope / uncertainty

- Argus source commit: `962cb06554daaede17b786c495e13ee3b6530e6e`, verified current public main during this invocation.
- No unauthorized mutation, concurrent lost-update race, deadlock, or power-loss test was executed against Argus.
- Normal resident daemon stage work remains outer-pipeline-lock serialized in the traced standard path; this run does not claim a demonstrated normal-daemon race.
- Direct model editing of descriptive fields in the authoritative pipeline JSON is an explicit current research-role contract and venue-research prompt path; the security/integrity consequence is an architectural inference, not a reproduced corruption.
- Backend sandbox permissions are not generalized here. `RunnerOptions` for venue research does not explicitly request read-only mode, but effective backend confinement must be audited separately.
- File/directory fsync guarantees are OS/filesystem-specific. The candidate's crash-durable file design remains untested.
- No public file-backed exact match for CAS + one-shot consume + receipt was found; absence from this search is not proof none exists.

## Nonempty frontier

1. Enumerate every model-facing prompt/Skill that explicitly permits or requests writes to `.argus/PIPELINE_STATE.json`; classify field ownership and whether host post-validation exists.
2. Finish authoritative writer inventory by privilege class: host control writer, admin/setup CLI, model-direct writer, compatibility migration, and read-only consumer.
3. Inspect the actual venue-research backend/sandbox construction for Codex and other supported backends to determine whether the control path can be made physically read-only while leaving ordinary work writable.
4. Design a backward-compatible control/descriptor split and define exact promotion semantics for descriptive fields such as `target_venue`.
5. Audit `argus learn`, standalone math objective, and verification-policy entry points for live-owner fencing; choose refuse-versus-CAS behavior explicitly.
6. Add/test a lower-level mutation lock or outer-lock token contract without nested-lock deadlock.
7. Prototype a file commit primitive with temp file fsync + atomic replace + parent-directory fsync where supported, then fault-inject before/after each boundary.
8. Continue searching for a public file-backed implementation combining exact-state CAS and one-shot consume/receipt; otherwise retain Snaplist as the combined transactional precedent and test the Argus adaptation directly.

## Exact continuation

First enumerate all current model-facing Argus prompts/Skills that can write `.argus/PIPELINE_STATE.json`, then trace venue-research through each backend's effective sandbox/writable-path policy to determine whether raw control-file writes can be denied without breaking the feature. In parallel, classify the remaining admin/direct writers and sketch a backward-compatible control-versus-descriptor migration. Preserve the distinction between demonstrated current source behavior, external invariant precedents, and the untested adaptation.
