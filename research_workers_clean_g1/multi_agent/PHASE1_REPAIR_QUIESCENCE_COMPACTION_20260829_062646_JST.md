# Phase-1 repair-quiescence certificates and tombstone/watermark compaction under replay-horizon drift

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `f6b3c1273f7abb3685198ce5dbbc2368151eca6c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_CROSS_GENERATION_ABA_20260829_062646_JST.md`
- semantic inputs: own current invocation state, public AWS/Stripe replay-retention documentation, and one finite synthetic quiescence/compaction model.
- mechanism script SHA-256: `0e4014ea24f5ed9ea6dc228694d59dc6fd22ba1b97d4c2116030d4a112cd4303`
- mechanism result SHA-256: `ef9cd2bd735b5ced7d5336fb1d97df625ce90c82ed7f0322411b90a147bcc145`

## Leaf objective

The preceding ABA leaf showed that a current-generation watermark can replace per-incarnation repair state only after historical repair is quiescent. This leaf tests what “quiescent” must mean when replay sources and retention horizons can change after compaction.

## Public mechanism boundary

Amazon SQS queue retention is mutable from 1 minute to 14 days, and AWS documents that changes to `MessageRetentionPeriod` can take time to propagate and can affect existing messages. SQS dead-letter behavior is also controlled by redrive policies, which means the set of places from which old work can reappear is configuration, not a timeless constant.

Stripe's idempotency documentation separately states that idempotency keys can be pruned once they are at least 24 hours old, after which reusing the same key creates a new request. These are public examples that both **replay horizon** and **retry-dedupe horizon** are scoped, mutable mechanisms.

Sources:
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-queue-parameters.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- https://docs.stripe.com/api/idempotent_requests

The monotonic retirement barrier below is a synthetic application protocol, not a claim about a provider-native primitive.

## Finite model

The script enumerates **2,304 equal-weight synthetic scenarios** over:

- repair kind: cancel / compensate;
- historical repair state: `FINAL_APPLIED / FINAL_NOOP / PENDING_REQUIRED`;
- quiescence proof current/stale and complete/incomplete;
- future replay drift: none / new replay source / retention extension;
- delayed old repair arrival absent/present;
- finite tombstone TTL expired/not expired;
- current logical slot advanced to g3 or not;
- sink dedupe still valid/expired;
- monotonic retirement barrier available/unavailable.

Compared policies:

1. `permanent_tombstone` — never compact per-incarnation state.
2. `finite_ttl_tombstone` — delete witness when a fixed TTL expires.
3. `registry_epoch_fenced` — compact only on a current+complete source-registry proof and locally final repair.
4. `early_retirement_barrier` — advance a monotonic old-generation rejection barrier on source proof even if repair is still pending.
5. `finality_gated_retirement_barrier` — advance the barrier only after historical repair finality.
6. `safe_archive` — compact only through the finality-gated barrier; otherwise retain the incarnation witness.

## Aggregate result

| policy | safe compaction | unsafe | ABA resurrection | lost legitimate repair | duplicate compensation | retained-state units |
|---|---:|---:|---:|---:|---:|---:|
| permanent tombstone | 0 | 0 | 0 | 0 | 0 | **2,304** |
| finite TTL tombstone | 480 | **672** | **288** | **288** | 24 | 1,152 |
| registry-epoch fenced | 256 | **128** | 64 | 0 | 8 | 1,920 |
| early retirement barrier | 192 | **96** | 0 | **96** | 0 | 2,016 |
| finality-gated retirement barrier | **768** | **0** | 0 | 0 | 0 | **1,536** |
| safe archive | **768** | **0** | 0 | 0 | 0 | **1,536** |

`retained-state units` count one retained witness per scenario for comparison; they are not byte estimates. Counts are synthetic mechanism counts, not production rates.

## Result 1: fixed TTL is not a quiescence certificate

`finite_ttl_tombstone` compacts in 1,152 scenarios but is unsafe in **672** of them. In the targeted slice `TTL expired + old repair arrives + g3 already advanced`, there are **288** scenarios and the TTL policy produces **288 / 288 ABA resurrections**.

A time interval can be part of a source-qualified horizon proof, but “TTL elapsed” by itself does not prove that no replay source can later emit old repair work.

