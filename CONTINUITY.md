# O / Chat continuity

Updated: 2026-08-24 JST

Mandatory continuity: read this file before every O-related answer/reasoning/action, then update it in the same turn whenever the conversation advances or materially clarifies the current design/state. Treat this as the chat-side reconstruction checkpoint so long conversation history is not required. Before sending new semantic context to O, show the wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Standing context
- Goal: materially accelerate genuine real-world AGI; O is instrumental/replaceable.
- User-side work should be minimized; repository/tool work belongs on the automated/Work side.
- Treat O and this chat as same-base-model for idea-generation overlap. Before proposing a new idea to send to O, ask whether O could readily derive it from its actual current context. Prefer genuine context asymmetries, user-originated design choices, external evidence/observations, or concrete failures over duplicating reasoning O can readily do itself.
- External ideas and user proposals are hypotheses, not automatic truth.
- Context is an intervention with information value and interference cost; more context is not monotonically better. Prefer minimal, gated, on-demand context and judge usefulness by downstream behavior/results.
- Evaluation itself is fallible. Distinguish measured improvement from metric validity; evaluator design may itself need falsification/calibration.

## O inbox / uptake
- Revisions 7-12: context-conditioning, asynchronous freshness, recursive context selection, context-to-action gaps, behavioral/outcome evaluation, scientist-agent external baselines.
- Revision 13: ChatGPT Work primary; Claude stopped as executor.
- Revision 14: recurring durable-authority reconciliation, not one-time cleanup.
- Revision 15: O-centered context kernel. Context management/retention and the work loop should be centered in O Engine; prevent externally known information from silently disappearing from O decision context; compare architectures rather than assuming raw full-context copying is optimal.
- Revision 16 is a withdrawn integrity-quarantine record for the malformed/truncated write; no missing semantics were reconstructed.
- Revision 17 resumed generation 7.
- Revision 18 is the user-approved recursive Skill-in-Skill Context Kernel architecture proposal. It was safely appended and acknowledged.
- Revision 19 is the scientist-agent positive-control/evaluation-scope observation. It was safely appended and acknowledged.
- PR 289 merged the dedicated future append path `append_remote_user_input_inbox`: expected revision, JSON/schema validation, contiguous sequences, duplicate/secret rejection, one expected-blob CAS, and exact remote readback. PR 290 durably published that native lifecycle.
- A clarification intended for authoritative Revision 20 has now been observed by the live Work owner but is not yet appended or acknowledged because the current Execute request is frozen. Its meaning: limit negative evidence to the candidate/configuration/conditions actually tested; do not generalize one component or O-adapted variant failure to an entire scientist-agent family or untested mechanisms; do not require redundant positive-control reproduction when equivalent original conditions are already established; interpret Revision 19 as an anti-overgeneralization/evidential-scope rule.

## Current recursive Skill-in-Skill design
- O Engine is a recursive Skill-in-Skill context system candidate. All relevant durable context should be reachable from inside O Engine, but not materialized all at once.
- Kernel is conceptually the always-entered minimal root context/Skill: indispensable global invariants and reachable action/context affordances, not a giant prompt.
- Each Skill with children may itself support model-reasoned child selection; a separate Selector Skill at every level is not mandatory.
- At each level the model reasons over currently materialized context, optionally uses local Skill criteria/checklists/priors, opens one or multiple useful child Skills, reasons again with added context, and recurses until enough context exists to decide/act.
- Local judgment criteria are optional, situation-dependent, falsifiable, and may guide both local judgment and child selection without accumulating when irrelevant.
- Reachable action/context space includes implementation, experiments, external exploration, user questions/proposals/permission/operation requests, evaluator changes, and modification/replacement of O itself.
- Authority/freshness/provenance remain part of the Context Kernel / manifest-event-ledger direction.
- Routing/context selection itself is improvable and should be evaluated by downstream decision/outcome quality, missed-needed context, unnecessary context load/interference, elapsed time/cost, and comparative interventions.

