# Phase-1 multi_agent checkpoint — wide-operation admission and fairness (Part 41)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_STABLE_DOMAIN_CONTENTION_20260830_013535_PART40.md`

Part 40 found a hybrid safety shape: local stable-domain work uses file-SHA manifest CAS, while a cross-domain operation uses a non-force branch publication that updates every touched local manifest atomically. This leaf tests the liveness problem that remains: continuous unrelated local commits can keep invalidating the wide proposal's branch base.

Executable model: `research_workers_clean_g1/multi_agent/phase1_wide_fairness_20260830_part41.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_wide_fairness_20260830_part41.json`

The finite lattice has `576` scenario shapes and `2,880` strategy evaluations over 0/1/2/4 local operations already in flight, 0/2/8 new local attempts, retry budgets 1/2/4/8, normal owner vs crash vs rate-limit interruption, takeover/no takeover, and wide-publication response loss.

## Result 1 — non-force ref safety does not imply starvation freedom

`no_ticket_branch_retry` remains safe because a local commit that moves the branch makes the old wide proposal fail its non-force ref update. But in the 64 normal-owner scenarios with eight available local commits after the wide attempt starts, **64/64 bounded retry attempts exhaust** for retry budgets up to eight under an adversarial schedule that places one local commit before every wide ref update.

Across the whole lattice the no-ticket strategy terminalizes 128/576 scenarios and leaves 256 retry-exhausted scenarios. This is not a Git correctness bug; it is the distinction between conflict detection and fairness.

GitHub's `force=false` ref update gives the safety conflict, not an admission scheduler:
https://docs.github.com/en/rest/git/refs

## Result 2 — a durable cooperative REQUESTED ticket can bound new interference without becoming the safety fence

The tested ticket protocol separates liveness and safety:

1. wide owner CASes one durable ticket to `REQUESTED(wide_id, ticket_epoch, owner_epoch)`;
2. a worker starting a **new** local PREPARED transition reads the ticket first and defers while REQUESTED;
3. local operations that were already in flight before the ticket may still commit once; the ticket read is deliberately *not* treated as an atomic safety predicate;
4. wide owner retries its branch proposal from the newest base; the proposal atomically updates every local manifest whose effects it overlaps and carries the ticket/transition identity;
5. if an overlapping pre-ticket local commit wins first, the wide ref update fails and retries; if wide wins first, that local worker's old manifest SHA fails later;
6. when the finite pre-ticket in-flight set has drained, no new cooperative local admission is added, so the next wide retry can publish;
7. ticket release is included in the successful wide publication or performed by a fenced takeover/recovery transition.

This avoids the Part 39 TOCTOU mistake because the ticket is **not** used as the correctness fence. A local worker that slips after an old ticket read is still safe; it merely causes another wide ref conflict. Safety remains in the touched-manifest SHA and non-force branch publication.

In the 64 normal-owner scenarios with eight post-ticket local attempts, the cooperative ticket defers all 512 such attempts. It terminalizes 40/64 scenarios; the remaining 24 exhaust only because the chosen retry budget is not greater than the finite number `k` of pre-ticket operations. The tested deterministic condition is `retry_budget > k`.

This is a useful liveness result but not an unbounded fairness theorem. It assumes a finite set of pre-ticket in-flight operations and cooperative new workers that honor the current ticket.

## Result 3 — ticket ownership needs the same epoch fencing as work ownership

A crash or repository rate-limit interruption can leave REQUESTED behind. Simply allowing a new owner to continue the same logical ticket without changing a fencing epoch is unsafe: in 192 interruption+takeover scenarios, the no-epoch variant terminalized 120, and **all 120** successful takeovers leave an unsafe late-old-owner publication path in the model.

With `ticket_epoch / owner_epoch` takeover fencing, the corresponding 192-scenario slice still terminalizes 120 when retry budget is sufficient, but stale old-owner publication is **0** and all 120 successful takeovers are reconciled under the higher epoch.

The old owner cannot publish by time expiry alone. Takeover must be a current authority transition, and the final wide commit must bind the current ticket epoch/owner epoch/transition ID. Lost publication responses are reconciled by ancestry or the persistent transition ID rather than blind retry.

## Result 4 — stronger fairness by putting every local admission on one global root buys liveness with a permanent hotspot

`global_root_every_admission` makes every local admission conflict directly with the wide REQUESTED transition. In the model it terminalizes 384 scenarios, more than the cooperative-read ticket, but incurs **3,504 global-root touches** and defers 2,928 local attempts across the finite lattice.

That is the same trade-off identified earlier: a root CAS can turn liveness control into a strict per-operation fence, but it also turns the root into the steady-state serialization point that the local-manifest design was intended to avoid.

The cooperative ticket is therefore preferable when its assumptions hold: the global ticket is normally a read-only admission signal for local work and a write hotspot only when a wide operation requests priority. Repository API reads/writes remain transport, not compute; rate limits are handled by checkpoint/recovery.

## Scope and acceptance

Accepted within the tested stable-domain/no-complete-rewind/cooperative-worker scope:

- a durable REQUESTED ticket can improve wide-operation starvation behavior without being used as a false cross-file safety predicate;
- local safety remains manifest-SHA fencing;
- wide safety remains non-force branch publication that changes all touched manifests;
- ticket takeover requires an incarnation/epoch/transition identity;
- response loss requires readback/ancestry reconciliation.

The mechanism uses only lightweight repository reads/CAS/ref publication, no richer-mode/manual/protected execution step, no external hosted coordinator, no finite monthly/trial/paid quota, and zero incremental monetary cost.

Unresolved boundaries remain:

1. no hard starvation guarantee if pre-ticket work can be unbounded or some workers ignore/never observe REQUESTED;
2. an owner interrupted after REQUESTED can temporarily block local admissions until a later invocation performs fenced recovery;
3. complete same-domain rewind;
4. direct fixed-path consumer parity;
5. arbitrary external sink authority/idempotency.

## Exact continuation

Next leaf: **ticket recovery under bounded recurring-pool assumptions and repeated scheduler/rate-limit interruption**.

Use the sanitized pool size only as a bound candidate, not as an assumption of one-inflight-per-role. Compare:

- finite `max_inflight` contract stored in ticket vs no such contract;
- takeover only after explicit owner epoch CAS;
- `REQUESTED -> RECOVERING -> APPLIED/RELEASED` state machine;
- local admission while ticket lease looks expired but has not been authority-transitioned;
- repeated interruption across multiple invocations;
- ticket response-loss and duplicate recovery;
- abandoned ticket compaction using the Part 35/39 incarnation+retirement-witness rules.

Required negative control: treating wall-clock expiry as automatic RELEASED. Measure stale owner publication, false local unblock, indefinite exclusion, number of repository authority touches, and the exact assumptions needed for a finite starvation bound.
