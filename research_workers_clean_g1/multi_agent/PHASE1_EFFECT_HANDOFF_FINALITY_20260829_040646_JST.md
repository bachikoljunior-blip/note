# Phase-1 reservation-to-external-effect handoff finality stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- semantic control tuple remains frozen from this invocation: note main `63e0f497bc9157c6c5075a8c615327dc49b8e76a`, root control revision `21`, root blob `87e2d9e19b16d39b495a4a5512d871069d7521ee`, role config revision `6`, role config blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- after the first leaf's own repository writes advanced main, a SHA-only ref lookup observed `4c8fbb0c1208aab7a5d1c7d4201b90a9a5f65aa3`; SHA-only/empty-content path reads verified the authoritative root and role-config blob identities were still exactly the frozen blobs, so revision-21 post-freeze rules allowed continued semantic work without consuming newer-head semantics.
- semantic inputs for this leaf: own preceding cross-shard checkpoint/result/script, public AWS Prescriptive Guidance transactional-outbox documentation, public AWS SQS FIFO deduplication documentation, public PayPal REST idempotency documentation, and this finite synthetic model. No O/O-derived state, downstream state, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Leaf objective

The cross-shard leaf showed that current authority can be proven at a root or sink boundary. This leaf asks what happens next when the authoritative effect lives in a different system:

`read current authority -> call external sink -> record effect applied`

The two unresolved failure windows are:

1. **effect ambiguity:** the sink may have applied the side effect but the dispatcher crashes or loses the response before recording it locally;
2. **revocation TOCTOU:** authority is current when checked locally, then parent/claim authority changes before the external sink applies the effect.

The leaf separates durable *intent*, transport idempotency, sink-side durable effect identity, authority fencing, and multi-sink partial completion.

## Public mechanism facts used

### Transactional outbox solves the local dual-write gap, not duplicate downstream effects

AWS Prescriptive Guidance describes the transactional outbox pattern as storing the business update and outbox event in one local transaction so a crash cannot commit one without the other. The same guidance explicitly warns that the event processor may send duplicate messages and recommends making the consumer idempotent by tracking processed messages.

- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

That supports a strict distinction used here: an outbox is durable dispatch intent, not proof that an external side effect happened exactly once.

### Transport deduplication has documented retention scope

Amazon SQS FIFO deduplicates the same `MessageDeduplicationId` only within a **5-minute** deduplication interval. After that interval, the same identifier is not an indefinite exactly-once fence.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fifo-queue-message-identifiers.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html

PayPal similarly says `PayPal-Request-Id` is stored for a period of time and retries are safe only while the server stores the ID; its current REST guidance gives refund as an example where the same ID can be retried for up to 45 days. It also notes simultaneous requests with the same ID are not both processed.

- https://developer.paypal.com/api/rest/requests/

The model therefore treats finite transport idempotency as a scoped capability, never as permanent application identity.

## Finite model

The executable enumerates **2,304 equal-weight synthetic scenarios** over:

- sink capability: non-idempotent / finite transport idempotency / durable application `effect_id` / cooperative sink authority-epoch validation,
- transport token fresh vs expired,
- sink outcome: success / ambiguous-applied / ambiguous-not-applied,
- crash: none vs after effect before local record,
- authority revocation: none / before sink check / after sink check but before external call,
- dispatcher takeover: none vs takeover,
- one sink vs two sinks,
- second sink success vs blocked,
- disjoint vs overlapping effects.

The model compares:

1. **NEG direct blind retry** — local authority read, direct external call, retry on ambiguity.
2. **Transactional outbox only** — durable local intent, but no sink-side durable dedup/current-authority cooperation.
3. **Outbox + finite transport idempotency** — retries rely on the sink's finite key-retention contract.
4. **Fenced dispatcher + local sink-time authority recheck** — current dispatcher epoch and authority are checked immediately before the external call, but the sink is not part of that authority transaction.
5. **Fenced dispatcher fail-closed** — same local fencing, but ambiguous non-idempotent/expired cases are left unresolved instead of blindly retried.
6. **Durable sink effect ID** — sink durably deduplicates by application effect identity; no permanent current-authority cooperation is assumed.
7. **Cooperative sink authority epoch** — strong capability: the sink atomically validates current authority epoch and consumes a durable effect ID with the effect.
8. **Staged serial integrator** — one integrator serializes dispatch but has no extra sink cooperation.

