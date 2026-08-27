# Long Horizon clean_g1 checkpoint — actionable alternatives and retry budgets

Observed checkpoint time: 2026-08-28T07:04:47.571206+09:00

## Frozen semantic control tuple
- frozen note main SHA: `3009465cf48864bd1377c2f62f170c7804b6c1d0`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- semantic inputs used: own `LATEST.md`, own latest checkpoint, own sanitized feedback, and public sources only. No O/O-derived state, other-worker state, downstream state, legacy/pre_independence research, shared aggregate ledger, or other-role receipts/configs were used.
- repository main later advanced during the invocation. Later movement was used only for write safety and was not adopted semantically.

## New evidence

### 1. A direct final-success feedback-content factorial substantially closes the previous feedback-interface gap
Primary paper: Jaideep Ray and Ankit Goyal, *Structured Feedback Improves Repair in an LLM Agent Loop*, arXiv:2607.14167v1, 2026-07-15, https://arxiv.org/html/2607.14167v1

VeriHarness uses deterministic external validation and a bounded retry loop. Its primary experiment holds task, model, gate and four-call cap fixed across four feedback policies on the same 50 TextWorld games for each model:
- `RawDiag`: original validation error only;
- `LocObs`: failure label + location + observed value, but no alternatives;
- `SameNL`: location + observed value + admissible alternatives in prose;
- `TypedFields`: the same repair values in named fields plus a failure label.

Primary results:
- Qwen2.5-Coder-14B: `14/50 (28%)` RawDiag, `18/50 (36%)` LocObs, `35/50 (70%)` SameNL, `36/50 (72%)` TypedFields.
- Llama-3.1-8B: `8/50 (16%)`, `9/50 (18%)`, `29/50 (58%)`, `29/50 (58%)` respectively.
- TypedFields vs RawDiag: `+44pp` Qwen, 95% paired-bootstrap interval `[28,60]`, Holm-adjusted exact `p=3.15e-5`; `+42pp` Llama, interval `[28,56]`, `p=3.81e-6`.
- The key ablation is alternatives: TypedFields vs LocObs is `+36pp` Qwen and `+40pp` Llama. Location + observation alone stays close to RawDiag.
- Serialization is not the active ingredient in this study: SameNL vs TypedFields differs by only `+2pp` Qwen and `0pp` Llama, with both adjusted `p=1`.
- Under budget sensitivity, RawDiag is flat from four through eight calls on the 15-game subset, while structured feedback continues to exploit extra calls. More retries are not useful if they do not receive decision-relevant new information.
- The 15-task HumanEval scope check is an important limit: one answer passed the visible assertion but failed hidden tests, so all feedback policies stopped after one call and all finished `14/15`. Feedback cannot repair a failure the validator cannot expose.

Control implication: the previous hypothesis that post-failure interfaces should expose *reachable repair affordances* now has direct paired final-success evidence in a bounded agent loop. The dominant content is not merely `where/what failed`; it is the set of valid replacements available in the current state. JSON-like structure may help orchestration/logging, but no reasoning advantage over matched prose was detected here.

Scope guard: this is 50 generated TextWorld games, two quantized open models, deterministic validator semantics and enumerable alternatives. It is not repository-scale software repair or production API evidence, and the first-call prompt names the policy, so pre-repair prompts are not byte-identical.

### 2. Re-reading the end-to-end rollouts in `Feedback That Backfires` separates anti-loop success from task success
Primary paper: Esmail Gumaan, *Feedback That Backfires: Why Small Language Model Agents Repeat the Call They Just Watched Fail*, arXiv:2608.23651, submitted 2026-08-24, https://arxiv.org/abs/2608.23651

The earlier checkpoint emphasized the teacher-forced repetition mechanism. Its 24-task Qwen2.5-0.5B ToolShed rollout table adds an important outcome-level correction:
- standard verbatim harness: success `0.42`, exact failed-action repetition `0.31`;
- `abstract` failure representation: success `0.33`, repetition `0.16`;
- verbatim + decoder ban: success `0.42`, repetition `0.08`;
- clean restart/drop: success `0.33`, repetition `0.80`;
- explicit `do not repeat`: success `0.58`, repetition `0.24`.

