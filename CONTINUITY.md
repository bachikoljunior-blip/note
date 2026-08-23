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
- Avoid turning “escape the current search space” into a new rigid heuristic. Excessive breadth can itself create a narrowed policy that under-explores promising regions. Exploration policy must preserve both depth and breadth, detect when either is being over- or under-used, and evaluate the tradeoff by downstream results rather than by following a fixed anti-locality rule.

## External-context items sent to O
1. Long-lived accumulated context can suppress hypotheses/strategies available to the same base model under different context.
2. Durable state and live execution advance on different clocks; freshness/provenance/invalidation/reconciliation/decision-time context selection are structural concerns.
3. Revision 9: context selection changes judgment and is itself conditioned by previously selected context.
4. Revision 10: same-family model repeatedly failed to apply explicitly present, understood constraints in later actions; availability/retrievability is not equivalent to behavioral control. Commit `48cdbe227e1c81f0f5fbd0c1ae6c85b25194b3ce`.
5. Revision 11: successful context integration should be evaluated by whether it actually produces useful behavioral and outcome changes, not merely storage/recall/explanation. Repaired append-only representation commit `496c1bb57e5cf89b3dbf9776964274d8fb355ae7`.
6. Revision 12: autonomous scientist-agent systems with closed loops over hypothesis generation, experimentation, evaluation, and research-result inheritance have externally evaluated outputs/measured improvements; use them as external baselines and compare/test mechanisms rather than designing only from O's current internal approach. Commit `1e2ceeb86825af9f883d561071b4f231bdd1f6fc`.

## Current behavioral-uptake evidence
- Generation-4 primary became stale and the insurance monitor acquired generation 5 by fenced CAS at 2026-08-23T06:14Z.
- Generation 5 acknowledged revision 12 and did not merely summarize it: it compared AI Scientist-v2 against O on hypothesis generation, experiment execution, evaluation, result inheritance, cost/latency, and failure containment.
- The comparison refused wholesale adoption and selected one reversible candidate: bounded staged best-checkpoint inheritance. Proposed falsifiable experiment: on three matched non-production units, compare O single-lineage Root selection with three sandboxed sibling hypotheses scored by the same deterministic metric; retain only the best passing checkpoint. Reject if median invocations/wall time do not improve, replay is unstable, or regressions/side effects worsen.
- This is the first clear behavioral-uptake evidence for the recent external-context stream, but not yet outcome improvement: the candidate's measured advantage is explicitly `not_yet_measured` and implementation remains unauthorized until the experiment proceeds.
- PR 263 (`agi: compare bounded scientist checkpoint inheritance`) publishes this comparison and native recovery records at head `536407444dd16ae706583aa1df5903af82d61149`. At last check its CI was still running in `pytest -q`; main integration and the matched experiment were waiting on that exact-head CI.

## Withheld
- Persistence itself is selective and can lose information before later context selection: do not send merely as insight because revision 9 plausibly lets O derive it; reconsider only with new external evidence/observed failure.
- Exploration-depth tradeoff: if O can derive from existing context that “escape local search” can itself over-bias toward breadth, do not send yet. Reconsider if O exhibits systematic breadth-over-depth behavior or fails to self-correct it.

## Operational cautions/repairs
- Revision 9 once damaged append-only inbox semantics; repaired by `7f882e1e0d1932363b977effbf646894f39118d5`.
- Monitor completion condition was corrected: automation-created strict external gate is not the user's completion criterion; truthful reporting remains required.
- Do not impersonate another live writer's heartbeat/lease merely to make state fresh.
