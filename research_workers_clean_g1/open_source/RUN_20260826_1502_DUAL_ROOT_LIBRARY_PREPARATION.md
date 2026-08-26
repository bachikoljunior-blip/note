# Open Source Systems Scan — dual-root library preparation and venue authority

Run time: 2026-08-26 15:02 JST
Role: `open_source`
Frozen semantic control tuple: note main `b448726ce9420fd51974e70df965c4e6e3fb68e4`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source pin: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (verified current public main during this run).

## Independence
Only the sanitized root control, this role's own clean state, and public source were used semantically. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, aggregate execution ledger, or other-role receipt/config was read. No role-local sanitized feedback file existed at the frozen note revision.

## Material finding: the split-root defect starts *before* checklist rendering
The previous checkpoint isolated a dynamic-venue split-brain in Planner/Reviewer/Manager checklist rendering. The public source now shows an earlier and more direct failure path: research Skill-library preparation itself is still single-rooted on the execution workdir even though production daemon state is split.

### Production really uses separate roots
`daemon/_life_worker_runtime_context.py::_runner_namespace()` sets:

- `ns.workdir = cfg.project_workdir` (operator repository / execution workdir), and
- `ns.project_state_dir = cfg.life_dir` (Manager/session control root).

`apps/_runtime_construction.py::_manager_roots()` then constructs `Manager(project_root=state_root, execution_workdir=workdir, ...)`. Therefore the normal daemon path is genuinely split-root, not a test-only topology.

### Manager persists `target_venue` only in the protected state root
`manager/_vertical_ops.py::_commit_vertical_decision_locked()` calls `persist_vertical(self.project_root, ..., target_venue=decision.target_venue or None)`. `self.project_root` is the protected Manager state root. There is no corresponding host-side write of `target_venue` into `self.execution_workdir` in this path.

That is correct as an authority boundary: the Manager-selected target belongs in protected state. But research preparation currently looks elsewhere.

### The vertical library-preparation contract carries no state root
`core/vertical_contract.py::VerticalLibraryContext` contains `workdir`, `stage`, objective/direction/mode, runner/model, etc., but no `state_root` / `authority_root`.

`skills/loop_skill_library.py::_prepare_vertical_libraries()` computes:

- `stage = current_stage(mission.workdir)`,
- `load_vertical_contract(..., project_root=mission.workdir)`, and
- `VerticalLibraryContext(workdir=mission.workdir, stage=stage, ...)`.

Yet `SkillLoop.run()` already computes `vertical_state_root = self.config.vertical_state_root or workdir` and uses that protected root for the authoritative role-prompt vertical resolution. The library-preparation path simply drops that root.

### Research venue preparation then reads `target_venue` from the wrong root
`verticals/research/library_preparation.py` invokes `needs_venue_research(context.workdir)`.

`verticals/research/venue_research.py::_target_venue(workdir)` calls `_venue_key_from_pipeline_state(Path(workdir))`, so it reads the execution-workdir copy of `PIPELINE_STATE`, not the Manager state root.

`needs_venue_research()` explicitly returns `False` when that workdir-side venue is absent. Thus a fresh split-root campaign can take this sequence:

1. workdir has no pipeline state;
2. Manager classifies research and persists a non-built-in `target_venue` into `life_dir/.argus/PIPELINE_STATE.json`;
3. Engineer mission runs in the workdir;
4. research library preparation asks the workdir for `target_venue`;
5. workdir has none, so `needs_venue_research()` returns `False`;
6. the source-backed `research/VENUE_PROFILE.json` research step is never started.

This is stronger than the previous checklist-only diagnosis: the profile can fail to be created at all.

## Material finding: library-preparer stage can also be stale under split roots
The same missing state-root plumbing affects `context.stage`.

`_prepare_vertical_libraries()` obtains stage with `current_stage(mission.workdir)`. `stage_machine.current_stage()` reads pipeline state from the supplied root and, if no valid state exists, falls back to the first stage of the resolved/fallback vertical. With a fresh workdir copy that has no Manager state, this becomes the research stage.

