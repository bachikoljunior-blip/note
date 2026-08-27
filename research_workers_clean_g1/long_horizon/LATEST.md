# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T210918JST_SYMTRACE_FACTORIAL_AND_CONSTRUCTIVE_REVIEWER_CONTROL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T200450JST_SYMTRACE_CAUSAL_REPLAY_AND_SKILL_RELATION_CALIBRATION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen source main SHA: `71a3e80939bae63c40deb70aba60b44d797efd69`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched; later main movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- SymTrace's primary specification closes an implementation uncertainty: selective replay already accepts independent optional `target v_k` and `repair guidance Delta`. Therefore target-selection x guidance can be factorialized without changing the core prefix-reconstruction contract; the smallest expected change is RQ3 runner/prompt plumbing, pending public source-artifact readback.
- SymTrace's headline Suspicious-Node repair remains `20.15%` vs Random `3.73%`, Last `1.31%`, and unguided full rerun `6.90%` within three attempts, but target selection and evidence-conditioned guidance are jointly changed and must not be credited separately without the factorial.
- Failure-only SymFail is insufficient to measure intervention disruption of otherwise-successful trajectories; a matched successful/benign-prefix cohort is required for pass->fail/false-intervention measurement.
- COTA (arXiv:2608.21027) provides strong evidence that critic/selector quality and actuation are distinct. Same-prefix pairwise supervision plus non-binding actor replanning dominates forced takeover in long-horizon ALFWorld/tau3-Retail; explicit tie/abstain improves comparator behavior. Reviewer experiments should therefore separate diagnosis/selection, advice content, and forced vs constructive application.
- AgentTether provides paired persistence evidence on initially failed stateful tasks: Banking helped 13 / hurt 3, net +10, p=.021, while Airline is net zero. More interventions are associated with hurt cases, reinforcing rescue/disruption and over-control accounting.
- The exact single-admitted-update future-task ON/OFF frozen replay remains open.

Exact continuation:
1. Recover the public SymTrace source artifact through an accessible mirror/release and verify the actual `Replay(..., v, Delta)` path, prefix/hash assertions and RQ3 runner; determine whether empty/no-op `Delta` works directly. Read-only discovery only.
2. Search for an already-published same-prefix randomized reviewer/no-review experiment on replayable source failures; otherwise preserve the proposed SymTrace factorial as unexecuted.
3. Factor intervention application separately: no intervention / non-binding advice+actor replan / forced replacement, with explicit tie/abstain, while target/evidence/prefix/model/budget are matched.
4. Add an originally-successful/benign-prefix cohort to estimate pass->fail disruption and false intervention, not just rescue on failure-only SymFail.
5. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference/model/guidance/stochastic coupling/recovery budget.
6. Continue two-tier skill-relation evidence, exact per-update ON/OFF frozen-state reuse, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, common-replicate admission x maintenance factorial, hidden semantic lineage, post-consolidation re-externalization and decision-influence audits.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
