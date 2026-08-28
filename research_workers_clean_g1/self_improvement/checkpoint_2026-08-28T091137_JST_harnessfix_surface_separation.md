# Self-Improvement Clean Checkpoint — sequence 89

Created: 2026-08-28T09:11:37+09:00

Frozen semantic tuple: note main `0ee54b2ba30142266aca7fa1581256df1183e161`, control revision 12, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued from role-local clean sequence 88 plus public sources only. No O, other-worker, downstream, aggregate-ledger, legacy/pre-independence or other-role semantic state was used.

## Positive comparison — HarnessFix separates adaptive validation from final test

Sequence 88 found that EvalVitals' public fix path uses its nominal CONFIRM surface twice: first as input/feedback for fix generation and repair escalation, then again to compute candidate e-values. The next question was whether a public repair system cleanly labels adaptive selection as such and keeps a different surface for final generalization.

`HarnessFix/HarnessFix` at public main `9167a0b9a58748c73b56c3ee04fdc3437ba0c56e` provides a useful comparison.

### Split semantics are explicit

For SWE-Bench Verified, `data/sample_swebench.py` creates three non-overlapping subsets from the official source pool:

- train: trace collection and repair iteration;
- val: regression/promotion gate during repair;
- test: held out for final evaluation.

The sampler checks train/test overlap and then samples val only from the remainder. This is materially stronger than calling a surface held-out while also using it to design the candidate being scored.

### Validation is intentionally adaptive, not misclassified as a final certificate

The public SWE pipeline makes the roles clear:

- candidate vs current-base VAL comparison is explicitly labelled `promotion evidence`;
- promotion decides whether the candidate becomes the next base;
- the iteration report persists validation regressed IDs, improved IDs, target metrics and failure reasons;
- `build_next_iteration_guidance` explicitly tells the next iteration to analyze validation regressions and preserve validation improvements;
- the subsequent aggregate step can consume validation-regression analyses and the prior iteration report.

So VAL is an adaptive TUNE/selection surface. It is not an untouched certification surface, and the code does not pretend otherwise.

### Final TEST adds empirical evidence that the acceptance gate matters

The public RQ3 table reports held-out test task scores for the regression-aware acceptance ablation:

| Benchmark | H0 | no regression-aware acceptance | full HarnessFix | full minus no-acceptance |
|---|---:|---:|---:|---:|
| GAIA | 43.3 | 55.6 | 61.7 | +6.1 pp |
| SWE | 45.3 | 53.3 | 57.3 | +4.0 pp |
| AppWorld | 36.7 | 39.3 | 43.0 | +3.7 pp |
| TB2 | 17.6 | 24.5 | 26.5 | +2.0 pp |

The RQ1 artifact reports full HarnessFix improvements over the starting harness on held-out test of +18.4 pp GAIA, +12.0 pp SWE, +6.3 pp AppWorld and +8.9 pp TB2, with the listed three-run held-out standard deviations 1.7, 1.7, 1.9 and 2.9 pp respectively.

These are author-released result tables rather than an independent replay: the repository explicitly excludes raw benchmark data, traces, logs and generated evaluation outputs. The source code and split construction support the protocol structure, but not independent reconstruction of the paper's exact candidate chronology from the public artifact.

## Design lesson

HarnessFix closes one problem that EvalVitals sequence 88 exposed: it separates **adaptive candidate selection** from **final held-out generalization evaluation**. It does not close all of the long-horizon statistical-control problem.

A stronger decomposition is now:

1. **EXPLORE/TRAIN** — failure diagnosis and source evidence.
2. **TUNE/VAL** — adaptive repair generation, candidate selection, regression feedback and strategy reopening. Reuse is allowed and should be labelled adaptive.
3. **CERTIFY** — freeze a candidate before querying this surface; compute candidate-local anytime-valid/post-selection-valid evidence; do not feed outcomes back into candidate generation before terminal certification.
4. **OUTER/TEST** — final one-shot generalization surface never used by proposal, certification, promotion, rollback, routing, stopping or recovery.

HarnessFix has 1, 2 and 4 in its public protocol. Sequence 88's EvalVitals path has EXPLORE and an adaptive combined TUNE/CERTIFY surface, with no inspected third outer surface. The missing public composition remains a real system with all four surfaces plus long-horizon durable evaluation accounting.

## Limits

- HarnessFix's validation promotion is threshold/rule based, not candidate-local anytime-valid evidence.
- VAL is queried repeatedly and its detailed regression outcomes feed later repair iterations, so it is not reusable statistical certification.
- No proposal-across-time error/FDR/FWER spending was identified in the inspected pipeline.
- The public repo does not provide a first-class immutable outer-query ledger that proves zero pre-final TEST access under every external evaluation script.
- Public raw run/evaluation outputs are excluded, so the paper chronology cannot be independently replayed from repository state alone.

## Source-bound artifact

Machine-readable contract: `research_workers_clean_g1/self_improvement/repair_surface_separation_contract_2026-08-28T091137_JST_harnessfix.json`.

Pinned source: `HarnessFix/HarnessFix@9167a0b9a58748c73b56c3ee04fdc3437ba0c56e`.

Relevant blobs:

- `data/sample_swebench.py@0807489f69a7f9016596bd039a950a2b5d35c0d9`
- `run_pipeline_swe.py@b5a904ca66c69cc8f8639ec9dde1289e8f0d5d1c`
- `failure_analysis/check_val_gate.py@2e2573e05b066be22d734540aabbc52c5f90e32c`
- `exp/rq1_effectiveness.md@7cf743a3c0b4c870bdb9bad527a00fe6d6b5b31a`
- `exp/rq3_ablation.md@bddab929a163e37bdb7895ba0ec3107c8f93cbaf`

## Exact next action

Search for a public repair/self-improvement system that inserts a frozen **CERTIFY** surface with candidate-local anytime-valid evidence between HarnessFix-style adaptive TUNE/VAL and an untouched TEST/OUTER surface. Verify in executable code that certification outcomes do not feed the proposer before terminal certification, and require OUTER to be unused by promotion, rollback, routing, stopping and recovery. In parallel, retain the Harn hard-kill/provider-reconciliation frontier for revisions that change its relevant paths. Frontier remains nonempty.
