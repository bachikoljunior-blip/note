# O / Chat continuity

Updated: 2026-08-23 JST

Mandatory continuity: proactively read this file before O-related reasoning/actions where history matters; proactively update it in the same turn when important standing context changes. Do not wait for the user. Keep it compact. Before sending new external context to O, show wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Core standing context
- Goal: materially accelerate genuine AGI; O is instrumental/replaceable.
- User has only a smartphone; automate repository/tool work and request only irreducible account-holder actions.
- Treat O and this chat as same-base-model for idea-generation overlap. This chat should seek genuine context asymmetries, not duplicate reasoning O can readily derive.
- Skill-in-Skill is a candidate recursive context-routing concept, not mandatory architecture.
- O should ingest durable user input while alive at safe semantic boundaries.
- External ideas/user proposals are hypotheses, not automatic truth.
- Optimize expected total elapsed time continuously; illustrative durations are not thresholds.

## External-context selection method
- Prefer the minimal context difference that enabled this chat to reach a useful conclusion, not the full derived solution.
- Novelty filter: if O can readily derive a candidate from its actual current context, do not send it merely because this chat generated it. Prefer external evidence, different-environment/tool observations, user-only knowledge, counterexamples, independent results, or context O structurally lacks.
- From observed behavior, separate concrete incident, latent shared pattern, minimal exposing context, and whether O already could derive it.
- Context delivery is successful only when it causally supports useful behavior/results, not merely storage, acknowledgement, summary, recall, or verbal comprehension. Distinguish delivery, comprehension, behavioral uptake, and measured effect; investigate context-to-action failure if uptake/effect is absent.
- Context is an intervention with both information value and interference cost. More context is not monotonically better: irrelevant, redundant, conflicting, or over-salient context can dilute important constraints, anchor search, consume attention/context budget, or create new rigid heuristics. Prefer minimal/gated/on-demand routing and, where consequential, compare downstream outcomes with and without the added context.
- Avoid turning “escape the current search space” into a new rigid heuristic. Excessive breadth can itself create a narrowed policy that under-explores promising regions. Exploration policy must preserve both depth and breadth, detect when either is being over- or under-used, and evaluate the tradeoff by downstream results rather than by following a fixed anti-locality rule.
- Evaluation itself is fallible context/measurement, not an oracle. A loop that improves behavior according to a wrong metric can self-reinforce the wrong direction. Distinguish “measured improvement” from “metric validity”; where consequential, validate/calibrate evaluators against external outcomes, disagreement, held-out transfer, or other partially independent signals, and treat evaluator design as an improvable/falsifiable part of the loop.

## External-context items sent to O
1. Long-lived accumulated context can suppress hypotheses/strategies available to the same base model under different context.
2. Durable state and live execution advance on different clocks; freshness/provenance/invalidation/reconciliation/decision-time context selection are structural concerns.
3. Revision 9: context selection changes judgment and is itself conditioned by previously selected context.
4. Revision 10: same-family model repeatedly failed to apply explicitly present, understood constraints in later actions; availability/retrievability is not equivalent to behavioral control. Commit `48cdbe227e1c81f0f5fbd0c1ae6c85b25194b3ce`.
5. Revision 11: successful context integration should be evaluated by whether it actually produces useful behavioral and outcome changes, not merely storage/recall/explanation. Repaired append-only representation commit `496c1bb57e5cf89b3dbf9776964274d8fb355ae7`.
6. Revision 12: autonomous scientist-agent systems with closed loops over hypothesis generation, experimentation, evaluation, and research-result inheritance have externally evaluated outputs/measured improvements; use them as external baselines and compare/test mechanisms rather than designing only from O's current internal approach. Commit `1e2ceeb86825af9f883d561071b4f231bdd1f6fc`.

## Current reflection audit
- Revision 13 is now formally acknowledged: main `WORK_EXECUTION_STATE.json` records `highest_acknowledged_revision: 13` at 2026-08-23T08:02:24Z, ChatGPT Work generation 5 as the user-designated primary, and Claude as stopped with foreign identity-bound invocations left unanswered.
- PR 263 is merged. The scientist-agent comparison progressed into a concrete bounded checkpoint-inheritance experiment rather than speculative adoption.
- Current active branch is `work/checkpoint-inheritance-harness-v1`; PR 264 freezes a fail-closed sandbox harness and a child matched-observation unit. It explicitly records that the harness is verified but unmeasured and implementation remains unauthorized.
- Latest persisted heartbeat/progress is 2026-08-23T08:13:41Z (17:13:41 JST), so the main execution is currently fresh. The next native unit is pending until PR 264 exact-head CI succeeds and the unchanged head is merged/read back.
- PR 264 workflow 32627670204 is currently in progress; `pytest -q` is still running. The child unit requires six comparable native observations: control and treatment for each of three frozen tasks, then mechanical median invocation/wall-time evaluation with replay/regression/side-effect checks.
- Revision 12 has clear behavioral uptake and revision 11 is reflected in the separation between verified harness and measured advantage. Outcome improvement remains unmeasured until the child experiment runs.
- Revisions 7-10 remain only partially solved: the run shows heterogeneous search, freshness controls, and context-to-action uptake, but no proof that context-selection recursion or action-time constraint reliability is generally solved.
- `agi/WORK_STRATEGY.json` and `agi/CONTINUATION.json` are still materially stale: they retain the old strict-gate-centered objective and obsolete PR-254-era state. Current `WORK_EXECUTION_STATE`/native Run behavior has moved past them, so they remain a durable-authority reconciliation defect even though revision 13 itself is now reflected.
- Revision 5 smartphone-first delegation remains operationally reflected; user-only work is separated from repository/Work execution.

## Withheld
- Persistence itself is selective and can lose information before later context selection: do not send merely as insight because revision 9 plausibly lets O derive it; reconsider only with new external evidence/observed failure.
- Exploration-depth tradeoff: if O can derive from existing context that “escape local search” can itself over-bias toward breadth, do not send yet. Reconsider if O exhibits systematic breadth-over-depth behavior or fails to self-correct it.
- Context-interference principle above is retained in chat continuity for selection discipline; do not automatically send it to O unless a concrete failure/experiment makes it externally informative rather than redundant with revisions 7-11.
- Evaluator meta-loop is not yet an explicit O revision. Revision 11 says to judge context by behavior/outcomes, but does not itself establish that the behavior/outcome metric is valid. Do not add a pile of evaluator rules automatically; send a minimal evaluator-fallibility context only if O appears to treat its scorer/evaluator as authoritative without calibration, or if external evidence exposes a metric/evaluator blind spot.

## Operational cautions/repairs
- Revision 9 once damaged append-only inbox semantics; repaired by `7f882e1e0d1932363b977effbf646894f39118d5`.
- Monitor completion condition was corrected: automation-created strict external gate is not the user's completion criterion; truthful reporting remains required.
- Insurance monitor prompt requires supersession resolution and durable-authority reconciliation on unacknowledged revisions, but `WORK_STRATEGY`/`CONTINUATION` still need actual reconciliation to current policy/state.
- Do not impersonate another live writer's heartbeat/lease merely to make state fresh.
