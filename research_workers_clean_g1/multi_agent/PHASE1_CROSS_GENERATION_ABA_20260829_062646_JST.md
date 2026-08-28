# Phase-1 cross-generation cancellation/compensation ABA and effect-incarnation identity

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `f6b3c1273f7abb3685198ce5dbbc2368151eca6c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_AUTHORIZATION_CANCEL_COMPENSATION_20260829_062646_JST.md`
- semantic inputs: own current invocation state, public Kubernetes/Stripe/AWS documentation, and one finite synthetic ABA model.
- mechanism script SHA-256: `32b7ff44df009c8cdfeef97c0b76c1347904628abc3e759b6807bda9d51c6177`
- mechanism result SHA-256: `9b3572453d0233b78e59196bbcec9cba405888da0bae8f98c28e03e08ceb09f1`

## Leaf objective

The predecessor leaf made cancellation/compensation explicit after an irrevocable `AUTHORIZED(effect_id)`. This leaf adds **generation reuse**: generation g1 may leave a delayed cancel or compensation behind while generation g2 later re-authorizes the same logical task/effect key.

The failure question is an ABA problem. A human-readable/logical name can become current again while delayed work from an older incarnation still exists.

## Public mechanism boundary

Kubernetes explicitly separates object **Name** from object **UID**: a deleted object can later be recreated with the same name, while each object created over the cluster lifetime has a distinct UID intended to distinguish historical occurrences of similar entities. That is a direct public precedent for treating a reusable logical key and an incarnation identity as different fields.

Stripe's idempotency documentation also makes retry retention finite: keys can be removed after they are at least 24 hours old, and a request using a pruned key is treated as a new request. Amazon SQS FIFO similarly documents a 5-minute deduplication interval; AWS SDK/API guidance warns that a resend after the deduplication interval can no longer be recognized as the earlier duplicate. These are public examples that a stable-looking request key is not a permanent replay fence.

Sources:
- https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
- https://docs.stripe.com/api/idempotent_requests
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagededuplicationid-property.html

## Finite model

The executable script enumerates **768 equal-weight synthetic scenarios** over:

- delayed old operation: `cancel` or `compensate`;
- g1 effect state: `PENDING / APPLIED`;
- g2 current state: `PENDING / APPLIED`;
- historical g1 effect still addressable or not;
- g1 repair quiescent or still legitimately required;
- old operation response: clear applied / ambiguous applied / ambiguous absent;
- takeover absent/present;
- dedupe contract still valid/expired;
- per-incarnation tombstone present/absent.

Policies:

1. `logical_key_reuse` — old work targets the reusable logical key, so after g2 appears it may act on g2.
2. `unique_per_generation` — old work carries g1's immutable effect identity, but historical routing and retry dedupe are separate requirements.
3. `watermark_only` — sink rejects all operations from generations below current minimum.
4. `tombstone_per_incarnation` — keep a historical incarnation/single-use witness for old repair.
5. `safe_archive` — current logical slot is generation-fenced; historical repair uses immutable g1 effect identity and tombstone/dedupe evidence; compaction to a watermark is allowed only after historical repair is quiescent.

## Aggregate result

| policy | safe terminal | unsafe | mis-cancel | mis-compensation | duplicate compensation | orphan repair |
|---|---:|---:|---:|---:|---:|---:|
| logical-key reuse | 240 | **400** | **160** | **160** | 16 | 32 |
| unique per generation | 636 | 4 | 0 | 0 | 4 | 96 |
| watermark only | 576 | 0 | 0 | 0 | 0 | **192** |
| per-incarnation tombstone | 656 | 0 | 0 | 0 | 0 | 96 |
| safe archive | **680** | **0** | 0 | 0 | 0 | **48** |

Counts are equal-weight synthetic mechanisms, not empirical incident rates.

## Result 1: reusable logical keys create a real ABA target

Across the full lattice, `logical_key_reuse` produces **160 cross-generation mis-cancels** and **160 cross-generation mis-compensations**. In the 384-scenario slice where g2's state is vulnerable to the old operation (`cancel` while g2 is pending, or `compensate` while g2 is applied), this baseline is unsafe in **320 / 384** scenarios.

A current logical name is therefore not enough to identify the intended historical effect. The old operation must carry an immutable effect-incarnation identity.

