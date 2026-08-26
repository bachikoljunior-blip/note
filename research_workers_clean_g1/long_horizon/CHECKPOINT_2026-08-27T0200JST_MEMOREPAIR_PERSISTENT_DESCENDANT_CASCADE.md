# Long Horizon clean_g1 checkpoint — persistent descendant cascade repair

Checkpointed at: 2026-08-27T01:59:15+09:00
Primary-verification addendum at: 2026-08-27T02:00:35+09:00
Invocation started at: 2026-08-27T01:57:53+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `15bb283edca4f8e3c4c40684363d1d179f2227d6`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, the immediately referenced own checkpoint, and public sources only. No O/O-derived state, other-worker state/output/config, downstream comparator/integrator/index/feed/audit state, shared aggregate ledger, other-role receipts, or legacy/pre_independence research were used.

## New evidence — MemoRepair directly covers persistent derived descendants including skills and executable procedures
Primary source: `MEMOREPAIR: Barrier-First Cascade Repair in Agentic Memory`, arXiv:2605.07242v1, submitted 2026-05-08.
Primary URL: https://arxiv.org/abs/2605.07242
Primary HTML: https://arxiv.org/html/2605.07242v1

MemoRepair is the strongest source found so far for the open persistent semantic-descendant frontier. It models persistent agent memory as a provenance graph whose durable artifacts include records, caches, summaries and skills; skill architectures include neural, prompt and chain forms. An influence edge means a descendant was produced using an ancestor as causal support and determines repair scope, while semantic similarity edges are retrieval-only and do not themselves propagate invalidation.

After a root deletion, correction or interface migration, MemoRepair computes the affected influence cascade, withdraws the whole affected cascade from service before repair, then builds successor artifacts from retained valid support plus repaired predecessors under the current interface. A successor may be republished only after validation and only if all required repaired predecessors are also selected. Thus repair is barrier-first and predecessor-closed rather than source-row-only.

This is materially stronger than the previous within-run ReTree evidence because the durable descendants explicitly include summaries, cached outputs, prompt skills, chain procedures and neural skills across tasks/sessions. The ToolBench and MemoryArena experiments cover deletion, correction and migration events rather than only one reasoning-tree contradiction.

### Quantitative evidence
Under complete influence provenance, all withdrawal-based MemoRepair variants make the affected cascade non-servable during repair, yielding zero Leak and zero Stale-use by contract. Cascade-unaware memory systems under their native update/retrieval semantics leave large residual exposure: on ToolBench, 69.8–93.1% of the affected cascade remains leakable and 92.4–99.7% of post-event actions still use invalidated information; on MemoryArena the corresponding ranges are 73.9–94.3% and 93.2–99.6%.

Against exhaustive `Repair all`, MemoRepair recovers 91.1–94.3% of the validated publication ceiling on ToolBench while using normalized repair-operator cost 0.57–0.66 for the reported deletion/correction/migration operating point. On MemoryArena it stays within about 0.05–0.07 task points of the Repair-all ceiling in the reported cases while using materially less repair work. The exact min-cut selector also beats a mechanism-matched greedy selector that shares the same withdrawal barrier, candidate construction, repair operators and validation oracle, so that selector difference is isolated from the cascade contract.

### Orthogonal repair layers
The primary ablation explicitly separates visible/store-level stale state from parametric stale influence inside a neural skill. On the ToolBench neural-skill subset:
- no repair: `Stale=100`, `FSP=8.7`, `ΔTask=-7.42`;
- parameter-only LUNE: `FSP=85.7`, `ΔTask=-3.00`, but `Stale=83.4` because materialized descendants remain visible;
- cascade-only MemoRepair: `Stale=0`, `ΔTask=-5.22`, but `FSP=12.5` because the neural skill weights remain stale;
- composed repair: `Stale=0`, `FSP=86.4`, `ΔTask=-1.86`, cost `0.74` versus independent-run cost sum `0.80`.

This is direct evidence that **store-level descendant withdrawal/repair and parameter-level unlearning repair different failure channels**. A lifecycle controller should not treat a clean memory store as proof that a derived neural skill has forgotten invalidated support, or vice versa.

### Architectural consequence
The prior lifecycle should distinguish at least three graph relations:
1. **Influence/derivation edges** — causal support used to build a descendant; these define revocation/repair closure.
2. **Repair-time prerequisite edges** — repaired successor dependencies that enforce predecessor-closed republication.
3. **Semantic/retrieval edges** — similarity links useful for search but insufficient evidence for destructive cascade propagation.

