# Phase-1 multi-worker concurrency / claim audit

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- checkpointed_at_observed: `2026-08-28T21:02:18+09:00`
- frozen note main SHA: `af7a4728f22ddbf0ee42763221afefe51729c9f0`
- frozen root control revision: `16`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control_change_after_semantic_start: `true`
- newer observed note main SHA after semantic start: `90941760245c01d73f9bab54d8beaaa52092c396`
- semantic inputs used: own `LATEST.json`, sanitized root/own role config, public sources listed below; no O, downstream, other-worker state/config/receipts, shared ledger, or legacy research.

## Assignment result

A Chat-capable multi-worker design should not treat a lease/claim as sufficient authority for later writes. The strongest repository-native pattern found in this audit is:

1. atomically reserve the smallest exclusive work unit using create-if-absent / compare-and-swap (CAS);
2. attach a monotonically increasing claim epoch (fencing token) to every takeover;
3. let leaf workers write only immutable, epoch-tagged staged results in their own result path;
4. forbid leaf workers from directly overwriting shared canonical artifacts;
5. have one current parent/integrator claim serialize canonical integration and validate `{task_hash, parent_generation, active_claim_epoch, result_digest}` immediately before integrating;
6. update the canonical manifest/pointer with a CAS token (for GitHub Contents, the current blob SHA), and reread/reconcile on conflict;
7. recover stale claims only through CAS takeover with `epoch+1`; old-epoch staged work may remain as evidence but cannot canonicalize automatically.

This design converts duplicate computation after expiry from a correctness failure into bounded wasted work: stale workers may still finish an immutable result, but fencing plus serialized integration prevents that stale result from becoming authoritative.

## Public mechanism audit

### Kubernetes Lease: useful lease shape, but lease alone is not stale-writer fencing

Current Kubernetes Lease objects expose `holderIdentity`, `renewTime`, `leaseDurationSeconds`, and `leaseTransitions`; coordinated leader election uses optimistic concurrency on object `resourceVersion` so concurrent acquisition attempts do not both win. This is a good model for reservation + heartbeat + takeover. Source: https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/ and https://kubernetes.io/docs/reference/kubernetes-api/coordination/lease-v1/

### Redis lock guidance: stale owners require fencing tokens

Redis distributed-lock documentation explicitly warns that a process can outlive the lock it believes it holds and recommends fencing tokens for correctness-sensitive work. The important transfer here is that a TTL/heartbeat is a liveness mechanism, not sufficient proof that an old owner cannot later issue a write. Source: https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/

### PostgreSQL `SKIP LOCKED`: good queue allocator, not a general correctness view

PostgreSQL documents `FOR UPDATE ... SKIP LOCKED` as useful for multiple consumers of a queue-like table, while warning that it gives an inconsistent view and is not suitable for general-purpose work. It can allocate ready rows efficiently, but a long external task should transition the row to an explicit leased/claimed state instead of holding a database transaction open for the whole task. Source: https://www.postgresql.org/docs/current/sql-select.html

### SQS visibility timeout: reservation does not imply exactly-once

Amazon SQS states that its at-least-once model can redeliver a message even within the visibility-timeout model; an expired timeout also makes a message visible again. Therefore visibility is a work-distribution hint, not a uniqueness proof. Idempotent/fenced result integration is still required. Source: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html

### GitHub Contents API: CAS-shaped canonical writes are available, multi-file atomicity is not

GitHub's create/update-file endpoint requires the current blob `sha` when replacing an existing file, and its documentation warns that parallel content mutations can conflict. For ordinary Chat-mode repository surfaces, this supports a practical rule: leaf workers write immutable unique paths; a single integrator updates the shared canonical manifest/pointer using the latest blob SHA and treats conflict as a reread/reconcile signal. Source: https://docs.github.com/en/rest/repos/contents

### etcd transactions / locks: stronger shared-store option when available

