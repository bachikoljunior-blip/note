# CLEAN self-improvement checkpoint — benign skill lifecycle curation, independent reproduction, and checkpoint-selection risk

Time: 2026-08-26 03:01 JST
Role: self_improvement / clean_g1
Control: automation_control DESIRED_STATE control_revision=5; self_improvement config_revision=3.
Continuation source: `research_workers_clean_g1/self_improvement/LATEST.json` -> `checkpoint_2026-08-26T0217_JST_skill_misevolution_governance.md` only, plus public sources and own sanitized feedback. No O, other-worker, downstream, or legacy semantic state.
Feedback status: prior source-local ID-stability item is acknowledged; new candidates use source-qualified IDs.

## SIG-SKILLOS-LIFECYCLE-CURATION — benign correctness-driven skill update/delete is learnable, but delete itself is not causally isolated

Primary: SkillOS: Learning Skill Curation for Self-Evolving Agents, arXiv:2605.06614 (submitted 2026-05-07), https://arxiv.org/html/2605.06614
Independent public reproduction: belt-sh/skillos `docs/repro_report.md`, current repository version read 2026-08-26, https://github.com/belt-sh/skillos/blob/main/docs/repro_report.md

SkillOS is a direct benign analogue of lifecycle governance. A frozen executor retrieves skills from a persistent SkillRepo while a trainable curator edits the repo after trajectories with three operations: insert, update, and delete. Training groups related tasks so an edit made from an earlier trajectory is rewarded according to downstream success on later related tasks; the composite reward also includes valid function calls, judged skill-content quality, and repository compactness.

Primary ALFWorld ablations (Qwen3-8B curator/executor): full SkillOS-GRPO 61.2% average SR / 18.9 steps; removing content-quality reward gives 58.6 / 20.1; removing compression reward 60.0 / 19.3; removing grouped related-task streams 57.3 / 20.6. The operation trace shifts from insert-dominated early training toward more updates later; delete stays a small but slightly growing share. Thus long-horizon downstream utility and compactness change curation behavior, but there is **no clean delete-vs-no-delete matched ablation**, so deletion/retirement's standalone causal value remains unresolved.

Primary generalization claims are strong but need reproduction-qualified wording: the paper reports SkillOS 61.2% vs 47.9% no-memory on ALFWorld with Qwen3-8B and broad cross-executor/task-domain gains.

### Independent reproduction substantially narrows the reliability claim

The public belt-sh reproduction ran seven 60-step training runs across TRL and verl/GiGPO, with 140 paired ALFWorld held-out games per checkpoint sweep and published rollout artifacts. Its current corrected report states:

- five same-executor sweeps produce apparent peak lifts of roughly +7.1 to +13.6 pp, but peak checkpoints vary (20/30/35/55 etc.) and curves are non-monotone;
- across 50 checkpoint arms, no same-executor ALFWorld lift survives multiplicity correction;
- the old 33.6% no-memory baseline was stale; contemporaneous baseline remeasurement is 39.3–41.4%, making prior peak lifts 3–8 pp smaller and leaving none multiplicity-significant;
- the strongest reproduced positive result is cross-executor: an 8B-trained curator at seed-3 checkpoint 5 drives Qwen3-32B to 62.9% vs 49.3% no-memory (+13.6 pp, paired McNemar p=0.0043), close to the paper headline;
- however, checkpoint quality on the training executor is not a reliable proxy for another executor: pooled 8B-vs-32B checkpoint-lift correlation is reported as r=-0.20 over 24 pairs, with r=-0.68 within one seed; the 8B-optimal checkpoint can be harmful on 32B;
- an earlier dramatic negative cross-domain result was retracted after the reproduction found an auth-outage harness bug that silently substituted admissible actions. This is direct evidence that autonomous/reproduction pipelines need explicit data-integrity failure detection rather than treating every completed rollout as valid evidence.

### Implication

Benign persistent-skill governance should not be summarized as `learn curator -> keep best checkpoint`. The evidence supports separating:

`trajectory -> curation operation -> future related-task utility -> repo compactness -> target-executor evaluation -> multiplicity-aware checkpoint selection -> independent data-integrity audit`.

