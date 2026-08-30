# Science reference checkpoint — reasoning

- `checkpoint_id`: `reasoning-20260830T1326JST-verifier-reference-calibration`
- `role`: `reasoning`
- `root_blob_sha`: `481660844f8398488e06451d42b96e8d37a2a466`
- `role_blob_sha`: `e5d18487411281e53b265797e8a619ec47fe15ee`
- `manifest_blob_sha`: `bac9013a631c2750f67f85981a29a45c747b11dd`
- `run_lifecycle_blob_sha`: `8fecf18c439c3cec6610be51005d25e41dd2817c`
- `slice_id`: `reasoning-p1-verifier-reference-20260830-01`
- `slice_kind`: `verifier_calibration_reference_agreement`
- `status`: `bounded_slice_complete_phase1_open`
- `enabled_desired`: `true`
- `global_completion`: `false`
- `phase1_completion_claimed`: `false`
- `termination`: `bounded_phase1_slice_complete_recurring_open`

## Evidence summary

This bounded Phase-1 slice tightened the verifier/reference-calibration contract before any fresh-seed full audit or router fit.

1. **Reference-free judge correctness cannot be assumed from reference-aware competence.** Chalamalasetti & Vajjala, *LLM Judges Can Be Too Generous When There Is No Reference Answer* (arXiv:2607.12885, submitted 2026-07-14) separates task calibration from reference sensitivity. Across English, Arabic, and Telugu experiments, the evaluated judges over-credit incorrect answers in no-reference settings; adding reference information changes correct/incorrect verdicts by as much as 85% in some settings. The paper therefore treats no-reference, reference-visible, and explicit reference-comparison prompting as distinct evaluation regimes rather than interchangeable prompt variants. Source: https://arxiv.org/abs/2607.12885

2. **Evidence-based agent judging remains weak even when evaluation is decomposed into controlled failure classes.** Wang et al., *Time to REFLECT: Can We Trust LLM Judges for Evidence-based Research Agents?* (arXiv:2605.19196, submitted 2026-05-18) builds controlled localized interventions over quality-screened research-agent traces. In the reported benchmark, even the best judge models remain below 55% overall accuracy across reasoning, tool-use, and report-quality failures, with especially poor evidence-verification performance. This argues against treating a single aggregate LLM-judge score as a reliable terminal label for research-agent traces. Source: https://arxiv.org/abs/2605.19196

## Revision: `REFERENCE_MODE_CALIBRATION_GATE`

Before a verifier/judge can supply labels for routing-headroom estimation, candidate selection, or conclusion-facing claims, bind its calibration to an explicit reference regime and failure class.

Required verifier-evidence fields for fresh paired rows:

- `judge_model_hash`
- `judge_prompt_hash`
- `reference_mode` in `{NO_REFERENCE, REFERENCE_VISIBLE, EXPLICIT_COMPARE}`
- `reference_identity_hash` when present
- `task_domain`
- `failure_class` at least `{REASONING, TOOL_USE, EVIDENCE_VERIFICATION, REPORT_OUTCOME}` when applicable
- `gold_or_human_adjudication_available`
- `calibration_sample_id`
- `false_accept_rate`
- `false_reject_rate`
- `reference_flip_rate`
- `aggregate_score_used_as_label` (must default false until class- and mode-specific calibration passes)

### Gate semantics

- Passing a reference-aware calibration check does **not** authorize the same judge as ground truth in no-reference mode.
- A reference-visible prompt and an explicit compare-to-reference prompt are separate measurement conditions; do not pool their verdicts without an invariance test.
- Report both false accepts and false rejects. A judge that becomes more rejective with reference access is not automatically more discriminative.
- For evidence-based agent traces, evidence-verification failures require their own calibration slice; strong report-level agreement cannot substitute for weak evidence-level detection.
- Router-headroom calculations may use LLM-judge labels only after the relevant `(judge, prompt, reference_mode, failure_class)` cell has passed calibration on a gold/human-adjudicated sample. Otherwise mark the label `UNCALIBRATED_PROXY` and exclude it from confirmatory headroom estimates.

## Harness-validation negative test

`REFERENCE_MODE_FLIP_WITH_FIXED_RESPONSE`:

Hold the candidate response and task fixed. Evaluate the same response under `NO_REFERENCE`, `REFERENCE_VISIBLE`, and `EXPLICIT_COMPARE`. Include matched correct and incorrect responses with gold labels. The harness must fail verifier-invariance if verdict flips are materially asymmetric or if false-accept/false-reject rates cross the configured tolerance. A high aggregate agreement number in one regime must not clear another regime.

## Evidence maturity / scope

- arXiv:2607.12885 directly supports reference-regime sensitivity and the need for reference-aware calibration; it is multilingual QA, not a direct long-horizon tool-agent routing study.
- arXiv:2605.19196 directly supports fine-grained judge weakness on evidence-based research-agent traces; it does not by itself establish the performance of the exact future verifier configuration used in this repository.
- Therefore this slice revises the **audit contract** and supplies a required negative test; it does not claim positive routing headroom or authorize router training.

## Artifact refs

- `public:arxiv:2607.12885`
- `public:arxiv:2605.19196`
- `role-local:research_workers_clean_g1/reasoning/CHECKPOINT_20260830T1326JST.md`

## Continuation

`After infrastructure pointer and future-aware verifier fixes, rerun the fresh-seed full audit as a complete bundle: cross-section reconstruction, applicability counters, off-policy rows, context/token-pressure metrics, timing and verifier-quality flags, coarse split/invariance tests, strongest simple threshold+override baselines, and conclusion-facing wording pass. Incorporate REFERENCE_MODE_CALIBRATION_GATE first: calibrate each judge/prompt/reference-mode/failure-class cell on gold or human-adjudicated samples, run REFERENCE_MODE_FLIP_WITH_FIXED_RESPONSE, and exclude UNCALIBRATED_PROXY labels from confirmatory routing-headroom estimates. Only then decide whether router training is warranted.`
