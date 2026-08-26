# Open Source Systems Scan — role checklist root scope narrowing

Run time: 2026-08-26 13:58 JST
Role: `open_source`
Frozen semantic control tuple: note main `426210f68b4683f3c00cb1c554ba0ff58b3d19fa`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source pin: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (verified current public main during this run).

## Independence
Only the sanitized root control, this role's own clean state, and public source were used semantically. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, aggregate execution ledger, or other-role receipt/config was read.

## Material scope correction
The previously identified split-root dynamic-venue inconsistency is real, but the directly affected role set can now be narrowed.

### Reviewer is concretely affected
`SupervisedEngineer` constructs `ReviewerConfig` with the campaign `vertical_state_root` and, per round, replaces only `working_dir` with the actual Engineer workdir. `Reviewer.evaluate()` forwards both into `render_reviewer_prompt()`. That renderer resolves `_proot` from `vertical_state_root or working_dir`, then calls `evaluate_request(_proot, altitude_root=working_dir, ...)`. Reviewer uses `ChecklistMode.AUTO`, so ordinary review receives a stage checklist and final-submission review receives the full-pipeline checklist.

`RolePromptCatalog.resolve()` uses `altitude_root` for the vertical prompt fragment/search-altitude facts but still calls `format_stage_checklist()` / `format_full_pipeline_checklist()` with `project_root=root`, where `root` is the protected Manager/session state root. Therefore a dynamically researched non-built-in venue profile that exists only in the Engineer workdir can be visible to worktree-derived prompt fragments while remaining unresolved inside the Reviewer's checklist.

### Planner is concretely affected
`Planner.plan_next()` passes `project_root=workdir` and `state_root=cfg.state_root` to the planner prompt builder. `build_continuous_prompt()` resolves `_workspace=project_root` and `_proot=state_root or _workspace`, then calls `continuous_request(_proot, altitude_root=_workspace)`. `continuous_request()` explicitly uses `ChecklistMode.STAGE`.

So the continuous Planner has the same dual-root shape: stage/vertical authority comes from protected state while the work facts live in the worktree, but its checklist is currently rendered from protected state only.

### Engineer mission is *not* directly affected by the stage-checklist path
`mission_request()` does not request a checklist; `RolePromptRequest.checklist_mode` defaults to `NONE`. The Engineer mission therefore receives the vertical fragment from `altitude_root=workdir`, but `stage_checklist` remains empty in the catalog path. Existing prompt-catalog tests assert exactly this for Engineer.

This corrects the broader wording from the previous checkpoint: the concrete dynamic-venue checklist split-brain directly affects Planner and Reviewer, plus Manager paths that explicitly render a checklist, not the ordinary Engineer mission through `RolePromptCatalog`.

### Manager LLM stage-decision fallback is also affected, with an important exception
`Manager.decide_stage_transition()` uses the protected `root` for stage authority. When the deterministic fast path applies after a clean Reviewer `done`, `_ensure_stage_completion(root, cur, evidence_root=self.execution_workdir)` validates against the actual workdir and can advance without another Manager semantic judgment. This path is correctly split-root-aware.

When the deterministic fast path does *not* apply, however, the Manager builds its LLM prompt via `resolve_role_prompt(stage_decision_request(root, stage=cur))` and passes `prompt_context.stage_checklist` into `build_stage_decision_prompt()`. That checklist is rendered from the protected root only. Therefore an ambiguous/replan/regression/non-bounded case can still expose the Manager model to an unresolved dynamic-venue checklist even though deterministic completion uses the valid workdir evidence root.

This makes the defect asymmetric: the strongest deterministic evidence gate can be correct while the semantic fallback prompt is stale/unresolved.

## Hook scan: current concrete defect is research-specific
A repository-wide search for the vertical custom hooks `render_stage_checklist_body` and `render_full_checklist_body` found only the research vertical implementation plus the generic stage-machine dispatcher. Other inspected verticals such as quant define static `CHECKLIST_ITEMS` and do not use a worktree-derived custom checklist renderer.

