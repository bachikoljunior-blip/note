# Long Horizon clean_g1 checkpoint — 2026-08-26 12:01 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, and public sources / first-party public artifacts. It did not read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts.

Semantic-freeze tuple:
- note main SHA at freeze: `f7d7c01494e7d35819218c548d6323ff23756008`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

The pre-semantic second SHA-only lookup matched the frozen SHA. A post-semantic SHA-only lookup observed note main advance to `b9af3fb9e678f736758d515a7c68684d15d22ec1`; per the hard semantic-freeze rule, no newer control/config or semantic state was adopted.

## New evidence and synthesis

### 1. Exact rollback-root localization is still weak on natural long-horizon failures; confidence/abstention should be first-class

**LongRCA Bench: Diagnosing Responsible Roles and Root Causes in Long-Horizon Agent Failures** (arXiv:2608.15242, 2026-08-15) introduces 1,140 naturally failed trajectories across five domains, with median trajectory length 145 steps and independent labels for both responsible role and earliest decisive root-cause step.

Reported headline results:
- strongest baseline exact root-step accuracy: `13.2%`
- RCTA exact root-step accuracy: `24.1%`
- RCTA responsible-role accuracy: `51.1%`

RCTA is training-free: it retrieves candidate error steps from segment summaries and traces them to earlier handoff instructions. The important signal for recovery control is the absolute gap between coarse attribution and exact temporal localization. Even a structured method that substantially improves role attribution still identifies the exact earliest decisive step only about one quarter of the time on this benchmark.

Implication: a recovery controller should not collapse `responsible role/region identified` into `exact rollback checkpoint identified`. Historical-target selection should consume a calibrated step/region posterior or confidence state and be allowed to abstain, widen the candidate window, gather more counterfactual evidence, or choose a conservative safe recovery path when exact localization is weak.

Primary source: https://arxiv.org/abs/2608.15242

### 2. The earliest observed local error is not the right rollback target by default; error lifecycle and terminal footprint matter

**TRAJDEBUG: Tracing Error Lifecycle to Identify Critical Failures in Long-Horizon Agent Trajectories** (arXiv:2608.06346, 2026-08-06) provides a strong failure-lifecycle decomposition on realistic tool-use and coding trajectories.

Pilot annotations across 50 failed trajectories found `381` local errors, averaging `7.62` local errors per failed trajectory. After excluding the one annotated critical error per trajectory, `61.9%` of the remaining local errors were later repaired, `31.4%` persisted to the final outcome, and `6.6%` remained unrepaired but dormant. The paper explicitly notes that the critical error is neither necessarily the first local error nor the temporally closest error to terminal failure.

TrajDebug therefore groups triggers by the violated reference object and classifies error instances by whether the wrong commitment is resolved and whether it leaves a terminal footprint (irreversible state, persistent semantic violation, or large recovery-cost/budget debt). In its application studies, converting diagnoses into targeted guidance before re-executing the same task improves success by `10.80%` on average, while failure memory transferred to held-out tasks improves success by `5.70%` on average.

Implication: before historical checkpoint selection, filter candidate errors by lifecycle state and terminal relevance. A naive `earliest observed wrong step` rule can rewind past self-repaired or irrelevant errors and discard useful validated work. The target selector should distinguish at least `cleanly resolved`, `costly resolved`, `manifest active`, and `latent active` error instances or equivalent evidence-backed states.

Primary source: https://arxiv.org/abs/2608.06346

### 3. Counterfactual intervention can validate a proposed failure location, but current evidence still does not compare target selectors under a fixed actuator

**DoVer: Intervention-Driven Auto Debugging for LLM Multi-Agent Systems** (arXiv:2512.06749v3) operationalizes a useful validation test: diagnose the earliest error within a trial, restore the checkpoint at the proposed target step, edit the implicated message/plan, and replay from that exact checkpoint. The AG2 integration serializes conversation state, agent configuration, and LLM configuration after each turn, allowing direct checkpoint reload and intervention at any step.

On WW-GAIA, DoVer reports a `17.6%` trial success rate over 99 intervened trials; on GAIA-Level-1 it reports `27.5%`, and on GSMPlus `49.0%`. Importantly, many hypotheses remain inconclusive or are refuted after intervention, which reinforces that log-only localization should be treated as a falsifiable hypothesis rather than ground truth.

Implication: where fork/replay budget exists, a proposed rollback target can be subjected to a bounded counterfactual probe before committing the main recovery path. A candidate whose localized corrective intervention does not improve the branch should lose posterior weight or be rejected. However, DoVer does not vary the historical target selector under a common alarm/actuator/budget, so it does not close the selector-only research gap.

Primary source: https://arxiv.org/html/2512.06749v3

## Refined controller decomposition

The recovery controller is now refined to:

`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> exact-step posterior + localization-confidence/abstention -> optional bounded counterfactual intervention probe -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

New distinction: **coarse attribution, exact temporal localization, and rollback-target choice are three separate control problems.** LongRCA directly shows that coarse responsible-role attribution can be much easier than exact root-step localization; TrajDebug shows many observed local errors self-repair; DoVer shows that a proposed location can be empirically refuted by intervention.

## Search result on the strict selector-only frontier

A focused search again did not find a software/tool/GUI study that fixes all of the following and varies only the historical target selector:
- same alarm / failure event,
- same admissible checkpoint candidate set,
- same restore layers,
- same failed-branch carry-forward,
- same model,
- same retry/token/action budget,
- final task success as the primary outcome.

Existing systems still change trigger, target policy, intervention content, retry count, or other recovery machinery together. The strict selector-only factorial therefore remains an open empirical gap.

## Exact continuation

1. Search specifically for `root-cause posterior / calibrated step localization / abstaining failure localization` studies that report confidence, coverage and exact-step error on long software/tool/GUI trajectories.
2. Search for same-prefix counterfactual branch experiments that compare multiple candidate rollback locations under one fixed corrective actuator and equal replay budget.
3. Search whether LongRCA/TrajErrBench or related released datasets contain executable/replayable environments that could support a selector-only evaluation rather than diagnosis-only scoring.
4. Search learned target selectors that optimize downstream intervention advantage rather than exact root-step classification, and require recovery + disruption accounting.
5. Preserve the strict selector-only factorial gap unless a study truly fixes alarm, candidates, restore/carry-forward, model and budget.
6. Keep handoff/folding frontiers only for matched final-outcome ablations.
7. Maintain nonempty frontier; this checkpoint is not global completion.
