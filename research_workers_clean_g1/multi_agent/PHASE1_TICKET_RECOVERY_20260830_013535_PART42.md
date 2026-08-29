# Phase-1 multi_agent checkpoint — ticket recovery, finite starvation bounds, and compaction (Part 42)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_WIDE_FAIRNESS_20260830_013535_PART41.md`

Part 41 showed that a cooperative wide REQUESTED ticket can stop *new* local work from extending a branch-ref starvation race, while old pre-ticket work remains safely handled by touched-manifest/ref conflicts. This leaf asks when that becomes a finite liveness claim rather than an informal expectation, and how the ticket itself can be recovered/compacted.

Executable model: `research_workers_clean_g1/multi_agent/phase1_ticket_recovery_20260830_part42.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_ticket_recovery_20260830_part42.json`

The recovery lattice has `3,840` scenarios and `19,200` strategy evaluations. A separate ticket-compaction lattice has `128` scenarios and `512` strategy evaluations. Counts are finite mechanism counts, not deployment probabilities.

## Result 1 — wall-clock expiry cannot mean automatic RELEASED

The required negative control treats a REQUESTED ticket as automatically released when its wall-clock lease appears expired, without a current repository authority transition. In the 1,440 scenarios where there is at least one interruption and the old owner later resumes, this policy is **1,440/1,440 unsafe**: local work can be admitted as though the ticket were gone while the old owner still possesses a proposal path that has not been fenced by a new ticket epoch.

The correct use of time is only as *eligibility to attempt takeover*. Expiry permits a worker to try a current-blob CAS such as:

`REQUESTED(ticket_epoch=e, owner=o1) -> RECOVERING(ticket_epoch=e+1, owner=o2)`

The higher epoch/current transition is the fence. Until that succeeds, local admission remains blocked or fails closed; time alone does not revoke the old authority.

This is the same lease-vs-fencing distinction found earlier for PREPARED manifests and external effects.

## Result 2 — a finite starvation bound needs an explicit finite-inflight contract

`epoch_recovery_no_declared_bound` is safe from stale old-owner publication in the model, but every one of its `3,840` scenarios remains marked **finite_starvation_bound_unproven**. Observing that the configured CLEAN pool contains a finite number of roles is not by itself a protocol bound on simultaneously in-flight operations; the runtime may overlap invocations or a role may have already-created work.

The strong bounded variant therefore makes `max_inflight` an explicit ticket/protocol contract rather than inferring it from the role count. It proves progress only when all of the following are true:

1. actual pre-ticket in-flight work is `<= max_inflight`;
2. new cooperative PREPARED admissions defer while the current ticket is REQUESTED/RECOVERING;
3. every interruption is followed by a fenced recovery epoch transition within the declared recovery budget;
4. wide branch retry budget is greater than the remaining in-flight conflicts plus interruption/recovery losses;
5. the final publication binds current ticket epoch/owner epoch/transition ID and uses response-loss reconciliation.

Across the full lattice, `epoch_recovery_declared_bound` has 920 scenarios in which those conditions are all met; **all 920 terminalize with a finite bound and stale-old-owner count 0**. It fail-closes the rest: 1,280 have no declared bound, 768 violate the declared bound, 672 exhaust the recovery-transition budget, and 200 exhaust the branch retry budget.

In the explicit `declared_bound=10` / `actual_inflight<=10` slice there are 1,024 scenarios. Exactly 500 also have enough retry/recovery budget and terminalize with a proved finite bound; 524 remain pending because a required budget is insufficient. The number 10 here is only a tested bound value, not an inference that the current scheduler guarantees at most ten peers in flight.

## Result 3 — repeated interruption is recoverable only as repeated authority transitions

A crash or repository rate-limit interruption after REQUESTED does not require a richer-mode rescue path. A later scheduled invocation can read the current ticket and, if takeover eligibility holds, CAS to a higher recovery epoch. Repeated interruptions consume repeated recovery transitions; the protocol does not pretend that one timestamp revokes every previous owner.

This keeps the accepted path within repository transport. A rate-limited invocation checkpoints and returns; a later invocation continues the same state machine. No optional hosted compute, finite monthly credit, or manual user action is added.

