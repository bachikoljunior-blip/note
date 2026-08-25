# Long Horizon external research — clean_g1 checkpoint — 2026-08-25 23:58 JST

## Boundary / provenance
- Generation: `clean_g1`.
- Worker: `long_horizon`.
- Effective repository control read first: `automation_control/DESIRED_STATE.json`, control_revision 3, role `long_horizon`, config_revision 2, enabled_desired=true, control blob `df95ef1fcc2d2bd84daecb6d56ea3c7fa5c9aa3a`.
- Continuation input was limited to this worker's own clean namespace, public sources, and own sanitized feedback path.
- Own sanitized feedback `research_feedback_clean_g1/long_horizon/FEEDBACK.json` was checked and remains absent (404); no feedback was consumed.
- Did not use O/O-derived state, other workers, comparator/integrator/index/feed, shared execution ledger, other-role receipts, or legacy/pre-independence research as semantic research context.
- Previous continuation point: `CHECKPOINT_2026-08-25T2300JST.md` blob `77889746aea0c9fbe818e00ce5bd6c1306ec9927`.

## New primary-source finding A — a direct online state-quality/intervention gate exists, and it is explicitly false-positive-budgeted
Primary: `Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE Agentic Tasks`, arXiv:2608.03222v1, 2026-08-04, https://arxiv.org/abs/2608.03222 and HTML https://arxiv.org/html/2608.03222 .

This directly fills part of the prior frontier asking for an online corruption/failure signal that gates intervention and is evaluated on final task outcomes rather than detector AUROC alone.

### Mechanism
- FailFast is a 0.6B online monitor using only observable trajectory prefixes, not policy logits/hidden states.
- Its input is task ISSUE plus a recent eight-step WINDOW of thoughts/actions/observations and a persistent pin of the latest patch-producing step.
- Training adds dense fail-to-pass progress targets obtained by replaying intermediate patches against the official evaluator.
- Deployment is explicitly a budgeted alarm: maximize failure recall subject to a target trajectory-level false-positive rate (FPR), rather than maximizing detector accuracy without intervention cost.
- Alarm inference is suppressed in the noisy opening phase; the reported best balance uses a minimum 20-step gate. Count-M or sustained-K voting reduces single-step noise.
- On alarm, RestartSmart starts a fresh same-policy rollout with no old prompt history and offers the aborted run's repository diff as an optional, unverified overlay. The new agent can inspect/apply/discard it. This separates recoverable physical work from potentially bad reasoning history.

### Direct quantitative evidence
SWE-bench Verified:
- At target 5% FPR, FailFast saves 14.6–20.4% of execution tokens across four policy models. On Qwen3.6-27B, 20.4% saved exceeds the paper's AgentStop adaptation at 12.5%.
- At target 10% FPR, RestartSmart improves final resolution by +3.0 to +4.0 percentage points across three open-weight policies.
- Qwen3.6-27B baseline resolution 66.6%:
  - RestartSmart, 10% FPR: 69.8% (+3.2 pp), FP-lost 15.2%, TP-recovered 27.6%, +30.3% net token overhead.
  - cold restart, 10%: 67.2% (+0.6), FP-lost 36.4%, TP-recovered 19.7%, +17.8% overhead.
  - RestartSmart, 25%: 71.8% (+5.2), FP-lost 8.8%, TP-recovered 28.9%, +43.8% overhead.
  - cold restart, 25%: 66.8% (+0.2), FP-lost 27.5%, TP-recovered 20.2%, +18.2% overhead.
- Qwen3.5-9B baseline 48.2%: RestartSmart peaks at 52.2% (+4.0) at 10% FPR; cold restart 50.8% (+2.6).
- Gemma4-31B baseline 62.2%: RestartSmart reaches 65.2% (+3.0); cold restart 64.0% (+1.8) at 10% FPR.

