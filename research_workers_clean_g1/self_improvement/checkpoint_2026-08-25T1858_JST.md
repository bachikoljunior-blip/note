# Self Improvement Scan — clean_g1 checkpoint

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 18:58 JST
Search bias: self-improvement/meta-learning; benchmark-first, ablation-first; trace mechanisms backward from quantitative gains.
Boundary: continuation used only prior clean_g1 self_improvement state plus public external sources. No legacy self_improvement state, other workers, comparator/integrator output, O, or O-derived state was read.

## New primary-source branch 1 — GSME provenance resolved

### Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity — arXiv:2607.13683v1, 2026-07-15
Primary v1 PDF: https://arxiv.org/pdf/2607.13683v1
Latest arXiv revision v2 (2026-07-30) is retitled **HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution** and renames the archive/screening formulation while retaining the core semantic-bank + gated-verification idea: https://arxiv.org/html/2607.13683v2

This is the bibliographic identity of the GSME source referenced by the existing HSI frontier. Preserve the version distinction: claims explicitly about GSME terminology should cite v1; claims about the latest paper should use HarnessBank/v2.

### v1 GSME mechanism
- Frozen task model; separate stronger evolver diagnoses failures and proposes harness patches.
- Search archive is categorical quality-diversity keyed by semantic `(where × why)` pathology rather than task identity, one gated elite per cell, with quality-biased global-best extension plus cross-cell recombination.
- `where` spans prompt / knowledge / runtime / config; `why` is model-assigned pathology.
- The diagnosis label steers exploration but does not decide credit; measurement is deterministic.

### v1 three gates
1. **Validity gate**: environment health pre-check; infra failures are repaired/retried up to twice instead of immediately treated as agent failures. Persistent infra failure is kept in denominator and scored 0.
2. **Activation gate**: each patch declares an activation beacon; a mechanism is credited only if it actually fires. Trials on which it never fires are not attributed to it.
3. **Significance gate**: navigation uses K=3 mean pass@1 > vanilla; reported credit requires paired per-task `z >= 1.96` (paired 2-sigma) on the same task set. Final generalization is measured on a sealed test scored once after evolution.

### v1 quantitative evidence
- Six credited sealed-test domains: gains from about +9 to +15.5 pp; retention 86–147% of train gain in v1. SWE-bench test +5.1 pp is explicitly preliminary because n=26 gives z=0.78.
- Recovery-defense matched ablation on LiveCode train, K=3 pass@1: vanilla 64.6; max_tokens 32768 67.0; max_tokens 131072 71.1; thinking-off 73.2; **selective recovery 79.4**. The targeted mechanism therefore beats a 16x token budget and blanket thinking-off within this tested setup.
- Cross-model AppWorld dissociation: Qwen3.6-27B matched verify-finalize +15.5 vs submit-verify +1.2; Qwen3.5-397B +0.2 vs **+13.6**; Gemini 3 Flash +5.8 vs **+13.5**. This supports pathology-matched correction rather than a universal harness patch.
- Gate/archive ablation in v1 text: deterministic `Delta > 0` would credit four candidate mechanisms, including one whose activation beacon fired zero times; a single-run gate credits a truly neutral mechanism roughly 60% of the time and even a >=3 pp apparent 'win' roughly 25% of the time, while only the genuinely significant mechanism survives paired-2sigma on the sealed test. This directly supports activation/significance screening as protection against phantom progress.
- Archive evidence is weaker causally: on four of six domains the selected harness is a cross-cell recombination, and accepted edits span four levers, but there is **no clean no-archive matched ablation** isolating semantic QD itself from the rest of the loop.

### latest v2 HarnessBank equations / ablation
Latest v2 formalizes:
- validity: candidate ledger must be protocol-valid;
- activation: sum of deterministic activation beacons across subset attempts > 0;
- paired significance: per-task difference `delta_i`, mean gain `Delta_hat`, `z = Delta_hat / (sigma_hat_delta / sqrt(n))`, and gate requires `Delta_hat > 0` and `z >= 1.96`.
- Gated screening then filters candidates before full-train evaluation and semantic-bank competition.

