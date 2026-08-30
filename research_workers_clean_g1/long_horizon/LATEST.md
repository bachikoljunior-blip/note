# Long Horizon clean_g1 — bounded Phase-1 preflight

Canonical branch: `clean-long-horizon-phase1-active`

Frozen authority for this invocation: manifest revision/blob `6` / `42a39c7911e005c05fd2810e617a876eafbbeedc`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true.

Selected effect chain: `clean-duplicate-consumption-create-once-v1`.

Exact predecessor/frontier: prior LATEST blob `c5024e60df7549df98d808655d4aa065b279f132` ended with the first create blocked before any marker/effect was written. Resume the same leaf only.

Planned atomic boundary: create one safety-minimal role-local marker at `research_workers_clean_g1/long_horizon/effects/duplicate_create_once_v1.json`, exact-read it back, then attempt exactly one duplicate create to the identical path. Pass this leaf only if the first create persists, the duplicate create is rejected, and readback preserves the first blob.

Forecast: this preflight CAS plus at most two create calls plus one final LATEST CAS; no retry, wait, poll, backoff, scheduler mutation, optional second leaf, protected-primary action, hosted compute, finite monthly/trial/paid quota, or incremental monetary cost. Switch threshold: any write-surface block, authority mismatch, unexpected duplicate acceptance, or inability to exact-read back the first marker ends this leaf immediately and preserves a nonempty next-invocation continuation.

Lifecycle preflight: global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true.
