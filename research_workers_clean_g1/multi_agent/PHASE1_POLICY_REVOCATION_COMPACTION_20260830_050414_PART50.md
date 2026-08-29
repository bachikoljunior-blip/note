# Phase-1 multi_agent checkpoint — policy revocation and grandfather compaction (Part 50)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `exact_blob_two_pass`
- predecessor: `PHASE1_PROOF_POLICY_EVOLUTION_20260830_050414_PART49.md`

Executable finite fixture: `research_workers_clean_g1/multi_agent/phase1_policy_revocation_compaction_20260830_part50.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_policy_revocation_compaction_20260830_part50.json`

Part 49 found that an old proof-carrying artifact can safely remain terminal only when current authority either explicitly grandfathers its exact historical policy hash or re-evaluates it under the exact current deterministic local policy hash. Part 50 asks how to represent revocation compactly without introducing a hosted revocation service or cross-role artifact scan.

The finite lattice has `16,384` scenario shapes and `114,688` strategy evaluations. It crosses four revocation shapes (`prefix_only`, `sparse_only`, `prefix_plus_sparse`, `family_recreate`) with old-artifact replay, response loss, current/stale revocation state, family incarnation match, epoch floor membership, exact-hash tombstone membership, Bloom false positives, current local re-verification, and complete authority-domain rollback.

## Public mechanism observations

TUF's update model keeps monotonically checked metadata versions and rejects rollback to lower trusted versions. Snapshot metadata binds referenced metadata by version/hash, which is a useful public precedent for separating current trust state from an artifact's old signature or name:
- https://theupdateframework.github.io/specification/draft/
- https://theupdateframework.io/docs/metadata/

Bloom filters are compact probabilistic membership structures with false positives but, under the intended construction, no false negatives for inserted elements. Public documentation makes that availability/safety asymmetry explicit:
- https://docs.cloud.google.com/memorystore/docs/valkey/about-bloom-filters
- https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter

These are mechanism precedents only. The candidate below does not add TUF, Memorystore, RocksDB, a hosted revocation service, or any quota-bearing dependency.

## Result 1 — prefix floors and sparse tombstones solve different revocation shapes

On the `2,048`-scenario mechanism-invariant slice, a family epoch floor alone has `64` unsafe effects. By mode, it is safe for prefix revocation but misses `32` sparse-only and `32` prefix-plus-sparse revocations. An exact hash tombstone set is the mirror image: safe for sparse-only but misses `32` prefix-only and `32` prefix-plus-sparse cases.

Therefore a compact monotonic `min_accepted_epoch` and an exact sparse revoked-hash set are complementary rather than interchangeable:

- the floor represents “every artifact before epoch N is revoked” in O(1) family state;
- exact hash tombstones represent non-prefix exceptions without materializing every historical artifact.

With an incarnation-sensitive policy-family identity, `floor_plus_exact_tombstone` has `0` unsafe effects on all four modeled current-state revocation modes.

## Result 2 — a Bloom sparse set is a storage/availability trade-off, not stronger authority

Replacing the sparse exact set with an idealized no-false-negative Bloom filter also has `0` unsafe effects on the invariant slice, but creates `96` Bloom-specific false exclusions and `280` total false exclusions versus `216` for the exact set.

That behavior is acceptable only if false-positive denial is an explicit availability trade-off. A Bloom filter cannot establish a stronger revocation proof than the authoritative set it approximates; its benefit is compact representation, and its cost is denying some valid artifacts.

## Result 3 — current local re-verification can recover availability without resurrecting old authority

`current_policy_reverify` is safe on the invariant slice but conservative: `128` terminals, `0` unsafe effects, `216` false exclusions. The combined strategy `floor_tombstone_or_current_reverify` reaches `224` terminals with `0` unsafe effects and only `120` false exclusions.

The important identity rule is that re-verification mints a **new acceptance identity bound to the exact current policy hash**. It does not remove a revocation record or reinterpret the revoked old acceptance as valid. This preserves Part 49's result-ID/policy-hash fencing rule.

## Result 4 — immutable acceptance receipts alone cannot survive later revocation

