# Open Source Systems Scan — Manager-state split scope correction

Run time: 2026-08-26 12:00 JST
Role: `open_source`
Frozen control tuple: note main `e01f1794f340dea06da4f33c0c4fde71d6649fe9`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Repository write occurred after note main advanced; the newer note control was not adopted semantically in this invocation.

## Independence
Only the sanitized root control, this role's config/state, public sources, and this role's optional sanitized feedback path were used. No O state, other worker state/config, downstream comparator/integrator/index/feed/audit state, legacy research state, shared execution ledger, or other-role receipt was read.

## Public source pin
- `lbx154/Argus` current public main: `71571444f2f8e6f9dd2ae39530c44b56bbbeccec`.

## Material scope correction
The previous candidate description overstated how much physical authority separation was still missing in current Argus. Current public main already separates the Manager control root from the Engineer execution workdir in the Web/daemon composition:

- `apps/_runtime_construction.py::_manager_roots()` uses `project_state_dir` as the Manager `state_root` when supplied, while `workdir` remains the Engineer/project workspace. It migrates a legacy workspace `.argus/PIPELINE_STATE.json` into the isolated state root once.
- `manager/_core.py` explicitly defines `project_root` as the session-scoped harness state root for pipeline/domain/stage authority and `execution_workdir` as the user repository modified by Engineer. It says Web/daemon composition keeps them separate.
- `daemon/_life_worker_runtime_context.py::_runner_namespace()` sets `project_state_dir = life_dir` and `workdir = project_workdir`, so the real long-running daemon receives separate roots.
- `tests/skills/test_manager_state_migration.py` explicitly checks that the workspace copy is left intact because it is also a live evidence root, while the Manager copy is imported into the state root.
- `manager/_stage_ops.py` reads/mutates stage control using the Manager root but passes `execution_workdir` separately as `evidence_root` to completion validators.

Therefore there is no basis to say that an Engineer write to the workspace copy of `.argus/PIPELINE_STATE.json` directly mutates the authoritative Manager stage in the ordinary isolated daemon/Web composition. That risk remains possible only in compatibility/direct-library configurations where `project_state_dir` is absent and `_manager_roots()` deliberately defaults state root and workdir to the same path, or through a separate synchronization defect that must be demonstrated.

## What remains real
### 1. Two semantic planes still reuse the same filename/schema vocabulary
Current research Engineer policy says the Engineer may update descriptive fields such as `objective`, `target_venue`, and artifact paths in `.argus/PIPELINE_STATE.json`, while `current_stage` and per-stage statuses are Manager-owned (`verticals/research/skills/engineer/auto-research-pipeline.md`). In isolated composition those are physically different root-local files, but the identical filename and overlapping conceptual schema hide the authority boundary from model-facing text and compatibility callers.

### 2. `target_venue` is a concrete model-written evidence-plane field
`verticals/research/venue_research.py` dynamically instructs the model to write venue artifacts and also update only workspace `.argus/PIPELINE_STATE.json.target_venue`. `venue-format-research.md` repeats that contract. `venue_profiles.py` resolves venue from a supplied root's `target_venue`, so this is live metadata, not dead prose. It should be described as evidence/descriptor state unless it is explicitly promoted into Manager authority.

### 3. The results-analysis Skill still contains stale/undefined transition wording
At current main, `research-results-analysis-and-figures.md` still ends with: “Only then advance analysis/narrative state in `.argus/PIPELINE_STATE.json`.” Repository code exposes canonical `analysis` as a stage, but no dedicated `analysis_state` or `narrative_state` schema was identified. Core Planner/Reviewer prompt policy instead tells model roles to report/replan and says Manager owns rollback/stage mutation. This wording should be replaced with an artifact-local readiness report or a request for Manager transition; it should not ask Engineer to “advance” an ambiguous control-looking state.

### 4. Compatibility mode preserves the original mixed-authority hazard
`_manager_roots()` defaults `state_root = workdir` when `project_state_dir` is not supplied. Thus library/direct callers can still collapse authority and evidence into one physical file. Any design claiming backend-independent authority separation must either require a distinct state root or make low-level mutators/callers safe when the roots coincide.

### 5. Generic state replacement still has no object revision/CAS
`core/pipeline_state.py` provides temp-file + `os.replace()` visibility atomicity but no expected prior revision/digest or generic cross-writer CAS. `verticals/math/objective_mode.py` explicitly documents that its read-modify-write can lose a concurrent `persist_vertical` edit and leaves that race to a lifecycle assumption. Existing outer Manager locking may make ordinary daemon stage flows safe; this does not prove all direct/admin/compatibility writers share that serialization boundary.

