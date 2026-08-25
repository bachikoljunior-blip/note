# O / Chat continuity

Updated: 2026-08-25 19:56 JST

Mandatory continuity: read this file before every O-related answer/reasoning/action, then update it in the same turn whenever the conversation advances or materially clarifies the current design/state. Treat this as the chat-side reconstruction checkpoint so long conversation history is not required. Before sending new semantic context to O, show the wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Main-session ownership
- This chat is now the main user dialogue, design, and status-reconstruction session for O / O Engine.
- The former main chat remains attached to the external-research automations and is automation-only; it is not the canonical ordinary-dialogue session.
- Do not create duplicate research or O automations merely because this session changed.
- This handoff preserves context, not prior conclusions. Latest repository state, durable execution records, source receipts, and evidence override this file when they conflict.

## Standing objective and dialogue policy
- Goal: materially accelerate genuine real-world AGI; O is instrumental and replaceable.
- Do not lower the achievement standard, relabel internal engineering as AGI, or blur observation, inference, and unknowns.
- Minimize user-side work. Repository/tool work belongs on the automated/Work side; the user is smartphone-first.
- Treat O and this chat as same-base-model for idea-generation overlap. Before proposing context to send, ask whether O could readily derive it from its actual current context. Prefer user-specific goals/constraints, genuine context asymmetries, external evidence, concrete failures, and durable meta-requirements over duplicating O's own reasoning.
- External ideas and user proposals are hypotheses, not automatic technical truth.
- Context is an intervention with information value and interference cost. Prefer minimal, gated, on-demand context and judge it by downstream behavior/results.
- Evaluation is fallible. Distinguish measured improvement from metric validity and falsify/calibrate evaluators where needed.
- When the user asks “where are we?”, “was it reflected?”, or similar, inspect current durable state instead of inferring from old chat.
- When the user explicitly asks to send/apply something to O, inspect current state for duplication, supersession, acknowledgement, and conflicts; mutate only through a safe connected path and verify readback.

## Authoritative restoration order
1. Read current `bachikoljunior-blip/O/AGENTS.md`.
2. Read latest remote `main`, especially `agi/WORK_EXECUTION_STATE.json` and `agi/USER_INPUT_INBOX.json`.
3. Follow the exact active branch/run/snapshot/request references from `WORK_EXECUTION_STATE.json`; `.continual/runs/`, immutable Work invocations, episodes, candidates, and evidence ledgers are durable execution truth.
4. Read `agi/WORK_STRATEGY.json` and any decision-relevant source receipts.
5. Read current clean external-research state under `research_workers_clean_g1/`, `research_comparators_clean_g1/`, and `research_index_clean_g1/`.
6. Treat this file and other summary pointers as reconstruction aids, not as authority over newer execution records.

## Current O execution snapshot
Observed at 2026-08-25 19:56 JST; re-read before relying on it.

- Latest observed O `main`: `e76c4e9d6d75c30769fc7c93ba6c1f0531779b46` (`Checkpoint generation 12 at last durable native request`, committed 19:16:52 JST).
- `agi/WORK_EXECUTION_STATE.json` reports generation 12, status `checkpointed`, execution id `work-recovery-20260825T100803Z-9a82cfcc7affd1e3a617ba9e2c512ec0`, and inbox revision 22 acknowledged.
- Latest observed heartbeat/progress is 19:16:19 JST with `stale_after_seconds: 900`; the owner is checkpointed rather than currently running.
- Current branch remains `work/recovery-gen11-rev22-native-lifecycle-v1`; checkpoint head `cbb8619f4d7dd6a12fed740fe80764c3c971c71e`, tree `ced01225faead09cf8390e12d7cf2dcccd56b812`.
- Native run remains `run-work-recovery-gen9-durability-repair`, snapshot revision 55, current unit `unit-3d61e557b2542d07c83fa354`, with exactly one current immutable pending Work request: `invoke-248450c08547af10470c50e6`.
- The frozen unit compares the current Context Kernel route with a manifest-free control under three revision-22-bound held-out action-adherence scenarios: stale authority, safe supersession of revision 21 by revision 22 while preserving unrelated directives, and a fresh path-disjoint main advance that should proceed without unnecessary blocking. Scenarios, rubric, routes, budget, source clock, executor/model binding, and judge must be frozen before outputs; score actual action traces, not verbal comprehension.
- If matched execution cannot be preserved, the exact unit should return `INSUFFICIENT_EVIDENCE`; any positive or negative conclusion is limited to the tested routes, three scenarios, exact revision, executor/model binding, budget, judge, and conditions.
- The previous checkpoint-inheritance reconciliation/publication is complete and must not be rerun or generalized. Its negative result applies only to the exact tested bounded-stage configuration; it does not reject the scientist-agent family, original methods, adaptations, or untested mechanisms.
- AGI remains unsupported. No independent production evidence or truthful completion of the user's upper objective is recorded.

