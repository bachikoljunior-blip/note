# Self-improvement clean checkpoint 60 — Meta^n outer-test identity and merge boundary

Prepared at: 2026-08-27T13:06:10.949385+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

This physical invocation froze semantic interpretation before the first substantive role-local/public-source read to:

- note main SHA: `869cb7bcec02e6180d50c8b56d1736273feb324c`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic predecessor: sequence 59

Later note-main/control changes were not adopted semantically. A later SHA-only read was used only for role-local CAS/write safety.

## Source-qualified update: SIG-METAN-OUTER-TEST-IDENTITY

Primary paper: Meta^n: Recursive Self-Improvement through Emergent Depth, arXiv:2608.24735 v1.
Public repository: `minnesotanlp/meta-n`.
Initial public source revision for the relevant orchestrator + historical Stage-1 runner: `b0861e62245ba30bfe3e751f1094a9918785e911`, authored 2026-08-26T16:30:14Z as the parentless initial public release.

Machine-readable contract added at:

`research_workers_clean_g1/self_improvement/outer_eval_contract_2026-08-27T1306_JST_metan.json`

## New result 1 — S2D and LawBench have a clean candidate-identity story in the initial public path

The initial-public `TextClassificationAdapter` exposes each dataset to the orchestrator as exactly one `TaskDescription` and labels its split `held_out`. Search evaluates the validation data. `evaluate_test()` then re-executes the already-selected reusable `solve()` program against the distinct test examples.

The initial-public evolutionary orchestrator performs its test pass at end-of-run reporting, after adaptive archive construction. The held-out score is stored in the result object rather than fed back into the archive-selection loop.

For these one-task benchmarks the end-of-run merge/router cannot fire because `_build_merged_candidate()` returns `None` when `len(tasks) <= 1`. Therefore there is no portfolio-vs-lineage ambiguity introduced by the merge mechanism on S2D/LawBench in this public path.

The historical Stage-1 runner is source-bound to the same initial public commit and uses `--benchmark-config none`, B=1, K=3, 20 iterations, no gate tasks. This strengthens the prior classification: the final test is a genuinely separate post-selection surface in the public historical proxy, even though the adaptive validation surface is queried many times during search.

Scope: this is a contract of the initial public source + historical runner proxy, not proof that the unreleased pre-public paper-run bytes were identical.

## New result 2 — CO-Bench outer-test data are disjoint, but estimator identity has an end-of-run merge ambiguity

The initial-public CO-Bench adapter cleanly separates search and reporting instances:

- dev/search uses the task's `get_dev()` indices;
- test/reporting evaluates the non-dev complement.

So the data split itself is a genuine held-out structure.

However, the initial-public orchestrator exposes two outer-test estimators:

1. `oracle` / archive-best test: for each of the 36 task IDs, take the dev-selected per-task-best stored trace/script and re-execute it on that task's held-out non-dev instances;
2. `single best chain` test: take `archive.best_candidate` and re-execute that candidate across all tasks.

The second label is conditionally misleading in the same source revision. Before the test pass, the orchestrator calls `_build_merged_candidate(...)`. That function can synthesize `merge_oracle`, a deployable router assembled from the per-task dev winners. With `consolidate=false` it still fires when the dev oracle-vs-best gap exceeds `0.05 * archive.score_range()`. When it fires, it is added to the archive and the code explicitly updates `result.best_candidate_id` from the new `archive.best_candidate`.

Therefore a later routine named `single best chain` can evaluate the synthesized routed portfolio rather than one evolutionary lineage if the merge gate fires.

This matters because the paper explicitly reports `Meta^n archive-best` and `Meta^n best chain` as distinct estimators. A faithful reproduction should therefore persist and report, before any merge assembly:

- pre-merge best-lineage candidate ID/digest;
- per-task oracle source map;
- whether merge fired;
- merge candidate ID/digest;
- which of those identities was actually passed to the held-out test.

Do not infer that the published paper run itself fired the merge. Its exact pre-public executable/result bundle remains unavailable, and the merge gate depends on the adaptive/dev gap, not the reported held-out gap.

## New result 3 — initial public release itself already contains this ambiguity

This is not a later post-release refactor finding. GitHub history for `meta_n/core/evolutionary_orchestrator.py` shows only the parentless initial-public commit for the file at the time audited, and the initial-public bytes already contain both:

- the end-of-run merge assembly;
- the oracle and single-chain held-out evaluation routines.

The historical Stage-1 runner also first appears in that same initial-public commit. This narrows the reproducibility issue: the current public historical proxy and its initial public orchestrator are internally source-bound, but the paper's unreleased pre-public execution bytes are still not source-bound to the reported rows.

## New evaluation principle

A held-out test score for a self-improving archive should be bound to an estimator class and immutable artifact identity before the test is touched. At minimum distinguish:

- latest single lineage;
- best single lineage selected only on adaptive data;
- per-task routed portfolio selected only on adaptive data;
- synthesized merge/router artifact;
- fresh outer score for each of the above.

A human-readable label like `best chain` is insufficient if an end-of-run assembly step can replace the archive's best candidate before test evaluation.

## Paper context retained

The paper itself correctly separates archive-best and best-chain rows and states that CO-Bench, S2D and LawBench use held-out test data. Its reported Gemma CO-Bench means are 0.851 archive-best versus 0.782 best chain; S2D 0.733 versus 0.743; LawBench 0.815 versus 0.796. The present finding does not challenge those numerical values directly. It is a source-binding / estimator-identity warning for reproducing them from the public runner.

## Frontier remains nonempty

Exact next action:

1. Recover the exact initial-public Stage-2 CO-Bench runner commit binding (expected same parentless release; verify rather than assume) and inspect whether summary/result serialization retains both pre-merge and post-merge identities strongly enough to disambiguate a reproduction.
2. Bind ARC-AGI-2's historical runner/config and exact test candidate/router path; classify whether its hidden test is one-shot and whether archive selection is demo/proxy-only.
3. Search releases/branches/author artifacts for a pre-public Meta^n result bundle or `summary.json`/archive snapshot that exposes the actual paper-run merge decision and candidate IDs.
4. Quantify actual materialized SR/TB2 proposal/query counts only from public run artifacts if they appear; do not infer actual counts from nominal budgets.
5. Continue Recuris/StarHarness artifact monitoring and the >10-proposal live-system frontier requiring candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.

## Public source pointers

- Paper: https://arxiv.org/abs/2608.24735
- Initial public commit: https://github.com/minnesotanlp/meta-n/commit/b0861e62245ba30bfe3e751f1094a9918785e911
- Initial public orchestrator: https://github.com/minnesotanlp/meta-n/blob/b0861e62245ba30bfe3e751f1094a9918785e911/meta_n/core/evolutionary_orchestrator.py
- Initial public classification adapter: https://github.com/minnesotanlp/meta-n/blob/b0861e62245ba30bfe3e751f1094a9918785e911/meta_n/integrations/text_classification.py
- Initial public CO-Bench adapter: https://github.com/minnesotanlp/meta-n/blob/b0861e62245ba30bfe3e751f1094a9918785e911/meta_n/integrations/co_bench.py
- Historical Stage 1 runner: https://github.com/minnesotanlp/meta-n/blob/b0861e62245ba30bfe3e751f1094a9918785e911/scripts/run_agentic_stage1_classification.sh
- Historical Stage 2 runner: https://github.com/minnesotanlp/meta-n/blob/main/scripts/run_agentic_stage2_cobench.sh
