# Self-improvement clean checkpoint — Meta^n Stage-2 serialization + ARC CLI boundary

- sequence: 61
- timestamp_jst: 2026-08-27T14:04:28+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1306_JST_metan_outer_test_identity_and_merge_boundary.md`
- frozen note main SHA: `c721f07be3c743313f255069fed32a4d44c31f55`
- frozen root control revision: 11
- frozen role config revision: 6
- clean inputs used: own sequence-60 state + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream state, legacy/pre-independence state, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound findings

### 1. Stage-2 CO-Bench historical public proxy is explicitly bare-config

At Meta^n initial public commit `b0861e62245ba30bfe3e751f1094a9918785e911`, `scripts/run_agentic_stage2_cobench.sh` uses four tasks (`search,workforce,emergency,crew_scheduling`), `max_iterations=8`, beam width `B=2`, children per parent `K=2`, max depth 4, patience 2, gate_tasks 3, and explicitly passes `--benchmark-config none`. Its nominal generation capacity is therefore at most 32 challengers plus the seed before early stopping/gate effects. This public historical proxy must not be conflated with an unpublished/pre-public paper executable.

### 2. Final serialization loses an explicit pre-merge single-lineage identity

In the same initial-public orchestrator, `EvolutionaryResult.best_candidate_id` is first set from the archive best before end-of-run merge. If `_build_merged_candidate(...)` creates a merge/router, the code then recomputes archive best and overwrites `best_candidate_id`; it separately stores `merge_candidate_id`. Test evaluation happens afterward, including the routine labeled as the single-best-chain test, which reads the current `archive.best_candidate`.

`EvolutionaryResult.to_dict()` persists `best_candidate_id` and optional `merge_candidate_id`, but there is no separate `pre_merge_best_candidate_id` or immutable `artifact_actually_tested_id`. Final `save_results()` overwrites `summary.json` with this post-merge result. The full archive index retains each candidate's `candidate_id`, `parent_id`, iteration/depth and scores, so if the complete archive chronology survives, a pre-merge champion can often be reconstructed offline by excluding the merge candidate and replaying strict-best updates. A headline/final summary alone cannot do this unambiguously.

**Implication:** outer-evaluation provenance needs separate source-bound fields for `pre_merge_single_lineage_id`, `merge_or_router_id`, and `artifact_id_actually_tested` (preferably content-addressed), rather than relying on names such as “best chain.”

### 3. ARC adapter has a real hidden TEST grid boundary, but its dev signal is explicitly only a proxy

The initial-public ARC adapter stores gold TEST outputs outside `task.metadata`, exposes only TEST inputs in public task metadata, shows TRAIN demonstrations to the solver, uses `evaluate()` on TRAIN demonstration pairs during evolution, and uses `evaluate_test()` on hidden TEST pairs. Unit tests explicitly verify that TEST inputs are absent from the solver description and that `evaluate_test()` exists and scores the TEST pairs.

However, the adapter's own `split_type()` is `proxy`, not `held_out`: comments state that train-demo perfection routinely fails the hidden test and that split-aware overfit protection is not consumed by archive selection. The archive still ranks candidates on raw `evaluate()` train-demo score. Thus the hidden test number can remain unqueried during search while selection itself can overfit a weak proxy.

### 4. More serious public-integration gap: ARC is advertised/parsed but not wired into the public CLI task-loading branch

At the exact initial-public `meta_n/main.py` revision, `arc_agi_2` is accepted by `--benchmark`, and the repository ships `meta_n/integrations/arc_agi.py` plus ARC adapter tests and a setup script. But the production `async_main()` task-loading chain contains branches for CO-Bench, text classification, Terminal-Bench, SWE-bench, and the OpenEvolve family, then falls through to `elif args.tasks` / the generic error. There is no `elif args.benchmark == "arc_agi_2"` branch constructing `ARCAGI2Adapter`/executor. The current public `main.py` inspected in this run shows the same branch structure.

Therefore the repository contains a functioning ARC adapter in isolation, but the advertised `python -m meta_n.main --benchmark arc_agi_2 ...` style public CLI path is not source-bound to a runnable adapter integration in the inspected public revision. Because the paper nevertheless reports ARC-AGI-2 as a key result, the exact paper-run ARC executable/orchestration path must have been different, unpublished, manually wired, or otherwise not recoverable from this public CLI path. This is a provenance/reproduction gap, not evidence that the reported ARC result is false.

### 5. If ARC is run through the evolutionary orchestrator, artifact identity remains a separate issue from test secrecy

The generic end-of-run test helpers evaluate per-task source traces on each adapter's `evaluate_test()` and also evaluate the current archive best. A merge candidate is assembled from task-specific source winner traces. Hence, on a multi-task ARC run, if a merge/router becomes archive best before the final test, the code path labeled “single best chain” can evaluate a task-ID-routed portfolio rather than one inherited lineage. Hidden TEST outputs can remain untouched during search while the identity of the outer-tested artifact is still misclassified.

This finding is source-bounded to the public orchestrator/adapter logic. The actual pre-public paper-run ARC executable and proposal/result bundle are unavailable, so whether its reported ARC result used such a merge/router is unknown.

## Evidence boundary / non-claims

- Do not claim the public historical runner exactly reproduces the paper-run executable; the public repository begins from a parentless post-paper initial commit.
- Do not claim the ARC paper result is false because the public CLI wiring is absent.
- Do not call ARC's search signal a held-out dev set: it is the visible TRAIN demonstrations and the adapter labels it `proxy`.
- Do not call `best_candidate_id` a single-lineage identity after end-of-run merge without checking candidate type/lineage.
- Do not infer that a hidden TEST split is an outer lockbox unless test access and tested-artifact identity are both source-bound for the actual run.

## Updated design hypothesis

Self-improvement evaluation needs two independent provenance axes:
1. **evaluation-surface provenance** — which examples/labels were queried by proposal, gating, selection, rollback, routing, stopping and final reporting;
2. **artifact-identity provenance** — the immutable exact object evaluated at each surface: pre-merge lineage, routed portfolio/merge, checkpoint, or other composite.

A clean outer-eval record should persist at least `{search_surface_digest, selection_surface_digest, outer_surface_digest, pre_merge_lineage_id/hash, router_or_merge_id/hash, artifact_actually_tested_id/hash, access_log_digest}`.

## Evidence-access gaps

- No public Stage-2 paper-run result bundle/proposal chronology was found in the inspected initial tree; run experiment outputs are not source-bound here.
- No dedicated historical ARC experiment runner exists in the initial public tree; only ARC setup script + adapter/tests are present.
- The exact pre-public paper-run ARC executable, candidate chronology, merge decision, final tested artifact ID and raw held-out result matrix remain unavailable.

## Nonempty frontier / exact next action

1. Search public Meta^n branches/releases/commits/artifacts and author-linked public resources for the actual ARC paper-run invocation/result bundle or a source revision that wires `ARCAGI2Adapter` into the run path; if found, bind model/config/candidate count/gate/search surface/final artifact/test surface exactly.
2. Inspect Meta^n ARC-related paper text and any public result files to distinguish reported dev/proxy score, hidden TEST score, best single lineage, and routed archive/merge values; do not infer from labels alone.
3. If no ARC execution artifact is recoverable, lock the gap as `PAPER_RESULT_WITH_UNBOUND_PUBLIC_EXECUTABLE` and move to the next system rather than repeatedly re-searching the same tree.
4. Continue the broader unresolved frontier: find a real >10-proposal LLM self-improvement experiment that simultaneously has candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback channel, complete proposal chronology, immutable promotion identity, and an outer test never used for adaptive selection/rollback/routing/stopping.

Research remains open; this checkpoint is a continuation boundary, not completion.