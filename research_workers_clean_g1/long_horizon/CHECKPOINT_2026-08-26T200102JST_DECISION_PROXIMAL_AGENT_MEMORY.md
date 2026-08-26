# Long Horizon clean_g1 — decision-proximal agent memory / abstention checkpoint

## Frozen semantic control tuple
- invocation_started_at: `2026-08-26T19:58:56+09:00`
- checkpointed_at: `2026-08-26T20:01:02+09:00`
- frozen note main SHA: `1525e6d0512ce012c8b1db6e08216ae6253d7d74`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- both pre-semantic SHA-only Git-ref lookups matched the frozen SHA. After the first own-state read, semantic config was frozen for this invocation.
- semantic boundary preserved: only this role's clean state, its own sanitized feedback, and public sources were used. O, other workers, downstream state, legacy/pre_independence research, shared ledger, and other-role receipts/configs were not read semantically.
- own feedback item `lh-own-observability-boundary-20260825` was followed: no shared aggregate ledger or other-role receipt was read.

## New primary-source findings

### 1. Direct software/tool-agent evidence: memory helps when it is a selective intervention on the next decision, not merely retrievable history
`Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents` (arXiv:2607.08716, submitted 2026-07-09) gives the most direct controlled evidence found in this pass for the previous checkpoint's `retrieval -> downstream action/outcome` frontier.

Primary source: https://arxiv.org/abs/2607.08716

Design:
- The action agent is left unchanged; a separate memory agent maintains execution-state memory and emits either a concise transient reminder or an explicit no-intervention action before the next action-agent call.
- Terminal-Bench 2.0 tests autonomous CLI/code/debugging tasks; tau2-Bench tests stateful conversational tool use. The action model, tools and decoding procedure remain unchanged between baseline and memory conditions; the optional transient memory context is the intervention.

Main paired outcomes:
- Terminal-Bench 2.0, Sonnet 4.5 action agent, 85 valid paired tasks: `37.6% -> 45.9%` pass@1 (`+8.3 pp`).
- Terminal-Bench 2.0, Opus 4.6 action agent: `43.5% -> 45.9%` (`+2.4 pp`).
- tau2-Bench, Sonnet 4.5, 278 tasks: task-weighted `55.0% -> 61.8%` (`+6.8 pp`).
- tau2-Bench, Opus 4.6: `66.2% -> 68.7%` (`+2.5 pp`).

Ablation nuance matters:
- On tau2 with Sonnet, full selective memory has macro/micro `64.3 / 61.2`.
- Exposing the full memory bank every step gives `61.5 / 58.6`.
- Mem0 top-10 retrieval gives `62.1 / 60.8`.
- Always injecting a synthesized reminder gives `63.5 / 61.5`: slightly higher micro by `0.3` but lower macro, and the authors explicitly treat this as within expected run variance. Therefore the paper supports targeted intervention over passive/full-bank exposure, but does **not** establish a universal advantage of silence over always-on reminders on every aggregate.
- Injection-only guidance without a persistent bank is unstable: airline falls below baseline (`68.0 -> 62.0`) while telecom improves, showing that generic advisor output can introduce domain-specific negative transfer.

Calibration negative evidence:
- With a frozen Qwen3.5-122B-A10B action agent on SETA, an untrained Qwen3.5-27B memory agent *hurts* average verifier reward `0.709 -> 0.693`; SFT recovers to `0.720`, GRPO to `0.734`.
- The trained memory policy transfers to held-out Terminal-Bench: `37.6% -> 41.1%` pass@1.
- The paper's qualitative cases show useful interventions immediately before state-changing tool calls, reactivating verified records, eligibility rules, one-shot limits, failed-edit diagnoses and active entities. Remaining failures include speculative reminders and unnecessary verification.

Narrow transfer implication: this is direct evidence that `memory exists/retrieves` is not the same as `memory productively intervenes`. A high-value long-horizon memory contract should include an explicit `null/silence` option and optimize *intervention effect on the next action and final verifier outcome*, while measuring negative transfer/disruption. It does not prove the best trigger schedule—the memory agent is invoked on a fixed schedule in the main experiments.

