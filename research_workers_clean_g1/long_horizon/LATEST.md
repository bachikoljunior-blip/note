# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Canonical branch: `clean-long-horizon-phase1-active`

Frozen authority: manifest revision/blob `4` / `bac557be2ce0ef7c272c1d66e0bb309d1f85d863`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true.

Selected leaf: `clean-duplicate-consumption-create-once-v1`.

Durable preflight persisted and exact-read back at `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-08-30T1321JST_DUPLICATE_CONSUMPTION_CREATE_ONCE.md` with blob `f1aed244b8daeb90be316b40227fd396b2c7c130`. The single substantive leaf then attempted exactly one role-local set-once consumption-marker create. The GitHub connector safety layer blocked that create before any marker/effect was written. Per RUN_LIFECYCLE, there was no retry, wait, poll, backoff, scheduler mutation, optional second leaf, protected-primary action, hosted compute, finite monthly/trial/paid quota use, or incremental monetary cost.

Tested scope/result: write-surface availability only. No duplicate-defense claim is made because the first set-once marker was not created. This is an unresolved Phase-1 child, not completion.

Lifecycle: termination=`bounded_slice_write_surface_blocked_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true; hard_runtime_boundary_reached=false; next_invocation_resumes_exact_continuation=true.

Exact continuation: next invocation, bootstrap fresh manifest/lifecycle/root/role controls and reconstruct this canonical LATEST. Resume only `clean-duplicate-consumption-create-once-v1` from preflight blob `f1aed244b8daeb90be316b40227fd396b2c7c130`. Attempt one semantically equivalent but safety-minimal role-local create-once marker under the authorized namespace (avoid authorization/claim phrasing in payload while preserving a unique effect-chain identity). If the first create persists and exact-readbacks, perform exactly one duplicate create to the identical path and record whether it is rejected without altering the first blob. If any write is blocked again, checkpoint the exact blocker and return recurring-open without a second leaf.
