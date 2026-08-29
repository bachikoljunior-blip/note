# Phase-1 multi_agent checkpoint — CANCELLED tombstone + lazy cell release (Part 34)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `68446d6322630d4ba65d734db1422c50a5782f78`
- sanitized root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 33 / same-generation abandoned reservation cleanup
- post-freeze main movement was observed; exact root/config identities remained unchanged.

## Selected leaf

Part 33 made `GRANTED -> CANCELLED` and `GRANTED -> AUTHORIZED` mutually exclusive CAS transitions in one reservation grant record. This leaf asks what happens **after `CANCELLED` wins**, while the old reservation may still be physically present in one or more cell records.

The candidate is **logical revocation first, physical cleanup later**:

- the durable reservation record stays `CANCELLED`;
- stale cell rows continue to point to the old reservation ID until reclaimed;
- a new claimant encountering such a row reads the referenced reservation, proves it is currently `CANCELLED`, and CAS-reclaims that single cell under the new deterministic reservation ID;
- the new claimant's partial cell prefix remains `PREPARED` and therefore non-authoritative.

This makes per-cell deletion/release garbage collection rather than the revocation proof.

## Public mechanism audit

GitHub's Contents API update requires the blob `sha` of the file being replaced and can return `409 Conflict`, which is sufficient for a current-cell compare when reclaiming one stale holder row. It is still a per-path primitive:
- https://docs.github.com/en/rest/repos/contents

Kubernetes explicitly separates a reusable object **Name** from a lifetime-unique **UID**; a deleted object can be recreated with the same name while the new occurrence receives a different UID. This is a public precedent for using incarnation-sensitive identity rather than a resettable logical name/epoch in the cell ABA case:
- https://kubernetes.io/docs/concepts/overview/working-with-objects/names/

## Finite stress grammar

Executable model: `research_workers_clean_g1/multi_agent/phase1_cancelled_release_20260829_190119_part34.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_cancelled_release_20260829_190119_part34.json`

The semantic model has `864` scenario shapes and `5,184` strategy evaluations over:

- six single/spanning logical claim shapes on three cells;
- old-cell cleanup state `none / partial / full`;
- reservation witness `CURRENT_CANCELLED / MISSING / ROLLED_BACK_GRANTED`;
- cell delete/recreate ABA;
- incarnation-sensitive vs resettable identity;
- late old-owner return;
- complete vs incomplete serial registry.

Compared mechanisms:

1. block whenever a stale holder row remains;
2. eager physical release with no lazy proof;
3. copy cancellation state into cells and wait for cell cleanup;
4. **durable reservation-level tombstone + lazy cell reclaim**;
5. treat a missing tombstone as proof the holder is gone (negative control);
6. complete staged/fenced integrator.

A separate `72`-scenario recovery model covers crash/response-loss/rate-limit interruption, durable tombstone availability, deterministic new reservation identity, and stale-row presence.

Counts are finite synthetic mechanism counts, not observed failure rates.

## Current-tombstone strong slice

With `CURRENT_CANCELLED`, incarnation-sensitive cells, and complete registry fixed, there are `72` scenarios per mechanism:

| mechanism | unsafe | progress | blocked | false block | tombstone/reclaim reads |
| --- | ---: | ---: | ---: | ---: | ---: |
| block stale rows | 0 | 28 | 44 | 44 | 0 |
| eager release | 0 | 28 | 44 | 44 | 0 |
| per-cell cancel copy | 0 | 28 | 44 | 44 | 0 |
| **lazy reservation tombstone** | **0** | **72** | **0** | **0** | 68 |
| missing-is-free control | 0 | 72 | 0 | 0 | 68 |
| complete staged integrator | 0 | 72 | 0 | 0 | 72 |

The missing-is-free control happens to be safe in this slice only because the tombstone is explicitly current; its failure appears when the witness is absent.

### Result 1 — logical revocation can precede multi-cell cleanup

With a current `CANCELLED` reservation witness, lazy reclaim was **0/72 unsafe and 72/72 progress**, even if no cell, one cell, or every cell had already been physically cleaned.

By contrast, mechanisms that demanded the claim's relevant cells be physically cleared/marked before admitting the next claim made only `28/72` progress and produced `44/72` false blocks. A partial cleanup crash therefore does not need a multi-cell release transaction if all new claimants can follow the stale holder pointer to one durable terminal reservation record.

This is the central new result: **the post-cancellation authority object is the reservation tombstone, not the set of cell cleanup writes**.

### Result 2 — missing tombstone must fail closed

