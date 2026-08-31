# Long Horizon Phase-1 checkpoint — same-generation stale-sequence guard

## Frozen authority and predecessor
- manifest control_revision=20, blob=`bf8cff1c59401834679b89a151178c3729a50723`
- RUN_LIFECYCLE control_revision=1, blob=`8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root control_revision=26, blob=`481660fb6008a57cea162da38439cf115c8d7ebe`
- role control_revision=17/config_revision=8, blob=`d790db45343bec399d00c6e9410432963726d72c`
- transport_mode=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true
- predecessor LATEST blob=`82bfc8b8c20c7537f3486c4aa6c555e10f08b3e0`
- preflight blob=`256ee8ab72dc2b1816cb8ce68708c3af7ee3f83a`
- reconstructed current state blob=`f79a86302e6c4fcb095aec7b22cc6491bb3da20a`

## One bounded leaf
Effect chain: `clean-rate-limit-same-generation-stale-sequence-guard-v1`.

Current canonical semantic state reconstructed from the exact blob:
- `state_sequence=6`
- `plan_generation=3`
- `current_plan=defer_no_retry_plan`
- `retry_attempt=3`, `max_attempts=3`
- `switch_count=2`

Test-only incoming continuation:
- `state_sequence=5`
- `plan_generation=3`
- `current_plan=compact_plan`
- carries predecessor semantics while copying the current generation number.

Deterministic controller evaluation, before any LIVE-state write:
1. generation freshness: `3 < 3` is false, so the prior generation-only guard does not reject this trace;
2. sequence freshness: `5 < 6` is true;
3. decision=`REJECT_STALE_SEQUENCE`;
4. no LIVE-state write is authorized, no retry attempt 4 is created, and `defer_no_retry_plan` cannot regress to `compact_plan` in this tested trace.

This closes only the same-generation / older-sequence replay case. It also exposes the next residual: a payload that copies both `plan_generation=3` and `state_sequence=6` while substituting stale predecessor plan/body would pass generation and sequence freshness. Repository CAS alone does not semantically bind the proposed body when the caller already possesses the current content SHA. Therefore a canonical-state/body fingerprint or equivalent exact semantic binding remains necessary to test.

## Acceptance constraints and scope
- richer-mode/Work/protected-primary/manual-user execution dependency: none
- finite monthly/trial/paid quota dependency: none
- incremental monetary cost: 0
- repository transport only; no repository API volume used as compute
- scheduler mutation by worker: none
- tested scope: deterministic role-local controller predicate using reconstructed exact state; no claim about hostile concurrent writers or global task success
- conflict check: no other-role/downstream/O/legacy semantics consumed; no LIVE state mutation performed

## Exact continuation
Next invocation execute exactly one leaf `clean-rate-limit-same-sequence-same-generation-body-fingerprint-guard-v1`: bootstrap/freeze current controls; exact-read the canonical role LATEST and reconstructed current state; construct a test-only incoming continuation with `plan_generation=3` and `state_sequence=6` but stale predecessor `current_plan=compact_plan`/body; with current CAS authority assumed, test an exact canonical semantic fingerprint (or equivalent immutable body binding) before any LIVE write. Required outcome is rejection of body substitution without attempt 4 or plan regression, while the untouched canonical payload remains admissible. Persist whether the minimum binding should cover the whole canonical semantic payload or a smaller tuple, and do not combine another leaf.

termination=`bounded_slice_complete_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true; hard_runtime_boundary_reached=false; next_invocation_resumes_exact_continuation=true.
