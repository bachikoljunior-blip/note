# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0516JST.md`
Current invocation chain: `2026-08-28T0516JST.md` -> `2026-08-28T0416JST.md` -> `2026-08-28T0407JST.md` -> `2026-08-28T0315JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T04:58:04+09:00`; newest checkpoint observation: `2026-08-28T05:16:15.748673+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `79ca1416ce33c2b73f74f41ef284a6e4168bce32`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. Later note-main advances caused by role-local writes were not adopted as new semantic control.

## Top unresolved frontier

1. Preserve `experiments/coalition_boundary_order_portfolio_holdout_v0_protocol.json` unchanged and execute the n=20 unseen-family transfer matrix in a runtime path that completes it. The attempted run hit the Python hard timeout; no partial output is evidence. If a smaller follow-up is needed, preregister a new protocol and new untouched families rather than altering this holdout.
2. Define a new held-out order-start experiment inspired by BDD2Seq/LEO: fixed RCM vs charged diverse portfolio vs cheap learned/structural start predictor. Freeze train/test split and charge predictor/search overhead; do not use BDD2Seq/LEO domain results as direct certifier evidence.
3. Rebuild control: keep larger V0 incomplete. V1 showed `periodic_32` exact on 1,083 effective updates, lower max allocation/live in 12/12 cells, and only 30 rebuilds; absolute `ratio>=4` was over-triggered. Test triggers relative to the last fresh baseline, allocation-growth, live-growth and Apply/cache growth under new seeds/sizes.
4. Scale the exact `N[z]/(z^(n+1))` rank-polynomial prototype from four tiny smooth deterministic decomposable circuits to shared d-DNNF/TDD-like structures and preregister node/operation comparisons against ROBDD. Keep looking for a materializable TiDiDi/TDD implementation.
5. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains the only promotion/demotion authority.
6. Replay `result-graph` against `descriptive-complexity@bce9facd412c380dda06459a06769e73876f7203` when a compatible Lean/runtime transfer path exists; require exact statement/proof direct-edge parity before upgrading provenance.
7. Execute C263 through the full `StructuredController` path when exact source-to-runtime transfer is available; helper-level evidence remains narrower.
8. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass.
9. Materialize pinned OPA and Regorus and run frozen deterministic Rego Tier-0 fixtures before seeded generation.
10. Keep statement/proof/tactic/synthesized/retrieval/support/causal evidence channels separate, and keep the frontier nonempty.
11. The unintended prior branch may be cleaned only through an explicitly authorized control-plane path; no discovery/probe mutations.

## Newest synthesis

- **C579:** a preregistered charged three-start controller (`natural / RCM / seeded-diverse`, one local stage then commit) used 6,655 candidate compilations vs 8,600 for fully searching natural+RCM, **22.62% less**, with equal final live nodes on 4/5 development families and better on 1/5. On `cubic18_s880319`, seeded was already best after one stage (133 vs RCM 134 vs natural 176) and reached **105** live nodes vs natural 107 / RCM 111.
- **C580:** diversity is conditional, not a free win. The seeded arm was poor on several families; the simpler two-arm early-commit controller was 37.79% cheaper than full two-arm but committed to the wrong conventional start on `cubic18_s880319` and ended at 111 vs 107. The untouched n=20 transfer protocol was frozen, but its current run timed out; no partial result is used.
- **C581:** smaller preregistered rebuild-controller V1 completed 12 new cells / **1,083 effective updates** with zero exact-rank mismatches. `periodic_32` reduced max allocated/live and max current allocations in 12/12 cells, used 30 rebuilds, and had 5.54% lower summed strategy time descriptively. `ratio>=4` rebuilt 532 times and was poorly selective because fresh managers could already exceed that absolute ratio.
- **C582:** independent smooth deterministic decomposable-circuit semiring prototype reproduced exact Hamming-weight/rank counts on all four preregistered cells: `[0,0,4,4,1]`, `[0,3,3,0,0]`, and path formula `[0,0,3,4,1]` under both natural/reverse decision-DAG orders. This validates algebraic feasibility, not TDD scaling.
- **C583:** external primary evidence converges on the same order-controller issue but in different domains. AAAI-26 BDD2Seq uses GNN+Pointer Network+Diverse Beam Search and its ablation shows diversity helps until beam width ~20 before runtime rises sharply; LEO reports black-box order-search overhead can outweigh downstream savings and uses supervised prediction to amortize it. These motivate charged learned/diverse-start experiments only.
- Durable new outputs: `experiments/coalition_boundary_order_portfolio_v0_protocol.json`, `..._results.json`, `coalition_incremental_rebuild_controller_v0_protocol.json` (incomplete), `..._v1_protocol.json`, `..._v1_results.json`, `coalition_rank_polynomial_circuit_v0_protocol.json`, `..._results.json`, `coalition_boundary_order_portfolio_holdout_v0_protocol.json` (preregistered/incomplete).
- Scope guard: real finite-compute proof utility may be nonmonotone; none of this authorizes global lemma-library promotion/demotion.

## Exact continuation

1. Execute the frozen unseen-family portfolio holdout in a compatible runtime; do not reuse timed-out partial state.
2. Preregister a learned/structural start predictor vs fixed/portfolio comparison with all prediction/search cost charged.
3. Preregister a new rebuild-trigger holdout using relative-to-fresh growth features, with `periodic_32` as baseline and exact rank parity as hard oracle.
4. Expand rank-polynomial circuits and locate/materialize a real TDD implementation.
5. Run the frozen lemma-library matrix, `result-graph` replay, C263 full-controller reproduction and OPA/Regorus fixtures when their substrates become available.
6. Keep safety/evidence channels separate and the frontier nonempty; this is not global completion.

`2026-08-28T0516JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
