# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2100.md`.
Latest frontier evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent EvoAgentBench cells. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's public parametric CBR uses up to 8 concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged case labels, and persistent cross-query planner history.

Memento source code writes the current query's final `is_correct` outcome as `truth_label` for **every retrieved case**, and its pair classifier trains directly on that label. A post-checkpoint public raw-data audit confirmed this pattern in representative slices from the beginning, middle, and near end of checked-in `memory/training_data.jsonl`: within one query, both positive- and negative-labeled retrieved memories receive the same final `truth_label` (both for successful and failed current queries). This establishes coarse query-level credit assignment in the artifact itself, but does not prove downstream causal harm or a corpus-wide frequency. See `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.

### `clean-os-g1-005` — reviewer/verifier-gated durable self-evolution, mechanically grounded

ArgusAgent connects Reviewer decisions to durable backlog/journal state, bounded replan convergence, rollback of premature dynamic-plan stage advances, independent-review handoff sealing, and learned-candidate promotion. Learned vertical promotion requires success + final `done` + actual Reviewer source. Stage certificates fingerprint checklist/evidence and certify only Manager `advance`/`complete` actions.

Scope correction: independent review is conditional on policy/environment/vertical contract, not universal. Stage-certificate writes are caught fail-soft, so downstream enforcement still needs tracing.

Operational artifact for 731 SWE-Bench Pro tasks: 466 external-review, 265 self-review; 43 external-review trajectories requested revision and 34 were eventually officially resolved, with 22 eventually Reviewer-accepted and 21 not. Routing is task-dependent, so these figures are descriptive rather than a causal reviewer ablation.

### `clean-os-g1-006` — separate within-task failure repair from cross-task durable memory admission

Independent public reproduction `ramankrishna/reasoning-bank`, Claude Haiku 4.5, 30-instance SWE-bench Lite subset, 3 seeds, official SWE evaluator:

- one attempt / no retry: 45/90 = 50.0%;
- naive retry: 38/90 = 42.2% (−7.8 pp);
- fresh per-instance ReasoningBank: 45/86 = 52.3% (+10.1 pp vs naive retry, +2.3 pp vs one-shot);
- persistent cross-instance bank: 21/45 = 46.7% (−3.3 pp vs one-shot, −5.6 pp vs fresh).

Persistent memory showed no positive early→late transfer signal. Limits are material: only 45/90 persistent cells remained clean after infra/API-credit failures, task pool was bimodal, intervals overlap, and referenced raw cells were not committed. This is scoped negative/matched evidence, not a refutation of original ReasoningBank or its reported +4.6 pp SWE-Bench Verified result with Gemini-2.5-Flash.

Transfer rule: within-task retry repair and durable cross-task learning require separate controls. Cross-task memory should not inherit credit from retry recovery; require held-out transfer evidence and a no-memory fallback.

### Official ReasoningBank auditability gap

The public `google-research/reasoning-bank` repository exposes runner/evaluation code but this pass found no checked-in per-instance SWE prediction/result bundle joinable to the released runner's online LLM induction labels. Public label agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence that labels are wrong.

## Primary source pointers

- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/engineer/round_settlement.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/life/supervisor/_mission_execution_settlement.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/core/stage_certificate.py
- https://github.com/microsoft/ArgusAgent/blob/main/technical_report/evidence/swebench_pro/reviewer_mechanism_stats.json
- https://github.com/google-research/reasoning-bank
- https://github.com/ramankrishna/reasoning-bank/blob/main/experiments/swebench/RESULTS.md
- https://github.com/Memento-Teams/Memento/blob/main/client/parametric_memory_cbr.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py
- https://raw.githubusercontent.com/Memento-Teams/Memento/main/memory/training_data.jsonl

## Nonempty frontier

1. Trace Memento retriever training/checkpoint validation artifacts and repository history for validation AUC/F1 plus any matched no-memory/nonparametric/parametric downstream ablation. Determine whether retriever validation predicts downstream benefit or merely correlates with final-query outcome.
2. If feasible, obtain a whole-file structured pass over Memento `training_data.jsonl` to quantify class balance, mixed `case_label` signs per query, and global query-level label-broadcast frequency. Representative slices already confirm the mechanism; do not invent a corpus-wide rate without full parsing.
3. Trace Argus tests/downstream consumers of `stage-certificates.json` to distinguish mechanically mandatory stage admission from fail-soft observability; determine whether stage advancement can survive certificate persistence failure.
4. Search additional independent matched persistent-vs-fresh/no-memory memory ablations with task-native evaluation, sufficient n, and generalized-vs-concrete memory contrasts.
5. Continue ReasoningBank release/supplement/OpenReview search for raw SWE predictions and induction labels joinable to official outcomes.
6. Continue EvoAgentBench release/issue/supplement search for exact Memento/ReasoningBank adapters/configs/per-run artifacts needed to explain the 45.8→9.5 / 45.8→53.0 divergence.

## Exact continuation

Inspect Memento retriever training/checkpoint artifacts and repository history for reported validation AUC/F1, checkpoint-selection semantics, and any downstream ablation against no-memory or nonparametric retrieval. Test whether the learned pair score is calibrated to held-out task benefit rather than only query-level success correlation. If that branch has no public downstream evidence, switch immediately to Argus stage-certificate consumers/tests and trace whether certificate write failure can be bypassed during stage advancement. Persist the result and keep the frontier nonempty.