### Strong negative evidence inside the same matched experiment
- A prompt-level intervention baseline (SWE-PRM) helps the weaker Qwen3.5-9B: 48.2% -> 52.4% (+4.2), but hurts the stronger Qwen3.6-27B: 66.6% -> 63.4% (-3.2). The paper argues intrusive corrective prompting can disrupt a stronger agent's coherent policy and, unlike FailFast, lacks an explicit FPR budget.
- Cold restart is not equivalent to smart recovery. On Qwen3.6-27B it destroys up to 36.4% of false-alarm runs at 10% FPR and yields only +0.2 pp at the 25% operating point, despite lower compute cost.
- Thus a state-quality trigger is not sufficient by itself: the intervention type and what crosses the restart boundary determine whether the detector creates net value.

### Intervention-boundary ablation: do not cut at the alarm instant if an atomic edit/effect is still settling
RestartSmart compares immediate termination at the alarm with a patience boundary that waits for the first post-alarm edit and then five edit-free steps before freezing the overlay.

Qwen3.6-27B:
- 10% FPR: Immediate FP-lost 21.2 / TP-recovered 28.9 / resolution 69.6 (+3.0); Wait 15.2 / 27.6 / 69.8 (+3.2).
- 25% FPR: Immediate 18.8 / 22.8 / 68.8 (+2.2); Wait 8.8 / 28.9 / 71.8 (+5.2).

Scope-bounded interpretation: a correct alarm may still be a bad *cut point*. Waiting until the current recoverable artifact reaches a coherent boundary can sharply reduce disruption. This supports separating `whether to intervene` from `when the current atomic semantic/effect unit is safe to cut`.

### Important scope limits
- Evidence is SWE-bench Verified under mini-swe-agent, not a universal long-horizon environment result.
- The monitor predicts terminal failure from observable prefixes, not a generic latent-state integrity score.
- RestartSmart is fresh retry + optional code-diff carryover, not arbitrary historical checkpoint selection or coupled context/environment rewind.
- Higher resolution costs extra compute: Qwen3.6's +5.2 pp point uses +43.8% net token overhead; 10% FPR is more compute-efficient (+3.2 pp at +30.3%).

## New primary-source finding B — rollback intervention timing has a non-monotonic information-bandwidth optimum
Primary: `Generator-Assistant Stepwise Rollback Framework for Large Language Model Agent`, EMNLP 2025, ACL Anthology 2025.emnlp-main.892, https://aclanthology.org/2025.emnlp-main.892/ .

GA-Rollback uses a generator plus an assistant that reviews actions/observations, identifies the earliest recent erroneous action, and asks the generator to roll back. The environment is reconstructed by reset + replay to the selected earlier trajectory prefix. Low-confidence assistant feedback can be filtered to prevent unnecessary rollback.

For embodied ALFWorld, the Wait-Info strategy deliberately delays the assistant's diagnosis so that it sees a bounded number of subsequent generator actions before deciding where to roll back. The primary Figure 4 shows a clear inverted-U relationship:
- performance rises as wait horizon grows to about `k=6`, producing roughly a 4–8 percentage-point gain over the no-wait baseline, then declines as the context becomes noisy/combinatorial;
- Qwen2.5-14B-Instruct is about 80.6% at the no-wait baseline and peaks at 88.1% around k=6;
- GLM4-9B-Chat likewise peaks near k=6 at about 78.3% from a low-70s no-wait baseline.

The authors interpret this as an information-bandwidth trade-off: too little look-ahead starves diagnosis of causal evidence, while too much floods it with error-diffused state. The paper also explicitly notes that longer embodied tasks remain challenging, particularly in determining which step to roll back to.

Scope-bounded interpretation:
- This is evidence that rollback diagnosis/targeting need not be best at either immediate intervention or arbitrarily long observation.
- It is not a direct matched comparison of target-selection algorithms (fixed-depth vs latest-good vs root-cause vs learned selector). The historical target-selection frontier therefore remains open.
- GA-Rollback is computationally expensive relative to Act-only in its reported settings; rollback control must be evaluated jointly with task success and cost.

