# Long Horizon clean_g1 — shift-robust conformal checkpoint

## Frozen semantic control tuple
- invocation_started_at: `2026-08-26T17:57:27+09:00`
- checkpointed_at: `2026-08-26T18:03:47+09:00`
- frozen note main SHA: `cc9cb9fae8c79c150521a860142ab7d7b0e27e85`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- this is a continuation under the already frozen semantic tuple; later repository writes were not adopted as semantic control.
- semantic boundary preserved: only own clean state, own sanitized feedback and public sources were used.

## New primary-source findings

### 1. Conformal candidate regions need an explicit shift-validity state; calibrated confidence can fail before raw accuracy visibly fails
`Post-Hoc Trajectory-Risk Certification for Modular LLM-Based Security Agents` (arXiv:2608.05199; Aug. 4, 2026) studies trajectory-level conformal certificates across a two-stage security-agent pipeline. Across 12 configurations, average trajectory coverage is `92.7% ± 2.4%` at alpha `0.10`. Under cross-dataset deployment, however, the paper reports **single-step miscoverage reaching 100% while accuracy remains 78%**.

Primary source: https://arxiv.org/abs/2608.05199

Transfer implication for rollback localization is deliberately narrow: a conformal rollback candidate region calibrated on one trace distribution should not be treated as currently valid merely because the localizer's raw exact/top-k accuracy still appears acceptable. A `coverage_assumption_status`/shift alarm must be first-class, and stale certification should fail closed or trigger recalibration rather than silently continue.

This does NOT establish that the same magnitude of miscoverage occurs for rollback targets; the task and labels differ.

### 2. Online shift adaptation itself can fail because density-ratio estimation degenerates; adaptation method must be audited, not assumed
`Online Shift Detection and Conformal Adaptation for Deployed Safety Classifiers` (arXiv:2606.11949; Jun. 10, 2026) reports an 800-cell preregistered factorial. Shift detection is valid in `693/800 = 86.6%` cells with mean latency `39.5` steps. Weighted conformal adaptation recovers up to `39 pp` of lost coverage for DeBERTa in one regime, but collapses for other classifiers because high-dimensional density-ratio estimation perfectly separates source/target and clips importance weights to the floor. PCA to 32 dimensions restores substantial correction in some cases (`+33 pp` Llama Guard, `+21 pp` ShieldGemma).

Primary source: https://arxiv.org/abs/2606.11949

Transfer implication: for sequential rollback-target sets under shift, `detected_shift=true` is not enough to justify reweighting. The controller should record effective sample size / weight degeneracy / calibration feasibility and abstain when the adaptation layer itself is unreliable.

Again, this is evidence from safety classifiers, not a direct rollback-target experiment.

### 3. Recent anytime selective-risk work suggests a better conceptual fallback for non-exchangeable streams than frozen marginal conformal sets
`Conformal Selective Acting: Anytime-Valid Risk Control for RLVR-Trained LLMs` (arXiv:2605.20270; May 18, 2026) explicitly targets adaptive online streams where offline exchangeability is unavailable. It uses per-threshold e-processes and selective action/release rather than claiming a frozen split-conformal set remains valid indefinitely. Across the paper's reported 10,300 rounds, it claims pathwise validity and non-refusing deployment on every tested cell among ten compared methods.

Primary source: https://arxiv.org/abs/2605.20270

This is not a localization method and should not be transplanted mechanically. But it sharpens the rollback controller architecture: when trace distribution is adaptive/non-exchangeable, the uncertainty layer should expose a sequential validity contract (or explicit `unknown`) rather than reuse an exchangeable calibration guarantee out of scope.

### 4. Structured tool-call risk control reinforces semantic stratification instead of one aggregate confidence score
`Beyond Aggregate Risk: Role-Stratified Conformal Risk Control for LLM Tool Calls` (arXiv:2607.24343; Jul. 27, 2026) calibrates separate risk budgets for semantic argument roles and reports more consistent role-specific compliance under model/attack transfer, detector noise, drift, unseen tool suites and adaptive attacks than aggregate-only calibration.

Primary source: https://arxiv.org/abs/2607.24343

Transfer implication: rollback/localization uncertainty may need stratification by semantic event class (e.g. reversible local edit, external commit, credential/recipient binding, environment transition) because an aggregate historical-target confidence can hide rare high-risk target classes. This is a design hypothesis, not yet direct evidence for rollback-target selection.

## Synthesis delta
The uncertainty component of the long-horizon recovery controller should now carry **validity provenance**, not only a set/score:
- calibration distribution / trace regime identity;
- exchangeability or sequential-validity assumption status;
- shift detector state and detection latency;
- recalibration/adaptation method;
- effective calibration sample size / weight degeneracy diagnostics;
- semantic risk stratum when target classes have materially different consequences;
- explicit abstention / unknown state when validity cannot be certified.

This strengthens the prior controller split:
`risk/failure sensing -> validity/shift check -> calibrated candidate region or unknown -> admissibility/safe-boundary filter -> historical target selector -> live recovery evaluation`.

It also strengthens the experimental requirement: selector studies should report target-localizer coverage **conditional on deployment regime/shift state**, not one pooled coverage number.

## Exact continuation
1. Search for rollback/error-localization methods with sequential/e-process/conformal validity directly on adaptive agent traces; do not infer direct applicability from safety-classifier work.
2. Search whether any causal/executed-replay localizer reports calibration under distribution shift, not just annotated-step accuracy.
3. Design an executed-replay audit of conformal candidate regions stratified by trace regime and semantic event class; measure coverage, set width, abstention, live recovery success and redo cost separately.
4. Continue the vLLM CRN/trace-replay frontier: quantify same-position Gumbel coupling under divergent logits, and find a verified trace-replay-to-live handoff.
5. Continue searching for realized post-rollback recovery-dose reporting.
6. Preserve strict selector-only gap and target-semantics distinctions.
7. Maintain a nonempty frontier; this checkpoint is not global completion.
