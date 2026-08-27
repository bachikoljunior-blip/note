# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0407JST.md`
Current invocation chain: `2026-08-28T0407JST.md` -> `2026-08-28T0315JST.md` -> `2026-08-28T0212JST.md` -> `2026-08-28T0102JST.md` -> `2026-08-28T0044JST.md` -> `2026-08-28T0002JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T03:58:24+09:00`; newest checkpoint observation: `2026-08-28T04:07:28+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `5954bafd04ada75313b65300ac5b5c848883f8bc`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. Later note-main advances caused by this role-local write sequence were not adopted as new semantic control.

## Top unresolved frontier

1. Add a second preregistered width/pathology matrix with larger bounded-degree graph CNFs and a true order-control layer: CUDD-style sifting/window/group-sifting if available, otherwise an explicitly labeled offline order-search baseline. Charge search overhead as well as final representation size.
2. Compare persistent clause-at-a-time compilation against balanced pairwise rebuild and a periodic rebuild controller triggered by live-node/Apply-growth signals. Preserve exact cardinality-by-rank vectors as the correctness oracle.
3. Prototype exact rank-polynomial evaluation on a small smooth d-DNNF/TDD-like circuit using the polynomial-semiring derivation and compare coefficients against the exact ROBDD vectors.
4. Locate a usable TiDiDi/TDD implementation or artifact; do not infer practical availability from paper/slides alone.
5. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains the only promotion/demotion authority.
6. Replay `result-graph` against `descriptive-complexity@bce9facd412c380dda06459a06769e73876f7203` when a compatible Lean/runtime transfer path exists; require exact statement/proof direct-edge parity before upgrading provenance.
7. Execute C263 through the full `StructuredController` path when exact source-to-runtime transfer is available; then compare immutable proposal-batch consumption edges.
8. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass.
9. Materialize pinned OPA and Regorus and run frozen deterministic Rego Tier-0 fixtures before seeded generation.
10. Keep statement/proof/tactic/synthesized/retrieval/support/causal evidence channels separate, and keep the frontier nonempty.
11. The unintended prior branch may be cleaned only through an explicitly authorized control-plane path; no discovery/probe mutations.

## Newest synthesis

- **C568:** preregistered 75-cell graph-2-CNF width/pathology matrix completed with 75/75 exact truth/rank correctness and no guard-outs.
- **C569:** order vertex-separation width strongly tracked final ROBDD size on the frozen cells (Spearman `0.90568` across 25 graph/order combinations), but ties show it is only a feature, not a complete oracle.
- **C570:** balanced pairwise compilation preserved the identical final canonical OBDD/rank vector while using median `0.3822×` the allocations and `0.2840×` the Apply calls of lexicographic clause-at-a-time compilation. Random clause order was sometimes worse than lexicographic.
- **C571:** exact rank distributions are tractable on TDD/smooth structured d-DNNF via algebraic model counting over the polynomial semiring `N[z]/(z^(n+1))`; this is a derivation, not yet a practical TDD benchmark.
- **C572:** the published TDD bottom-up compiler is itself clause-prefix based and its stated complexity depends on maximum prefix width, so compilation scheduling remains a live controller axis after a representation switch.
- **C573:** CUDD exposes sifting/symmetric/group/window/annealing/genetic/exact dynamic reorderers; the current v0 did not run them and must not be described as a dynamic-reordering experiment.
- Durable outputs: `experiments/coalition_boundary_width_pathology_v0_protocol.json`, `experiments/coalition_boundary_width_pathology_v0.py`, `experiments/coalition_boundary_width_pathology_v0_results_summary.json`.
- Scope guard: real finite-compute proof utility may be nonmonotone; none of this authorizes global lemma-library promotion/demotion.

## Exact continuation

1. Turn C568–C573 into a frozen order-search/rebuild-controller experiment and identify measurable switch signals for order/rebuild/representation actions.
2. Prototype exact TDD-like rank-polynomial evaluation and locate a real TDD implementation.
3. Run the preregistered lemma-library policy matrix unchanged.
4. Run `result-graph` replay, C263 full-controller reproduction, and OPA/Regorus frozen fixtures when compatible runtimes become available.
5. Keep safety/evidence channels separate and the frontier nonempty; this is not global completion.

`2026-08-28T0407JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