v2 TB2 ablation isolates the statistical gate more explicitly:
- HarnessBank (K=3, 2sigma): test 45.4, false elites 0, rounds 10.
- **without 2sigma**: same deployed test score, +2 false elites, does not terminate before >20-round cap.
- **without confirm + 2sigma**: test -1.6 pp vs full, +3 false elites, >20-round cap.
- Post-convergence neutral candidates create phantom progress in 62–76% of rounds under single-run or K=3-mean crediting; paired-2sigma stops at the 10-round floor.
Interpretation: significance gating may matter more for archive hygiene, stopping, and future-parent quality than for a single already-obvious winner. Do not claim the validity gate has an isolated causal ablation; none was found.

## New primary-source branch 2 — adaptive reuse / longer optimization horizon

### VeRO: A Harness for Agents to Optimize Agents — arXiv:2602.22480v4 / ICML 2026
Primary PDF: https://arxiv.org/pdf/2602.22480

VeRO supplies agent-specific evidence that more repeated optimization/evaluation is not monotonically useful.

#### Budget ablation
- Budget B in {2,4,8,16,32}; N=3 per (budget, task); each evaluation call covers a full train/validation set of 46–100 samples, so B=8 is about 400–800 target-agent invocations per run.
- GAIA held-out performance shows an inverted U: **0.119 at B=2 -> 0.195 at B=8**, roughly plateaus through B=16, then **falls to 0.170 at B=32**.
- Authors associate the later decline with optimization-trajectory entropy collapse toward prompt-centric changes plus recorded reverts; this is evidence against 'more self-improvement rounds are always better', but it is not a pure dev-set-reuse ablation.
- GPQA holdout remains in [0.600, 0.630] and MATH in [0.890, 0.897] across budgets, within one-budget SD; TAU-Bench Retail instead rises monotonically from **0.412 -> 0.528** through B=32. So optimal horizon is task-dependent.

#### Validation-to-test mismatch
- VeRO explicitly selects best-validation commits and re-evaluates on holdout where available.
- One MATH trajectory improves validation **0.78 -> 0.92**, but that improvement is not reflected in test and is associated with a lower training score. This is a direct concrete example that an intuitively helpful, validation-selected agent edit can fail to generalize.
- GPQA has no validation split and selects on train; the paper explicitly acknowledges this as an overfitting risk.

Interpretation/scope: adaptive reuse is a real concern in self-improving agents, but VeRO does not isolate repeated reuse of the *same dev set* from simultaneous changes in search policy, candidate family, and trajectory entropy. Treat the GAIA inverted-U as empirical warning, not a reusable-holdout causal proof.

## New primary-source branch 3 — reusable holdout theory + synthetic demonstration

### Generalization in Adaptive Data Analysis and Holdout Reuse — Dwork et al., NeurIPS 2015 / arXiv:1506.02629
Primary: https://arxiv.org/abs/1506.02629

This is not an agent paper; it is a transferable statistical mechanism for the unresolved repeated-dev-reuse problem.

- Repeated adaptive holdout use can overfit the holdout itself.
- Thresholdout compares train and holdout statistics; when discrepancy is small it returns the train estimate, and only when discrepancy crosses a noisy threshold does it reveal a noisy holdout estimate and decrement an overfitting budget. This limits information leaked from the holdout across adaptive queries.
- Synthetic null experiment: n=10,000, d=10,000, labels independent of features, so true classifier accuracy cannot exceed 50%. Reusing a standard holdout yields **>63% reported accuracy at k=500** on both train and holdout, while a fresh dataset exposes the spurious result. Thresholdout prevents the holdout overfit and returns a valid estimate in this setup.
- The paper's implementation used threshold T=0.04 and tau=0.01 and Gaussian noise for the experiment.

