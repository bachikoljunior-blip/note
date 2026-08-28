# Phase 1 reasoning architecture — deterministic state, selection, continuation, handoff

Status: role-local Phase-1 checkpoint for `phase1-clean-reasoning-direct-architecture`.

Frozen semantic tuple for this invocation:
- note main SHA: `4632516483a5fb873c0ebc4b1709cb8505a9271a`
- DESIRED_STATE control revision: `16`
- DESIRED_STATE blob: `e319840755761e8aaf5c979598dd15ad6aeb79e1`
- reasoning config revision: `6`
- reasoning config blob: `cc8b37410994561a016a72c467b25ff0582d6462`
- Phase: `phase_1_chat_parity`
- Root problem: `o-chat-parity-root-v2-active-pool`

Boundary: semantic inputs were restricted to this role's own clean state, the sanitized root/config, and public sources. No O/O-derived, peer-worker, downstream, legacy, shared-ledger, or other-role receipt semantics were used. `DESIRED_STATE.json` was never edited.

## Direct result

A deterministic Chat-capable worker can be organized as:

`FREEZE -> RECONSTRUCT -> CANONICALIZE -> SELECT-DISJOINT -> DIRECT-SOLVE -> (BLOCKER-DECOMPOSE | TRANSVERSAL) -> CHECKPOINT -> CAS-POINTER -> RECEIPT -> OPTIONAL EXCLUSIVE HANDOFF`

Every stage returns either a deterministic value or an explicit witness explaining why it cannot safely return one. No wall-clock "newest wins", stale mutable pointer, lease, or heuristic ranking is allowed to silently resolve a semantic conflict.

## Own-state reconstruction finding

The role-local mutable `LATEST.md` observed at the frozen view still pointed to `2026-08-28T1435JST.md`, while the same role's source-qualified repository chronology contained a later immutable checkpoint `2026-08-28T1807JST_budget_conditioned_joint_value.md`. This is a concrete same-role stale-pointer case. Therefore `LATEST` must be treated as an acceleration index, not the semantic source of truth. The architecture below repairs that class of failure by validating role-local chronology and predecessor evidence before using a mutable pointer as "latest".

The preserved pre-Phase-1/base continuation is the frontier in `2026-08-28T1807JST_budget_conditioned_joint_value.md`: fresh-seed, signal-independent paired optional-action audit with joint terminal gain/cost modeling. Under the Phase-1 overlay it is restoration metadata only and is not resumed here.

## Existing-solution audit

### Git compare-and-swap refs
Git `update-ref <ref> <new-oid> <old-oid>` updates a ref only after verifying the current ref still equals the expected old object. Its transactional stdin mode locks all involved refs and aborts if a required lock/match fails. Pattern: immutable objects first, expected-old guarded pointer promotion second.
Source: https://git-scm.com/docs/git-update-ref

### Temporal deterministic replay
Temporal's current agent architecture separates deterministic Workflow orchestration from non-deterministic I/O Activities because Workflow code is replayed from recorded history after failure. Pattern: durable immutable history is authoritative, replay logic deterministic, side effects separately recorded.
Source: https://go.temporal.io/platform-hub/ai-engineering/ai-reference-architecture

### etcd revisions, transactions, and fencing
etcd exposes a cluster-wide monotonically increasing revision and atomic compare/then/else transactions. Its documentation also warns that lease-based locks alone cannot protect external resources after lease expiry; version validation/fencing is required for correctness outside etcd.
Sources:
- https://etcd.io/docs/v3.6/learning/api/
- https://etcd.io/docs/v3.6/learning/why/

### Serializable conflict handling
PostgreSQL Serializable isolation fails a transaction when concurrent reads/writes would yield a result inconsistent with every serial execution. Architectural analogue: fail closed on unresolved action/state conflict and retry/reconstruct rather than selecting a convenient winner.
Source: https://www.postgresql.org/docs/18/sql-set-transaction.html

## 1. Frozen semantic view

Define:
`F = (main_sha, control_revision, config_revision, config_blob)`

Bootstrap:
1. obtain `main_sha` only from a clean ref-object lookup;
2. read sanitized root control and this role config at exactly that SHA;
3. repeat the SHA-only lookup before first own-state/public semantic read;
4. if semantic control/config revision changed, restart bootstrap;
5. at first substantive semantic read, freeze `F`.

**F1 one semantic configuration.** All conclusions/checkpoints in one invocation cite exactly one `F`.

**F2 post-freeze drift is not silently adopted.** Later repository-head movement can be used only as mechanical CAS/readback evidence for authorized writes, not to reinterpret the frozen semantic result.

## 2. Deterministic latest-state reconstruction

Immutable checkpoint:
`C = (id, predecessor_ids, policy_rev, materialized_state_digest, write_set, frontier, continuation, provenance)`

