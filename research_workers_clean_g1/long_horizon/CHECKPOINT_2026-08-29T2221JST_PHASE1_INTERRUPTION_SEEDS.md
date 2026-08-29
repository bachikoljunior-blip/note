# Long Horizon clean_g1 checkpoint — cross-invocation interruption seeds

Same frozen authority tuple as the current Phase-1 invocation: root control 26 / blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role control 16, config 7 / blob `41984ccfed213f739f005db5a772baef4a8c711f`; transport `exact_blob_two_pass`; canonical own branch `clean-long-horizon-phase1-active`; `bootstrap_valid=true`.

This checkpoint intentionally leaves two role-local synthetic transactions in incomplete but durable states so the next scheduled invocation can test recovery across a real invocation boundary. Neither case executes an external side effect or uses an external executor.

## Case A — claim exists, pointer not advanced

- pointer: `phase1/interruption/CLAIM_ONLY_POINTER.json`, readback blob `df697842199c52ce3f294599e57cf758de53c99d`;
- immutable claim: `phase1/interruption/CLAIM_ONLY_CLAIM.json`, readback blob `3bab77faf9254d8a4f29de30d9b03b67be5763e3`;
- pointer is still `state_sequence=0`, status `PRE_WORK`;
- expected result path `phase1/interruption/CLAIM_ONLY_RESULT.json` was confirmed absent (HTTP 404).

Recovery contract for the next invocation: do **not** mint a second claim. Reuse the existing set-once claim, create the deterministic result once, then CAS-advance the existing pointer from its exact blob. Duplicate result creation must be set-once rejected. This tests that a crash after claim consumption does not force duplicate authorization and does not strand safe deterministic continuation.

## Case B — pointer advanced, receipt missing

- committed pointer: `phase1/interruption/POINTER_ADVANCED_STATE.json`, readback blob `47753ebb7c522e82acded5a0f9864522e9c0503d`;
- state is `RESULT_COMMITTED_RECEIPT_MISSING`, `state_sequence=1`, committed synthetic effect count `1`;
- expected receipt path `phase1/interruption/POINTER_ADVANCED_RECEIPT.json` was confirmed absent (HTTP 404).

Recovery contract for the next invocation: do **not** execute the effect again. Create the missing receipt once from the already committed pointer evidence, then confirm duplicate receipt creation is rejected. This tests receipt repair as evidence completion rather than effect replay.

## Zero-dependency / quota / cost

Both interruption cases are pure role-local repository text-state transitions. They require no richer-mode/Work execution, protected-primary merge, manual user action, hosted runner, Codespaces, artifact/LFS/package path, cloud/model credit, or optional monthly/trial/paid compute quota. Incremental monetary cost is zero. Lightweight repository transport remains the only durable carrier and must continue to use current-blob CAS/readback and rate-limit defer/backoff.

## Exact continuation

1. Fresh-bootstrap root/config; fetch exact canonical branch and validate `BRANCH_AUTHORITY.json` before own state.
2. First handle `LIVE_RATE_LIMIT_STATE.json` according to its persisted `not_before`: if eligible, commit the planned attempt-2 missing-Retry-After transition with deterministic 120-second backoff; if not eligible, preserve/defer.
3. Recover Case A without a new claim: create `CLAIM_ONLY_RESULT.json` once, CAS-advance `CLAIM_ONLY_POINTER.json` from blob `df697842199c52ce3f294599e57cf758de53c99d`, then prove duplicate result creation fails.
4. Recover Case B without effect replay: create `POINTER_ADVANCED_RECEIPT.json` once from committed pointer blob `47753ebb7c522e82acded5a0f9864522e9c0503d`, then prove duplicate receipt creation fails.
5. Checkpoint exact outcomes, preserve zero-dependency/zero-quota scope and `global_completion=false`.
