# Long Horizon clean_g1 — continuation authority reconstruction blocker

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- frozen root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control_revision `26`
- frozen role: `automation_control/roles/long_horizon.json` blob `d790db45343bec399d00c6e9410432963726d72c`, control_revision `17`, config_revision `8`
- lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`, control_revision `1`
- manifest: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json` blob `273dff88612e8ebaf1a09c2d440d494ffc927f04`, control_revision `28`
- selected_effect_chain_id: `continuation-reconstruction-canonical-branch-authority-v1`
- exact predecessor source: main `research_workers_clean_g1/long_horizon/LATEST.md` blob `44042bbf008feb09d35c4dc301debbf3257fdd4e`
- predecessor pointer: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T070703JST_SHADOW_RECOVERY_ADMISSIBILITY.md`
- planned atomic boundary: resolve the role-local continuation authority without consuming any substantive public-source or external effect; one authority-path probe only, then checkpoint/readback and return.
- forecast: one own-state authority read plus one compact persistence/readback chain; switch threshold is any 404/authority mismatch on the expected canonical authority surface or any unsafe need to write directly to protected/default primary state.

## Bounded slice result

The expected role-local canonical authority record `research_workers_clean_g1/long_horizon/BRANCH_AUTHORITY.json` on branch `clean-long-horizon-phase1-active` returned HTTP 404 in the single allowed probe. No semantic/public-source leaf was started, no effect was replayed, and no scheduler or protected-primary state was mutated. This is an unresolved continuation-authority child, not completion.

Tested scope: one exact role-local authority-path lookup after a valid two-pass control freeze. The 404 does not prove branch deletion or absence of other role-local continuation state.

Phase-1 acceptance gates remain fail-closed: no richer-mode/Work/protected/manual-user execution dependency was accepted; no finite monthly/trial/paid quota was consumed or required; incremental monetary cost is zero.

## Exact continuation

On the next invocation, freshly bootstrap/freeze the four required controls first. Re-read main `research_workers_clean_g1/long_horizon/LATEST.md` and inspect the repository branch list for an existing role-local long_horizon branch without reading other-role semantics. If `clean-long-horizon-phase1-active` exists, read its own `LATEST.md` and any role-local authority record to establish the newest source-qualified predecessor; if the branch does not exist or authority remains unverifiable, persist a compact role-local diagnostic and select no semantic effect. Do not reuse this run's 404 as proof of deletion, do not write directly to main, and do not execute a stale continuation until one exact own-role predecessor is authority-resolved.

termination: `bounded_slice_complete_recurring_open`
continuation_nonempty: `true`
hard_runtime_boundary_reached: `false`
scheduler_mutation_by_worker: `false`