Response-loss after ticket takeover or final wide publication is reconciled from the current ticket/transition ID and branch ancestry/current state. Blind duplication is not required.

## Result 4 — strict global admission can remove the finite-inflight retry term, but recreates the steady-state hotspot

`global_root_every_admission` terminalizes 2,400/3,840 scenarios whenever recovery-transition budget is sufficient, because all local admissions contend on the same root after REQUESTED. The cost is **31,488 global-root touches** in this finite lattice.

That strategy gives a simpler liveness proof but violates the locality objective that motivated Parts 38–41. The cooperative ticket is therefore a conditional optimization: it avoids a global write on ordinary local work, but only earns a finite starvation claim when the finite-inflight contract is explicit and actually satisfied.

## Result 5 — ticket compaction needs an incarnation-sensitive retirement witness

The ticket-compaction lattice applies the same finality rule as Part 35 to the liveness ticket itself.

Deleting a terminal ticket merely because current old references look clean completes GC in 32 scenarios, but **16/32 become unsafe** when a stale old ticket/holder state is restored afterward. Current cleanliness is not a future non-reappearance proof.

A monotonic retirement floor scoped to the ticket/conflict-domain **incarnation** safely completes 16 requested-GC scenarios and blocks GC when the required retirement witness/incarnation proof is absent. By contrast, a floor keyed only by a reusable logical name falsely blocks **16** new-incarnation cases after key/domain recreation.

A permanent ticket tombstone is safe but retains all 128 modeled tombstones. Thus the compact accepted form remains the Part 35/39 pattern:

`retired_ticket_epoch[domain_incarnation] >= terminal_ticket_epoch`

All admission/recovery paths reject epochs at or below that floor. This result still inherits Part 36's complete-rewind boundary: if the floor and every other admissible witness are all restored to older identical bytes, the distinguishing evidence is gone.

## Repository/public mechanism mapping

The state machine uses GitHub Contents current-file SHA conflict behavior for ticket/manifest CAS and non-force branch publication for wide commits:

- Contents create/update file: https://docs.github.com/en/rest/repos/contents
- Git refs / non-force ref update: https://docs.github.com/en/rest/git/refs

No claim is made that these APIs provide a fairness scheduler. The finite bound is application-level and depends on the explicit in-flight/recovery contracts above.

## Phase-1 zero-dependency / zero-quota assessment

Accepted within tested scope:

- `REQUESTED -> RECOVERING -> APPLIED/RELEASED` with current-blob epoch fencing;
- time used only to authorize an attempted takeover, never as automatic release;
- cooperative local admission deferral;
- explicit finite `max_inflight` contract when a finite starvation bound is claimed;
- response-loss reconciliation by transition identity/ancestry;
- incarnation-sensitive ticket retirement watermark before terminal-ticket compaction.

All accepted operations are lightweight repository reads/writes/ref updates, zero incremental monetary cost, no optional monthly/trial/paid quota dependency, no hosted coordinator, and no richer-mode/manual/protected execution step. Rate-limit interruption remains checkpoint/recovery, not a quota-bearing compute route.

Still unresolved: how to establish/enforce a nontrivial finite `max_inflight` contract from the scheduled-Chat runtime itself without introducing a global per-admission write; noncooperative/legacy workers can still invalidate the liveness assumptions. Complete rewind, direct fixed-path consumers, and arbitrary external sinks remain unresolved as before.

## Exact continuation

Next Phase-1 leaf: **derive or falsify a zero-write finite-inflight witness for scheduled Chat**.

Test only CLEAN-admissible, zero-cost information sources and protocol constructions:

- repository ticket records of currently admitted PREPARED operations;
- one-per-role deterministic admission slot with incarnation/epoch and explicit release/takeover;
- bounded role slot + local operation queue;
- no-overlap assumption as a negative/unproven baseline;
- global root admission counter as the strong but hotspot baseline.

Required adversarial cases: same role overlapping two invocations, crash before release, late release after takeover, role-slot delete/recreate, scheduler replay/duplicate invocation, rate-limit interruption, and wide ticket acquisition while slots are stale. The target is either a repository-local proof that admitted in-flight work is bounded without a global write per local operation, or a precise unresolved boundary showing why a role-count-based bound is not derivable from current scheduled-Chat semantics.
