# Long Horizon clean_g1 — bounded Phase-1 preflight

Canonical branch: `clean-long-horizon-phase1-active`

Frozen authority for this invocation: manifest revision/blob `7` / `26b08f75ed25273b05e43ce77e018675c635b37a`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true.

Selected effect chain: `clean-duplicate-consumption-create-once-v1`.

Exact predecessor/frontier: prior branch LATEST blob `aeaaac30227c9906c06828ea5c790ce808a4acb3` precommitted the create-once duplicate probe. Reconstruction now finds the first marker already durable at `research_workers_clean_g1/long_horizon/effects/duplicate_create_once_v1.json`, blob `e70231f40a2accc03a104bd121c1198fcebc7fa9`; therefore do not recreate the first effect.

Planned atomic boundary: perform exactly one duplicate `create_file` attempt to that identical path. Pass this leaf only if GitHub rejects the duplicate create and a subsequent exact readback preserves blob `e70231f40a2accc03a104bd121c1198fcebc7fa9`. No retry, wait, poll, backoff, scheduler mutation, or optional second leaf.

Forecast/switch threshold: one duplicate-create call, one marker readback, one final LATEST CAS, and at most one immutable own receipt. Any unexpected duplicate acceptance, authority/CAS mismatch, or inability to verify the original blob terminates this slice recurring-open with a nonempty exact continuation.

Lifecycle preflight: global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true; hard_runtime_boundary_reached=false.