Manager transitions, however, mutate only the protected state root. `stage_machine._set_stage()` writes `PIPELINE_STATE` at its `project_root` and merely projects the resulting stage to `STATUS.md` under `evidence_root`; it does not mirror `current_stage` back into the workdir pipeline-state copy.

The repository's migration tests make this divergence explicit: `migrate_legacy_manager_state(state_root, workdir)` copies legacy state into the Manager root once and intentionally leaves the workdir copy unchanged because it remains an evidence root.

Therefore after a protected-root transition to `plan`, `benchmark`, `run`, etc., research library preparation can continue to observe an old/fallback `research` stage from the workdir.

Concrete research-vertical consequences in the current public source:

- the `plan`/`benchmark`/`run` branch that appends `engineer/training-infrastructure-guide.md` can be skipped because the stale context still says `research`;
- the research-only idea-portfolio branch can be reconsidered at the wrong time;
- venue-research gating is driven by the stale library-preparer stage rather than the authoritative Manager stage.

A search for `LIBRARY_PREPARER =` found the concrete provider hook only in the research vertical at this public revision, so the demonstrated behavioral defect should remain research-scoped. The framework contract is generically missing the authority root, but no cross-vertical runtime failure is claimed without another provider.

## Authority/descriptor classification clarified
This run also resolves an important ambiguity from the previous frontier: the workspace-side `PIPELINE_STATE` is not uniformly authoritative or uniformly untrusted. Authority is key-specific.

### `current_stage`, `vertical`, route fields, Manager `target_venue`
These are Manager-owned control fields in the protected state root after split-root migration. The one-time migration explicitly leaves the workdir copy unchanged, so the workdir copy is not a reliable current authority for these keys.

### Math objective is deliberately dual-root
`manager/_vertical_ops.py::_adopt_operator_objective()` explicitly writes the operator objective to **both** `self.project_root` and `self.execution_workdir` when the roots differ, with a code comment explaining why: deterministic vertical validators run against the evidence/workdir root, so a state-root-only objective would make the gate unsatisfiable.

This is a strong internal precedent: when the same semantic value is genuinely required at both authority and evidence roots, Argus already performs an explicit host-mediated dual-root projection rather than assuming the workspace copy stays synchronized.

### Workdir `target_venue` in venue research is descriptive, not authority
The venue-research model prompt itself calls the requested workdir write “only the descriptive `target_venue` field in `.argus/PIPELINE_STATE.json`”. In split-root production, that model-authored value cannot safely become the Manager authority. It is at most a compatibility/descriptor copy.

The model should not need to mutate a control-shaped file merely to canonicalize the venue key. A cleaner boundary is: model writes source-backed `VENUE_SELECTION.md` + `VENUE_PROFILE.json`; host validates the profile key against the protected Manager target and, if a compatibility copy is still needed, writes it itself.

## Existing resolver already has the right mismatch guard
`verticals/research/venue_profiles.py::resolve_venue_profile()` is safer than a naïve local-profile lookup:

1. an explicit environment override has highest precedence;
2. a built-in state key resolves directly from the built-in registry;
3. a local dynamic profile is accepted only when there is no state key or when `_normalize_venue_key(local.key) == _normalize_venue_key(state_key)`;
4. otherwise it falls through to `get_venue_profile(state_key)`, which raises for an unknown non-built-in key.

So a mismatching local dynamic profile does **not** silently override a state-selected venue in the current same-root implementation. A two-root resolver should preserve this exact normalized-key equality rule: protected root supplies target identity; evidence root supplies the source-backed dynamic profile; mismatch/missing/malformed fails closed.

## Refined candidate `clean-os-g1-005`
The candidate should now be framed as **dual-root research context plumbing**, not only checklist rendering:

