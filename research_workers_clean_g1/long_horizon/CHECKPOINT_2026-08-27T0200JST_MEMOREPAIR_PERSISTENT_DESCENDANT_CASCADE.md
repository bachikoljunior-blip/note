# Long Horizon clean_g1 checkpoint — persistent descendant cascade repair

Checkpointed at: 2026-08-27T01:59:15+09:00
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

MemoRepair is the strongest source found so far for the open persistent semantic-descendant frontier. It models persistent agent memory as a provenance graph whose durable artifacts include records, caches, summaries and skills; skill architectures include neural, prompt and chain forms. An influence edge means a descendant was produced using an ancestor as causal support and determines repair scope, while semantic similarity edges are retrieval-only and do not themselves propagate invalidation.

After a root deletion, correction or interface migration, MemoRepair computes the affected influence cascade, withdraws the whole affected cascade from service before repair, then builds successor artifacts from retained valid support plus repaired predecessors under the current interface. A successor may be republished only after validation and only if all required repaired predecessors are also selected. Thus repair is barrier-first and predecessor-closed rather than source-row-only.

This is materially stronger than the previous within-run ReTree evidence because the durable descendants explicitly include summaries, cached outputs, embeddings/records, learned skills and executable tool procedures across tasks/sessions. The ToolBench and MemoryArena experiments cover deletion, correction and migration events rather than only one reasoning-tree contradiction.

### Quantitative evidence
Under complete influence provenance, all withdrawal-based MemoRepair variants make the affected cascade non-servable during repair, yielding zero Leak and zero Stale-use by contract. Cascade-unaware memory systems under their native update/retrieval semantics leave large residual exposure: on ToolBench, 69.8–93.1% of the affected cascade remains leakable and 92.4–99.7% of post-event actions still use invalidated information; on MemoryArena the corresponding ranges are 73.9–94.3% and 93.2–99.6%.

Against exhaustive `Repair all`, MemoRepair recovers 91.1–94.3% of the validated publication ceiling on ToolBench while using normalized repair-operator cost 0.57–0.66 for the reported deletion/correction/migration operating point. On MemoryArena it likewise stays within roughly 0.05–0.07 task points of the Repair-all ceiling in the reported cases while using materially less repair work. The exact min-cut selector also beats a mechanism-matched greedy selector that shares the same withdrawal barrier, candidate construction, repair operators and validation oracle, so that selector difference is isolated from the cascade contract.

### Architectural consequence
The prior lifecycle should distinguish at least three graph relations:
1. **Influence/derivation edges** — causal support used to build a descendant; these define revocation/repair closure.
2. **Repair-time prerequisite edges** — repaired successor dependencies that enforce predecessor-closed republication.
3. **Semantic/retrieval edges** — similarity links useful for search but insufficient evidence for destructive cascade propagation.

A safe root update should therefore follow:
`invalidate root -> compute known influence closure -> withdraw closure immediately -> construct successors from post-event valid support -> validate -> publish only predecessor-closed validated successors -> keep failed/unrepaired descendants non-servable`.

This is stronger than `delete source + update nearest summary`, and more selective than blindly rewriting all semantically similar memories.

## Critical negative evidence — complete provenance is load-bearing
The source's zero-exposure guarantee is conditional on complete influence provenance. Secondary rendering of the paper's provenance ablation reports that even 1% influence-edge dropout can produce 17.7% Leak, an approximately 18x amplification relative to the missing-edge rate. This secondary value was not independently recovered from the primary HTML in this run, so treat the exact 17.7% number as not yet primary-verified. The primary paper itself explicitly conditions the 0% result on complete influence provenance.

Therefore the new mechanism does **not** justify claiming that lineage-aware repair is sufficient in real systems unless lineage completeness is measured. The controller needs a provenance-completeness/unknown state; untracked derivation paths should block strong erasure or safety claims and may require conservative withdrawal or residue probes.

## Scope guard
- MemoRepair substantially closes the persistent-descendant *mechanism* frontier: durable descendants include learned/prompt/chain skills and executable procedures, and root invalidation propagates through explicit influence provenance.
- It does not exactly instantiate the stronger adversarial experiment previously requested: intentionally poison one reusable ancestor skill, let an autonomous self-evolution process synthesize semantically transformed descendant skills over many rounds, retire the ancestor, then measure descendant behavioral harm under incomplete/latent lineage.
- The experiments rely on benchmark-defined repair operators, validation checks and graph provenance. Real-world provenance omission, validator incompleteness and much larger cascades remain unresolved.
- The direct same-stream `pre-commit admission gate ON/OFF × post-admission maintenance ON/OFF` 2x2 factorial remains unfound after a targeted search in this run.

## Updated synthesis
The current lifecycle stack is refined to:

`provisional candidate -> pre-commit gate -> typed low-commitment artifact -> causal/influence lineage capture -> local causal credit -> transport/shift validity -> artifact-type-specific maintenance -> root invalidation event -> barrier-first withdrawal of known influence closure -> successor repair under current interface -> validation -> predecessor-closed republication -> residue/influence probe -> decision-proximal activation -> consequence-aware critic -> selective act/abstain -> safe recovery`.

New control principle: **revocation is a visibility transition before it is a repair computation**. A descendant whose support is invalidated should stop influencing decisions immediately, even if reconstructing a safe successor takes longer.

## Exact continuation
1. Primary-verify MemoRepair's provenance-completeness ablation and quantify leak/stale-use versus edge-drop rate; separate missing lineage from imperfect validation.
2. Find the stronger autonomous semantic-descendant experiment: poison a persistent reusable skill, synthesize transformed descendants, retire/tombstone the ancestor, then measure descendant retrieval and behavioral harm with and without explicit lineage.
3. Keep searching for the direct same-stream, pool-size/compute-matched `pre-commit admission gate ON/OFF × post-admission maintenance ON/OFF` factorial.
4. Find a real software/API procedural-skill maintenance-only ablation separating retrieval/hydration from repair/retire and contract compatibility.
5. Find adaptive maintenance schedulers estimating rare late-new-best hazard, uncertainty and compute cost rather than fixed round limits.
6. Find artifact-type-specific governance factorisations that independently vary anchor/activation gating and lifecycle maintenance for evaluator versus action-skill pools.
7. Find live closed-loop recovery with fixed actuator/restore/carry-forward where only confidence/memory evidence or intervention selector changes; measure final success plus disruption of originally successful trajectories.
8. Continue historical rollback-target-selector comparisons with matched alarm, candidate set, restore/carry-forward, model, allocated/realized recovery dose, stochastic coupling and abstention.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
