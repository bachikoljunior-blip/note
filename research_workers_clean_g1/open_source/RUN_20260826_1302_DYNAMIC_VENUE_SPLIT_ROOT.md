# Open Source Systems Scan — dynamic venue split-root inconsistency

Run time: 2026-08-26 13:02 JST
Role: `open_source`
Frozen semantic control tuple: note main `c7b85b7a1067335d1bac9911800bb28201e215d9`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source pin: `lbx154/Argus@71571444f2f8e6f9dd2ae39530c44b56bbbeccec` (verified current public main during this run).

## Independence
Only the sanitized root control, this role's own config/state, and public source were used semantically. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, aggregate execution ledger, or other-role receipt/config was read.

## Material finding
Current split-root Argus has a concrete dynamic-venue inconsistency that is narrower than the previously suspected general Manager/evidence split problem.

For ordinary split-root composition, the Manager's `project_root` is the protected state root while `execution_workdir` is the Engineer/project workspace. Manager routing persists the operator-selected `target_venue` into the protected Manager root. Venue research, however, runs in the Engineer workdir and writes the source-backed dynamic `research/VENUE_PROFILE.json`, `research/VENUE_SELECTION.md`, and a normalized/descriptive workspace `target_venue` there.

That split is legitimate by itself. The bug-shaped inconsistency appears in prompt/checklist rendering:

1. `SkillLoop.run()` calls `mission_request(vertical_state_root, altitude_root=workdir)`.
2. `RolePromptCatalog.resolve()` deliberately sends `altitude_root` to the vertical prompt fragment because paper/work artifacts live in the worktree, but sends `root` (the Manager/session state root) to `format_stage_checklist()` / `format_full_pipeline_checklist()`.
3. Research checklist rendering calls `_resolve_checklist_venue(project_root)`, which calls `resolve_venue_profile(project_root)` on that exact root.
4. For a built-in venue, Manager-root `target_venue` is sufficient because the built-in registry resolves it. For a non-built-in researched venue, `resolve_venue_profile()` additionally needs `research/VENUE_PROFILE.json` under the same root. The researched profile exists under the workdir, not the Manager state root.
5. Therefore a valid non-built-in profile in the Engineer workdir can coexist with an unresolved-venue checklist rendered from the Manager root.

This is not merely a hypothetical single-root compatibility concern: the actual prompt-construction API intentionally distinguishes `vertical_state_root` from `workdir`, and the role prompt catalog intentionally uses those roots differently.

## Why deterministic completion can disagree with the prompt
Manager stage transition code keeps authority and evidence separate more carefully than the checklist renderer:

- stage/control resolution uses the Manager root;
- vertical completion hooks receive `project_root=self.execution_workdir` plus `state_root=root`;
- research `stage_completion_issues()` runs paper structural checks against the evidence/workdir root.

So, for a researched non-built-in venue, deterministic completion logic can see the valid workdir venue profile while the Engineer/Reviewer checklist prompt can append `venue.profile` unresolved from the Manager root. This creates a concrete split-brain between role-facing checklist semantics and evidence-facing deterministic validation.

## Current test gap
The venue checklist tests build a single root containing both pipeline state and venue context. They cover missing venue, built-in EMNLP/AAAI, unknown venue, and full-pipeline rendering, but not `manager_state_root != execution_workdir` with a dynamic `VENUE_PROFILE.json` only in the workdir.

The Manager-state migration tests explicitly verify that split roots exist and that the workspace pipeline copy remains a live evidence root, but they do not combine this with researched venue resolution. The venue-research tests are also single-root. A search for `VENUE_PROFILE.json` combined with `project_state_dir` found no current sync/promotion path.

## Scope limits
- No live campaign was mutated and no production failure was reproduced; this is source-level reachability analysis.
- The inconsistency applies to dynamically researched/non-built-in venues. Built-in venues resolve from the Manager-root `target_venue` and are not implicated by this path.
- The finding does not show that all role prompts are wrong, only that the generic checklist-rendering root differs from the work/evidence root in the actual split-root mission construction.
- It does not imply the Manager-state split should be removed. The split is a useful authority boundary; the resolver contract should become root-aware instead.

## Refined candidate
`clean-os-g1-005` now has a concrete submechanism:

**dual-root role rendering: protected control root for stage/route ownership + explicit evidence/descriptor root for worktree-derived semantic facts.**

A minimal adaptation is to extend checklist rendering with an explicit evidence/descriptor root rather than copy model-authored evidence wholesale into protected Manager state. For research venue rendering, resolve `target_venue` authority from the state root while resolving a matching dynamic `VENUE_PROFILE.json` from the evidence root, fail-closed on mismatch, missing profile, or malformed profile, and preserve built-in behavior.

Proposed regression shape:

- Manager root: research vertical, draft stage, non-built-in `target_venue=ExampleConf`.
- Workdir: matching valid `research/VENUE_PROFILE.json` and venue evidence.
- `format_stage_checklist("draft", project_root=manager_root, evidence_root=workdir)` should render ExampleConf rules and no unresolved venue gate.
- Mismatched profile key, malformed profile, or missing workdir profile must fail closed.
- Built-in AAAI/EMNLP behavior remains unchanged.
- Single-root compatibility remains supported by defaulting evidence root to project root only when an explicit split root is absent.

## Frontier
1. Trace Reviewer prompt construction end-to-end and confirm it passes the same Manager-root/workdir pair as Engineer, or narrow the affected role set if not.
2. Search all other vertical render hooks for worktree-derived facts that currently receive only the control root; classify this as a general dual-root prompt API defect or a research-venue-only defect.
3. Inspect exact `objective` and generic artifact-path consumers/writers now that `target_venue` has a concrete split-root result; distinguish protected authority from evidence descriptors.
4. Return to protected-state writer fencing only for actual authority writers: enumerate paths bypassing `manager_pipeline_lock`, expected-revision/CAS semantics, and crash durability.

## Exact continuation
Start with Reviewer construction and the other `RolePromptCatalog` call paths: record, for Engineer/Reviewer/Planner, which root is passed as `project_root` and which as `altitude_root`, and whether stage/full-pipeline checklist rendering can consume workdir evidence. Then scan every vertical `render_stage_checklist_body`/`render_full_checklist_body` hook for worktree-only facts. If research venue is the only affected consumer, keep the fix narrow; otherwise promote `descriptor_root/evidence_root` to the generic prompt/checklist contract. After that, resume exact schema tracing for `objective` and artifact-path descriptors before returning to protected-state CAS/durability.