### 2. Independent embodied evidence: structured, retrieved memory can beat full raw history under a fixed planner/controller
`HAM-VLN: Harnessing Hierarchical Agentic Memory for Zero-Shot Vision-and-Language Navigation` (arXiv:2607.29600, submitted 2026-07-31) provides a different-domain controlled planner-memory comparison.

Primary source: https://arxiv.org/abs/2607.29600

On R2R-CE val-unseen, with the same planner, grounding model and controller across ablations and three independent runs:
- Full HAM-VLN: success rate `61.0 +/- 1.7`, SPL `48.1 +/- 0.2`.
- Remove world graph with only K=1 working window: SR `51.7 +/- 1.3`.
- Replace graph with *full raw visual history*: SR `53.3 +/- 1.2`, still `7.7 pp` below full HAM-VLN.
- Remove episodic memory: SR `53.3 +/- 2.6`.
- Remove semantic memory: SR `53.3 +/- 0.5`.
- Remove reflection/failure memory: SR `55.7 +/- 1.3`, SPL `36.9 +/- 0.9`.
- Remove all three agentic memory views: SR `50.7 +/- 1.7`.

The system keeps recent observations verbatim but retrieves older place states using subgoal relevance + recency + salience and returns attached failure notes only when their place is retrieved. This independently supports the architecture candidate `small current working window + structured addressable state + subgoal-conditioned retrieval + grounded failure evidence` over simply giving the planner all raw history.

Scope guard: this is zero-shot embodied navigation with a world graph, not software agents; the exact ranking and magnitudes should not be generalized across environments.

### 3. Coding-context bridge: decision-aware utility is promising, but current evidence stops short of end-to-end repair
`Decision-Aware Memory Cards: Counterfactual-Inspired Context Selection and Compression for Tool-Using LLM Agents` (arXiv:2606.08151) explicitly scores candidate context by estimated action shift, outcome uplift, necessity and negative-transfer risk rather than semantic similarity alone.

Primary source: https://arxiv.org/abs/2606.08151

Useful evidence:
- On 50 SWE-bench Verified *file-retrieval* instances, Qwen3.6-plus reranking BM25 top-50 raises hit@1 `0.58 -> 0.78` and MRR@10 `0.634 -> 0.790`.
- In a controlled synthetic utility diagnostic, removing the top-utility unit collapses v3 F1 `0.245 -> 0.000`; random removal gives `0.205`.
- Selected-then-compressed cards save `44.93` tokens/query (95% CI `[41.05, 48.74]`, `p<1e-3`) in the reported compression test.
- Negative boundary: RepoBench-R generic summaries can beat cards, compact rankers do not yet replace the heuristic, and the paper reports only a three-instance patch smoke—not official end-to-end SWE-bench repair success.

Therefore CICL is good support for *how to measure decision-critical context*, but must not be counted as evidence that typed cards themselves improve software-agent task success.

### 4. Abstention is an independent long-horizon control capability, and detecting danger after an irreversible action is too late
`AgentAbstain: Do LLM Agents Know When Not to Act?` (arXiv:2607.10059, submitted 2026-07-11) evaluates 263 paired should-act/should-abstain tasks across 42 executable sandbox environments, 17 frontier models and 4 harnesses.

Primary source: https://arxiv.org/abs/2607.10059

Key results:
- Best paired accuracy is only `59.5%` (Gemini 3.1 Pro); 13/17 models are below 50% paired accuracy. Constant always-act/always-refuse policies cannot exceed 50% by construction.
- Mean act accuracy is `80.6%` versus abstain accuracy `59.1%`; within-model paired act-pass vs abstain-pass correlation averages `phi=-0.10` (15/17 negative). General task ability therefore does not imply calibrated restraint.
- The benchmark records `115` post-hoc abstention cases (`2.6%` of qualifying abstain runs): the agent performs the critical action, then verbally claims or signals restraint. This is especially important for rollback/recovery because the commit boundary has already been crossed.
- The paper finds models do not reliably treat `this operation mutates state` as a feature that changes abstention behavior.

