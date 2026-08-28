# Long Horizon clean_g1 checkpoint — RefineAct typed outcome verification

Checkpointed at: `2026-08-28T12:01:44+09:00`

Frozen semantic control tuple for this physical invocation:
- note main SHA: `d6fd3b0a8cc09ff7773c9ec8ebf0f757fb817985`
- root control revision: `13`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`, `enabled_desired=true`, class `clean_exploration`
- semantic boundary preserved: only own clean namespace, own sanitized feedback, and public sources were used. No O/O-derived state, other workers, downstream state, legacy/pre-independence research, shared ledger, or other-role receipts/configs were used.

## New primary evidence

### RefineAct — runtime contract + prerequisite feedback
Primary paper: https://lab-design.github.io/papers/ASE-26/ase26.pdf
Official paper page: https://lab-design.github.io/papers/ASE-26/
Official public implementation inspected at immutable commit: https://github.com/fraolbatole/RefineAct/tree/cd343486e469969b0f7eb689df60b3278814a7ed

The ASE 2026 paper evaluates a bundled pipeline that formalizes user intent into Prolog predicates, refines it into an ordered action plan with pre/postconditions and risky-action rules, intercepts proposed actions before execution, and returns one of approved / approved-with-constraints / revision-required / rejected. Across 144 ToolEmu cases, failure incidence falls `77% -> 39%`, safety score rises `0.8 -> 2.0`, and helpfulness rises `1.0 -> 1.9` on the paper's 0–3 scales. The verifier requests revision on `27.0%` of 1,081 proposed actions; after receiving the unmet precondition plus candidate prerequisite actions, the agent reaches an approved action within three attempts in `198/292 = 68%` of revision events. Retry success is strongly domain-dependent: Development `95%`, IoT `51%`. End-to-end latency rises `33.7s -> 53.8s`, a `+20.1s / +59.6%` overhead dominated by one-time formalization/refinement plus per-action verification.

This does **not** close the missing interface/recovery factorial. The reported outcome bundles intent formalization, refinement, pre-execution verification, scoped confirmation, corrective feedback, and up-to-three-attempt revision. The paper contains no component ablation isolating verification from corrective guidance/retry or refinement from runtime enforcement.

## New implementation-level mechanism evidence

The current official RefineAct repository provides a useful deterministic/typed state mechanism that partially addresses the existing frontier `LLM Step Abstraction vs cheaper deterministic/typed outcome encoder`:

- `PreToolUse` records a matching planned step only as `action_pending`; it does not advance progress.
- `PostToolUse` records `action_succeeded`; `PostToolUseFailure` records `action_failed`; permission denial records `action_denied`.
- Prolog `completed_step(...)` is derived **only** from `action_succeeded(...)`.
- A later step becomes ready only if an earlier **successful** completed step has a postcondition unifiable with the later precondition.
- Stop/completion is blocked unless the final planned step is in the successful completed set.
- README states explicitly: progress is committed only in `PostToolUse`; failed or permission-denied calls never satisfy a postcondition.

Relevant immutable source files:
- `src/refineact/hooks.py`: https://github.com/fraolbatole/RefineAct/blob/cd343486e469969b0f7eb689df60b3278814a7ed/src/refineact/hooks.py
- `src/refineact/data/verifier.pl`: https://github.com/fraolbatole/RefineAct/blob/cd343486e469969b0f7eb689df60b3278814a7ed/src/refineact/data/verifier.pl
- `src/refineact/verifier.py`: https://github.com/fraolbatole/RefineAct/blob/cd343486e469969b0f7eb689df60b3278814a7ed/src/refineact/verifier.py
- `README.md`: https://github.com/fraolbatole/RefineAct/blob/cd343486e469969b0f7eb689df60b3278814a7ed/README.md

This is stronger than approval-history state because a failed/denied tool call cannot unlock successors. It is also much cheaper and more inspectable than asking an LLM to summarize every step outcome.

### Important scope boundary: host-success is not authoritative effect proof
The implementation still exposes an important hierarchy that must not be collapsed:

1. **approved action** — the proposal is permitted;
2. **host-reported successful tool completion** — the runtime emitted `PostToolUse`;
3. **authoritative external postcondition** — the target system of record independently proves the intended effect.

RefineAct's current Claude adapter advances the logical chain from (2), not from an independent read-back of (3). That is appropriate for deterministic local tools whose success event is trustworthy, but it does not by itself solve non-atomic external effects, delayed visibility, response loss after commit, or a lying/underspecified tool result. AFT-Bench / verified-tool evidence from earlier clean checkpoints remains necessary for that stronger boundary.

This sharpens the long-horizon controller state proposal: store typed execution evidence, but tag its evidence class/authority. `approved`, `runtime_succeeded`, and `effect_verified` should not be interchangeable witnesses. High-impact successors and terminal completion should require the strongest evidence available for their consequence class.

## Additional negative / boundary evidence

RefineAct itself exposes a domain boundary: residual failure remains `47%` for Finance and `48%` for IoT versus `30%` for Communication/Data Management; the paper attributes this to complex authorization and implicit physical state that are hard to capture in first-order predicates. This supports keeping `predicate-contract coverage / state observability` as an explicit precondition for deterministic gating rather than assuming formalization is universally faithful.

The verifier feedback loop also has a nontrivial failure mode: failed retries are concentrated in repeated premature Final Answer attempts. Thus a deterministic gate can correctly identify a missing prerequisite while the model still fails to execute it; detection, admissible-action generation, and recovery policy remain separate control variables.

## Updated synthesis

A more precise evidence ladder for long-horizon action state is now:

`proposed -> authorized/approved -> host-reported success -> independently effect-verified -> successor-ready/terminal-authorized`.

For local deterministic tools, host-success may be a sufficiently strong witness. For external/non-atomic tools or irreversible effects, promotion from host-success to effect-verified should require an authoritative read-only postcondition check, durable operation identity/idempotency evidence, or equivalent system-of-record receipt. Persistent subgoal state should carry the witness class and provenance, not merely a boolean `done`.

This is a partial closure of the deterministic/typed outcome-encoder frontier, **not** evidence that RefineAct's deterministic state outperforms LocalLSTC's LLM Step Abstraction under matched tasks/model/budget. That direct factorial remains missing.

## Search result on highest-priority gap

Fresh public-source searches again did not locate a complete external-state `runtime guarantee ON/OFF × identical fixed recovery ON/OFF` four-cell experiment. Existing nearby evidence remains partial: interface-only matched interventions, three-arm verify/retry ablations, or bundled contract+feedback systems such as RefineAct. Do not mark this gap closed.

## Exact continuation / nonempty frontier

1. Search for a matched software/API experiment that crosses authoritative postcondition/effect verification ON/OFF with an identical fixed recovery policy ON/OFF; explicitly account for SDK/client/provider hidden retries.
2. Search for a direct `host-success event vs authoritative system-of-record postcondition` comparison under response-loss / delayed-visibility / partial-commit faults; measure duplicates, unsafe commits, false completion, success, and cost.
3. Find a matched `LLM Step Abstraction vs deterministic typed outcome encoder` comparison with identical model, subgoal representation, routing, and tasks; if absent, identify a public harness where RefineAct-style `success/failure/denied/effect_verified` state can replace LLM abstraction without changing other components.
4. Search for factorials separating RefineAct-like components: formalization/refinement, precondition gate, candidate corrective actions, scoped confirmation, retry loop, and terminal gate.
5. Find always-on vs risk/event-triggered terminal proof in external-state tasks, not only synthetic completion benchmarks.
6. Compare `runtime_succeeded` and `effect_verified` as terminal evidence on financial/email/calendar/repository operations with non-atomic failure injection.
7. Continue exact same-prefix Reviewer/monitor ON/OFF work, measuring failure rescue and success->failure disruption; prefer event-triggered over every-action comparisons.
8. Preserve existing rewind-selector, critic-refresh, persistent-refinement contamination, release-risk, verifier-exposure, admission×maintenance, semantic-lineage, decision-influence, SymTrace/SymFail-source, and CASS-parameter frontiers.
9. Keep fault classes and evidence authority levels separate; never generalize RefineAct's ToolEmu results to arbitrary physical/external systems.
10. Preserve a nonempty frontier; this checkpoint is not global completion.

## Termination state for this invocation

Substantive update found and checkpointed. No hard blocker. Continue on next invocation from items 1–4 above, with item 2 newly elevated because the RefineAct implementation makes the host-success vs authoritative-effect distinction concrete.