1. Add `state_root` (or `authority_root`) to `VerticalLibraryContext`.
2. In `SkillLibraryMixin._prepare_vertical_libraries()`, compute `stage` from `self.config.vertical_state_root or mission.workdir`, and load the active vertical contract against that state root. Keep `context.workdir` as the artifact/evidence location.
3. Change research venue preparation to accept both roots. Read the selected `target_venue` only from the authority root; write `VENUE_SELECTION.md`, `VENUE_PROFILE.json`, and attempt receipts only under the evidence/workdir root.
4. Stop asking the model to rewrite `.argus/PIPELINE_STATE.json` in the workdir. If a compatibility projection is still required, have host code write a descriptor copy only after normalized identity matches the Manager target.
5. Generalize `resolve_venue_profile(authority_root, evidence_root=None)` (or an equivalent typed request): built-in identity from authority root, dynamic profile from evidence root, normalized key equality required, same-root remains the default for backward compatibility.
6. Thread that same evidence root through research stage/full checklist rendering for Planner/Reviewer/Manager semantic fallback, preserving the previous checkpoint's fix.
7. Do **not** mirror the whole protected pipeline state into the workdir. The math-objective code demonstrates that selected fields may legitimately be dual-root; whole-object mirroring would reintroduce authority ambiguity and stale-write races.

## Regression matrix
- Fresh split-root research project, non-built-in Manager target, workdir with no pipeline state: venue research is triggered from the protected target and writes profile only to workdir.
- Fresh split-root project at Manager stage `plan`: library context stage is `plan`, and `training-infrastructure-guide.md` is required even though workdir has no current-stage state.
- Manager advances `plan -> benchmark` while an old workdir pipeline copy still says `research`: next library preparation observes `benchmark`, not stale `research`.
- Workdir dynamic profile key matches protected target after normalization (`Example Conf 2026` vs `EXAMPLECONF`): accepted.
- Workdir profile key mismatches protected target: fail closed; no model-authored workdir field may override it.
- Built-in target: no venue-research provider call; profile resolves from authority root as before.
- Same-root direct/legacy mode: byte-compatible behavior where `authority_root == evidence_root`.
- Math objective dual-root behavior remains unchanged.
- Existing single-root venue tests remain green, plus new split-root tests that intentionally keep the workdir copy absent/stale.

## Scope limits
- No live Argus campaign was mutated and no production failure was reproduced. This is source-level reachability and contract analysis on exact public main `16bb128...`.
- The concrete library-preparer defect is demonstrated for the research vertical because it is the only current provider found with `LIBRARY_PREPARER`.
- The current public resolver's same-root normalized identity guard is a positive result; the problem is that authority and evidence roots are not both available at all callers.
- Environment venue override remains an explicit host-level precedence path; this run does not classify it as a model/workdir authority bypass.

## Frontier
1. Trace `research_target_level`, `research_direction_mode`, and project checklist-store reads across state root vs workdir; classify which are authority, evidence, or compatibility projections.
2. Search for any other framework hook that receives only `workdir` even though a `vertical_state_root` is already available, especially preparation/iteration-assessment paths.
3. Inspect split-root tests around `SkillLoop._prepare_vertical_libraries`; if none cover stale/absent workdir pipeline state, specify the minimal regression fixture using two temp roots and a fake venue-research runner.
4. Inspect whether the workdir-side `target_venue` write is consumed by any code that cannot be converted to explicit authority/evidence roots; only then decide whether a host-written compatibility copy is needed.
5. After the two-root context table is complete, return to protected-state writer fencing: common mutation authority, expected revision/digest CAS, one-shot capability, and crash durability.

## Exact continuation
Start by tracing `research_target_level`, `research_direction_mode`, project checklist store, and iteration-assessment consumers with the same two-root matrix. For each key/hook record: authoritative writer, authoritative root, evidence root, model writability, whether a compatibility copy exists, and whether a stale workdir value can affect routing/checklists/completion. Then inspect all callers of `prepare_libraries`/`VerticalLibraryContext` and all consumers of workdir `target_venue`; if research remains the only affected provider, keep the implementation fix narrow at behavior level while making `state_root` generic in the core contract. Finally return to the protected-state CAS/capability branch.