## Strong same-repository precedent
`core/project_contract.py` already states the desired authority principle unusually clearly: the operator goal contract is kept in the session state root rather than the working tree because “A contract an agent could edit would not be a contract.” Precise constraint/objective changes are revision-bound to explicit operator confirmation. Engineer receives a briefing derived from this protected contract rather than editing it directly.

This is a stronger local precedent than inventing a new architecture from scratch: extend the same principle consistently to pipeline authority and remove model-facing ambiguity between protected control and writable evidence/proposals.

## Refined candidate
Canonical candidate remains `clean-os-g1-005`, now scoped as:

**authority-partitioned host control + model proposal/evidence plane, with compatibility-safe mutation semantics**

This is not “add physical separation” as though Argus lacked it. Current Argus already has the central physical split in real daemon/Web composition. The remaining adaptation is to make the split explicit and complete across schemas, prompts, direct callers, and mutations.

## Migration matrix
| Current concept | Current writer / location | Proposed authority | Proposed model output | Host action |
|---|---|---|---|---|
| `current_stage`, per-stage status/history, rollback/complete | Manager state root in isolated composition | host-only | Reviewer/Engineer readiness or replan verdict | validate evidence, mutate protected state under one serialized/CAS-aware path |
| `vertical`, workflow route | Manager state root | host-only | Manager semantic decision event | validate known route, persist/readback protected state |
| `target_venue` | Engineer workspace `.argus/PIPELINE_STATE.json` plus venue artifacts | evidence/proposal until host acceptance is needed | `research/VENUE_SELECTION.md` + `research/VENUE_PROFILE.json` with source provenance | optionally promote verified venue key into protected route/control projection; otherwise consumers read explicit descriptor artifact |
| operator objective / precise constraints | protected goal contract already exists | host/operator-authorized | semantic clarification proposal only | use `goal_contract.json` confirmation/revision mechanism; do not treat writable pipeline `objective` as independent authority |
| artifact paths | model-facing mixed-ownership prose; no concrete generic schema key confirmed in this scan | artifact/evidence plane | explicit artifact manifest/provenance records | index/validate; do not grant stage/control mutation authority |
| analysis/narrative readiness | stale Skill wording says “advance” pipeline state | evidence/verdict plane | analysis report, readiness marker, or Reviewer verdict | Manager decides actual stage transition |
| math objective mode/goal | shared generic pipeline state API; operator/host semantics | protected operator/host state | request/proposal, never model choice | serialize with Manager control state and preserve stronger completion contract |

## Evidence-to-claim limits
- No live unauthorized stage mutation, lost update, or deadlock was reproduced in this run.
- Ordinary daemon/Web composition now has source-level evidence of physical Manager/workspace separation; do not describe the old single-file model as the current general production architecture.
- Workspace `.argus/PIPELINE_STATE.json` remains intentionally live evidence after migration; deleting it blindly would break current behavior.
- A split-brain bug between Manager-root and workspace-root venue/objective consumers is plausible but was not established here. It requires a concrete current call path with divergent reads before promotion.
- The generic “artifact paths” permission is underspecified; exact live generic pipeline keys/consumers were not identified yet.

## Frontier
1. Trace `target_venue` and research target/descriptor reads across isolated Manager root versus execution workdir and determine whether any current call path can observe divergent copies after migration.
2. Find exact live consumers/writers, if any, for the research pipeline prose terms `objective` and generic “artifact paths”; classify documentation-only wording separately from schema-backed state.
3. Enumerate all model-facing raw control-like writes outside research and distinguish workspace evidence writes from protected Manager-state mutations under the current split-root architecture.
4. Identify every compatibility/direct entry point where `project_state_dir` is absent and roots collapse; measure which are real product paths versus library-only compatibility.
5. Then resume host-writer fencing/CAS/durability: inventory writers that bypass `manager_pipeline_lock`, expected-revision semantics, and fsync/crash guarantees only for paths that still mutate protected state.

## Exact continuation
Start with current-main call-path tracing for `target_venue`: for each `resolve_venue_profile`/stage-checklist consumer, record whether its root is Manager `project_root` or Engineer `execution_workdir`, and whether any host promotion/synchronization occurs after `venue_research` writes the workspace descriptor. If no divergence reaches an authoritative decision, downgrade this branch from active correctness risk to prompt/schema clarity plus compatibility hardening. Then resolve the exact schema status of `objective` and “artifact paths” before returning to protected-state writer/CAS and durability analysis.
