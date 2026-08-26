# Open Source clean_g1 — RUN_20260826_1058_BACKEND_SCOPED_CONTROL_WRITE

Frozen semantic invocation tuple: note main `ebcfa779ac2634d1ded90b37c6d1d4104d0581bb`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. The note main advanced after semantic freeze; later Note reads were limited to SHA-only head resolution plus the role's own current `LATEST.json` for safe write sequencing. Inputs remained own clean state plus public sources only. No O/O-derived, other-worker, downstream comparator/integrator/index/feed/audit, aggregate-ledger, other-role, or legacy/pre-independence semantic state was read. The configured own sanitized feedback path did not exist at the frozen head, so no feedback was consumed.

Public Argus source remained current `main` at `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` during this invocation.

## Finding A — venue research cannot currently get the needed writes while physically denying only control-state writes

`argus_skill/verticals/research/venue_research.py::_build_prompt()` gives a model one mixed write task: create `research/VENUE_SELECTION.md`, create `research/VENUE_PROFILE.json`, and also update only the descriptive `target_venue` field in `.argus/PIPELINE_STATE.json`, while relying on prompt text not to edit `current_stage` or stage statuses. `research_venue_profile()` runs that prompt through `gateway_run_exec()` with project root as `working_dir`, `full_auto=True`, `live_search=True`, and no explicit `sandbox_mode` or `isolate_workdir`.

This is a current product path rather than a dormant example. `argus_skill/verticals/research/library_preparation.py` invokes venue research during ordinary non-exploratory paper missions at research/plan/benchmark/run/analysis when an explicit non-built-in venue still needs a profile.

The runner's global access chokepoint then shows why enabling the existing sandbox is not enough:

- `AgentCliRunner.run_exec()` applies `_apply_sandbox_policy()` before spawn.
- With `ARGUS_SKILL_SAFE_MODE` unset/false — the tested default — `_apply_sandbox_policy()` forcibly clears `sandbox_mode`/`isolate_workdir`, sets `dangerous_yolo=True`, and turns `full_auto` off for every backend.
- With safe mode on, non-Codex backends are returned unchanged by the central engineer-sandbox conversion. For this venue call they therefore keep no read-only restriction while retaining `full_auto=True`. The backend builders map that to write-capable/noninteractive behavior: Claude/Qoder use accept-edits, Copilot allows all tools when not read-only, OpenCode selects its full-access agent, Grok uses yolo, and DSH maps every non-read-only call to `danger-full-access`. Pi is not narrowed to its explicit read-only tool set unless `sandbox_mode == "read-only"`; this run does not claim more about Pi's provider-default tool surface than that absence of an Argus-enforced read-only restriction.
- With safe mode on and Codex engineer sandbox configured to `workspace-write`, `-C <project-root>` is the writable workspace. That keeps the needed research artifacts writable but also keeps `.argus/PIPELINE_STATE.json` writable because it is inside the same project root.
- Switching that Codex invocation to `read-only` would deny the same model the writes to `research/VENUE_SELECTION.md` and `research/VENUE_PROFILE.json` that constitute the feature's output.

The public sandbox tests independently lock much of this behavior: safe mode OFF grants every tested backend the legacy full-access policy; the engineer sandbox is default-OFF; the central conversion deliberately skips non-Codex backends; and Codex workspace-write roots writable access at `-C`.

**Consequence:** the current single-workdir permission model does not express the needed authority: “write venue artifacts, but never raw-write host control state.” A path/field-specific host mediation boundary is not merely defense-in-depth for this feature; it is the missing permission shape.

Scope: source-level authority analysis only. No model was executed to corrupt or modify stage/control state, and this does not claim a reproduced exploit.

## Finding B — current stage-authority tests protect stage semantics, not raw control-file write authority

Argus has a real and useful prompt-level stage authority cleanup:

- the built-in Planner role says Manager alone changes `.argus/PIPELINE_STATE.json` and project stages;
- research Planner fragments explicitly say not to edit the pipeline file and that Manager owns rollback;
- `tests/test_stage_authority_prompts.py` guards removal of old Engineer/Reviewer/Planner instructions to advance/rollback stage state and checks that the auto-research Engineer skill still marks stage fields Manager-owned.

But the research Engineer contract in `auto-research-pipeline.md` intentionally permits direct updates to descriptive fields such as objective, target venue, and artifact paths. The same physical JSON therefore remains model-writable by design even though stage fields are semantically Manager-owned. The tests do not prove field-level write isolation, because a process that can rewrite the JSON can physically rewrite both classes of field.

A path-scoped GitHub code search of `argus_skill/verticals/research/skills/engineer` finds exactly two current Skill files referencing `PIPELINE_STATE.json`:

1. `auto-research-pipeline.md`, which explicitly defines the mixed-ownership contract;
2. `research-results-analysis-and-figures.md`, whose final verification text says “Only then advance analysis/narrative state in `.argus/PIPELINE_STATE.json`.”

The second phrase is now a targeted ambiguity, not yet a demonstrated stage-authority violation. Public search did not reveal a separately named “narrative state” schema in this pass. It must be traced before deciding whether it means a descriptive marker, stage-adjacent state, or obsolete wording.

Separately, `venue_research.py` constructs a third model-facing instruction dynamically and explicitly requests the `target_venue` mutation. Therefore enumerating only static Engineer Skill markdown misses at least one active raw-write instruction.

## Finding C — candidate `clean-os-g1-005` now needs a backend-agnostic scoped write boundary

The candidate is refined from “separate control vs descriptor authority” to the more operational requirement below.

### Required invariant

A model subprocess may write product artifacts in its assigned project workspace, but must not hold raw write authority to the host-control object at all. Descriptive/control promotion must occur through a narrow host mediator that validates schema and expected state before committing through the same centralized mutation authority used by stage/route writers.

For venue research, the minimally disruptive migration is:

1. Model writes `research/VENUE_SELECTION.md` and `research/VENUE_PROFILE.json` only.
2. The selected profile key is treated as a proposal derived from that validated profile, not as authorization to rewrite `.argus/PIPELINE_STATE.json`.
3. Host verifies the profile is loadable/source-backed and normalizes its key.
4. Host promotes only `target_venue` through an allowlisted patch schema under the authoritative pipeline lock/CAS boundary.
5. A proposed patch containing `current_stage`, per-stage status, route/vertical authority, revision, capability state, or unrelated fields is rejected with control state unchanged.

A more general compatibility design may split `PIPELINE_CONTROL.json` (host-owned) from a model-writable descriptor/evidence object, but filenames are not the invariant. If one physical control file is retained, the process boundary must make raw model writes to that file impossible and expose only a scoped host patch tool/API.

### Why this must be backend-agnostic

Current backend policy is heterogeneous. A fix that depends only on Codex `workspace-write` does not cover Claude/Qoder/Copilot/OpenCode/Pi/Grok/DSH, and even Codex workspace-write grants the whole project root. Therefore the authority boundary should live above provider CLI permission differences — ideally in the host state architecture and mutation API — rather than trusting each backend to honor a prose-only “edit only field X” rule.

## Finding D — write-time tests should be added alongside existing stage-prompt tests

The existing tests are good regressions for semantic role instructions but do not falsify raw-write authority. The candidate's minimum regression matrix now includes:

1. Venue research still creates/updates `research/VENUE_SELECTION.md` and `research/VENUE_PROFILE.json` when the host control object is not model-writable.
2. The same model process cannot directly alter host control bytes, including when global safe mode is OFF.
3. A valid source-backed venue profile is promoted by host to only the normalized `target_venue` field.
4. A malformed or over-broad proposal containing `current_stage`, stage status, route/vertical, revision, or unrelated keys is rejected and leaves host control byte-identical.
5. Two host promotions from the same expected revision cannot both commit; the stale one fails with no write.
6. Backend matrix covers Codex, Claude, Qoder, Copilot, OpenCode, Pi, Grok, and DSH at the Argus policy layer; unsupported native isolation must not silently fall back to raw control-file write access.
7. Existing Manager-only stage authority and read-side completion revalidation remain independent of this new descriptor-promotion gate.
8. Existing venue-research behavior still fails closed on unverifiable venue information rather than fabricating a profile.

