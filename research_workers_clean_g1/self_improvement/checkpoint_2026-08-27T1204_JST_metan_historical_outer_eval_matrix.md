# Self-improvement clean checkpoint 59 — Meta^n historical runner matrix and outer-evaluation surface

Prepared at: 2026-08-27T12:04:30+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

This physical invocation froze semantic interpretation before the first substantive role-local/public-source read to:

- note main SHA: `7ea9e3bb08ae6e1713b76f33a2e84e2660bcc333`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic predecessor: sequence 58

Later control/main changes are not adopted semantically in this invocation.

## Source-qualified update: SIG-METAN-HISTORICAL-RUN-MATRIX

Primary paper: Meta^n: Recursive Self-Improvement through Emergent Depth, arXiv:2608.24735 v1 (submitted 2026-08-25).
Public repository: `minnesotanlp/meta-n`; public main observed at `b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8`.

A machine-readable matrix was added at:

`research_workers_clean_g1/self_improvement/paper_run_config_matrix_2026-08-27T1203_JST_metan.json`

It source-binds the recovered historical runner surfaces, current default benchmark profile, and public adapter split contracts.

## New result 1 — all recovered headline-agentic historical runner proxies disable today's default metacognition profile

The recovered Stage 1 / Stage 2 / Stage 3a / Stage 3b / Stage 4 scripts all explicitly pass:

`--benchmark-config none`

They then set their own beam width, candidate count, gate tasks, patience and retry behavior. The current bundled `benchmark_features.yaml`, by contrast, turns on `consolidate`, `regression_guard`, `within_task_recursion`, `focus_current_headroom`, `symmetric_trace_sampling`, classification `eval_repeats=3`, and OpenEvolve `foster_adoption` by default.

Therefore a current default README-style rerun is not the same improvement-control surface as the public historical runner proxies. The later default regression/consolidation stack cannot be retroactively used as the causal or safety mechanism behind the historical headline rows.

Scope: these scripts were published after the paper and are historical-run proxies, not cryptographic proof that the unreleased pre-public source bytes were identical.

## New result 2 — the OpenEvolve family has no fresh outer-test surface in the public historical path

The public `OpenEvolveBaseAdapter`, which covers AlphaEvolve Math, Symbolic Regression and AlgoTune, explicitly declares:

`split_type() -> "dev_equals_test"`

Its contract says the evaluator is deterministic and `evaluate_test` delegates to the same evaluation surface. This changes the evidence classification of the Stage 3a/3b agentic paths:

- AlphaEvolve Math: B=2, K=2, max 6, gate 3, nominal 24 challengers + seed; no distinct outer test.
- AlgoTune: same B/K/max/gate; no distinct outer test.
- Symbolic Regression: four subruns, each B=2, K=2, max 6, gate 3; no distinct outer test.

The gate may still be useful as an intra-run filter, but it is not a fresh generalization check. Search, gate and final score are all tied to the same evaluator/task identities in this public adapter contract.

This does not make these benchmark results invalid. It narrows the claim: they demonstrate adaptive same-surface benchmark improvement, not post-selection held-out generalization.

## New result 3 — TerminalBench Stage 4 also has no separate post-selection test path

The shared `BenchmarkAdapter` contract explicitly documents that adapters with a real test split implement `evaluate_test`, while `terminal_bench` and `swe_bench` do not. `TerminalBenchAdapter` does not add an `evaluate_test` override.

The recovered TB2 agentic runner contains 13 subruns. Every subrun uses B=1, K=2, with max iterations 6, 8 or 10 and gate tasks either 0 or 2. Nominal candidate totals including seed are therefore 13, 17 or 21 per subrun before early stopping.

Because there is no separate TerminalBench test path, the Stage 4 best/summary score remains on the same configured task list used by evolution. A 2-task gate is not an outer test and the 0-gate subruns have no promotion filter at all beyond the archive/search logic.

Evidence class: historical-script proxy + public adapter contract. Exact paper-run candidate chronology remains unavailable.

## New result 4 — only three recovered historical-agentic runner families currently have a distinct held-out final surface

