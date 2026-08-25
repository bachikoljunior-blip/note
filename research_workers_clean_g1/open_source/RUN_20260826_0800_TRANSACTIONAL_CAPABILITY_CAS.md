# Open Source clean_g1 — RUN_20260826_0800_TRANSACTIONAL_CAPABILITY_CAS

Continuation within the same frozen semantic invocation tuple: note main `ab5d9ae732b8d590a8de659411584db9f7722230`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. Only own clean state plus public sources were used; no O/O-derived, other-worker, downstream, aggregate-ledger, other-role, or legacy/pre-independence semantic input was read.

## Finding A — normal Manager objective adoption is lock-bound; standalone objective CLI remains distinct

Fresh source tracing resolves one ambiguity from the previous run. `manager/_vertical_ops.py` exposes a commit wrapper that chooses `self.pipeline_lock()` unless the caller explicitly states `_lock_held=True`, and then enters `_commit_vertical_decision_locked(...)`. The locked implementation performs route/stage reset work and calls `self._adopt_operator_objective(...)` before returning the committed division.

Therefore the normal Manager path that transcribes an operator objective into a vertical-specific durable field is protected by the same pipeline lock as the route commit. This should be separated from the standalone operator CLI in `verticals/math/objective_mode.py`, which calls `set_objective()` directly and whose own source explicitly acknowledges that its full-object read/modify/write can lose an edit when interleaved with `persist_vertical()`.

This narrows current operational evidence:

- normal Manager objective adoption: lock-bound under the checked path;
- standalone math objective CLI: explicit external writer, lifecycle separation assumed rather than enforced;
- `argus learn`: explicit external route writer, likewise outside the Manager lock when invoked directly.

## Finding B — exact public precedent found: one-shot scoped capability + exact-state rejection + consumption in the same DB transaction

Fresh public `azizu06/snaplist@bf1e631ec8b01b53938f81b3e66764d6b151f792` (verified current `main`) contains an implementation pattern substantially closer to `clean-os-g1-005` than the earlier Step Functions/Kubernetes composition or the multi-step mcp-email-server near-precedent.

### Capability mint/binding

`src/lib/pipeline/guided-correction-completion.ts` generates a random 32-byte base64url capability token and authorizes it against a fixed attempt identity including:

- item id;
- listing id;
- completion run id;
- expected prior run id;
- expected review revision;
- for mobile flow, claim run id, idempotency key, and attempt generation.

The public client does not get a generic mutation surface: completion is a fixed privileged RPC, and the SQL function itself is executable only by `service_role`.

### Transactional completion primitive

`supabase/migrations/20260802204000_mobile_guided_correction_listing_regeneration.sql` defines `public.complete_mobile_guided_correction(...)` as one PL/pgSQL completion transaction. The function:

1. hashes the presented token and selects the capability row `FOR UPDATE`;
2. rejects missing, expired, or already-consumed capability rows;
3. verifies the commit is bound to the capability's item, completion run, and exact expected review revision;
4. locks the reservation, item, and listing rows `FOR UPDATE` and requires the durable item `review_revision` to equal the capability's expected prior revision, plus matching listing run/publication state;
5. locks the idempotent claim row and requires its exact attempt generation;
6. updates the item with a `WHERE ... review_revision IS NOT DISTINCT FROM expected_review_revision` predicate, failing if the state moved;
7. updates the listing with its expected prior run and editable-state predicates;
8. writes prediction/evidence/allowance/receipt state;
9. marks the capability `consumed_at` only when it is still unconsumed;
10. returns success only after all checks and writes pass.

Because these checks, target writes, and capability-consumption update are inside the same PostgreSQL function invocation, an uncaught exception aborts the statement transaction rather than leaving a successfully consumed capability paired with a rejected target mutation. The capability row and target rows are also locked before mutation.

This is the previously missing combined precedent: **scoped one-shot authority and expected-state freshness are enforced at the same durable mutation boundary, and successful target mutation and capability consumption commit together.**

### Public regression evidence

The repository's SQL test suite for mobile guided correction states that two live corrections holding the same review revision must not both complete against the same attempt generation, asserts that stale review revisions are rejected, and verifies the fixed completion RPC is inaccessible to ordinary authenticated callers while available only to the internal service role. The migration itself additionally rejects replay by requiring both capability and allowance completion rows to remain unconsumed.