Algorithm `RECONSTRUCT(F)`:
1. read role-local `LATEST`/`STATE` first as hints;
2. discover source-qualified role-local checkpoints in repository chronology and minimum predecessor chains needed to explain candidate heads;
3. reject malformed provenance, predecessor, digest, role, or frozen-control tuples;
4. construct checkpoint DAG and compute maximal heads under ancestor relation;
5. for incomparable heads, find least common verified predecessor and compare only effects since it;
6. define `overlap = write_set(H1) ∩ write_set(H2)`;
7. incompatible policy/config semantics without migration proof => `AMBIGUOUS(policy_mismatch, witness)`;
8. `exact_diff_on_overlap(H1,H2) != ∅` => `AMBIGUOUS(overlap_diff, witness)`;
9. equal overlap but unproven idempotent/commutative effects => `AMBIGUOUS(noncommutative_effect, witness)`;
10. otherwise deterministically join disjoint/equal compatible heads in stable checkpoint-id order and return `RESOLVED(state, provenance)`.

Repository chronology discovers candidates; it does not overwrite causal/semantic conflicts.

Proof obligations:
- **R1 Sound provenance:** every returned key traces to validated frozen-view evidence.
- **R2 Determinism:** same frozen role-local evidence set => same result independent of enumeration order.
- **R3 Conflict visibility:** differing overlapping writes cannot yield `RESOLVED`.
- **R4 Policy safety:** policy mismatch blocks merge absent explicit migration/equivalence proof.
- **R5 Pointer non-authority:** stale `LATEST` cannot hide a later valid descendant/head.

Negative witnesses:
- same predecessor, `H1: task=T,status=blocked`, `H2: task=T,status=complete` => overlap ambiguity;
- equal state bytes but policy revisions changing eligibility semantics => policy ambiguity.

## 3. Non-conflicting task/action selection

Canonical action:
`A = (role, job_id, branch, task_key, action_key, read_scope, write_scope, resources, capability, status, preconditions, effect_contract, priority_key, provenance)`

Eligibility requires role/capability/phase match, ready status, and all preconditions true.

Symmetric `conflict(a,b)` is true for:
1. same `action_key` with different canonical effect;
2. write/write overlap without proof effects are identical or commute;
3. write/read overlap capable of invalidating a precondition/result;
4. exclusive/capacity-1 resource overlap;
5. same ownership/handoff record and generation;
6. same semantic task branch with mutually exclusive effect contracts.

Build the undirected conflict graph over eligible actions. Sort by immutable total `priority_key`; greedily accept an action iff it has no conflict with an already accepted action. This is a deterministic maximal independent set.

Proof obligations:
- **S1 Pairwise disjointness:** insertion rule forbids conflict edges among selected actions.
- **S2 Maximality:** every unselected eligible action conflicted with an earlier selected action that remains selected.
- **S3 Determinism:** canonical records + symmetric conflict + total immutable order imply one selected set.
- **S4 Identity contradiction:** reused `action_key` with non-identical effects is a witness, not a tie.

Scope limit: these prove role-local selection safety. Global cross-role disjointness requires an authorized shared ownership/claim surface and cannot be inferred from unseen peer state.

## 4. Direct-solution-first reasoning

For selected task `t`, define deterministic directly-applicable constructive actions `Direct(t)`.

State machine:
- `START -> DIRECT_SOLVED(result) -> COMPLETE`
- `START -> DIRECT_BLOCKED(witnesses) -> MINIMAL_BLOCKERS`
- `START -> DIRECT_HARDSTOP(frontier) -> CHECKPOINT`
- `MINIMAL_BLOCKERS -> DECOMPOSE`
- any hard runtime/tool boundary -> `CHECKPOINT`, never parent completion.

A decomposition is legal only after a direct attempt yields explicit blocker witnesses. Timeout/runtime stop is not a blocker proof.

- **D1 Direct-first:** no decomposition transition from `START` without prior `DIRECT_BLOCKED`.
- **D2 No false completion:** checkpoint terminates an invocation, not the parent objective.
- **D3 Minimal decomposition:** decompose witnessed irreducible blockers only.

## 5. Transversal alternatives after branch overrun

Freeze branch/cost forecast `B` before expansion. If observed branches/projected cost exceed `B`, preserve current branches and build blocker hypergraph:
`H = {B_1, ..., B_n}`

Enumerate inclusion-minimal hitting sets in deterministic `(cardinality, lexical-key)` order.

- **T1 Coverage:** every emitted transversal intersects every blocker set.
- **T2 Minimality:** deleting any member destroys coverage.
- **T3 Epistemic restraint:** transversal status is candidate-generation evidence, not proof of solvability.

## 6. Durable continuation and pointer promotion

Checkpoint payload must include frozen tuple, predecessor, canonical state digest, selected action/status, completed evidence, unresolved blockers/dependencies, exact continuation, overlay restoration metadata, and actual offset-aware timestamps.

Write protocol:
1. construct checkpoint without repository mutation;
2. PREREAD target absence and pointer blob/version;
3. create immutable checkpoint;
4. VERIFY exact readback/digest;
5. CAS-update `LATEST` against preread pointer blob/version;
6. POSTREAD pointer and verify target;
7. write immutable own receipt **last**.

If pointer CAS fails, checkpoint remains valid. Do not overwrite intervening pointer; record `pointer_reconcile_required`.