A historical immutable `accepted=true` receipt, when treated as permanently terminal without consulting current revocation authority, has `576` unsafe effects in the invariant slice. Immutability proves that an acceptance occurred; it does not prove that the acceptance has not since been revoked.

This is the same authenticity/freshness split seen in earlier leaves: durable history is useful for provenance and response-loss recovery, but current authorization remains a separate predicate.

## Result 5 — delete/recreate requires family incarnation identity

A policy family name is reusable. A revocation floor such as `family=X, epoch>=4` cannot safely govern a later logically distinct family that reuses the same name unless the family has an incarnation-sensitive identity.

The candidate therefore binds each artifact and revocation record to `policy_family_incarnation_id`, not only a display name. Delete/recreate produces a new incarnation; old artifacts do not silently cross that boundary.

## Result 6 — complete repository rollback defeats every repository-local revocation witness tested

The strongest negative control contains 32 scenarios where a later authority state really revoked the artifact, but the repository authority **and all remembered role-local policy/revocation state are then completely rewound**. The worker sees a self-consistent pre-revocation world.

Unsafe counts in this rollback slice are:

- immutable acceptance receipt only: `32/32`
- family floor only: `32/32`
- exact tombstone only: `32/32`
- floor + exact tombstone: `32/32`
- current-policy re-verification: `32/32`
- floor/tombstone OR current re-verification: `32/32`

The Bloom variant blocks 16 cases only because its false-positive bit happens to deny them. That is accidental denial, not anti-rollback authority.

This is an indistinguishability boundary for the modeled authority domain: if all evidence that “a later revocation existed” lives inside the same rollback domain and all of it is rewound, a future stateless invocation cannot distinguish:

1. a world that never advanced past the old policy; from
2. a world that advanced, revoked the artifact, and was completely rolled back.

No repository-local floor, tombstone, acceptance chain or current-policy hash can prove the missing history after that complete rollback.

## Current candidate within the tested non-rollback scope

For a self-local policy family whose current repository authority is trustworthy and not completely rolled back, the strongest compact candidate is:

1. incarnation-sensitive `policy_family_id`;
2. monotonic `min_accepted_epoch` for prefix revocation;
3. exact sparse revoked-policy/artifact hash tombstones (or an explicitly availability-sacrificing Bloom representation if false-positive denial is acceptable);
4. artifact/result identity bound to exact authorizing policy hash and family incarnation;
5. optional current deterministic local re-verification that creates a new current-policy acceptance identity rather than resurrecting the revoked one;
6. response-loss recovery by immutable deterministic result/revocation identities.

The frozen control26/config8 tuple does not expose a generic shared historical hash/tombstone registry. That absent control surface remains an unresolved child rather than an accepted execution dependency.

## Zero-dependency / zero-quota assessment

The finite model and accepted current-state mechanism need only scheduled-Chat reasoning plus role-local repository state/transport. No hosted runner, Codespaces, artifact/LFS/package service, cloud execution, external model/API credit, external revocation/proof service, richer-mode arbitration, protected-primary execution, or manual user action is added. Incremental monetary cost is zero.

The complete-rollback boundary is **not** treated as solved by asking for an external quorum, transparency service, user action, or protected execution. It remains an unresolved capability child.

## Exact continuation

Next Phase-1 leaf: **rollback-domain escape without hosted coordination**.

Compare only CLEAN-safe candidates:

1. user-visible immutable prompt/control facts already available to scheduled Chat;
2. Git object reachability/ancestry as a historical witness;
3. read-only repository branch-protection/ruleset facts where allowed and semantically relevant;
4. role-local acceptance-receipt chains;
5. multiple independent repository refs when they are genuinely separate rollback domains;
6. fail-closed no-witness baseline.

Adversaries: force-rewind, delete/recreate, unreachable-but-existing Git objects, full role-local state loss, all candidate refs rewound together, response loss, and authority name reuse.

The goal is to determine whether any scheduled-Chat-native, zero-cost, zero-finite-quota witness is genuinely outside the repository rollback domain. If none is available, formalize the indistinguishability boundary, preserve it as an unresolved child, and select the next independent non-conflicting multi-agent leaf rather than declaring Phase-1 complete.
