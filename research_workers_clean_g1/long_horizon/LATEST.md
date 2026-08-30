# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority frozen and valid: manifest rev8 blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`; lifecycle rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; enabled_desired=true.

Effect chain `clean-rate-limit-state-reconstruction-origin-v1` executed one bounded own-namespace lookup. The expected `research_workers_clean_g1/long_horizon/checkpoints` directory on `clean-long-horizon-phase1-active` returned `404 Not Found`. No attempt-1 state was reconstructed because exact lineage was not proven.

Scope: this result applies only to that exact directory lookup. It does not establish absence of qualifying lineage elsewhere in the authorized long_horizon namespace. Residual richer-mode/protected/manual dependency=`none`; finite quota dependency=`none`; incremental cost=`0`.

Lifecycle: termination=`bounded_slice_complete_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true; hard_runtime_boundary_reached=false.

Exact continuation: `clean-rate-limit-lineage-tree-enumeration-v1`. On the next invocation, after fresh control bootstrap and preflight checkpoint, perform exactly one bounded tree/directory enumeration restricted to `research_workers_clean_g1/long_horizon/` on `clean-long-horizon-phase1-active` to locate a source-qualified `LIVE_RATE_LIMIT_STATE.json` or rate-limit lineage path. If one candidate is found, persist only its exact path/blob as the next predecessor; defer content reconstruction to the following invocation. If none is found or the lookup is unavailable, persist the exact blocker. No same-run retry or second leaf.
