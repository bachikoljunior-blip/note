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
- Revision 16 was intended to carry the recursive Skill-in-Skill proposal, but the main `USER_INPUT_INBOX.json` write was malformed/truncated inside sequence 13. O correctly detected the invalid unacknowledged revision 16 and checkpointed fail-closed instead of guessing or acknowledging it. Revision 16 is therefore NOT safely ingested yet.
- Because the malformed inbox cannot be safely appended to, the exact approved Revision-16 proposal and the newly approved scientist-agent positive-control observation are now durably stored in `agi/USER_INPUT_INBOX_RECOVERY.json` on main (commit `f7800115f7ce8a51092187f74fd33e1cb7805fe4`). That file is explicitly a repair source, not an acknowledgement/ingestion record. Required repair remains: restore valid revision-15 history, append pending 16 then 17, validate JSON, then ingest at a safe Root boundary.

## Current recursive Skill-in-Skill design — approved by user for sending as proposal
- Desired abstraction: O Engine is a recursive Skill-in-Skill context system. All relevant durable context should be reachable from inside O Engine, but not materialized all at once.
- Kernel is effectively the always-entered root Skill. This is mainly a useful abstraction, not necessarily a mandatory implementation detail to prescribe. The essential requirement is that an always-entered minimal root context exposes indispensable global invariants and reachable action/context affordances without becoming a giant prompt.
- Each Skill that has child Skills should itself contain/own child-selection capability; a separate Selector Skill need not be inserted at every level. This is a design simplification/candidate, not an absolute requirement if O finds a better equivalent mechanism.
- Selection is semantic/model reasoning, not merely a fixed mechanical routing table: at each level the model reasons over currently materialized context, optionally using local Skill guidance/criteria, selects one or multiple useful child Skills, opens them, reasons again with added context, and recursively continues until enough context exists to decide/act.
- Thus the loop is interleaved reasoning <-> context retrieval, not a one-shot tree traversal.
- Local Skill judgment criteria are optional and situation-dependent. When useful, opening a Skill may materialize its local criteria/checklists/priors before child selection. Those criteria can guide both substantive local judgment and child-Skill selection, remain revisable/falsifiable, and should not accumulate when irrelevant.
- Reachable action/context space includes internal reasoning/implementation, experiments, external exploration, user questions/proposals/permission/operation requests, evaluation/evaluator changes, and modification/replacement of O itself.
- Authority/freshness/provenance remain part of the Context Kernel / manifest-event-ledger direction. Retrieval should resolve authoritative/fresh sources rather than blindly trust stale local material.
- Routing/context selection itself is improvable and should be evaluated by downstream decision/outcome quality, missed-needed context, unnecessary context load/interference, elapsed time/cost, and comparative context interventions where useful.
- Important distinction: all context reachable within O != all context always in the prompt.
- Treat the architecture as a proposal to compare/falsify, not automatic adoption.

## Exact approved Revision-16 semantic proposal text
"Revision 15のO-centered Context Kernelの候補構造として、Skill-in-Skill型の再帰的context retrievalを比較検討してほしい。各Skillでモデル自身が現在materializeされているcontextを使って推論し、必要な子Skillを一つまたは複数選んで開き、追加contextを得て再推論する流れを再帰的に行う。全contextはO Engine内から到達可能にするが一度に全てはmaterializeしない。必要なSkillには局所的な判断基準・checklist・prior等を持たせ、それらも子Skill選択や局所判断に使えるようにするが、固定ルールとして絶対視せず改善・反証可能にする。Kernel=root Skillや各Skill自身が子選択を持つ構造は候補として扱い、より良い等価構造があれば比較してよい。routing/context selection自体も、必要contextの取り逃し、不要context負荷、最終判断/結果、所要時間・コストで評価する。即採用ではなく、現Context Kernel案との比較・検証対象として扱ってほしい。"

## Scientist-agent evaluation issue — approved external context for pending Revision 17
- Concrete criticism of current evaluation design: O has so far extracted/adapted mechanisms from externally successful scientist-agent systems (e.g. checkpoint inheritance) rather than first reproducing the demonstrated successful configuration as a fidelity-preserving positive control.
- Key implication: if the demonstrated original part/configuration has not been established as a positive control, failure of an O-adapted/decomposed variant cannot distinguish (a) failure to reproduce the external baseline, (b) effect destroyed by adaptation/ablation, from (c) genuine evidence against the original method.
- Exact pending Rev-17 context: `External context: if the part or configuration that actually produced reported results in a scientist-agent system has not been tested as an unmodified or fidelity-preserving positive control, failure after adapting or decomposing it for O does not establish that the original method lacks value. Preserve the distinction between failure to reproduce the demonstrated baseline, loss of effect caused by adaptation/ablation, and genuine evidence against the original method.`
- Do not over-specify the derived solution unless needed; O can likely derive reproduction -> adaptation -> ablation sequencing itself once this evaluation flaw is exposed.

