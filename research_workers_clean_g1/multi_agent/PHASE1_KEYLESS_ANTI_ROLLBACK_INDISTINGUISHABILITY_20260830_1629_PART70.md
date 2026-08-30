# Phase-1 multi_agent Part 70 — keyless anti-rollback indistinguishability

## Frozen authority
- DESIRED_STATE blob: `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26.
- multi_agent config blob: `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8.
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`.
- Transport: manifest exact-blob authority. Presemantic witness was persisted and exact-read back before the first own-state read.

## Bounded leaf
Test the exact Part69 unresolved child: whether a stateless scheduled-Chat worker can detect a *complete rollback of its entire permitted repository authority domain* using only zero-cost, zero-finite-quota, non-secret state inside that same rollback domain.

The test is intentionally narrow. It does **not** claim that Git repositories always lose old objects after a rewind, nor that protected branch/ruleset configurations cannot prevent rewinds. It asks whether a worker that is allowed to observe only the current rollback-domain state can distinguish two histories when the adversarial restore makes those observations exactly equal.

## Paired-history fixture
Let `S3` be the complete permitted durable repository state at generation 3. For each candidate mechanism, compare:

- `H0`: system reaches `S3` and never advances.
- `H1`: system reaches `S3`, advances to generation 4 (possibly issuing an irreversible authorization/effect), then the entire permitted rollback domain is force-rewound/restored so the next invocation observes exactly `S3` again.

At the next invocation the worker has no protected secret, manual configuration, hosted coordinator, paid/trial/monthly credit, or durable state outside the rollback domain.

Candidates tested:
1. current ref + commit ancestry/current-tip monotonicity;
2. a compact generation-floor record in a different repository path but the same rollback domain;
3. repository-resident signed metadata plus repository-resident trust/key state;
4. fail-closed logic over the union of all same-domain records.

Eight paired traces (4 candidates × H0/H1) were evaluated by observational equality.

## Result
For all four candidates, the post-restore observation supplied to the next stateless invocation is identical in `H0` and `H1` by construction.

| Candidate | Distinguishes H0/H1 after complete same-domain restore? | Consequence |
|---|---:|---|
| current ref / ancestry | No | A remembered later commit SHA would distinguish, but retaining that SHA outside the restored domain is exactly the missing external witness. |
| separate floor path | No | Restoring the whole repository snapshot restores the floor with it. |
| repo-resident signature/key state | No | Authenticity of the restored snapshot does not establish freshness when trusted key state rolls back with the snapshot. |
| fail-closed over all same-domain records | No | It may reject both histories, but cannot reject only H1 while accepting H0 from identical observations. |

This is an information-boundary result rather than a GitHub implementation claim: with identical observations and no external memory, any deterministic algorithm returns the same decision in both histories; any randomized algorithm has the same decision distribution. Therefore it cannot simultaneously (a) accept generation 3 in the never-advanced history for availability and (b) reject generation 3 only in the advanced-then-rolled-back history for irreversible anti-rollback safety.

The only ways out change an assumption: keep a monotonic witness outside the rollback domain; prevent the rollback with separately administered authority; retain a protected secret/monotonic hardware state; or redesign effect semantics so replay of the restored generation is harmless and anti-rollback detection is unnecessary. The first three remain disallowed/unresolved for current Phase-1 acceptance because they introduce external/protected/manual authority or a dependency not available to the worker.

## Observation vs inference
**Observation from the bounded fixture:** all 4 mechanisms have observation-equivalent H0/H1 pairs under complete same-domain restore; 0/4 distinguish the histories. The fail-closed candidate preserves safety only by also blocking the legitimate H0 case.

**Inference limited to tested scope:** no mechanism whose entire durable evidence and trust state is restored to the same snapshot can prove that a later generation once existed. This does not rule out a repository configuration that makes such a restore impossible, a witness outside the rollback domain, or a different effect algebra that makes stale replay benign.

## Phase-1 assessment
- Incremental monetary cost: **0**.
- Finite monthly/trial/paid quota dependency added: **none**.
- Richer-mode/protected/manual execution dependency in the test: **none**.
- Accepted external hosted coordination: **none**.
- Result type: **exact unresolved blocker narrowed to the complete same-domain rollback threat model**, not completion.
- Part69 scoped positive remains unchanged: repository CAS issuance is still valid only under its explicit no-authority-rollback assumption.

## Exact continuation
Execute exactly one bounded non-conflicting leaf on **rollback-tolerant effect semantics that may remove the need for anti-rollback detection**. Compare at least: idempotent set-insert keyed by stable effect ID, monotone max-generation register, commutative/monotone merge, and destructive overwrite/non-commutative effect. Use paired `g3 -> g4 -> authority rollback -> stale g3 replay` traces and classify when stale replay is provably dominated/harmless versus when an external monotonic witness or sink-side generation fence remains necessary. Preserve the complete-rollback impossibility result; do not generalize a positive from monotone effects to arbitrary external sinks.
