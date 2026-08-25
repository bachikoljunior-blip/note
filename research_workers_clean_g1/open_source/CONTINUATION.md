# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2358.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; released Memento router validation is leakage-prone, and iteration-curve claims need a matched no-memory control

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent behavior. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's public parametric CBR uses up to 8 concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged case labels, and persistent cross-query planner history.

Memento's public runner writes the current query's final `is_correct` result as `truth_label` for every retrieved case. The released pair-classifier training script then makes its default validation split by individual rows, not grouped by query/task/episode. The checked-in data contains repeated same-query rows and exact duplicate pairs, so the documented Oct-2025 `--val_ratio 0.1 --save_best` path can place correlated/duplicate examples across train and validation. Pair-level validation AUC/F1 therefore cannot by itself establish unseen-query memory utility.

**Paper-era provenance is now sharply bounded.** The paper mechanism is paper-era: arXiv v1/v2 describe a parametric Q-function, binary cross-entropy training, and Top-K retrieval. But the official public repository at 2025-08-25 commit `8ec09ef4b1ee0cab640b20f903d5bae3deab0b19` contains no `memory/` directory, no retriever training script, no training data/checkpoint, and no experiment-time retriever validation configuration. The official README later says Parametric Memory code would arrive the next month and records its 2025-10-05 release. Therefore the row-level validation defect is established for the **released Oct-2025 implementation**, not proven to be the protocol used for the **Aug-2025 paper results**. The paper itself does not report a retriever train/validation split or held-out retriever AUC.

**New evaluation-scope correction from paper Table 4 (DeepResearcher):**

- AgentFly without CBR: 78.65 → 84.47 (**+5.82 pp** across Iter1→5)
- non-parametric CBR: 79.84 → 84.85 (**+5.01 pp**)
- parametric CBR: 80.46 → 85.44 (**+4.98 pp**)

Parametric-minus-no-CBR gaps by iteration are +1.81, +1.91, +1.48, +1.32, +0.97 pp. Thus the **raw upward iteration slope is not memory-specific**: the no-CBR control rises slightly more. The supported memory signal is the positive between-arm gap at each reported iteration, not the shared upward trend. The reason the no-CBR arm improves across iterations remains unresolved and must be identified before interpreting the curves causally.

GAIA also needs scope separation. The paper says validation starts with empty memory and stores successful/failed trajectories over three iterations; that validation score is therefore an adaptation-stream measurement. The GAIA test score uses the case bank accumulated during validation and is stronger held-out transfer evidence. OOD gains of 4.7–9.6 pp support the CBR family, but the paper text does not establish that the OOD figure specifically validates the later released neural-retriever checkpoint-selection protocol.

Operational implication: adaptive memory evaluations should separately report (1) within-stream adaptation, (2) frozen-memory held-out transfer, and (3) memory-specific delta versus a matched no-memory/no-write control under the same iteration/order/resampling regime. Learned routers should use group-held-out units matching deployment, group duplicates, and prefer downstream held-out task utility over pair-level AUC for checkpoint selection.

### `clean-os-g1-005` — Argus shows why evidence validity and transition authority must be separate gates

At public Argus commit `455da6cb2fe10e9fbaeab5126f2f3b363237cf57`, ordinary forward advancement is materially well-guarded:

- Manager delegates advance to `skills.stage_machine.advance_stage(...)`.
- `advance_stage` calls `_ensure_stage_completion(...)` before `_set_stage` mutates `PIPELINE_STATE.json`.
- validator issues raise `StageCompletionError`; validator exceptions become `completion validator unavailable: ...` and also fail closed.
- only after the check passes does `_set_stage` mark status/history/current stage and atomically write state.

However the current source and regression test document a real prior failure, testbed run 13 (`s-d9ea298f`). An Engineer at math stage `scope` imported `complete_final_stage(...)` directly; the primitive validated only `scope`, stamped a genuine contract fingerprint, and marked later `solve`/`review` stages skipped. The resulting state passed structural completion audit because it was minted by the legitimate primitive. This demonstrates that **valid evidence for the current stage is not the same thing as authority to perform a terminal transition**.

