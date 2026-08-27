# Self-improvement clean checkpoint 56 — Meta^n portfolio selection and merge-oracle boundary

Prepared at: 2026-08-27T10:06:24+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

This physical invocation froze semantic control before substantive reads at:

- note main SHA: `2e87b96b20d51d9b8e7df0981c477d55075087ba`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic predecessor: sequence 55

Later note-main advances are operationally ignored for semantic interpretation in this invocation. This checkpoint only writes role-local clean state.

## Source-qualified update: SIG-METAN-PORTFOLIO-SELECTION-GENERALIZATION

Primary paper: Meta^n: Recursive Self-Improvement through Emergent Depth, arXiv:2608.24735 v1, submitted 2026-08-25 15:44:25 UTC.
Public code: `minnesotanlp/meta-n`, current public `main` inspected during this invocation.

The paper and public implementation make a sharper distinction than a generic "recursive self-improvement score" suggests: evolutionary search maintains a monotonically growing archive, while the reported archive/oracle score is a **per-task max across different candidate chains**, not necessarily the score of one chain.

Public `Archive` tracks `_best_per_task` independently by task and retains the winning candidate id/trace for each task. The evolutionary result separately records `best_mean_score` / `best_candidate_id` and `oracle_mean_score` / `per_task_best_scores`. This means selection-set monotonicity of the archive oracle is structurally different from monotonic improvement of a single deployable lineage.

### Direct held-out warning from the reported results

The paper's held-out Symptom2Disease results show the archive portfolio slightly **below** the best single chain on both reported backbones:

- Gemma: archive-best held-out `0.733` vs best single chain `0.743`;
- GPT-5.2: archive-best held-out `0.725` vs best single chain `0.734`.

The paper also reports GPT-5.2 Symptom2Disease archive/dev around `0.887` before the held-out result of `0.725`. Therefore per-task archive selection that is monotone on the adaptive selection split is not monotone on held-out generalization, at least for this tested prompt-rewrite setting.

Scope: this is not evidence that archive search is broadly harmful. CO-Bench and LawBench show positive archive-vs-chain held-out gaps. It is direct evidence that **archive-best must not be treated as a theorem-like monotonic self-improvement metric once evaluation moves off the adaptive selection split**.

### Adaptive candidate/query pressure is now more concrete

The paper's reported evolutionary settings and production candidate counts permit partial reconstruction of the adaptive search budget rather than treating it as an unspecified loop:

- CO-Bench uses beam width 2 × 2 children and max 8 Gemma iterations; the single-shot run reports 33 candidates, exactly seed + `8×4` candidates. Agentic reports 29 candidates.
- Symptom2Disease uses 1 × 3 children, max 20 iterations, patience off; both reported variants have 61 candidates, exactly seed + `20×3`.
- LawBench uses the same 1 × 3 / 20-iteration setting and reports 61 candidates for both variants.
- AlphaEvolve Math and AlgoTune use 2 × 2 / 6 iterations, whose full budget is 25 including seed; reported single-shot counts are 25, while agentic counts are 24.

This matters because the same adaptive dev/selection data participate in dozens of candidate comparisons. The presence of a distinct final test split prevents direct test leakage on the standard path, but does not make the selection score an unbiased estimate of the selected archive portfolio's generalization.

## Source-qualified update: SIG-METAN-CONSOLIDATION-MERGE-ROUTER

The current public implementation makes the consolidation result more precise than the phrase "zero regression" alone.

`consolidate=True` evaluates exactly one focus task freshly and **inherits every other task's existing per-task-best trace without re-solving it**. The code explicitly exempts these inherited traces from re-evaluation and describes the mode as monotonic/collateral-free because non-focus scores are frozen.

Afterward `_build_merged_candidate()` constructs `merge_oracle` with **no LLM call and no re-evaluation**. It creates a `task_solution_map` from each task id to that task's already-selected best script, copies the stored per-task traces, sets the merged candidate mean equal to `oracle_mean_score` by construction, and routes each known task id to its stored winner.

Therefore:

1. The consolidation "no regression" property applies first to an **accounting/portfolio trajectory** where non-focus outcomes are inherited rather than jointly re-measured under one changed solver.
2. The synthesized deployable object is a **task-id router over frozen specialist scripts**, not evidence that one general solver chain acquired all improvements without interference.
3. For the same known benchmark task identities, this router is genuinely executable; it is not merely a table statistic. But its oracle value depends on knowing which task id to route to and on having selected each specialist using the adaptive search panel.
4. The implementation's held-out archive test re-evaluates each task's selected specialist script on held-out data, while the separate chain test evaluates one archive-best chain across all tasks. Those are substantively different deployment objects and must be reported separately.

Scope: this does **not** negate the paper's compute-matched consolidation improvement. It narrows the claim. A per-task routed specialist bank can be useful, but "recursive self-improvement of one agent" and "portfolio assembly with known-task routing" are distinct mechanisms.

## Consequence for self-improvement evaluation

For archive-based or skill-bank systems, record at least four distinct objects:

- `latest_single_lineage`: the actual latest descendant;
- `best_single_lineage`: one fixed artifact selected on adaptive data;
- `routed_portfolio`: task-conditioned selection among multiple artifacts;
- `outer_test_policy`: the actual router/artifact policy frozen before untouched evaluation.

Selection-split monotonicity, per-task oracle monotonicity, and held-out policy improvement are separate claims. A monotone per-task archive should not be scored as one lineage's recursive gain unless the tested deployment really contains and evaluates the same routing policy.

## Reproducibility boundary remains

The public repository is highly instrumented for future replay (candidate ids/parents, traces, injected code, config/checkpoints and LLM I/O), but the visible Git history begins after paper submission and the reported paper-run `experiments/*` bundles are not in the public tree. Thus the exact stochastic proposal chronology and exact pre-public executable/config remain unavailable for a fixed-proposal matched replay.

## Frontier remains nonempty

Exact next action:

1. Recover any public Meta^n paper-run bundle, pre-public source archive, release asset, author artifact, or exact config that binds the reported candidate chronology to an executable revision; otherwise preserve the replay gap.
2. Re-tabulate all Meta^n headline results as `best_single_lineage` vs `routed_portfolio`, and by evidence class `held_out` / `proxy` / `dev_equals_test` / `none` / run-specific `heldout_consumed_by_search`.
3. Quantify selection-query exposure per benchmark/seed from the exact B×K×iteration settings and early-stop behavior, separating proposed candidates from materialized/evaluated candidates.
4. Inspect whether consolidation's reported compute-matched comparison evaluates the same routed deployment policy on a fresh panel or only the monotone inherited per-task accounting surface; identify any final re-execution of the full merged router on disjoint data.
5. Inspect optional verifier, rollback, regression-guard and checkpoint-selection paths for any additional nominal outer-test consumption.
6. Continue Recuris pre-public scorer/per-trial provenance recovery and StarHarness code/run-ledger monitoring from public sources only.
7. Continue searching for a >10-proposal live LLM self-improvement system combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.

## Primary source pointers

- Paper: https://arxiv.org/abs/2608.24735
- Public repo: https://github.com/minnesotanlp/meta-n
- Public `Archive`: `meta_n/core/archive.py`
- Public evolutionary implementation: `meta_n/core/evolutionary_orchestrator.py`
- Current inspected orchestrator blob: `7ff64cc6d62c58a1bcfe442431da3f253305631e`
