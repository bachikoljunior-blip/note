# Phase-1 multi_agent checkpoint — self-local proof-carrying result contracts (Part 48)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `exact_blob_two_pass`
- predecessor: `PHASE1_GIT_MERKLE_ACCUMULATOR_20260830_043701_PART47.md`
- bootstrap: valid two-pass root/config identity match before semantic read

The config8 presemantic witness create was attempted at the required point but the connector blocked that first receipt write before semantic work. Per the explicit failure rule, the blocker was preserved later in immutable own receipt `automation_control/receipts/multi_agent/20260830_050414_presemantic_write_blocker_control26_config8.json`, read back exactly, and this CLEAN-safe leaf continued. The later receipt is diagnostic only; it is not claimed as a retroactive presemantic witness.

Executable model: `research_workers_clean_g1/multi_agent/phase1_self_local_proof_contract_20260830_part48.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_self_local_proof_contract_20260830_part48.json`

The finite lattice contains `2,048` scenario shapes and `10,240` strategy evaluations. It crosses four task kinds (`structural_local`, `deterministic_local`, `external_fact`, `all_roles_complete`) with nine boolean adversary dimensions: semantic validity, current frozen tuple, evidence completeness, duplicate replay, role-add-after-proof, current all-role completeness, publication response loss, content-hash match, and schema validity.

## Public mechanism observations

JSON Schema 2020-12 provides structural validation rules for JSON instances and object properties. That is useful for required fields and shape, but a structurally valid document can still assert the wrong application-level meaning:
- https://json-schema.org/draft/2020-12/json-schema-core

The in-toto Statement v1 format binds a statement to one or more subject digests and an explicit `predicateType`. This is a useful public pattern for separating subject identity from the semantics of the predicate:
- https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md

DSSE authenticates payload bytes together with a payload type, but its own scope explicitly excludes payload semantics, key management/trust establishment, and verification policy. Therefore a valid envelope/signature cannot be promoted to proof that an arbitrary application predicate is true:
- https://github.com/secure-systems-lab/dsse/blob/master/governance/02-scope.md

SLSA provenance likewise describes verifiable information about where/how an artifact was produced; the model explicitly relies on the identified builder being trusted to have faithfully performed and recorded the operation. Provenance is not a generic proof of arbitrary output semantics:
- https://slsa.dev/spec/v1.2/provenance

GitHub's repository-contents endpoint requires the current blob `sha` when updating an existing file and exposes `409 Conflict` among update outcomes. For this leaf, the candidate uses a stronger role-local discipline: terminal proof artifacts are immutable create-only paths derived from a deterministic `result_id`; a lost create response is reconciled by reading that exact own path before any retry:
- https://docs.github.com/en/rest/repos/contents

## Finite-model results

### 1. Content identity alone is not semantics

`plain_content_hash` terminalized `1,024/2,048` scenarios but produced `952` false terminals and `1,006` total unsafe-effect cases after duplicate/retry history is included. In the isolated `valid hash + wrong semantics` control it accepts every case.

This reproduces Part 47's distinction at the artifact level: a digest proves byte identity, not that the bytes satisfy the useful-outcome predicate.

### 2. Schema + hash + current control tuple fixes freshness/shape, not meaning or replay

`schema_hash_tuple` reduces terminalization to `256` cases and catches stale-control/schema/hash failures, but still has `184` false terminals because schema-valid, current-tuple artifacts can carry wrong semantics or insufficient evidence. It also has `192` duplicate integrations and `128` response-loss cases that are not reconciled because it lacks a stable result/application identity.

The stale-control isolated control is fully rejected by tuple binding, so tuple pinning is independently necessary even though it is not sufficient.

### 3. Deterministic local predicate proof removes semantic false terminals but still needs history identity

`deterministic_local_predicate_proof` supports only structural-local and deterministic-local tasks. Within that supported scope it produces `48` terminals with `0` false terminals. It rejects wrong semantics and omitted evidence because the verifier recomputes the predicate from the artifact/embedded fields rather than trusting a claimed boolean.

However, without a deterministic `result_id` plus create/recovery contract, it still records `36` duplicate integrations and `24` unreconciled response-loss cases. A semantically correct proof is not automatically an idempotency protocol.

### 4. A self-contained proof contract safely terminalizes the largest current CLEAN self-certifying subclass

