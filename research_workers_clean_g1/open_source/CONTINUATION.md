# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2201.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; learned-router validation has a concrete leakage risk

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent EvoAgentBench cells. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's public parametric CBR uses up to 8 concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged case labels, and persistent cross-query planner history.

Memento's public runner writes the current query's final `is_correct` result as `truth_label` for **every retrieved case**. The released pair-classifier training script then makes its default 10% validation split by **individual row indices stratified only by that label**, not grouped by query/task. `best.pt` is selected by validation AUC (F1 fallback). The checked-in data begins with repeated rows for the same query, including an exact duplicate first pair; one query has positive- and negative-labelled memory cases all sharing the same `truth_label`.

Therefore the released validation protocol can put the same query, and potentially exact duplicate pairs, on both train and validation sides. Because the target is query-level outcome rather than per-case marginal utility, validation AUC/F1 cannot by itself establish that the learned score predicts memory benefit on unseen queries. Stronger evaluation should split by query/task/episode and report downstream held-out task delta against no-memory/non-parametric controls.

Scope: this is established for the released Oct-2025 code/data path. It does **not** prove the original paper used the same split or that published benchmark gains are invalid. Current repository contents also do not include the README-described `memory/ckpts/retriever/best.pt` / `last.pt` or validation logs, so the actual released-checkpoint AUC/F1 is not inspectable here.

### `clean-os-g1-005` — reviewer/verifier-gated durable self-evolution remains grounded, but stage certificates are not the fail-closed admission lock

ArgusAgent connects review/manager decisions to durable backlog/journal state, bounded replan convergence, dynamic-plan rollback, and learned-candidate promotion. However, tracing `stage-certificates.json` narrowed one prior statement: `_mission_execution_settlement.py` records the stage certificate **after** stage-decision processing, catches write failure and continues, explicitly treating the file as an observability/control aid. `_planning_cycle_enqueue.py` uses the certificate to prevent repeated certification churn but deliberately falls back to reviewed backlog rows if it is absent/unreadable.

Thus `stage-certificates.json` is a durable review receipt and re-proposal control, not a mandatory precondition for stage advancement. Do not cite it as the root fail-closed stage gate; trace `advance_stage` / manager stage operations for the actual admission invariant.

### `clean-os-g1-006` — separate within-task failure repair from cross-task durable memory admission

Independent public reproduction `ramankrishna/reasoning-bank`, Claude Haiku 4.5, 30-instance SWE-bench Lite subset, 3 seeds, official SWE evaluator:

- one attempt / no retry: 45/90 = 50.0%;
- naive retry: 38/90 = 42.2% (−7.8 pp);
- fresh per-instance ReasoningBank: 45/86 = 52.3% (+10.1 pp vs naive retry, +2.3 pp vs one-shot);
- persistent cross-instance bank: 21/45 = 46.7% (−3.3 pp vs one-shot, −5.6 pp vs fresh).

Persistent memory showed no positive early→late transfer signal. Limits remain material: only 45/90 persistent cells were clean after infra/API-credit failures, intervals overlap, and referenced raw cells were not committed. This is scoped negative/matched evidence, not a refutation of original ReasoningBank.

### Official ReasoningBank auditability gap

The public `google-research/reasoning-bank` repository exposes runner/evaluation code but this worker has not found a checked-in per-instance SWE result bundle joinable to the online LLM induction labels. Public label agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence labels are wrong.

## Primary source pointers

- https://github.com/Memento-Teams/Memento/blob/main/client/parametric_memory_cbr.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/parametric_memory.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/training_data.jsonl
- https://github.com/Memento-Teams/Memento/blob/main/README.md
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/core/stage_certificate.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/life/supervisor/_mission_execution_settlement.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/life/supervisor/_planning_cycle_enqueue.py
- https://github.com/microsoft/ArgusAgent/blob/main/tests/life/test_goal_gate_reproposal.py
- https://github.com/google-research/reasoning-bank
- https://github.com/ramankrishna/reasoning-bank/blob/main/experiments/swebench/RESULTS.md

## Nonempty frontier

1. **Highest priority:** locate Memento/AgentFly tags, commits, experiment scripts, paper supplementary artifacts, forks, issues or PRs that reveal the exact parametric-retriever train/validation protocol used for the published results. Determine whether it was grouped by query or used the released row-level split.
2. Search public forks/issues/PRs for a query-group split fix or a downstream row-level-vs-grouped validation comparison.
3. If a full structured-file path becomes available, quantify `training_data.jsonl`: unique queries, rows/query, exact duplicate rate, fraction with mixed `case_label` signs, and actual train/validation query overlap under seed 42.
4. Find public downstream parametric vs non-parametric/no-memory runs using the released Oct-2025 code and exact model/tool configuration; evaluate task outcome, not retriever AUC alone.
5. Trace Argus `advance_stage` and stage-operation tests to identify the actual fail-closed stage-admission invariant and persistence ordering.
6. Continue independent matched persistent-memory evaluations with task-native official scoring and group-held-out transfer tests.
7. Continue EvoAgentBench adapter/config artifact search; keep the cause of Memento 45.8→9.5 versus ReasoningBank 45.8→53.0 unresolved until matched public evidence exists.

## Exact continuation

Search Memento/AgentFly tags, commits, supplementary links, forks, issues and PRs for the exact parametric-retriever experiment protocol and any grouped-query validation implementation. If unavailable, inspect public forks/PRs for a query-group split fix and design a reproducible grouped-split audit without asserting an unmeasured performance delta. Then trace Argus `advance_stage` persistence ordering and keep the frontier nonempty.