## Known state-coherence warning
- `agi/CONTINUATION.json`, `agi/WORK_MODE_HANDOFF.json`, and `agi/AUTONOMY_STATE.json` may contain older top-level summaries that conflict with newer lease/run state.
- Do not use those auxiliary summaries alone to answer current-status questions. Prefer `AGENTS.md`, latest `WORK_EXECUTION_STATE.json`, the referenced active branch/run snapshot and immutable request/response records, then reconcile auxiliary files as needed.
- `agi/WORK_STRATEGY.json` contains current revision-22 policy, but individual descriptive fields such as `current_stage` may lag the exact active unit; use the active run records for execution position.
- `agi/USER_REQUEST_QUEUE.json` may contain old non-blocking requests with overdue reevaluation dates; do not assume they still require user action without a fresh Root/state review.

## O inbox / durable user context
- Revisions 7-12 cover context conditioning, asynchronous freshness, recursive context selection, context-to-action gaps, behavioral/outcome evaluation, and scientist-agent external baselines.
- Revision 13 transferred primary execution to ChatGPT Work and stopped Claude as executor; later revisions establish the current fenced Work process.
- Revision 14 requires recurring durable-authority reconciliation.
- Revision 15 establishes the O-centered Context Kernel.
- Revision 18 records the recursive Skill-in-Skill Context Kernel architecture.
- Revision 19 records scientist-agent positive-control/evaluation-scope requirements.
- Revision 20 requires exact tested-scope negative evidence and permits reuse of provenance-equivalent positive controls instead of duplicate reproduction.
- Revision 21 points to legacy pre-independence research and is historical only.
- Revision 22 supersedes revision 21 for current research intake: only `research_index_clean_g1/O_FEED.json` is the current bridge; the subscription directive is active and acknowledged after PR 308 merge/readback.
- PR 289 merged `append_remote_user_input_inbox` with expected revision, schema validation, one expected-blob CAS, and exact remote readback.

## Recursive Skill-in-Skill design
- O Engine is a recursive Skill-in-Skill context-system candidate. Relevant durable context should be reachable from inside O Engine without materializing all of it at once.
- Kernel is the always-entered minimal root context/Skill.
- A Skill may expose multiple child Skills; the model can reason over current context, choose one or more useful children, recurse to arbitrary useful depth, and obtain only selected branches.
- A mandatory Selector Skill at every level is not required. Local criteria/checklists/priors are optional, situation-dependent, falsifiable aids rather than a fixed routing table that replaces model reasoning.
- Evaluate routing by downstream decision/outcome quality, missed-needed context, unnecessary context/interference, elapsed time, and cost.
- Current repository infrastructure includes a Context Kernel / DecisionContextManifest / source-clock and invalidation control plane, but end-to-end semantic benefit is still under behavioral evaluation.

## Scientist-agent evidence scope
- Scientist-agent systems remain external baselines/research sources, neither adopted nor rejected wholesale.
- Always distinguish original method, published configuration/result, O-specific adaptation, actually tested configuration, untested components, and failure scope.
- Checkpoint inheritance was one extracted/adapted candidate. Failure of its exact width-1 versus width-3 bounded configuration does not disprove the family or untested mechanisms.
- Positive controls are required only when they distinguish reproduction failure, adaptation/ablation loss, and evidence against the original method. Reuse adequately provenance-equivalent controls rather than duplicating them.
- Positive evidence also cannot exceed the tested scope.

## Clean external-research status
Observed at 2026-08-25 19:56 JST; re-read before relying on it.