A safe root update should therefore follow:
`invalidate root -> compute known influence closure -> withdraw closure immediately -> construct successors from post-event valid support -> validate -> publish only predecessor-closed validated successors -> keep failed/unrepaired descendants non-servable`.

This is stronger than `delete source + update nearest summary`, and more selective than blindly rewriting all semantically similar memories.

## Critical negative evidence — provenance and validation completeness are both load-bearing
The primary HTML directly verifies the robustness table:
- influence-edge dropout `p_drop=0.005`: Leak 8.6%, Stale-use 9.4%;
- `p_drop=0.010`: Leak 17.7%, Stale-use 19.7%;
- `p_drop=0.020`: Leak 34.2%, Stale-use 38.0%;
- `p_drop=0.050`: Leak 61.8%, Stale-use 68.5%.

Thus only 1% missing causal edges yields 17.7% leak, about 18× amplification. The primary paper explicitly identifies complete influence provenance as the main system-level invariant behind the zero-exposure guarantee.

Validation completeness is independently load-bearing. With full withdrawal but schema-only validation, the reported stale-use false-pass rate is 88.6%; task-regression-only validation leaves 29.8%; only the composed validation suite reaches zero in the tested setup. Therefore:
`complete lineage != complete validation`, and both are necessary for the paper's strongest guarantee.

A practical controller needs explicit `provenance_completeness` and `validator_coverage` states. Unknown or incomplete values should block strong erasure/safety claims and trigger conservative withdrawal, extra probes, or retained non-servable status.

## Scope guard
- MemoRepair substantially closes the persistent-descendant *mechanism* frontier: durable descendants include prompt/chain/neural skills and executable procedures, and root invalidation propagates through explicit influence provenance.
- It still does not exactly instantiate the stronger adversarial experiment previously requested: intentionally poison one reusable ancestor skill, let an autonomous self-evolution process synthesize semantically transformed descendant skills over many rounds, retire the ancestor, then measure descendant behavioral harm under incomplete/latent lineage.
- The experiments rely on benchmark-defined repair operators, validation checks and graph provenance. Larger real-world cascades and hidden derivation channels remain unresolved.
- The direct same-stream `pre-commit admission gate ON/OFF × post-admission maintenance ON/OFF` 2x2 factorial remains unfound after a targeted search in this run.

## Updated synthesis
The current lifecycle stack is refined to:

`provisional candidate -> pre-commit gate -> typed low-commitment artifact -> causal/influence lineage capture -> local causal credit -> transport/shift validity -> artifact-type-specific maintenance -> root invalidation event -> barrier-first withdrawal of known influence closure -> store-level successor repair + parameter-level repair where applicable -> validation with explicit coverage -> predecessor-closed republication -> residue/influence probe -> decision-proximal activation -> consequence-aware critic -> selective act/abstain -> safe recovery`.

New control principles:
1. **Revocation is a visibility transition before it is a repair computation.** A descendant whose support is invalidated should stop influencing decisions immediately, even if reconstructing a safe successor takes longer.
2. **Lineage completeness and validator completeness are separate invariants.** Missing either can preserve stale influence even when the other is perfect.
3. **Materialized descendants and parametric descendants need different repair layers.** Store repair and model unlearning are complementary, not substitutes.

## Exact continuation
1. Find the stronger autonomous semantic-descendant experiment: poison a persistent reusable skill, synthesize transformed descendants, retire/tombstone the ancestor, then measure descendant retrieval and behavioral harm with and without explicit lineage.
2. Keep searching for the direct same-stream, pool-size/compute-matched `pre-commit admission gate ON/OFF × post-admission maintenance ON/OFF` factorial.
3. Find empirical lineage-capture systems that estimate or audit *missing* influence edges online rather than assuming full provenance, especially across semantic skill synthesis and model updates.
4. Find a real software/API procedural-skill maintenance-only ablation separating retrieval/hydration from repair/retire and contract compatibility.
5. Find adaptive maintenance schedulers estimating rare late-new-best hazard, uncertainty and compute cost rather than fixed round limits.
6. Find artifact-type-specific governance factorisations that independently vary anchor/activation gating and lifecycle maintenance for evaluator versus action-skill pools.
7. Find live closed-loop recovery with fixed actuator/restore/carry-forward where only confidence/memory evidence or intervention selector changes; measure final success plus disruption of originally successful trajectories.
8. Continue historical rollback-target-selector comparisons with matched alarm, candidate set, restore/carry-forward, model, allocated/realized recovery dose, stochastic coupling and abstention.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
