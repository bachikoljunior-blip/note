# Self-improvement clean checkpoint — strategy reopening and adaptive evaluation boundary

- sequence: 64
- timestamp_jst: 2026-08-27T17:08:09+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1607_JST_aide2_100step_selection_and_autoresearch_warrant_boundary.md`
- frozen note main SHA: `7c0efbf3860e5022910dd39a6bc4403d09372592`
- frozen root control revision: 11
- frozen role config revision: 6
- clean inputs used: own sequence-63 role-local state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream state, legacy/pre-independence state, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound findings

### 1. Task-CoEvolve shows that the evaluation surface itself should adapt — but it is a screening/allocation mechanism, not a promotion certificate

Task-CoEvolve (arXiv:2608.20169v2, 2026-08-24) changes which validation tasks are evaluated as the harness evolves. It samples tasks according to historical outcome variance, concentrating budget where candidate harnesses disagree, then uses sampling-aware estimation to compare candidates evaluated on different subsets.

On online text classification it runs 20 evolution iterations with three candidates per iteration (60 candidates total) and uses separate train/validation/test splits. Full-set search averages 48.6% held-out test accuracy. Task-CoEvolve reaches 49.3% with 20% of the validation evaluations and 47.6% with 7%. At 20%, the ablation progresses from fixed-subset 47.2 → uniform resampling 48.2 → sampling-aware estimation 48.8 → variance-weighted adaptive selection 49.3. The largest single gain is therefore simply not reusing one fixed tiny subset.

But the partial-set estimator is not accurate enough to treat as a behavioral certificate. When all 60 candidates are retrospectively scored on the full validation set, estimated-vs-true Spearman correlation is 0.62 at 20% and 0.13 at 7%. The estimated winner is only the 12th-best of 60 at 20% (51.3% true full-val score vs 54.7% for the true best) and the 10th-best at 7% (46.4% vs 47.8%). This is acceptable as a search-allocation signal, not as evidence that a candidate is actually better than its incumbent.

Terminal-Bench 2.1 is an additional scope boundary: the paper explicitly uses the same 89 tasks for search and final evaluation. Its 61.8/41.6 results at 20% budget are therefore same-surface search results, not untouched outer-test generalization.

The public GitHub repository exists, but as observed in this run it contains only README/figures and still says executable code will be available soon. The exact sampler/estimator/run chronology cannot yet be independently replayed.

### 2. Self-improvement can be statistically careful and still fail because it never reopens the strategy family

`What is Missing from AI Post-Training AI` (arXiv:2608.19072v1, 2026-08-19) separates execution-level changes from strategy-level changes over public post-training trajectories. Across 3,557 recognized adjacent training-experiment pairs it identifies only 74 strategy changes, 2.08% total: 0.98% objective-family changes, 1.07% data-source changes, and 0.03% stage-structure changes.

The paper's experience-driven scaffold persists experimental evidence, adds reusable context and an evaluator, and materially improves execution (+12.6 points on GSM8K and +40.8 on HumanEval in the reported runs), yet the high-level strategy remains largely fixed. Human guidance can bind a different strategy before execution, demonstrating that the agent can understand and implement a departure from its default, but once training begins it falls back into local within-strategy adjustment. On AIME 2025, the richer framework uses about 7.9× the baseline tokens while achieving almost no robust gain; the extra compute is spent refining the already chosen strategy.

The most useful interpretation is not that the model cannot perform strategy changes. Rather, **strategy reopening is not an explicit decision point**. The current loop closes locally (execute → evaluate → repair) while remaining globally linear with respect to the proposal family.

### 3. Acceptance control and strategy-reopening control are orthogonal

The previous frontier emphasized repeated-selection-safe promotion, durable cross-proposal statistical spending, warrant/process gates and untouched outer evaluation. The new evidence adds another independent axis:

`candidate quality control` answers “is this edit better than the incumbent?”

while

`strategy reopening control` answers “should the system stop proposing edits from this family and reopen the higher-level choice?”

A perfect acceptor can still spend a long run safely selecting small improvements inside the wrong family. Conversely, a strategy-reopening trigger without a valid acceptor can jump between noisy alternatives and accumulate false promotions.

The resulting decomposition is:

`adaptive evaluation allocation / cheap screening`
→ `candidate-local evidence and promotion`
→ `cross-candidate error/risk control`
→ `explicit strategy-reopening decision`
→ `immutable/versioned persistence`
→ `untouched outer evaluation`.

### 4. Adaptive task allocation should expose its own provenance

Because the validation sampler itself adapts from prior candidate outcomes, a replayable system should preserve more than candidate scores. At minimum it needs candidate identity, sampled task IDs, inclusion probabilities, outcomes, estimator/version, estimated score, decision, and the exact feedback returned to the proposer. Otherwise a later auditor cannot distinguish a genuine candidate improvement from a favorable adaptive sampling path.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/evaluation_strategy_control_contract_2026-08-27T1706_JST.json`.

## Scope / non-claims

- Do not treat Task-CoEvolve as an anytime-valid acceptance gate; it is evidence about efficient evaluation allocation and adaptive screening.
- Do not treat Terminal-Bench 2.1 numbers from Task-CoEvolve as untouched-test evidence; search and final evaluation use the same 89 tasks.
- Do not claim adaptive sampling is always better than full-set evaluation; gains are benchmark/model/budget dependent and the estimator can rank candidates poorly at low sampling rates.
- Do not treat the post-training strategy-lock-in study as proof that any proposed strategy-reopening trigger improves outcomes; it diagnoses a missing control transition.
- Do not infer that more strategy changes are always better. The needed object is evidence-triggered reopening, not indiscriminate strategy churn.

## Nonempty frontier / exact next action

1. Continue searching for >10-proposal real-LLM self-improvement systems that combine candidate-local anytime-valid evidence with durable cross-proposal statistical spending and now also an explicit evidence-triggered strategy-reopening mechanism.
2. Prefer systems that publish complete candidate and evaluation chronology, including adaptive task-sampling probabilities and feedback payloads, so screening and promotion can be independently replayed.
3. Revisit Task-CoEvolve when executable code/results are published; audit whether inclusion probabilities, random seeds, candidate chronology and full-validation calibration artifacts are preserved.
4. Search for a replayable post-training or harness-evolution system where proposal sequences can be held fixed while comparing (a) full fixed validation, (b) random resampling, and (c) adaptive variance-weighted screening, under the same candidate-local promotion rule and untouched outer test.
5. In parallel, seek a matched intervention that turns strategy revision into an explicit decision point after plateau/regression while holding model, execution budget and outer evaluation fixed. Measure strategy-change rate separately from final outcome so increased churn is not mistaken for improvement.

Research remains open; this checkpoint is a continuation boundary, not completion.