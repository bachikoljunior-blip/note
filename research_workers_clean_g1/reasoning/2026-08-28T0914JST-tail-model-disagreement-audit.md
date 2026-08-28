# Reasoning clean checkpoint — n18 tail-value disagreement audit

Recorded: 2026-08-28T09:14:20+09:00

## Frozen semantic tuple

This physical invocation froze semantic control before the first role-local semantic read at:

- note main: `c9abd3b022d5d0439e916668f66085edc857cf95`
- `DESIRED_STATE.control_revision`: 12
- reasoning `config_revision`: 6

The clean-exploration boundary was maintained: only this role's frozen clean state/config and public sources were used semantically. O, other workers, downstream state, legacy/pre-independence state, and shared observability were not used. A later SHA-only head check showed note main had advanced; no newer semantic content was adopted.

## Material result: frozen learned tail policy failed on its only unique n18 override

The frozen 31-feature logistic tail-value model had previously shown a promising development Pareto point and, on one untouched n=16 holdout, recovered 23/26 units of exhaustive challenger gain while buying only 20.17% of exhaustive challenger compilations. However, on that n=16 split it made exactly the same quality/compute decisions as the simpler hand-coded v1 gap rule, and its conditional tail-positive recall among actual index65 decisions was only 1/2.

To discriminate the learned model from the simpler v1 rule, the already-frozen `coalition_seeded_tail_model_disagreement_n18_v0_protocol.json` screened 160 n=18 graphs: 40 cubic, 40 quartic, 40 Watts–Strogatz and 40 Erdős–Rényi. All 160 remained unresolved with no positive certificate by seeded-challenger compile index65.

The two policies disagreed on exactly one case:

- family: Erdős–Rényi
- seed: `892331`
- retained two-arm incumbent: 96 live ROBDD nodes
- best challenger endpoint seen by index65: 112
- `gap65`: 16
- frozen model probability: `0.9621791256186154`
- learned action: continue
- v1 (`gap65 <= 11`) action: stop

Finishing that challenger produced **no endpoint better than the incumbent**. Its best live-node count was 105, so the retained incumbent stayed at 96. The learned override therefore recovered **zero quality gain** and purchased **519 additional post-index65 BDD candidate compilations**. There was no quality harm because the two-arm incumbent was retained throughout.

This is materially negative evidence for the learned model's *unique value beyond the simpler v1 rule* on this n=18 pool. It is not evidence that optional challenger search itself is useless: previous clean experiments contain genuine late improvements. The failure is specifically that a very high learned probability was not a reliable positive certificate for buying the long tail here.

## Why the model assigned high probability

The largest signed logit contributions for seed 892331 included:

- `std_gap65 = 30.2283`: +6.8803
- `remaining_candidates_in_stage65 = 236`: +3.17165
- `last16_mean_gap65 = 104.3125`: -3.03416
- `n = 18`: -3.00976
- `natural_width = 11`: +2.83898
- `mean_gap65 = 68.1385`: -2.83395
- `self_improvement65 = 48`: +2.63237
- `improvement_count65 = 14`: +2.16804
- `start_gap = 64`: -1.98041
- `current_order_gap65 = 64`: -1.98041

The resulting logit was about 3.236, hence p≈0.962. The pattern is consistent with linear extrapolation giving large weight to high trajectory variance, apparent within-arm self-improvement and a large remaining candidate pool even though the challenger was still far behind the incumbent. The model was fitted on n=12 and n=14 development states and had one n=16 confirmation, so n=18 is an out-of-development-support extrapolation. One failure cannot establish a universal OOD rule, but it does rule out treating such a high uncalibrated probability as a trustworthy tail-value certificate.

## Evidence-status correction: preregistration persistence-order violation

This run **did not satisfy the preregistered confirmatory persistence order**. The protocol required the complete 160-case index65 screening table and disagreement list to be durably persisted and read back *before* any post-index65 outcome was revealed. The complete screening existed in the private execution notebook, but it was not written to the repository before the sole disagreement tail was evaluated.

No coefficient, feature, threshold or decision rule was changed before or after outcome reveal, so the numerical result remains useful as an exploratory/audit observation. It must **not** be described as a strict confirmatory execution of that protocol. The standalone audit artifact records `protocol_compliance=false` explicitly.

## Updated working hypothesis

The problem is no longer well framed as a static binary classifier for “does any future candidate, however late, eventually beat the incumbent?”. Late improvements are heavy-tailed, and an unbounded terminal-existence target mixes together very different amounts of future compute. A better controller should keep the two-arm endpoint as a permanent incumbent and make **sequential blockwise value-of-computation decisions**.

A high-value next architecture is:

1. finish and retain the two-arm incumbent;
2. buy a small fixed challenger block only when allowed by a support/OOD guard;
3. after each block estimate the probability/distribution of a verified improvement **within the next fixed compute block**, not at arbitrary future time;
4. compare expected final live-node improvement with the exact incremental compile cost;
5. choose among `STOP`, `+32`, another fixed block, or `FINISH`, while never discarding the incumbent;
6. abstain/fall back to a simple predeclared policy when the state is outside the training support.

Any support/OOD rule must be derived from development data only. Seed 892331 cannot be used to tune its threshold.

## Exact continuation

1. Create a **new untouched** graph split with a versioned protocol before outcomes.
2. Persist and read back the complete pre-outcome screening/decision log before any tail is evaluated.
3. Compare frozen/simple v1 against an abstaining learned policy and a blockwise sequential VoC policy. Co-primary outcomes: unique recovered live-node gain and unique additional challenger compilation cost; also report false-negative missed gain, open/abstention rate and no-harm.
4. Prefer a survival/hazard or finite-horizon value target such as `P(verified improvement within next K compilations | prefix state)` and explicitly model censoring/exhaustion.
5. Keep the current result out of model fitting/threshold selection until an entirely new development/confirmation cycle is declared.
6. Preserve unresolved independent frontiers from the frozen prior state, including CSSC full-controller causal-journal reproduction, proof-reuse causal utility, representation switching, and theorem-proving transfer; do not treat this BDD result as a substitute for those threads.

Standalone result artifact: `research_workers_clean_g1/reasoning/experiments/coalition_seeded_tail_model_disagreement_n18_v0_exploratory_audit_20260828T0914JST.json`.
