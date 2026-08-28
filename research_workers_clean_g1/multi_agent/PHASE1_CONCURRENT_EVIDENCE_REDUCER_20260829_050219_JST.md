# Phase-1 concurrent evidence reducer / out-of-order lifecycle stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple: note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- later SHA-only head recheck after role-local writes: `469bddba18c0a6edc01ffb9974b584ed37c23bc3`; root/config path/blob-only identity checks remained exactly `e4f6d24...` / `9a3edbe4...`, so revision-22 identity-based post-freeze continuation remained valid. No newer-head semantic content was adopted.
- semantic inputs: own Phase-1 effect-vector terminality checkpoint/result, public Stripe/AWS documentation, and this finite synthetic model only.

## Leaf objective

The preceding leaf made parent terminality a reduction over unique original-effect and compensation identities. This leaf asks how two independent reconcilers should merge asynchronous evidence for the same identity when delivery is duplicated, delayed, out of order, or mixed with a stale prior attempt.

The failure modes are generic coordination problems:

- the same event can be delivered more than once;
- a later terminal transition can arrive before an earlier event;
- wall-clock/event timestamps can tie or be misleading for causal order;
- an event from a prior object/attempt can arrive after the current attempt;
- a stale reducer can write after a current reducer takeover;
- two reducers can independently trigger the same compensation.

## Public mechanism evidence

Stripe's webhook documentation states that event delivery order is **not guaranteed**, warns that snapshot events can share the same `created` timestamp, says not to use `created` to determine ordering or duplicate processing, and recommends tracking event IDs because duplicate deliveries can occur. It also documents automatic/manual retries.

- https://docs.stripe.com/webhooks

AWS S3 Event Notifications similarly documents at-least-once delivery, no guarantee that notifications arrive in event order, and rare duplicate notifications. Amazon EventBridge documents at-least-once delivery for durable service events and does not generally provide message ordering.

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html
- https://docs.aws.amazon.com/eventbridge/latest/ref/event-delivery-level.html

These sources support the generic assumption that reducers must tolerate duplicate/out-of-order evidence. They do not define the synthetic reducer semantics below.

## Finite model

The executable enumerates **3,456 equal-weight synthetic scenarios** over:

- six current-object lifecycle families: success, late failure, reversal, pending, local acceptance then success, local acceptance then failure;
- optional stale prior-attempt (`X1`) terminal evidence while the certificate's current identity is `X2`;
- six delivery partitions across reconcilers A/B, including split, reverse, duplicate-to-both, partial/full, stale/current, and local-vs-provider evidence;
- timestamps that are ordered, tied to the same second, or make stale prior-attempt evidence appear newer;
- authoritative current-status lookup present/absent;
- reconciler A current vs stale epoch;
- A-then-B vs B-then-A canonical write order.

Compared reducers:

1. `root_lww` — last worker/local observation wins.
2. `timestamp_lww` — max event timestamp wins; ties break by processing order.
3. `naive_enum` — globally ranks states `PENDING < ACCEPTED < SUCCEEDED < FAILED < REVERSED`, ignoring object identity.
4. `event_set_unfenced` — event-ID dedupe and source-qualified reduction per worker, but both workers can publish canonical summaries/triggers without reducer fencing.
5. `fenced_source_reducer` — append/dedupe immutable event IDs, filter by current object identity, keep local acceptance nonterminal, resolve conflicting authoritative terminal evidence with current status when available or remain nonterminal, and let only the designated current reducer publish/trigger.

## Main results

| reducer | correct terminal coverage | false terminals | stale evidence accepted | missed late failure/reversal | duplicate compensation-trigger scenarios |
|---|---:|---:|---:|---:|---:|
| root_lww | 1,680 / 3,456 = 48.61% | **1,128 (32.64%)** | 1,296 | 408 | 1,008 |
| timestamp_lww | 2,000 / 3,456 = 57.87% | **1,000 (28.94%)** | 1,296 | 280 | 1,008 |
| naive_enum | 2,016 / 3,456 = 58.33% | **1,296 (37.50%)** | **1,776** | 0 | 0 |
| event_set_unfenced | 1,440 / 3,456 = 41.67% | **408 (11.81%)** | 0 | 408 | 192 |
| fenced_source_reducer | **2,304 / 3,456 = 66.67%** | **0** | **0** | **0** | **0** |

The strong reducer leaves **1,152** scenarios unresolved rather than guessing; those include genuinely pending truth or conflicting authoritative evidence without the modeled current-status capability. Counts are finite mechanism counts, not production failure rates.

## Result 1: last-write-wins is not an evidence merge

`root_lww` false-terminalizes 1,128 scenarios and accepts stale prior-attempt evidence in 1,296 scenarios. Canonical state depends on which reducer happens to commit last, so a stale worker can regress a newer summary even when both pieces of evidence remain available elsewhere.

In the explicit `stale_reducer_commits_last` slice (864 scenarios), root-LWW produces **516** false terminals. Source-aware event reduction without a reducer fence improves that to 156, but still fails because a stale reducer can publish a summary computed from a partial view after the current reducer.

The fenced reducer has **0** false terminals in this slice: workers may append evidence, but canonical reduction/trigger authority is single-current-epoch.

## Result 2: timestamp LWW does not recover causal order

