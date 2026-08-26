# Open Source Systems Scan — research charter root gate follow-up

Run: continuation of the 2026-08-26 15:02 JST physical invocation.
Role: `open_source`.
Frozen semantic control tuple remains note main `b448726ce9420fd51974e70df965c4e6e3fb68e4`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains pinned to `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Stronger finding: the wrong root can weaken a deterministic stage gate, not only prompts/preparation
The prior checkpoint showed that split-root research preparation can miss the Manager-selected target and can read a stale stage. Continuing the root matrix reveals a more consequential path: for the **research stage itself**, the deterministic completion validator drops the protected state root before deciding whether the mandatory broad-research idea portfolio is required.

### The generic stage machine passes both roots correctly
`skills/stage_machine.py::_ensure_stage_completion()` calls the active vertical completion validator with:

- `project_root = evidence_root or project_root` for artifacts, and
- `state_root = project_root` for Manager-owned state.

This is the correct two-root contract. Normal `advance_stage(..., evidence_root=workdir)` therefore has enough information to enforce a protected-root charter against workdir evidence.

### The research validator uses the state root for later stages, but not for the research-stage portfolio gate
`verticals/research/stages.py::stage_completion_issues(stage, project_root, state_root=None)` does the right thing for the later research pipeline:

- plan / analysis / draft / review / submission resolve `research_target_level` from `state_root or project_root` before checking argument organization;
- analysis / draft / review / submission likewise resolve the target from `state_root or project_root` before publication-scale checks;
- `iteration_assessment(...)` also resolves its target directly from the required `state_root` argument.

But after those branches, the research-stage path is:

```text
if normalized != "research": return ()
return idea_portfolio_completion_issues(project_root)
```

The received `state_root` is discarded.

### `idea_portfolio_completion_issues()` then asks the workdir whether the charter requires a portfolio
`verticals/research/idea_portfolio.py::idea_portfolio_completion_issues(project_root)` begins:

```text
if not portfolio_required(project_root):
    return ()
