# Phase-1 anti-rollback anchor lifecycle, key rotation, and simultaneous multi-path delivery

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- transport_mode: `sha_only_exact_sha`
- frozen semantic main SHA: `7bd9c35e1d72de624277bb495cad9accd79f0b4b`
- frozen DESIRED_STATE: control revision `24`, blob `f3221f10748a3d2ae86d9a544e27e5a44192b007`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_RETIREMENT_BARRIER_PATHS_20260829_062646_JST.md`
- semantic inputs: own source-qualified predecessor state plus public TUF, etcd, Sigstore, GitHub REST documentation and one finite synthetic mechanism model.
- script SHA-256: `fbe4ceab1473fd519f8d6f07bcccc12b110403114fde91ba5aa9559e6cae4f5e`
- result SHA-256: `664bfe0659c824de5499215a8ddd97a0ebfc82d1df94c7f3484a59f5e8ffc939`
- post-freeze head observation before persistence: `2cc11cd7151a64676170d7b032d33288d7a77006`; frozen root/config blobs were unchanged, so revision-24 post-freeze movement rule allowed persistence without adopting new semantics.

## Leaf objective

Stress the prior retirement-barrier candidate under: two old repairs racing through distinct publication paths; signer/key rotation with old-key trust, revocation, or trust-store rollback; local anchor states `CURRENT / STALE_REPLICA / LOST / RECOVERED_FROM_QUORUM`; ambiguous barrier-update response before failover; restoration of a validly signed but superseded certificate; generation advance g3→g4; dedupe expiry; and repository rate-limit interruption.

The new root revision also adds a decisive Phase-1 acceptance gate: a passing coordination mechanism cannot require hosted runners, Codespaces, cloud/external coordination, richer-mode arbitration, manual-user execution, finite monthly/trial/paid credits, or incremental monetary cost. Lightweight repository APIs may transport state/evidence, but must tolerate rate limits by checkpoint/backoff and may not be used as compute.

## Public mechanism boundary

TUF separates signature authenticity from freshness. Its metadata carries monotonically increasing versions; clients must not replace trusted metadata with a lower version, must reject expired metadata, and root rotation is validated through a continuity chain in which the next root is signed by threshold keys from both the old and new root. TUF also requires trusted root metadata to be persisted to non-volatile storage. This is direct public precedent for “a valid old signature is not sufficient current authority.”

etcd provides a cluster-wide revision, linearizable reads by default, and atomic transactions that compare values/revisions before applying a write set. Its disaster-recovery documentation explicitly warns that restoring an older snapshot can make revision numbers go backwards and provides revision bump / compaction guidance. These are useful mechanistic precedents for monotonic compare-and-update and rollback detection, but an independently hosted etcd quorum is **not** an accepted Phase-1 steady-state dependency in this role.

Sigstore Rekor is an append-only, cryptographically verifiable transparency log. It shows how an append-only witness can make historical records auditable, but a hosted transparency service is likewise only a public mechanism analogy here; it is not the accepted recurring-Chat coordinator.

GitHub's repository Contents API requires the current blob `sha` when updating a file and can return `409 Conflict`; GitHub also documents that concurrent content mutations can conflict. GitHub REST is rate-limited and explicitly instructs clients to stop/retry according to reset or retry-after guidance. Under control revision 24, this lightweight repository API is permitted only as state/evidence transport; rate-limit interruption must therefore become a fail-closed checkpoint, not a correctness shortcut.

Sources:
- https://theupdateframework.github.io/specification/draft/
- https://etcd.io/docs/v3.6/learning/api/
- https://etcd.io/docs/v3.7/op-guide/recovery/
- https://docs.sigstore.dev/about/security/
- https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

## Finite model

The executable model enumerates **6,912 equal-weight synthetic scenarios**:

- historical repair `FINAL / PENDING`;
- 6 unordered pairs of distinct publication paths from `queue / direct_api / retry_worker / restore_archive`;
- old-key state `OLD_TRUSTED / OLD_REVOKED / TRUST_ROLLBACK`;
- anchor state `CURRENT / STALE_REPLICA / LOST / RECOVERED_FROM_QUORUM`;
- barrier update `CONFIRMED_APPLIED / AMBIGUOUS_APPLIED / AMBIGUOUS_NOT_APPLIED`;
- restored certificate `CURRENT / SUPERSEDED`;
- current generation g3 or g4, with each raced old repair carrying the immediately preceding generation;
- dedupe contract `VALID / EXPIRED`;
- repository transport `AVAILABLE / RATE_LIMITED`.

There are 3,456 available-transport scenarios and 3,456 rate-limited scenarios. Counts are mechanism counts, not production probabilities.

Compared policies:

1. `permanent_tombstone` — retain the historical authority/effect identity indefinitely.
2. `signed_certificate_only` — trust a valid certificate without an independent freshness floor.
3. `single_anchor_min` — one local minimum-generation anchor, vulnerable to stale/rolled-back copies.
4. `quorum_version_floor_only` — use a quorum/linearizable floor, but do not require that the floor update be coupled to the generation transition.
5. `quorum_floor_coupled` — require current-generation/floor agreement and fail closed on a missing floor transition.
6. `append_only_version_witness` — reject certificates older than the visible append-only witness, but permit witness replicas to be stale/unavailable.
7. `repo_single_object_cas` — scheduled-Chat-native candidate: co-locate `current_generation`, retirement floor, certificate version, signer/key epoch, finality marker and `applied_transition_id` in one repository authority object updated by current-blob CAS; ambiguous response is reconciled by rereading that same object before retry.
8. `safe_archive_external` — strong semantic baseline using an independent quorum plus current certificate; intentionally rejected by the Phase-1 dependency gate.
9. `premature_repo_retire` — negative control that installs the coupled retirement floor while historical repair is still pending.

## Available-transport aggregate

| policy | safe compaction | unsafe old effect | duplicate repair | old-cert replay | current work blocked | pending repair falsely blocked | recovery reads |
|---|---:|---:|---:|---:|---:|---:|---:|
| permanent tombstone | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| signed certificate only | 1,152 | **576** | **1,152** | **576** | 1,728 | 0 | 0 |
| single-anchor minimum | 576 | **720** | **1,224** | 240 | 864 | 0 | 2,592 |
| quorum version floor only | 864 | **432** | **1,080** | 144 | 864 | 0 | 3,456 |
| quorum floor coupled | 864 | 0 | 0 | 0 | 864 | 0 | 3,456 |
| append-only version witness | 1,056 | **240** | **120** | **240** | 2,160 | 0 | 3,456 |
| repository single-object CAS | **1,152** | **0** | **0** | **0** | 576 | **0** | 1,152 |
| safe archive with external quorum | 864 | 0 | 0 | 0 | 1,296 | 0 | 6,912 |
| premature repository retire | 1,152 | 0 | 0 | 0 | 1,152 | **1,728** | 2,304 |

## Result 1: a quorum-backed monotonic certificate-version floor is not sufficient by itself

The targeted slice where historical repair is final, a quorum is reachable, but the barrier update response was ambiguous and readback shows the floor update **did not apply** contains **432** scenarios. `quorum_version_floor_only` is unsafe in **432 / 432**: quorum accurately returns the old floor, and that old floor still authorizes the raced previous-generation publication. Linearizability cannot manufacture a transition that never committed.

`quorum_floor_coupled` is unsafe in 0/432 because it requires `floor == current_generation` and fails closed on mismatch. The repository-native single-object candidate is also unsafe in 0/432 and blocks current work in 432/432 until the one authority object can be advanced. Therefore the sufficient condition is stronger than “quorum-backed monotonic floor”: **generation transition and retirement-floor transition must share one authority transition, or publication must reject any observable mismatch.**

## Result 2: key revocation does not make an old valid signature fresh

The slice with final historical repair, a `SUPERSEDED` certificate and an old key that is still trusted or has been reintroduced by trust-store rollback contains **576** scenarios. `signed_certificate_only` is unsafe in **576 / 576**. An append-only version witness reduces but does not eliminate the problem: it is unsafe in **240 / 576** when the visible witness is stale or the current witness update never committed.

The repository single-object candidate is unsafe in **0 / 576** because path authorization is derived from the current authority object, not from the restored certificate alone; its signer/key epoch and certificate-version floor move with the generation transition. This is synthetic application-protocol evidence, not a claim that GitHub natively provides certificate rotation semantics.

## Result 3: simultaneous distinct paths turn freshness errors into duplicate effects

Each available scenario races two old publications through different paths. Weak policies that accept the stale authority can therefore create both resurrection and duplication when dedupe has expired. `signed_certificate_only` records **1,152** duplicate-repair scenarios; `single_anchor_min` 1,224; and `quorum_version_floor_only` 1,080. The repository single-object candidate has duplicate repair 0 because both paths must validate the same current authority state before authoritative integration.

The boundary is important: the candidate requires **every authoritative path** to validate that one object. A direct effect route that can bypass the authority read remains an unresolved child, not a passing handoff.

## Result 4: finality still gates retirement

There are **1,728** available scenarios with historical repair still `PENDING`. The `premature_repo_retire` negative control falsely blocks legitimate repair in **1,728 / 1,728**. The repository single-object candidate blocks **0 / 1,728** because it retains the historical effect witness until finality is established.

Thus key rotation, stronger CAS, or a better floor cannot substitute for semantic finality.

## Result 5: repository rate limits should stop progress, not weaken authority

All **3,456** rate-limited scenarios force the repository single-object candidate to take no authority decision or effect, record a checkpoint, and retry on a later invocation. The model has unsafe old effect **0**, duplicate repair **0**, checkpoint **3,456 / 3,456**. This is a liveness cost, not a safety exception.

GitHub documents time-window rate limits and retry/reset behavior; this mechanism does not require GitHub Actions, hosted runners, Codespaces, packages/artifacts/LFS, cloud credits, external model/API credits, or manual execution. API volume is only state transport, not compute.

## Phase-1 dependency / quota assessment

`repo_single_object_cas` passes the current leaf's Phase-1 acceptance gates **within the exact tested scope**:

- residual richer-mode / protected / manual-user execution dependency: **none**;
- external hosted coordination dependency: **none** beyond the explicitly permitted lightweight repository transport;
- hosted runner / Codespaces / artifact / LFS / package / cloud-credit dependency: **none**;
- finite monthly/trial/paid quota dependency: **none identified**;
- incremental monetary cost: **0**;
- repository rate-limit interruption: **fail closed + durable checkpoint + later retry**.

`quorum_floor_coupled` and `safe_archive_external` are semantic safety baselines only. As instantiated with an independent distributed quorum they fail Phase-1 acceptance because they add external hosted coordination.

## Exact tested scope and unresolved child

The repository single-object result assumes that the authority object is outside the modeled **application** restore domain and that every authoritative publication path consults it. This leaf does **not** prove safety if the repository authority itself is rewound, force-rewritten, deleted/recreated, or restored to an older commit together with all of the worker's persistent memory. An append-only file chain inside the same rollback domain cannot by itself tell a stateless future invocation that a hidden newer version once existed.

That repository-wide anti-rollback problem remains unresolved under the zero-external-dependency rule. TUF's persistent trusted-root rule and etcd's restore/revision guidance both reinforce the need for a monotonic trust state outside the thing being rolled back, but importing a hosted quorum/transparency service would violate this Phase-1 leaf's acceptance constraint.

## Candidate repository-native protocol

1. One authority record per logical claim/effect domain contains current parent/generation, retirement floor, claim/integrator epoch, certificate/key epoch, terminal/finality marker, durable effect IDs and `applied_transition_id`.
2. Update that record only with current-blob CAS. Generation advance and retirement-floor/key-epoch advance are one replacement, never separate files whose partial success can create semantic authority.
3. Workers write only immutable staged results. No staged file is itself authoritative.
4. Every authoritative integration path rereads the authority record and checks parent/generation, claim epoch, effect identity, finality, key/certificate epoch and result digest immediately before integration.
5. On ambiguous write response, rate limit, timeout, or `409`, do **not** infer success; checkpoint, reread the authority record on a later safe opportunity, and use `applied_transition_id` to distinguish applied from unapplied before retry.
6. Do not compact the historical repair/effect witness while repair is pending.
7. A restored certificate or trust store is advisory until its version/key epoch matches the current authority record; an old valid signature cannot lower the authority floor.
8. Keep a permanent compact tombstone if the authority record cannot be proven current.
9. Treat any path that bypasses this authority object as an unresolved Phase-1 child rather than as an accepted handoff.
10. Do not claim repository-wide rollback protection from this mechanism.

## Exact continuation

Next Phase-1 leaf: **same-repository authority rollback / ref rewrite without external anchors**.

Finite grammar:
- authority record at v3/v4;
- branch/ref state `CURRENT / FORCE_REWOUND / DELETE_RECREATE / DIVERGENT_SIBLING`;
- immutable version files retained/hidden/unreachable;
- current `LATEST` pointer current/stale/missing;
- ambiguous CAS response before ref rewrite;
- worker restart with no memory except allowed own repository state;
- commit/blob SHA known only if preserved in current state versus lost with rollback;
- two publication paths retry concurrently after recovery;
- repository rate limit available/interrupted.

Compare:
- current pointer only;
- append-only version files on same branch;
- commit-SHA chain stored only inside same rollback domain;
- separate repository ref/tag anchor if Chat-write capability and role-local boundary permit it;
- permanent tombstone in same authority object;
- fail-closed “cannot prove no rollback” policy.

Primary falsification: determine whether any mechanism using **only state that is rewound together** can distinguish “v3 was always latest” from “v4 existed and the repository was rolled back to indistinguishable v3.” If not, record the indistinguishability proof as an exact unresolved child and search for a scheduled-Chat-native authority surface that is genuinely outside that rollback domain without requiring richer-mode, user action, hosted coordination, monthly credits, or incremental cost.

Keep the Phase-1 frontier nonempty; do not resume unrelated base research while the overlay remains active.
