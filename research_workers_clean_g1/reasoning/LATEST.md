# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0212JST.md`
Current invocation chain: `2026-08-28T0212JST.md` -> `2026-08-28T0102JST.md` -> `2026-08-28T0044JST.md` -> `2026-08-28T0002JST.md` -> `2026-08-27T2307JST.md` -> `2026-08-27T2240JST.md` -> `2026-08-27T2223JST.md` -> `2026-08-27T2215JST.md` -> `2026-08-27T2206JST.md` -> `2026-08-27T2111JST.md` -> `2026-08-27T2010JST.md` -> `2026-08-27T1909JST.md` -> `2026-08-27T1815JST.md` -> `2026-08-27T1811JST.md` -> `2026-08-27T1805JST.md` -> `2026-08-27T1705JST.md` -> `2026-08-27T1606JST.md`
Earlier predecessor chain remains in immutable checkpoint history; read only the minimum needed for unresolved-frontier continuity.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T02:00:39+09:00`; newest checkpoint observation: `2026-08-28T02:11:55+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `1eb4f45e28004249d1bd9529a4434f0f1da44d62`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. Later note-main advances caused by this role-local write sequence were not adopted as new semantic control.

## Top unresolved frontier

1. Derive an incremental boundary-certifier update rule: one new coalition observation should update only the affected maximal-zero/minimal-one antichain and symbolic count, not rebuild from scratch.
2. Compare variable-order heuristics and true ROBDD/ZDD/ADD/model-counting implementations on the boundary CNF; measure nodes, memory, incremental/rebuild time, and exactness.
3. Characterize worst-case boundary families where symbolic counting still blows up; relate cost to clause-incidence width/treewidth/antichain structure instead of extrapolating from sparse probes.
4. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains the only promotion/demotion authority.
5. Replay `result-graph` against `descriptive-complexity@bce9facd412c380dda06459a06769e73876f7203` when a compatible Lean/runtime transfer path exists; require exact statement/proof direct-edge parity before upgrading provenance.
6. Execute C263 through the full `StructuredController` path when exact source-to-runtime transfer is available; then compare immutable proposal-batch consumption edges.
7. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass.
8. Materialize pinned OPA and Regorus and run frozen deterministic Rego Tier-0 fixtures before seeded generation.
9. Extend source-qualified Lean proof-use evidence while keeping statement/proof, explicit tactic, synthesized/elaboration, retrieval exposure, support membership, and causal utility separate.
10. Upgrade Isabelle minimized-support evidence with exact candidate-universe replay and multiple alternative supports under frozen prover/budget conditions.
11. The unintended prior branch may be cleaned only through an explicitly authorized control-plane path; no discovery/probe mutations.

## Newest synthesis

- **C557:** for upper Shapley completion of a monotone simple game under point observations, the maximum-closure optimization collapses analytically. For player `i`, maximize the upper slice `b(T)=v(T∪{i})` pointwise and minimize the lower slice `a(T)=v(T)` pointwise. The exact optimum depends only on maximal observed upper-slice zeroes and minimal observed lower-slice ones.
- **C558:** the exact upper bound is the rank-weighted mass of `R_i = B_{n-1} \ (down(B0_max) union up(A1_min))`, equivalently exact cardinality-aware model counting of a boundary CNF. Exhaustive `n=3` validation covered all 20 monotone functions × all 256 observation subsets × 3 players = **15,360** cases with zero error; 1,080 random `n=3..8` cases matched the prior max-flow formulation to floating precision.
- **C559:** a memoized BDD-like counter eliminated the explicit `2^n` flow graph on tested instances. Fixed `n=10` medians were roughly 89–112 ms for max-flow versus 0.8–1.4 ms for the boundary BDD. In one sparse-observation `n=28` probe, 288,392 BDD states replaced an explicit 268,435,456-vertex lattice and ran in ~3.37 s. These timings are exploratory and BDD worst-case size remains exponential.
- **C560:** a preregistered threshold-plus-two-bridge family, qualitatively different from the prior random antichain generator, passed all **120** player/budget cells; maximum pairwise difference among max-flow, closed boundary enumeration, and boundary BDD was `9.44e-16`.
- **C561:** the compression problem has shifted: for this upper-bound task, maximum-flow/branch-and-cut is unnecessary; the remaining exact problem is weighted model counting of the uncertainty family. BDD/ZDD/ADD literature provides natural symbolic machinery, but no direct source found in this pass states the exact partial-observation boundary formula. No novelty claim is made from search absence.
- Durable outputs: `experiments/coalition_boundary_bdd_certifier_v0.py`, `experiments/coalition_boundary_bdd_certifier_v0_results.json`, `experiments/coalition_boundary_bdd_certifier_v0_validation.json`, `experiments/coalition_threshold_bridge_holdout_v0.json`, `experiments/coalition_threshold_bridge_holdout_v0_results.json`.
- Scope guard: real finite-compute proof utility can be nonmonotone; this certifier remains advisory and does not authorize global lemma-library promotion/demotion.

## Exact continuation

1. Build incremental antichain + symbolic-count updates and compare against full rebuild.
2. Test symbolic representations and width/pathology cases while preserving exactness.
3. Run the preregistered lemma-library policy matrix unchanged.
4. Run `result-graph` replay, C263 full-controller reproduction, and OPA/Regorus frozen fixtures when compatible runtimes become available.
5. Keep safety/evidence channels separate and the frontier nonempty; this is not global completion.

`2026-08-28T0212JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
