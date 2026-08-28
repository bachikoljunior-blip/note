# Phase-1 cross-shard finality / fencing race stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- frozen note main SHA: `63e0f497bc9157c6c5075a8c615327dc49b8e76a`
- frozen root control revision: `21`
- frozen root manifest blob: `87e2d9e19b16d39b495a4a5512d871069d7521ee`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- semantic freeze proof: SHA-only `refs/heads/main` lookup was `63e0f497…` both before exact-SHA control fetch and immediately before the first role-local semantic read. A later SHA-only recheck before persistence remained `63e0f497…`.
- semantic inputs: sanitized root manifest revision 21, own role config revision 6, own `LATEST.json`, own preceding wide-sharded-reservation checkpoint and script, official/public etcd/DynamoDB/CockroachDB documentation, and the new finite synthetic model. No O/O-derived state, downstream state, other-worker state/config/receipts, shared aggregate ledger, or legacy/pre-independence research was used.

## Leaf objective

Stress the exact race left unresolved by the previous wide-reservation leaf:

`verify all shard receipts current -> one shard expires/takes over (or parent/coordinator changes) -> root COMMITTED`

The key question is whether a durable root state can safely compress independently changing shard authority, and what proof must be atomic with the root commit.

## Public mechanism facts used

### Atomic compare + commit exists when the full authority set fits one transaction

Current etcd documentation describes `txn` as an atomic If/Then/Else over the key-value store. Multiple compare predicates on different keys are evaluated atomically; if all succeed, the success block is applied atomically. etcd's current API-guarantees page states KV operations are strictly serializable and atomic. These are useful primitives for binding current shard epochs, parent generation and coordinator epoch to one root write, provided the whole compare/write set fits one transaction/request and lives in that authority domain.

- https://etcd.io/docs/v3.7/learning/api/
- https://etcd.io/docs/v3.7/learning/api_guarantees/

DynamoDB provides a concrete bounded example: `TransactWriteItems` atomically executes at most 100 item actions in one account/Region, including condition checks/writes. This preserves the previous leaf's scope boundary: a wide claim set can exceed a documented atomic envelope.

- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Constraints.html

CockroachDB Parallel Commits remains an architectural precedent only: a `STAGING` transaction is not trusted by label alone; recovery checks the listed writes and prevents missing writes from later succeeding before deciding committed/aborted.

- https://www.cockroachlabs.com/blog/parallel-commits/

No claim below treats these provider guarantees as automatically inherited by an application-level protocol.

## Finite model

The executable enumerates **1,728 equal-weight synthetic scenarios** over:

- reservation width: `small80` vs `wide120`,
- effect-set relation: disjoint / one-shard overlap / multi-shard overlap,
- root pre-state: `PENDING` vs `STAGING`,
- race: none / shard-1 takeover / shard-2 expiry / shard-3 takeover / parent supersession / coordinator takeover,
- root-commit outcome: success / ambiguous-applied / ambiguous-not-applied,
- idempotency token: fresh vs expired,
- restart state: full local state vs only durable reservation ID,
- cleanup: none vs partial cleanup followed by an overlapping new claimant.

Counts are mechanism stress counts, not operational probabilities.

Compared protocols:

1. **NEG root-COMMITTED trust** — verify shards sequentially, then write/trust root `COMMITTED` without atomically re-checking shard epochs.
2. **Atomic compare+root commit <=100** — one transaction compares all shard epochs plus parent/coordinator and writes root; modeled available only in the bounded `small80` scope.
3. **Naive hierarchical certificate** — root compares compact immutable group certificates, but shard takeover/expiry does not invalidate them.
4. **Fenced hierarchical certificate** — any shard authority transition atomically invalidates/bumps its group certificate in the same authority domain; root atomically compares current group-cert epochs plus parent/coordinator.
5. **Sink-time revalidation** — root is only intent; every authoritative effect re-checks current shard/parent/coordinator authority, and terminality is granted only after all required sinks pass.
6. **Staged + one fenced integrator** — workers stage immutable results; one current integrator epoch owns canonical effect issuance and durable publication identity.

## Main results

| protocol | terminals | unsafe terminals | duplicate authoritative effects | structural blocks | parallel-effect admissions | serialized-effect admissions |
|---|---:|---:|---:|---:|---:|---:|
| NEG root-COMMITTED trust | 1,728 | **1,440** | **288** | 0 | 576 | 0 |
| atomic compare+root commit <=100 | 144 | 0 | 0 | **864** | 48 | 0 |
| naive hierarchical cert | 1,152 | **864** | **288** | 0 | 384 | 0 |
| fenced hierarchical cert | 288 | 0 | 0 | 0 | 96 | 0 |
| sink-time revalidate | 288 | 0 | 0 | 0 | 96 | 0 |
| staged fenced integrator | **1,440** | 0 | 0 | 0 | 0 | **1,440** |

### The verification-to-commit race is real in the model

The direct shard-race slice contains **864** scenarios. Both protocols that treat a historical shard proof as current authority terminalize all 864 and are unsafe in **864/864**:

- NEG root-COMMITTED trust: 864 terminal / **864 unsafe**, 288 duplicate-effect cases,
- naive hierarchical cert: 864 terminal / **864 unsafe**, 288 duplicate-effect cases.

The mechanism is exact: a shard was valid when verified/certified, then changed authority before root commit, while the root write had no atomic predicate tied to the shard's current epoch.

The narrow `wide120 + shard race + overlapping effect + partial cleanup/new claimant` slice has **144** scenarios. Both historical-proof protocols are **144/144 unsafe** and produce **144/144 duplicate authoritative effects**. The bounded atomic candidate is structurally unavailable in all 144 wide cases.

### Root COMMITTED is not a sufficient certificate by itself