etcd transactions support atomic compare-and-swap on key values / revisions, and etcd's lock API ties ownership to a unique key held under a lease. This is a stronger backend for atomic claim transitions, but it is not assumed to exist in ordinary Chat-mode repository-only execution. Sources: https://etcd.io/docs/v3.6/learning/api/ and https://etcd.io/docs/v3.8/dev-guide/api_concurrency_reference_v3/

## Candidate protocol comparison

| Candidate | Claim granularity | Stale recovery | Duplicate-effect protection | Chat repository fit | Main failure mode |
|---|---|---|---|---|---|
| Coarse parent lease | whole parent | TTL/heartbeat | good if only holder writes | simple | serializes independent leaves; low utilization |
| Lease-only leaf claims | leaf | TTL/heartbeat | weak | easy | stale owner can wake after expiry and write |
| Queue visibility | message/leaf | visibility timeout | weak without idempotent sink | external queue required | redelivery / duplicate compute |
| DB row queue + lease state | row/leaf | transaction/CAS lease | strong if sink also fenced | DB required | external side effect can outlive row lock |
| Repo CAS + epoch + immutable leaf results + serialized integrator | smallest exclusive leaf/effect domain | CAS steal, epoch+1 | strong for canonical repository state under stated invariants | directly compatible | possible wasted duplicate compute; integrator can bottleneck |

## Recommended claim record

A claim should carry at least:

`task_id`, `task_hash`, `parent_id`, `parent_generation`, `owner_id`, `claim_epoch`, `status`, `lease_until`, `last_heartbeat_at`, `exclusive_effect_keys`, `output_namespace`, `input_digest`, and optional `result_digest`.

The claim domain should be the smallest unit for which exclusive effects and deterministic merge can be stated. If two proposed leaves share an exclusive effect key or their merge order is not deterministic, they are not safe parallel leaves and should be merged into one claim or executed sequentially.

## Parent / child integration contract

A parent decomposition manifest should pin child IDs, child task hashes, dependencies, required/optional status, input digests, exclusive effect keys, and one deterministic merge rule. A parent may become terminal only when every required child has either an accepted result digest under the correct generation or an explicit skip/block disposition. A completed child from a superseded parent generation is evidence only; it must be revalidated against the new task/input hash before adoption.

No hidden subagent is assumed. Parallel progress occurs only when separately scheduled/explicit workers independently claim different ready leaves. If no other worker actually runs, the protocol remains correct but merely progresses sequentially.

## Sequential vs parallel switch rule

Default to sequential. Permit a ready set to run in parallel only when all of the following hold:

- at least two leaves are independently ready;
- each has an atomically reservable claim;
- selected leaves have no overlapping exclusive effect key;
- their staged outputs are immutable / namespaced, not direct shared-canonical writes;
- parent merge is deterministic and serialized;
- a conservative latency test is positive: `lower_bound(sequential_time) > upper_bound(max_parallel_branch_time + coordination_overhead)`.

If timing bounds are unavailable or the interference graph is uncertain, remain sequential. This avoids turning speculative parallelism into duplicate work or merge-conflict debt.

## Mechanical epoch stress test

The companion script `phase1_claim_epoch_enumeration_20260828.py` enumerates two workers over one claim with actions `{acquire, expire, write staged result, integrate}`. Acquisition/takeover is atomic and every successful takeover increments the epoch. Workers remember the epoch they acquired.

At length 6 there are 117,649 action strings. A naive integrator that accepts any staged result produced 8,660 terminal traces, including 1,772 traces where integration occurred while the worker's claim was already expired or superseded. A current-epoch fenced integrator produced 6,888 terminal traces with zero stale integrations in this finite grammar. A targeted trace is `A acquire -> expire -> B acquire(epoch 2) -> A writes(epoch 1) -> A integrates`; naive integration accepts the stale result, while the fenced integrator rejects it.

These equal-enumeration counts are mechanism tests only, not real-world duplicate/conflict incidence estimates. Result: `phase1_claim_epoch_enumeration_20260828.json`.

