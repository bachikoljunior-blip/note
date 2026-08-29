# Phase-1 multi-agent cross-original compensation conservation and final resource status

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_PARTIAL_COMPENSATION_CONSERVATION_20260829_092530_PART20.md`
- script: `research_workers_clean_g1/multi_agent/phase1_cross_original_finality_20260829_092530_part21.py`
- result: `research_workers_clean_g1/multi_agent/phase1_cross_original_finality_20260829_092530_part21.json`

## Objective

Extend the one-original conservation ledger to two independent irreversible effects/captures, required compensation vector `{A:60, B:40}`. Test whether parent-level amount conservation, intended routing metadata, or provisional resource success can substitute for authoritative per-original finality.

The model deliberately allows the total compensated amount to equal 100 while the wrong original effect receives the refund, allows a request intended for A to produce a sink resource bound to B, and lets a provisionally applied refund later become `FAILED` or `REVERSED` in the synthetic lifecycle.

## Public mechanism audit

Current Braintree/PayPal documentation provides useful external-effect precedents:

- Braintree transaction responses expose status history, including `settling`, `settled`, `settlement_declined`, `failed`, and related states: https://developer.paypal.com/braintree/docs/reference/response/transaction/python
- Braintree refund documentation distinguishes synchronous request success from processor settlement failure and exposes `settlement_declined`: https://developer.paypal.com/braintree/docs/reference/request/transaction/refund/python
- Braintree orchestration guidance for several processors explicitly warns that refund/capture can remain `SETTLING` after HTTP/API uncertainty and later reconcile to `SETTLED` or `SETTLEMENT_DECLINED`; for example: https://developer.paypal.com/braintree/docs/guides/orchestration/dlocal/

The synthetic `APPLIED -> FAILED/REVERSED` branch is therefore a generic provisional-to-final-state stressor. It is not a claim that every PayPal/Braintree refund can reverse after final settlement.

## Finite model

The executable model enumerates **8,000 equal-weight synthetic scenarios** over:

- initial allocation: correct, swapped amounts, cross-bound resources, all 100 on A, or all 100 on B;
- late status: stable, A failed, B failed, A reversed, B reversed;
- ambiguous creation: none, hidden applied/not-applied on A, hidden applied/not-applied on B;
- durable resource status: yes/no;
- old idempotency entry: valid/expired;
- takeover: no/yes;
- current writer verifier: available/outage;
- duplicate resource observation: no/yes;
- repeated same compensation kind: no/yes.

Policies:

1. parent aggregate amount only;
2. per-original amount using **intended request routing**;
3. per-original amount using authoritative sink-bound resource identity, but treating provisional application as final;
4. effect-vector certificate over unique sink-bound resources in final `SETTLED` state, with current-writer-fenced replacement for clearly failed/reversed resources and fail-closed behavior when final status is unavailable;
5. the same vector shape but blind retry/replacement when final status is unavailable.

Counts are mechanism counts over this synthetic grammar, not production failure rates.

## Result 1: exact parent total does not imply correct per-original conservation

`PARENT` terminalized 4,080 scenarios and false-terminalized **3,616**. A focused 32-case slice used stable final status, no ambiguity, verifier available, and a wrong initial allocation whose total was still 100. Parent-total conservation terminalized **32/32 falsely**.

This falsifies `sum(all compensation)==sum(all obligations)` as a sufficient terminality condition when obligations belong to distinct original irreversible effects.

The terminal certificate must preserve the vector structure, not only the scalar total.

## Result 2: intended routing metadata is not authoritative resource binding

`PER_INTENDED` terminalized 2,040 scenarios and false-terminalized **1,576**. In the focused 8-case `CROSS_BIND` slice, request A was intended to satisfy A but the sink resource was actually bound to B, and vice versa. Intended-route accounting terminalized **8/8 falsely**.

`PER_BOUND_PROVISIONAL`, which groups by the authoritative sink-bound original, terminalized 0/8 in the same slice. Thus request intent and sink effect identity are separate evidence domains.

## Result 3: correct resource binding is still insufficient if status is provisional

`PER_BOUND_PROVISIONAL` reduced false terminalization to 656 overall, but still treats the current observed resource as final. In the focused 64-case correct-allocation slice where one resource later became failed/reversed and durable final status was available, it false-terminalized **48** cases.

The strong effect-vector policy reconciled the final status, excluded the failed/reversed resource from satisfied amount, and—only when the current-writer verifier was available—issued a replacement keyed to the failed/reversed resource identity. It safely terminalized **64/64** with false terminalization 0 in this modeled slice.

The replacement identity is not a fresh claim epoch. It is derived from the failed/reversed resource being replaced so takeover does not create a second logically distinct replacement.

## Result 4: final-status vector + authoritative binding is safe in the tested lattice

`EFFECT_VECTOR_STRONG` terminalized **992** of 8,000 scenarios, all 992 exact, with **0 false terminals**. It fails closed on wrong-bound settled resources, over-allocation that cannot be repaired by adding compensation, missing final status, or verifier outage when a new effect would be required.

The certificate shape is:

`{original_effect_id -> unique(resource_id, authoritative_binding, amount/range, final_status)}`

with terminality only if every required original effect is exactly satisfied by final-settled resources and there is no over-allocation, wrong binding, or unresolved resource.

## Result 5: blind progress after status loss recreates the ambiguity problem

In 200 correct-allocation scenarios with no durable status, expired old idempotency, and current-writer verifier available, `EFFECT_VECTOR_STRONG` terminalized **0/200**. The blind variant retried and terminalized all 200, but **168/200 were false terminals** because already-created or later-failed resource truth could not be distinguished from a genuinely missing effect.

Only 32 blind retries happened to end with the exact vector. From the available observation they are indistinguishable from the unsafe 168 before retry.

## Candidate protocol refinement

Terminality is now a two-dimensional conservation proof:

1. **segment conservation within each original effect** from Part20;
2. **effect-vector conservation across original effects** from this leaf.

For every authoritative sink resource, retain:

- durable resource/effect ID;
- authoritative original effect/capture binding;
- immutable amount/range contract;
- current final status or a status-version proof;
- replacement lineage if a failed/reversed resource is superseded.

Do not infer finality from parent scalar totals, intended request routing, raw webhook multiplicity, or a provisional applied state.

## Generic protected boundary

The remaining generic protected requirement is:

> The authoritative sink/status domain must expose final resource status **and authoritative original-effect binding**, while any replacement effect must be current-writer fenced and durably keyed to the specific failed/reversed resource. CLEAN can construct vector certificates, recovery/replacement identities and fail-closed checks, but cannot install or globally validate those sink-side primitives.

Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Exact continuation

Next non-conflicting Phase-1 leaf: **status-version and observation-order fencing for effect-vector finality**. Keep two originals but add status events with version/sequence `{1,2,3}`, delayed/out-of-order webhook delivery, stale replica reads, replacement creation between observations, and takeover. Compare:

1. last-arriving-event wins;
2. terminal status string only, no version;
3. per-resource monotonic status version but no authoritative read fence;
4. authoritative current read plus monotonic version and replacement lineage;
5. fail-closed certificate when current version cannot be proven.

Primary falsification: even a correct per-original resource vector can be false if a stale `SETTLED` observation arrives after a newer failure/reversal or if replacement is certified against an old resource version. Measure false terminality, duplicate replacement, stale-status acceptance and recoverability. Preserve the current generic sink-side authority/finality boundary and determine whether a monotonic resource-version primitive is an additional independent requirement.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
