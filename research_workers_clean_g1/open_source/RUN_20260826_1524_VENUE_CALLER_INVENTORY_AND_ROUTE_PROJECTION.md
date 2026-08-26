# Open Source Systems Scan — venue caller inventory + route projection audit

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `35d595e6d6b18bd0fb6953063957f74a7e57662f`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (verified current public `main` during this run).
Independence: no O/O-derived state, other-worker state, downstream state, legacy research, aggregate ledger, or other-role receipts/configs were read.

## Result 1 — venue-dependent production caller inventory is now bounded
A repository-wide code search for `resolve_venue_profile(` at the pinned public commit finds exactly these production modules:

1. `verticals/research/stages.py`
2. `verticals/research/reviewer_simulation.py`
3. `verticals/research/paper_layout_review.py`
4. `verticals/research/academic_language_review.py`
5. `verticals/research/paper_infrastructure_review.py`
6. `verticals/research/paper_structural_minimums.py`

No second hidden production resolver caller was found. This lets the split-root venue fix be scoped to a finite read-side surface rather than a whole-framework rewrite.

### Deterministic stage blocker
`paper_structural_minimums` is the load-bearing deterministic path. `stages.stage_completion_issues(...)` invokes it for `draft`, `review`, and `submission` with the evidence/workdir `project_root`; the protected `state_root` is not threaded into the structural venue resolver. This is the previously identified source-reachable failure:

- built-in Manager target exists only in protected state -> workdir resolver sees no target -> `unresolved_venue_profile` blocks stage completion;
- dynamic workdir profile + workdir descriptive key can be internally self-consistent without proving identity against the protected Manager target.

This remains the first patch priority.

### Deterministic tool-level validator, but not a stage-machine caller
`reviewer_simulation.validate_reviewer_simulation(project_root)` also resolves venue from one root. An unresolved venue is emitted as a structural issue and the CLI exits non-zero. However repository call-site search found no production stage-machine invocation of this validator; direct function references are its own module plus tests. Treat it as a deterministic standalone/skill validator whose split-root behavior should be aligned, not as evidence of a second current stage-transition blocker.

### Advisory / model-backed review generators
- `paper_layout_review.generate_layout_review(project_root, ...)` resolves venue directly from `project_root`; an unresolved venue raises before a review artifact is produced. Search for `LAYOUT_REVIEW.json` found no separate production consumer outside the generator, so this is not currently a deterministic stage gate.
- `academic_language_review.generate_academic_language_review(project_root, ...)` also resolves from one root. The stage checklist explicitly labels `paper/ACADEMIC_LANGUAGE_REVIEW.json` as **advisory** and says the reviewer-agent checklist is the source of truth. Its split-root failure can remove advisory evidence or break an invoked review skill, but should not be described as a deterministic host quality verdict.
- `paper_infrastructure_review.generate_paper_infrastructure_review(project_root, ...)` catches unresolved venue and records it as a blocking issue inside that review artifact. `prompt_policy` tells Planner to trust a fresh model-backed infrastructure review and regenerate it if stale/missing, so this can impede model-facing workflow, but no `stage_completion_issues` call-site was found for the review generator itself.

### `stages.py` is a separate semantic/checklist surface
The stage module resolves venue for venue-dependent checklist rendering (`draft`, `review`, `submission`). Existing `test_stage_checklists_venue.py` constructs a single root containing both `PIPELINE_STATE.json` and the project artifacts; it verifies explicit/missing/unknown venue behavior but does not exercise protected state root + execution evidence root. Therefore current tests do not cover the production split-root shape for dynamic profiles or built-in protected targets.

## Result 2 — fresh split-root workdir route fields are absent by design, not merely “not yet observed”
The continuation asked whether host code might silently project `research_target_level`, `research_direction_mode`, or `target_venue` into the execution workdir after Manager classification.

Exact-key assignment searches on the pinned repository found:

- pipeline `payload["research_direction_mode"]` assignment only in `skills/vertical_select.py`;
- pipeline `payload["target_venue"]` assignment only in `skills/vertical_select.py` (other hits are tests);
- pipeline `payload["research_target_level"]` assignment in `skills/vertical_select.py`; `publication_scale.py` has an identically named field in its own assessment artifact, not a pipeline-state projection.

