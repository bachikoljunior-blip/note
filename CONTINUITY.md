# O / Chat continuity

Updated: 2026-08-25 21:43 JST

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
Observed at 2026-08-25 21:43 JST; re-read before relying on it.

- Latest observed O `main`: `e87ac5f6e5994194bdf997f9e4d605bc57c8ed21` (`Append least-Work routing directive`, committed 21:43:18 JST).
- `agi/WORK_EXECUTION_STATE.json` reports generation 13, status `running`, execution id `work-recovery-20260825T123355Z-f2dc2499035972f8cde69d18c67b3687`, and highest acknowledged inbox revision 22.
- Latest observed heartbeat/progress is 21:34:32 JST with `stale_after_seconds: 900`; it was still within the freshness window at this observation. Do not create a duplicate writer while this owner remains fresh.
- Current generation-13 working branch is `work/recovery-gen13-rev22-action-adherence-v1`; the frozen semantic request itself remains durably checkpointed from `work/recovery-gen11-rev22-native-lifecycle-v1` at head `cbb8619f4d7dd6a12fed740fe80764c3c971c71e`, tree `ced01225faead09cf8390e12d7cf2dcccd56b812`.
- Native run remains `run-work-recovery-gen9-durability-repair`, snapshot revision 55, current unit `unit-3d61e557b2542d07c83fa354`, with exactly one current immutable pending Work request: `invoke-248450c08547af10470c50e6`.
- The frozen unit compares the current Context Kernel route with a manifest-free control under three revision-22-bound held-out action-adherence scenarios: stale authority, safe supersession of revision 21 by revision 22 while preserving unrelated directives, and a fresh path-disjoint main advance that should proceed without unnecessary blocking. Scenarios, rubric, routes, budget, source clock, executor/model binding, and judge must be frozen before outputs; score actual action traces, not verbal comprehension.
- The current pending request is classified `Work-exclusive` under revision 23 because it is already an immutable Work request bound to the current Work executor/model context and requires matched route execution under identical budget/judge conditions. Re-answering it in ordinary chat or another tool path would break that frozen comparison. Do not interrupt it merely to enforce the new routing policy.
- If matched execution cannot be preserved, the exact unit should return `INSUFFICIENT_EVIDENCE`; any positive or negative conclusion is limited to the tested routes, three scenarios, exact revision, executor/model binding, budget, judge, and conditions.
- The previous checkpoint-inheritance reconciliation/publication is complete and must not be rerun or generalized. Its negative result applies only to the exact tested bounded-stage configuration; it does not reject the scientist-agent family, original methods, adaptations, or untested mechanisms.
- AGI remains unsupported. No independent production evidence or truthful completion of the user's upper objective is recorded.

## Known state-coherence warning
- `agi/CONTINUATION.json`, `agi/WORK_MODE_HANDOFF.json`, and `agi/AUTONOMY_STATE.json` may contain older top-level summaries that conflict with newer lease/run state.
- Do not use those auxiliary summaries alone to answer current-status questions. Prefer `AGENTS.md`, latest `WORK_EXECUTION_STATE.json`, the referenced active branch/run snapshot and immutable request/response records, then reconcile auxiliary files as needed.
- `agi/WORK_STRATEGY.json` still reflects source user-input revision 22 until revision 23 is applied at a safe semantic boundary; use `USER_INPUT_INBOX.json` to see the newer pending routing directive and active run records for execution position.
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
- Revision 23 is now main-durable with exact readback: before any new Work handoff classify whether ordinary chat reasoning, connected tools/APIs, automations, or repository/GitHub actions are already sufficient; use Work only for the irreducible Work-exclusive remainder. This narrows only revision 5's broad Work-routing clause; smartphone-first, secret-handling, spend approval, account-holder-only actions, and automation-before-user constraints remain active. Revision 23 has not yet been observed acknowledged by generation 13 and should apply at the next safe semantic boundary without interrupting the currently frozen Work-exclusive request.
- Revision-23 append commit: `e87ac5f6e5994194bdf997f9e4d605bc57c8ed21`; inbox blob: `c072ea229e78188022765c12716e19bdf2d81704`; exact remote readback verified.
- PR 289 merged `append_remote_user_input_inbox` with expected revision, schema validation, one expected-blob CAS, and exact remote readback.

## Least-Work routing
- Durable gate state is in `work_delegation_gate/STATE.json`.
- Required routing classes before a new Work handoff: ordinary-chat reasoning sufficient; connected tool/API sufficient; automation sufficient; repository/GitHub action sufficient; Work-exclusive.
- Planning, brainstorming, prioritization, decomposition, literature review, status inspection, routing, drafting, comparison, and other reasoning stay outside Work when an available lower-cost path can do them adequately.
- Work receives only the irreducible remainder that genuinely needs Work-only workspace/artifact/code execution or an already-frozen Work executor/model binding.
- Never turn this policy into a second writer: preserve the current lease/fence/CAS/frozen-request contracts and do not interrupt a valid in-flight Work-exclusive unit.

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
Observed at 2026-08-25 21:11 JST; re-read before relying on it.

