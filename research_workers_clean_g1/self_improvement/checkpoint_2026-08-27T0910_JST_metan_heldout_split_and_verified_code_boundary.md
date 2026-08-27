# Self-improvement clean checkpoint 55 — Meta^n held-out split and verified-code boundary

Timestamp: 2026-08-27T09:10:47.511881+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

Unchanged for this physical invocation:

- note main SHA: `380533a125d725d5c24721426052fd0604cd2dac`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic predecessor for this invocation: sequence 53

This checkpoint advances sequence 54 with a correction/refinement discovered by continuing the public-source audit. It does not adopt newer repository control semantics.

## Correction to sequence 54 — final test is post-search on the normal/default path, but one optional forensic flag can consult CO-Bench held-out test during search

Sequence 54 said no public code path was found where final-test outcome feeds archive selection/routing. That statement was too broad.

The source-bound initial public release includes an optional `--verified-code` mechanism. It is **default OFF**, and the bundled `benchmark_features.yaml` does not enable it. The source calls the mechanism a `Forensic #2` / `VERIFY-THEN-INJECT` channel and describes it as build-only / unmeasured. The paper HTML contains no `verified` mechanism mention found in this audit.

However, when `--verified-code` is explicitly enabled, `COBenchAdapter.make_heldout_verifier()` can return a real sandbox verifier for a **crew-scheduling-only** run. That verifier executes an Omega-authored helper against the CO-Bench **held-out TEST split** and keeps/drops the helper based on test performance. The adapter is explicit that this override is consulted only when `verified_code` is on; it returns no real held-out verifier for non-crew/multi-task CO runs.

Therefore the correct contract is:

- normal/default public Meta^n search path: held-out test is post-search reporting for the adapters with genuine test splits;
- optional crew-only CO `--verified-code` path: held-out test is an adaptive build-time gate and is **not** an untouched outer test for that run;
- `--verified-code + --force-code-library-live` is the end-to-end meaningful CO combination because CO normally demotes the Python helper library.

Any experiment using this forensic flag needs an additional independent outer test if it wants an untouched-generalization claim.

This is a scope correction, not evidence that the paper's headline runs used the flag. The exact private paper-run executable/config remains unavailable; the public default and bundled profile leave the flag off, and the paper does not describe it.

## Paper/source alignment — the paper itself distinguishes split semantics more carefully than the abstract headline

The full arXiv HTML explicitly states:

- held-out test is reported for CO-Bench, Symptom2Disease, and LawBench;
- AlphaEvolve Math, AlgoTune, and Symbolic Regression have no held-out split and report benchmark score directly;
- ARC-AGI-2 Table 2 reports a dev score, while the held-out test result is reported separately in text;
- for the depth-1 ablation table, no held-out test pass was run and the numbers are archive-best validation scores.

Thus the paper does not actually present all benchmark-family scores as homogeneous held-out tests. The source audit strengthens the rule that downstream summaries should preserve those distinctions rather than compressing all eight families into one notion of generalization.

## CO-Bench exact split semantics

At the source-bound initial public release:

- each CO task loads all case files and a `get_dev()` map from its config;
- search/dev evaluation uses only the dev-map instance indices;
- final test evaluation uses the disjoint complement: every non-dev instance, including all instances of files not present in the dev map;
- the task metadata exposed to the solver contains task name, problem description, solve template and solution language, not the individual dev/test instances;
- the task description is built from the problem DESCRIPTION and solve-template source, not held-out cases;
- `evaluate_test()` is documented as final reporting only on the normal path.

So CO-Bench provides a genuine **within-task instance holdout**: search knows the task family/contract but not the final test instances through the ordinary TaskDescription channel.

The distinction is important: this is not unseen task identity generalization. It is generalization from dev instances to disjoint instances of the same optimization problem family/task.

## Text-classification exact split semantics

### Symptom2Disease

The public adapter:

- loads the Hugging Face train and official test splits;
- shuffles only the train split with a fixed seed;
- uses the first `max_val` shuffled train examples as adaptive validation;
- uses the remainder as training/few-shot source;
- leaves the official dataset test split for final `evaluate_test`.

### LawBench charge prediction

The public adapter:

- uses the first 200 rows as train;
- the next `max_val` as adaptive validation;
- the remaining rows as test.

### What the evolving solver sees

For both classification datasets, `TaskDescription.metadata` deliberately excludes val per-case texts and labels. It includes:

- label vocabulary,
- metric/language,
- a few-shot subset of TRAIN examples.

The source explicitly says val payload must not enter metadata because Omega's injected pre-process can read metadata. Search evaluation passes val case texts to the candidate solve function at execution time and returns aggregate score plus limited mismatch feedback, so the **validation set is adaptive search data**, as intended. Final test uses the separate test examples only after search on the normal orchestrator path.