Paired analyses sharpen the mismatch:
- decoder ban cuts repetition `31% -> 8%` and loops `29% -> 12%`, but task success changes `+0pp`;
- abstraction reduces repetition but changes success by `-8pp` with interval `[-21,0]`;
- clean restart drives repetition `31% -> 80%` and does not improve success;
- the natural-language prohibition moves success by `+17pp [4,33]` even though its measured repetition change is not significant; the authors explicitly decline to attribute that success gain to the repetition mechanism.

Control implication: a mechanism metric such as loop/repetition rate is not a safe surrogate for final success. Suppressing the failed surface form can release budget without supplying a competent next action. This makes the VeriHarness alternatives result especially important: a robust post-failure interface needs both **anti-anchoring** and **actionable replacement information**.

Scope guard: end-to-end rollouts cover one 0.5B model and 24 tasks. The anti-loop mechanism is broader across six small checkpoints, but the task-success numbers are not.

### 3. Structured reflection can be trained, but it does not isolate runtime feedback encoding
Primary paper: Junhao Su et al., *Failure Makes the Agent Stronger: Enhancing Accuracy through Structured Reflection for Reliable Tool Interactions*, arXiv:2509.18847v3, revised 2026-04-15, https://arxiv.org/abs/2509.18847

Tool-Reflection-Bench contains perturbation-derived tool-call failures. The trained Llama-3.1-8B improves Repair@1/3/5 from `0.7/5.1/6.8` to `4.7/20.5/26.4`; Qwen2.5-7B from `2.4/6.1/8.0` to `9.3/10.3/11.4`; Qwen3-4B from `9.6/10.6/10.6` to `14.9/18.5/19.5`.

This supports a distinct mechanism: a model can learn a `diagnose -> propose executable correction` policy. But the benchmark test set consists only of failure cases and the intervention is post-training, not a same-model runtime encoding factorial. It therefore does not measure benign-prefix disruption or tell us whether raw error vs transformed error vs alternatives is the active runtime variable.

### 4. Retry must be budgeted across the whole stack, not only at the agent policy layer
Primary agent paper: Isham Kalappurackal Mansoor et al., *Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures*, arXiv:2608.02645, https://arxiv.org/abs/2608.02645

Its separate medium-fault ablation compares retry-only, verify-only and verify-before-retry. Retry-only is about `58%` success / `42%` duplicate actions; verify-only about `80% / 20%`; verify-before-retry about `72% / 28%`. The paper explicitly concludes verification is the main measured factor and retry is not always beneficial.

A new experimental-confound detail is important: the LLM client itself retries rate-limited responses **up to five times**. Thus an apparent `recovery off` arm can still contain lower-layer retries unless the experiment audits SDK/client/gateway/provider behavior.

Adjacent systems evidence: Sanjit Ghosh et al., *Retry Amplification in Distributed Systems*, arXiv:2608.25403, 2026-08-26, https://arxiv.org/abs/2608.25403. In a five-tier simulator under correlated failure, no-retry succeeds `55.4%`, standard three-attempt retry `41.5%`, circuit breaker `55.3%`, adaptive retry budgeting `54.9%`; standard retry raises observed amplification to `1.34x` versus `1.00-1.01x` for the controlled strategies. This is not LLM-agent evidence, but it establishes the systems mechanism that independently configured retries at multiple layers can compose into an amplifier.

Control implication: a recovery controller should own a **global retry/effect budget** across agent loop, tool wrapper, SDK/client, gateway and provider layers. `retry OFF` in future factorials must mean either all such layers are disabled or every hidden retry is measured and included in realized recovery dose.

Scope guard: the distributed-systems result is simulator/system evidence, not direct proof of the same quantitative effect in LLM agents.

