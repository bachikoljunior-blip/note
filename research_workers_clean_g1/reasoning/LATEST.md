# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0315JST.md`
Current invocation chain: `2026-08-28T0315JST.md` -> `2026-08-28T0212JST.md` -> `2026-08-28T0102JST.md` -> `2026-08-28T0044JST.md` -> `2026-08-28T0002JST.md` -> `2026-08-27T2307JST.md` -> `2026-08-27T2240JST.md` -> `2026-08-27T2223JST.md` -> `2026-08-27T2215JST.md` -> `2026-08-27T2206JST.md` -> `2026-08-27T2111JST.md` -> `2026-08-27T2010JST.md` -> `2026-08-27T1909JST.md` -> `2026-08-27T1815JST.md` -> `2026-08-27T1811JST.md` -> `2026-08-27T1805JST.md` -> `2026-08-27T1705JST.md` -> `2026-08-27T1606JST.md`
Earlier predecessor chain remains in immutable checkpoint history; read only the minimum needed for unresolved-frontier continuity.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T03:01:18+09:00`; newest checkpoint observation: `2026-08-28T03:15:04+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `5dca371ce05e08e12442c6e08449caab1975587d`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. Later note-main advances caused by this role-local write sequence were not adopted as new semantic control.

## Top unresolved frontier

1. Build a width/pathology matrix for the boundary CNF using structures with known hard monotone-CNF embeddings; compare fixed orders, standard BDD reordering heuristics, and live-node/cache growth. Distinguish final OBDD lower bounds from intermediate compilation-order blowups.
2. Add an exact escape policy: persistent one-clause update versus periodic balanced/non-incremental recompilation versus a more structured representation. Preserve exact cardinality-by-rank counts and measure live nodes, dead nodes, Apply work, memory and wall-clock separately.
3. Investigate TDD/structured-d-DNNF/ZDD/ADD implementations for cardinality-by-rank counting; do not assume ordinary model-count support is enough.
4. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains the only promotion/demotion authority.
5. Replay `result-graph` against `descriptive-complexity@bce9facd412c380dda06459a06769e73876f7203` when a compatible Lean/runtime transfer path exists; require exact statement/proof direct-edge parity before upgrading provenance.
6. Execute C263 through the full `StructuredController` path when exact source-to-runtime transfer is available; then compare immutable proposal-batch consumption edges.
7. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass.
8. Materialize pinned OPA and Regorus and run frozen deterministic Rego Tier-0 fixtures before seeded generation.
9. Extend source-qualified Lean proof-use evidence while keeping statement/proof, explicit tactic, synthesized/elaboration, retrieval exposure, support membership, and causal utility separate.
10. Upgrade Isabelle minimized-support evidence with exact candidate-universe replay and multiple alternative supports under frozen prover/budget conditions.
11. The unintended prior branch may be cleaned only through an explicitly authorized control-plane path; no discovery/probe mutations.

## Newest synthesis

- **C562:** one new informative observation has an exact antichain-local update. A non-dominated upper-slice zero replaces only maximal zeroes it contains; a non-dominated lower-slice one replaces only minimal ones containing it. The new boundary clause subsumes every logically removed weaker clause, so a persistent diagram can safely conjoin only the new stronger clause.
- **C563:** preregistered holdout over 12 unseen cells (`n=10/14/18`) processed **2,537 effective updates with zero correctness mismatches** against a fresh rebuild after every effective observation. Median total speedups in the current Python runtime were `4.19× / 10.23× / 20.85×`; timing is descriptive, not asymptotic. Persistent rank memoization recomputed median `8.5 / 20.5 / 54.5` states per update versus median live diagrams `48.5 / 370 / 2697.5` nodes.
- **C564:** any subsumption-minimal positive monotone CNF embeds exactly into the boundary family via clause `S -> Z=U\\S`, with `A1_min=empty`. A generated implementation check covered **8,000** random clause families / **510,000** truth assignments with zero mismatch. Therefore known exponential OBDD/pathwidth lower bounds for monotone CNF transfer directly to a subset of this boundary family.
- **C565:** SAT 2023 proves a separate worst-case hazard: some CNFs have polynomial non-incremental bottom-up compilations but every clause-at-a-time incremental core becomes exponential. Persistent update must therefore retain a rebuild/recompile escape action rather than being universal policy.
- **C566:** 2026 Tree Decision Diagrams provide a more succinct OBDD generalization with FPT-size representation for treewidth-bounded CNFs where OBDD lacks such a guarantee. Rank-distribution counting on TDDs remains unvalidated here.
- **C567:** the current pure-Python manager does not garbage-collect unreachable historical nodes; production BDD packages such as CUDD do. Prototype allocated-node counts must not be interpreted as inherent live-memory requirements.
- Durable outputs: `experiments/coalition_incremental_boundary_holdout_v0_protocol.json`, `experiments/coalition_incremental_boundary_holdout_v0.py`, `experiments/coalition_incremental_boundary_holdout_v0_results.json`, `experiments/coalition_boundary_monotone_cnf_embedding_v0.py`, `experiments/coalition_boundary_monotone_cnf_embedding_v0_results.json`.
- Scope guard: real finite-compute proof utility can be nonmonotone; this certifier remains advisory and does not authorize global lemma-library promotion/demotion.

## Exact continuation

1. Turn C564/C565 into a frozen pathology/recompilation experiment and identify measurable switch signals for representation/order/rebuild actions.
2. Test true BDD/ZDD/TDD/d-DNNF-style implementations and variable-order heuristics while preserving exact rank counts.
3. Run the preregistered lemma-library policy matrix unchanged.
4. Run `result-graph` replay, C263 full-controller reproduction, and OPA/Regorus frozen fixtures when compatible runtimes become available.
5. Keep safety/evidence channels separate and the frontier nonempty; this is not global completion.

`2026-08-28T0315JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
