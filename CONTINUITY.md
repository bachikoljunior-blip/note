# O / Chat continuity

Updated: 2026-08-24 JST

Mandatory continuity: read this file before every O-related answer/reasoning/action, then update it in the same turn whenever the conversation advances or materially clarifies the current design/state. Treat this as the chat-side reconstruction checkpoint so long conversation history is not required. Before sending new semantic context to O, show the wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Standing context
- Goal: materially accelerate genuine real-world AGI; O is instrumental/replaceable.
- User-side work should be minimized; repository/tool work belongs on the automated/Work side.
- Treat O and this chat as same-base-model for idea-generation overlap. Before proposing a new idea to send to O, explicitly ask whether O could readily derive it from its actual current context. Prefer genuine context asymmetries, user-originated design choices, external evidence/observations, or concrete failures over duplicating reasoning O can readily do itself.
- External ideas and user proposals are hypotheses, not automatic truth.
- Context is an intervention with information value and interference cost; more context is not monotonically better. Prefer minimal, gated, on-demand context and judge usefulness by downstream behavior/results.
- Evaluation itself is fallible. Distinguish measured improvement from metric validity; evaluator design may itself need falsification/calibration.

## O inbox / uptake
- Revisions 7-12: context-conditioning, asynchronous freshness, recursive context selection, context-to-action gaps, behavioral/outcome evaluation, scientist-agent external baselines.
- Revision 13: ChatGPT Work primary; Claude stopped as executor.
- Revision 14: recurring durable-authority reconciliation, not one-time cleanup.
- Revision 15: O-centered context kernel. Context management/retention and the work loop should be centered in O Engine; prevent externally known information from silently disappearing from O decision context; compare architectures rather than assuming raw full-context copying is optimal.
- Revision 15 is acknowledged. O selected an authoritative-source-referenced DecisionContextManifest/Event-Ledger direction rather than copying all raw external data into every prompt.

## Current recursive Skill-in-Skill design under discussion — NOT YET SENT AS A NEW REVISION
- Desired abstraction: O Engine is a recursive Skill-in-Skill context system. All relevant durable context should be reachable from inside O Engine, but not materialized all at once.
- Kernel is effectively the always-entered root Skill. It should contain only indispensable global context / invariants and the index/affordances needed to reach the rest, avoiding a giant always-present prompt.
- Each Skill that has child Skills should itself contain/own the child-selection capability; a separate Selector Skill need not be inserted at every level.
- Selection is semantic/model reasoning, not merely a fixed mechanical routing table: at each level the model reasons over the currently materialized context, optionally using local Skill guidance/criteria, selects one or multiple useful child Skills, opens them, reasons again with the added context, and recursively continues until enough context exists to decide/act.
- Thus the loop is interleaved reasoning <-> context retrieval, not a one-shot tree traversal.
- A Skill may contain local decision criteria/checklists/priors when useful: what matters in that domain, when to open which children, when multiple branches are useful, stopping/evaluation criteria. These should guide model reasoning rather than become unquestionable rigid rules; they remain falsifiable/improvable.
- Reachable action/context space should include at least internal reasoning/implementation, experiments, external exploration, user questions/proposals/permission/operation requests, evaluation/evaluator changes, and modification/replacement of O itself. This prevents an action from disappearing merely because the current semantic prompt omitted that affordance.
- Authority/freshness/provenance remain part of the Context Kernel / manifest-event-ledger direction. Retrieval should resolve authoritative/fresh sources rather than blindly trust stale local material.
- Routing/context selection itself is an improvable object. Evaluate downstream decision/outcome quality, missed-needed context, unnecessary context load/interference, elapsed time/cost, and where possible compare routing/context interventions rather than judging by verbal comprehension.
- Important distinction: "all context is reachable within O" != "all context is always in the prompt".
- Current candidate wording should present this as an architecture to compare/falsify, not automatic adoption.

## Why this design arose
- Concrete observed failure: outer Work context can know durable policy/action affordances while a fresh O semantic Root receives only a subset; information existing in the repository is not equivalent to influencing action-time reasoning.
- Earlier Root requests also retained stale historical entry context alongside newer objectives. Revision 15 began addressing this via an O-centered Context Kernel.
- The recursive Skill design is intended to solve selective materialization without reverting to full-context overload.

## Current execution checkpoint
- Latest checked state on 2026-08-24: generation 6 recovery owner is running; Revision 15 acknowledged.
- O selected DecisionContextManifest/Event-Ledger and discovered a stale-context request-freeze failure itself.
- PR 282 merged: pre-freeze mandatory Work-state freshness/identity validation, fail-closed before semantic request mutation; protected regression 159 passed. O explicitly retained the limitation that local freshness does not prove latest-remote observation.
- Current next unit binds authoritative remote Work-state observation request/receipt before semantic request freeze, addressing that remaining provenance/freshness gap.
- AGI remains unsupported; internal engineering progress is not AGI evidence.

## Chat operating policy
- Before each O-related response, restore from this file first.
- Update this file after each substantive conversational step so the current design can be reconstructed even if old chat context drops.
- Do not automatically send every derived idea to O. First distinguish: (a) user-originated design/context, (b) concrete external observation/failure, (c) an inference O can probably derive itself. For (c), usually let O derive it unless communicating it has clear marginal value.
- When drafting O input, preserve the user's intended semantics while minimizing redundant context and avoiding premature architecture lock-in unless the user explicitly chooses it.
