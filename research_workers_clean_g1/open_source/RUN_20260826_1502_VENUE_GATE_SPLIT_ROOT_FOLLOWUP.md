# Open Source Systems Scan — split-root venue gate follow-up

Run: further continuation of the 2026-08-26 15:02 JST physical invocation.
Role: `open_source`.
Frozen semantic control tuple remains note main `b448726ce9420fd51974e70df965c4e6e3fb68e4`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains pinned to `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Stronger finding: paper-stage deterministic validation can deadlock or validate the wrong venue under split roots
The two previous checkpoints established that protected Manager state and execution evidence are split in production, while several research preparation/checklist paths still assume one root. Tracing `target_venue` into the deterministic paper gate shows a direct later-stage consequence.

### Venue resolution is intentionally strict in one root
`verticals/research/venue_profiles.py::resolve_venue_profile(project_root)` has no implicit default venue. Its behavior is:

1. explicit host environment override wins;
2. a built-in `target_venue` from `project_root/.argus/PIPELINE_STATE.json` resolves from the built-in registry;
3. otherwise a local `research/VENUE_PROFILE.json` is accepted when there is no state key or when its normalized key matches the state key;
4. otherwise `get_venue_profile(state_key)` raises `KeyError` for missing/unknown selection.

This is a good single-root fail-closed contract: no silent EMNLP/default fallback and no local dynamic profile overriding a different same-root state key.

### Paper structural validation resolves the venue from the evidence workdir only
`verticals/research/paper_structural_minimums.py::validate_paper_structural_minimums(project_root)` calls `resolve_venue_profile(project_root)` directly. It has no `state_root` argument.

If venue resolution raises, the validator does not ignore it: it emits a blocking structural issue with code `unresolved_venue_profile` in addition to any manuscript issues.

`verticals/research/stages.py::stage_completion_issues(...)` invokes this validator at `draft`, `review`, and `submission` using the **artifact/evidence `project_root`**. Although `stage_completion_issues` itself receives `state_root`, it does not pass that protected root into the structural venue resolver.

### Fresh split-root built-in venue can therefore become unsatisfiable
Normal production construction gives:

- protected state root (`life_dir`) containing Manager route fields, including `target_venue`;
- execution workdir containing the paper and research artifacts and intentionally not synchronized with the protected pipeline state.

Manager commits `target_venue` through `persist_vertical(self.project_root, ...)`. Code search found no normal host-side `persist_vertical(self.execution_workdir, ...)` or equivalent post-classification projection of the route into the workdir. The one-time migration goes workdir -> state root, not state root -> workdir.

For a fresh split-root project with a **built-in venue** such as AAAI/ICLR/EMNLP, this yields a source-reachable sequence:

1. protected state root has `target_venue=AAAI` (for example);
2. workdir has no current Manager pipeline state and no dynamic profile is needed;
3. venue-research preparation does not create a compatibility copy, because it itself reads the workdir and sees no target;
4. at draft/review/submission, deterministic stage completion calls `validate_paper_structural_minimums(workdir)`;
5. `resolve_venue_profile(workdir)` sees neither a state key nor local dynamic profile and raises “no target venue selected”;
6. the structural validator emits `unresolved_venue_profile`;
7. stage completion remains blocked even though the Manager has a valid target in protected state.

This is a stronger failure mode than a prompt mismatch: it can make a correctly targeted built-in-venue paper **deterministically unable to close a paper stage** solely because the gate reads authority from the evidence root.

No live campaign was mutated or reproduced; this is exact source-level reachability on the pinned public commit.

## Dynamic venue has the opposite authority risk
For a non-built-in venue, `venue_research.py` asks the model to create `research/VENUE_PROFILE.json` and also to update “only the descriptive `target_venue` field” in the workdir `.argus/PIPELINE_STATE.json`.

The same-root resolver then sees only the workdir pair. If the workdir local profile and its model-authored descriptive key agree with each other, they can pass same-root identity checks even if they do **not** match the protected Manager target. The current deterministic structural validator has no protected-root input with which to compare them.

So split-root behavior is asymmetric:

- **built-in target + absent workdir copy:** false-positive blocking (`unresolved_venue_profile`);
- **dynamic local profile + self-consistent workdir descriptive key:** potentially validates rules for a venue not proven equal to the protected Manager target.

The source does not demonstrate a model actually changing venue against instructions; the second point is an authority-boundary weakness, not a reproduced wrong-venue submission.

## This explains why copying `target_venue` into the workdir is the wrong primary fix
A tempting patch is to mirror Manager `target_venue` into the workdir. That would unstick built-in validation but would preserve two mutable copies of an authority field and leave stale-write ambiguity.

The existing math-objective dual-root projection is not a reason to mirror every field. Math intentionally needs the same objective at both roots because deterministic evidence validators consume it there. For venue identity, validators can instead accept the protected authority root separately while reading profile/artifact evidence from the workdir. There is no need to make the workdir copy authoritative.

## Refined two-root venue resolver
The clean adaptation is an explicit authority/evidence API, for example:

```text
resolve_venue_profile(authority_root, *, evidence_root=None)
```

Semantics:

1. host environment override keeps its documented highest precedence (host-level override, not model evidence);
2. read `target_venue` only from `authority_root`;
3. if it names a built-in venue, resolve directly from the registry — no workdir state copy required;
4. for a non-built-in target, read `research/VENUE_PROFILE.json` from `evidence_root or authority_root`;
5. accept it only when normalized profile key equals normalized protected target;
6. missing/malformed/mismatch fails closed with a target-specific error;
7. same-root callers remain backward compatible when `evidence_root` is omitted.

Then thread the protected root into all **deterministic** venue-sensitive gates first:

- `validate_paper_structural_minimums(project_root, *, state_root=None)`;
- research `stage_completion_issues(..., state_root=...)` passes it;
- any other deterministic venue validator found by the remainder of this audit gets the same typed split.

Role-facing helpers (reviewer simulation, layout review, academic-language review, infrastructure review) can migrate after deterministic safety is correct, but should ultimately use the same authority/evidence resolver to avoid semantic disagreement between what roles are told and what gates enforce.

The model instruction to rewrite workdir `.argus/PIPELINE_STATE.json` should become unnecessary: the model can write only source-backed `VENUE_SELECTION.md` / `VENUE_PROFILE.json`; host code compares the profile key against protected target identity.

## Regression matrix additions
- Split-root built-in target AAAI in protected state, no workdir pipeline state, valid AAAI manuscript: structural validator resolves AAAI and does **not** emit `unresolved_venue_profile`.
- Split-root built-in target ICLR with a stale workdir `target_venue=EMNLP`: protected ICLR wins.
- Split-root dynamic protected target `ExampleConf 2026`, workdir profile key `ExampleConf`: accepted after normalization.
- Same protected target, workdir profile key `OtherConf`: fail closed even if workdir descriptive `target_venue=OtherConf` agrees with the profile.
- Protected dynamic target with missing profile: fail closed and name the missing target/profile, not a generic default.
- Same-root existing venue-profile tests remain unchanged.
- Draft/review/submission `advance_stage(state_root, evidence_root=workdir)` uses protected venue identity while validating workdir paper artifacts.

## Checklist-store/root matrix note
`skills/checklist_store.py` is explicitly a **legacy read path**: current Planner verdicts no longer write `checklist_ops`. It reads `research/CHECKLISTS.json` relative to whichever project root is supplied and re-injects protected seed items on read. In current split-root role rendering, the supplied root is normally protected state, while historical checklist files may have lived in the workdir. This is a backward-compatibility question, not a current Planner authority channel. It should be audited/migrated separately rather than folded into the new venue/charter authority design.

## Hook parity result so far
The core contract already distinguishes roots in the higher-risk hooks:

- mission preparation: explicit `project_root` + `state_root`;
- stage completion: evidence `project_root` + optional `state_root`;
- iteration assessment: explicit `project_root` + `state_root`.

Library preparation remains the clear anomaly: `VerticalLibraryContext` has only `workdir`, and code search found exactly one production constructor plus the research provider. No second concrete `LIBRARY_PREPARER` provider was found at the pinned commit, so behavior scope should remain research-specific while the core context field can be made generic.

## Exact continuation
Finish the venue-dependent caller inventory (`reviewer_simulation`, paper layout/language/infrastructure reviewers) and distinguish deterministic blockers from advisory/model-facing helpers. Then search for any post-classification host projection of `research_target_level`, `research_direction_mode`, or `target_venue` that code-search syntax might have missed via generic pipeline-object mutation. If none exists, mark fresh split-root workdir route fields as absent by design. Finally freeze the two-root read-side patch set and resume the separate mutation-authority/CAS/crash-durability branch.