# Phase-1 multi-agent Part 64 — post-ABORT child reclamation

Frozen authority: DESIRED_STATE blob `481660fb6008a57cea162da38439cf115c8d7ebe` control revision 26; role config blob `f6bade5e0f774a0623e615b1fc5f924475732d5c` config revision 8; RUN_LIFECYCLE blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; transport `sha_only_main_ref_exact_sha`; frozen main `3bde851bbebd71fce454f869bc341e2c3e627286`. Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`. Bootstrap valid: true.

Predecessor: `PHASE1_TOPOLOGY_ABORT_CLEANUP_20260830_0830_PART63.md`. Only the exact predecessor continuation was used. No O, other-worker, downstream, shared-ledger, legacy, commit-message, or unrelated repository semantics were used.

## Bounded slice

Starting state: root generation G2 is durably `ABORTED` and carries an exact cleanup set of three child `(logical_name, generation, incarnation)` identities. This slice asks how those child artifacts can be reclaimed without allowing a later topology generation that reuses the same logical child name to be deleted by an old cleanup request.

A finite equal-weight Boolean lattice enumerates eight adversaries, giving 256 scenarios per strategy and 1,280 strategy-scenario evaluations:

1. a child logical name is reused by a new incarnation before cleanup completes;
2. cleanup is interrupted after a proper prefix of the three children;
3. one exact delete is applied but its response is lost;
4. repository rate limit interrupts subsequent cleanup;
5. the cleanup coordinator is stale;
6. root cleanup-witness compaction is attempted;
7. an old cleanup request is replayed;
8. a later topology generation reuses the same child name.

Compared strategies:

- **eager exact delete** — target exact child generation/incarnation IDs, but retain no monotonic per-child progress certificate and compact the root witness when GC is requested;
- **root manifest + monotonic cursor** — retain the exact cleanup set in the ABORTED root, advance a monotonic per-child cleanup cursor, fence stale coordinators, read-before-retry after ambiguous response, and reject root-witness compaction while any child outcome is unresolved;
- **per-child tombstones** — exact-incarnation tombstones record settled children; root compaction is permitted only after every expected child has a durable tombstone/terminal record;
- **name-only GC** — delete by current logical child name and allow GC without exact incarnation fencing;
- **fail closed** — reclaim only in the all-clear trace and otherwise retain state.

Safety oracle: destructive cleanup must identify the exact retired child incarnation; stale coordinator cleanup is not authoritative; ambiguous delete is read-before-retry; partial/rate-limited cleanup must preserve enough durable information to enumerate the remaining exact cleanup set; a root cleanup witness may be compacted only if exact-generation fencing and complete-set recoverability survive compaction. Counts are mechanism-lattice counts, not production failure rates.

## Results

| strategy | unsafe scenarios / 256 | stale-delete operations | ABA/replay events | stranded child-units | false blockage units | recovery reads | root compactions | unsafe root compactions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| eager exact delete | 120 | 0 | 0 | 592 | 128 | 240 | 128 | 120 |
| root manifest + monotonic cursor | 0 | 0 | 0 | 576 | 248 | 160 | 8 | 0 |
| per-child tombstones | 0 | 0 | 0 | 576 | 248 | 192 | 8 | 0 |
| name-only GC | 210 | 336 | 128 | 576 | 128 | 0 | 128 | 126 |
| fail closed | 0 | 0 | 0 | 765 | 255 | 0 | 0 | 0 |

The highest-value negative result is that **exact-incarnation delete alone is not enough to justify deleting the root cleanup witness**. In this model eager exact delete never targets a later incarnation, but 120/128 attempted root compactions occur while partial, ambiguous, rate-limited, or stale-coordinator state still exists. Those 120 cases lose complete-set recoverability and are therefore unsafe even though the individual delete key itself was exact.

The name-only control is worse in a different way: 210/256 scenarios are unsafe, with 336 stale-delete operations and 128 ABA/replay events. Logical-name reuse is therefore a separate fencing obligation from progress durability.

Within this finite model, both strong strategies have zero modeled safety failures. The **root manifest + monotonic cursor** has lower modeled recovery-read cost than per-child tombstones (160 vs 192) because the root remains the canonical enumeration/progress witness. Tombstones trade more per-child retained state and reads for a more distributed proof of settled children. Neither strategy may compact the root merely because delete requests were issued; compaction is admitted only in the 8/128 GC-attempt traces where no partial, ambiguous, rate-limit, or stale-coordinator uncertainty remains.

## Reproducibility rule set

For each of the 256 Boolean assignments, evaluate the five strategies with these deterministic rules:

- `reuse := reuse_name OR later_generation_reuses_name`.
- Exact-incarnation strategies never delete a later incarnation when replayed; replay requires a confirmatory read if the old target may already be absent.
- A stale coordinator performs no authoritative cleanup under the strong strategies.
- `partial` or `rate_limit` leaves only the first of three children settled in this bounded model.
- `ambiguous` means the second exact delete may have applied but is not acknowledged; the strong strategies perform one read-before-retry.
- `manifest+cursor` and `child_tombstone` reject root compaction unless every expected child outcome is terminal and unambiguous.
- `eager_exact_delete` compacts on every GC request; if any cleanup outcome remains unresolved, that compaction is unsafe because the complete exact cleanup set is lost.
- `name_only_gc` targets a reused current name when reuse exists; replay can therefore act on a later incarnation.
- `fail_closed` leaves all three children when any adversary bit is set.

These rules fully determine the table above and keep observations distinct from production-rate inference.

## Public mechanism provenance inherited from the predecessor

No additional public read batch was consumed in this bounded invocation. The predecessor already records two source-qualified precedents used only as mechanism analogues: Kubernetes delete/update preconditions can include `uid` and `resourceVersion`, supporting exact-incarnation destructive preconditions; etcd transactions support an atomic conjunction of comparisons guarding a request block. Neither mechanism is accepted as an external Phase-1 dependency. The current slice adds only a role-local finite-model result about preserving the complete cleanup set through partial/ambiguous reclamation.

## Phase-1 assessment

Observation: in this exact three-child Boolean model, the safe reclaim rule is `ABORTED root with exact cleanup set -> fenced exact-incarnation child settlement -> monotonic progress evidence -> root cleanup-witness compaction only after all expected child outcomes are terminal and unambiguous`.

Inference: an exact delete key solves stale-target identity but does **not** by itself solve restart/recovery completeness after the root cleanup manifest is discarded. Conversely, a durable progress manifest without incarnation-sensitive destructive preconditions does not solve name-reuse ABA. Both identity fencing and complete-set recovery evidence are required.

Scope caveat: three children, fixed Boolean adversary ordering abstractions, repository-local authority only. This does not prove unbounded cleanup sets, complete repository rollback safety, or external sink atomicity.

Residual richer-mode/protected/manual-user execution dependency added: none. Finite monthly/trial/paid quota dependency added: none. Incremental monetary cost: 0. External hosted coordination: none required or accepted. Repository transport remains lightweight role-local state/evidence only; rate-limit interruption is fail-closed and resumed on a later invocation, never waited/retried here.

`global_completion=false`; `phase1_completion_claimed=false`; `enabled_desired=true`; scheduler mutation by worker: false.

## Exact continuation

Next invocation, model **second-order GC of the cleanup witness itself** after all exact children are terminal. Compare: (1) permanent root cleanup manifest; (2) compact root witness `{retired_generation, cleanup_set_digest, terminal_cleanup_id, incarnation_floor}`; (3) per-child tombstones with later tombstone GC; (4) digest-only witness without an anti-rollback floor; and (5) fail closed. Enumerate later generation/name reuse, tombstone deletion, ambiguous compaction CAS, stale coordinator replay, repository restore/rollback inside the same authority domain, rate-limit interruption, and cleanup-set hash collision as a symbolic mismatch event. Measure old-cleanup resurrection, stale deletion, false blockage, retained-state units, recovery reads, and whether a compact witness remains sufficient after every detailed child record is gone. Do not start that second leaf in this invocation.