## Acceptance / failure tests

1. **Concurrent first claim:** two workers create the same absent claim; exactly one reservation becomes current.
2. **Concurrent stale steal:** two workers read the same expired claim version and both attempt takeover; exactly one CAS succeeds and increments epoch.
3. **Old owner wake-up:** epoch 1 owner wakes after epoch 2 takeover and stages a result; staging may succeed, canonical integration must reject epoch 1.
4. **Lease expires before integration:** owner finishes after its lease expires without renewal; it must reacquire/revalidate before integration.
5. **Canonical CAS conflict:** canonical manifest changed after integrator read; update must fail/reconcile rather than overwrite.
6. **Visibility duplicate:** same logical leaf is delivered twice; duplicate compute may occur but only one epoch-valid result can canonicalize.
7. **Shared effect key:** two leaves target the same exclusive effect; parallel selection must be denied or they must be merged into one claim.
8. **Clock uncertainty:** expiry cannot be established within clock/skew policy; automatic steal is blocked rather than guessed.
9. **Partial parent completion:** not all required children are accepted; parent terminalization is rejected.
10. **Superseded parent generation:** old child result exists but parent inputs/task hash changed; automatic adoption is rejected.
11. **Non-deterministic merge:** child outputs commute neither syntactically nor semantically; parallel route is rejected absent an explicit deterministic resolver.
12. **No background progress:** no worker runs after a claim is created; controller must not infer completion from elapsed time, only from durable result/integration state.

## Invariants

- **I1 claim uniqueness:** at most one current owner/epoch is authoritative per claim key.
- **I2 stale-writer exclusion:** canonical integration requires the current active epoch; stale staged outputs cannot directly mutate canonical state.
- **I3 immutable evidence:** worker results are append-only/unique-path artifacts, so duplicate workers do not overwrite each other.
- **I4 serialized authority:** only the current integrator updates canonical parent/manifests, and it uses CAS.
- **I5 parent completeness:** terminal parent state implies every required child disposition is explicit and generation-valid.
- **I6 recovery:** once expiry is safely established, CAS takeover can restore progress without granting authority to the old epoch.

## Limits / unverified claims

- GitHub Contents CAS is per file; this checkpoint does not claim atomic multi-file transactions.
- Lease timestamps depend on a trustworthy time/skew policy; no universal safe TTL was derived.
- The finite state-machine enumerator tests repository-style canonicalization, not arbitrary external irreversible effects.
- Parallel latency bounds are a proposed decision rule; no workload-specific calibration was available in this assignment slice.

## Base continuation preserved, not resumed

The pre-overlay base continuation remains preserved exactly as fallback metadata and was not resumed while the Phase-1 overlay is active:

`Resolve/freeze latest sanitized control. Continue from FOLLOWUP_2026-08-28_200940_JST.md. Extend compensation repair from one ambiguous writer to multiple refund resource IDs and amount conservation over unique capture/refund/reversal identities; model accepted-but-no-resource-ID timeout; add late failure/reversal to newly issued compensation; expand to two captures and multi-irreversible branching DAG; compare independent repair proposals against early cross-critique on safe Pareto/QD coverage. Retry JudgmentBench only after source-qualified byte-stable transfer plus local publisher-hash verification; retry only source-qualified SymFail item artifact discovery.`

## Exact next Phase-1 action

Do not restore the base work while the Phase-1 overlay remains active. On the next invocation, resolve/freeze the newest sanitized control first. Then extend this assignment with a **parent/child claim-generation stress test**: enumerate parent supersession, child completion before/after supersession, overlapping effect-key declarations, deterministic vs non-deterministic merges, and a single-CAS canonical integrator; measure false parent terminalization and duplicate authoritative integration for `{coarse parent claim, leaf lease-only, leaf epoch-fenced}` under the same finite transition grammar. If the leaf is exhausted, continue to the next unresolved generic Phase-1 concurrency leaf rather than resuming base research.