## Result 2: unique incarnation identity fixes ABA but not retry ambiguity

`unique_per_generation` eliminates all g1→g2 mis-cancel and mis-compensation in this model. It still has **4 unsafe duplicate-compensation scenarios**, all in the targeted slice:

`g1 compensation is still legitimate + g1 is historically addressable + first compensation response ambiguous but actually applied + takeover + dedupe contract expired`.

That slice has 4 scenarios and `unique_per_generation` duplicates in **4 / 4**. Per-generation identity answers **which effect**; it does not answer whether an ambiguous repair request may be retried.

## Result 3: a minimum-generation watermark is an ABA fence but can orphan legitimate history

There are **192** scenarios where a legitimate historical g1 repair still remains. `watermark_only` rejects every g1 operation once minimum generation becomes 2, producing **192 / 192 orphan repairs**.

By contrast, when `repair_quiescent=true`, the dedicated 384-scenario slice shows `watermark_only` safe-terminal in **384 / 384**. This gives a precise compaction rule:

> a current-generation lower-bound watermark can replace historical per-incarnation repair state only **after** all legitimate historical repair for the retired generation is final/quiescent.

Before that point, the watermark is too coarse because it cannot distinguish a dangerous stale mutation of the current logical slot from a legitimate repair of an older immutable effect.

## Result 4: current-slot fencing and historical-repair routing are separate authority planes

The `safe_archive` keeps the current logical slot fenced by generation while allowing old repair only through an immutable historical effect identity. It has unsafe 0 and reduces orphan repair to **48**, exactly the slice where a legitimate repair exists but **neither** an immutable historical route nor a per-incarnation tombstone remains.

This means the safe state cannot be compressed to a single `{logical_key, min_generation}` record while historical repair is still possible. A small permanent/retained historical witness is needed until repair quiescence.

## Candidate protocol

1. Use a reusable `logical_effect_key` only for the current slot.
2. Mint a distinct immutable `effect_incarnation_id = H(logical_key, parent_generation, authorization_id)` for every authorization.
3. Every cancel/compensation record names the exact effect incarnation it repairs; never resolve an old repair through the current logical key.
4. Maintain a current-slot `minimum_generation` (or equivalent fencing epoch) so old-generation publications cannot attach to the new incarnation.
5. Maintain historical repair routing/witness for each incarnation until its cancellation/compensation vector is final and all source-qualified retry/replay horizons are quiescent.
6. Treat request dedupe retention separately from incarnation identity. After a sink's dedupe window expires, ambiguous old repair cannot be retried merely because the effect ID is still unique.
7. A per-incarnation tombstone/single-use repair witness can reconcile ambiguous old repair and block duplicate compensation.
8. Compact per-incarnation state into a logical-slot generation watermark only after a quiescence certificate proves no legitimate historical repair can still arrive or be required.
9. If historical routing/tombstone was lost before quiescence, fail closed/manual rather than retarget the current logical key.

## Exact tested scope

- Two generations only, one logical effect slot, one delayed old operation.
- g1 state simplified to pending/applied and g2 to pending/applied.
- Compensation duplication is modeled as additive; repeated cancel of the same immutable old effect is treated as state-idempotent.
- No partial amounts, multi-effect DAG, Byzantine storage, identity collision, or clock skew.
- Dedupe retention is boolean rather than provider-specific time arithmetic.
- Counts are equal-weight synthetic mechanisms, not production rates.

## Exact Phase-1 continuation

Continue with **repair-quiescence certificates and tombstone/watermark compaction under replay-horizon drift**.

Next grammar:

- per-incarnation witness states `ACTIVE / REPAIR_PENDING / FINAL / COMPACTED`;
- replay-source registry epoch and source retention horizons;
- quiescence proof may be current, stale, or incomplete;
- compaction before/after dedupe expiry;
- new replay source or retention extension after compaction;
- old delayed repair after compacted watermark;
- current generation advances again to g3;
- compare permanent tombstone, finite TTL tombstone, registry-epoch fenced compaction, monotonic source-retirement barrier, and safe archive;
- measure ABA resurrection, lost legitimate repair, duplicate compensation, false quiescence, retained-state cost, and safe compaction coverage;
- test whether a monotonic **repair-retirement lower bound** can compact per-incarnation tombstones without blocking a still-legitimate historical compensation.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