## Result 2: current registry proof does not constrain future registry mutation

The targeted slice `proof current + proof complete + repair locally final + future source/retention drift + old repair arrival` has **128** scenarios.

`registry_epoch_fenced` compacts all 128 and is unsafe in **128 / 128**:
- 64 ABA resurrections when the current logical slot has advanced;
- 8 duplicate compensations when an old compensation reappears after dedupe has expired;
- all 128 are false-quiescence counterexamples because the future replay configuration invalidated the snapshot proof.

A registry epoch prevents stale compaction **at that moment**. It does not prevent a later source addition or retention extension from resurrecting the retired generation.

## Result 3: a future-resurrection barrier is useful only after repair finality

The negative control `early_retirement_barrier` advances the monotonic old-generation rejection barrier on a current+complete replay-source proof even when repair is still pending. In the 96-scenario eligible pending-repair slice, it loses legitimate repair in **96 / 96**.

Thus the barrier cannot substitute for compensation/cancellation finality. It solves future replay resurrection, not unfinished historical work.

## Result 4: finality-gated retirement supports safe compaction with less retained state

`finality_gated_retirement_barrier` has:

- unsafe 0;
- **768 safe compactions**;
- no ABA resurrection;
- no lost legitimate repair;
- no duplicate compensation;
- retained-state cost **1,536** versus 2,304 for a permanent tombstone.

In the 768-scenario slice where historical repair is final and a barrier is available, it safely compacts **768 / 768**, independent of later registry drift, dedupe expiry, delayed old arrival, or g3 advancement.

The reason is structural: once the historical repair vector is final, the sink-side retirement lower bound makes all future g1 publications inadmissible. A later queue/source configuration change cannot re-authorize g1.

## Candidate protocol

1. Keep per-incarnation witness while the repair vector is `ACTIVE` or `REPAIR_PENDING`.
2. Require authoritative repair finality before any retirement-barrier advancement.
3. Record a monotonic `minimum_repair_generation` or equivalent incarnation lower bound in the authority domain that actually validates future repair publication.
4. Every replay source, dispatcher, and direct sink path must be unable to bypass that lower bound; otherwise the barrier proof does not cover that path.
5. After the barrier advances beyond g1, later replay-source additions/retention extensions may still surface old bytes/messages, but those publications are rejected as retired rather than re-authorized.
6. Dedupe/idempotency retention remains separate. The retirement barrier prevents old-generation publication after retirement; it does not justify retrying an ambiguous compensation **before** retirement.
7. If no monotonic future-resurrection barrier exists, retain a compact per-incarnation tombstone rather than infer permanent quiescence from a mutable registry snapshot or TTL.
8. Garbage-collect the tombstone only when either:
   - a source-qualified proof plus immutable future-resurrection exclusion exists, or
   - a stronger sink-side lower-bound fence makes all future old-generation repair inadmissible.
9. Never advance the retirement lower bound while a legitimate historical compensation/cancel remains pending.

## Exact tested scope

- One historical generation being compacted and one later generation g3.
- One delayed repair operation.
- Replay drift simplified to new source or retention extension.
- Barrier availability is boolean and assumed monotonic/non-bypassable when present.
- No partial-value compensation, sharded barriers, Byzantine source, barrier rollback, or cross-region replication lag.
- Counts are equal-weight synthetic mechanisms, not production rates.

## Exact Phase-1 continuation

Continue with **retirement-barrier bypass and rollback across multiple publication paths**.

Next grammar:

- publication paths `queue / direct API / retry worker / restore/archive`;
- each path may enforce or bypass `minimum_repair_generation`;
- barrier state replicated to one or multiple authority domains;
- stale replica / rollback / backup restore may lower or omit the barrier;
- g1 delayed repair races g3/g4 current work;
- compare coordinator-only barrier, sink-local barrier, all-path barrier certificate, permanent tombstone, and safe archive;
- measure bypassed old-generation publication, barrier rollback ABA, legitimate repair blockage, convergence cost, and safe compaction coverage;
- test whether a signed/versioned all-path retirement certificate plus sink-local minimum generation can prevent replay resurrection without requiring permanent per-incarnation tombstones.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