Stripe explicitly warns that distinct events can share the same second-level `created` timestamp and that `created` should not be used to determine event order. The model's `tie_timestamp_late_terminal` slice has 384 late-failure/reversal scenarios with tied timestamps.

- timestamp-LWW: **160 false terminals**, including **112 missed late failures/reversals**;
- root-LWW: the same 160 / 112;
- fenced source reducer: **0 / 0**.

A stale prior-attempt event is also allowed to have a newer delivery/event timestamp in another profile; object identity therefore has to fence evidence before any ordering rule is considered.

## Result 3: a global monotonic enum is not provider-generic finality

`naive_enum` avoids missing a current failure/reversal in this specific rank order, but it ignores attempt identity. In the `stale_prior_attempt_vs_current_success` slice (288 scenarios), stale `X1` FAILED/REVERSED evidence competes with current `X2` success:

- naive enum: **288 / 288 false terminals and stale-evidence acceptance**;
- root-LWW/timestamp-LWW: 144 / 288 false terminals;
- both source-aware current-identity reducers: 0.

This is why the terminality certificate must bind evidence to the exact `effect_id` / `compensation_id` (and attempt generation where applicable) before reducing state. A single cross-provider enum such as `SUCCEEDED < FAILED < REVERSED` is not a substitute for object identity and source semantics.

## Result 4: immutable event sets help, but reducer authority is a separate fence

`event_set_unfenced` deduplicates evidence IDs and never accepts stale `X1` as current `X2`, cutting false terminals sharply. It is still unsafe under concurrent canonical writers:

- **408** false-terminal scenarios overall;
- **156** in the stale-reducer-commits-last slice;
- **192** duplicate compensation-trigger scenarios.

The event log provides replay/recovery evidence, but a stale summary writer can still publish a partial reduction, and two reconcilers can independently trigger the same compensation.

The candidate therefore separates:

- many-writer idempotent **evidence append**;
- one-current-epoch **canonical reducer/trigger authority**;
- deterministic trigger identity so duplicate evidence never means duplicate compensation.

## Result 5: duplicate event handling must happen before side effects

In the 576-scenario `duplicate_delivery` slice:

- root-LWW: **288** duplicate compensation-trigger scenarios;
- timestamp-LWW: **288**;
- event-set-unfenced: **192**;
- fenced source reducer: **0**.

Stripe's documented duplicate-delivery guidance maps directly to the first layer: persist/process event identity idempotently. The model adds a second generic coordination requirement: even perfectly deduped evidence must not be allowed to produce the same exclusive compensation from two unfenced reducers.

## Candidate reducer protocol

1. Bind every evidence record to canonical `{effect_or_compensation_id, attempt/generation, source, provider_event_id_or_status_observation_id}`.
2. Append evidence idempotently by event/observation identity; duplicate delivery changes no logical state.
3. Never treat local request acceptance as final provider effect state.
4. Ignore evidence for stale prior attempt/object identities when reducing the current certificate, while retaining it for audit/history.
5. Do not infer causal order from wall-clock/event timestamps unless the source explicitly guarantees that order. Tied timestamps remain ties.
6. If the current identity has conflicting authoritative terminal evidence and the provider-specific transition rule is not proven, query authoritative current status when available; otherwise remain nonterminal.
7. Canonical summary publication and compensation triggering require the current reducer/integrator epoch. Evidence append can remain multi-writer.
8. Use deterministic trigger identity linked to the current effect/compensation identity and desired recovery transition so replayed evidence or reducer restart cannot create duplicate compensation.
9. Rebuild canonical terminality by replaying the event set plus authoritative status evidence; the root Boolean remains a derived cache/certificate, never the sole source of truth.

## Scope limits

- Synthetic finite grammar only.
- The strong reducer is told which object identity (`X2`) the current parent certificate expects. Discovering/rebinding identity itself is outside this leaf.
- Authoritative status lookup returns synthetic current truth when available. Real APIs have their own consistency/freshness contracts, which must be source-qualified separately.
- No claim is made that one state lattice works across providers. The model deliberately fails closed on conflicting terminal evidence unless a source-specific resolver exists.
- Durable event-log compaction, tombstones, retention windows, and replay across schema/version migration remain untested.

## Exact Phase-1 continuation

Continue with **bounded evidence retention / compaction without losing late-failure and dedupe proof**.

Next finite grammar:

- append-only evidence IDs for current and historical attempts;
- event retention TTL/window, compaction snapshot, tombstone/dedup horizon, and provider redelivery horizon;
- late failure/reversal arriving before vs after compaction;
- duplicate event arriving after tombstone expiry;
- schema/version migration of the reducer snapshot;
- crash between snapshot write and event-log truncation;
- concurrent compactor/reducer epoch takeover;
- compare raw append-only log, snapshot+unsafe truncation, snapshot+tombstone horizon, versioned snapshot+retained terminal witnesses, and archive/replay fallback;
- measure false terminalization after compaction, duplicate compensation after dedupe expiry, missed late reversal/failure, stale-attempt resurrection, storage growth, recovery I/O, and safe retention coverage.

Official-source audit target: event retry/redelivery windows and provider event-retention/retrieval guarantees. Keep the rule that retention safety is source-specific; do not convert one provider's retry horizon into a generic TTL.
