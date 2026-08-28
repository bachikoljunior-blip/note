# Phase 1 follow-up — durable checkpoint publication crash matrix

Status: role-local Phase-1 continuation under frozen semantic tuple `4632516483a5fb873c0ebc4b1709cb8505a9271a` / control rev 16 / reasoning config rev 6. This follows the direct architecture and handoff crash-model checkpoints. No post-freeze repository semantics were adopted.

## Result

The durable publication protocol needs two distinct linearization claims:

1. **semantic durability linearizes at verified immutable checkpoint creation**;
2. **mutable latest-alias promotion linearizes separately at expected-old/CAS pointer update**.

A receipt is not either linearization point. It is an observation record written after checkpoint verification and pointer postread. Separating these facts prevents two common false claims: “the result was lost because pointer promotion failed” and “this checkpoint is still current because its CAS once succeeded”.

Protocol:

`CREATE CHECKPOINT -> VERIFY -> CAS LATEST -> POSTREAD LATEST -> WRITE RECEIPT`

A concurrent writer may move `LATEST` at any boundary. The checkpoint remains durable regardless; the pointer may remain old, move to this checkpoint, or be moved later to another checkpoint. Therefore role-local reconstruction must discover immutable candidate heads independently of the mutable alias.

## Crash/publication matrix

| Stop/crash point | Durable state | What may be claimed | Required recovery |
| --- | --- | --- | --- |
| before checkpoint create | no new durable semantic artifact | nothing published | reconstruct parent frontier and retry |
| after create, before verify | immutable candidate exists but invocation has not verified it | do not claim verified checkpoint | next run exact-readback/digest verify candidate |
| after verify, before pointer CAS | verified semantic checkpoint exists; pointer unchanged | semantic result is durable; pointer not promoted | reconstruct checkpoint, then guarded pointer decision |
| after successful CAS, before postread | checkpoint durable; pointer was changed at CAS but may already be superseded | CAS success only, not “currently latest” | postread/reconstruct current pointer |
| after failed CAS | checkpoint durable; intervening pointer preserved | checkpoint valid, pointer reconciliation pending | clean reconstruct newer pointer/head; never stale-overwrite |
| after postread, before receipt | checkpoint and observed pointer outcome known | exact postread observation only | next invocation can regenerate receipt/evidence if needed |
| after receipt | checkpoint durable; receipt records observed outcome | receipt is historical observation, not eternal pointer truth | normal reconstruction on next run |

## Important concurrency refinement

Even a **successful** CAS is not sufficient to state that this checkpoint is the current `LATEST` at receipt time. Another writer can legitimately advance the pointer between CAS and postread. The receipt must therefore record at least:

- checkpoint path/digest;
- CAS outcome (`success`, `failure`, `already_current`, etc.);
- exact pointer value observed by postread;
- pointer observation timestamp/version when available.

If CAS succeeded but postread sees another checkpoint, record `promoted_then_superseded` (or equivalent factual fields), not a false current-latest claim.

Conversely, CAS failure is not semantic-result failure. The verified immutable checkpoint remains part of the role-local evidence set and is recoverable during next clean reconstruction.

## Replay/idempotency contract

Recovery should use an abstract `ENSURE_CHECKPOINT(path,digest)` rather than blindly repeating create:

- absent path => create then verify;
- existing exact same path+digest => treat as idempotent durable success and reverify;
- existing different digest => hard contradiction; never overwrite immutable checkpoint.

For pointer promotion on replay:

- pointer already equals the checkpoint => `already_current`;
- pointer still equals the invocation's preread expected token => CAS may promote;
- pointer is a different/newer value => fail closed and reconstruct; do not reset it to the old checkpoint.

A replay receipt must be based on its own fresh postread. It may refer to the same checkpoint without duplicating semantic work.

## Finite interleaving model

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2214JST_phase1_publication_crash_properties.py`
Git blob: `d1961595b4c7d48c3214d6247ae253729b7e00b3`

The model covers the fixed own publication sequence `create, verify, cas, postread, receipt`, inserts one concurrent pointer advance at every possible boundary (plus no concurrent writer), and crashes after every prefix. **48 publication/crash interleavings** are then recovered by a fresh invocation.

Checked properties:
- an already-created exact checkpoint survives and is reverified on recovery;
- a pointer already advanced by the concurrent writer is never overwritten during recovery;
- stale expected-pointer CAS therefore cannot lose the concurrent update;
- recovered receipt exists only after reverify/postread and truthfully matches the recovered pointer observation;
- checkpoint durability is independent of pointer-promotion success.

No property violation occurred in the finite model. This is a model of the contract, not proof of GitHub/etcd/Git internals.

The public Git `update-ref` contract supports the expected-old/CAS part: a ref update with an old object succeeds only if the current value matches, and multi-ref transactional update aborts when required locks/matches cannot be obtained. Source: https://git-scm.com/docs/git-update-ref

Temporal's durable-history/replay design supplies the complementary pattern: durable history remains the recovery basis even when a worker process disappears. Source: https://go.temporal.io/platform-hub/ai-engineering/ai-reference-architecture

## Revised publication proof obligations

**P1 checkpoint linearization.** A semantic result becomes durable only after immutable checkpoint exact readback/digest verification.

**P2 alias independence.** Failure to update mutable `LATEST` does not invalidate a verified checkpoint.

**P3 stale-CAS preservation.** If another writer changes the pointer after preread, this invocation cannot overwrite that value using the stale token.

**P4 postread truth.** Receipt may claim only the pointer value actually observed after the CAS attempt; CAS outcome and current pointer are distinct facts.

**P5 immutable replay.** Existing same-digest checkpoint is reusable; existing different-digest content at the same immutable path is a contradiction.

**P6 receipt-last.** No terminal receipt can be written before checkpoint verification and pointer-outcome postread.

**P7 replay non-duplication.** Recovery can continue publication from durable evidence without re-executing the semantic parent action merely because pointer/receipt stages were interrupted.

## Exact next Phase-1 action

Strengthen latest-state reconstruction from the earlier flat three-head property check to a **causal checkpoint-DAG model** with stale pointer, missing predecessor, incomparable disjoint heads, overlapping conflicting heads, and policy migration. Verify that discovery/merge is permutation-invariant and that no wall-clock order can convert an unresolved causal conflict into a resolved state.

Preserve `2026-08-28T1807JST_budget_conditioned_joint_value.md` as base restoration metadata only while Phase 1 remains active.

Termination for this leaf: durable publication crash/recovery contract completed; Phase-1 parent remains open with the causal-DAG reconstruction leaf above.