When the stale holder's terminal record was missing, the strong lazy mechanism blocked **72/72** with unsafe `0`. Treating missing as equivalent to cancelled/free admitted all 72 and was **44/72 unsafe**, exactly where at least one relevant stale holder row remained.

Thus cleanup cannot delete the cancellation witness merely because some cells appear free. The absence of the proof is not proof of absence.

### Result 3 — cell identity must be incarnation-sensitive

With current cancellation evidence and a forced cell delete/recreate ABA:

- current blob/incarnation-sensitive identity: **0/36 unsafe**;
- logical name or resettable numeric epoch only: **36/36 unsafe**.

Kubernetes' name-vs-UID distinction is a public analogue: the same logical name can refer to a later occurrence, while UID distinguishes historical incarnations. citeturn171253search0

For this repository protocol, the current file blob SHA plus holder reservation identity serves as the immediate compare; a separately resettable integer must not be the only proof. GitHub documents the current `sha` requirement and `409` conflict behavior for updates. citeturn831430search1

### Result 4 — partial per-cell cancellation remains a liveness tax

In the current-tombstone/incarnation-strong slice, a per-cell cancellation-copy design produced:

- no cleanup: `0/24` progress;
- partial cleanup: `4/24` progress, `20/24` blocked;
- full cleanup: `24/24` progress.

It is safe in this abstraction but unnecessarily couples logical revocation to wide cleanup completion. The reservation-level tombstone removes that coupling.

### Result 5 — deterministic identity/readback still matters during lazy reclaim

In the recovery model, with stale cells present:

- durable cancellation tombstone + deterministic new reservation ID: **9/9 resumable, 0 orphan, 0 self-conflict**;
- no durable tombstone: **18/18 orphan/unprovable reclaim authority**;
- durable tombstone but new/random retry ID: **9/9 self-conflict** in the ambiguous-partial-write model;
- rate-limit interruption with the strong pair: **3/3 safe checkpoint and 3/3 resumable**.

Again, repository rate limits are a checkpoint/backoff condition, never a reason to treat stale authority as dead.

## Rollback/GC boundary

The model deliberately includes a stronger negative control: the repository-visible reservation state is rolled back from `CANCELLED` to an old `GRANTED` state and a late old owner returns. The lazy protocol is **36/36 unsafe** in that slice because every current read now says the old grant is live.

This is not fixable by adding more files **inside the same completely rolled-back authority domain** unless some monotonic witness survives the rollback. The current leaf therefore does not claim repository-wide force-rewind/restore safety.

That unresolved case is narrower than ordinary cleanup: with a current tombstone, cleanup can be fully lazy and local; with total authority rollback, the evidence needed to distinguish histories has itself disappeared.

## Phase-1 zero-dependency / zero-quota assessment

The tested lazy-release mechanism is repository-local and Chat-capable. It requires no hosted runner, Codespaces, artifact/LFS/package service, cloud-credit executor, external lock service, manual user execution, paid/trial/monthly quota, or incremental monetary spend. Lightweight repository reads/CAS are state transport and are allowed to fail/rate-limit with durable checkpoint/resume.

Global Phase-1 closure is **not** claimed. Two unresolved children remain:

1. **complete authority-domain rollback/restore** that erases the durable `CANCELLED` witness;
2. **arbitrary protected external effect after `AUTHORIZED`**, where sink-native idempotency/status/fencing is not exposed.

Neither is packaged as an accepted richer-mode or user handoff.

## Scope limits

- Three logical cells and six claim shapes.
- Stale cell rows carry a holder reservation ID that a claimant can resolve to the terminal record.
- Current blob/incarnation identity is assumed available for cell CAS.
- Tombstone retention/compaction is not solved yet.
- Complete repository rollback is intentionally a negative control.

## Exact continuation

Next leaf: **cancellation-tombstone retention and compaction** under the Phase-1 zero-quota constraint.

Compare:

1. permanent per-reservation tombstone;
2. compact monotonic per-cell retired-holder floor;
3. append-only reservation terminal index;
4. generation-level cancellation watermark;
5. fail-closed no-GC.

Enumerate all cells cleaned, stale-cell restore, cell delete/recreate, task-key reuse, repository branch rewind/restore, response loss, and rate-limit interruption.

Primary question: **what is the weakest durable witness that bounds state growth without allowing a cancelled reservation to become authoritative again?** Explicitly test whether any witness stored in the same rollback domain can solve a complete repository rewind, or whether that history pair is information-theoretically indistinguishable and must remain unresolved.
