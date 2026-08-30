# Phase-1 multi_agent Part 69 — keyless capability issuance and rollback boundary

## Frozen authority
- Phase: `phase_1_chat_parity`
- Root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- Task: `phase1-clean-multi-agent-concurrency-claims`
- Frozen main commit: `ab1bcabadaf0b4be4b2d421b20e8b387eb37ba2f`
- Root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- Role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- Lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- Transport: SHA-only main-ref + exact-SHA reads
- Presemantic liveness witness: `automation_control/receipts/multi_agent/receipt_2026-08-30T142810_JST_presemantic.json`, exact-read back before own-state/public semantic reads.

## Bounded leaf
Continuation from Part 68 asked whether a positive exact-generation grant for the repository-resident single-object special case can be issued without a long-lived worker secret, protected/manual execution, hosted coordination, finite monthly quota, or a new rollbackable authority.

I compared five issuance forms over nine targeted traces: fresh mint/consume; mint response lost after apply; mint response lost before apply; generation advance after mint; stolen grant seen by a reader without repository write permission; consumption by a different already-authorized repository writer; worker restart with no secret access; rate-limit interruption; and full same-domain authority rollback/ABA after a newer generation existed.

### Mechanisms
1. **Long-lived signed bearer capability.** Requires custody of a private signing key. That is a residual secret/protected-authority dependency for this Phase-1 route. Signature authenticity also does not by itself prove current generation at the sink.
2. **Sender-constrained signature/proof key.** Removes ordinary bearer replay only if the sender retains a private key, so it preserves the same forbidden key-custody dependency.
3. **Repository-CAS opaque grant ID in the same authority object.** Store `{generation, effect_binding, grant_id, grant_state, applied_effect_id}` in one repository object. Mint and consume are current-blob-SHA guarded updates. The grant ID is deliberately *not* treated as a secret credential; repository write authentication remains the authority boundary.
4. **Deterministic/public grant ID.** Keyless but adds no authorization beyond the repository object; it is only an idempotency/correlation identity and has the same rollback boundary as (3).
5. **Fail-closed issuance.** Safe when no acceptable authority exists, but gives no positive grant.

## Targeted result
For mechanism (3), under the explicit scope **single repository object, sender identity not semantically required, and no force-rewind/ABA of the authority object**, eight of the nine targeted traces are handled without a worker-held secret:
- ambiguous mint success is reconciled by reading the current object before retry;
- generation advance is rejected when consume atomically compares current generation/effect binding and changes `grant_state`/`applied_effect_id` in the same object;
- a reader who steals a public grant ID but lacks repository Contents-write authority gains no new write capability;
- another actor who already has Contents-write authority may consume the grant, so the design is valid only when *which worker* consumes is not part of the authorization contract;
- worker restart needs no private key because all issuance state is in the object;
- rate-limit interruption fails closed and checkpoints rather than treating a request as applied.

The ninth trace, **full same-domain rollback/ABA**, is not solved. A future invocation that can observe only an authority object restored to an earlier exact state cannot distinguish (A) a world where the later generation never existed from (B) a world where it existed and the entire authority domain was rolled back. Adding a signature whose trust/rotation state is stored in the same rollback domain does not break that indistinguishability; adding a private key or external monotonic witness breaks the CLEAN/zero-dependency acceptance gate. Therefore the repository-CAS opaque grant is a useful *scoped positive special case*, but it is not a rollback-complete exact-generation capability.

## Public-source qualification
GitHub's current REST Contents documentation states that updating an existing file requires the blob `sha`, that the endpoint requires repository Contents write permission for fine-grained tokens, and that conflicting contents operations must be serialized: https://docs.github.com/en/rest/repos/contents . GitHub's REST authentication documentation states that access tokens act as the caller's identity subject to their scopes/permissions and must be kept secure: https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api . These support the narrow claim that the opaque grant ID need not itself be a bearer secret: write authority comes from authenticated repository permission plus current-object CAS. They do **not** prove anti-rollback outside the repository's own authority domain.

## Acceptance / non-acceptance
- Incremental monetary cost added by this mechanism: **0**.
- Optional monthly/trial/paid quota dependency added: **none**; repository API is transport only and rate-limit interruption is fail-closed/checkpointed.
- Richer-mode/protected/manual execution dependency for the scoped repository-object mechanism: **none**, provided sender identity is not part of the effect contract and same-domain rollback is excluded.
- Accepted external hosted coordination: **none**.
- Arbitrary external sink generalization: **not accepted**.
- Full same-domain rollback/ABA: **unresolved child**.
- Global Phase-1 completion: **false**.

## Exact continuation
Execute exactly one bounded non-conflicting leaf on **keyless anti-rollback witnesses for a single repository authority object**. Compare: repository commit ancestry/current-ref monotonicity, a compact generation-floor record in a separate path within the same rollback domain, signed metadata whose key state is also repository-resident, and fail-closed detection. Use paired histories that end in identical observable repository state after a force-rewind/restore to test indistinguishability. Determine whether any scheduled-Chat-native, zero-cost, zero-finite-quota mechanism can distinguish those histories without protected secrets, manual configuration, or an authority outside the rollback domain. If not, keep rollback-complete issuance unresolved and select the next role-safe claim/idempotency child next invocation; do not broaden the scoped repository-CAS positive result.
