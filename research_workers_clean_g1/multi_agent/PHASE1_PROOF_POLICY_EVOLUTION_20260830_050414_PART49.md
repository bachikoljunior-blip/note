# Phase-1 multi_agent checkpoint — proof-policy evolution and compatibility (Part 49)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `exact_blob_two_pass`
- predecessor: `PHASE1_SELF_LOCAL_PROOF_CONTRACT_20260830_050414_PART48.md`

Executable model: `research_workers_clean_g1/multi_agent/phase1_proof_policy_evolution_20260830_part49.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_proof_policy_evolution_20260830_part49.json`

This leaf asks when a Part48 proof-carrying artifact can remain terminal after the sanitized verifier/policy evolves, without a cross-role reader, external proof service, richer execution mode, finite quota, or manual migration.

The finite lattice has `4,096` scenario shapes and `24,576` strategy evaluations. Policy changes are `unchanged`, `compatible_minor`, `stricter_new_evidence`, or `scope_broadens_external`, crossed with current-policy result, evidence completeness, exact-version and exact-hash grandfather flags, policy-lookup freshness, same-version byte stability, old-artifact replay, response loss, artifact hash match, and schema validity.

## Public mechanism observations

The in-toto Attestation Framework defines TypeURI major-version semantics and explicitly says same-major messages are semantically correct but may be incomplete. Its monotonic principle is designed so ignoring a field cannot turn a DENY into an ALLOW:
- https://github.com/in-toto/attestation/blob/main/spec/v1/README.md

SLSA provenance uses the same pattern: incompatible changes alter the major version in `predicateType`, while minor changes are backwards-compatible and monotonic:
- https://slsa.dev/spec/v1.2-rc2/build-provenance

That does **not** imply that an old terminal/ALLOW result automatically remains terminal after every same-major change. A semantically correct old message may be incomplete for a stricter current policy. Parser compatibility and acceptance compatibility are distinct.

TUF provides a useful anti-rollback analogy: clients track trusted metadata versions, reject lower versions, and bind snapshot metadata to hashes/versions of referenced metadata. Its update rules show why a mutable name such as `latest` or a bare version number is weaker than an exact content identity plus current trust decision:
- https://theupdateframework.github.io/specification/draft/
- https://theupdateframework.io/docs/metadata/

These are architectural precedents only; this Phase-1 candidate does not add TUF infrastructure or a signing service.

## Finite-model results

### 1. Unpinned `latest policy` is unsafe under rollback, replay and response loss

`latest_unpinned_policy` terminalizes `288` scenarios, with `72` false terminals, `216` duplicate integrations, `96` stale-policy replays and `234` unsafe-effect scenarios. The failure mechanism is simple: an artifact whose acceptance identity does not bind the policy can be interpreted under a rolled-back or changed policy, and a lost response can cause the same logical result to be re-applied without knowing which policy authorized it.

A mutable `latest` lookup is therefore not an acceptance identity.

### 2. Exact version pinning is still ambiguous if bytes can change under the same version

`exact_version_allowlist` improves replay recovery but still has `116` false terminals and `96` stale-policy replays. The negative slice is same-version policy-byte mutation: the version string still matches while the verifier semantics have changed.

This does not mean version numbers are useless. It means a version is only a sufficient identity when the authority guarantees immutability of the bytes/semantics for that version. Without that invariant, terminal proof must bind an exact policy content hash or equivalent immutable object identity.

### 3. Same-major/minor compatibility is not automatic terminality preservation

The `monotonic_minor_range_negative` strategy treats same-major policy evolution as enough reason to retain an old terminal result. It has `108` false terminals and `128` stale-policy replays (`200` unsafe-effect cases total).

The public in-toto/SLSA monotonic parsing rule explains the correct narrower claim: an older same-major message can remain semantically parseable/correct while being incomplete. If the current verifier newly requires evidence, the old artifact can be safely DENIED until reverified; same-major compatibility does not grant an unconditional grandfathered ALLOW.

### 4. Exact policy-hash grandfathering is safe but requires current authority to say so

