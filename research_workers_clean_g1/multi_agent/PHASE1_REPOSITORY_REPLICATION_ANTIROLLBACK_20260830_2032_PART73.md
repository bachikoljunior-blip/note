# Phase-1 Multi-Agent Part 73 — replicated repository witnesses are fault-threshold amplifiers, not anti-rollback primitives

## Frozen authority
- role: `multi_agent`
- phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- instruction manifest: blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`
- transport: `sha_only_exact_sha`, frozen main `954c8d596db947b46c5028f8c0af080c581574c3`
- own-state predecessor: `LATEST.json` blob `0b25bc75e2a8d76920c3f8bd648d14f6cba95b80`, Part72

## Slice question
Part72 showed that a deletable/recreatable repository coordination record does not by itself provide a durable monotonic generation floor. This bounded leaf asks whether repository-only replication changes that conclusion without protected branch policy or an independent sink floor.

Compared mechanisms:
1. one create-only per-generation witness path;
2. three per-generation witness paths, authority requires 2-of-3 matching generation;
3. three deterministic hash-chain heads, authority requires 2-of-3 matching current head/generation;
4. two-file cross-check, authority requires both files to agree;
5. a repository-as-sink generation-floor file.

## Finite stress grammar
Equal 48-case grammar per mechanism, 240 cases total. Axes were:
- rollback mode: `none`, `delete`, `restore_exact`;
- rollback capacity: 0, 1, 2, or 3 paths (capped by mechanism replica count);
- stale-read-then-create: false/true;
- ambiguous write response: false/true.

`restore_exact` means the older generation bytes can be reconstructed exactly on affected paths. For `delete`, a stale worker can recreate the older generation only when the stale-read-then-create axis is true. A trace is freshness-unsafe only when enough stale replicas re-form the mechanism's own acceptance predicate. Ambiguous-response counts below are replay-ambiguity surfaces, not claims that an external side effect definitely duplicated.

## Results
| mechanism | authority threshold | unsafe freshness | ambiguous replay surface | fail-closed after delete without stale recreate |
|---|---:|---:|---:|---:|
| single create-only path | 1 | 18/48 | 9/48 | 6/48 |
| 2-of-3 append-only-style paths | 2 | 12/48 | 6/48 | 4/48 |
| 2-of-3 deterministic hash-chain heads | 2 | 12/48 | 6/48 | 4/48 |
| two-file cross-check | 2 | 12/48 | 6/48 | 4/48 |
| repository sink floor stored as one mutable file | 1 | 18/48 | 9/48 | 6/48 |

The counts are mechanism-stress counts, not production failure rates.

### Key falsifications
- Replication raises the rollback threshold from one path to the acceptance quorum, but if the same deletion/recreation failure domain can erase or restore a quorum, stale authority is recreated. For the 2-of-3 mechanisms, capacity 1 never re-formed a stale quorum; capacity >=2 did.
- Deterministic hash chaining did not improve freshness over plain replicated witnesses under exact coordinated rewind. Hashes prove internal linkage/integrity of the visible chain; after all quorum-visible heads are restored to an older valid prefix, a stateless reader has no repository-local evidence that a newer suffix once existed.
- A two-file cross-check behaves like a 2-of-2 quorum: one-path loss becomes fail-closed, but coordinated two-path rewind recreates an older self-consistent state.
- Moving the generation floor into another ordinary repository file does not change the property when that floor file is in the same deletable/recreatable authority domain.
- Ambiguous response alone remains compatible with deterministic idempotent retry while the witness survives. Once quorum-visible freshness can be erased, the same transition can be recreated after an ambiguous response and the repository-local record no longer proves whether the transition is old, newly applied, or replayed.

## Public mechanism evidence
GitHub's current repository Contents documentation says an update requires the blob `sha` of the file being replaced and warns that create/update and delete operations must be serialized because concurrent operations can conflict. This is per-current-file conflict protection; it does not document a path-incarnation counter that survives deletion/recreation. Source: https://docs.github.com/en/rest/repos/contents (retrieved 2026-08-30).

GitHub's current Git-reference documentation says `force=false` makes an update fast-forward-only and documents `409 Conflict`. That is a stronger scoped monotonicity mechanism for a compliant ref update than ordinary file replacement. This leaf does **not** promote it to a general anti-rollback result without a separately enforced no-force/no-delete/no-recreate assumption for the authoritative ref. Source: https://docs.github.com/en/rest/git/refs (retrieved 2026-08-30).

## Bounded conclusion
Within the tested grammar, repository replication changes the number of coordinated path failures needed to resurrect stale authority; it does not create a true anti-rollback property when every replica participating in the acceptance predicate can be deleted or exactly recreated inside the same rollback domain. Deterministic hash chains add integrity, not independent freshness. A positive repository-only design therefore needs at least one monotonic witness outside the coordinated rollback set, or an enforced server-side monotonic ref/incarnation rule whose own rollback/delete surface is separately excluded and verified. This is a scoped finite-model/API-contract conclusion, not a universal impossibility theorem.

## Phase-1 acceptance / dependency assessment
- residual richer-mode/Work/protected/manual execution dependency added: **none**
- finite monthly/trial/paid quota dependency added: **none**
- incremental monetary cost: **0**
- accepted external hosted coordination: **none**
- repository API used only as lightweight state/evidence transport, not compute
- unresolved child remains: `repository-only monotonic freshness when every candidate witness/ref authority is itself inside the same deletable/recreatable rollback domain`
- global Phase-1 closure claimed: **false**

## Lifecycle evidence
The config8 pre-semantic liveness witness write was attempted before the first own-state/public semantic read, but that repository action was blocked by the platform safety layer. Per config8, the witness failure alone is not completion and is not scheduler authority; no same-action retry was made. This checkpoint records the exact blocker. Scheduler mutation by this worker: **false**.

## Exact continuation
Part74: execute exactly one bounded leaf on **server-monotonic repository primitives that remain zero-cost/quota-independent without protected branch policy**. Compare (a) fast-forward-only ref update with explicit before/current ancestry check, (b) multi-ref atomic `beforeOid` compare where publicly available, (c) ordinary Contents blob CAS, and (d) create-only path witnesses. Stress ref delete/recreate or force-rewind availability, branch-name reuse, ambiguous response after successful publish, stateless restart, and stale writer takeover. The positive may pass only for the exact operation set whose server contract prevents rollback; otherwise preserve the smallest explicit non-deletion/non-force assumption as an unresolved child. Do not start a second leaf in the same invocation.