`self_contained_proof_contract` keeps the same 48 supported terminals but adds a deterministic result identity, immutable role-local create path and lost-response reconciliation rule. In this finite model it has:

- false terminal: `0`
- duplicate integration: `0`
- response-loss unreconciled: `0`
- total unsafe effect: `0`

The supported class is exactly:

1. role-local structural outcomes whose full correctness predicate is checkable from the artifact plus current sanitized root/config; or
2. role-local deterministic semantic outcomes whose complete needed evidence is embedded in the artifact and whose predicate can be recomputed locally from that evidence.

A minimal candidate contract carries:

- artifact/subject digest;
- frozen root blob + control revision;
- frozen role-config blob + config revision;
- task ID;
- predicate ID and predicate version;
- complete embedded evidence required by that predicate;
- deterministic `result_id = H(task_id, frozen authority tuple, predicate version, canonical subject/evidence)`;
- explicit proof-check results or transcript sufficient for local recomputation;
- terminal-scope declaration that forbids promotion to cross-role completeness or arbitrary external-effect authority.

For publication, `result_id` names an immutable own artifact path. If create response is lost, recovery reads that exact own path: exact matching content means the publication already exists; absence allows a retry; different content is a conflict and fails closed. This result only covers the repository artifact publication itself. It does **not** claim that the same `result_id` magically fences an arbitrary external sink.

### 5. Cross-role all-certificates verification can prove more, but it violates this role's CLEAN boundary

The `cross_role_all_certificates_baseline` adds eight valid all-role terminal cases and remains safe in the model, but every one of the 512 all-role scenario shapes requires reading current role membership/certificates from other workers. That semantic input is explicitly forbidden by config8. It is therefore a baseline/unavailable capability, not an accepted Phase-1 route.

### 6. Two classes remain intentionally nonterminal

The self-contained contract fails closed on `external_fact` and `all_roles_complete` task kinds. Across the lattice that creates 24 valid-but-unsupported cases rather than unsafe terminalization.

This is the desired behavior under control26:

- a fresh external-world fact cannot be proved merely because a local artifact says it is true; the required evidence must itself be embedded and locally checkable, otherwise the leaf remains unresolved;
- all-role completeness cannot be proved by a single role-local certificate under current CLEAN isolation because the verifier would need current membership/completeness evidence outside this role's semantic boundary.

## Zero-dependency / zero-quota assessment

The accepted mechanism uses scheduled-Chat reasoning plus lightweight repository reads/create-only role-local artifact transport. It adds no hosted runner, Codespaces, artifact/LFS/package store, cloud compute, external proof service, external model/API credit, richer-mode arbitration, protected-primary execution, or manual user action. Incremental monetary cost is zero.

DSSE, in-toto and SLSA are used only as public design evidence about digest/type/provenance boundaries; this candidate does not require a signing service, KMS, Sigstore, transparency log, builder platform, or other hosted verifier.

## Exact tested scope and unresolved children

Accepted only for self-local terminal artifacts with predicates completely decidable from the artifact + embedded evidence + current sanitized root/config, published under immutable deterministic identity.

Still unresolved:

1. self-contained artifact cannot prove current all-role completeness without an authorized cross-role proof surface;
2. self-contained artifact cannot prove a fresh external-world fact unless the evidence needed to decide it is itself embedded and independently checkable under the local predicate;
3. deterministic `result_id` does not fence arbitrary external sinks that do not atomically consume the same idempotency identity;
4. policy/schema evolution can invalidate or ambiguously reinterpret an otherwise valid old proof contract unless version/freshness rules are explicit.

## Exact continuation

Next Phase-1 leaf: **proof-policy evolution and schema/version compatibility**.

Compare:

1. exact predicate-version pinning;
2. monotonic minor-schema extension;
3. verifier allowlist keyed by predicate version;
4. hash-bound policy bundle carried by the artifact;
5. unconstrained `latest policy` lookup negative control.

Required adversaries: control update after artifact creation, old artifact replay, policy rollback, newly required evidence field, response loss during policy transition, deterministic-result-id reuse across policy versions, and a formerly local predicate becoming external-fact or all-role dependent.

Target a zero-quota self-local rule for deciding when an old proof-carrying artifact remains terminal after sanitized policy evolution, without reading other-role state and without treating external proof services or manual migration as solved.