## Finding E — current generic file writer still does not solve coordination or durability

`argus_skill/core/pipeline_state.py::write_pipeline_state()` writes a same-directory temporary JSON and uses `os.replace()`. It has no expected revision/digest, no compare-and-swap, no shared inter-process serialization primitive inside the writer, and no file or parent-directory fsync. This remains consistent with the prior candidate refinement: splitting model authority without centralizing host writers would solve only one half of the problem.

The intended final bundle remains:

- model/control authority partition;
- all host pipeline writers routed through one mutation authority;
- documented lock order/reentrancy contract;
- exact expected-state revision/digest check;
- one-shot scope-bound privileged transition capability where needed;
- deterministic evidence validation before privileged semantic transition;
- semantic mutation + revision increment + capability consumption + idempotent receipt at one authoritative commit point;
- stale/replayed/mismatched authority or failed evidence validation => no write;
- exact replay after a successful commit => return the committed receipt, not a second transition;
- explicit atomic-visibility versus crash/power-loss durability guarantees.

## Tested scope / uncertainty

- Argus public source: `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e`, verified current public main during this invocation.
- No unauthorized control mutation, exploit, race, deadlock, or power-loss experiment was executed.
- The statement that safe-mode OFF grants the tested legacy full-access policy is directly encoded and regression-tested. Backend-specific native semantics beyond Argus's command/env construction are not generalized beyond the source shown.
- For Pi specifically, the source proves only that Argus does not force the read-only tool list for this venue call; this run does not infer the exact provider-default writable tool set without additional source evidence.
- `research-results-analysis-and-figures.md` contains state-update wording, but its intended schema/authority remains unresolved and is not classified as a stage-authority violation yet.
- A control/descriptor split and host promotion API remain an untested Argus adaptation, not a measured improvement.

## Nonempty frontier

1. Trace the `research-results-analysis-and-figures.md` “analysis/narrative state” instruction to the actual expected JSON fields and determine whether it conflicts with current Manager-owned stage semantics or is only descriptive/obsolete wording.
2. Enumerate dynamic model prompts outside `skills/engineer/` that can request project-control mutations, using code search for `PIPELINE_STATE.json`, `write`, `update`, `advance`, and `rollback` patterns; classify each as model-direct, host-mediated, or read-only.
3. Trace the effective writable surface for venue research through each backend with safe mode ON/OFF and any native provider isolation; preserve Argus source facts separately from provider assumptions.
4. Sketch a backward-compatible migration in which old mixed state is read once under host lock, host-control fields move to an exclusive control object, descriptive fields are copied to a descriptor/evidence object, and all later promotions use schema+CAS mediation.
5. Audit admin/direct host writers (`argus learn`, standalone math objective, verification policy, classification diagnostics, compatibility migration) for live-owner fencing and the centralized mutation boundary.
6. Prototype/test path-level control immutability plus descriptor promotion without changing normal venue-research outputs.
7. Retain the prior file-durability and one-shot capability frontier after authority partition is closed.

## Exact continuation

First resolve the ambiguous `research-results-analysis-and-figures.md` instruction by tracing every expected analysis/narrative field into current pipeline-state readers/writers/tests. Then enumerate dynamic model-facing control mutations outside static Engineer skills and build a backend-by-backend write-authority matrix for venue research. Use those results to specify a backward-compatible control/descriptor migration that physically removes model raw-write authority while preserving required project-artifact writes. Preserve demonstrated current source behavior, external precedents, and untested adaptation as separate evidence classes.