`exact_hash_allowlist` terminalizes `512` cases with `0` false terminals, `0` stale-policy replay and `0` duplicate integration in this model. Its proof obligation is strong and explicit:

- the artifact binds the exact old policy hash;
- current sanitized authority explicitly says that exact historical hash remains accepted for the stated terminal scope;
- result/application identity also binds that exact policy hash.

This supports stable grandfathering even if the current general policy is stricter or has broadened, because the current authority is explicitly granting the old exact policy identity.

However the frozen control26/config8 tuple does not expose a generic historical-policy-hash allowlist. Therefore this is a generic architecture candidate and unresolved control-surface child, not a claim that such a registry is already deployed.

### 5. Re-evaluation under the exact current policy hash is safe but deliberately conservative

`current_hash_bound_reverify` has `96` terminals and `0` unsafe effects. It ignores the old `passed=true` assertion and instead recomputes the current deterministic local predicate from the artifact plus embedded evidence, binding the new acceptance identity to the exact current policy hash.

It has many false exclusions (`580`) because it fails closed when:

- current evidence is incomplete;
- the policy source is not current/authoritative;
- the predicate has broadened to an external-fact scope that this CLEAN worker cannot decide locally.

This conservative behavior is correct under control26.

### 6. The best generic candidate is explicit exact-hash grandfather OR exact-current-hash reverify

`hybrid_hash_allowlist_or_current_reverify` terminalizes `560` scenarios with:

- false terminal: `0`
- duplicate integration: `0`
- stale-policy replay: `0`
- unsafe effect: `0`
- false exclusions: `116`

Its acceptance rule is:

1. **Grandfather path:** current sanitized authority explicitly allowlists the artifact's exact historical policy hash; or
2. **Migration path:** the verifier re-evaluates the artifact and complete embedded evidence under the exact current deterministic local policy hash.

In either path, the resulting acceptance/result identity includes the exact authorizing policy hash. An old result ID is never silently reused as a current-policy acceptance identity.

If the predicate becomes external-fact or all-role-completeness dependent, only an explicit exact-hash grandfather can preserve the old terminal scope. Otherwise the artifact is nonterminal until a role-authorized local proof exists; no external service or manual migration is counted as solved.

## Zero-dependency / zero-quota assessment

The accepted mechanism uses only sanitized current control/config plus role-local immutable proof artifacts and Chat-side deterministic verification. It adds no hosted runner, Codespaces, artifact/LFS/package service, cloud execution, external proof/signature service, external model/API credit, protected-primary execution, richer-mode arbitration, or manual user step. Incremental monetary cost is zero.

The exact-hash grandfather branch is not currently available as a generic config26 registry, so it remains an unresolved child rather than an accepted dependency. The current-hash re-evaluation branch is usable only for predicates fully decidable from allowed local inputs.

## Exact scope boundary

This leaf does not solve complete repository-authority rollback. If repository authority and every remembered local state are all rewound together, a current-hash verifier cannot prove from inside that same rollback domain that a later policy ever existed. That remains the previously identified authority-domain capability boundary.

It also does not claim a content hash is collision-proof in an absolute mathematical sense; the model assumes ordinary cryptographic collision resistance for the selected digest, as in standard content-addressed systems.

## Exact continuation

Next Phase-1 leaf: **policy revocation and grandfather compaction without a global historical allowlist**.

Compare:

1. per-artifact current-policy re-verification;
2. compact revocation floor keyed by predicate family/epoch;
3. exact policy-hash tombstone set;
4. Bloom/approximate revocation negative control;
5. immutable acceptance receipt tied to current policy hash.

Required adversaries: policy delete/recreate with name reuse, revoked old hash replay, role-local state loss, response loss during revocation write, stale revocation floor, policy-family epoch advance, and complete repository rollback.

Target a self-local zero-quota revocation proof that does not enumerate other-role artifacts. If safe compaction needs a new shared historical-authority surface, preserve it as an unresolved child rather than treating it as a handoff.