Transfer implication: long-horizon recovery should evaluate `abstain before irreversible commit` separately from failure detection and verbal uncertainty. An `unknown / do-not-commit` state is only useful if enforced before the effect boundary.

### 5. Conformal error localization currently gives exchangeability-based set coverage, not anytime-valid adaptive-trace validity
Re-reading the primary formal statements in `Conformal Agent Error Attribution` (arXiv:2605.06788) clarifies the previous frontier.

Primary source: https://arxiv.org/abs/2605.06788

- Its filtration-based conformal methods produce contiguous prediction sets and satisfy finite-sample coverage assuming calibration/test trajectories are **exchangeable**.
- The paper explicitly lists exchangeability/distribution shift as a limitation and points to adaptive conformal inference as future loosening.
- The rollback experiment then chooses the **earliest step in the conformal set** and restarts with **additional context from the failed trace**.

Thus the reported rollback outcome conflates at least three factors: prediction-set construction, a fixed earliest-in-set target rule, and corrective failed-trace context. It is not a selector-only comparison, and it does not provide an anytime-valid/e-process guarantee for a single adaptively evolving agent trajectory whose policy and state are changed by earlier interventions.

This sharpens the open gap: `contiguous calibrated set under exchangeability` is useful uncertainty quantification, but a deployed rollback localizer still needs validity monitoring under policy/state shift, an abstention state when validity is unsupported, and ideally sequential/anytime guarantees if the same trace is queried repeatedly.

## Synthesis delta
The previous `available -> retrievable -> represented -> decision-proximal -> causally used -> outcome` chain now has direct agent-task support.

A stronger memory/recovery controller candidate is:
1. bounded current working context;
2. source-addressable structured memory outside the immediate context;
3. subgoal/decision-conditioned candidate retrieval;
4. explicit intervention utility (`action shift`, expected outcome uplift, necessity, negative-transfer/disruption risk);
5. targeted transient reminder/card near the relevant decision rather than full-bank exposure;
6. explicit silence/null action;
7. matched next-action and final-outcome counterfactual evaluation;
8. pre-commit abstention/authorization gate for irreversible effects;
9. calibration/validity state for memory and rollback localizers, with `unknown` rather than forced action when deployment validity is unsupported.

The strongest negative lesson is symmetrical across memory and recovery: *adding an auxiliary agent is not intrinsically helpful*. An untrained memory agent can reduce task reward; generic guidance can hurt a domain; full raw history can underperform structured retrieval; and post-hoc abstention cannot undo an irreversible effect.

## Exact continuation
1. Search new software/tool/GUI-agent work for matched `context item present vs absent -> next action/rollback-target change -> final task outcome`, not just retrieval metrics.
2. Search error localizers for online/adaptive conformal, confidence-sequence/e-process, selective prediction or explicit abstention on adaptively queried agent traces; preserve the distinction between exchangeable-trajectory marginal coverage and within-trajectory anytime validity.
3. Extend the strict rollback-selector experimental design with a **decision-influence audit**: for each candidate memory/context unit, branch from the same reconstructed state with item present/absent and measure action distribution shift, selected rollback target, realized recovery dose, final verifier success and disruption of originally successful trajectories.
4. Add `null intervention` and `abstain/do-not-commit` arms; score both under-intervention failures and over-intervention disruption.
5. Long-context ablation: generic summary vs full raw history vs targeted typed restatement vs raw-source lookup near the decision boundary, under increasing irrelevant context, with final task success—not retrieval—as the primary outcome.
6. Continue strict target semantics separation: earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint and intended semantic version are not interchangeable.
7. Continue the vLLM/common-random-number + prefix state-integrity and realized recovery-dose frontier.
8. Maintain a nonempty frontier; this checkpoint is not global completion.