```

and `portfolio_required(project_root)` reads both:

- `research_target_level`, and
- `research_direction_mode`

from that same supplied root. It requires the portfolio only when target is `publishable` or `doctoral` and direction is not `locked`.

In production split-root operation, those Manager route fields are persisted in the protected state root. The fresh execution workdir is intentionally not kept synchronized after migration. Therefore a fresh broad publishable/doctoral research campaign can present:

- protected state root: `research_target_level=publishable|doctoral`, `research_direction_mode=broad`, `current_stage=research`;
- workdir: no current Manager pipeline state, or a stale compatibility copy.

The research-stage validator receives both roots from the generic stage machine, but sends only the workdir into `idea_portfolio_completion_issues`. With no workdir target, `portfolio_required()` returns false and the portfolio validator returns **zero issues**.

So a normal Manager-owned `advance_stage(state_root, target_stage="plan", evidence_root=workdir)` can satisfy its deterministic research-stage validator without the broad publishable/doctoral portfolio requirement solely because the charter was looked up in the wrong root. This is a fail-open **completion-gate scope error**, not merely a missing prompt hint.

No live campaign was mutated and this exact bypass was not executed; the claim is source-level reachability on the pinned public commit.

## The preparation defect and gate defect reinforce each other
`verticals/research/library_preparation.py` also reads `research_target_level(context.workdir)` and calls `portfolio_required(context.workdir)`. On a fresh split-root campaign, it can therefore skip forming the 12-route / independent-review idea portfolio in the first place.

This creates a coherent failure chain:

1. Manager commits a broad publishable/doctoral research charter under the protected state root.
2. Library preparation consults only the workdir; missing target means `portfolio_required=False`, so the portfolio is not formed.
3. Later, if Planner/Manager requests research -> plan based on the semantic work completed, the generic stage machine invokes deterministic validation with both roots.
4. Research's own research-stage validator drops `state_root` and again decides `portfolio_required=False` from the workdir.
5. The deterministic gate therefore does not repair the earlier omission.

The framework has the two-root information at both moments; the research-specific code discards it twice.

## Auto-close helper has the same missing argument
`life/supervisor/_planning_cycle_enqueue.py::_research_stage_ready_for_close(state_root, evidence_root)` correctly checks protected state to confirm vertical=`research` and current_stage=`research`, but then calls:

```text
vertical_stage_completion_issues(
    definition,
    stage="research",
    project_root=evidence_root,
)
```

without `state_root=state_root`, even though the generic wrapper supports it.

This helper additionally requires `research/IDEA_SELECTION.json` and positioning/grounding files before it returns true, so a **fresh completely missing portfolio will not auto-close through this helper alone**. Scope must stay exact. However, once selection artifacts exist or are stale from another charter, the helper still validates the portfolio requirement against the wrong root and can misinterpret a changed target/direction. It should pass `state_root` regardless.

The existing `tests/life/test_research_stage_auto_close.py` stubs `vertical_stage_completion_issues` and therefore does not exercise this two-root charter lookup. Existing idea-portfolio tests also construct one root containing target, direction, stage, and evidence together.

## Direction-mode asymmetry under stale copies
The wrong-root read can fail in either direction:

- protected `broad`, stale workdir `locked` -> required broad portfolio can be incorrectly waived;
- protected `locked`, stale workdir `broad` with a publishable/doctoral target -> portfolio can be incorrectly required;
- fresh workdir with no target -> `portfolio_required=False`, the most direct false-negative case.

The protected state semantics are intentionally monotonic in one important direction: `persist_vertical` refuses to downgrade an existing `broad` research direction to `locked`. That makes the protected root especially important; a stale workdir should not be allowed to reintroduce a logically older `locked` value into gate decisions.

## Two-root contract audit result
The root matrix is now clearer:

| Concern | Correct authority/evidence split in current source | Status |
| --- | --- | --- |
| Planner stage / route | protected state root / workdir facts | correctly split |
| Reviewer target level + verification profile | protected state root / workdir facts | correctly split |
| Later research stage completion (argument/publication scale) | target from state root / artifacts from workdir | correctly split |
| Final iteration assessment | target from state root / result+artifacts from workdir | correctly split |
| Research Skill-library stage | should be state root / workdir artifacts | **currently reads workdir** |
| Dynamic venue target for preparation | should be state root / profile in workdir | **currently reads workdir** |
| Broad research portfolio required? | should read target+direction from state root / portfolio artifacts from workdir | **currently reads workdir** |
| Research-stage portfolio completion gate | should read charter from state root / portfolio artifacts from workdir | **currently drops state root** |
| Auto research-stage close helper | already has both roots | **fails to pass state root to validator** |
| Math objective | needs both protected/evidence copies for its validator | explicit host-mediated dual-root projection already exists |
| Legacy project checklist store | historical read-only compatibility data tied to whichever root is supplied | not a current Planner mutation channel; do not generalize as a new control writer |

The core framework already demonstrates the preferred API shape elsewhere: `VerticalContract.prepare_mission(...)` and `VerticalContract.assess_iteration(...)` both receive explicit `project_root` and `state_root`, while `VerticalLibraryContext` is the anomalous single-root context.

## Refined adaptation for `clean-os-g1-005`
Keep the previous dual-root venue/checklist changes and add the deterministic charter gate explicitly:

1. Extend `VerticalLibraryContext` with `state_root` and compute its `stage` from the protected root.
2. Change `portfolio_required(evidence_root, *, state_root=None)` so target/direction resolve from `state_root or evidence_root` and artifact work remains in `evidence_root`.
3. Change `idea_portfolio_completion_issues(evidence_root, *, state_root=None)` and thread `state_root` into `portfolio_required`.
4. In `research.stage_completion_issues`, call `idea_portfolio_completion_issues(project_root, state_root=state_root)` for the research stage.
5. In `_research_stage_ready_for_close`, pass `state_root=state_root` to `vertical_stage_completion_issues`.
6. In research library preparation, decide whether portfolio is required using `context.state_root`, but create/read portfolio artifacts under `context.workdir`.
7. Preserve normalized target/profile identity checks for dynamic venue resolution and do not mirror the whole protected pipeline object into the workdir.
8. Keep same-root direct/legacy calls backward compatible by defaulting `state_root` to the evidence/project root.

## Minimal new regression tests
- Split roots: state root has research + publishable + broad; workdir has no pipeline state. `stage_completion_issues("research", workdir, state_root=state_root)` must report missing/invalid idea portfolio, not `()`.
- Same state root but direction=`locked`: missing portfolio is allowed.
- Stale workdir says `locked`, protected root says `broad`: protected root wins and missing portfolio blocks.
- Stale workdir says `broad`, protected root says `locked`: protected root wins and missing portfolio does not block.
- `advance_stage(state_root, target_stage="plan", evidence_root=workdir)` must fail closed on a broad publishable/doctoral charter with missing portfolio.
- `_research_stage_ready_for_close` must pass its protected root through to the real validator; avoid mocking away the root-sensitive behavior.
- Existing single-root idea-portfolio and research-stage tests remain valid.

## Scope limits
- This is a source-level two-root contract defect at exact public commit `16bb128...`; no live unauthorized transition or lost research campaign was reproduced.
- `_research_stage_ready_for_close` is not claimed to auto-close a completely missing portfolio because it separately requires a selection artifact before invoking the validator.
- The stronger normal `advance_stage` reachability is independent of that helper because `_ensure_stage_completion` already calls the research validator with both roots.
- Current Planner and Reviewer prompt target-level resolution use the protected root correctly; do not generalize this defect to every research policy read.

## Frontier
1. Trace whether `research_target_level` / `research_direction_mode` are deliberately projected into the workdir anywhere after Manager classification; if not, treat workdir reads in research preparation/portfolio as unequivocally wrong rather than compatibility-dependent.
2. Trace all consumers of workdir `target_venue` and determine whether the model-authored compatibility field can be deleted entirely after a two-root resolver is introduced.
3. Add root ownership to the project checklist-store matrix: distinguish historical workdir stores from current protected-root checklist rendering and avoid resurrecting deprecated Planner checklist mutation.
4. Inspect every vertical hook context for dual-root parity: mission prelude and iteration assessment are already dual-root; library preparation is not. Search for any second hook with the same omission.
5. Then return to protected-state mutation fencing (single mutation authority, expected revision/digest CAS, one-shot capability, crash durability) after the read-side root contract is complete.

## Exact continuation
First search for any host-side post-classification projection of `research_target_level`, `research_direction_mode`, or `target_venue` into the execution workdir; classify each as authority, compatibility projection, or absent. Then enumerate all `VerticalLibraryContext` constructors and `library_preparer` providers to prove whether research is the only concrete behavior affected. Finally inspect the project checklist store and any other vertical hook contexts for missing `state_root`; if no second behavioral defect appears, freeze the two-root read-side design and resume the separate protected-state CAS/capability durability branch.