- **C1 Crash durability:** after checkpoint verification, semantic result survives later pointer/receipt failure.
- **C2 No lost pointer update:** stale expected pointer token cannot overwrite concurrent pointer value.
- **C3 Receipt truthfulness:** receipt records observed outcomes only.

## 7. Precise exclusive-action handoff

Ownership:
`Owner = (task_key, action_key, owner_id, generation, checkpoint_digest)`

Offer:
`H = (handoff_id, task_key, action_key, source, target, expected_generation, checkpoint_digest, precondition_digest, exclusive_scope)`

Protocol:
1. source writes immutable offer while ownership remains `(source,g)`;
2. target validates checkpoint/preconditions;
3. sole transfer commit is CAS `Owner(source,g) -> Owner(target,g+1)`;
4. source marks local work handed off only after observing committed owner record;
5. every external side effect bears fencing generation and protected resource rejects generations lower than current.

Crash semantics:
- offer before CAS: source remains owner;
- CAS before source observes: target is owner; replay sees `g+1`;
- duplicate/stale acceptance expecting `g`: fails after first success;
- lease expiry alone is not sufficient external fencing.

- **H1 At-most-one owner per generation:** same expected `(source,g)` cannot commit two transfers.
- **H2 Stale-owner exclusion:** after `g+1`, generation `g` operations must be rejected.
- **H3 No handoff-by-message:** prose/inbox handoff without ownership CAS/fencing is advisory.

Current dependency: this clean role cannot read or mutate a cross-role/shared ownership registry. It can specify/test H1-H3 locally but cannot claim a global exclusive handoff was executed.

## 8. Executable Phase-1 property checks

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2207JST_phase1_architecture_properties.py`
SHA-256: `b43e350d04805dfd5455276f6050c6d72cf773a226f25adcd0c6d002924ddbd5`

Exhaustive checks:
- 33,867 undirected conflict graphs for `n <= 6`: selected set independent and maximal;
- 5,832 three-head state/policy cases: reconciliation invariant under all head permutations and fail-closed on policy/overlap disagreement;
- 1,940 blocker hypergraphs: deterministic inclusion-minimal transversal coverage;
- all valid direct-reasoning traces of length <= 4: no decomposition without prior direct blocker;
- 27 pointer-CAS cases: stale expected token never overwrites intervening value;
- 6 permutations of three racing ownership transfers from one generation: exactly one CAS succeeds and old generation is fenced.

These are finite property checks of the model, not proof of connector/server implementation correctness.

## 9. Consolidated proof obligations

1. **FROZEN_CONFIG**
2. **ROLE_BOUNDARY**
3. **PROVENANCE**
4. **LATEST_OR_AMBIGUOUS**
5. **EXACT_OVERLAP_DIFF**
6. **POLICY_COMPATIBILITY**
7. **TASK_DISJOINTNESS**
8. **SELECTION_MAXIMALITY**
9. **DIRECT_FIRST**
10. **TRANSVERSAL_TRIGGER**
11. **DURABLE_CHECKPOINT**
12. **POINTER_CAS**
13. **RECEIPT_AFTER_VERIFY**
14. **HANDOFF_CAS**
15. **FENCING**
16. **NO_FALSE_COMPLETION**

## 10. Concise Phase-1 handoff summary

Use immutable role-local checkpoints/receipts as source of truth; treat `LATEST` only as a CAS-guarded alias. Reconstruct causal heads and fail closed on `exact_diff_on_overlap` or `policy_mismatch`. Select ready actions as a deterministic greedy maximal independent set under explicit read/write/resource/handoff conflicts. Attempt direct construction before blocker decomposition; on branch overrun emit minimal blocker transversals. Persist checkpoint -> verify -> CAS pointer -> postread -> receipt. Transfer an exclusive action only by generation-CAS ownership plus fencing; prose handoff alone is non-exclusive. With clean role isolation, global cross-role disjointness/handoff execution remains an authorized-controller obligation.

No cross-role inbox write is attempted because the frozen role config authorizes only this role's state/output and own receipt namespace.

## Unresolved dependencies and next Phase-1 frontier

The generic architecture is specified and finitely property-checked. Remaining work is Phase-1 continuation, not base research restoration.

Unresolved dependency:
- `XROLE_OWNERSHIP_SURFACE`: global cross-role exclusivity cannot be proved/executed from clean role-local semantic inputs. Needed capability: an authorized ownership registry or equivalent CAS/fencing surface. Until present, cross-role handoff stays advisory.

Exact next Phase-1 action:
1. model handoff crash points (`offer`, `CAS commit`, `ack observed`, `side-effect fence`) and verify replay/idempotency under duplicate delivery and stale acknowledgements;
2. add a negative-path acceptance table for stale `LATEST`, missing predecessor, `exact_diff_on_overlap`, `policy_mismatch`, pointer CAS failure, and absent global ownership capability;
3. keep pre-Phase-1 base continuation frozen at `2026-08-28T1807JST_budget_conditioned_joint_value.md` until Phase-1 overlay ends or repository control explicitly restores it.

Termination for this checkpoint: direct architecture plus first finite property audit completed. The recurring parent objective is not complete; frontier remains non-empty.
