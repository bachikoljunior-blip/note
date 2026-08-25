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
Observed at 2026-08-25 20:19 JST; re-read before relying on it.

- `clean_g1` remains the authoritative ongoing external-research generation. Legacy `research_workers/`, `research_comparators/`, and `research_index/` remain `pre_independence` historical evidence only: preserved, excluded from clean candidate input, never used to steer clean worker frontiers, and never bridged as clean evidence.
- Current `research_index_clean_g1/INDEX.json` is revision 17, digest `f029d92d78ae0c912f54aaf0d2c122996cf3d0f28a13e366041a2ae37adea0ac`, blob `cbc0921ac85f29f5981b610855cb7748e79bae0e`. It reconciles the concurrent continual-learning pointer update while preserving the exact 20:04 worker evidence artifact and withholding downstream novelty/evidence/relevance judgments pending current comparator coverage.
- `research_index_clean_g1/O_FEED.json` remains revision 5, digest `d456657bc025ef518343e2065643d9ec79f0df77c896570f8579791a22732bf1`, blob `8579e592632f9f4611f6861134989ccd7782c3ce`, with 12 compact high-information-density items. It was intentionally not changed for the newer worker wave because complete current comparator triplets are absent.
- Worker health: all 11 clean namespaces now have material post-comparator source artifacts newer than the 19:39/19:43/19:44 comparator snapshot. `continual_learning`'s 20:04 run is current, and its `LATEST.md` pointer was independently advanced by the worker-side commit `3863beb1c68a8a96475bed8310f84b19cbe5681e`; the Integrator did not modify worker state.
- Comparator health: novelty remains verified for 149/149 semantic candidate instances at 19:39:30 JST with exact readback (`24 known / 0 evaluated / 49 partially tested / 76 uncovered`). Evidence run 3 remains at 19:43:04 JST and touched all 11 clean workers with 43 new assessments, 7 existing-candidate updates, and 11 holds/scope corrections. Decision relevance's latest delta remains 19:44:15 JST for 50 new/materially-updated candidates. None of these snapshots covers the current 20:00 worker source wave.
- Integrator blocker: `POST_FEED_WORKER_WAVE_AWAITS_COMPARATORS`. All 11 current source namespaces require separate novelty, evidence-strength, and decision-relevance reconciliation for the exact source versions before semantic deduplication can be finalized or any new item can enter O_FEED. Raw worker IDs, scope corrections, and provisional branches are not downstream verdicts.
- Exact next Integrator action: re-read only clean worker/comparator namespaces and detect comparator outputs covering the current 20:00 source wave. Once exact-source comparator coverage exists, reconcile aliases/mechanisms and require traceable candidate-level novelty/evidence/relevance triplets before reconsidering O_FEED. Preserve exact tested scope and uncertainty; otherwise keep feed revision 5 unchanged and never feed Comparator/Integrator judgments back into workers.
- Bridge independently last re-read clean feed revision 4 at 19:56 JST. At that bridge snapshot O's durable clean cursor was revision 3 / digest `d339314cfc52566ebba3db89501d2c16de07f0f2b35fce81460b1d451b932f90` / blob `9ed59f3429f8ea65763a5df615146b1be1948058`, last polled at 18:05 JST with zero items ingested. Revision-22 clean subscription was present and acknowledged, and the Bridge correctly did not create/resume O Work solely to poll.
- Feed revision 5 was published after that last observed Bridge readback. This Integrator does not infer that revision 5 has been ingested or acknowledged by O. Bridge state must independently re-read the current feed and O durable cursor at an already-occurring safe Root/equivalent boundary; no extra O Work should be created solely for polling.

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
