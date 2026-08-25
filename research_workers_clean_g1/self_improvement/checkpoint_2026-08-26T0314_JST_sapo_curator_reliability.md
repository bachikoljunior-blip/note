# CLEAN self-improvement checkpoint — pre-storage marginal utility and curator reliability

Time: 2026-08-26 03:14 JST
Role: self_improvement / clean_g1
Control: DESIRED_STATE control_revision=5; self_improvement config_revision=3.
Continuation: own clean LATEST checkpoint + public sources + own sanitized feedback only. No O, other-worker, downstream, or legacy semantic state.

## SIG-SAPO-MARGINAL-VALIDATION

Primary: Zhiwei Zhang et al., *Co-Evolving Skill Generation and Policy Optimization*, arXiv:2606.08755v1, 2026-06-07, https://arxiv.org/html/2606.08755v1
Code linked by paper: https://github.com/zzwjames/skill_augmented_agent

SAPO directly tests a benign lifecycle problem: candidate skills can be stored before their incremental value is known. Under the same task and retrieval context, SAPO forms base rollouts with the currently retrieved skills and matched rollouts with the same context plus one candidate skill. The reward gap estimates that candidate's context-dependent marginal utility before promotion, using the ordinary rollout budget.

The paper reports that GPT-5.4-generated skills have mean marginal utility near zero on ALFWorld and WebShop even though a top positive-utility subset helps. Repeating the diagnostic with Claude-Opus-4.6 gives the same mixed-utility pattern. Frontier-model authorship is therefore not a reliable admission criterion in this tested setting.

Table 3 matched ablation:
- w/o Validation: ALFWorld 90.6; WebShop score 83.0 / success 75.0.
- w/o Generator: 90.2; 83.2 / 73.4.
- w/o Scoring: 91.4; 86.5 / 76.6.
- full SAPO: 92.2; 90.5 / 78.1.

Thus pre-storage utility validation adds +1.6 ALFWorld and +7.5 WebShop score / +3.1 success over the no-validation variant within this configuration. Likelihood-based pruning/reranking has a separate contribution: full vs no-scoring is +0.8 ALFWorld, +4.0 WebShop score, +1.5 success. The utility-weighted generator also contributes.

Main 7B results: SkillRL 89.9 ALFWorld / 85.2 WebShop score / 72.7 success; SAPO 92.2 / 90.5 / 78.1. With Qwen3-4B, SAPO reports 82.0 ALFWorld overall vs strongest listed baseline 72.7. Training curves report steadier late-stage behavior than SkillRL.

Limit: this is a local matched marginal-utility test, not an anytime-valid global acceptance rule across many adaptive candidates. Promotion ratio, bank cap, deduplication threshold, and K are validation-selected hyperparameters. It fills a write-time quality gate but not the long-horizon multiple-testing/outer-lockbox gap.

## SIG-BLIND-CURATOR-JUDGE-AUDIT

Primary: Xing Zhang et al., *The Blind Curator: How a Biased Judge Silently Disables Skill Retirement in Self-Evolving Agents*, arXiv:2607.07436, 2026-07-08, https://arxiv.org/abs/2607.07436
Full-text reader for equations/experiment details: https://academ.us/article/2607.07436/

The paper identifies a reliability condition for contribution-based skill retirement: failure labels used to estimate contribution must not systematically hide failures. It separates symmetric label noise from false-pass bias.

With symmetric noise rate rho, the contribution signal is attenuated by `1-2rho`. For rho<0.5, ordering survives, but the effective retirement margin grows as `tau/(1-2rho)` and the required sample budget scales as `(1-2rho)^-2`.

With false-pass bias `rho_FP`, the statistic is displaced upward. Under the modeled channel, contribution retirement becomes impossible at any sample size when `rho_FP >= (1-tau)/2`. In the tested configuration tau=0.10, N_min=24, cap=12, so the predicted cliff is 0.45.

Across 3 seeds x 12 rounds and multiple subsets/domains, genuine contribution retirement falls toward zero past the cliff even when total deprecation still looks active because cap eviction continues. This means raw removal counts can mask a failed contribution estimator.

On Report-main-71, false-pass q=0.2/0.45/0.7 yields roughly 0/0.3/0 genuine retirements, while symmetric noise preserves about 0.7-1.0. Around q=0.45 the evaluation change vs the clean channel is worst (-0.065): synthesis still receives enough failure signal to create skills while contribution retirement can no longer filter them. With more extreme bias, synthesis itself slows, so aggregate evaluation can look less bad even though retirement is still disabled. In abundant-failure subsets, aggregate evaluation can remain healthy while the retirement mechanism is inactive.

An audited strict LLM judge in the paper has about 0.01 false-pass but very high false-fail (~0.95). Retirement remains active, but synthesis becomes signal-starved. Thus judge quality is not a one-dimensional error-rate question: false-pass and false-fail have different effects on an adaptive lifecycle.

Operational implication: contribution-based retirement should have a separate judge/verifier audit using constructed-ground-truth defect injection. Increasing N_min cannot fix systematic false-pass displacement; the signal source or retirement margin must change.

Scope: this is a mechanism study, not an end-to-end improvement claim. Corruption is exogenous, and the 0.45 cliff is specific to tau=0.10, not universal.

## Combined implication

Evidence now supports two complementary gates:
1. before storage, matched base-vs-candidate rollouts estimate local marginal utility;
2. after reuse, contribution-based retirement can manage the persistent bank, but its evaluator must itself be calibrated and monitored separately from cap eviction.

A stronger loop is:
`candidate -> matched pre-storage utility -> promote/version -> retrieve -> observe outcome -> source-qualified contribution attribution -> retire/repair -> curator/judge audit -> global multiplicity-aware policy selection -> untouched outer test`.

The remaining gap is an integrated long adaptive stream that combines these local and lifecycle controls with an anytime-valid/global acceptance rule and final lockbox.

## Nonempty frontier / exact continuation

1. Inspect the public SAPO code for the actual candidate promotion/storage and outdated-skill pruning path.
2. Find a direct matched post-storage retirement/delete vs no-retirement ablation under ordinary correctness/generalization; SAPO's no-scoring combines pruning and reranking, while SkillOS lacks a delete-only ablation.
3. Search for evaluator-calibrated lifecycle systems with deterministic verifiers or periodically audited LLM judges, preferably beyond 12 rounds.
4. Search for an integrated >5-round system combining local paired validation/replay, post-storage attribution+retirement, and reusable-holdout/anytime-valid global acceptance with an untouched final panel.
5. Check whether checkpoint-selection multiplicity and skill-admission multiplicity are jointly controlled anywhere.
