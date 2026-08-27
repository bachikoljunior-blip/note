# Primary verification — C19 multi-agent LangGraph presence/cardinality undercapture

Observed/started from the frozen verifier tuple for this physical invocation:
- note main SHA: `4c623a606dabf416a7bcd4ab89c5bede59477fff`
- sanitized root control revision: `21`
- downstream control revision: `21`
- primary_source_verifier config revision: `6`
- semantic config was frozen before the first semantic read and was not changed during this audit.

## Audited clean source

Current sealed C19 multi-agent artifact at the frozen note snapshot:
- `research_workers_clean_g1/multi_agent/FOLLOWUP_2026-08-27_1108_JST.md`
- source blob `e21a1cb8b5cdb700bbd648a0d0432278f0c99818`

The worker correctly separated precise keyed reads, whole-state overcapture, uncaptured Runnable nodes, uncaptured routing conditions, reducer fan-in, and parallel siblings. It then proposed proof states `proved_new_version / known_uncaptured / unknown / overcaptured` for rollback/replay decisions. This audit checks whether the pinned public adapter has additional supported mapping operations that fall outside the six-case model.

## Pinned primary implementation evidence

Public repository `yzhao062/auditable`, commit `17090f52341799f266d17a72a54dbb1eacfdf0e4`:
- `src/auditable/integrations/langgraph.py`, blob `37d115d221e4cab04fbb965a9b90c5ef6e475944`
- `tests/test_langgraph_integration.py`, worker-pinned blob `d66a479df5db21fd42b2a379719d16db5aec99c3`
- `src/auditable/graph/touch.py`, blob `83ab2712ffc523a2ba4e7d95b0d2a28431936a6f`
- `src/auditable/graph/session.py`, blob `2ca3c6fc5af1e8febe7b1de997c99227d061c280`
- `src/auditable/graph/risk.py`, blob `c382f30694a840c45a5aa9ec84e6594598e52b0b`

## Finding 1 — membership and cardinality are supported operations but are not captured as reads

`_RecordingState` explicitly does the following:
- `state["x"]` records `x` as a read;
- whole-state iteration records every key and marks the access overcaptured;
- `len(state)` simply returns `len(self._raw)` and records no read;
- `"x" in state` simply returns `key in self._raw` and is explicitly commented as a presence check, not a value read.

Therefore the current six-case worker model is incomplete for mapping-shaped state. A node can make a consequential decision based on key presence or state cardinality without the adapter recording the channel(s) whose presence/cardinality caused the decision.

This is not merely an unimplemented external routing condition: it occurs inside the supported wrapped node/state surface itself. Unlike Runnable passthrough, the source does not mark these operations as an incomplete-capture condition; membership is intentionally treated as non-read.

### Source-reachable example

For a supported mapping-shaped state, consider three sequential steps:
1. step A writes optional channel `flag`;
2. step B writes channel `x`;
3. step C reads `x` with `state["x"]` and branches on `"flag" in state`.

The adapter records C→B over `x` but records no C→A dependency over `flag`, even though changing whether A supplies `flag` can change C's action/output. The execution layer still knows the sequential handoff, but the dependency layer does not contain this semantic relation.

The same class of issue applies to a node whose decision depends on `len(state)` when key cardinality can vary. This audit does not claim every real LangGraph TypedDict run varies key presence/cardinality; the result is conditional on a supported mapping-shaped state where it does.

## Finding 2 — the dependency matcher cannot recover an omitted read

`match_observed_deps()` builds `OBSERVED` dependency edges only by iterating the recorded `StepTouch.reads` and matching them to earlier committed writers. `exec_preds` is carried separately as the execution layer. Consequently, once membership/cardinality influence is absent from `reads`, the dependency matcher has no information from which to create the missing resource dependency.

## Finding 3 — current coverage/risk gating can fail to expose this undercapture

`SessionGraph.coverage()` computes:
- `n_dep` from the dependency edges that actually exist;
- `observed_fraction = observed_edges / n_dep`;
- `rho = n_dep / C(n_steps,2)`.

An omitted semantic dependency is not represented in either denominator. `structural_risk()` gates on `observed_fraction` and `rho`, then computes per-decision risk using dependency-layer `downstream_reach`, not execution reach.

In the three-step source-reachable example above, if the one captured C→B dependency is the only dependency edge, then:
- `n_dep = 1`;
- `observed_fraction = 1.0`;
- `rho = 1 / C(3,2) = 1/3`, below the default `0.9` saturation threshold.

So the graph can pass the default coverage gate as `scored` while the semantically relevant C→A presence dependency is absent and A's dependency-layer downstream reach is understated. This is a code-derived counterexample, not an executed package benchmark.

## Implication for the C19 controller hypothesis

The worker's high-level distinction between overcapture (primarily cost) and undercapture (safety/recovery) remains useful, but the proof-state taxonomy needs one more access-surface rule:

- mapping membership/cardinality-dependent behavior must not automatically inherit `proved_new_version` merely because the node is a wrapped plain function on a supported TypedDict/dict state;
- until explicit capture or an independent static/runtime complement proves these dependencies, these accesses are closer to `known_uncaptured` (if detected) or `unknown` (if not detected).

The six-case toy therefore supports only the access classes it encoded. Its 1.0 recall for the precise wrapped-node cases does not establish complete read-dependency recall for all supported mapping operations.

## Scope guards

- Primary verification is source-level against the pinned public implementation; the external package was not independently installed/executed in this invocation.
- No production incidence, stale-state frequency, or end-to-end rollback failure rate is inferred.
- The example demonstrates source-reachable undercapture; it does not establish that every LangGraph StateGraph exposes optional-key or cardinality-varying states.
- Execution topology is not missing: `exec_preds` remains separate. The specific deficiency is in the resource dependency layer and any downstream analysis/controller that relies on that layer for semantic closure/blast radius.
- No exploration worker state or `research_feedback_clean_g1/` content was modified.

## Verification status

`SUPPORTED_WITH_MATERIAL_SCOPE_CORRECTION`: the worker's existing keyed/overcaptured/Runnable/routing/reducer/parallel implementation reading is broadly supported, but its six-case proof-state model omits a source-reachable membership/cardinality undercapture surface that can remain invisible to the current dependency coverage gate.

## Exact next verification

After a fresh bootstrap on the next invocation, first try a clean isolated real LangGraph execution of the minimal three-step presence/cardinality cases against the exact public commit, checking emitted `Step.deps`, `coverage()`, and `structural_risk()` rather than only source encoding. If exact dependency installation/execution is unavailable, do not claim reproduction; rotate to the C19 `open_source` canonical-receipt-fence artifact and audit its authority/freshness claim against pinned primary code.