Therefore the current evidence does **not** justify claiming a generic cross-vertical semantic failure. The framework contract is generically single-root for checklists, but the concrete worktree-derived checklist dependency found so far is research venue resolution.

## Refined candidate
Keep `clean-os-g1-005` narrow and backward-compatible:

**protected state root + explicit evidence root for research checklist rendering, without moving model-authored evidence into protected state.**

Minimal adaptation shape:

1. Preserve `project_root` as the protected stage/route authority root.
2. Add an optional `evidence_root` to checklist formatting (or explicitly reuse the already-carried `altitude_root` as the checklist evidence root).
3. In `RolePromptCatalog`, pass `evidence_root=altitude_root or root` when rendering stage/full-pipeline checklists.
4. In the research renderer, resolve authoritative `target_venue` from the state root, resolve a dynamic `research/VENUE_PROFILE.json` from the evidence root, and require the normalized keys to match. Missing/malformed/mismatched dynamic profile fails closed. Built-in venue lookup remains state-root-only and unchanged.
5. Other verticals ignore the optional evidence root unless they later introduce worktree-derived checklist facts.

This is preferable to copying the dynamic profile into Manager state because the existing state/worktree split is a useful authority boundary.

## Regression matrix
- Reviewer, split root, dynamic non-built-in venue: stage checklist resolves from state target + workdir profile.
- Reviewer `final_submission`: full-pipeline checklist resolves the same venue and no unresolved profile marker appears.
- Planner continuous prompt, split root, dynamic venue: stage checklist resolves from workdir evidence while stage authority remains in state root.
- Manager semantic fallback, split root, dynamic venue: LLM stage-decision prompt receives the resolved checklist; deterministic fast path remains unchanged.
- Engineer mission: `stage_checklist == ""` remains true; no unnecessary checklist injection.
- Dynamic profile key mismatch, malformed profile, or missing profile: fail closed.
- Built-in AAAI/EMNLP and all single-root tests remain unchanged.
- Static-checklist verticals such as quant remain byte-equivalent when no evidence root is used.

## Scope limits
- No live campaign was mutated and no production failure was reproduced; this is source-level reachability and contract analysis.
- The current concrete issue is dynamic/non-built-in research venue resolution under split roots.
- Built-in venues are not implicated by this mechanism.
- Ordinary Engineer mission prompts are not directly implicated by the checklist path.
- The Manager deterministic advance path is already evidence-root-aware; the exposed Manager path is the semantic fallback that renders a checklist from state root only.

## Frontier
1. Trace schema-backed `objective`, artifact-path, and other descriptor fields across protected Manager state versus execution workdir; classify each as authority, descriptor/evidence, or compatibility copy.
2. Search model-facing prompts for other worktree-derived facts that are not implemented through `render_stage_checklist_body` / `render_full_checklist_body`; do not infer generic coverage from hook names alone.
3. Inspect the research venue resolver's key-normalization/mismatch behavior and design the exact two-root API so state authority cannot be silently overridden by a workdir profile.
4. After descriptor tracing, return to actual protected-state writers that bypass `manager_pipeline_lock`: expected revision/digest CAS, one-shot authority, and crash durability.

## Exact continuation
Start with the authoritative-vs-descriptor schema trace: enumerate every read/write of `objective`, `target_venue`, generic artifact-path/descriptor fields, and any workspace copy of `.argus/PIPELINE_STATE.json`; record which root each consumer uses and whether the value affects authority or only evidence/prompting. Then inspect `resolve_venue_profile()` normalization and mismatch handling so the proposed two-root research checklist resolver can combine Manager-owned target identity with workdir-owned source-backed profile without allowing the workdir to override the target. If no additional worktree-derived checklist consumer appears, keep the role/checklist fix research-specific and generic only at the optional API plumbing layer.