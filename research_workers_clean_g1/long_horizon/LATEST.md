# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T000150JST_RETIREMENT_SENSOR_RELIABILITY_AND_DERIVED_MEMORY_ERASURE.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T230122JST_CAUSAL_MEMORY_CREDIT_AND_CONTRACT_PRESERVATION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `ac9400d54c8766a5bf61bd87fd6dcac75a1f46cb`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository changes were not adopted as semantic control.

Current synthesis delta:
- Ratchet v3 shows post-admission retirement can become actively harmful when its evidence floor is too small: its harsh-retirement ablation falls below the no-skill floor, while the default evidence floor/threshold yields strong positive rolling gain on the tested MBPP+ stream.
- Ratchet's judge-channel analysis separates false-pass from phantom-failure errors: false-pass bias can make threshold retirement incapable of evicting bad artifacts no matter how many samples are collected, so destructive maintenance needs evaluator-channel certification rather than more data by default.
- More governance is not automatically better: explicit dedup filters are not load-bearing at the tested scale when a strong authoring prior is present, and frequent meta-skill refresh adds 55% wall time for only marginal/noisy gain.
- Deployment-Time Memorization directly shows deletion-residue through derived memory tiers: raw-only deletion leaves summary-derived copies recoverable around 20%, re-summarization reduces but does not eliminate residue, and full-pipeline purge/tombstone drives worst-tier residue to zero in the evaluated settings.
- Therefore lifecycle governance now needs both `retirement-sensor validity` and `revocation closure across derived holders`; source-row deletion or retirement is not a completion criterion.
- MemLineage corroborates that derivation lineage can be persisted across sessions, but a semantically transformed descendant-retirement experiment remains missing.

Exact continuation:
1. Keep searching for a direct 2x2 or richer factorial crossing pre-commit admission gating with post-admission maintenance on the same stream under size/compute-matched controls.
2. Find an explicit semantic-descendant experiment: contaminate a reusable skill/memory, synthesize descendants, retire/delete/tombstone the ancestor, and measure descendant retrieval plus behavioral harm.
3. Find maintenance controllers that certify evaluator error channels or use anytime-valid evidence before destructive retire/repair, especially software/API agents with deterministic-validator controls.
4. Find a maintenance-only ablation for typed procedural contracts in real software/API agents, separating retrieval/representation/hydration from longitudinal repair/retire.
5. Find a live closed-loop software/tool/GUI experiment where the recovery actuator is fixed and only confidence/memory evidence or intervention selector changes; require final task success and disruption of originally successful trajectories.
6. Continue historical rollback-target-selector comparisons with matched recovery budgets, realized recovery dose, state-integrity controls and abstention.
7. Preserve all scope guards and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