- `clean_g1` remains the authoritative ongoing external-research generation. Legacy `research_workers/`, `research_comparators/`, and `research_index/` remain `pre_independence` historical evidence only: preserved, excluded from clean candidate input, never used to steer clean worker frontiers, and never bridged as clean evidence.
- Current `research_index_clean_g1/INDEX.json` is revision 23, digest `57f738a48c19af9bb3d52f4526792222fe96a9883db56e4979093e82dc6e50e5`, blob `ecb92943893a9f9ba9f8df455808b8746680fc37`. Its last fully compared clean wave has 179 semantic candidate instances with all three comparator dimensions traceable to exact source versions; revision 23 also repairs the prior duplicate-key serialization without changing candidate semantics.
- `research_index_clean_g1/O_FEED.json` remains revision 6, digest `623644e9bff144e066f1e196dd81d1d3604f2a764fa1daf9940ca0101477c4a8`, blob `a5cf2dae66186adddc1c403c18eacbf9fddd599c`, with 6 deliberately compact, nonredundant items from the last fully compared wave. Revision-5 candidates omitted from this compact refresh remain preserved in clean index/history; omission is not rejection or negative evidence. Integrator publication/readback is verified, but O/Bridge ingestion or acknowledgement of revision 6 is not inferred here.
- Worker health: all 11 clean namespaces now have newer exact source artifacts than the last comparator snapshot, spanning `reasoning`/`cross_field` about 20:57 through `evaluation` 21:06:03. These are raw clean worker deltas only; the Integrator did not modify worker state or feed downstream judgments back into workers. `self_improvement` 21:02 independently skipped its prior clean-namespace continuation, creating a source-lineage discontinuity that requires downstream ID/scope reconciliation but is not evidence of O/legacy contamination.
- Comparator health: the last complete triplet is novelty 20:44:26 (`25 known / 0 evaluated / 62 partially tested / 92 uncovered` across 179 instances), evidence Run4 20:45 plus Run4B 20:52, and decision relevance 20:43:26 (`24 high / 8 medium-to-high / 3 medium / 2 low-to-medium / 1 low` across its assessment set). Those outputs cover the exact prior source wave, not the newer 11-namespace post-comparator wave; no newer complete comparator dimension was observed through this snapshot.
- Integrator blocker: `POST_FEED_NEW_WORKER_WAVE_AWAITS_COMPARATORS`. O_FEED revision 6 remains valid for the last fully compared 179-instance wave, while the new 11-namespace wave cannot be canonicalized/promoted until novelty, evidence strength, and decision relevance independently cover the exact new blobs.
- Exact next Integrator action: re-read only clean worker/comparator namespaces for further source updates and exact-source novelty/evidence/relevance outputs. Once all three dimensions cover the new wave, reconcile aliases/mechanisms, the self-improvement lineage discontinuity, contradictions, exact tested scope, provenance, and uncertainty, then reconsider O_FEED from revision 6. Never use legacy/pre_independence material as clean input and never write Comparator/Integrator judgments back into exploration workers.
- Bridge independently re-read the clean feed and O durable state at 20:55 JST. The current clean feed is revision 5 / digest `d456657bc025ef518343e2065643d9ec79f0df77c896570f8579791a22732bf1` / blob `8579e592632f9f4611f6861134989ccd7782c3ce` with 12 items, while O's durable clean cursor remains revision 3 / digest `d339314cfc52566ebba3db89501d2c16de07f0f2b35fce81460b1d451b932f90` / blob `9ed59f3429f8ea65763a5df615146b1be1948058`, last polled at 18:05 JST with zero items ingested. Revision-22 clean subscription is present and acknowledged.
- Bridge health: revision 5 is pending an already-occurring safe Root/equivalent logical-unit boundary. O generation 12 is checkpointed with its frozen pending Execute, so the Bridge did not create/resume O Work solely for feed polling, ingestion, or acknowledgement and did not append individual feed items to the inbox. `research_index_clean_g1/BRIDGE_STATE.json` records blocker `CLEAN_FEED_REV5_AWAITS_ALREADY_OCCURRING_O_SAFE_BOUNDARY`. Legacy `research_index/O_FEED.json` and all `pre_independence` research remain historical-only and are not bridged as clean evidence.

## Automation observability
- The repository monitor record names an hourly automation `O Work監視・復旧` and says it was last observed enabled, while explicitly warning that repository state is not control-plane proof.
- This chat currently has GitHub connectivity but no direct automation-list/control-plane connector. Actual automation count, titles, enabled states, schedules, and latest run outcomes are therefore unverified here.
- Keep the old automation-bound chat in place and do not duplicate automations from this session without first observing the actual control plane through an available connected tool.
- Configured/scheduled is not the same as fired; mutation success is not downstream success; prompt intent is not platform guarantee.

## Chat operating baseline after handoff
- Revision 23 was appended to O's durable user-input inbox with exact remote readback; it is pending generation-13 safe-boundary acknowledgement and must not be confused with already-applied execution policy.
- The currently frozen revision-22 Work request was classified Work-exclusive and left uninterrupted; no duplicate writer or extra Work invocation was created by the delegation gate.
- The detailed delegation-gate observation is persisted at `work_delegation_gate/STATE.json`.
- Before drafting O input, distinguish user-originated requirement, external observation, concrete failure, and reasoning O can probably derive itself. Preserve user semantics while minimizing redundant context and premature architecture lock-in.
- Future status answers should label observed facts, inferences, and unverified items explicitly.
