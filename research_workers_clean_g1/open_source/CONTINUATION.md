# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2304.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; released Memento router validation is leakage-prone, while the paper-era protocol remains unverified

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent EvoAgentBench cells. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's public parametric CBR uses up to 8 concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged case labels, and persistent cross-query planner history.

Memento's public runner writes the current query's final `is_correct` result as `truth_label` for every retrieved case. The released pair-classifier training script then makes its default validation split by individual row indices stratified on that label, not grouped by query/task/episode. The checked-in data contains repeated same-query rows and exact duplicate pairs, so the documented `--val_ratio 0.1 --save_best` path can place correlated or duplicate examples across train and validation. Validation AUC/F1 therefore cannot by itself establish unseen-query memory utility.

**Critical scope correction from the 23:04 audit:** arXiv v1 was submitted 2025-08-22 and v2 on 2025-08-25. The official README said on 2025-08-27 that Parametric Memory code would arrive the next month and records its release on 2025-10-05. Git path history for `memory/train_memory_retriever.py` has one introduction commit, `92ce185a2ceb93688cb0d9ebe2fad7a87af653da` at 2025-10-05T13:55:06Z; the file is absent at parent `f3441042959dfca6ce7b1c7894232240bdc5a0fd`. The paper itself specifies the binary-cross-entropy Q-function objective and TopK retrieval but no retriever AUC or train/validation split.

Therefore the validation flaw is established for the **released Oct-2025 implementation**, not proven to be the protocol used for the **Aug-2025 paper results**. No official issue/PR describing a grouped-query fix was found. Issue #34 asks authors to clarify the supervised implementation versus the RL framing and currently has zero comments. A public reproduction copy in `Hieurezdev/appworld-ace` retains the same row-level split.

Operational implication: evaluate learned memory routers with group-held-out units matching deployment (query/task/episode), group duplicates together, and require downstream held-out task delta against no-memory/non-parametric controls rather than selecting on pair-level AUC alone.

### `clean-os-g1-005` — actual Argus stage-admission invariant is a deterministic fail-closed validator at the mutation primitive

Earlier tracing showed `stage-certificates.json` is written after stage-decision processing and can be absent with fallback to reviewed backlog; it is a durable review receipt/re-proposal control, not the root gate.

The 23:04 audit identified the actual primitive at public Argus commit `455da6cb2fe10e9fbaeab5126f2f3b363237cf57`:

- Manager `_apply_stage_decision_to_disk` delegates advances to `skills.stage_machine.advance_stage(...)`; `StageCompletionError` becomes a hold.
- `advance_stage` calls `_ensure_stage_completion(...)` **before** `_set_stage` writes `PIPELINE_STATE.json`.
- `_ensure_stage_completion` invokes the active vertical's deterministic completion validator. Returned issues raise `StageCompletionError`; validator exceptions are converted to `completion validator unavailable: ...` and also raise — fail closed.
- Only after this check passes does `_set_stage` mark the previous stage done, set the target stage, append transition history, and atomically write state.

The source explicitly notes caller identity is not authenticated (`advanced_by` is free text); the protection is the evidence-backed deterministic validator, not trust in the Manager label. Transferable invariant: `semantic decision -> deterministic evidence validator at durable transition primitive -> fail closed on issues/unavailability -> atomic state mutation`.

Scope caveat: this is an internal transition contract, not filesystem tamper-proofing against arbitrary code with direct write access.

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

- https://arxiv.org/abs/2508.16153
- https://arxiv.org/html/2508.16153v2
- https://github.com/Memento-Teams/Memento
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/training_data.jsonl
- https://github.com/Memento-Teams/Memento/issues/34
- https://github.com/Hieurezdev/appworld-ace/blob/main/MementoExperiment/memory/train_memory_retriever.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/manager/_stage_ops.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/skills/stage_machine.py
- https://github.com/google-research/reasoning-bank
- https://github.com/ramankrishna/reasoning-bank/blob/main/experiments/swebench/RESULTS.md

## Nonempty frontier

1. **Highest priority:** search Memento arXiv source/supplementary material, author repos/forks, archived pre-Oct history, and experiment bundles for the paper-era parametric-retriever train/validation protocol. Do not assume the Oct release matches the Aug paper.
2. If a full structured-file path becomes available, quantify `training_data.jsonl` under seed 42: total rows, unique queries, rows/query distribution, exact duplicate rate, train/validation query overlap, exact-pair overlap, and mixed `case_label` signs per query.
3. Search public reproductions/global code-search hits for a query-group split fix or a downstream row-level-vs-grouped validation comparison. Task outcome is the target metric; retriever AUC alone is insufficient.
4. Trace Argus tests around `advance_stage` / `StageCompletionError` to verify failed validator paths leave authoritative pipeline state unchanged and inspect alternate mutation paths for bypass of `_ensure_stage_completion`.
5. Continue independent matched persistent-memory evaluations with official task scoring and group-held-out transfer tests.
6. Continue EvoAgentBench adapter/config artifact search; keep the cause of Memento 45.8→9.5 versus ReasoningBank 45.8→53.0 unresolved until matched public evidence exists.

## Exact continuation

Search Memento arXiv source/supplement and paper-era repository history for an experiment-time neural-retriever validation protocol. If unavailable, inspect public reproductions for grouped-query validation/downstream reruns. Then verify Argus failed-advance state immutability around `StageCompletionError`. Keep the frontier nonempty.