- `clean_g1` remains the authoritative ongoing external-research generation. Legacy `research_workers/`, `research_comparators/`, and `research_index/` remain `pre_independence` historical evidence only: preserved, excluded from clean candidate input, never used to steer clean worker frontiers, and never bridged as clean evidence.
- Current `research_index_clean_g1/INDEX.json` is revision 9, digest `0cf3e67da7df96d496514487c9089743c36be29d5cda2161e2caf5f8c9cb117e`, blob `ea80083a183917eb5ec95875f09fdf2cbb834beb`. Revision 9 preserves the immutable revision-3→4→5→6→7→8→9 chain and reconciles the concurrent novelty-comparator update rather than rewriting the point-in-time revision-8 checkpoint.
- `research_index_clean_g1/O_FEED.json` is revision 4, digest `c583e921c44aa01406ac612cfb497530516f4cec8551eba904bc074c176f541e`, blob `a62f5bfce5577ca163ce754efd38f19465b2768b`, with 8 compact high-information-density items. No post-wave item was admitted without a complete current three-dimension comparator triplet.
- Worker health: all 11 clean namespaces are present in the novelty comparator's exact source-snapshot readback, and the Integrator has not written to worker state. Semantic identity remains mechanism + clean source artifact/version; source-bound/raw-ID collisions and evidence-only revisions are not silently double-counted.
- Comparator health: novelty is verified for 149/149 semantic candidate instances at 19:39:30 JST with exact readback at 19:50 (`24 known / 0 evaluated / 49 partially tested / 76 uncovered`). Evidence remains a 68-candidate base plus current overlay/run-1/run-2 incremental verification layers; no current evidence state/readback establishes complete 149-instance coverage. Relevance remains the 73-candidate base plus a 39-candidate new/materially-updated delta; it is not a complete 149-instance snapshot.
- Integrator blocker: `EVIDENCE_RELEVANCE_POST_WAVE_GAP`. Novelty has caught up, but newer/post-wave semantics cannot enter O_FEED until evidence strength and decision relevance are both explicitly current and candidate-level traceable. Secondary `MATERIALIZATION_CHAIN` bookkeeping remains: future reconciliation must preserve exact scopes, contradictions, source versions, semantic-ID handling, and comparator provenance across revisions 3→9.
- Bridge independently re-read clean feed revision 4 at 19:56 JST. O's durable clean cursor remains revision 3 / digest `d339314cfc52566ebba3db89501d2c16de07f0f2b35fce81460b1d451b932f90` / blob `9ed59f3429f8ea65763a5df615146b1be1948058`, last polled at 18:05 JST with zero items ingested.
- Revision-22 clean subscription is present and acknowledged. Feed revision 4 is pending O acknowledgement because generation 12 is checkpointed with the frozen Execute request; the Bridge did not create/resume an O Work call solely to poll, did not append individual feed items to the inbox, and did not claim ingestion before an already-occurring safe Root/equivalent boundary. Exact pending state is durable in `research_index_clean_g1/BRIDGE_STATE.json` under blocker `CLEAN_FEED_REV4_AWAITS_ALREADY_OCCURRING_O_SAFE_BOUNDARY`.
- Exact next Integrator action: re-read only clean worker/comparator namespaces; first check for newer evidence-strength and decision-relevance artifacts covering the 149-instance worker snapshot and for any newer clean-worker deltas. Reconcile candidate-level triplets by semantic mechanism/source version, merge evidence-only scope updates into existing instances, and reconsider O_FEED only for candidates meeting all gates. Keep downstream judgments out of clean worker state.
- Exact next Bridge action: re-read clean O_FEED plus O latest main/inbox/work state. If O's clean cursor is still behind revision 4, wait for an already-occurring safe Root/equivalent boundary; after durable acknowledgement, record exact revision/digest/blob and clear the pending blocker. Never bridge legacy/pre_independence research as clean evidence.

## Automation observability
- The repository monitor record names an hourly automation `O Work監視・復旧` and says it was last observed enabled, while explicitly warning that repository state is not control-plane proof.
- This chat currently has GitHub connectivity but no direct automation-list/control-plane connector. Actual automation count, titles, enabled states, schedules, and latest run outcomes are therefore unverified here.
- Keep the old automation-bound chat in place and do not duplicate automations from this session without first observing the actual control plane through an available connected tool.
- Configured/scheduled is not the same as fired; mutation success is not downstream success; prompt intent is not platform guarantee.

## Chat operating baseline after handoff
- No new semantic directive was sent to O during this bridge turn; revision 22 already contains the durable clean-feed subscription.
- This file was updated only as chat-side continuity and must not be confused with O's user-input inbox or technical evidence.
- Before drafting O input, distinguish user-originated requirement, external observation, concrete failure, and reasoning O can probably derive itself. Preserve user semantics while minimizing redundant context and premature architecture lock-in.
- Future status answers should label observed facts, inferences, and unverified items explicitly.