The repair now refuses completion off the final stage unless `allow_early_completion=True`, and read-side validation rejects old staged early-completion records even when their fingerprint is genuine. A dedicated regression proves refusal happens before any write and leaves `PIPELINE_STATE.json` byte-for-byte unchanged. The normal Manager path derives the flag from `workflow_mode=direct`.

But the source/test explicitly describes this as **"a lock, not a signature"**: `completed_by` is free text, the fingerprint is recomputable, and an in-process caller determined to pass `allow_early_completion=True` still can. Therefore the stronger transferable invariant is:

`semantic proposal -> authoritative workflow-state read -> transition-specific authorization/capability -> deterministic evidence validation -> fail closed before write -> atomic durable mutation -> read-side authority revalidation`

Avoid treating a caller-supplied boolean or free-text `by=` as authority. Prefer a private mediator or opaque capability whose standing is derived internally from authoritative state. This is an architectural residual-risk finding, not evidence that the current normal Manager path routinely mis-completes projects.

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
- https://github.com/Memento-Teams/Memento
- https://github.com/Memento-Teams/Memento/commit/8ec09ef4b1ee0cab640b20f903d5bae3deab0b19
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/training_data.jsonl
- https://github.com/Memento-Teams/Memento/issues/34
- https://github.com/Hieurezdev/appworld-ace/blob/main/MementoExperiment/memory/train_memory_retriever.py
- https://github.com/microsoft/ArgusAgent/tree/455da6cb2fe10e9fbaeab5126f2f3b363237cf57
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/manager/_stage_ops.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/skills/stage_machine.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/tests/skills/test_stage_completion_authority.py
- https://github.com/google-research/reasoning-bank
- https://github.com/ramankrishna/reasoning-bank/blob/main/experiments/swebench/RESULTS.md

## Nonempty frontier

1. **Highest priority — Memento control slope:** identify what changes between the five DeepResearcher iterations when CBR is disabled (resampling/order/pass@k/model stochasticity/other changing factor). Until then, do not interpret the common iteration rise as causal continual learning.
2. **Memento paper-era retriever provenance:** search arXiv source/supplement, author mirrors, archived experiment bundles, or author-side artifacts for the actual Aug-2025 parametric-retriever training/checkpoint protocol. Official public repository history is now exhausted for this question because the implementation was absent.
3. **Memento matched evaluation:** find or reproduce a row-level-vs-query-group split comparison; quantify total rows, unique queries, duplicate rate, query/pair overlap under seed 42, and whether retriever validation AUC predicts frozen held-out task utility.
4. **Argus authority surface:** trace `allow_early_completion`, `reset_stage_for_replacement_intent`, `persist_vertical(force_replacement=...)`, and actual in-process import/sandbox permissions. Determine which privileged transitions are capability-bound versus caller-asserted.
5. **Argus intermediate immutability:** locate or add evidence of an explicit regression test that failed `_ensure_stage_completion` during ordinary `advance_stage` leaves state byte-for-byte unchanged. Code ordering implies this, but a direct test would strengthen it.
6. Continue independent matched persistent-memory evaluations with official task scoring/group-held-out transfer tests, and keep EvoAgentBench Memento-vs-ReasoningBank causal attribution unresolved without matched public artifacts.

## Exact continuation

Inspect Memento paper/arXiv source or author-side experiment artifacts for how the five DeepResearcher iterations and the no-CBR control were generated, specifically what changes between iterations when CBR is disabled. If no public artifact exists, mark causal attribution unresolved rather than infer. Then trace Argus early-completion/reset authorization from Manager decision to primitive, including whether agent execution sandboxes can directly import/call stage-machine privileged operations after the run-13 repair. Keep the frontier nonempty.