## Current synthesis delta
The previous post-failure interface hypothesis can now be sharpened to:

`authoritative state/effect observation -> fault/recoverability class -> transform/suppress harmful verbatim failure surface -> expose validator-known location/observation only if useful -> expose currently admissible recovery alternatives/affordances -> choose one competing recovery action under a global retry/effect budget -> verify terminal/effect state`

Three primary studies now converge on the *actionability* of feedback rather than diagnostic verbosity or serialization:
- VeriHarness: admissible alternatives carry most of a `+42 to +44pp` final-success gain over raw diagnostics in TextWorld;
- Outcome Monitors (previous checkpoint): removing the public recovery-tool list removes the ToolMaze gain while extra diagnostic detail/timing does not help;
- Feedback That Backfires: changing the failed surface form can suppress loops without improving final success, proving that anti-anchoring alone is insufficient.

The controller therefore needs two separate objectives after failure:
1. **do not re-anchor the policy on the failed action**;
2. **make a feasible corrective action identifiable**.

A third objective is systems-level: ensure additional attempts do not silently multiply across layers.

## Updated high-value controlled experiment
Hold fixed the same failure-producing prefix, external state, model, validator, candidate recovery action set, stochastic coupling and total realized recovery budget. Cross:

### Feedback content axis
1. raw diagnostic;
2. location + observation only;
3. admissible alternatives only;
4. location + observation + alternatives in prose;
5. same values in keyed/typed form;
6. transformed failure description + alternatives;
7. verbatim failed action + alternatives.

### Recovery-execution axis
- no additional attempt;
- one agent-level retry with all lower-layer retries disabled/accounted;
- verify/reconcile before retry;
- switch/resume/replan/rollback/abstain when indicated by class.

Measure separately:
- failure -> success rescue;
- benign/success -> failure disruption on matched nonfailure prefixes;
- exact/canonical failed-action repetition;
- wrong recovery-action class;
- validator-visible vs hidden failure coverage;
- realized model calls, tool executions and hidden SDK/provider retries;
- duplicate/unsafe external effects;
- token/action/time cost.

The central unanswered question is no longer whether actionable alternatives can help in a bounded tool loop; that now has direct evidence. It is whether the same causal ordering survives **stateful software/API agents with non-atomic effects and non-enumerable alternatives**, and how it interacts with verification, Reviewer/critic intervention and rollback.

## Exact continuation
1. Find repository-scale software/API-agent common-replicate experiments that compare raw diagnostics vs validator-generated *actionable alternatives* under equal compute and measure final success plus disruption/effect safety.
2. Search the complete `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2. Require a true no-interface/no-recovery cell and audit hidden SDK/client/gateway/provider retries.
3. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials while holding failure representation and affordance exposure fixed.
4. Search class-aware controllers choosing `no-op / retry / switch / resume / rollback / replan / abstain` under one global recovery budget, reporting wrong-action confusion and realized multi-layer retry dose.
5. Search critic-refresh cadence comparisons `frozen / periodic-k / drift-triggered / continuous` with a fixed base-policy checkpoint and matched critic-update/evaluation budget.
6. Preserve rollback-selector-only comparison with alarm, candidate checkpoints, restore/carry-forward/inference state, model, guidance, stochastic coupling and post-intervention budget fixed.
7. Add persistent-refinement contamination experiments: reward-only admission vs independent authority/spec validation vs validation + revocable lineage, with delayed descendant contamination after reuse/evolution.
8. Keep transient interruption, process state loss, ambiguous effect, schema/argument, stale/contradictory observation, permission/authority, rate-limit, irreversible effect, terminal-belief error, repetition loop, missing procedure and impossible/no-valid-path failures separate.
9. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized Reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission x maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
10. Locate official SymTrace/SymFail source if publicly discoverable; paper methodology remains usable evidence, but runtime/API claims remain unverified until code is identified.
11. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
12. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