## Evaluated mechanism/candidate status so far
- Scientist-agent family: retained as an external baseline/research source, not adopted wholesale. PR 263 compared AI Scientist-v2 against O with a frozen rubric and selected checkpoint inheritance only as the next sandbox experiment; no AGI/capability claim.
- Checkpoint inheritance: measurement harness/provenance machinery was built (PRs 263-265), but genuine matched native observations could not be obtained. The native cycle recorded `INSUFFICIENT_EVIDENCE`; implementation remained unauthorized. Treat as not adopted / currently rejected-for-activation rather than disproven in principle.
- Deterministic recursive history commitment v2: adopted and merged (PR 266) after deterministic/reproducibility regressions; this is internal engineering, not capability evidence.
- Lazy recursive Skill context-routing infrastructure: adopted as infrastructure and merged (PR 268), with bounded depth/node/fan-out/context budgets and fail-closed manifest/content binding. Semantic child selection benefit was explicitly unmeasured; infrastructure adoption != behavioral validation.
- Held-out recursive routing activation: not adopted. Later held-out work retained zero admissible observations / `INSUFFICIENT_EVIDENCE` and no activation because selector contamination prevented valid measurement.
- Four-way CI sharding: adopted and merged (PR 270) to replace the ~50-minute single pytest step; subsequent native cycle treated the bounded CI engineering unit as PASS. This is measured workflow-speed engineering, not capability gain.
- O-centered Context Kernel / DecisionContextManifest + Event-Ledger: selected under revision 15 over naive raw full-context copying and is actively being engineered/validated. This is a chosen architecture direction, not yet proven end-to-end superior.
- Full-context-everywhere/raw-copy approach: explicitly not selected as the default under revision 15; O chose authoritative-source references/selective materialization instead. Treat as rejected as default architecture, not universally impossible.
- Several safety/control mechanisms (authority reconciliation, resume identity drift guards, pre-freeze freshness checks, immutable provenance binding) were adopted after concrete failure modes, but these are correctness infrastructure rather than scientist/self-improvement hypotheses.

## Why this design arose
- Concrete observed failure: outer Work context can know durable policy/action affordances while a fresh O semantic Root receives only a subset; information existing in the repository is not equivalent to influencing action-time reasoning.
- Earlier Root requests also retained stale historical entry context alongside newer objectives. Revision 15 began addressing this via an O-centered Context Kernel.
- The recursive Skill design is intended to solve selective materialization without reverting to full-context overload.

## Current execution process / checkpoint
- Execution model: Work runtime is the outer tool/executor layer; O Engine owns semantic decision cycles. A single fenced writer holds mutation authority. User inbox is polled at safe semantic/Root boundaries; frozen invocations are not mutated mid-flight.
- O semantic cycle is broadly Root -> Candidate/Preflight -> Execute -> Task Evaluate -> Consolidate/Learn -> Root, with immutable request/response records and exact continuation persisted between boundaries.
- External effects (GitHub/CI/merge/etc.) are fenced/idempotent, validated at exact heads, and read back before being treated as completed observations.
- Context Kernel work adds a pre-freeze context stage: gather/verify authoritative source observations, build decision context/manifest, then freeze the semantic request. PR 282 already added fail-closed local freshness/identity validation before semantic request mutation; the next work had been authoritative remote-source observation binding.
- Latest state checked 2026-08-24: generation 6 is `checkpointed`, not running, because malformed unacknowledged revision 16 was detected. It intentionally blocks PR 286 merge/development mutation until the inbox is repaired exactly. PR 286 exact head had already passed four pytest shards plus aggregate; that success is preserved but not merged while input authority is malformed.
- Required recovery sequence recorded by O: restore complete valid revision-15 history from the prior valid commit/blob; append the exact authoritative revision-16 proposal without guessing; validate JSON; acquire a new fenced generation by CAS; ingest revision 16 at a safe Root boundary; then revalidate unchanged PR 286 head/CI/mergeability before continuing. Pending recovery now also includes Revision 17 after Revision 16.
- AGI remains unsupported; internal engineering progress is not AGI evidence.

## Chat operating policy
- Before each O-related response, restore from this file first.
- Update this file after each substantive conversational step so the current design can be reconstructed even if old chat context drops.
- Do not automatically send every derived idea to O. First distinguish: (a) user-originated design/context, (b) concrete external observation/failure, (c) an inference O can probably derive itself. For (c), usually let O derive it unless communicating it has clear marginal value.
- When drafting O input, preserve the user's intended semantics while minimizing redundant context and avoiding premature architecture lock-in unless the user explicitly chooses it.
