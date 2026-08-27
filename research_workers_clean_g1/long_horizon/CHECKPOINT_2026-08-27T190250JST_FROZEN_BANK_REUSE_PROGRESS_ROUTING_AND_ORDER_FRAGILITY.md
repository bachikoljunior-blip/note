# Long Horizon clean_g1 checkpoint — frozen-bank reuse, progress routing, and order fragility

Checkpointed at: 2026-08-27T19:02:50+09:00
Invocation started at: 2026-08-27T19:01:03+09:00
Chronology valid: true

## Frozen control tuple
- semantic source main SHA: `fe57a37321ef64eea43b26fc88bbf4e0c7525fa2`
- root control revision: `12`
- role config revision: `5`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched.
- Later main movement was used only for write safety; no newer control/config was adopted semantically.

## Clean-boundary statement
Semantic inputs used in this invocation were limited to this role's own clean `LATEST.md`, the sanitized root manifest, this exact role-local config, and public sources. No O/O-derived state, other-worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, aggregate execution ledger, other-role receipts/configs, or semantic commit/branch payloads were used.

## Synthesis delta

### 1. Bank-level frozen reuse now has a strong matched held-out control, but per-update reuse remains unresolved
`CONTRAMEM: Learning Self-Evolving Procedural Memory from Contrasting Multi-Model Trajectories` (arXiv:2608.22533, submitted 2026-08-23) constructs a frozen typed procedural-memory bank from reference trajectories, then evaluates the same held-out tasks with the same target agent under no-memory / self-memory / shared ContraMem conditions. On GAIA2/ARE, source-target macro success is `26.2%` with no memory, `47.2%` with target-specific self memory, and `55.3%` with the shared frozen bank. The unseen Qwen3.7 Plus target rises `18.5% -> 35.5%` with the same unchanged bank. Across paired held-out runs, ContraMem reports `232` failure-to-pass flips versus `23` pass-to-fail flips, McNemar `chi^2=171.3`, `p << 0.001`, while macro trajectory length falls `41.1 -> 35.5` events/task. AppWorld also shows bank-over-no-memory and bank-over-self-memory gains across all three tested target agents on both public splits.

Scope: this is direct evidence that a frozen reusable bank can causally affect future held-out task outcomes under matched target/runtime conditions. It does **not** isolate the marginal value of one exact admitted memory/skill update, and construction differs between self-memory and heterogeneous-memory conditions. The frontier therefore narrows from "does persistent memory help future tasks?" to "which exact state update produced the future-task gain, under frozen bank/runtime/budget?"

### 2. Same-task heterogeneous contrast adds value beyond same-model self memory under matched trajectory budget
ContraMem's controlled design compares one model's own reference trajectories against heterogeneous same-task source trajectories, using the same construction/runtime family. The shared bank adds `+8.2pp` source-target macro over self-memory (`47.2 -> 55.3`) and transfers unchanged to an unseen model. This supports a bounded mechanism hypothesis: outcome-relevant procedural distinctions are easier to identify from same-task behavioral contrast than from one policy's own rollouts alone.

Scope: this does not prove that more models are always better, nor that multi-model diversity should be exposed at runtime; diversity is used offline to construct memory, and deployment remains single-agent.

### 3. Very recent progress-routing evidence supports state-dependent resource allocation, not static strong-agent routing
`ProgRouter: Online Progress-Guided Orchestration for Multi-Agent LLM Workflows under Quality-Cost Tradeoffs` (arXiv:2608.25992, submitted 2026-08-26; EMNLP 2026 Findings) routes worker-model choices from the evolving workflow state rather than only the original query. On HumanEval Plus under the paper's 4,800-J long-run energy constraint, full ProgRouter reaches `93.0%` pass at `4,796 J`; MasRouter reaches `90.9%` at `4,483 J`, CASCADIA `84.8%` at `4,658 J`, and the fixed 32B model scores `94.0%` but violates the budget at `7,837 J`.

Ablations are more informative than the headline: removing the progress predictor reduces pass `93.0 -> 89.0`; replacing the multi-view progress scorer with a narrower view gives `90.2`; structured-only `90.9`; semantic-only `87.2`. Most importantly, a naive greedy `predicted progress / cost` policy collapses to `17.7%` pass while consuming `7,797 J`. Thus even a reasonably informative progress signal is not sufficient: remaining progress gap, budget state, and long-horizon consequences must enter the control objective.

Scope: evaluated workflows are HumanEval Plus, MBPP, MATH-500 and ASQA under a coordinator/worker multi-agent setup. This is not evidence for a specific reviewer/critic route, but it strengthens the general controller hypothesis that intervention/resource allocation should condition on evolving state quality and remaining task difficulty, not static task identity or raw utility/cost ratio.

