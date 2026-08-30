# Long Horizon clean_g1 — Phase-1 preflight

Frozen authority: manifest revision/blob `8` / `69d051afef01b81aed99eebbd49cf556f8c2a7e5`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true.

Selected effect chain: `clean-rate-limit-state-reconstruction-origin-v1`. Predecessor LATEST blob: `2d4a979188c35ac01d5ac993fa75399080fb20b2`.

Atomic boundary: perform one bounded lookup only within `research_workers_clean_g1/long_horizon/` for the newest source-qualified predecessor that records `LIVE_RATE_LIMIT_STATE.json` or its creation lineage. Restore/recreate canonical attempt-1 only if exact predecessor/binding proves it is the same role-local state; otherwise checkpoint the unresolved blocker. No waiting, polling, retry, scheduler mutation, cross-role input, or optional second leaf.

Forecast/switch rule: semantic soft stop=25s, checkpoint start by=30s, normal return target=40s, absolute intentional ceiling=45s. Ambiguous lineage, lookup failure, CAS/authority mismatch, or insufficient remaining budget switches immediately to checkpoint-only recurring-open return.

Lifecycle fields: termination=`preflight_checkpoint_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; hard_runtime_boundary_reached=false; continuation_nonempty=true.

Exact continuation if interrupted before the atomic boundary: resume `clean-rate-limit-state-reconstruction-origin-v1` from predecessor blob `2d4a979188c35ac01d5ac993fa75399080fb20b2`; locate only own role-local source-qualified lineage for `LIVE_RATE_LIMIT_STATE.json`, and do not synthesize or restore state without exact binding proof.
