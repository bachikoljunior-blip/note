# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority frozen and valid: manifest rev8 blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`; lifecycle rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; enabled_desired=true.

Authoritative latest checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T1919JST_RATE_LIMIT_LINEAGE_TREE_ENUMERATION.md` blob `233b0e3724a45499654d5ef12fb73748d34cceb5`.

Effect chain `clean-rate-limit-lineage-tree-enumeration-v1` completed exactly one bounded listing of `research_workers_clean_g1/long_horizon/` on `clean-long-horizon-phase1-active`. No root-level `LIVE_RATE_LIMIT_STATE.json` was present. One source-qualified lineage predecessor was selected without reading its content: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md` blob `7f2494356092d909cd442bdf881b342a59a67b73`. Scope is only that exact root listing; subdirectories and candidate content were not inspected.

Scope/acceptance: residual richer-mode/protected/manual dependency=`none`; finite monthly/trial/paid quota dependency=`none`; incremental cost=`0`; global_completion=false; phase1_completion_claimed=false; scheduler_mutation_by_worker=false; termination=`bounded_slice_complete_recurring_open`.

Exact continuation: `clean-rate-limit-candidate-content-reconstruction-v1`. After fresh bootstrap and a persisted/read-back preflight checkpoint, fetch exactly `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md` on `clean-long-horizon-phase1-active`, require blob `7f2494356092d909cd442bdf881b342a59a67b73`, reconstruct only its rate-limit predecessor state and exact next transition, persist/read back, and return recurring-open. If missing/mismatched, persist a stale/missing predecessor blocker. Do not execute attempt-2, enumerate another directory, retry/wait, or start a second semantic leaf.