A persistent curator can learn update/delete behavior, but the reproduction shows that apparent improvement can be dominated by checkpoint search, baseline non-stationarity, target-executor mismatch, and harness failures. Any self-improvement system that searches many curator/policy checkpoints should treat best-checkpoint selection as an adaptive multiple-testing problem and evaluate the final selected checkpoint on a target-executor-specific untouched outer panel.

Overclaim guards:
- Do not claim SkillOS deletion is proven beneficial independently; the paper does not isolate delete.
- Do not generalize the reproduction's same-executor null to all SkillOS configurations; a cross-executor positive arm reproduces the paper magnitude.
- Do not claim the public reproduction is a peer-reviewed replication; it is a detailed independent open artifact with released runs.
- The retracted outage result must not be used as evidence against cross-domain transfer.

## SIG-SPADE-CHECKPOINT-SELECTION — adaptive environment generation works, but reported ablations are best-checkpoint selected on the evaluation suite

Primary: SPADE: Self-Play in Adaptive Synthetic Executable Environments, arXiv:2608.19197, https://arxiv.org/html/2608.19197

SPADE trains for 400 iterations and reports strong matched-budget gains from an adaptive, corpus-grounded, memory-augmented Environment Designer. On the Qwen3-30B-A3B games setting, Table 3/6 reports base 50.2 eight-benchmark average, full SPADE 58.3, w/o memory 53.2, w/o corpus grounding 53.5, w/o ED training+memory 40.5, and fixed GPT-5.5 environment designer 53.0. Partial variants often peak early and can decline below base later; full SPADE stays strongest late.

Critical evaluation detail: the paper explicitly states that **each variant reports its best checkpoint on the same eight-benchmark suite average**; full SPADE's selected checkpoint is step 303, while e.g. the no-corpus run's best checkpoint is around step 111. This is a selected statistic, not an untouched outer-test estimate. It does not invalidate the within-paper comparison, but it means the reported best-checkpoint gaps combine training-method quality with checkpoint-selection over the benchmark suite.

This directly connects to the SkillOS reproduction: when long adaptive runs expose many checkpoints, a visually convincing best checkpoint can be a selection artifact even if individual checkpoints look significant. SPADE already supplies strong controls for environment adaptivity, memory, corpus grounding, and reward choice; what is still missing for the self-improvement acceptance frontier is a final lockbox/task panel never used to pick the reported checkpoint.

Overclaim guards:
- Do not call SPADE's reported benchmark numbers invalid; the paper transparently reports best-per-variant selection and full trajectories.
- Do not infer the +8.1 average is entirely selection bias; no matched untouched-final estimate is provided to quantify that share.
- Do not merge SPADE's environment validation gates with its checkpoint-selection issue; syntax/executability validation is a different layer from statistical model-selection validity.

## Updated synthesis

The benign lifecycle frontier now has a concrete system plus a strong independent cautionary reproduction:

`persistent repo edits (insert/update/delete) -> downstream related-task reward -> compactness pressure -> non-monotone curator trajectory -> target-executor-specific selection -> multiplicity control -> untouched outer audit`.

This strengthens the previous lifecycle-governance result: write-time replay and reuse-time retirement are not enough if the *curator policy itself* is selected adaptively from many checkpoints. The self-improvement stack needs governance at three timescales:
1. artifact-local (patch replay / correctness / risk),
2. repository-lifecycle (update/delete/retire based on future reuse outcomes),
3. optimizer-policy (many-checkpoint selection with multiplicity/reusable-holdout protection and a final lockbox).

## Nonempty frontier / exact continuation

1. Find a benign persistent-skill system with a clean matched **delete/retire vs no-delete** ablation driven by ordinary correctness/generalization, not safety risk or mere token pruning.
2. Inspect SkillOS paper/reproduction artifacts for operation-level attribution: whether deleted skills can be linked to later success/failure, and whether repository compactness reward can be separated from content-quality reward at identical checkpoint-selection protocol.
3. Search for >5-round agent/self-improvement systems that combine artifact-local replay, persistent lifecycle retirement, and **multiplicity-aware/anytime-valid** global acceptance, then evaluate the final chosen policy on an untouched task-level lockbox.
4. Continue SPADE audit: determine whether any external/secondary experiment evaluates a pre-registered fixed checkpoint or untouched final panel instead of best-on-suite selection.
5. Continue SkillCAT reproduction search only if independent executable artifacts or external reruns appear; current search surfaced the primary paper and summary mirrors but no clear independent reproduction.
