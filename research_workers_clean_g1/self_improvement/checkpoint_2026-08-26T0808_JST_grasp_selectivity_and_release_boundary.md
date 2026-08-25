# CLEAN self-improvement checkpoint — GRASP gate selectivity and public-release audit boundary

Run timestamp: 2026-08-26 08:08 JST
Role: self_improvement / clean_g1
Frozen semantic control tuple remains the invocation tuple: note main `9c2ca150e7c708cb3e36aa6cfb0d21720cd41c18`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. This checkpoint extends only the own-role/public-source work already begun under that frozen tuple. No later repository control state was adopted semantically.

## GRASP gate selectivity: promotion is sparse, not automatic

Primary: Johannes Moll et al., *GRASP: Gated Regression-Aware Skill Proposer for Self-Improving LLM Agents*, arXiv:2605.29668, current v3 revised 21 Aug 2026 and accepted to EMNLP 2026 Main.
Primary source: https://arxiv.org/abs/2605.29668
Public repository inspected: `jomoll/GRASP@9d7d125a3e9b46ed591692475eb07aff4ae67d34`.

The current primary paper reports useful gate-selectivity statistics across the five main seeds. GRASP applies an edit in about **64% of development batches** and rejects all four candidates in the other **36%**. Across all generated candidates, only about **16%** are admitted; on average **1.3 of 4 candidates per batch** clear the hard regression budget. Accepted edits have median net probe score 3 and mean 4 fixed examples above the acceptance threshold, with a tail to 15.

This matters because it rules out an interpretation of the gate as ceremonial bookkeeping. The loop often decides that none of the proposed persistent edits is trustworthy enough to promote. Coupled with the no-gate ablation from the preceding checkpoint, the evidence says the useful mechanism is not merely repeated skill writing: **selective non-promotion is part of the gain**.

Probe sensitivity also shows a nontrivial statistical-compute tradeoff. With the same general mechanism, reported test accuracy is about **82.3** for probe size N=16, **88.8** for N=36, and **86.5** for N=72. Candidate count K=1 yields **73.4±23.1**, K=4 gives the 88.8 main result, and K=8 falls to **84.4±8.3**. The paper notes that a larger candidate pool on a fixed probe can dilute reliability. Thus “more proposals” or “more validation” is not monotonically beneficial; the proposal-to-evidence ratio itself is a control variable.

## Public-release audit boundary

The repository's `results/README.md` says the public result mirror contains per-epoch validation scores, held-out scores, failure taxonomies, best/end learned skill libraries with history, and run configurations. It **deliberately omits full per-episode rollout traces, run logs, and per-epoch `*_updates.json` edit logs** to keep the mirror small; full traces are described as available on request.

This creates a precise reproducibility boundary. The aggregate gate selectivity and ablation results are primary-paper evidence, and the released implementation shows how candidates would be proposed, forked, probed and conditionally applied. But the public mirror does not expose enough candidate-level chronology to independently reconstruct every proposed edit, its incumbent/candidate probe result, the rejected candidates, and the exact acceptance history for the reported seeds.

The same boundary affects the 10-epoch stability claim. The paper reports a separate one-seed-per-method 10-epoch stability run, which is longer than its standard five-epoch main protocol. The searched public result configs for the main gpt-oss MedAgentBench runs are five-epoch configs, and this run did not locate a separately labelled released 10-epoch stability config/artifact. This is **not evidence that the run did not exist**; it means late-round acceptance-rate drift, repeated-probe overfitting, and candidate-history diagnostics cannot currently be independently reconstructed from the public mirror found here.

## Secondary mechanism contrast: MUSE-Autoskill

Primary: Huawei Lin et al., *MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation*, arXiv:2605.27366, 26 May 2026.
Primary source: https://arxiv.org/abs/2605.27366

MUSE-Autoskill is a useful lower-strength contrast for lifecycle gating. Its skill creation path uses unit tests before registering a newly created skill; a failed test triggers revision and rerun, and the broader lifecycle supports refinement/merging/pruning using execution feedback. On SkillsBench, the paper reports 53.19% without skills, 68.40% with human skills, and 60.35% overall with self-created skills; a Hermes executor using MUSE-generated skills improves from 47.89% to 58.40%, versus 61.21% with human skills.

However, the causal evidence is weaker than GRASP. The unit-test gate is not isolated in a matched ablation, and the self-created-skill evaluation largely reuses task identities after a successful trajectory has been discovered. Therefore this supports the general engineering idea of **testable lifecycle-managed skills**, but it should not be used as clean evidence that its unit-test promotion gate alone causes cross-task generalization.

## Updated evidence hierarchy

For persistent self-improvement promotion, the strongest current evidence in this frontier is now:

1. **GRASP** — matched candidate/incumbent behavioral replay, hard regression budget, explicit no-op, equal-compute controls, disjoint final test, and direct no-gate ablation.
2. **SkillEvo** — strong four-round governed improvement with separate evaluator family, untouched chronological final quarter, and human production confirmation, but no public implementation/reproduction found here and no anytime-valid long-horizon statistics.
3. **MUSE-Autoskill** — lifecycle/unit-test engineering evidence and positive skill reuse/transfer, but promotion-gate causality is not cleanly isolated.
4. **MindMemOS generic public path** — useful counterexample: a newly minted `draft` version is immediately copied into the live skill directory, demonstrating why lifecycle labels cannot substitute for auditing the executable activation boundary.

## Exact continuation

1. Search GRASP issues/releases/branches or requested artifacts for the omitted update logs or a public 10-epoch stability package. If unavailable, preserve candidate-chronology and late-round probe-overfit analysis as an explicit artifact-access gap.
2. Look for a way to replay released or obtainable GRASP candidate/probe histories under a sequential/e-process decision rule, holding proposal generation fixed, to quantify how many current accepted edits survive anytime-valid multiplicity control.
3. Continue searching for a real **>10-round** persistent LLM-agent system that combines editable lifecycle repair/retirement, reusable-holdout/e-process acceptance, proposal/round-global error spending, and an untouched final lockbox.
4. Continue locating the exact MindMemOS Table-4 40-task/eight-trajectory Sup/Unsup orchestration and its promotion/checkpoint semantics.
5. Continue SkillEvo code/reproduction and leakage audit; continue SkillShapley task/model-resampling and length-neutral controls.
6. Prefer cross-version/downstream causal attribution via dependency-aware selective replay over presence-based effectiveness heuristics.
7. Retain matched-total-compute/search controls whenever the evolution condition spends additional proposal/probe/evolution inference.