The negative control is unsafe in **1,440/1,728** total scenarios because it terminalizes through all five authority-race classes. Direct parent/coordinator predicates can eliminate those two race classes, which is why the naive hierarchical candidate has fewer failures, but it still fails every shard race. Therefore the root state name (`COMMITTED`) is not the proof; the proof is the atomic relationship between that root transition and the current authority versions it summarizes.

### Hierarchy only works if member authority transitions invalidate the summary

A compact group certificate can reduce the number of values the root must compare, but a certificate over historical shard state is not enough. In the positive synthetic `hierarchical_fenced_cert`, every shard takeover/expiry must atomically bump/invalidate the group certificate in the same authority domain. The root then atomically compares group-cert epochs plus parent/coordinator before committing. Under that explicit assumption, this model has **0 unsafe terminals and 0 duplicate effects**.

This is a protocol synthesis result, not an etcd/Cockroach/DynamoDB guarantee. If shard transition and certificate invalidation can be separated by a crash/network boundary, the positive proof no longer applies and the protocol must fail closed or use a stronger coordinator.

### Sink-time revalidation is safe for authority, but it changes the contract

`Sink-time revalidate` also has **0 unsafe terminals / 0 duplicates** because root commit is not effect authority. Any post-verification race causes the affected sink check to fail, so the parent is not terminalized. This preserves current authority without requiring one atomic root transaction over all shards, but it does **not** prove all-or-nothing external-effect semantics across multiple sinks. Some effects could succeed while another blocks; that partial-effect problem is intentionally the next leaf.

### Serialized integrator remains the broad safety fallback

The staged/fenced integrator terminalizes **1,440/1,728** safely in this grammar and serializes all 1,440 effect admissions. It tolerates shard-claim takeover because shard claims are not themselves effect authority; canonical effect publication remains owned by one current integrator epoch. Parent supersession still fails closed. This is a safety fallback, not a throughput optimum.

## Recovery / ambiguous root response

The model includes success, ambiguous-applied and ambiguous-not-applied root outcomes plus restart with only a durable reservation ID. Strong variants assume the root intent contains the complete expected contract plus a persistent integration identity. On the **576 reservation-only + ambiguous** scenarios, none of the strong candidates create an orphan reservation in the finite model. Safety still depends on re-checking current authority before any retry that may commit; an expired transport idempotency token is not itself a fencing proof.

## Acquisition liveness micro-test

The separate two-worker / three-shard order micro-test reuses all 36 order pairs:

- arbitrary hold-and-wait order: **24/36 deadlock**, 12/36 both finish,
- abort-on-conflict with release/retry: **36/36 finish**, with 1-3 modeled aborts,
- one canonical global order: both finish with **0 aborts** in the same toy schedule.

Thus wide reservation still needs either one deterministic total acquisition order or prompt abort/release on conflict; safety fencing does not remove hold-and-wait liveness hazards.

## Candidate protocol after this leaf

1. Persist a root intent with canonical task/effect identity, exact shard membership, parent generation, coordinator epoch and reservation ID. `PENDING/STAGING` is preparation, never external-effect authority.
2. For each shard, store the exact reservation ID, effect digest and monotonic shard epoch. Partial shard success is only prepared state.
3. If the entire current-authority predicate set fits one strictly serializable atomic transaction, compare every required shard epoch plus parent/coordinator and write root `COMMITTED` in that same transaction.
4. If hierarchy is used to compress the root predicate, a member shard authority transition must atomically invalidate/bump the summary certificate that the root compares. Historical Merkle/digest membership without current invalidation is insufficient.
5. If no such cross-shard atomic fence is available, do not treat root `COMMITTED` as effect authority. Revalidate at each authoritative sink or route publication through one current fenced integrator.
6. Recover ambiguous root writes from persistent `integration_id`/reservation identity before retrying; idempotency token freshness is transport protection, not semantic authority.
7. Keep canonical total-order acquisition or abort/release-on-conflict for liveness.

## Exact scope limits

- `atomic_compare_root_commit<=100` is positive only inside the modeled bounded atomic transaction envelope and one authority domain.
- `hierarchical_fenced_cert` assumes shard transition + certificate invalidation are atomic; this leaf does not prove a cross-database/cross-provider implementation can satisfy that assumption.
- `sink_time_revalidate` proves duplicate-authority safety in this model, not all-or-nothing external-effect completion across sinks.
- external sinks that ignore reservation/fencing metadata remain outside the positive proof.
- staged-integrator safety relies on the previously role-local-tested single current integrator epoch and persistent publication identity.
- no synthetic count is an empirical production rate.

## Exact Phase-1 continuation

Continue with the next unresolved non-conflicting leaf: **reservation-to-external-effect handoff finality**.

Finite grammar should separate reservation authority from effect execution and enumerate:

- root current/committed vs superseded after dispatch authorization,
- `read authority -> external side effect -> record applied` crash windows,
- sink outcome success / ambiguous-applied / ambiguous-not-applied,
- sink idempotency key fresh / expired / unsupported,
- per-effect deterministic integration ID vs transport-only token,
- multiple sinks where one succeeds and another blocks/fails,
- dispatcher/integrator epoch takeover,
- outbox row current vs stale after parent change,
- retry before readback vs read-before-retry,
- partial multi-effect completion and terminality claims,
- direct dispatch from root `COMMITTED`, transactional outbox + fenced dispatcher, sink-time authority revalidation, and serialized fenced integrator controls.

Measure duplicate external effects, false parent terminalization, orphan/ambiguous effects, partial-effect exposure, recovery reads/writes, safe parallel dispatch and serialization cost separately. Preserve exact provider-scope limits: transport idempotency is not assumed durable beyond documented retention, and non-idempotent sinks must fail closed or require an application-level deduplication authority.