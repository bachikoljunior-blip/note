# Open Source Systems Scan — repair recovery semantics do not require bearer continuity

Role: `open_source` clean exploration.
Frozen semantic control tuple remains note main `b8c5a5e3b93fa70aa698d16465a8724f4785e6b3`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public Argus source remains `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## New result

The previous run identified that repair authorization/capability nonces are durably persisted in plaintext even though the model prompt receives only public ids/scope. The next question was whether **the same nonce must survive process restart** to preserve current crash-recovery behavior.

The public regression suite indicates that same-bearer continuity is **not an asserted semantic requirement**.

### Claimed capability crash

`test_claimed_capability_recovers_after_head_commit_crash` simulates a crash after the durable `claimed` event but before the claimed HEAD snapshot is safely current. Recovery through `current_repair_capability()` is asserted to restore:

- the same `capability_id`, and
- `status == "claimed"`.

The test does **not** assert nonce continuity.

### Acceptance-started crash

When the one allowed acceptance retry has started but durable settlement is missing, `current_repair_capability()` does not replay the acceptance run after restart. It fails closed by writing a durable rejected settlement with the reason that the acceptance outcome was unavailable and the one-shot retry was not replayed. This path therefore does not need the original bearer in order to reproduce the external acceptance attempt.

### Closed-settlement crash

`test_closed_capability_recovers_after_head_commit_crash` recovers the already durable `closed` event and its accepted result, clears stale active-capability projection if needed, and does not need to re-execute the privileged mutation.

### Current runtime coupling

The current implementation nevertheless couples recovery to the raw nonce because `_mission_execution_runtime.py` loads `current_repair_capability()` into `state.repair_capability` and, for a recovered `claimed` capability, calls `begin_acceptance_retry(..., nonce=state.repair_capability["nonce"])`. Settlement similarly supplies the persisted nonce to `close_repair_capability()`.

That is an implementation choice, not a behavior asserted by the recovery tests.

## Safer compatibility-preserving redesign

A lower-risk change can remove durable plaintext bearer continuity without weakening the tested recovery contract:

1. Persist durable **authorization facts** and capability identity/status, but store only a verifier/hash or no bearer at all in model-readable state.
2. On the normal in-process path, keep the one-shot bearer only in host memory.
3. If the process restarts while capability status is `claimed`, revalidate campaign/objective/epoch, exact current state revision, authorization id, action scope, expiry, frozen evidence/tree, write baseline and mission id under the control lock, then mint a **new ephemeral host-only nonce** for the same durable capability identity (or perform `begin_acceptance_retry` through an internal trusted method that does not expose a bearer).
4. If restart occurs after `acceptance_started`, retain today's fail-closed behavior: reject the interrupted one-shot retry; do not replay it.
5. If a durable `closed` event exists, recover the settlement directly.
6. Any old nonce must become invalid after restart/re-mint; no dual-valid window.

This preserves the tested properties—capability identity, one-shot acceptance budget, exact-current authorization, frozen evidence, fail-closed interrupted acceptance, and durable closed settlement—while removing the need to keep a reusable plaintext secret in the control tree.

## Why this matters for `clean-os-g1-005`

The proposed general protected-stage capability should copy the **revision and evidence fencing** from `CampaignControlStore`, but should not copy the plaintext durable bearer pattern. The cleaner invariant is:

`durable authorization + durable capability identity/status + exact current revision` are restartable; **bearer material is ephemeral host authority**.

If a backend/layout cannot guarantee that Manager control files are unreadable to the model, correctness should still hold because reading durable state reveals no reusable privileged bearer.

## Regression additions

- claimed capability recovery preserves `capability_id`/status but asserts the recovered durable record contains no reusable plaintext bearer;
- restart re-mint produces a new bearer/verifier generation and the pre-crash bearer is rejected;
- re-mint is allowed only while the original authorization is still exact-current and all frozen evidence/tree/write-baseline guards pass;
- acceptance-started crash remains a fail-closed rejection with no retry replay;
- closed-settlement crash still recovers the exact accepted/rejected receipt;
- model sandbox read test may read the control metadata without obtaining anything sufficient to call privileged mutation methods;
- wrong/stale bearer generation changes zero bytes.

## Scope limits

No live model exploit was executed. The claim is narrower: the current source persists raw bearers, but its own public crash-recovery tests do not require the same nonce to survive. A host-only re-mint/internal trusted-transition design is therefore compatible with the observed recovery contract in principle; it remains an unimplemented adaptation until tested in Argus.

## Exact continuation

Trace `issue_authorization` and backlog creation to ensure a recovered `claimed` capability can be revalidated from durable non-secret fields without consulting any model-writable state. Then inspect the ordering between authorization event append and immutable HEAD revision commit to design a crash-safe re-mint generation marker. In parallel, turn the pipeline-writer matrix into a concrete field-ownership/mutation API table and verify whether the existing Manager pipeline lock can be passed as an explicit transaction context rather than nested with `.manager-control.lock`.