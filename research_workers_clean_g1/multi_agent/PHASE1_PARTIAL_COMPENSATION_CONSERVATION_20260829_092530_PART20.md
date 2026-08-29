# Phase-1 multi-agent partial compensation conservation: immutable segment contracts plus remaining-obligation ledger

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_COMPENSATION_CLAIM_COLLISION_20260829_085803_PART19.md`
- script: `research_workers_clean_g1/multi_agent/phase1_partial_compensation_conservation_20260829_092530_part20.py`
- result: `research_workers_clean_g1/multi_agent/phase1_partial_compensation_conservation_20260829_092530_part20.json`

## Objective

Extend the previous one-unit compensation model to partial and multi-resource compensation. The original effect has a required compensation amount of 100. The initial repair plan is either one segment `{100}` or two segments `{40,60}`; takeover may preserve order, reverse it, or re-partition as `{60,40}`. The model distinguishes logical segment identity from claim epoch, and distinguishes sink resource identity from the amount/range contract it satisfies.

The primary falsification target was ordinal-only segmentation: after takeover/replanning, ordinal `0` can refer to a different amount/range than before. A second target was range identity without a remaining-obligation ledger: a new range can overlap an already-applied but differently partitioned range. A third target was blind retry after an ambiguous partial application has outlived both durable status and the old idempotency window.

## Public mechanism audit

Current PayPal/Braintree documentation provides a concrete external-effect analogue without supplying the repository protocol itself:

- Braintree supports multiple partial refunds against one transaction, but requires that their sum remain below the original transaction amount and recommends avoiding simultaneous refund requests for the same transaction: https://developer.paypal.com/braintree/docs/reference/request/transaction/refund/python
- PayPal's current refund guide recommends storing capture/refund history, using idempotency keys, validating against the remaining refundable balance, tracking cumulative refund amount, and querying refund status by refund ID: https://developer.paypal.com/checkout/refund-payment
- PayPal documents `PayPal-Request-Id` as an idempotency mechanism and says the server stores the ID for up to 45 days, so an idempotency key is a bounded retry aid rather than a permanent proof of non-application: https://developer.paypal.com/api/make-api-requests

These are mechanism precedents only. The immutable-range and remaining-obligation rules below are conclusions of this finite synthetic model, not claims about PayPal/Braintree internals.

## Finite model

The executable model enumerates **3,072 equal-weight synthetic scenarios** over:

- initial plan: `FULL100 / SPLIT40_60`;
- takeover replan: `SAME / REORDER / REPART60_40`;
- first effect truth/observation: `CONFIRMED_APPLIED / AMBIG_APPLIED / AMBIG_NOT_APPLIED / AMBIG_PARTIAL`;
- old idempotency entry: `VALID / EXPIRED`;
- durable sink status: `YES / NO`;
- takeover: `NO / YES`;
- current-writer verifier at recovery: `AVAILABLE / OUTAGE`;
- sink result resources: `ONE / TWO` IDs;
- duplicate resource observation: `NO / YES`;
- repeated same compensation kind: `NO / YES`.

All candidates retain the previous leaf's sink-time current-writer fence when it is available, so this leaf isolates compensation segmentation/amount identity rather than re-proving stale-writer fencing. Counts are mechanism counts over this balanced grammar, not production failure rates.

Policies compared:

1. one stable key for the whole original effect;
2. segment key derived from plan ordinal;
3. segment key derived from immutable amount/range contract;
4. immutable range key plus claim epoch embedded in the logical identity;
5. conservation ledger: attempted segment contract is frozen until reconciled, resource observations are deduped by durable resource ID, only the proven remaining obligation can be replanned into disjoint immutable ranges, claim epoch stays separate, and unreconcilable ambiguity fails closed;
6. the same ledger but blind retry after durable status is absent and the old idempotency entry has expired.

## Result 1: whole-effect identity is too coarse once compensation is partial

`FULL` terminalized 1,488 scenarios and false-terminalized **992** of them. In the sharpest slice, the initial plan is `{40,60}`, the first 40 is confirmed, and the current-writer verifier is available. The whole-effect key marks the logical compensation as done after the first segment; it terminalizes and under-compensates **192/192** scenarios.

Therefore the stable logical compensation key from the previous leaf is necessary for the top-level obligation, but partial execution also needs stable subordinate segment/obligation identity.

## Result 2: ordinal segment identity is not stable under replanning

`ORDINAL` false-terminalized 600 scenarios overall. In the 64-case slice with initial `{40,60}`, takeover to `{60,40}`, verifier available, and the first segment confirmed or ambiguously applied, ordinal identity produced **56 false terminals**: 48 under-compensations and 8 duplicate-effect cases.

Ordinal `0` is a plan position, not an immutable effect contract. Replanning can make the same ordinal refer to a different amount/range, so an idempotency hit can suppress required work or an expired hit can allow overlapping work.

## Result 3: immutable range identity alone still does not authorize overlapping replans

`RANGE` improved identity stability but still false-terminalized 592 scenarios. In the same 64-case `{40,60} -> {60,40}` takeover slice it terminalized **64/64** unsafely, with duplicate application in all 64. The old `[0,40)` and the new `[0,60)` are distinct keys but overlap in authority.

This separates two proof obligations:

- *identity*: which exact segment contract did an effect attempt target?;
- *conservation authority*: is that segment still part of the currently unsatisfied obligation, disjoint from already-applied or unresolved work?

Range identity answers the first but not the second.

## Result 4: claim epoch must still stay out of logical segment identity

`RANGE_EPOCH` false-terminalized 816 scenarios overall. In the 32-case slice with takeover, same plan, ambiguous first application, no durable status, and verifier available, embedding the new claim epoch in the segment key caused **32/32 duplicate effects and false terminals**. The new writer is authorized, but it is still retrying the same logical compensation segment.

Thus claim epoch remains writer authority metadata, not a fresh compensation identity.

## Result 5: strong candidate = frozen attempted segment + unique-resource conservation ledger

`LEDGER_STRONG` safely terminalized **1,248** scenarios with **0 false terminals, 0 over-compensation terminals, 0 under-compensation terminals, and 0 duplicate external effects** in this model. It deliberately left 1,824 cases nonterminal, comprising verifier outage plus unreconcilable ambiguity.

The rule is:

1. a started segment gets an immutable logical contract, for example `H(original_effect_id, compensation_kind, contract_digest, range)`;
2. once attempted, that contract cannot be silently repartitioned until its status is reconciled;
3. sink resource observations are deduped by durable resource ID before amount/range conservation is computed;
4. resolved coverage is subtracted from the obligation;
5. only the proven remaining coverage may be repartitioned, and newly issued segments must be disjoint;
6. claim epoch/holder is checked separately at effect application;
7. terminality requires exact-once coverage of the original obligation, not just `sum(attempted amounts)==100` or a count of successful calls.

The repeated-same-kind verifier-available slice contained 768 scenarios; the strong policy terminalized 624 safely and produced **0 duplicate effects / 0 false terminals**.

## Result 6: resource IDs are evidence objects, not additive attempts

A focused 24-case control used a 100-unit original effect whose ambiguous first operation actually applied only 50, while the observed/status result duplicated the same single resource record. A naive raw-sum check saw `50 + 50` and false-terminalized **24/24**. Deduping by resource ID before conservation produced **0/24** false terminals in the strong policy.

So terminality should count unique durable effect resources bound to immutable satisfied ranges/amounts, not raw response/event multiplicity.

## Result 7: ambiguity past both status and idempotency remains fail-closed

There are 288 verifier-available scenarios with an ambiguous first outcome, no durable status, and the old idempotency record expired. `LEDGER_STRONG` terminalized **0/288** and created no duplicate effects. `LEDGER_BLIND` terminalized all 288, but **192/288** were false terminals with duplicate compensation because the hidden first attempt had already applied fully or partially.

The other 96 blind retries happened to be safe only because the hidden first attempt had not applied. From the available evidence, the protocol cannot distinguish those 96 from the 192 unsafe cases.

## Candidate protocol refinement

Maintain two levels of identity:

- top-level obligation key: `H(original_effect_id, compensation_kind, contract_digest)`;
- immutable segment key: `H(obligation_key, segment_range_or_amount_contract)`.

Maintain a monotonic conservation ledger under the top-level obligation:

- `SATISFIED`: unique durable resource IDs and exact covered range/amount;
- `AMBIGUOUS`: segment attempted but application truth not yet recoverable;
- `PENDING`: disjoint remaining obligation not yet attempted.

A takeover may change claim epoch but not an already-started segment key. Replanning may only partition `PENDING` coverage; it cannot rewrite `AMBIGUOUS` coverage. Parent terminality requires the union of unique `SATISFIED` coverage to equal the required obligation exactly, no overlap, no gap, and no unresolved segment.

## Generic protected boundary

The remaining generic protected requirement is now narrower and more explicit:

> The authoritative compensation sink must atomically enforce current writer authority **and remaining-obligation conservation** at effect application, and must expose durable enough effect identity/status to bind each applied resource to the immutable obligation segment. A CLEAN worker can derive keys, segment plans, ledgers, recovery checks and fail-closed continuations, but cannot install or globally validate that sink-side authority/conservation primitive.

Classification: `downstream_verification_required`. This is not a global Phase-1 pass claim.

## Exact continuation

Next non-conflicting Phase-1 leaf: **cross-original compensation conservation and late reversal**. Model two original irreversible effects/captures with independently required compensation totals, plus partial resources, takeover, ambiguous resource creation, and a later refund/reversal failure after an earlier `APPLIED` observation. Compare:

1. parent-level aggregate amount conservation only;
2. per-original-effect amount ledgers;
3. per-original immutable segment/resource ledgers;
4. an effect-vector terminality certificate that requires each resource's final status and binds it to the original effect/capture;
5. the same certificate with blind replacement of a late-failed resource.

Enumerate cross-original resource aliasing, a correct parent total applied to the wrong original effect, late `APPLIED -> FAILED/REVERSED`, resource-ID duplication, takeover between originals, ambiguous retry, and replan. Primary falsification: a parent-level conserved total can be exactly 100 while compensating the wrong original effect, and an `APPLIED` resource may cease to satisfy finality after a later reversal. Preserve the generic sink-side authority boundary and test whether final-status binding is an additional independent requirement.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
