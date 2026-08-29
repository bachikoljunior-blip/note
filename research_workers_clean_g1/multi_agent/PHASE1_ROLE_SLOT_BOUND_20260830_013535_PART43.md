# Phase-1 multi_agent checkpoint — per-role slots and the finite-inflight boundary (Part 43)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_TICKET_RECOVERY_20260830_013535_PART42.md`

Part 42 made a finite `max_inflight` contract a prerequisite for a finite wide-operation starvation bound. This leaf tests whether such a bound can be derived repository-locally without putting every ordinary local admission through one global write.

Executable model: `research_workers_clean_g1/multi_agent/phase1_role_slot_bound_20260830_part43.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_role_slot_bound_20260830_part43.json`

The slot model has `192` scenario shapes / `768` strategy evaluations. The separate wide-starvation model has `160` scenario shapes / `640` evaluations. Counts are mechanism counts, not production probabilities.

## Result 1 — one current-blob slot can serialize overlapping invocations of the same role

The per-role slot candidate is one deterministic role-local authority record:

`FREE -> HELD(role_incarnation, slot_epoch, operation_id) -> FREE/RETIRED`

A same-role invocation must acquire the slot before creating an authoritative PREPARED operation. If another invocation has already changed the slot blob, the loser cannot acquire from its stale FREE SHA. A crash permits a later takeover only through a higher current slot epoch; the effect publication itself must validate the current `(role_incarnation, slot_epoch, operation_id)` rather than merely trusting that the slot was acquired earlier.

Without a role slot, the finite model admits concurrent duplicates in **128 scenarios**. A slot that serializes admission but is not revalidated at effect time still has **24 stale old-effect** cases after crash/takeover. The epoch-fenced slot reduces that to six cases across the full lattice, and every remaining case is a delete/recreate ABA where identity is not incarnation-sensitive.

In the explicit incarnation-sensitive strong slice (`96` scenarios), epoch-fenced role slots have **0 unsafe old effects**, while blocking 128 duplicate-overlap admission events and performing 24 takeover epoch transitions.

### Blob-SHA ABA caveat

A file path is not itself an incarnation ID. Git blob SHA is a content hash; if a deleted role-slot path is recreated with byte-identical content, a historical expected blob SHA can in principle reappear. The slot therefore carries a new incarnation identifier on recreation, so the bytes — and consequently the current blob identity — differ even when the logical role name is reused.

This is the same name-vs-incarnation rule established earlier for conflict domains/tickets.

## Result 2 — per-role slots can bound *simultaneous* admitted work, but only under a universal protocol invariant

If there are `N` canonical role slots and every authoritative operation must hold exactly one current role slot, with each role serializing its own local operation queue, then simultaneous admitted operations are bounded by `N`.

That is a real repository-level invariant; it does not require a global write for every local operation. But the proof depends on **universal adoption**: an operation that bypasses its role slot is outside the bound. The sanitized root currently identifies a finite intended role set, but role count alone is not proof that each physical invocation is one-at-a-time or that every effect path has adopted this slot protocol.

The current `multi_agent` CLEAN role also cannot inspect other roles' private state/config to verify slot adoption. So this leaf records the generic mechanism, but does not elevate the current repository to a proved full-pool `max_inflight=N` deployment.

## Result 3 — an instantaneous bound is not a starvation bound if replacements keep arriving

The wide-starvation model is the sharper negative result. Even if role slots cap instantaneous in-flight work, a role that finishes one local operation can acquire its slot again and create another. An adversarial sequence of replacements can therefore continue moving the branch before every wide ref update.

Across 160 finite scenarios, `role_slots_only` terminalizes 68 and leaves **92 starved/retry-exhausted**, exactly the same count as no admission control in this lattice. The role slots reduce simultaneous concurrency but do not stop replenishment.

This separates two proof obligations:

1. **finite occupancy:** at most `K` operations are already in flight when the wide request becomes authoritative;
2. **closed arrivals:** after that request, no new conflicting local operations join until the wide request completes/releases.

A finite starvation bound requires both.

## Result 4 — role slots plus the shared REQUESTED gate solve the finite model mechanically, but the current CLEAN boundary does not expose that shared gate

If the Part 41 REQUESTED ticket is added to role slots, new replacement rounds defer after the ticket while only the initial bounded holders drain. In the finite model this raises terminal cases from 68 to **112/160** and reduces retries; the remaining 48 fail only because retry budget is not larger than the initial bounded in-flight set.

The global-root baseline terminalizes all 160 scenarios, but incurs 2,440 global authority touches and therefore reintroduces the steady-state hotspot.

However, there is an important deployment boundary in the current repository control: this CLEAN role's allowed semantic inputs are its own role-local state, sanitized root/config, own sanitized feedback and public sources; its write destinations are its own role namespace and own receipts. Other-role slot state and a dynamically writable shared claim/ticket file are not currently admissible CLEAN semantic inputs/write destinations.

Therefore:

- **per-role slots** are a generic zero-global-write mechanism for same-role admission and an instantaneous bound if universally adopted;
- **shared ticket + slots** is a mechanically successful generic finite-starvation construction;
- but the shared-gate part is **not deployable by this role under the current CLEAN policy** and cannot be counted as current Phase-1 outcome parity merely because the finite model is safe.

This is not a request for a manual/protected handoff. It is an unresolved repository-control capability child: either a sanitized shared coordination surface must become explicitly admissible for all participating CLEAN roles without violating isolation, or a different mechanism must close arrivals without shared dynamic semantic state.

## Result 5 — branch serialization alone cannot communicate semantic priority

The branch ref itself serializes commits and detects stale wide proposals, but it does not tell a new local role invocation that a semantically equivalent or higher-priority wide request exists. CLEAN policy also forbids using unrelated commit messages/diffs as a semantic backchannel. Thus branch movement is a safety/version signal, not an admissible semantic admission queue.

That means the no-shared-state route still lacks the “closed arrivals” half of a finite fairness proof.

## Phase-1 zero-dependency / zero-quota assessment

Per-role incarnation/epoch slots are repository-local, zero incremental cost, and do not require hosted compute, finite monthly/trial/paid quota, richer mode, protected execution or manual user action. They are accepted as a **generic same-role admission mechanism** in the tested no-complete-rewind scope.

Full-pool finite-starvation parity remains unresolved because the currently tested construction also needs a dynamic shared REQUESTED gate that is outside this role's CLEAN semantic/write surface. Treating another worker's state, shared ledger, commit semantics, or downstream authority as that gate would violate current control and is not accepted.

Complete same-domain rewind, direct fixed-path consumer parity, and arbitrary external sink atomicity remain open as before.

## Exact continuation

Next Phase-1 leaf: **shared-gate alternatives that preserve CLEAN isolation**.

Audit only sanitized/public/mechanical constructions, without reading other worker state:

- branch/ref namespaces as write-only contention channels with no semantic cross-read;
- deterministic time/turn epochs as an admission schedule (required negative: time is not authority/fencing);
- static conflict-free role/effect ownership encoded in sanitized root, avoiding dynamic claims entirely;
- user-visible output idempotency keys whose duplicate suppression is enforced by a shared sink rather than worker semantic reads;
- repository path create-once claims where contenders need only success/conflict status, not another worker's payload;
- root/config-issued per-role capability partitions that guarantee nonoverlap by construction.

The target is to find a full-pool duplicate/conflict-prevention route where CLEAN workers never consume each other's semantic state, or to narrow the remaining boundary to exactly which material outcomes inherently require an admissible shared sink/claim authority.
