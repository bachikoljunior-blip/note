# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T010235JST_DEPENDENCY_REPAIR_AND_SPARSE_SKILL_EVOLUTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T000150JST_RETIREMENT_SENSOR_RELIABILITY_AND_DERIVED_MEMORY_ERASURE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `91e54d08ef70f398c1232e92936e5a36086b1ad9`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository changes were not adopted as semantic control.

Current synthesis delta:
- ReTree provides a mechanism-matched descendant-repair control: replacing a refuted ancestor plus dependency-directed descendant pruning beats ancestor-only FlatUpdate by 2.2–4.7 pp across four search datasets. This partially closes the semantic-descendant frontier for within-run reasoning state, but not for persistent semantically transformed skills.
- Persistent skill evolution is sparse and non-monotonic: only 55/388 candidates became new validation bests; 38/55 appeared in rounds 1–4, yet 6/11 final selected evolved skills first appeared in rounds 6–9. Fixed early cutoff is therefore unsafe even though marginal yield decays.
- Failure-containing revision feedback is generally more productive in the primary skill-evolution study, but positive-only wins in an extended setting prevent a universal failures-only rule. Evidence role should be classified rather than hard-coded.
- SpreadsheetBench shows persistent procedural revision can produce gains not replaced by extra parent sampling: 50.53 parent vs 85.77 evolved vs 54.80 oracle-parallel. Conversely validation improvement can reverse on released test, so deployment/transfer checks remain distinct.
- Memory maintenance should minimize propagation outside the proven dependency closure; conversational-memory ablations favor conservative consolidation over delayed flush/coarse summary in the tested setting.
- Evaluator pools and action skills require different governance. In the metric co-evolution study, removing anchor guards collapses into vacuous always-pass behavior while removing evaluator lifecycle does not; activation/anchor validity can dominate evaluator retirement.
- Direct matched `admission gate ON/OFF × post-admission maintenance ON/OFF` factorial remains unfound.

Exact continuation:
1. Find the direct same-stream admission-gate × maintenance factorial under matched pool size/compute.
2. Find an explicit persistent semantic-descendant experiment: contaminate ancestor skill/memory, synthesize descendants, retire ancestor, measure descendant retrieval and behavioral harm. ReTree covers only within-run dependency descendants.
3. Find a real software/API procedural-skill maintenance-only ablation separating retrieval/hydration from repair/retire and contract compatibility.
4. Find adaptive maintenance schedulers estimating rare late-new-best hazard, uncertainty and compute cost rather than using fixed round limits.
5. Find factorisations that independently vary anchor/activation gating and lifecycle maintenance for evaluator versus action-skill pools.
6. Find live closed-loop recovery with fixed actuator/restore/carry-forward where only confidence/memory evidence or intervention selector changes; measure final success plus disruption of originally successful trajectories.
7. Continue historical rollback-target-selector comparisons with matched alarm, candidate set, restore/carry-forward, model, allocated/realized recovery dose, stochastic coupling and abstention.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