Manager `_vertical_ops.py` calls `persist_vertical(self.project_root, ..., research_target_level=..., research_direction_mode=..., target_venue=...)`. The route is therefore persisted to the protected Manager root. No normal call of `persist_vertical(self.execution_workdir, ...)` was found, and no second direct assignment path for those route keys was found.

Generic pipeline writers (`stage_machine`, verification-policy and classification diagnostics, etc.) can preserve keys already present in the object they read, but the source search found no code that synthesizes these three route fields into a **fresh** execution-workdir state after classification. The one-time Manager-state migration direction is legacy workdir -> protected state root, not a continuing protected-root -> workdir mirror.

Conclusion: for a fresh production split-root campaign, absence of these route fields from the execution workdir is the intended current architecture. A stale/legacy workdir may still retain old copies, which is worse than relying on a mirror because freshness is not guaranteed. Read-side consumers must therefore not treat the workdir route copy as authority.

## Result 3 — two-root venue patch set can now be frozen narrowly
Do **not** mirror `target_venue` back into the workdir as the primary fix. That would create two mutable authority copies and preserve stale-write ambiguity.

A narrower compatible patch surface is:

1. Change the venue resolution seam to support protected authority plus artifact evidence, e.g. `resolve_venue_profile(authority_root, *, evidence_root=None)`.
2. Read `target_venue` only from `authority_root` (except the documented host environment override).
3. Built-in target: resolve registry profile from protected identity; no workdir pipeline copy required.
4. Dynamic target: load `research/VENUE_PROFILE.json` from `evidence_root or authority_root`; accept only when normalized profile identity equals the protected target; missing/mismatch fails closed.
5. Thread `state_root` through `validate_paper_structural_minimums` and the `draft/review/submission` deterministic stage gate first.
6. Give `reviewer_simulation` and the three model-backed review generators an optional protected `state_root`/explicit resolved `venue` so invoked tools use the same authority/evidence split; same-root CLI use remains backward compatible.
7. Update venue-dependent checklist/role rendering so Manager-owned identity comes from protected state and dynamic profile evidence comes from the execution workdir.
8. Remove the venue-research instruction that asks the model to rewrite workdir `.argus/PIPELINE_STATE.json`; model output should be source-backed `VENUE_SELECTION.md` / `VENUE_PROFILE.json`, with host-side identity comparison.
9. Keep target-level handling already done correctly in `stage_completion_issues`: it resolves the research target from `state_root or project_root` and passes the explicit target into `publication_scale_issues(project_root, research_target_level=target)`.

## Regression matrix
- split-root built-in AAAI/ICLR/EMNLP protected target + no workdir route state -> correct venue rules resolve;
- stale workdir `target_venue` disagrees with protected built-in target -> protected target wins;
- protected dynamic target + matching workdir profile -> accepted;
- protected dynamic target + self-consistent but different workdir key/profile -> fail closed;
- protected dynamic target + missing/malformed profile -> fail closed naming protected target;
- same-root existing tests remain unchanged;
- deterministic structural stage validation and reviewer-simulation/tool generation resolve the same venue identity;
- checklist rendering and deterministic gate agree under split roots;
- no new protected-root -> workdir route mirror is introduced.

## Scope limits
This is source-level reachability and call-site inventory on the pinned public commit. No live campaign was mutated and no split-root failure was reproduced end-to-end. The claim is architectural: the current code paths permit the identified read-side mismatch and current tests are single-root for venue checklists. It is not a claim that every live campaign is currently failing.

## Exact continuation
Resume the separate mutation-authority branch now that the venue/read-side patch surface is bounded. Enumerate every production writer of `.argus/PIPELINE_STATE.json` and classify by protected-root vs execution-workdir target, outer-lock coverage, expected prior revision/digest/CAS, and whether a model can reach the write path directly. Re-check the concrete external writers already identified (`argus learn`, standalone math objective) and the model-writable workdir evidence copy. Then design the minimal common mutation authority that preserves existing outer locks while adding exact-prior-state fencing/one-shot authority where needed, and audit `write_pipeline_state` crash durability (file fsync + parent-directory fsync) separately from atomic visibility.