# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2100.md`.
Base candidate ledger: `STATE.md` (candidates 001–004); later candidate/refinement detail is in the run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor, not a simple threshold story

ReasoningBank and Memento public paths both retrieve without an absolute admission threshold, so threshold presence does not explain their divergent EvoAgentBench cells.

ReasoningBank's released SWE path uses top-1 prior-task retrieval, up to three generalized success/failure lessons, system-message injection, and explicit model discretion about relevance. Memento's public parametric CBR path uses up to eight concrete `Question + Plan` examples, a stronger planner-directed user message, LLM-judged positive/negative case labels, and a persistent query-stream planner history.

New implementation detail from Memento: retriever training broadcasts the current query's final `is_correct` outcome to **every retrieved case** as `truth_label`; the pair classifier trains on that label. This is coarse query-level credit, not marginal per-memory utility. The same public script keeps one `shared_history` across queries. These are concrete confounds / candidate negative-transfer mechanisms, not proven causes of EvoAgentBench's 45.8→9.5 collapse.

### `clean-os-g1-005` — reviewer/verifier-gated durable self-evolution, mechanically grounded

ArgusAgent's runtime connects Reviewer decisions to durable state rather than merely prompting about review:

- `done`, `blocked`, and `replan_requested` alter backlog/journal state;
- no-progress replans reset to pending only up to a durable bounded-convergence threshold, then become terminal no-progress;
- premature dynamic-plan stage advances can be rolled back while sibling/dependent nodes remain unfinished;
- independently reviewed handoff evidence is sealed only when `review_source == reviewer`;
- learned vertical candidates are promoted only on success + final review `done` + actual Reviewer source;
- stage certificates fingerprint the checklist/evidence and certify only Manager `advance` / `complete` actions.

Scope correction: independent review is conditional on explicit policy / environment / vertical contract, not universal. Stage-certificate persistence is caught fail-soft in the surrounding supervisor, so certificate enforcement still needs downstream-consumer tracing.

Operational artifact for 731 SWE-Bench Pro tasks: external Reviewer used on 466, self-review on 265. Of the external-review paths, 43 requested revision and 34 were eventually officially resolved; 22 ended Reviewer-accepted after revision and 21 did not. Routing is task-dependent, not randomized, so this is descriptive operational evidence rather than a causal reviewer ablation.

### `clean-os-g1-006` — separate within-task failure repair from cross-task durable memory admission

Independent public reproduction `ramankrishna/reasoning-bank` ran Claude Haiku 4.5 on a 30-instance SWE-bench Lite subset, 3 seeds, using the official SWE evaluator. Reported clean-cell results:

- one attempt / no retry: 45/90 = 50.0%;
- naive retry: 38/90 = 42.2% (−7.8 pp);
- fresh per-instance ReasoningBank: 45/86 = 52.3% (+10.1 pp vs naive retry, +2.3 pp vs one-shot);
- persistent cross-instance bank: 21/45 = 46.7% (−3.3 pp vs one-shot, −5.6 pp vs fresh).

The persistent bank also showed no positive early→late transfer signal; the difficulty-matched deficit versus the one-shot control widened later in the stream. Major limits: only 45/90 persistent-bank cells remained clean due infrastructure/API-credit failures, the 30-task pool is highly bimodal, CIs overlap, and referenced raw per-cell outputs were not committed. Treat as scoped negative/matched evidence, not a refutation of the original ReasoningBank paper or its reported +4.6 pp SWE-Bench Verified result with Gemini-2.5-Flash.

Transfer rule: retry repair and durable cross-task learning must be evaluated separately. A memory system that repairs harmful retries has not thereby demonstrated positive cross-task transfer; persistent memory should require its own held-out transfer evidence and no-memory fallback.

### Official ReasoningBank reproducibility gap

The public `google-research/reasoning-bank` repository exposes SWE-Bench runner/evaluation code but this pass found no checked-in per-instance prediction/result bundle that can be joined to the released runner's online LLM `success` / `fail` induction labels. The repository tree has no ordinary checked-in `predictions` or `results` paths. Therefore public label-agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence the labels are wrong.

## Primary source pointers from the latest run

- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/core/models.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/engineer/round_settlement.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/life/supervisor/_mission_execution_settlement.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/core/stage_certificate.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/apps/_runtime_helpers.py
- https://github.com/microsoft/ArgusAgent/blob/main/technical_report/evidence/swebench_pro/reviewer_mechanism_stats.json
- https://github.com/google-research/reasoning-bank
- https://github.com/ramankrishna/reasoning-bank/blob/main/experiments/swebench/RESULTS.md
- https://github.com/Memento-Teams/Memento/blob/main/client/parametric_memory_cbr.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py

## Nonempty frontier

1. Quantify Memento's checked-in `memory/training_data.jsonl`: class balance, retrieved-case count per query, and how often retrieved positive/negative cases receive the same current-query `truth_label`. Characterize outcome-credit ambiguity directly.
2. Trace Memento retriever training/checkpoint validation and search for matched no-memory / nonparametric / parametric ablations. Determine whether retriever validation predicts downstream benefit or only query-outcome correlation.
3. Trace Argus tests and downstream consumers of `stage-certificates.json` to distinguish mechanically mandatory stage admission from fail-soft observability; specifically determine whether stage advancement can survive certificate persistence failure.
4. Search for additional independent matched persistent-vs-fresh/no-memory memory ablations with task-native evaluation, sufficient n, and generalized-vs-concrete memory contrasts.
5. Continue ReasoningBank release/supplement/OpenReview artifact search for raw SWE predictions and induction labels joinable to official resolved outcomes.
6. Continue EvoAgentBench release/issue/supplement search for exact Memento/ReasoningBank adapters/configs/per-run artifacts needed to explain the 45.8→9.5 / 45.8→53.0 divergence.

## Exact continuation

Obtain a representative or complete sample of Memento's checked-in `memory/training_data.jsonl` through public-source tooling and quantify how each query's final `truth_label` is copied across retrieved cases, including cases whose existing `case_label` signs differ. Then inspect retriever validation/checkpoint metrics and any matched no-memory/nonparametric ablation. If the large artifact cannot be streamed, immediately switch to Argus stage-certificate enforcement tests/consumers, record the access limitation, and continue rather than stopping.
