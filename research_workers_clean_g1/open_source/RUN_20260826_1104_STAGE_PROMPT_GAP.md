# Open Source clean_g1 — RUN_20260826_1104_STAGE_PROMPT_GAP

Same frozen semantic invocation as the immediately preceding 10:58 checkpoint: note `ebcfa779ac2634d1ded90b37c6d1d4104d0581bb`, control revision 9, open_source config revision 5. This is a continuation checkpoint from public Argus source only.

## Resolved part of the prior ambiguity

Current public Argus `main` remains `962cb06554daaede17b786c495e13ee3b6530e6e`.

`research-results-analysis-and-figures.md` ends its verification procedure with:

> Only then advance analysis/narrative state in `.argus/PIPELINE_STATE.json`.

The current generic stage machine defines the authoritative state shape relevant to advancement as `current_stage`, `stages[<stage>].status`, and `stage_history`; for the research vertical, `analysis` is a canonical pipeline stage. Repository-wide code search at this pinned revision returns zero definitions/usages for symbols `analysis_state` and `narrative_state`. No separate dedicated “narrative state” field was identified in the current pipeline-state API.

At the same revision, the built-in Planner role says Manager alone changes `.argus/PIPELINE_STATE.json` and project stages, and `tests/test_stage_authority_prompts.py` explicitly describes the Manager as the sole writer of `current_stage` after initialization. That regression test checks removal of the old Engineer advance wording only in `auto-research-pipeline.md`; it does not inspect `research-results-analysis-and-figures.md`.

**Classification:** the analysis Skill's final sentence is a current authority-contract gap. It is at minimum undefined/stale wording because the named `analysis/narrative state` schema does not exist; if interpreted as the existing analysis stage/status, it conflicts with the Manager-only stage contract. It should not be treated as evidence that Engineers are intentionally authorized to advance pipeline stages. A safe cleanup is to replace it with an artifact-local completion statement or “report readiness to Manager,” while leaving actual stage advancement to the existing Manager host path.

Scope remains source-level. This run did not execute an Engineer and did not reproduce an unauthorized stage write.

## Dynamic-prompt enumeration refinement

A GitHub code search scoped to `argus_skill/verticals/research/skills/engineer` finds exactly two current Skill files that mention `PIPELINE_STATE.json`: `auto-research-pipeline.md` and `research-results-analysis-and-figures.md`.

A separate current-code search for Python files containing both the `.argus/PIPELINE_STATE.json` literal and `RunnerOptions` returns `venue_research.py`, `manager/skill_tidy.py`, and its tests. The post-mission Skill-tidy reviewer explicitly says not to edit project/session state and withholds candidate procedures that name `PIPELINE_STATE.json`; it is therefore not another positive example of a model being asked to mutate project control. `venue_research.py` remains the concrete generated-prompt path found in this pass that positively asks a model to update the project pipeline file.

This is not claimed as a proof that no other dynamically composed mutation instruction exists: prompts may refer to state without the exact filename literal, and role Skills can be included indirectly. The next scan should therefore search semantic action verbs plus state API names, not only exact path strings.

## Candidate impact

`clean-os-g1-005` gains two separate migration obligations:

1. **Physical authority partition:** model subprocesses must be unable to raw-write host control even when product artifacts in the same project need writes.
2. **Prompt-contract cleanup:** all model-facing Skills/prompts must stop telling non-Manager roles to “advance” undefined/control state; descriptive proposals should be written to artifact-local schema and promoted by host.

Prompt cleanup without physical partition is insufficient, because venue research still needs a current positive model write to the mixed-ownership file. Physical partition without prompt cleanup is also insufficient, because stale instructions would create repeated denied writes/failures.

## Exact continuation

Enumerate model-facing control-mutation instructions that do not contain the exact pipeline filename: search for stage/status/vertical/objective/venue mutation verbs in role Skills and dynamically built prompts, classify each as host-mediated, model-artifact proposal, raw file write, or stale/ambiguous wording. Then produce a backend-independent migration matrix showing which current model outputs move to descriptor/evidence artifacts and which host control fields are promoted under schema+CAS. After that resume the host-writer/live-owner fencing and durability frontier.