Within the recovered Stage 1-4 historical-agentic runner set, the current source-bound classification is:

- Symptom2Disease: `held_out`; 60 challengers + seed, no gate in historical proxy, separate final test.
- LawBench charge: `held_out`; 60 challengers + seed, no gate in historical proxy, separate final test.
- CO-Bench: `held_out`; nominal 32 challengers + seed, historical proxy gate=3, reported agentic materialization 29 candidates, separate final test.
- AlphaEvolve Math: `dev_equals_test`.
- AlgoTune: `dev_equals_test`.
- Symbolic Regression: `dev_equals_test`.
- TerminalBench: no adapter-level test pass.

ARC-AGI-2 is deliberately not folded into this matrix until its exact historical execution surface is source-bound.

This distinction matters because the paper correctly spans heterogeneous benchmark families, but the strength of a self-improvement claim should be conditioned on the evaluation surface. A score obtained after dozens of adaptive candidate comparisons on the same evaluator is a weaker generalization claim than a score obtained after freezing the selected artifact and evaluating once on untouched data.

## Existing held-out warning retained

From the prior clean lineage, Symptom2Disease already gives a concrete example of why this split classification matters: the routed archive portfolio that is monotone on adaptive data is slightly below the best single lineage on held-out test for both reported backbones (Gemma 0.733 vs 0.743; GPT-5.2 0.725 vs 0.734). This remains a tested-scope warning against equating adaptive archive monotonicity with fresh generalization.

No broader claim is made about archive search or other benchmarks.

## Reproducibility implication

For recursive/self-improving agent papers, a result row should now bind at least:

1. exact historical CLI / runner digest;
2. whether default repository config was loaded or bypassed;
3. exact executable revision;
4. B × K × iteration budget and actual materialized candidate count;
5. gate predicate and whether the gate is same-surface or held-out;
6. adapter split class (`held_out`, `dev_equals_test`, `proxy`, `none`);
7. exact artifact/router frozen before final evaluation;
8. whether any nominal test data were queried by verifier, rollback, router, early-stop or checkpoint selection;
9. full proposal chronology when stochastic LLM generation prevents seed-only replay.

Without these bindings, later repository defaults can silently strengthen a historical method and make a reproduction appear safer or more generalizable than the experiment that produced the paper number.

## Frontier remains nonempty

Exact next action:

1. Bind the current public final-test implementation for Symptom2Disease, LawBench and CO-Bench to the exact selected candidate/router identity and confirm one-shot post-selection semantics.
2. Extend the matrix to ARC-AGI-2 and any single-shot historical mirrors only when their exact public runner/config surface is recovered.
3. Search releases, author artifacts, public branches and caches for a pre-public Meta^n executable/result bundle; otherwise retain `historical_script_proxy` as the evidence class.
4. Quantify actual materialized/proposal-query counts for SR/TB2 if paper-run artifacts appear; do not infer them from nominal budgets.
5. Preserve the Appendix-G consolidation outer-evaluation gap and keep `latest single lineage`, `best single lineage`, `routed portfolio`, and `outer-test policy` separate.
6. Continue Recuris scorer/provenance recovery and StarHarness release monitoring from public sources only.
7. Continue the >10-proposal live-system search requiring candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.

## Public source pointers

- Paper: https://arxiv.org/abs/2608.24735
- Repo: https://github.com/minnesotanlp/meta-n
- Stage 1: `scripts/run_agentic_stage1_classification.sh`
- Stage 2: `scripts/run_agentic_stage2_cobench.sh`
- Stage 3a: `scripts/run_agentic_stage3a_math_algotune.sh`
- Stage 3b: `scripts/run_agentic_stage3b_sr.sh`
- Stage 4: `scripts/run_tb2_agentic_all.sh`
- OpenEvolve adapter: `meta_n/integrations/openevolve.py`
- Shared benchmark split/test contract: `meta_n/integrations/benchmark.py`
- TerminalBench adapter: `meta_n/integrations/terminal_bench/adapter.py`
- Current default profile: `meta_n/configs/benchmark_features.yaml`
