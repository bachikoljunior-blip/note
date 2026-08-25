# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0558JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot used by the latest semantic run:
- root control revision: `8`
- role config revision: `5`
- frozen source main SHA: `5478ae1096aa60c44b78a4fb397b2de450e8f09d`
- root blob: `508c9f92dd965d2b5074932b99847411cb66bef4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

Current synthesis delta:
- Failure detection quality and intervention utility must be separated. For the tested critic/interventions, expected gain follows `p*r - (1-p)*d`; high-AUROC critics can still reduce final success when disruption of would-be-successful trajectories dominates recovery.
- Deployment calibration matters: one real-time monitor reports cold-transfer AUROC `0.527` vs recalibrated `0.885`, while its closed-loop rollback/rerun improves failure recovery `16% -> 45%` against resampling and task success `52% -> 73%` in the tested setup.
- Recovery mechanism and carry-forward policy are independent variables: RestartSmart reports SWE-bench Verified `66.6% -> 71.8%`, whereas cold restart reaches `66.8%`; selected durable artifacts can be useful even when stale reasoning history is cleared.
- Local checkpoint restore does not imply global effect rollback. ACRFence's proof-of-concept reports duplicate irreversible commits in `10/10` restore trials vs `0/10` without restore. Atomix shows that checkpoint replay can tie transactional execution on pure task recovery while irreversible-effect settlement remains a distinct safety dimension.
- A safe long-horizon recovery stack therefore needs separate detector, intervention-decision, cut-point, historical-target, carry-forward, local-restore, external-effect settlement, commit-time revalidation, and repair-stopping controls.

Exact continuation:
1. Primary-verify full Fail-Fast/RestartSmart tables/code for false-positive disruption and safe cut-point details.
2. Extract Atomix RQ3/combined-stress primary tables and exact effect-safety counts.
3. Search matched factorial studies that isolate detector quality from recovery mechanism.
4. Preserve unresolved checkpoint-target-selection and subgoal/folding-negative-evidence branches.

This pointer does not supersede exact source/tested-scope guards in the checkpoint. Future runs should read this pointer first, then only the minimum predecessor material required for unresolved frontier continuity.
