# Primary verification — C19 Meta^n historical runner / outer-evaluation contract

Observed: 2026-08-27T14:42+09:00
Verifier role: `primary_source_verifier`
Frozen note control/source SHA for this invocation: `5fcfb917e2b8d0db5600b30a35898c6fb128bad6`
Frozen root control revision: 11
Frozen verifier config revision: 4

## Source-qualified candidate

- namespace: `self_improvement`
- sealed C19 source artifact: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1204_JST_metan_historical_outer_eval_matrix.md`
- source artifact blob: `1cb181bb29bd17a49ef6a313f3fb892da5eeca91`
- source-local candidate id: `Meta^n`
- paper: `Meta^n: Recursive Self-Improvement through Emergent Depth`, arXiv:2608.24735v1, submitted 2026-08-25
- public repository commit checked: `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8`

## Verified findings

1. **Historical public agentic runner proxies bypass today's bundled metacognition profile.**
   `scripts/run_agentic_stage1_classification.sh` and `scripts/run_agentic_stage3a_math_algotune.sh` both explicitly pass `--benchmark-config none`. The CLI documents this as reproducing the bare pre-metacognition behavior. The current bundled `meta_n/configs/benchmark_features.yaml` is loaded by default otherwise and enables, among other things, `consolidate`, `regression_guard`, `within_task_recursion`, `focus_current_headroom`, and `symmetric_trace_sampling`; it also sets classification `eval_repeats: 3`. Therefore these later/default controls cannot be retroactively cited as mechanisms behind numbers produced through those historical-run proxy scripts.

2. **The OpenEvolve family has no distinct dev-vs-test surface in the checked public adapter.**
   At the pinned commit, `OpenEvolveBaseAdapter.split_type()` returns `"dev_equals_test"` and explicitly documents that its deterministic `evaluate_test` delegates to the same evaluation surface. Thus AlphaEvolve Math / Symbolic Regression / AlgoTune results obtained after adaptive search on this adapter are same-surface benchmark improvement, not fresh post-selection generalization evidence.

3. **Text classification does expose a distinct held-out test surface at the adapter-contract level.**
   `TextClassificationAdapter.split_type()` returns `"held_out"`, and `evaluate_test()` scores the selected reusable `solve()` function against the dataset test split, while ordinary `evaluate()` uses validation data. This supports treating Symptom2Disease and LawBench as capable of a genuine outer test under the current checked adapter contract.

4. **TerminalBench does not expose the optional adapter-level `evaluate_test` method.**
   The shared `BenchmarkAdapter` contract states that `terminal_bench` and `swe_bench` are adapters without that optional test pass, and the pinned `TerminalBenchAdapter` contains no `evaluate_test` implementation. Hence a Stage-4 TerminalBench score on this path should not be described as a separate post-selection outer test.

## Important remaining provenance gap

The above establishes **public code capability/configuration**, not execution proof for the paper-producing historical runs. In particular, this audit has not located a paper-run result bundle proving that the exact final candidate/router for each Symptom2Disease, LawBench, or CO-Bench historical run was frozen and then evaluated exactly once through the distinct test path, with no prior adaptive access to those test identities. Therefore `held_out` is currently a source-level split capability for these adapters; one-shot historical outer-evaluation execution remains `UNVERIFIED` until bound to immutable paper-run receipts/artifacts.

The historical scripts are themselves published proxies and are not cryptographic proof that unpublished pre-release source bytes were identical.

## Scope / decision consequence

- Do not invalidate the Meta^n headline benchmark scores solely because some adapters are same-surface.
- Do not interpret all eight benchmark-family wins as equally strong evidence of post-selection generalization.
- Separate at least: `same_surface_adaptive_improvement`, `held_out_capability`, and `held_out_execution_verified`.
- Do not attribute historical headline behavior to the current bundled metacognition defaults when the recovered historical runner explicitly disables that config.

## Primary sources checked

- https://arxiv.org/abs/2608.24735
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/scripts/run_agentic_stage1_classification.sh`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/scripts/run_agentic_stage3a_math_algotune.sh`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/meta_n/configs/benchmark_features.yaml`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/meta_n/integrations/benchmark.py`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/meta_n/integrations/openevolve.py`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/meta_n/integrations/text_classification.py`
- `minnesotanlp/meta-n@b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8/meta_n/integrations/terminal_bench/adapter.py`

Verdict: **worker core classification SUPPORTED, with historical held-out execution still UNVERIFIED.**