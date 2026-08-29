# Phase-1 partial/multi-resource compensation conservation under replanning

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_COMPENSATION_CLAIM_COLLISION_20260829_085803_PART19.md`
- script: `research_workers_clean_g1/multi_agent/phase1_partial_compensation_conservation_20260829_085803_part20.py`
- script SHA-256: `c5c84b04013cf88066f853190f1e307ceb35ffbe543c844028a6dac3ffa67db9`
- result: `research_workers_clean_g1/multi_agent/phase1_partial_compensation_conservation_20260829_085803_part20.json`
- result SHA-256: `ab972c3d2c4c286a64a13e2a3c25e990e2d1a91061f852caa3496665a89ce7d3`

## Objective

Extend compensation identity from a one-unit undo to partial/multi-resource compensation totaling exactly 100 units. The stress case permits an initial full `{100}` plan or split `{40,60}` plan, then a worker takeover that either keeps the plan or naively replans to `{50,50}`. Each actual sink apply creates a distinct compensation resource/effect, so correct parent terminality requires **amount/range conservation**, not merely “some compensation resource exists.”

The key question is what makes a partial segment identity stable across worker takeover and replanning. A full-effect key is too coarse; ordinal and amount-only keys are plan-relative/ambiguous; claim epoch is authority, not segment identity. The candidate is an immutable obligation range tied to the original effect, with replanning allowed only over the still-unfulfilled range.

## Finite model

The executable model enumerates **144 equal-weight synthetic scenarios** over:

- original compensation plan: `FULL100 / SPLIT40_60`;
- handoff: `NO_TAKEOVER / TAKEOVER_SAME_PLAN / TAKEOVER_REPLAN_50_50`;
- first segment truth/response: `CONFIRMED_APPLIED / AMBIG_APPLIED / AMBIG_NOT_APPLIED`;
- dedupe: `VALID / EXPIRED`;
- durable sink status: `DURABLE_STATUS / NO_STATUS`;
- current writer verifier: `AVAILABLE / OUTAGE`.

There are 72 verifier-available and 72 verifier-outage scenarios.

Policies:

1. one stable full-effect key reused for all partial requests;
2. segment key by ordinal within the current plan;
3. segment key by amount only;
4. segment key by ordinal plus claim epoch;
5. immutable original-effect range/obligation identity with fail-closed ambiguous recovery;
6. same range model but blind retry after status loss + dedupe expiry.

Each policy is evaluated against exact total compensation `100`; under- and over-refund are both false terminalization.

## Result 1: one full-effect key is too coarse for multiple partial resources

`single_full_effect_key` false-terminalizes **74/144** scenarios: 54 under-refunds and 20 over-refunds. In the 36 verifier-available split-plan scenarios, it under-refunds 27 and over-refunds 5, for **32/36** false terminalizations.

The root cause is that the same key is being asked to mean both “40-unit partial compensation” and “60-unit partial compensation.” With active dedupe/status, later distinct partial requests are suppressed as if they were retries of the first; without durable suppression, ambiguous retries can instead create duplicates.

A stable logical full compensation ID remains useful as the **parent obligation**, but it is not sufficient as the idempotency identity of every independently applied partial resource.

## Result 2: ordinal segmentation is not stable under replanning

`ordinal_segment_key` false-terminalizes 56/144 scenarios. It records **36 ordinal-replan payload collisions** where ordinal 0 is reused for a different amount/range after plan change.

In the 24 verifier-available takeover+replan scenarios, ordinal identity is wrong in **24/24**: 15 over-refunds and 9 under-refunds. When dedupe/status remembers old ordinal 0, the new 50-unit ordinal 0 can be suppressed by an earlier 100- or 40-unit request; when memory has expired, the changed ordinal can be applied again.

Therefore ordinal is a plan coordinate, not an immutable business/effect identity.

## Result 3: amount-only identity also aliases distinct ranges

`amount_only_segment_key` has the same aggregate terminality failure counts as ordinal identity: 56/144. Its distinct failure mechanism is explicit in **36 same-amount/different-range aliases**. After replanning to `{50,50}`, both distinct halves have the same amount and therefore the same amount-only key.

In the 24 verifier-available replan scenarios, 18 such range aliases are observed. Amount is part of a segment contract, but not a unique segment identity when separate obligation ranges can have equal size.

## Result 4: claim epoch makes segment identity less stable, not more

`claim_epoch_ordinal_key` changes namespace in 96 takeover scenarios and has **68 false terminalizations**, including 62 over-refunds. Aggregate over-refund amount is 4,740 synthetic units versus 2,580 for ordinal-only.

The fresh epoch is necessary to fence the new writer, but incorporating it into the segment's logical effect key causes the same immutable obligation range to look new after takeover. This repeats the previous whole-compensation result at segment granularity: **writer epoch must remain separate from logical effect identity**.

## Result 5: immutable obligation range + monotonic remaining-range planning is safe in tested scope

`range_contract_failclosed` terminalizes 60 scenarios and checkpoints 84: 72 verifier outages plus 12 ambiguous partial applications with no durable status and expired dedupe. Every terminal result compensates exactly 100 units; over-refund, under-refund and false terminalization are all 0 in the tested scope.

On takeover+replan, it does not discard the old segmentation and start `{50,50}` from zero. It first determines the already-satisfied immutable range, then replans only the remaining range. For a confirmed/reconciled 40-unit first segment, the remaining 60 can safely become `50+10`; for a confirmed 100-unit full compensation, replanning is a no-op. Across verifier-available replan scenarios it safely terminalizes 20 and checkpoints the 4 unreconcilable ambiguous cases.

This yields a more stable segment identity:

`segment_key = H(original_effect_id, compensation_kind, immutable_obligation_range, contract_digest)`

with claim/guard epoch stored separately as writer authority.

## Result 6: ambiguous partial apply remains a separate proof obligation

There are 12 verifier-available scenarios with ambiguous first application, no durable status and expired dedupe. The fail-closed range policy checkpoints **12/12**.

The blind-retry range policy terminalizes all 12 but duplicates the first range in the 6 `AMBIG_APPLIED` cases, causing **6/6 over-refunds** there. Aggregate excess is 420 synthetic amount units: three full-plan duplicates at +100 and three split-plan duplicates at +40.

Thus exact range identity prevents plan aliasing but cannot recreate lost apply/no-apply information. Durable sink status or still-valid idempotency is still required for safe ambiguous recovery.

## Candidate conservation ledger

For each original effect, maintain a durable obligation description independent of worker epochs:

`{original_effect_id, total_required, compensation_kind, satisfied_ranges -> durable sink effect IDs/status, remaining_ranges}`.

Rules:

1. required ranges cover the original obligation exactly once and do not overlap;
2. segment keys derive from immutable obligation ranges, not current ordinal, amount alone or claim epoch;
3. a takeover may repartition **only a currently unsatisfied range**, preserving its exact union;
4. each sink apply is fenced by current claim/guard epoch but records a durable resource ID against the stable range key;
5. parent terminality requires the union of uniquely satisfied ranges to equal the required obligation exactly, with no overlaps/gaps;
6. ambiguous segment apply without durable status/idempotency remains nonterminal.

## Generic protected boundary

The remaining generic sink requirement is now amount/range-aware:

> The compensation sink must enforce current writer authority and provide durable status/idempotency per immutable compensation segment/range. CLEAN can derive stable range contracts, detect overlap/gaps, replan the remaining obligation and checkpoint ambiguity, but cannot install or globally validate the protected sink invariant/status surface.

Classification: `downstream_verification_required`.

## Exact continuation

Next non-conflicting Phase-1 leaf: **two-original branching compensation DAG and global conservation**. Model two irreversible originals `{A:100, B:60}`, dependencies where B may only be compensated after A or independently, concurrent workers selecting rollback vs forward-complete branches, partial ranges, one ambiguous compensation, and a late reversal/failure of a newly issued compensation. Compare per-original independent ledgers, one parent aggregate amount ledger, a DAG terminality certificate over stable effect/range IDs, and greedy rollback. Test cross-original amount aliasing, branch double execution, compensation-of-compensation identity, false terminality and Pareto trade-offs between progress and irreversible risk.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