Transfer hypothesis only: a self-improvement acceptance gate that repeatedly exposes exact dev scores is an adaptive data-analysis channel. Potential mitigations include a fresh final sealed test, bounded acceptance-query budget, coarse/noisy release of dev evidence, rotating or growing canary pools, or sequentially valid testing. Do **not** transplant differential-privacy machinery wholesale without an agent-specific matched experiment.

## Updated mechanism hypotheses

1. **Credit is a control-plane object, not a proposer judgment.** The strongest current evidence supports separating semantic proposal from deterministic validity/activation/statistical credit.
2. **Activation should be measured before attribution.** A candidate that never fires can look beneficial under noisy score comparison; activation beacons localize this failure cheaply.
3. **Statistical gates mainly protect compounding dynamics.** In HarnessBank v2, removing 2sigma need not change the immediate winner, yet it inserts false elites and prevents convergence. This matters because false positives become future parents/memory.
4. **Pathology-keyed diversity is promising but not causally isolated.** Cross-cell recombination often appears in winners, but no clean no-archive control was found. Preserve as medium-strength search-structure hypothesis, not proven necessity.
5. **Longer improvement horizons need horizon control.** VeRO shows GAIA degrades after a mid-budget peak while TAU-Bench continues improving; continuation policy should be evidence-conditioned rather than always-more-rounds.
6. **A fixed dev gate can itself become part of the optimization target.** VeRO's validation/test mismatch plus classical adaptive-data-analysis results motivate an explicit 'gate integrity under reuse' metric.

## Rejected / narrowed interpretations

- Do not call arXiv:2607.13683 simply 'GSME' without versioning: v1 used GSME; latest v2 is retitled HarnessBank and changes terminology/formal presentation.
- Do not claim all three GSME/HarnessBank gates have separate matched ablations. Significance is isolated; activation has a concrete inert-candidate diagnostic; validity lacks a standalone causal ablation.
- Do not claim semantic quality-diversity itself causes the full held-out gain; no no-archive matched control was found.
- Do not interpret VeRO's B=32 GAIA drop as pure validation-set overfitting; search-distribution collapse and late prompt-centric drift are co-varying explanations.
- Do not assume reusable-holdout differential privacy is directly deployable for agent evaluation without cost/utility experiments.

## Nonempty unresolved frontier

1. Search for a **direct agent-specific dev-reuse ablation**: fixed candidate generator, same dev set, varying number of adaptive acceptance queries, with fresh sealed-test measurement.
2. Search for **sequentially valid / anytime-valid tests** or alpha-spending/e-process methods applied to repeated agent candidate acceptance; extract false-positive control vs rollout cost.
3. Inspect **SkillOpt (arXiv:2605.23904)** and related validation-gated skill evolution for whether they rotate validation data, reuse fixed gates, or report gate-overfitting failures.
4. Find a true **no-archive / greedy-search control** for HarnessBank/GSME, or independent work that isolates semantic pathology-keyed QD from gating and proposer strength.
5. Quantify **activation/adherence metrics** in other self-improvement systems and whether low activation predicts negative transfer before full evaluation.
6. Return to **MetaSkill-Evolve** primary tables and verify fast-loop vs slow-loop marginal gains and matched costs.
7. Search August 2026 papers after 2026-08-17 for newer self-improvement benchmarks with candidate-level statistical credit or dev-set reuse controls.

## Exact continuation

Next concrete action: search primary sources for **SkillOpt (arXiv:2605.23904)** and any agent/self-improvement paper using sequentially valid or reusable holdout-style acceptance. Extract whether the validation set is reused adaptively, the number of acceptance queries/rounds, any fresh sealed-test result, and an ablation of gate policy. If no agent-specific sequential test exists, branch to modern anytime-valid/e-process methods that could be adapted and record only experimentally demonstrated tradeoffs.

## Termination diagnostics

This checkpoint is not completion. After resolving GSME provenance and gates, the run continued into the unresolved adaptive-holdout frontier, inspected VeRO's budget/validation behavior, and then followed the statistical reusable-holdout branch. Frontier remains nonempty and exact continuation is above.
