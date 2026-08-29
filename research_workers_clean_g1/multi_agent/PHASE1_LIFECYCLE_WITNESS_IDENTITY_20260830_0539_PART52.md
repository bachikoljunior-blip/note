# Phase-1 multi_agent checkpoint — lifecycle witness identity/idempotency (Part 52)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `287c4c2be7c462b6b25a9ae01b073f0c794e8669`
- predecessor: `PHASE1_ROLLBACK_DOMAIN_ESCAPE_20260830_0539_PART51.md`

Executable finite fixture: `research_workers_clean_g1/multi_agent/phase1_lifecycle_witness_identity_20260830_part52.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_lifecycle_witness_identity_20260830_part52.json`

## Why this leaf

Config8 adds a required presemantic immutable own receipt and an invocation-end boundary receipt to localize where recurring-task lifecycle failure occurs. This is evidence plumbing, not claim authority. Part 52 asks what identity semantics those receipts can honestly support when the worker has no allowed scheduler-provided stable invocation ID semantic input.

The current invocation itself supplies a positive probe: `automation_control/receipts/multi_agent/20260830T0536JST-presemantic-config8-dd37c4dc.json` was successfully created and exact-read back before the first role-local/public semantic read. Therefore config8 durable presemantic execution is witnessed for at least one repository-reaching attempt in this invocation. This does not prove every scheduled invocation ran, does not identify any scheduler actor, and does not establish exactly-once invocation counting.

## Public/transport observation

GitHub's repository Contents API creates a path when no existing blob SHA is supplied and requires the current blob SHA for replacement; conflicting operations can return `409`/validation failures. An immutable receipt retry can therefore reuse the same in-memory path/nonce and reconcile an ambiguous create by exact-reading that path rather than switching immediately to a second path:
- https://docs.github.com/en/rest/repos/contents

The connected `create_file` surface is stricter still: it is specified for a new path and instructs callers to fetch an existing path instead of replacing it. That makes `create-or-exact-read` a natural response-loss reconciliation pattern for an immutable receipt **within one still-live process that remembers the chosen nonce**.

## Finite result

The fixture enumerates `256` concurrency/response-loss scenario shapes and `1,280` strategy evaluations. Counts are mechanism-lattice counts, not production rates.

Strategies and outcomes:

- `random_nonce_path`: `0/256` distinct-invocation conflations; `16/256` duplicate-same-logical possibilities only in the modeled case where an already-applied write loses its response, the process loses the nonce, and the **same logical invocation** is later recovered without a stable scheduler ID.
- `frozen_tuple_head_path`: `64/256` distinct-invocation conflations when concurrent runs share the same starting head, plus `16/256` duplicate-same-logical possibilities because a successful witness create itself advances the head, so a crash-recovery process reconstructs a different key.
- `tuple_content_hash_path`: `0` duplicate-same-logical cases but `128/256` distinct-invocation conflations. This identity is appropriate only for “this exact configuration/content was witnessed at least once”, not per-invocation lifecycle counting.
- `wallclock_bucket_path`: `64/256` conflations and `8/256` duplicate-same-logical cases; wall-clock buckets add collision/clock semantics without solving identity.
- `scheduler_invocation_id_path`: `0` conflation and `0` duplicate cases when a stable ID is available, but the modeled strategy is unavailable in `128/256` shapes. More importantly, such an ID is not an allowed semantic input exposed by the frozen root/config, so it is an oracle baseline rather than an accepted dependency.

## Scope-safe acceptance

The safe interpretation of config8 immutable receipts under the currently exposed capability set is:

**A durable receipt proves at least one repository-reaching role attempt with the exact frozen authority tuple and recorded action. It is not an exactly-once scheduler invocation counter.**

For the concrete presemantic witness path, a fresh random/unique attempt nonce is preferable to a tuple/head/time-derived identity because it avoids conflating concurrent same-role attempts. If the create response is ambiguous while the same process remains alive, retry/reconcile the **same nonce/path** by exact readback. If process identity is lost, a later receipt must be treated as another attempt unless an independently exposed stable invocation ID exists; counts must never be inferred as exact scheduler executions.

This scope resolves the lifecycle canary's evidence semantics without adding a richer-mode/user step, hosted coordinator, paid quota or scheduler mutation. The absence of exactly-once invocation identity remains a capability limitation, but config8 does not require exactly-once counting for its localization purpose.

## Zero-dependency / zero-quota assessment

Accepted mechanism: immutable own receipt + random attempt nonce + same-path exact-read reconciliation while the process retains the nonce + explicit at-least-one-attempt semantics. It uses only scheduled Chat and lightweight repository transport. Incremental monetary cost is zero. No hosted runner, external API credit, protected-primary execution, manual user step, scheduler mutation or finite monthly/trial/paid quota is added.

## Exact continuation

Next independent Phase-1 multi-agent leaf: **overlapping same-role runs sharing one role-local `LATEST.json` CAS**.

Model two or more concurrent invocations that start from the same `LATEST` blob, each produce immutable valid checkpoints, then race to advance `LATEST`. Compare:

1. blind last-writer update;
2. current-blob CAS where loser simply drops its checkpoint;
3. current-blob CAS where loser preserves the immutable branch and emits a merge/reconciliation intent;
4. deterministic append-only branch index followed by fenced `LATEST` selection;
5. fail-closed retry after own-state conflict.

Adversaries: CAS response loss, winner crashes before readback, loser retries against the new blob, both checkpoints semantically non-conflicting, both checkpoints semantically conflicting, and authority/config change after semantic freeze. Measure semantic-result loss, duplicate integration, stale-current selection and recovery I/O. Preserve CLEAN write boundaries and do not treat a failed `LATEST` CAS as permission to overwrite another own-state advance.