## Main result

| protocol | terminals | unsafe scenarios | duplicate effects | stale-authority effects | ambiguous unresolved | structural capability blocks |
|---|---:|---:|---:|---:|---:|---:|
| NEG direct blind retry | 1,026 | **1,192** | **504** | **1,024** | 0 | 0 |
| transactional outbox only | 984 | **1,248** | **672** | **1,024** | 0 | 0 |
| outbox + finite transport idempotency | 1,026 | **1,192** | **504** | **1,024** | 0 | 0 |
| fenced dispatcher + local recheck | 788 | **656** | **288** | **512** | 288 | 0 |
| fenced dispatcher fail-closed | 788 | **512** | **0** | **512** | **288** | 0 |
| durable sink effect ID | 448 | **256** | 0 | **256** | 0 | **1,152** |
| cooperative sink authority epoch | 160 | **0** | 0 | 0 | 0 | **1,728** |
| staged serial integrator | 752 | **704** | **384** | **512** | 384 | 0 |

The counts are deliberately not a scalar ranking. Capability-block counts mean the protocol refuses to claim a guarantee when the sink does not expose the required surface.

## Exact counterexample 1: local durability cannot solve external ambiguity

In the **16-scenario** slice with:

- non-idempotent sink,
- ambiguous-applied result,
- crash after the external effect but before local record,
- no authority revocation,
- no dispatcher takeover,

every local retrying protocol produces **16/16 duplicate external effects**:

- direct blind retry: 16 unsafe / 16 duplicate,
- transactional outbox only: 16 unsafe / 16 duplicate,
- outbox + finite-idempotency policy: 16 unsafe / 16 duplicate because this sink exposes no idempotency,
- fenced dispatcher + local recheck: 16 unsafe / 16 duplicate,
- staged serial integrator: 16 unsafe / 16 duplicate.

The fail-closed dispatcher instead has **0 duplicate / 0 unsafe terminals**, but leaves all 16 effects explicitly ambiguous/nonterminal. The two sink-cooperative protocols are structurally blocked on this sink.

This is the key indistinguishability boundary: after response loss, local state can be identical whether the sink applied or did not apply. If the sink exposes neither durable idempotency nor an authoritative status query/effect identity, retry can duplicate the applied world and no-retry can omit the not-applied world. Local serialization or an outbox cannot manufacture the missing observation.

## Exact counterexample 2: finite idempotency expiration restores the ambiguity

The same pattern appears in the **16-scenario** slice where the sink supports finite idempotency but the key has expired before retry. The local retrying protocols again produce **16/16 duplicate effects**. This is why transport idempotency retention must be part of the retry proof, not summarized as `has_idempotency_key=true`.

The public SQS five-minute dedup interval and PayPal's documented finite server-retention model are concrete examples of this scope boundary.

## Exact counterexample 3: local recheck still has a check-to-effect race

The **512-scenario** `authority revoked after local sink check but before external call` slice shows a second non-substitutable proof obligation:

- fenced dispatcher + local recheck: **512/512 stale-authority effects**, 512 unsafe,
- durable sink effect ID: duplicate-safe where supported, but **256/256 supported scenarios still stale**,
- staged serial integrator: **512/512 stale-authority effects**.

Durable effect identity solves retry duplication; it does not make a previous local authority check current at the instant another system applies the effect.

Only the strong `cooperative sink authority epoch` candidate is safe in its supported capability slice, because the model requires authority validation and durable effect-ID consumption to be atomic with effect application at the sink. It is structurally blocked on the other three sink capability classes. This is an explicit capability requirement, not a claim that ordinary APIs provide such a surface.

## Transactional outbox: what it does and does not prove

The outbox remains valuable: it prevents the local business-state/outbox dual-write gap and gives recovery a durable dispatch intent. AWS explicitly recommends idempotent consumers because duplicate sends can still occur. The finite model reflects that: `transactional_outbox_only` actually has more duplicate cases than direct dispatch because durable intent makes retry/re-dispatch likely after takeover or ambiguous acknowledgement unless the consumer/sink deduplicates.