Scope limit: this is a marketplace/database workflow, not an agent runtime. It demonstrates a systems invariant and implementation pattern, not an AGI-performance effect.

## Candidate refinement — `clean-os-g1-005`

The candidate no longer needs to be described only as a composition of separately demonstrated invariants. A concrete public implementation now demonstrates the combined transaction pattern.

A minimal Argus-specific adaptation can remain file-backed without persisting a readable bearer secret:

1. host mints a random one-shot secret but persists only its hash plus scope (`transition_kind`, `from_stage/route`, allowed target, exact state revision/digest, expiry);
2. low-level mutator acquires the existing pipeline file lock and reads one current pipeline object;
3. under that same lock, it verifies token hash, unused/expiry state, scope, deterministic evidence gate, and exact prior revision/digest;
4. it writes **one replacement pipeline object** that contains both the intended semantic state transition and the capability record marked consumed, while incrementing the durable state revision;
5. stale/replayed/mismatched requests write nothing; raw secret never needs to be persisted in model-readable state.

If capability metadata and pipeline state are kept in separate files, crash-safe atomic co-commit becomes harder and would need journaling/database support. Putting the capability hash/consumption metadata in the same authoritative state object is the closest file-backed analogue to the verified Snaplist transaction; whether that is acceptable for Argus state size/ownership is an untested adaptation question.

## Updated falsification matrix

1. normal Manager objective adoption remains lock-bound;
2. standalone objective CLI stale write is rejected with byte-identical state;
3. `argus learn` stale route write is rejected with byte-identical state;
4. fresh setup/admin writes still succeed;
5. capability token is bound to exact transition kind/from/target/state revision and cannot authorize a different mutation;
6. target state changes after mint -> stale capability rejected, unchanged state;
7. first valid use commits semantic transition + consumed marker in one atomic replacement/transaction;
8. replay -> rejected, unchanged state;
9. crash before commit -> neither transition nor consumed marker becomes durable;
10. crash after commit -> both transition and consumed marker are durable;
11. deterministic evidence/completion validator failure -> neither mutation nor consumption commits;
12. raw bearer secret is absent from model-readable durable state;
13. read-side revalidation still rejects old/corrupt state independent of write-time authority.

## Tested scope / uncertainty

- Argus source commit: `962cb06554daaede17b786c495e13ee3b6530e6e`, verified current `main` during this invocation.
- Snaplist source commit: `bf1e631ec8b01b53938f81b3e66764d6b151f792`, verified current `main` during this invocation.
- No unauthorized mutation or concurrent race was executed.
- PostgreSQL statement/transaction semantics support the all-or-nothing interpretation of the fixed completion function; no claim is made that Argus can obtain identical guarantees from multiple plain files without additional machinery.
- The proposed single-authoritative-object file adaptation is not tested in Argus and should be evaluated as an adaptation, not treated as imported evidence.

## Nonempty frontier

1. Inspect Argus `PIPELINE_STATE` schema/revision ownership to determine whether capability-hash metadata can safely live in the same authoritative object without creating model-facing leakage or unrelated writer churn.
2. Trace all remaining stage-machine production call sites and classify them as normal supervisor lock-bound, explicit admin/operator, or exported-but-unused library surfaces.
3. Search Argus tests/history/issues for live-session contracts around `argus learn` and math objective CLI; determine whether safest behavior is same-workdir live-daemon refusal or CAS-aware live mutation.
4. Inspect Snaplist's authorization migration and concurrent/replay SQL tests to extract the smallest storage invariants required for exact-once consumption, especially token hash uniqueness, expiry, row locking, and failed-transaction rollback.
5. Seek a matched file-backed implementation (not DB-backed) of the same one-object CAS+consume pattern; if absent, keep Snaplist as the strongest implementation precedent and test the Argus adaptation directly.

## Exact continuation

First inspect Argus pipeline-state schema/revision handling and determine whether one authoritative replacement can atomically carry both semantic state and a hashed one-shot capability consumed marker. Then finish the stage-machine production call-site matrix. In parallel, inspect Snaplist's capability-authorization migration and replay/concurrency SQL tests to extract minimal invariants for a faithful matched adaptation. Preserve the distinction between demonstrated external implementation, Argus-specific adaptation, and any later measured outcome.
