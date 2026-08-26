# Open Source Systems Scan — PIPELINE_STATE writer / authority matrix

Role: `open_source` clean exploration.
Frozen semantic control tuple remains note main `35d595e6d6b18bd0fb6953063957f74a7e57662f`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`, verified current public main at the invocation's semantic freeze.

## Storage primitive
`core/pipeline_state.write_pipeline_state(root, payload)` writes the complete JSON object to a sibling temp file and calls `os.replace(temp, path)`. It provides atomic namespace replacement / torn-read protection, but it has:

- no expected prior revision or digest,
- no compare-and-swap,
- no cross-process lock,
- no caller/capability authentication,
- no file `fsync`, and
- no parent-directory `fsync`.

Therefore atomic visibility, stale-writer exclusion, semantic authority, and crash/power-loss durability are four separate properties. The current primitive only directly supplies the first.

## Current writer classes

| Writer surface | Normal target | Current serialization / authority | CAS / exact prior state | Model reachability | Current scope assessment |
|---|---|---|---|---|---|
| `skills.vertical_select.persist_vertical` | caller-supplied root; Manager normally passes protected `project_root` | Manager-owned route decision. Daemon boot runs Manager division before Supervisor construction, so own-daemon mission writes do not overlap boot classification. No lock inside the primitive. | none | Manager model proposes route; host persists | normal protected-route writer, lifecycle-serialized at boot but primitive unfenced |
| `skills.stage_machine._set_stage` via advance/rollback/complete/reset | caller-supplied authority root; production Manager/Supervisor passes protected state root | Normal daemon drain is wrapped by `manager.pipeline_lock()` around `supervisor.run()`. Low-level primitive explicitly says intended Manager-only but caller is not authenticated and actor string is free text. | none | normal role path mediated by host; any code that can import the low-level API is not cryptographically/structurally rejected by primitive | regular path serialized, wrong-path/stale caller remains defense-in-depth gap |
| Supervisor Planner stage request / automatic research close | protected state root | occurs inside normal `supervisor.run()` drain, therefore under outer Manager pipeline lock; deterministic completion validator applies on advance | none at mutator | Planner requests, host applies | no evidence of regular daemon race; still whole-object RMW |
| Supervisor dynamic-plan rollback guard | protected state root | runs inside same drain lock and repairs premature Manager advance; rollback itself has no evidence validator/caller capability | none | host only in normal path | regular path serialized; low-level rollback authority unfenced |
| `manager.classification_contract` failure streak | protected state root | Manager `_vertical_ops` explicitly wraps record/reset calls with `self.pipeline_lock()` | none | host diagnostic only | serialized in current Manager call sites |
| `core.verification_policy.set_policy` | caller-supplied root | no internal lock. Repository call-site search found no production caller outside its own module/tests at pinned commit | none | library/API callable, no current built-in production caller found | dormant library writer surface; not evidence of a live race |
| `verticals.math.objective_mode.set_objective` CLI | operator-selected project root | module source explicitly acknowledges read-modify-write race with `persist_vertical`; intentionally leaves it because CLI is expected at setup | none | operator CLI; also `adopt_operator_objective` host hook | concrete externally invokable stale-write surface if used concurrently |
| Manager math `adopt_operator_objective` | **both** protected `project_root` and `execution_workdir` when split | host hook after route decision; intentionally transcribes the operator request into both roots | none | host, not model choice | intentional dual-root projection for math objective specifically; does not imply research route fields are mirrored |
| material/wiki learning bootstrap calling `persist_vertical(base, "learning")` | operator/admin-selected `base` | CLI stages material then directly persists learning vertical and tells operator to start daemon afterwards. No Manager pipeline lock is acquired in the shown path. | none | operator/admin CLI | concrete external setup writer; normal intended lifecycle is pre-daemon, but primitive does not fence an already-active same root |
| research `venue_research` model instruction | **execution workdir** `.argus/PIPELINE_STATE.json` | prompt explicitly asks model to update descriptive `target_venue` only; no host CAS/mediation for that write | none | yes, directly model-written | not protected Manager authority in production split-root, but a live mutable evidence/descriptor copy that can disagree with protected target and confuse single-root consumers |
| parallel teammate `_SkillLoopRunner.execute` | shared project workdir | explicitly `holds_stage_authority=False`; comment documents that default would write project stage and that this flag intentionally removes that authority | n/a | teammate Engineer model | positive containment: known parallel teammate path is prevented from stage mutation through normal runner transition path |

## Important scope corrections

### Normal daemon stage execution is not an established current race
`daemon/_life_worker_run.py` wraps each drain pass (`supervisor.run()`, or all concurrent supervisors) in the Manager pipeline lock. This covers Planner stage requests, Manager stage decisions reached during mission execution, automatic research close, and the dynamic-plan rollback guard in the normal daemon. Do not describe those normal operations as currently racing each other merely because the low-level storage is RMW.

### The low-level primitive still lacks transition authority/fencing
The stage module itself documents that `advance_stage`/`rollback_stage` are only *intended* Manager-only and do not authenticate the caller. The deterministic evidence gate strongly limits false **advance** claims, but it is not a caller capability, it does not make an old snapshot current, and it does not solve other semantic writers. The correct candidate is therefore an additional primitive-bound invariant, not replacing the existing outer lock or evidence checks.

### `os.replace` is not durability
A successful rename prevents readers from observing a partially written file, but without flushing file data before rename and parent-directory metadata after rename, the source does not establish survival across host crash/power loss. This is a separate durability question and should be tested separately from concurrency/CAS.

### Workdir state has mixed status and must not become a second protected authority
The current architecture intentionally keeps a workspace `.argus/PIPELINE_STATE.json` as a live evidence root for some vertical-specific descriptors/objectives. Math objective adoption intentionally writes both roots. Venue research also asks the model to change the workdir descriptive target. In contrast, protected research route fields (`research_target_level`, `research_direction_mode`, Manager `target_venue`) are not normally projected after classification. A blanket rule that the whole workdir file is either “authority” or “legacy junk” is therefore wrong; the schema needs ownership by field/root, or separate files.

## Refined candidate architecture
Do not create a new lock around every call blindly; normal daemon already holds an outer non-reentrant-looking file lock and nested acquisition is not an established contract. Instead:

1. Define field ownership: protected Manager control keys versus workdir evidence/descriptor keys.
2. Route every **protected-state** semantic mutation through one host mutation primitive accepting an expected prior revision/digest and a scoped mutation intent.
3. When a caller already owns `manager_pipeline_lock`, let the primitive operate under an explicit `lock_held`/transaction context rather than reacquiring it.
4. Re-read current protected state immediately before commit and reject expected-revision/digest mismatch with zero mutation.
5. For privileged model-triggered semantic transitions, require a host-held one-shot capability bound to transition kind/from/target/current revision/evidence fingerprint; do not persist a readable bearer secret in the model workspace.
6. Commit semantic transition + revision increment + consumed-capability marker + receipt in the same replacement object (or a transactional store) so crash cannot commit only half of the authority event.
7. External setup/admin writers (`math objective` CLI, learning bootstrap) should either refuse a live-owner root or use the same mutation primitive/CAS path.
8. Keep model-writable workdir evidence/descriptors outside protected transition authority; host promotes validated descriptors rather than letting a model rewrite a mixed authority object.
9. Add file `fsync` and parent-directory `fsync` only if crash-durability is an intended guarantee, with platform-specific tests. Do not conflate this with logical CAS.

## Strong regression targets
- stale external math CLI snapshot cannot overwrite a newer protected route/stage;
- learning/bootstrap against a live protected root fails or uses exact-current CAS;
- stale/replayed stage capability changes zero bytes;
- wrong transition kind/from/target changes zero bytes;
- evidence validator failure and capability rejection both leave state byte-identical;
- normal daemon nested mutation does not deadlock after common primitive introduction;
- teammate with `holds_stage_authority=False` still cannot change protected stage;
- protected state remains coherent if workdir descriptors are stale/conflicting;
- crash injection before/after temp flush, rename, and directory flush distinguishes atomic visibility from durable persistence.

## Scope limits
This is a source-level writer/call-site audit, not a reproduced lost-update exploit. Normal daemon stage paths were specifically narrowed away from an unsupported race claim because they are covered by the outer pipeline lock. The concrete concurrency exposure is in externally invokable/setup/library writers and in the absence of low-level stale-state/caller fencing if those paths overlap or are called outside their intended lifecycle.

## Exact continuation
Audit `skills.vertical_select.persist_vertical` and all non-stage pipeline writers for field-by-field ownership conflicts, especially whether Manager route persistence can overwrite workdir-only evidence if library-compatibility mode uses one root. Then inspect `CampaignControlStore`/repair capability code at the same public commit to compare its revision/fencing semantics against this proposed common primitive, and verify whether its capability bearer material is readable from each supported Engineer sandbox. Finally search for existing public implementations/tests of JSON-file CAS + durable rename/fsync on Windows/POSIX that can provide a lower-complexity precedent than moving PIPELINE_STATE to a database.