So the proof layers are:

1. **local atomic intent** — outbox or equivalent,
2. **current dispatcher authority** — epoch/fence,
3. **external effect identity / status** — durable sink-side dedup or authoritative lookup,
4. **current effect authorization** — if revocable until application, the sink must participate in authority validation or the contract must explicitly change to an irrevocable authorization/capability semantics.

None is a general substitute for the others.

## Multi-sink partial completion is a third axis

The **384-scenario** two-sink/second-blocked slice demonstrates that duplicate safety and authority safety do not imply atomic multi-effect completion. Even the cooperative sink candidate has partial exposure in the subset where the first sink validly applies and the second blocks. This leaf records partial-effect exposure separately and does not automatically call it unsafe because compensation/saga semantics are application-specific.

Therefore a parent terminal predicate must state whether the objective requires:

- every effect applied,
- a compensatable partial state,
- or merely durable dispatch intent.

Treating these as one `COMMITTED` bit would recreate the earlier root-certificate error at the effect layer.

## Current generic candidate

1. Atomically persist business state plus an outbox/effect intent with deterministic application `effect_id`, parent generation, required effect set and exact retry contract.
2. Fence dispatchers by current epoch; stale workers may stage/observe but cannot acknowledge or terminalize.
3. Immediately before dispatch, revalidate parent/current authority. This closes pre-check revocation only; do not claim it closes the external check-to-effect race.
4. If the sink offers durable application-level effect identity/status, use that identity for read-before-retry and never reduce it to a finite transport-token Boolean.
5. If the sink offers only finite idempotency, retry only while the documented retention/current-status proof is still valid. After expiry, block/reconcile rather than blind retry.
6. If the sink is non-idempotent and an ambiguous-applied state cannot be authoritatively queried, fail closed: the protocol cannot guarantee both no duplicate and eventual effect from local state alone.
7. If authorization must remain revocable until the external effect is applied, require sink cooperation/shared authority for an atomic authority check + effect-ID consume, or explicitly change the semantics to an irrevocable capability minted while authority is current.
8. Keep multi-sink partial completion/compensation as a separate terminality dimension.

## Exact scope limits

- The model does not claim a universal impossibility theorem for every distributed system; it isolates the tested information surfaces. A sink status endpoint, durable effect resource ID, transactional shared store, or domain-specific reconciliation can add information not present in the non-idempotent slice.
- `cooperative sink authority epoch` is a capability assumption, not an observed property of SQS, PayPal, or generic HTTP APIs.
- the SQS 5-minute interval is about FIFO message deduplication, not arbitrary external business effects.
- PayPal retention is operation-specific; the refund example is not generalized to every PayPal endpoint.
- partial multi-sink effect exposure is measured, not automatically judged unsafe without objective/compensation semantics.
- all counts are equal-weight synthetic mechanism counts, not incident frequencies.

## Exact Phase-1 continuation

Continue with **revocable-vs-irrevocable effect capability semantics and multi-sink terminality**.

Next finite grammar:

- authorization contract: revocable-until-effect vs irrevocable-after-authorize,
- capability mint atomic with parent generation vs separate read-then-mint,
- capability single-use / replayable / expiring,
- sink durable effect ID + capability nonce vs transport token only,
- parent supersession before mint / after mint / after first sink,
- two and three sinks with partial success and compensation availability,
- compensation itself idempotent/ambiguous/late-failing,
- dispatcher takeover and capability replay,
- terminal predicates: all-effects durable / compensated rollback / durable intent only,
- direct outbox dispatch, fail-closed non-idempotent sink, cooperative sink capability, and saga/compensation controls.

Measure stale-authority effects, duplicate external effects, capability replay, partial-effect exposure, false terminalization, compensation ambiguity, safe parallel dispatch, and liveness blocks separately. Preserve the exact distinction: irrevocable capability semantics can close the revocation TOCTOU only by changing the contract, not by proving that a revocable authorization stayed current.