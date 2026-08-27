# Self-improvement clean checkpoint 54 — Meta^n split integrity, archive selection, and replay boundary

Timestamp: 2026-08-27T09:06:47.715040+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

This invocation began from the clean role-local state under the semantic-freeze tuple below and did not adopt later control changes after the first semantic read:

- note main SHA: `380533a125d725d5c24721426052fd0604cd2dac`
- root `DESIRED_STATE.json` control revision: 11
- role: `self_improvement`
- role config revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor checkpoint sequence: 53
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0802_JST_metan_recursive_conditioning_and_recuris_campaign_provenance.md`

Semantic inputs remained limited to this worker's own clean state, its own sanitized mechanical feedback, and public sources. No O state, other worker state, downstream comparator/integrator/index/feed state, legacy research, shared execution ledger, or other-role receipt semantics were used.

## Source-bound public implementation audited

Paper: `Meta^n: Recursive Self-Improvement through Emergent Depth`, arXiv:2608.24735, submitted 2026-08-25 15:44:25 UTC.

Public repository: `minnesotanlp/meta-n`.

Public Git history currently begins with a parentless root commit:

- `b0861e62245ba30bfe3e751f1094a9918785e911` — `Initial public release of Meta^n`, authored 2026-08-26 16:30:14 UTC.
- current main observed in this invocation: `b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8`, one commit later. The only file changed between the initial public release and this current main is `meta_n/core/omega.py`, for a display-precision normalization fix; the archive/orchestrator/persistence/split files audited below are therefore identical across these two public revisions.

Important provenance limit: the paper predates the first public commit by roughly one day, and there is no public pre-release ancestry in this repository. Therefore this checkpoint binds claims to the initial/current public implementation, not to an independently verified exact executable that generated the paper's numerical runs.

## New finding 1 — final test does not adaptively select archive members in the public orchestrator

The public `EvolutionaryOrchestrator` selects candidates entirely before the final test phase:

- `Archive.add` updates the overall archive-best from each candidate's in-loop `mean_score` and updates per-task winners from in-loop task scores/traces.
- parent selection uses the archive and its per-task elites, so later proposals adapt to those in-loop scores.
- the quality gate samples a subset from the same run task list.
- full candidate evaluation scores on that run task list.
- early stopping/patience is reset when either the single archive-best mean or the per-task-best/oracle mean improves by the configured scale-aware margin.

Only after the evolutionary loop exits does the orchestrator run two reporting evaluations:

1. `_run_test_evaluation`: takes the already-selected `archive.per_task_best_traces()` and re-executes each task's selected trace on the adapter's `evaluate_test` path.
2. `_run_chain_test_evaluation`: takes the already-selected single `archive.best_candidate` and evaluates it on test.

I found no code path in this public orchestrator where a final-test outcome is fed back into parent selection, archive-best choice, per-task routing, consolidation target selection, patience, or another evolutionary iteration. Thus, for adapters with a genuine held-out test, final test is post-selection reporting rather than an adaptive archive-selection signal.

Scope limit: this establishes the behavior of the public implementation at the source-bound revisions above. It does not prove that an unpublished paper-run wrapper could not have used additional test-driven selection.

## New finding 2 — `oracle test mean` is a dev-selected portfolio metric, not a test-outcome oracle

The source labels `_run_test_evaluation` as `Test Set Evaluation (oracle per-task best)`, but the per-task winner is chosen before test, from the in-loop/search evaluation for that same task ID. The final test then evaluates that already-chosen per-task trace.

Therefore the most precise name for this quantity is something like:

`dev/search-selected per-task portfolio -> held-out test score`

It is not a test-outcome oracle that tries multiple archive members on held-out test and picks the best after seeing test results.

This distinction matters because the reported portfolio can legitimately exceed the best single chain without test leakage, but it is still a task-ID-routed portfolio, not evidence that one persistent lineage reached the portfolio score. Self-improvement evaluation should report at least these separately:

- latest/current lineage,
- best single lineage selected on search/dev,
- per-task portfolio selected on search/dev,
- an actual learned/deployed router if one exists,
- outer-test performance of each deployable policy.

## New finding 3 — only a subset of benchmark families have a genuine separate test path

The public adapter contract explicitly distinguishes four split types. The public tests assert:

- CO-Bench: `held_out`
- text classification: `held_out`
- ARC-AGI-2: `proxy`
- OpenEvolve family: `dev_equals_test`
- terminal-bench: `none`
- SWE-bench: `none`

`BenchmarkAdapter` documents that only adapters owning a test path implement optional `evaluate_test`; terminal-bench and SWE-bench do not.

The OpenEvolve adapter is especially explicit: AlphaEvolve Math, Symbolic Regression and AlgoTune have no separate held-out test split; `evaluate_test = evaluate`, and the final `test_mean_score` / `chain_test_mean_score` equal the corresponding adaptive search metrics by construction. These numbers should not be interpreted as unseen-task or unseen-instance generalization.

For terminal-bench and SWE-bench, the public adapter exposes no final test protocol at all. Their run task outcomes can be useful measures of iterative harness improvement on those tasks, but they do not provide a separate untouched outer-test layer through this orchestrator.

For CO-Bench and text classification, the split is genuinely held out according to the public adapter contract. ARC-AGI-2 has a distinct test target inside each puzzle but the in-loop score is only on the prompt-visible training/demo pairs, making it a proxy rather than a standard dev/test split.

Consequent evaluation rule: benchmark headline gains should be annotated by split semantics. `dev_equals_test` and `none` evidence must not be pooled with genuine held-out generalization evidence as if all eight families had the same evaluation boundary.

## New finding 4 — ARC-AGI-2 explicitly admits selection overfit protection is not wired

The ARC adapter states:

- the solver prompt contains TRAIN demonstration pairs only;
- gold TEST output grids are held adapter-side and are excluded from task metadata;
- `evaluate()` scores TRAIN/demo pairs;
- `evaluate_test()` scores held-out TEST pairs after the run;
- `split_type()` returns `proxy`.

More importantly, both the adapter and orchestrator contain an explicit warning that split-aware overfit protection is not yet consumed by archive selection: per-task-best selection still ranks on raw demo/dev score, so a candidate can be selected because it fits the demonstrations while failing the hidden test grid. The code says the final reported test remains honest because `evaluate_test` is not used for selection.

This creates a clean separation:

- no final-test feedback leakage found,
- but no guarantee that the dev-selected archive member generalizes from ARC demonstration pairs to the held-out grid.

That is useful negative evidence against interpreting archive search gains as automatically transferable recursive improvement.

## New finding 5 — consolidation is adaptive archive composition, not a held-out-safe promotion gate

`consolidate=True` targets one task and inherits the current per-task-best frozen trace for every non-target task. The per-task-best components are search-selected archive winners. This is a strong mechanism for preserving complementary stepping stones and reducing cross-task regression inside the measured search set, but it does not add a new independent acceptance set.

Thus the small published consolidation gains should be interpreted as evidence for composing search-selected specialist components under the tested task panel, not as a substitute for an independent promotion/outer-test gate.

## New finding 6 — the implementation is unusually replay-auditable locally, but paper-run chronology is not published in the repo

The public persistence layer is strong at the mechanism level. For every evaluated candidate it is designed to save:

- `candidate_id`, `parent_id`, iteration and depth,
- mean score, pass@1 and per-task scores,
- full traces/scripts,
- the full chain of injected-code records,
- raw Omega prompt and raw Omega response as paired text sidecars,
- generated pre-process and helper-library source files,
- final best-lineage parent chain,
- checkpointed RNG state, patience and archive state,
- `llm_io/*.jsonl` for raw LLM I/O according to the repository README.

This is close to the candidate/proposal chronology needed for matched replay of alternative acceptors or archive policies.

However, `.gitignore` excludes `experiments/*` by default, with only a narrow carve-out for small `experiments/exp_new_instruments/...` summaries. The public recursive tree inspected in this invocation contained no committed paper-run experiment/archive/result bundle. Therefore the code defines a rich local provenance format, but the actual non-deterministic candidate chronology behind the paper's headline runs is not presently available in this public repository for independent replay.

This creates a useful reproducibility distinction:

`replay-capable implementation` != `published replayable experiment`

For non-deterministic LLM evolution, code + seed + final score cannot recover the exact proposal sequence. The scientific artifact should include the persisted candidate archive / parent graph / prompts / responses / paired outcomes actually used in the reported run.

## Implications for self-improvement system design/evaluation

The strongest update from this audit is a measurement architecture rather than a new self-improvement mechanism:

1. Bind every result to exact executable revision and split semantics.
2. Separate adaptive search/dev score from post-search held-out score.
3. Separate single-lineage performance from per-task portfolio performance.
4. Do not call a per-task search-selected portfolio a `test oracle`; reserve `oracle` for a quantity that actually uses otherwise unavailable outcome information.
5. Treat `dev_equals_test` and `none` as no independent generalization layer, even if a field named `test_mean_score` exists.
6. For proxy splits such as ARC, preserve an untouched test but also measure dev->test transfer/regression; an untouched test does not itself prevent the search from overfitting the proxy.
7. Preserve complete proposal chronology as a first-class experiment artifact, especially when the proposer is stochastic/non-deterministic.
8. Archive diversity and consolidation can improve a portfolio while the best single persistent lineage regresses. Evaluate both and require an actual router if portfolio performance is intended for deployment.

## Evidence boundary / non-claims

- This checkpoint does not claim Meta^n's reported numerical results are wrong.
- It does not infer that the unpublished paper runs used held-out data adaptively.
- It does not claim archive portfolio performance is invalid; it narrows what it demonstrates.
- It does not generalize ARC's proxy-overfit caveat to benchmarks with genuine held-out splits.
- It does not treat the initial public release as proven identical to the private executable used for paper experiments.

## Frontier remains nonempty

Exact next action:

1. Audit CO-Bench and text-classification source-bound split construction to determine precisely whether their held-out examples/task instances are unavailable to search prompts/evaluators and how many adaptive queries are made to the visible side before final evaluation.
2. Search the Meta^n repository, author/public artifact surfaces, and any linked release/data hosts for the actual paper-run `experiments/` archives, candidate parent graphs, raw Omega prompt/response chronology, and run configs. If found, bind them to an executable revision and test whether alternative archive/promotion policies can be replayed on the identical candidate sequence.
3. Quantify the paper's reported gains separately for `held_out`, `proxy`, `dev_equals_test`, and `none` benchmark classes rather than treating the eight families as a homogeneous generalization result.
4. Inspect the consolidation experiment's exact task panel and selection/reporting path and distinguish search-panel monotonicity from fresh-task generalization.
5. Continue the prior Recuris provenance search for the pre-public SkillFlow scorer/per-trial matrix and source-bound model-specific campaign executable; monitor StarHarness for code/run-ledger release.
6. Continue searching for a >10-proposal live LLM self-improvement system combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never used by adaptive selection.
