# Phase 1 follow-up — causal latest-state DAG acceptance

Status: role-local Phase-1 continuation under frozen semantic tuple `4632516483a5fb873c0ebc4b1709cb8505a9271a` / control rev 16 / reasoning config rev 6. This follows the deterministic architecture, handoff crash model, and durable publication crash model. No post-freeze repository semantics were adopted.

## Result

Latest-state reconstruction must be **causal-head based**, not timestamp-max based and not pointer-max based.

The minimal semantic object is a checkpoint DAG whose edges name verified predecessor checkpoints. Repository chronology and `LATEST` help discover candidates; neither decides a conflict. Reconstruction first removes/quarantines provenance-invalid nodes, computes maximal causally valid heads, and then either:

- returns the unique valid head;
- deterministically joins multiple compatible incomparable heads; or
- returns an explicit ambiguity/invalid-provenance witness.

A wall-clock ordering permutation is intentionally not an input to the semantic reducer. This prevents a later timestamp from silently converting a genuine concurrent conflict into a winner.

## Causal reconstruction contract

For checkpoint node

`N = (id, parent, policy_semantics, state_delta, digest, provenance)`

a node is causally valid only if its predecessor chain reaches a verified root/current baseline using available allowed evidence. A missing predecessor means the candidate cannot contribute semantic state until repaired.

After validity filtering:
1. compute maximal nodes under ancestor relation;
2. if there are no heads, return baseline/empty resolved state;
3. if one head exists, materialize its verified predecessor chain;
4. with multiple heads, require policy-semantic compatibility or explicit migration proof;
5. materialize each head relative to its shared history;
6. if the same resulting key has different values across incomparable heads, return `AMBIGUOUS_OVERLAP`;
7. otherwise join equal/disjoint state in stable checkpoint-id order.

`LATEST` is a hint only:
- a pointer to an ancestor is stale but does not change the resolved semantic state;
- a pointer to one of several incomparable heads does not suppress the others;
- a pointer to a node whose predecessor chain is invalid yields `INVALID_POINTER_PROVENANCE`, not adoption by recency.

## Finite causal-DAG model

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2216JST_phase1_causal_dag_properties.py`
Git blob: `e0a69a8a4a9996a9739b4fd4ded5d8eed109e2fe`

The model enumerates three candidate checkpoints `n1,n2,n3` over one root. Each node may parent a valid earlier node/root or a missing predecessor; each may write nothing or one of four key/value updates; each uses policy semantics 1 or 2. It checks both strict policy compatibility and an abstract “migration proof supplied” mode.

Enumerated:
- **24,000 causal DAG/state/policy cases**;
- all **6 permutations** of timestamp/presentation order for every case, verifying the result is unchanged;
- **120,000 valid-pointer semantic-equivalence comparisons**, verifying that a valid pointer hint never changes the semantic reducer's result;
- missing-pointer targets always produce `INVALID_POINTER_PROVENANCE`.

No checked invariant failed.

Important model limitation: the boolean migration flag stands for a *previously verified semantic equivalence/migration proof*. A real implementation must not use a blanket “migration allowed” switch. It must bind the proof to the exact old/new policy revisions and affected state/action semantics.

## Strengthened reconstruction invariants

**R6 causal maximality.** Only nodes with valid predecessor chains can be semantic heads; heads are maximal under the ancestor relation, not maximal timestamps.

**R7 pointer semantic irrelevance.** For any pointer that references a causally valid node/root, changing the pointer hint alone does not change the semantic reconstruction result from the same evidence set.

**R8 invalid-pointer fail-closed.** If `LATEST` names a node with unverifiable ancestry, reconstruction reports invalid provenance rather than trusting the pointer.

**R9 timestamp non-authority.** Any permutation of presentation/wall-clock order over the same checkpoint DAG leaves reconstruction unchanged.

**R10 branch-conflict visibility.** Incomparable heads whose materialized states disagree on a key cannot be collapsed by timestamp, pointer choice, or stable lexical ordering; an explicit resolver is required.

**R11 migration specificity.** Policy-mismatched heads may be joined only when an authorized migration/equivalence proof covers the exact semantics needed for reconstruction and subsequent eligibility decisions.

## Provenance-negative handling

A malformed/orphan role-local file that is not referenced by `LATEST`, a receipt, or a validated checkpoint chain should be quarantined as non-source-qualified evidence rather than poisoning every reconstruction forever. In contrast, if the mutable pointer explicitly names such an orphan, the pointer itself is invalid and must be repaired through a later guarded promotion after a valid state is reconstructed.

This distinction prevents two opposite errors: trusting a corrupted latest pointer, and allowing irrelevant junk files to make all future state unrecoverable.

## Current architecture status

The original Phase-1 reasoning assignment now has concrete contracts and finite checks for:
- frozen-control semantics;
- stale-pointer/latest-state reconstruction;
- non-conflicting maximal action selection;
- direct-solution-first/decompose-only-on-blocker;
- transversal generation after branch overrun;
- immutable checkpoint + guarded pointer publication;
- precise generation-fenced exclusive handoff;
- handoff crash/replay idempotency;
- publication crash/recovery;
- causal DAG reconstruction independent of pointer/timestamp ordering.

Global cross-role exclusivity is still intentionally unclaimed because the clean role has no authorized shared ownership surface.

## Exact next Phase-1 action

Audit and model **repeated-run task-selection liveness**. A deterministic greedy maximal independent set is conflict-safe and maximal per run, but a repeatedly reintroduced high-priority action can starve a lower-priority eligible action forever. Define a durable, deterministic fairness mechanism that preserves conflict safety without using wall-clock race order, and prove the conditions under which every continuously eligible non-conflicting action eventually runs. Also define the fail-closed behavior when fairness metadata is stale or missing.

Keep `2026-08-28T1807JST_budget_conditioned_joint_value.md` as base restoration metadata only while Phase 1 remains active.

Termination for this leaf: causal latest-state reconstruction contract completed; Phase-1 parent remains open with repeated-run selection liveness above.