## Scientist-agent evaluation scope
- Scientist-agent family remains an external baseline/research source, not adopted wholesale or rejected wholesale.
- Checkpoint inheritance was only one extracted/adapted candidate. Its `INSUFFICIENT_EVIDENCE` result does not disprove the scientist-agent family or untested mechanisms.
- Positive controls are needed when necessary to distinguish reproduction failure, adaptation/ablation loss, and genuine evidence against the original method. But if materially equivalent original success conditions are already established, do not require redundant reproduction solely as ritual.
- Core rule: every negative result's scope is limited to what was actually tested. Candidate-level failure may not be promoted to family-level rejection without broader matched evidence.
- PR 291 merged a precommitted matched comparison protocol for current Context Kernel, recursive Skill routing, and eager-context diagnostic control, plus deterministic routing-receipt validation and scientist-agent causal classification. It remains PRECOMMITTED and unmeasured: zero routing observations and no positive-control result yet.

## Evaluated mechanism/candidate status so far
- Checkpoint inheritance: harness/provenance built in PRs 263-265; genuine matched native observations unavailable; `INSUFFICIENT_EVIDENCE`, implementation unauthorized. Not adopted, not disproven in principle.
- Deterministic recursive history commitment v2: adopted/merged in PR 266; internal engineering, not capability evidence.
- Lazy recursive Skill context-routing infrastructure: adopted/merged in PR 268; semantic child-selection benefit still unmeasured.
- Held-out recursive routing activation: not adopted; zero admissible observations / `INSUFFICIENT_EVIDENCE` because selector contamination invalidated measurement.
- Four-way CI sharding: adopted/merged in PR 270 and reduced feedback-loop latency; workflow engineering, not capability evidence.
- O-centered Context Kernel / DecisionContextManifest + Event-Ledger: selected under revision 15 and actively engineered; not yet proven end-to-end superior.
- Full-context-everywhere/raw-copy default: not selected; selective authoritative materialization preferred.
- Public-concepts-v2 evaluator contract exists on open PR 288; historical 11/12 trial remains immutable FAIL and is not retroactively relabeled.

## Current execution process / latest checkpoint
- Execution model: Work runtime is outer executor; O Engine owns semantic decision cycles. A single fenced writer holds development mutation authority. User inbox is polled at safe semantic/Root boundaries; frozen invocations are immutable.
- O semantic cycle: Root -> Candidate/Preflight -> Execute -> Task Evaluate -> Consolidate/Learn -> Root, with immutable request/response records and exact continuation.
- External effects are fenced/idempotent, exact-head validated, and read back before completion.
- Context Kernel work adds pre-freeze authoritative observation/freshness/provenance validation.
- Latest checked at 2026-08-24 21:15 JST: generation 7 is RUNNING, execution `work-recovery-20260824T040019Z-fed49f4a10c39430`, heartbeat/progress `2026-08-24T12:15:21.585Z`, fresh under the 900-second stale threshold.
- Highest acknowledged inbox revision is 19. Revision-20 clarification is durably recorded in `WORK_EXECUTION_STATE.user_input_inbox.pending_safe_boundary_input` as observed-not-yet-appended/acknowledged and is scheduled after the current identity-bound frozen Execute completes.
- PR 291 `Precommit matched context comparison and positive-control gate` merged at 2026-08-24T11:16:11Z. It creates the comparison/evidence-scope protocol, but no matched behavioral observations have been collected yet.
- Current active unit is native lifecycle publication for that context-comparison work. Superseded PR 292 was closed; replacement PR 293 is open at exact head `e3fe61198fe00079e7def3d52d83124dca3e61be`, containing 82 native-record-only paths.
- Canonical exact-head CI run `32724168634`: shards 0 and 1 succeeded; shard 2's pytest succeeded and job finalization was still completing; shard 3 pytest was still running; aggregate not yet available. Redundant exact-head runs remain queued and are not merge authority.
- After all four shards plus aggregate succeed, Work will re-read authority/inbox/main/head, require a conflict-free comparison, precommit merge authorization, expected-head merge PR 293, read back all 82 reviewed blobs, answer the frozen Execute, then safely append/ingest Revision 20 at the next boundary.
- AGI remains unsupported; internal engineering progress is not AGI evidence.

## Chat operating policy
- Before each O-related response, restore from this file first.
- Update this file after each substantive conversational step so the current design can be reconstructed even if old chat context drops.
- Do not automatically send every derived idea to O. Distinguish user-originated design/context, concrete external observation/failure, and inference O can probably derive itself.
- When drafting O input, preserve user semantics while minimizing redundant context and avoiding premature architecture lock-in.
