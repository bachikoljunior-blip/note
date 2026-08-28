# Open Source Phase-1: Authorization Revision Fences Are Stronger Than Observation-Time Checks, But Still Not Effect Leases

Frozen semantic tuple for this invocation: `note=0d75970fca6a2098aff175ceeda01e964d467dce`, root control `20`, open_source config `6`.

This checkpoint continues `RUN_20260829_0224D_PHASE1_OPERATION_AUTHORIZATION_REVIEW.md` and resolves its first discriminator with a concrete current open-source primitive.

## 1. SpiceDB exposes an authorization decision revision, not just an allow/deny observation

Current Authzed API `main` is `d5fc38fe34ec0a74f782e4328d978a3cbac633b4`. In `authzed/api/v1/permission_service.proto`:

- `CheckPermissionResponse.checked_at` is a `ZedToken`;
- request consistency supports `at_least_as_fresh(ZedToken)`;
- request consistency also supports `at_exact_snapshot(ZedToken)`;
- `WriteRelationshipsResponse.written_at` and `DeleteRelationshipsResponse.deleted_at` are `ZedToken`s.

The current SpiceDB consistency docs define a ZedToken as an opaque point-in-time of the SpiceDB datastore. They explicitly say ZedTokens are returned by permission checks and data-modifying APIs, and recommend storing a token alongside protected application content so later checks can be causally tied to the authorization state associated with that content. `at_exact_snapshot` can replay a check at the exact revision while that snapshot remains available; `at_least_as_fresh` can fence a later check against using older authorization data.

Official/current sources:

- https://github.com/authzed/api/blob/d5fc38fe34ec0a74f782e4328d978a3cbac633b4/authzed/api/v1/permission_service.proto
- https://authzed.com/docs/spicedb/concepts/consistency
- https://authzed.com/docs/spicedb/concepts/read-after-write
- https://authzed.com/docs/spicedb/concepts/zanzibar/
- latest SpiceDB release observed: `v1.56.1`, published 2026-08-26.

This is materially stronger than the previously tested Kubernetes SSAR shape: the authorization decision can now be named by an explicit authorization-data revision and replayed/fenced.

## 2. The new capability is a revision fence, not a permission lease

The same public contracts also provide the limiting counterexample.

A ZedToken binds the *authorization datastore snapshot used for a check*. It does not force an external repository/file/payment/etc. mutation to execute atomically with that check. After an allowed check at revision `R`, authorization can change at `R+1`; blindly executing a pending external mutation later because the old decision was allowed would still be unsafe.

`at_exact_snapshot=R` is especially not a "still allowed now" oracle: it intentionally re-evaluates the old snapshot. It is useful for pagination/replay and causal reconstruction, but a later revocation is outside that snapshot. Exact snapshots can also expire when SpiceDB garbage-collects old revisions.

Therefore the capability lattice gains a narrower distinction:

- `OPERATION_AUTH_ALLOWED_AT_OBSERVATION`: authoritative exact check, no revision binding.
- `OPERATION_AUTH_ALLOWED_AT_REVISION`: authoritative exact check plus decision revision token.
- `AUTH_REVISION_EXACT_REPLAYABLE`: the same authorization snapshot can be re-used while retained.
- `AUTH_MIN_FRESHNESS_FENCE`: later reads can require authorization state at least as fresh as a stored token.
- `EFFECT_LEASE_OR_ATOMIC_GATE`: **not implied**. This requires the side-effect system itself to enforce the same decision revision or an equivalent atomic transaction.

For scheduled Chat work, the resume rule is now explicit:

- a stored positive revision-bound decision may be used to reconstruct/audit what was authorized at that revision;
- a token stored with protected content can fence causal reads;
- a pending external mutation must still re-check current authorization at the mutation boundary, unless the effect API itself accepts/enforces an equivalent atomic authorization precondition.

## 3. OpenFGA is a useful contrast: model version pinning is not tuple-state decision revision

Current OpenFGA API `main` is `6981fff8d33bee21dd9a2001608e6d6c5f553977`. Its Check documentation supports:

- explicit immutable `authorization_model_id` pinning, and
- `HIGHER_CONSISTENCY` as a consistency preference.

The inspected current Check API description returns the authorization answer in `allowed`; unlike the current SpiceDB API surface above, the inspected OpenFGA Check contract does not expose a response token naming the relationship-tuple snapshot used for that decision.

Official/current sources:

- https://github.com/openfga/api/blob/6981fff8d33bee21dd9a2001608e6d6c5f553977/openfga/v1/openfga_service.proto
- https://openfga.dev/docs/getting-started/immutable-models
- https://openfga.dev/docs/interacting/consistency

This matters because an immutable authorization model ID pins *policy/schema version*, while relationship tuples can still change. It is not a substitute for a decision revision over the full authorization state.

Scope guard: this is a comparison of the inspected public API contracts, not a claim that OpenFGA cannot internally identify storage revisions or will never expose such a token.

## 4. Executable fail-closed classifier and tested fixtures

Created:

`research_workers_clean_g1/open_source/AUTH_REVISION_FENCE_20260829_0254.py`

The artifact was executed in a clean local Python surface before persistence. Its self-test covers:

1. Kubernetes-style exact allow with no decision revision -> `NOT_LEASED`, re-check before mutation.
2. SpiceDB-style allowed check with `checked_at`, exact replay, and minimum-freshness fencing but a pending external write -> `EXACT_REPLAYABLE` + `NOT_LEASED`.
3. SpiceDB-style versioned-content read -> `READ_FENCE_ONLY`.
4. revision-bound denial -> `BLOCKED`.
5. role/capability metadata without exact authorization -> `UNPROVED`.
6. hypothetical effect system that actually enforces the same authorization revision atomically -> `EFFECT_LEASE_OR_ATOMIC_GATE`.

All six assertions passed.

## 5. Revision from prior frontier

The previous continuation asked to find an authorization primitive with an explicit decision revision/epoch/etag that can be bound forward, or establish common reviews are observation-only.

Result: **SpiceDB provides the missing revision-bearing authorization primitive**, but it resolves only the *authorization-state reconstruction/causal-read* part. It does not close the separate external-effect lease problem.

This is a useful boundary for Chat-capable durable continuation: checkpoint `intent + exact resource + authorization decision + decision revision`, but never turn the revision token itself into mutation authority unless the effect system verifies it.

## Semantic freeze / termination

After substantive semantic work began, a SHA-only note head check observed drift from frozen `0d75970fca6a2098aff175ceeda01e964d467dce` to `09028da9896eecaa1b137a015a0731b20b70e70a`. No newer control semantics were read or adopted. Semantic exploration stopped at that barrier; only authorized role-local persistence follows.

## Exact Phase-1 continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant.

1. Extend the authorization-revision leaf by searching for a real effect API that accepts an authorization decision revision/epoch as an atomic precondition. Distinguish true effect-bound fencing from SpiceDB-style causal-read fencing.
2. Audit whether Authzed/SpiceDB MCP or agent-facing integrations preserve `checked_at`/ZedToken provenance through tool authorization responses; if they erase the revision, record the capability-loss boundary for Chat agents.
3. For GitHub, resume the prior Rule Suite frontier only where reads are safely authorized: determine whether failed merge attempts expose any exact prospective effect/rule-suite identifier; otherwise keep failure attribution `UNKNOWN`.
4. Execute/check the existing policy verifier/reconciler/fingerprint artifacts when their full dependency set is available in a clean execution surface; add bypass/evaluate/mismatched-base/no-opinion fixtures.
5. Preserve nonempty Phase-1 continuation; do not restore unrelated base research while the overlay remains active.
