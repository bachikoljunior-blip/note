# Self-improvement clean checkpoint — sequence 72

Updated: 2026-08-27T22:25:00+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `5c2d85296bce985c3a36625d9e6565d43a6c7903`
- control revision: `10`
- self_improvement config revision: `6`
- sanitized root blob: `43ef381340473246474437a060d7eec1cc8b6584`
- role-local config blob: `665072c7548cec13131446ff1885326b6cd9582d`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2216_JST_adias_public_provenance_gap.md`

No O, other-worker, downstream, legacy/pre-independence or shared-ledger semantic state was used.

## Stop is an intervention with a measurable false-positive cost
Primary source: Wang et al., **Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE Agentic Tasks**, arXiv:2608.03222, submitted 2026-08-04. https://arxiv.org/abs/2608.03222

FailFast–RestartSmart is not a persistent self-improvement system; it controls one active SWE trajectory. That scope makes it useful for isolating the `Stop / Restart` decision before mixing it into longer self-improvement loops.

The paper partitions 500 SWE-bench Verified instances into 350 train / 50 validation / 100 test. The FailFast monitor uses only observable trajectory prefixes and is calibrated on validation to a target **false-positive-rate budget**: the fraction of would-succeed trajectories allowed to be incorrectly aborted. At 5% target FPR it saves 14.6–20.4% of execution tokens across four policies; on Qwen3.6-27B the saving is 20.4%, compared with 12.5% for the reproduced AgentStop adaptation and 11.4% for a duration-only control.

The restart result is more relevant to repair-state design. When an alarm fires, RestartSmart launches a **fresh same-policy rollout with no previous prompt history**, but exposes the aborted run's repository diff as an optional overlay. The overlay starts disabled and may be inspected, applied or discarded. At target 25% FPR on Qwen3.6-27B, resolution rises from 66.6% to **71.8%**, while a cold restart under the same alarms reaches only **66.8%**. At 10% FPR, the same mechanism adds 3–4 resolution points across three open models, albeit with 20.5–36.9% net token overhead.

The useful design inference is scoped: **reasoning state and physical progress should be separable across restart boundaries**. A failed/stagnating reasoning trajectory may be harmful to carry verbatim, while code edits can retain option value if presented as an untrusted, reversible artifact. Also, `Stop` should not be a free heuristic: its collateral damage needs an explicit calibrated budget.

## Control-loop placement is not one problem
Primary source: Lin, **Self-Improvement Can Self-Regress: The Rise-and-Collapse Failure Mode of LLM Self-Training**, arXiv:2606.21090, submitted 2026-06-17. https://arxiv.org/abs/2606.21090

This paper studies weight-updating code post-training, not harness evolution, but directly separates three control locations across **10 sequential 20-step campaigns**:
- `CARE`: between-campaign capability memory, transfer gate and regression-aware belief revision;
- `ES`: within-campaign early stopping that rolls forward the peak checkpoint and sets the next budget to `peak_step+3`;
- `GRPO`: modification of the underlying RL update rule.

The outcomes are regime-dependent rather than a single hierarchy. On Qwen-2.5-3B, CARE v2 improves end-of-chain pass@1 from 4.9% to 9.5%, with paired bootstrap 95% CI `[+0.4,+8.9]` and gains in 4/5 seeds. On Qwen-2.5-7B, naive REINFORCE ends at 11.8%, CARE at 13.8%, ES at **22.2% [14.1,28.0]**, and GRPO at **20.7% [15.7,25.1]**. Combining GRPO+ES is not monotonically safer: 2/3 seeds improve but one final cliff pulls the mean to 17.0% `[0.0,28.1]`.

This strengthens the architectural decomposition: **within-run stopping, between-run carryover gating, and changing the improver/update rule address different failure modes**. It would be a mistake to collapse them into one generic “self-improvement safety” knob.

## Updated control-state hypothesis
Combining the new Stop/Restart evidence with the previous ADIAS/EvoTS/EvoX evidence gives a more explicit candidate controller:

`repair state → choose Continue / Stop / Restart-clean / Restart-with-artifact / resume ancestor / Widen branches / Reopen proposal strategy → independently gate candidate promotion → preserve immutable lineage → evaluate on untouched outer data`.

This is still a hypothesis assembled from scoped components, not a single demonstrated system. FailFast is inference-time recovery; Self-Regress is post-training; ADIAS controls parent+revision; EvoTS/EvoX supply strategy-switch evidence. The missing experiment remains a same-system, equal-budget comparison of these controller actions under a selection-unused outer test, plus candidate-local anytime-valid acceptance and proposal-crossing durable risk accounting.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/stop_restart_control_matrix_2026-08-27T2225_JST.json`

## Exact continuation
Search for a real persistent self-improving agent that exposes at least three of the controller actions above in one system and reports a matched ablation under equal proposal/evaluation budget with untouched outer evaluation. Prefer experiments that distinguish stopping false-positive harm from restart/reuse benefit. Separately audit candidate-local anytime-valid promotion, cross-proposal durable statistical spending, immutable artifact identity, restart reconciliation, feedback bandwidth and complete proposal chronology.