## Updated synthesis — recovery is at least a five-control problem
The strongest current decomposition is now:
1. **Checkpoint placement/granularity**: snapshot only recovery-relevant state changes where possible (prior Crab evidence).
2. **Whether to intervene**: use an online state/failure signal with an explicit false-positive/disruption budget, not detector accuracy alone (FailFast).
3. **When to cut after the alarm**: respect atomic/semantic/effect completion boundaries; an alarm instant can be an incoherent rollback boundary (RestartSmart patience ablation).
4. **Where in history to resume**: fixed-depth/latest-good/root-cause/dependency/semantic-admissible/learned or agent-selected remains insufficiently compared head-to-head; GA-Rollback shows diagnosis has an information-horizon optimum and acknowledges this remains hard.
5. **What to carry across recovery**: preserve useful, inspectable artifacts without blindly preserving the reasoning trajectory; optional code-diff overlay beats cold restart in the tested SWE setting. For reversible environment/context state, prior AgentRewind/DART evidence remains relevant; irreversible/compensable effects require separate accounting.

A useful controller objective should therefore optimize final task success minus compute/latency/storage/effect-risk, while explicitly reporting at least false-positive disruption (`FP lost`) and true-failure recovery (`TP recovered`).

## Tempered / rejected hypotheses added this run
- `An accurate online failure detector solves recovery`: rejected. Recovery mechanism and false-positive disruption are separately causal.
- `When the alarm fires, stop immediately`: rejected as a universal rule; coherent edit completion materially changes outcomes in RestartSmart.
- `Fresh restart is the safest neutral response`: rejected in the tested SWE setting; it discards useful artifacts and badly harms false-alarm runs.
- `Corrective prompt feedback should become more useful as policy models get stronger`: contradicted by the Qwen3.5 vs Qwen3.6 SWE-PRM reversal in this experiment.
- `More look-ahead always improves rollback localization`: contradicted by GA-Rollback's inverted-U Wait-Info curve.

## Nonempty frontier
1. **Historical rewind-target policy ablation**: directly compare agent-selected vs fixed-depth vs latest-known-good vs dependency/root-cause vs semantic-admissible vs random under identical tasks/budgets.
2. **Generalize the online state-quality gate beyond SWE**: test FailFast-like calibrated FPR control in embodied, web, analytical-state, and scientific-agent environments where failure signatures differ.
3. **Semantic + OS checkpoint control**: combine observable semantic/cognitive corruption signals with Crab-style recovery-relevant OS effect classification; quantify cases where cognition is corrupted but sandbox state did not change.
4. **Boundary discovery**: learn or infer safe atomic/semantic/effect cut boundaries automatically; compare immediate alarm cut, fixed patience, effect-settled, and learned boundary policies.
5. **Artifact carryover policy**: compare none / raw diff or state delta / compact lesson / selective dependency-local artifacts / full prior prompt under matched false alarms and true failures.
6. **Subgoal/folding negative evidence**: find controlled cases where wrong decomposition or stale folded summaries cause terminal degradation.
7. **Compensable-effect utility**: measure residual real-world cost after compensation, not merely binary rollback correctness.

## Exact continuation
Next run first action: search primary sources for a **direct historical rewind-target selector ablation** under matched trajectories and budgets, using terms `rollback target selection`, `checkpoint selection`, `rewind point`, `root cause rollback`, `latest good checkpoint`, `learned rollback policy`, `agent-selected rewind`, and `semantic boundary`. In parallel, search for non-SWE online failure/corruption gates with explicit false-positive/disruption accounting. If no direct target-selector study exists, preserve the gap and branch into automatic semantic/effect boundary discovery and artifact-carryover ablations rather than treating GA-Rollback's Wait-Info curve as target-selection proof.
