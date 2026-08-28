# Phase-1 authorization cancellation and compensation after irrevocable effect minting

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `f6b3c1273f7abb3685198ce5dbbc2368151eca6c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_CROSS_DOMAIN_CLAIM_WITNESS_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, public Stripe/AWS documentation, and one finite synthetic cancellation/compensation model.
- mechanism script SHA-256: `cbaa61890075d0facc97ab1b995b9f6f0492b3924b276bd58682db1bbb510ae2`
- mechanism result SHA-256: `e1af0e5b1f223dd207c8dbe7ef089a538d28d4964737ae11077565be4410d472`

## Leaf objective

The predecessor leaf made `AUTHORIZED(effect_id)` deliberately irrevocable in claim authority domain X so that later claim takeover could not retroactively invalidate an already-authorized external effect. This leaf asks what happens when a cancellation request arrives **after** that authorization point.

The key distinction is now:

1. retroactive local revocation — invalid, because authorization was intentionally one-way;
2. sink-native cancel-if-pending — valid only when the sink atomically prevents the effect from completing;
3. compensation after application — a new effect with its own identity, retry contract, and finality;
4. manual/nonterminal handling — required when neither cancel nor compensation can be proved final.

## Public mechanism boundary

Stripe's current PaymentIntent documentation says cancellation is available only in specific pre-completion states such as `requires_capture`, and cancellation returns an error when the intent is no longer cancelable. Once a payment succeeds, Stripe's refund guidance directs clients to create a refund instead of canceling the completed payment.

Stripe also documents that refunds can remain pending, can later fail, and in some flows can move through `requires_action`, `pending`, `succeeded`, `failed`, and `canceled`. This is a concrete public example where post-application compensation has its **own** lifecycle and cannot be treated as equivalent to pre-application cancellation.

AWS transactional-outbox guidance remains relevant for restart identity: it recommends atomic production of business state plus an outbox record and notes that downstream delivery can duplicate, so consumers should be idempotent. That supports stable cancellation/compensation identity but does not make an external sink cancellation atomic with local authority.

Sources:
- https://docs.stripe.com/api/payment_intents/cancel
- https://docs.stripe.com/refunds
- https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

## Finite model

The executable script enumerates **2,450 equal-weight synthetic scenarios**. Dimensions include:

- effect timing: before sink sees it / pending / cancel-vs-apply concurrent / already applied / already failed;
- sink supports atomic cancel-if-pending or not;
- sink supports compensation/reversal or not;
- clear vs ambiguous cancellation observation plus whether authoritative cancel status is visible;
- dispatcher takeover;
- compensation dedupe contract absent/present;
- compensation request clear or ambiguous and actually absent/applied;
- compensation finality: `succeeded / failed / reversed / pending`;
- compensation status visible/unavailable.

Policies:

1. `pretend_revocation` — mark X canceled and stop local delivery as if the old authorization had vanished.
2. `cancel_if_pending` — use sink cancellation but terminalize on an ambiguous cancel response.
3. `compensate_after_apply` — compensate after application but retry ambiguous compensation on takeover and terminalize on request application rather than final compensation.
4. `manual_irreversibility` — only terminalize on clearly/authoritatively confirmed cancel or terminal effect failure; otherwise leave manual/nonterminal.
5. `safe_archive` — require authoritative cancel success, or if effect applied, a separate compensation identity with safe retry and authoritative successful compensation finality; otherwise fail closed.

## Aggregate result

| policy | safe terminal | unsafe | false terminal | lost authorized effect | duplicate compensation |
|---|---:|---:|---:|---:|---:|
| pretend revocation | 196 | **2,254** | **2,254** | **1,372** | 0 |
| cancel-if-pending baseline | 784 | **882** | **882** | 0 | 0 |
| compensate-after-apply baseline | 966 | **938** | **938** | 0 | **112** |
| manual irreversibility | 784 | 0 | 0 | 0 | 0 |
| safe archive | **966** | **0** | **0** | 0 | **0** |

These are mechanism counts from the finite lattice, not empirical incident rates.

## Result 1: cancellation is a new sink operation, not retroactive claim revocation

`pretend_revocation` is unsafe in **2,254 / 2,450** scenarios. It loses **1,372** already-authorized effects by stopping delivery when the sink has not durably canceled them, and it falsely claims cancellation in another **882** scenarios where the effect is or becomes applied.

The authorization contract from the predecessor leaf therefore survives this cancellation leaf: once X entered `AUTHORIZED(effect_id)`, a later X-side `CANCEL_REQUESTED` cannot by itself erase the effect authority. Cancellation needs its own sink-visible proof.

## Result 2: ambiguous cancel response is not cancellation finality

In the slice where the sink supports cancel-if-pending but an ambiguous cancel response actually **did not cancel**, there are **588** scenarios.

- `cancel_if_pending` terminalizes all 588 and is unsafe in **588 / 588**.
- `safe_archive` terminalizes only 78 scenarios, where the effect subsequently applied and an independently proven successful compensation completed; it leaves the rest nonterminal.
- When an ambiguous cancel actually succeeded but no authoritative cancel status is observable, the dedicated slice has **294** scenarios and `safe_archive` leaves **294 / 294** unresolved instead of inventing finality.

Thus retryability/observability of the cancellation command and final cancellation state are separate proofs.

## Result 3: takeover does not make ambiguous compensation retry-safe

For the slice `effect already applied + compensation supported + first compensation request ambiguous but actually applied + takeover + no dedupe contract`, there are **16** scenarios.

- `compensate_after_apply` retries and produces **16 / 16 duplicate compensations**.
- `safe_archive` never produces a duplicate. It terminalizes only the 2 scenarios where the already-applied compensation can be authoritatively observed as succeeded; the remaining 14 stay unresolved.

The safe protocol therefore binds compensation to a separate stable `compensation_effect_id` and retries ambiguous delivery only when the sink's idempotency/dedupe contract covers that exact identity.

## Result 4: compensation acceptance is not compensation finality

In the 96-scenario slice where compensation was applied but later finality is `failed`, `reversed`, or still `pending`:

- `compensate_after_apply` is unsafe in **96 / 96** because it treats the compensation request as terminal cancellation.
- `safe_archive` terminalizes **0 / 96** and keeps the branch unresolved with residual exposure recorded.

By contrast, in the 24-scenario slice with authoritatively observable `succeeded` compensation, `safe_archive` terminalizes **24 / 24** safely.

This mirrors Stripe's public lifecycle distinction: refund initiation and later refund state are not the same event.

## Candidate protocol

1. Keep `AUTHORIZED(effect_id)` immutable as the original authorization witness.
2. Represent cancellation as `CANCEL_REQUESTED(cancel_id, effect_id)` rather than rewriting authorization history.
3. If the sink has an atomic cancel-if-pending primitive, invoke it by stable effect/cancel identity and terminalize only after an authoritative sink state proves the effect can no longer apply.
4. If the effect is already applied, create a **new** `compensation_effect_id` with its own contract digest, claim epoch, dedupe/idempotency proof, and status/finality witness.
5. Dispatcher takeover may change who drives cancellation/compensation but must not mint a second compensation identity for the same repair obligation.
6. On ambiguous compensation delivery, retry only if the sink-specific dedupe/idempotency contract is still valid for that exact compensation identity; otherwise reconcile by authoritative status or fail closed.
7. Do not mark cancellation terminal until the vector is final:
   - original effect `CANCELED` or `FAILED`, or
   - original effect `APPLIED` and compensation is authoritatively `SUCCEEDED`.
8. `PENDING`, `FAILED`, `REVERSED`, unknown, or unobservable compensation stays nonterminal/manual.
9. Treat residual irreversible exposure as explicit state, not as hidden success.

## Exact tested scope

- X authorization is already minted and intentionally irrevocable.
- Cancel-if-pending is modeled as an atomic sink primitive when supported.
- Compensation is a separate effect identity.
- No Byzantine store, identity collision, partial-amount compensation, multiple simultaneous compensations, or cross-generation effect-key reuse.
- Sink-native status visibility is simplified to a boolean authoritative read.
- Counts are equal-weight synthetic mechanisms, not production rates.

## Exact Phase-1 continuation

Continue with **cross-generation cancellation/compensation ABA and effect-incarnation identity**.

Next grammar:

- generation `g1` authorizes `effect_id_1`, then receives delayed cancel/compensation work;
- generation `g2` later authorizes the same logical task/effect key;
- compare logical-key reuse, unique per-generation effect IDs, sink tombstone/min-generation fence, and safe archive;
- delay g1 cancel until after g2 is pending/applied;
- delay g1 compensation until after g2 completes;
- include dispatcher takeover, ambiguous old cancel/compensation response, dedupe retention expiry, and effect-key reallocation;
- measure cross-generation mis-cancel, mis-compensation, duplicate effect, false terminal generation, and orphan repair;
- test whether a compact sink-side minimum accepted generation/effect-incarnation watermark can replace permanent per-effect tombstones without allowing ABA.

Keep the Phase-1 frontier nonempty and do not restore unrelated base research while the overlay remains active.
