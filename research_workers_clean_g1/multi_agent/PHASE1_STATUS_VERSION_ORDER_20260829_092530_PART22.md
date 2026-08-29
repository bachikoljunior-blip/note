# Phase-1 multi-agent status-version and observation-order fencing

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_CROSS_ORIGINAL_FINALITY_20260829_092530_PART21.md`
- script: `research_workers_clean_g1/multi_agent/phase1_status_version_order_20260829_092530_part22.py`
- result: `research_workers_clean_g1/multi_agent/phase1_status_version_order_20260829_092530_part22.json`

## Objective

Stress the Part21 effect-vector certificate when status evidence arrives out of order, the newest event is missing, an API read is stale, or recovery repeats across takeover. Current resource truth is modeled at status version 3; versions 1 and 2 are older observations (`PENDING`, then `SETTLED`), while version 3 is `SETTLED`, `FAILED`, or `REVERSED`.

The core question is whether a resource vector whose IDs/bindings are correct can still false-terminalize because the *status witness* is stale.

## Public mechanism audit

PayPal's current webhook guidance provides a direct ordering precedent: it documents at-least-once duplicate delivery, explicitly says events can arrive out of order, and recommends fetching current resource status instead of trusting arrival order: https://developer.paypal.com/api/invoicing/webhooks/

PayPal also exposes event-resend tooling, so an old notification can be observed again later: https://developer.paypal.com/api/rest/webhooks/events-dashboard/

GitHub similarly exposes webhook redelivery and unique delivery identifiers, which is another public example where delivery order/multiplicity is not itself business-state authority: https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/redelivering-webhooks and https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks

These sources motivate the mechanism class only. The version/finality protocol below is a synthetic repository-level conclusion.

## Finite model

The executable model enumerates **1,512 equal-weight synthetic scenarios** over:

- current v3 truth: `SETTLED / FAILED / REVERSED`;
- webhook delivery pattern: in-order, reverse, stale settled after v3, missing v3, only v2, only v3, duplicated v3 then stale v2;
- status API read: current v3, stale v2, unavailable;
- durable prior witness: none, v2, current-proven v3;
- takeover: no/yes;
- current-writer verifier: available/outage;
- repeat recovery: no/yes.

Policies:

1. last-arriving event wins;
2. highest version among webhook events only;
3. trust the status string returned by a read, without freshness/version fencing;
4. choose the maximum version among all observed events/read/witness, but without proof that no higher unseen version exists;
5. require a current-v3 proof from an authoritative current read or a previously persisted current-proven v3 witness; replacement identity is stable over `{resource_id, failed_status_version}`;
6. the same current proof, but replacement identity incorrectly includes claim epoch.

Counts are synthetic mechanism counts, not production failure rates.

## Result 1: arrival order is not status authority

`LAST_ARRIVAL` terminalized 1,152 scenarios and false-terminalized **576**. In the 72-case slice where truth is failed/reversed but delivery is `v1 -> v3 -> stale v2 SETTLED`, last-arrival handling false-terminalized **72/72**.

Thus event arrival time and resource-state order are independent axes.

## Result 2: monotonic event version is necessary but not sufficient when the newest event can be missing

`MONOTONIC_EVENT` reduced false terminalization to 288, but a focused 144-case slice omitted v3 and delivered only v1/v2 or v2. The highest delivered version was therefore stale `SETTLED`; the policy false-terminalized **144/144** when current truth was failed/reversed.

A monotonically processed event sequence proves only `max(delivered)`, not `max(current)` unless delivery completeness is itself guaranteed.

## Result 3: a status read without freshness/version proof can be just another stale observation

`READ_STRING` false-terminalized 528 scenarios. In 168 cases where truth was failed/reversed and the status read returned stale v2 `SETTLED`, it false-terminalized **168/168**.

This distinguishes *querying* from *authoritative currentness*. A read must carry a freshness/current-version contract strong enough for terminality.

## Result 4: maximum observed version still cannot prove absence of an unseen higher version

`MAX_SEEN_VERSION` false-terminalized 128 scenarios. In the 64-case slice with missing v3, no current-v3 read, no persisted v3 witness, and verifier available, the maximum observed version remained v2 and the policy false-terminalized **64/64**.

The strong policy terminalized **0/64** in the same slice.

Therefore the certificate needs a *current-version proof* or an explicitly absorbing finality token, not merely a locally monotonic counter.

## Result 5: current-version proof removes stale-status false terminality in this lattice

`CURRENT_PROOF_STRONG` terminalized **560** scenarios, all 560 exact, with **0 false terminals** and **0 duplicate replacements**. It treats webhook events as triggers/advisory evidence and terminalizes only when either:

- an authoritative current read proves v3, or
- a previously persisted witness already proves current v3 in this finite model.

When v3 says failed/reversed, replacement identity is `H(resource_id, failed_status_version, replacement_contract)` and claim epoch remains separate writer-authority metadata.

## Result 6: replacement identity must not inherit takeover epoch

A focused 70-case slice has current-proven failed/reversed v3, verifier available, takeover, and repeated recovery. If replacement identity includes claim epoch, the same failed resource becomes one replacement under epoch 1 and another under epoch 2. The negative control produced **70/70 duplicate replacements and 70/70 false terminals**.

The stable `{resource_id, failed_status_version}` replacement identity produced **0/70** duplicate replacements and false terminals.

This extends Part19's identity rule: logical recovery identity is tied to the failed effect/version being repaired, not to the worker that happens to hold the claim.

## Candidate protocol refinement

For each sink resource, maintain a durable status witness containing:

- resource ID and authoritative original-effect binding;
- immutable amount/range contract;
- monotonic resource status version/sequence;
- status value;
- provenance proving whether the version is merely observed or **current-proven**;
- replacement lineage keyed to `{resource_id, failed_status_version}`.

Webhook/event processing may update a local lower bound but cannot by itself certify currentness if delivery can be incomplete. A terminal effect-vector certificate must either possess a current-version proof for every resource or an absorbing finality token whose semantics guarantee no later invalidating transition.

## Generic protected boundary

The generic protected requirement is now:

> The authoritative sink/status domain must expose a current-version/freshness primitive or an absorbing finality token for each effect resource. CLEAN can dedupe/version webhook events, persist lower bounds, construct replacement lineage and fail closed, but cannot turn a stale replica, missing webhook, or merely highest-observed version into current authority.

Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Exact continuation

Next non-conflicting Phase-1 leaf: **status-read to terminal-commit TOCTOU**. Add the race `authoritative current read(v3) -> sink transitions to v4 -> repository parent terminal CAS`, plus replacement creation between read and commit. Compare:

1. read-current then terminalize without binding the read version;
2. persist v3 witness then repository-only CAS;
3. re-read immediately before repository CAS;
4. terminal commit that carries an expected sink resource version/finality token validated in the same authoritative sink domain;
5. absorbing finality-token design where no later invalidating transition is legal.

Enumerate `v3 SETTLED -> v4 FAILED/REVERSED`, `v3 FAILED -> replacement -> v4 old-resource SETTLED`, response loss, takeover, and repeated terminal CAS. Primary falsification: even a genuinely current read is stale the instant the sink can transition after the read unless terminal publication is fenced by the same resource version or the observed state is semantically absorbing. Measure false terminality, duplicate replacement and safe fail-closed recovery.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
