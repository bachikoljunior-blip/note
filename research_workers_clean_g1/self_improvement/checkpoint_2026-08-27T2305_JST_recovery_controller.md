# Self-improvement clean checkpoint — sequence 74

Updated: 2026-08-27T23:05:35+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `d9269d4ba2d663ce357370946af4e5994598433a`
- control revision: `12`
- self_improvement config revision: `6`
- sanitized root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role-local config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2232_JST_forge_controller_resume.md`

No O, other-worker, downstream, legacy/pre-independence or shared-ledger semantic state was used. Sanitized role-local feedback was read only for the already-acknowledged source-qualified-ID rule.

## Recovery controller frontier: selective rewind now has a strong matched comparison
Primary source: Zhuang et al., **AgentRewind: Recoverable Execution for Long-Horizon LLM Agents**, arXiv:2608.14380, submitted 2026-08-14. https://arxiv.org/abs/2608.14380

AgentRewind is not persistent cross-task self-improvement, so its evidence is used only for the recovery-controller mechanism. It directly separates three useful controller actions under shared agent/tools/environments/termination conditions:

1. **Continue** from the current state after evaluator rejection.
2. **Restart from root with experiences**: throw away current context/workspace, but carry accumulated evaluator-derived failure experience.
3. **Resume an ancestor / selective rewind**: restore an aligned context+environment checkpoint and inject a compact rewind memory explaining the abandoned suffix.

On the full 89-task Terminal-Bench 2.0 evaluation reported in the paper, success is **78.7% Continue, 70.8% Restart-with-Experiences, 83.1% AgentRewind**; average criteria passed are **88.7%, 79.2%, 90.2%** respectively. This is particularly useful negative evidence against a universal clean-restart rule: the full restart loses valuable prefix work in this tested setting, while selective rewind exceeds both alternatives.

On MettleBench with GPT-5.4 + mini-SWE-agent, Continue is **62.2%** and AgentRewind **87.8%**. The ablation is also unusually direct: success falls to **43.9% without environment rewind**, **65.9% without context rewind**, and **51.2% without rewind memory**. So environment state, agent context and carried failure knowledge are all separately necessary for the full tested result.

The paper also performs paired recovery from identical failed endpoints, making rewind availability the key intervention. That is closer to the counterfactual controller experiment sought in the prior frontier than ordinary end-to-end benchmark comparisons.

Scope guard: this is controlled runtime recovery, not evidence that persistent cross-task self-improvement should use the same policy. External irreversible side effects are not covered by filesystem/environment rollback. No official paper source repository was source-bound in this run, so checkpoint atomicity and actual crash behavior were not independently audited.

## Artifact-preserving restart can also beat cold restart
Primary source: Wang et al., **Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE Agentic Tasks**, arXiv:2608.03222, submitted 2026-08-04. https://arxiv.org/abs/2608.03222

RestartSmart starts a fresh same-policy rollout with no prior prompt history but offers the interrupted repository diff as an optional overlay. At a 25% false-positive operating point on Qwen3.6-27B, resolution rises **66.6% → 71.8%**, while cold restart reaches only **66.8%**. At a 5% false-positive target, the monitor saves **14.6–20.4% execution tokens**; the Qwen3.6-27B case saves 20.4% versus 12.5% for the paper's AgentStop adaptation.

This is another within-task controller result, but it independently supports the same narrower rule: useful artifacts from a failed trajectory can have positive continuation value even when the agent history should be reset.

## ScienceFlow supplies the persistent autoresearch analogue
Primary source: Zhao et al., **ScienceFlow: A long-horizon agent for ML research, scientific discovery and beyond**, arXiv:2608.14354, submitted 2026-08-14. https://arxiv.org/abs/2608.14354

Public implementation audited at `huawei-noah/noah-research` commit `d38150de76b45a0992bcfe175957d08004b7319a`, subtree `ScienceFlow/`.

ScienceFlow represents progress as a recoverable executable state containing workspace, memory, validation evidence and resource records. ESTRA then chooses two independent dimensions at a research boundary:

- anchor: **current state** or **archived Stage**;
- intent: **continue** or **redirect**.

This yields four relevant persistent controller actions: current+continue, archive+continue, current+redirect, archive+redirect. A separate execution controller admits/monitors/timeboxes/stops physical jobs.

The same-budget MLE-bench Lite ablation is strong whole-system evidence. Across 22 tasks, 24 hours and three seeds, Any-Medal is **80.30±2.62% full**, **66.67±2.62% without ESTRA**, and **69.70±5.25% without execution control**. Jigsaw median time-to-first-medal is **2.12h full vs 5.17h without ESTRA**; APTOS is **5.18h full vs 8.05h without execution control**. This supports recoverable re-anchoring and execution control in the tested persistent autoresearch setting, but it does not isolate the four ESTRA actions against one another.

## Public ScienceFlow restart path is materially stronger than FORGE's audited resume path
The public ScienceFlow repository contains `scripts/lnr_kill_resume.sh`, which can terminate processes bound to one workspace and resume that exact workspace with `scienceflow.cli run --resume`.

The dedicated resume package documents and implements three levels:

1. **task-level resume** — same workspace, with remaining budget derived from persisted `logs/state.json`;
2. **agent-memory resume** — reload persisted `ScienceAgent` memory and choose whether to continue an LLM round or complete an interrupted tool step;
3. **tool-cursor resume** — if the memory tail is exactly one assistant tool call with no matching tool result, execute that call directly, append its result and then continue.

`memory_state.py` classifies an empty/unreadable history as fresh start, a single pending tool call as `execute_pending_tool`, multiple pending tool calls as `pending_tool_bundle_unsupported`, and a completed tail as `continue_llm`. `continuation.py` runs the pending tool without re-logging the assistant message and emits resume-monitor events. `tests/test_lnr_resume.py` explicitly tests single-tool detection, direct resumed execution, transition back to `continue_llm`, monitor events and heartbeat behavior during a resumed bash command.

This is a useful contrast with the prior FORGE checkpoint: FORGE persisted memory artifacts but not `graduated_instances`, so restart could reactivate a frozen lineage. ScienceFlow demonstrates that process-resume semantics can explicitly persist and reconstruct the conversational/tool cursor. However, the current public support explicitly does **not** auto-replay bundles of multiple pending tool calls, and the inspected tests do not yet prove semantic equivalence at arbitrary kill points for ESTRA anchor identity, stage/controller state, resource budgets and evaluation-consumption state.

## Updated controller hypothesis: minimal causal rollback
The evidence now points to a more precise controller hypothesis than generic restart:

> Prefer the smallest rollback/re-anchor that removes invalid causal dependencies while preserving independently validated prefix/artifacts and carrying explicit failure evidence.

This is a synthesis hypothesis, not a theorem or a result attributable to one source. AgentRewind supports it for aligned context+environment state; RestartSmart supports artifact carryover after history reset; ScienceFlow supports restoring validated executable states; FORGE's resume defect shows that preserved artifact bytes are insufficient if controller state is lost.

A persistent self-improvement system should therefore durable-bind at least four state classes:

1. **artifact state** — memory/skill/code/workspace version;
2. **controller state** — active/frozen/retired status, chosen parent/anchor and budgets;
3. **evaluation-consumption state** — evidence already used for selection and evidence still untouched;
4. **side-effect/tool cursor** — pending effects, replay/idempotency identity and completion status.

The action space now has source-backed examples for `Continue`, `Restart-clean/root`, `Restart-with-artifact`, `Resume/re-anchor ancestor`, `Redirect/reopen`, `Widen/population`, `Resume-best/broadcast`, and `Stop/freeze`; but no single public real-LLM system in this continuation matches all important actions under one common proposal/evaluation budget plus a genuinely unused outer test.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/recovery_controller_matrix_2026-08-27T2305_JST.json`

## Exact continuation
Audit ScienceFlow's ESTRA Stage/anchor persistence and resume tests for whether archived-anchor identity, resource budgets, and stage/evaluation ledgers are reconstructed equivalently across kill points. Then search for a system with a true matched multi-action controller experiment — at minimum Continue, clean restart, artifact-preserving restart/rewind, and strategy redirect — under a common total proposal/evaluation budget and a selection-unused outer test. Prioritize explicit crash-injection/restart-equivalence tests and complete action chronology. Separately retain the still-unresolved requirements for candidate-local anytime-valid promotion, proposal-crossing durable statistical spending, immutable artifact identity and bounded selection-feedback bandwidth.