The label vocabulary is built from the dataset globally (including test labels), so this is not a claim of complete data-schema blindness; it is a standard closed-label classification setup where per-example test text->gold mappings remain held out.

## ARC-AGI-2 rechecked against the paper wording

The public adapter's split is different from CO/text classification:

- search scores the TRAIN demonstration pairs that are already shown in the puzzle prompt;
- final `evaluate_test()` scores the puzzle's hidden TEST pair(s);
- `split_type()` therefore returns `proxy`, not `held_out`;
- public source warns that per-task archive selection still uses the raw demo score and split-aware overfit protection is not wired.

The paper's Table 2 correspondingly labels the reported ARC archive score as dev and places the held-out result separately in text. That is an important safeguard against accidentally reading the table's 0.331 archive-best as held-out ARC performance.

## Search-feedback versus outer-test taxonomy now supported by source

For this Meta^n public implementation, evaluation evidence should be represented with at least these categories:

1. **held_out**: CO-Bench, Symptom2Disease, LawBench — separate test examples/instances exist. On the standard path they are post-search reporting.
2. **proxy**: ARC-AGI-2 — adaptive score is prompt-visible demonstration fit; held-out puzzle test is separate and can expose overfit.
3. **dev_equals_test**: AlphaEvolve Math, Symbolic Regression, AlgoTune — final `evaluate_test` just re-runs the same deterministic evaluator; no independent generalization layer.
4. **none**: TerminalBench and SWE-bench adapters — no optional `evaluate_test` method in the common public orchestrator.
5. **held-out-but-consumed-by-search**: a run-specific state, not a dataset property, created when an explicit mechanism such as CO crew `--verified-code` consumes a nominal test split during adaptive candidate construction.

This fifth category is the key correction: **split structure and realized information flow are separate contracts**. A dataset can have a held-out split while a particular run invalidates its outer-test status by querying it during search.

## Candidate-selection interpretation

On the standard path, final held-out data do not pick archive members. The archive-best candidate and each per-task portfolio member are chosen from adaptive search/dev scores, then those already-chosen artifacts are evaluated on test.

Therefore:

- held-out `archive-best` is better described as a **search-selected per-task portfolio evaluated on held-out data**;
- `best chain` is a **single search-selected lineage evaluated on held-out data**;
- the difference between them measures portfolio/per-task selection value under the tested task IDs, not one lineage's recursive gain;
- an actual deployment claim for the portfolio requires a router that can choose members without test outcomes.

The paper itself makes the archive-best versus best-single-chain distinction and states that their gap is what per-task selection buys.

## Reproducibility/provenance update

The arXiv submission timestamp is 2026-08-25 15:44:25 UTC. The public repository's entire visible Git history begins with the parentless `Initial public release of Meta^n` commit at 2026-08-26 16:30:14 UTC, followed by one Omega display-precision fix. Thus there is no public pre-submission commit history to bind to the actual reported runs.

The implementation is locally replay-friendly — candidate IDs/parents, traces, per-task scores, injected code, raw Omega prompt/response sidecars, RNG/checkpoint state and LLM I/O are designed to be persisted — but `experiments/*` is ignored by default and the inspected public tree does not include the reported paper-run archives. This remains the main barrier to matched replay of the exact stochastic proposal sequence.

## Updated design rule

A self-improvement evaluation should bind **both**:

- **split semantics**: does a separate test set exist?
- **information-flow semantics**: did any adaptive proposer, verifier, rollback rule, checkpoint selector, helper gate, router, or stopping rule consult it?

Only when both answers are favorable should a split be called an untouched outer test.

A practical per-run provenance record should include:

- `split_type`,
- exact search/dev identifiers or hashes,
- exact outer-test identifiers/hash kept hidden from proposer,
- every code path allowed to query each split,
- whether test was consulted by verification or rollback,
- final candidate/portfolio identity frozen before outer test,
- whether any post-test action can alter the deployed artifact.

## Frontier remains nonempty

Exact next action:

1. Recover the Meta^n paper-run experiment bundles or exact pre-public executable/config from author/public artifact surfaces; if unavailable, record the replay gap as durable rather than infer run flags from current defaults.
2. Audit the paper's exact CO/S2D/LawBench experiment hyperparameters and candidate counts against public config, and quantify adaptive search-query counts before each held-out evaluation.
3. Re-tabulate Meta^n reported gains by evidence class: held-out, proxy, dev==test, no test; separate best-single-lineage from per-task portfolio.
4. Inspect whether any other optional verifier/regression mechanism besides CO crew `--verified-code` can consume nominal outer data during search.
5. Audit consolidation's exact experiment: candidate generation budget, selection panel, inherited per-task winners, and whether the reported +0.10 versus compute-matched best-of-4 was measured on the same adaptive panel or a fresh one.
6. Continue the Recuris pre-public scorer/per-trial provenance search and StarHarness code/run-ledger monitoring.
7. Continue searching for a >10-proposal live LLM self-improvement system with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.
