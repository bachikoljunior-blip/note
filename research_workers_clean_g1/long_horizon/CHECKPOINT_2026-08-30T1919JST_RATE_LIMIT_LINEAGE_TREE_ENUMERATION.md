# Long Horizon Phase-1 preflight — rate-limit lineage enumeration

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-lineage-tree-enumeration-v1`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- frozen manifest: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json` rev8 blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`
- frozen lifecycle: `automation_control/RUN_LIFECYCLE.json` rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- frozen root: `automation_control/DESIRED_STATE.json` rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- frozen role: `automation_control/roles/long_horizon.json` control rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`
- enabled_desired: `true`
- canonical role branch: `clean-long-horizon-phase1-active`
- exact predecessor pointer: `research_workers_clean_g1/long_horizon/LATEST.md` blob `d56ee490a076e768b0c143031da88134a59607ed`
- predecessor frontier: `clean-rate-limit-lineage-tree-enumeration-v1`

Planned atomic boundary: perform exactly one bounded directory/tree enumeration restricted to `research_workers_clean_g1/long_horizon/` on `clean-long-horizon-phase1-active`. Locate a source-qualified `LIVE_RATE_LIMIT_STATE.json` or rate-limit lineage candidate. If one candidate is found, persist only its exact path/blob as the next predecessor and defer content reconstruction to a later invocation. If none is found or the listing is unavailable, persist the exact blocker. No content fetch of a candidate, no same-run retry, no second semantic leaf.

Forecast/switch threshold: one repository enumeration is the entire semantic leaf. Any need for a second enumeration, candidate-content fetch, retry, wait, or branch expansion triggers immediate checkpoint/return instead of expansion.

Acceptance/scope guards: residual richer-mode/protected/manual dependency=`none`; finite monthly/trial/paid quota dependency=`none`; incremental monetary cost=`0`; repository transport is state/evidence transport only, not compute.

Status: `preflight_persisted_pending_single_enumeration`.
