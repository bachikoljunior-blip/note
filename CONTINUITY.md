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
- The malformed revision-16 write was not reconstructed semantically. Generation 7 records revision 16 as withdrawn integrity quarantine bound to the malformed blob and preserves it as negative evidence.
- Revision 17 is now acknowledged, but in the current authoritative inbox it corresponds to the user's explicit `再開して` resume direction. The earlier Skill-in-Skill proposal and scientist-agent positive-control criticism remain preserved in recovery/note context and should not be falsely claimed as ingested unless restored as authoritative semantic revisions.

## Current recursive Skill-in-Skill design — user-approved proposal context
- Desired abstraction: O Engine is a recursive Skill-in-Skill context system. All relevant durable context should be reachable from inside O Engine, but not materialized all at once.
- Kernel is effectively the always-entered root Skill. This is mainly a useful abstraction, not necessarily a mandatory implementation detail to prescribe. The essential requirement is that an always-entered minimal root context exposes indispensable global invariants and reachable action/context affordances without becoming a giant prompt.
- Each Skill that has child Skills should itself contain/own child-selection capability; a separate Selector Skill need not be inserted at every level. This is a design simplification/candidate, not an absolute requirement if O finds a better equivalent mechanism.
- Selection is semantic/model reasoning, not merely a fixed mechanical routing table: at each level the model reasons over currently materialized context, optionally using local Skill guidance/criteria, selects one or multiple useful child Skills, opens them, reasons again with added context, and recursively continues until enough context exists to decide/act.
- Local Skill judgment criteria are optional and situation-dependent and may guide child selection and substantive local judgment while remaining falsifiable/improvable.
- Reachable action/context space includes internal reasoning/implementation, experiments, external exploration, user questions/proposals/permission/operation requests, evaluation/evaluator changes, and modification/replacement of O itself.
- Authority/freshness/provenance remain part of the Context Kernel / manifest-event-ledger direction.
- Routing/context selection itself is improvable and should be evaluated by downstream decision/outcome quality, missed-needed context, unnecessary context load/interference, elapsed time/cost, and comparative interventions.

## Scientist-agent evaluation issue — user-approved external context
- Current criticism: O extracted/adapted mechanisms from externally successful scientist-agent systems (e.g. checkpoint inheritance) rather than first reproducing the demonstrated successful configuration as a fidelity-preserving positive control.
- If the demonstrated original part/configuration has not been established as a positive control, failure of an O-adapted/decomposed variant cannot distinguish failure to reproduce the external baseline, effect destroyed by adaptation/ablation, from genuine evidence against the original method.
- Do not over-specify the derived solution unless needed; O can likely derive reproduction -> adaptation -> ablation sequencing itself once this evaluation flaw is exposed.

## Evaluated mechanism/candidate status so far
- Scientist-agent family: retained as an external baseline/research source, not adopted wholesale. PR 263 compared AI Scientist-v2 against O with a frozen rubric and selected checkpoint inheritance only as a sandbox experiment.
- Checkpoint inheritance: harness/provenance machinery built (PRs 263-265), but genuine matched native observations unavailable; `INSUFFICIENT_EVIDENCE`, implementation unauthorized. Not adopted, not disproven in principle.
- Deterministic recursive history commitment v2: adopted/merged (PR 266); internal engineering, not capability evidence.
- Lazy recursive Skill context-routing infrastructure: adopted/merged (PR 268); semantic child-selection benefit still unmeasured.
- Held-out recursive routing activation: not adopted; zero admissible observations / `INSUFFICIENT_EVIDENCE` because selector contamination invalidated measurement.
- Four-way CI sharding: adopted/merged (PR 270) and reduced feedback-loop latency; workflow engineering, not capability evidence.
- O-centered Context Kernel / DecisionContextManifest + Event-Ledger: selected under revision 15 and actively engineered; not yet proven end-to-end superior.
- Full-context-everywhere/raw-copy default: not selected; selective authoritative materialization preferred.

## Current execution process / latest checkpoint
- Execution model: Work runtime is outer executor; O Engine owns semantic decision cycles. A single fenced writer holds mutation authority. User inbox is polled at safe semantic/Root boundaries; frozen invocations are immutable.
- O semantic cycle: Root -> Candidate/Preflight -> Execute -> Task Evaluate -> Consolidate/Learn -> Root, with immutable request/response records and exact continuation.
- External effects are fenced/idempotent, exact-head validated, and read back before completion.
- Context Kernel work adds pre-freeze authoritative observation/freshness/provenance validation.
- Latest checked at 2026-08-24 16:14 JST: generation 7 is RUNNING, execution `work-recovery-20260824T040019Z-fed49f4a10c39430`, heartbeat/progress 2026-08-24T07:10:23.708Z, fresh under 900-second stale threshold. Highest acknowledged inbox revision is 17. Generation 7 resumed from the generation-6 malformed-input checkpoint under a new fenced CAS owner and did not infer missing revision-16 semantics.
- Current active unit is `unit-publish-public-concepts-v2`, branch `work/recovery-gen7-public-concepts-v2-v1`.
- PR 288 `Add opt-in public-concept heldout contract v2` is open at exact head `803d314996c9b3906c1de272e2465ea338a325b7`. It adds an opt-in `PublicConceptContract` / `public-concepts-v2` evaluator while preserving the frozen historical 11/12 trial as immutable FAIL and keeping `legacy-invariant-v1` default. 74 related tests and Work verification passed locally; this is evaluator-contract/publication engineering, not a new behavioral measurement or AGI evidence.
- Latest persisted CI observation: PR 288 workflow 32698944696 had pytest shards 0,1,2 succeeded; shard 3 in progress; aggregate pending. No rerun, head update, merge, or Candidate promotion yet. Next action is observe unchanged exact-head CI; only after all 4 shards + aggregate succeed should pending Execute `invoke-8c17214637e8334e3e9b2f3c` be submitted exactly once and lifecycle continue. This Execute explicitly must not merge.
- Historical physically blinded trial remains immutable mechanical FAIL. `public-concepts-v2` is a future-only evaluator-contract repair, not a retroactive reinterpretation of that trial.
- AGI remains unsupported; internal engineering progress is not AGI evidence.

## Chat operating policy
- Before each O-related response, restore from this file first.
- Update this file after each substantive conversational step so the current design can be reconstructed even if old chat context drops.
- Do not automatically send every derived idea to O. Distinguish user-originated design/context, concrete external observation/failure, and inference O can probably derive itself.
- When drafting O input, preserve user semantics while minimizing redundant context and avoiding premature architecture lock-in.
