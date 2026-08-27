# Self-improvement clean checkpoint 57 — Meta^n consolidation outer-evaluation gap

Prepared at: 2026-08-27T10:09:21+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

Semantic interpretation remains frozen to the tuple selected before the first substantive read in this physical invocation:

- note main SHA: `2e87b96b20d51d9b8e7df0981c477d55075087ba`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- invocation semantic predecessor: sequence 55

Sequence 56 was an intermediate checkpoint in the same frozen invocation. Later note-main advances are not adopted semantically here.

## Source-qualified update: SIG-METAN-CONSOLIDATION-OUTER-EVAL-GAP

Primary paper: Meta^n: Recursive Self-Improvement through Emergent Depth, arXiv:2608.24735 v1 (2026-08-25).
Public code: `minnesotanlp/meta-n`, public `main` inspected in this invocation.

Appendix G makes the consolidation claim narrower than a generic held-out no-regression claim:

- it says each candidate improves one focus task and **inherits the archive's frozen best traces for every other task**;
- it reports the **per-task-best mean** rising from `0.502` to `0.71 ± 0.02` on an 8-task CO-Bench band, versus `0.61 ± 0.03` for compute-matched best-of-4, for a `+0.10` difference with 95% CI `[+0.04,+0.16]`;
- it explicitly rests the main claim on the **shape of the trajectory**: consolidation is monotone by construction and therefore cannot regress an already-solved task on that maintained per-task-best state.

The paper does **not** identify these Appendix-G `0.71` / `0.61` numbers as a disjoint held-out-test evaluation, nor does Appendix G describe a fresh final panel after the adaptive consolidation search. The terminology is the same per-task-best archive quantity defined in the search method.

The current public implementation matches that interpretation:

1. In consolidate mode, the focus task is solved freshly while every non-focus task inherits its existing per-task-best trace without re-solving it.
2. `_build_merged_candidate()` then constructs `merge_oracle` by mapping each known task id to its stored winner script. It performs **no LLM call and no re-evaluation**; the merged candidate mean is set equal to the archive oracle mean by construction.
3. Separately, the ordinary end-of-run test machinery is capable of re-evaluating each selected specialist on a held-out test split (`_run_test_evaluation`) and, independently, one best single chain (`_run_chain_test_evaluation`).

What is missing from the public paper/artifacts is a binding showing that the Appendix-G `0.71 ± 0.02` and `+0.10` values are those held-out re-evaluations rather than the adaptive per-task-best search/accounting values. The reported paper-run experiment bundles are not public, so this cannot be resolved from candidate/test result files.

### Correct evidence classification

Therefore the current evidence contract is:

- **zero-regression trajectory**: verified as a construction property of the maintained per-task-best archive state on the consolidation/search panel;
- **mean lift versus compute-matched best-of-4**: primary-paper quantitative evidence on the reported consolidation study panel;
- **fresh outer-test lift of the consolidated router**: **unverified** from public artifacts;
- **single-general-solver no-regression**: not what the mechanism implements or what the paper's Appendix-G guarantee proves.

This is not a negative result against consolidation. A known-task specialist router can be a useful deployable policy, and the public implementation does contain a separate test-evaluation path capable of measuring it on held-out instances. The unresolved point is whether the exact Appendix-G headline numbers were produced by that outer path.

## Why this matters for self-improvement claims

A self-improvement system can obtain monotonicity at at least three different levels that must not be conflated:

1. **archive accounting monotonicity** — keep historical bests and never lower stored maxima;
2. **routed policy monotonicity on the adaptive panel** — dispatch known task identities to their historically best specialists;
3. **fresh generalization monotonicity** — freeze the whole routing policy, then improve or at least not regress when all selected specialists/router decisions are re-evaluated on data never used for search or selection.

Meta^n consolidation directly guarantees (1), materializes a policy for (2), and has generic code infrastructure capable of measuring (3), but the public Appendix-G result does not currently bind its headline consolidation numbers to (3).

For future self-improvement evaluation, a claimed no-regression guarantee should state the level explicitly and record a source-bound `search_panel_digest`, `selected_specialist_ids`, `router_policy_digest`, and a separate `outer_panel_digest` with final results produced only after the policy is frozen.

## Related selection-pressure refinement from sequence 56

The paper's production candidate counts show repeated adaptive selection before the final held-out pass on benchmarks that have one. For example, Symptom2Disease and LawBench use 61 materialized candidates in the full reported Gemma configurations (seed plus 20 iterations × 3 children), and CO-Bench single-shot uses 33 (seed plus 8 × 4). Thus the held-out final test is valuable precisely because the adaptive dev selection surface is queried dozens of times. The Symptom2Disease held-out result, where routed archive-best is slightly below the best single chain on both reported backbones, is a direct example that search-panel per-task maxima need not dominate on fresh data.

## Reproducibility boundary

The public repository records enough structure for future runs to preserve candidate ids/parents, scores, traces, injected code, checkpoints and LLM I/O, but the visible Git history starts after the paper submission and the reported paper-run `experiments/*` bundles are absent. Consequently:

- the exact proposal chronology cannot be replayed;
- the exact pre-public executable/config cannot be bound to the reported Appendix-G study;
- the Appendix-G numeric panel cannot presently be classified more strongly than the paper text permits.

## Frontier remains nonempty

Exact next action:

1. Recover any public Meta^n paper-run experiment bundle, pre-public source/config, release asset, author artifact or result matrix that binds Appendix-G consolidation numbers to search/dev versus held-out test; if unavailable, preserve this outer-evaluation gap.
2. Re-tabulate all Meta^n results by `latest_single_lineage`, `best_single_lineage`, `routed_portfolio`, and `frozen_router_outer_test`, with evidence classes `held_out`, `proxy`, `dev_equals_test`, `none`, and run-specific `heldout_consumed_by_search`.
3. Quantify adaptive selection-query exposure per benchmark/seed using B×K×iterations, actual materialized candidate counts, and early-stop behavior.
4. Inspect consolidation runner/config surfaces for any explicit final merged-router re-execution on a fresh panel and distinguish that result from inherited search-side per-task-best accounting.
5. Inspect optional verifier, rollback, regression-guard, helper-verification and checkpoint-selection paths for any additional nominal-test consumption.
6. Continue Recuris pre-public scorer/per-trial provenance recovery and StarHarness public code/run-ledger monitoring.
7. Continue searching for a >10-proposal live LLM self-improvement system with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.

## Primary source pointers

- Paper: https://arxiv.org/abs/2608.24735
- Public repo: https://github.com/minnesotanlp/meta-n
- Public archive: `meta_n/core/archive.py`
- Public orchestrator: `meta_n/core/evolutionary_orchestrator.py`
- Current inspected orchestrator blob: `7ff64cc6d62c58a1bcfe442431da3f253305631e`