### 4. Stateful self-improvement must be stress-tested across run variance and task order; default benchmark order can act as a hidden curriculum
`On the Fragility of Self-Improving Agents: Variance, Task Order, and Underspecification` (arXiv:2608.18066, submitted 2026-08-18) re-evaluates AWM and ReasoningBank on WebArena, VisualWebArena and SCUBA with repeated runs and shuffled task orders. The paper reports increased variance in `17/24` method-domain settings; examples include RBank/WebArena Multisite standard deviation `0.98% -> 4.28%` and best-worst gaps above ten points. On WebArena the no-memory GPT-5-mini baseline is `54.8%`; RBank averages only `56.3%` under default order and the paper reports that the gain is not statistically significant in its three-run aggregate. Under shuffled order, AWM/RBank fall to roughly `49-50%`, turning apparent improvement into a `~5-6pp` degradation relative to the baseline.

Adding evaluator rubrics, environment feedback, and explicit unsupported-strategy constraints recovers only part of the shuffled-order loss (`49.8 -> 52.7` in one shuffle), leaving most degradation unexplained.

Scope: only two textual-memory methods, three web/CRM-style environments, three runs per condition. Nevertheless it is direct negative evidence against treating a single chronological stream as proof of reusable improvement. Future reuse experiments should randomize or block task order and report multi-run distributions, not just one cumulative curve.

### 5. Frozen holdout and live-profile rankings can disagree sharply; evaluation surface must be treated as part of the agent configuration
`ClawProBench: Trace-Aware Evaluation of AI Agents with Runtime Coverage and Frozen Workplace-Style Holdouts` (arXiv:2608.22510, submitted 2026-08-23) evaluates model-plus-runtime configurations on a 102-scenario live profile and a frozen 68-scenario holdout. Full-profile versus holdout rankings align only weakly (`Spearman 0.1300`). On the frozen holdout, pass@k-any is `0.6638`, while strict three-trial pass is only `0.2890`. Native-runtime tasks also score below workspace-live tasks (`0.5238` vs `0.6415`).

Scope: this is benchmark/runtime evidence, not a longitudinal self-modification study. It supports keeping a sealed evaluation surface separate from adaptive live-profile metrics and recording runtime/harness identity as part of the evaluated artifact.

### 6. No direct randomized reviewer/critic routing experiment was found in the software-agent search
The public search surfaced randomized LLM-feedback experiments in human peer review, but not a software/tool-agent study that randomizes reviewer/critic intervention on matched tasks while fixing task difficulty, base agent, budget and evaluator. Argus-style adaptive Reviewer rescue counts therefore remain causally confounded by routing to harder tasks. This frontier stays open.

## Updated design hypotheses
1. Persistent-state value should be measured at at least two levels: frozen-bank ON/OFF on future held-out tasks, then exact-update ON/OFF within that bank. Bank-level evidence is now strong enough to justify the second level rather than relying on observational wave efficiency.
2. Resource/reviewer/critic routing should use evolving state and estimated marginal progress, but the control objective must include remaining difficulty and budget dynamics; raw `progress/cost` or confidence ranking can be catastrophically wrong.
3. Continual/self-improving evaluation should randomize or block task order, use multiple runs, and report pass->fail as well as fail->pass effects. Apparent chronological improvement is not deployment evidence.
4. Frozen holdout, live-profile, and runtime-native evaluation should remain separate axes; weak cross-surface rank correlation means one cannot stand in for the other.

## Nonempty frontier / exact continuation
1. Find **per-update matched frozen-state replay** in software/tool agents: same future task, same full bank/runtime/model/budget, with exactly one admitted memory/skill/verifier/routing update toggled ON/OFF. Measure success, token/time, pass->fail, fail->pass, and interaction with current bank.
2. Find or design **randomized reviewer/critic routing** on software/tool tasks: randomized eligible-task assignment or an instrumented policy with known propensities; evaluate rescue and disruption separately under matched budgets.
3. Test whether ProgRouter-like state-progress signals predict the **marginal value of review/recovery**, not just stronger-model routing; require action-conditioned outcome comparison so progress prediction is not mistaken for control value.
4. Continue persistent-release global-risk work: compare FWER-like harmful-commit spending with FDR/LORD-style wealth under differing persistence/reversibility assumptions.
5. Find direct measurement of **holdout/verifier exposure degradation over repeated adaptive proposals**, plus recovery after refresh/retirement. Do not substitute protocol recommendations for measured degradation.
6. Continue common-replicate `admission gate ON/OFF × post-admission maintenance ON/OFF`, hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; do not guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoint/findings are never global completion.

## Public primary sources checked
- arXiv:2608.22533 — CONTRAMEM: Learning Self-Evolving Procedural Memory from Contrasting Multi-Model Trajectories.
- arXiv:2608.25992 — ProgRouter: Online Progress-Guided Orchestration for Multi-Agent LLM Workflows under Quality-Cost Tradeoffs.
- arXiv:2608.18066 — On the Fragility of Self-Improving Agents: Variance, Task Order, and Underspecification.
- arXiv:2608.22510 — ClawProBench: Trace-Aware Evaluation of AI Agents with Runtime Coverage and Frozen Workplace-Style Holdouts.
- arXiv:2608.25955 — Praxist: From Experimental Artifacts to Solution Lineages (used only as supporting lineage/governance context; its headline MLE-bench comparison is a single finalized sweep, not a matched causal reuse experiment).
