# Self-improvement clean checkpoint 58 — Meta^n historical run configuration and adaptive selection pressure

Prepared at: 2026-08-27T11:02:25+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic-control tuple

This physical invocation froze semantic interpretation before the first substantive role-local/public-source read to:

- note main SHA: `828d11d61f7417ef51fdaf6248c3f3a671f92313`
- root control revision: 11
- self_improvement config revision: 6
- self_improvement config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- invocation semantic predecessor: sequence 57

Later note-main advances, if any, are not adopted semantically in this invocation.

## Source-qualified update: SIG-METAN-HISTORICAL-RUN-CONFIG

Primary paper: Meta^n: Recursive Self-Improvement through Emergent Depth, arXiv:2608.24735 v1 (2026-08-25).
Public code: `minnesotanlp/meta-n` public `main`, including the initial public release commit `b0861e62245ba30bfe3e751f1094a9918785e911` and current public commit `b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8`.

### New public provenance recovered from bundled historical run scripts

The public repository contains run scripts that explicitly preserve the historical experiment flag sets by passing `--benchmark-config none`, with comments that the bundled YAML must not rewrite them. This resolves an ambiguity from sequence 57: the current default benchmark feature profile is not the same execution policy as the main paper's historical agentic runs.

1. `scripts/run_agentic_stage1_classification.sh` says it mirrors `full_symptom2disease_v5` and `full_lawbench_v5`. It pins `--benchmark-config none`, then for both tasks uses `B=1`, `K=3`, `max_iterations=20`, effectively disabled patience (`999`), and `--gate-tasks 0`.
2. `scripts/run_agentic_stage2_cobench.sh` says it mirrors `full_cobench_v5`. It pins `--benchmark-config none` and uses `B=2`, `K=2`, `max_iterations=8`, `patience=4`, and `--gate-tasks 3`.
3. `scripts/run_agentic_stage3a_math_algotune.sh` says it mirrors the historical AlphaEvolve Math and AlgoTune runs. It likewise pins `--benchmark-config none`, with `B=2`, `K=2`, `max_iterations=6`, `patience=10`, and `--gate-tasks 3`.

These flags match the paper's experiment table closely enough to be useful historical-run proxies. They also match reported candidate counts where the full iteration budget was consumed: for S2D and LawBench, seed + 20*3 challengers = 61 archived candidates.

### Current default profile is materially different

The current and initial-public `meta_n/configs/benchmark_features.yaml` instead load a metacognition profile by default with:

- `consolidate: true`
- `regression_guard: true`
- `regression_guard_repeats: 3`
- `within_task_recursion: true`
- `focus_current_headroom: true`
- `symmetric_trace_sampling: true`
- S2D/LawBench additionally `eval_repeats: 3`

Its own comments state that consolidation children skip the quality gate and inherit non-focus task traces. The historical scripts deliberately bypass this profile. Therefore running the current README/default benchmark configuration is not equivalent to rerunning the main historical agentic paper configuration.

This also strengthens the prior separation between the main headline agentic runs and Appendix-G consolidation: consolidation was a separate study mechanism, not something that can be silently imputed into the historical main agentic rows from today's default YAML.

## Adaptive selection-pressure refinement

The historical/proxy configuration now allows a more concrete interpretation of selection exposure:

- **Symptom2Disease agentic:** 60 challengers plus seed on one adaptive search/dev surface, no quality gate (`gate_tasks=0`) in the historical script, then a separate held-out test in the paper.
- **LawBench agentic:** same 60 challengers plus seed, no quality gate, then a separate held-out test.
- **CO-Bench agentic:** at most 32 challengers plus seed from `B=2, K=2, 8 iterations`; the paper reports 29 archived candidates for the cited Gemma run, so early stopping/budget/path details reduced materialized candidates below the nominal maximum. A 3-task gate was enabled.

The public initial-release gate implementation is not a candidate-level no-regression test by default. A gate task clears if it succeeds and meets the parent-relative margin, and the candidate passes on the first cleared task; `protect_floor` is the opt-in mechanism that can veto a severe tested regression across gate tasks. The historical CO script does not set `protect_floor`, and it disables the bundled config that would otherwise enable other regression protections. Thus, **under the public historical command plus initial-public implementation**, CO's gate is a weak liveness/relative-quality screen rather than a statistical or all-task no-regression promotion certificate.

Scope guard: the exact pre-public executable used to produce the paper's reported rows is not publicly bound. Public Git history begins with the 2026-08-26 initial release, after the 2026-08-25 paper submission, and the paper-run `experiments/*` bundles are absent. Therefore the gate-semantics statement above is an executable reconstruction from the historical public command and initial-public source, not proof that the unreleased paper-run source bytes were identical.

## Why this matters for self-improvement evidence

A reproducible self-improvement claim should bind the experiment not only to a repository and model but to the exact improvement-control surface:

- historical run-script digest / full CLI
- whether repository benchmark config was loaded or explicitly disabled
- exact executable revision
- candidate/proposal chronology and parent lineage
- adaptive selection-query count
- gate predicate and regression protections actually active
- checkpoint/early-stop policy
- final held-out-test invocation and whether it was consumed by search, routing, rollback, or selection

Without those bindings, a later repository default can silently turn a historical search process into a materially different system while still appearing to be "the same codebase".

## Evidence classification

- **Historical agentic CLI reconstruction:** public artifact evidence, strong for the released run scripts and their stated mirror targets; not exact paper-run executable proof.
- **S2D/LawBench 61-candidate selection exposure:** paper + public run-script consistency; exact per-candidate chronology still unavailable.
- **Current-default versus historical-profile mismatch:** directly verified in public source.
- **CO public gate semantics:** directly verified for the initial-public source + historical public command; historical pre-public code equivalence unverified.
- **Appendix-G fresh outer-test consolidation gain:** remains unverified from public artifacts, as in sequence 57.

## Frontier remains nonempty

Exact next action:

1. Inspect the remaining bundled historical runner surfaces (Symbolic Regression, TerminalBench and any single-shot mirrors) and construct a source-bound `paper_run_config_matrix` separating historical CLI/YAML-none behavior from current default YAML behavior.
2. Build a held-out-benchmark selection-pressure table with nominal challengers, materialized candidates, gate/no-gate, gate predicate, adaptive selection surface, final test surface, and reported dev-to-test drift.
3. Search releases, author artifacts, caches and public branches for any pre-public experiment bundle or executable revision that binds the historical scripts to the exact paper runs; otherwise preserve `historical_script_proxy` as the evidence class.
4. Inspect final test-evaluation code per held-out benchmark to verify whether it is one-shot post-selection and to bind the tested candidate/router identities.
5. Preserve the Appendix-G consolidation outer-evaluation gap and distinguish archive-accounting monotonicity from fresh routed-policy generalization.
6. Continue Recuris scorer/provenance recovery and StarHarness release monitoring without importing downstream state.
7. Continue searching for a >10-proposal live LLM self-improvement system with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, and an outer evaluation never consumed by adaptive selection.

## Public source pointers

- Paper: https://arxiv.org/abs/2608.24735
- Repo: https://github.com/minnesotanlp/meta-n
- Historical classification runner: `scripts/run_agentic_stage1_classification.sh`
- Historical CO-Bench runner: `scripts/run_agentic_stage2_cobench.sh`
- Historical Math/AlgoTune runner: `scripts/run_agentic_stage3a_math_algotune.sh`
- Current/default benchmark profile: `meta_n/configs/benchmark_features.yaml`
- Public orchestrator: `meta_n/core/evolutionary_orchestrator.py`
- Public archive: `meta_n/core/archive.py`
