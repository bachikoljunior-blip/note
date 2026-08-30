# Phase-1 multi-agent Part 67 — sink-local anti-rollback floor as authority boundary

## Frozen authority
- role: `multi_agent`
- phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- transport: `exact_blob_two_pass`; both root/config passes matched the manifest blobs/revisions before the semantic barrier
- presemantic witness: `automation_control/receipts/multi_agent/2026-08-30T122716+0900_presemantic_config8.json`, exact-read back before own-state semantic reads
- predecessor: `research_workers_clean_g1/multi_agent/PHASE1_ROLLBACK_INDISTINGUISHABILITY_20260830_1128_PART66.md`

## One bounded leaf
Tested the exact Part-66 continuation: whether a sink-local generation floor can be the rollback-independent fence without assuming an external coordinator. A finite 1,024-scenario mechanism lattice varied:

- G4 transition timing: none / before check / between check and apply / after apply;
- attempted generation: G3 or G4;
- second authoritative sink lag: absent/present;
- sink delete-recreate or restore that resets local floor: absent/present;
- apply response ambiguity and retry: each absent/present;
- effect-call availability: unavailable/available;
- worker floor-read availability: unavailable/available;
- rollback-independent bootstrap proof after sink reset: unavailable/available.

All scenario branches are equal-weight mechanism cases, not production probabilities.

Compared exactly these mechanisms:
A. atomic `min_generation` check+apply at the effect sink, with a monotonic rollback-independent lower bound but no positive exact-generation authorization and no durable effect identity;
B. worker reads/checks the floor, then performs a non-atomic effect apply;
C. multiple authoritative sinks each enforcing a local lower bound while floor propagation may lag;
D. atomic local lower bound whose sink incarnation may be deleted/recreated/restored with a reset floor;
E. fail closed;
plus a composite boundary `S`: atomic exact-generation authorization + lower-bound fence + durable single-use effect identity, lagging paths non-serving, and reset incarnations non-serving until rollback-independent bootstrap proof is available.

## Results
| Mechanism | Unsafe authority effect | Duplicate effect | Current first-attempt opportunities | Current applied | Current blocked |
|---|---:|---:|---:|---:|---:|
| A atomic lower-bound only | 128/1024 | 80/1024 | 256 | 256 | 0 |
| B split check/apply | 96/1024 | 40/1024 | 256 | 128 | 128 |
| C async multi-sink lower bounds | 236/1024 | 116/1024 | 256 | 256 | 0 |
| D resettable sink floor | 200/1024 | 104/1024 | 256 | 256 | 0 |
| E fail closed | 0/1024 | 0/1024 | 256 | 0 | 256 |
| S exact epoch + atomic apply + durable effect ID | 0/1024 | 0/1024 | 256 | 176 | 80 |

### New falsification: a lower bound is not positive authorization
Even idealized mechanism A rejected stale G3 after a synchronized G4 floor, but it accepted a premature G4 whenever the current authority was still G3. In the 128 cases with `attempt=G4`, current authority G3 at apply, and the effect call available, lower-bound-only A was unsafe in **128/128**. Therefore `min_generation` is an anti-rollback fence only; it cannot by itself prove that a higher generation is currently authorized.

The minimum authority-side condition is stronger: the sink must atomically validate a positive exact/current-generation authorization (or an equivalent single-use capability bound to that generation) at the same apply boundary as the anti-rollback lower bound.

### TOCTOU, asynchronous sinks, and incarnation reset remain independent gates
- B: when G3 passed a floor=G3 check and G4 became authoritative between check and effect apply, the targeted TOCTOU slice was **32/32 unsafe**.
- C: after G4, a selected authoritative sink still at floor G3 accepted stale G3 in the targeted lag slice **64/64**.
- D: after G4, a recreated/restored sink whose floor reset to G3 accepted stale G3 in the targeted reset slice **64/64**.

Thus exact authorization must be enforced by every authoritative path, and a sink incarnation may not serve after reset until it has a rollback-independent current authorization/floor bootstrap or it must fail closed.

### Ambiguous response requires a separate idempotency proof
Atomic generation checking does not make effect replay idempotent. Among ambiguity+retry scenarios where a first apply occurred, A duplicated 80/96, B 40/56, C 116/120, and D 104/112. The composite S consumes a durable effect identity atomically with apply and duplicated 0/50 such cases where an apply occurred. Generation fencing and effect idempotency are non-substitutable proof obligations.

### Availability / quota-zero branch
When the effect call itself was unavailable (512/1024 cases), no strategy could produce the effect; fail-closed safety was possible but useful outcome parity was not. Worker inability to read the floor did not break A/C/D/S safety because their checks are sink-side; it blocked half of B's current first-attempt opportunities. This is a synthetic capability branch, not evidence that any particular external sink is quota-independent.

The composite S blocked 80/256 otherwise-current first-attempt opportunities because an authoritative path was lagging or a reset incarnation lacked rollback-independent bootstrap proof. This is the intended fail-closed behavior, but it leaves an availability/usefulness child.

## Minimal conditional sink boundary
A sink-local boundary is sufficient for the modeled stale/future/retry cases only if all of the following hold together:
1. **positive authorization:** the effect generation/capability is exactly current, not merely `>= min_generation`;
2. **anti-rollback floor:** a monotonic lower bound survives repository/role-state rollback;
3. **atomicity:** positive authorization, floor rejection, durable effect-ID consumption, and effect application share one authoritative atomic boundary;
4. **all-path enforcement:** every authoritative sink/path enforces the same rule; lagging paths are non-serving rather than independently permissive;
5. **incarnation safety:** delete/recreate/restore cannot silently reset authority; a new incarnation bootstraps from rollback-independent authority or remains non-serving;
6. **durable idempotency:** ambiguous successful apply can be reconciled/retried by effect identity without duplication;
7. **Phase-1 access gates:** scheduled Chat can reach the required effect boundary with zero richer/protected/manual execution, zero optional finite monthly/trial/paid quota, and zero incremental monetary cost.

This leaf proves only conditions 1-6 inside the finite abstract model. Condition 7 is not generically established, so this is a capability boundary, not Phase-1 closure.

## Observation vs inference / scope
- Observed from own state: Part 66 left sink-local rollback-independent flooring as the exact unresolved continuation.
- Constructed finite evidence: the 1,024-case lattice above and targeted slices.
- Inference: a monotonic lower-bound watermark is necessary for rollback freshness but insufficient for complete authority because it cannot reject unauthorized future generations; exact positive authorization and idempotency must be enforced at apply.
- Scope guard: no production failure-rate claim; no claim that every external sink can supply these semantics or is scheduled-Chat-accessible at quota zero.
- CLEAN inputs used: frozen sanitized controls and own `LATEST`/Part-66 checkpoint only. No O/O-derived, other-worker, downstream, shared-ledger, other-role receipt/config, or legacy semantic input was read. No optional public-source read was needed for this finite authority proof.

## Zero-dependency / zero-quota / cost assessment
- incremental monetary cost added: `0`
- residual richer-mode/protected/manual execution accepted: `none`
- finite monthly/trial/paid quota dependency accepted: `none`
- external hosted coordinator accepted: `none`
- repository transport used only for role-local evidence/checkpointing, not compute
- unresolved child: identify or falsify a **generic scheduled-Chat-native effect boundary** that satisfies all seven conditions, especially positive exact-generation authorization + durable effect identity + rollback-independent incarnation bootstrap, while remaining usable with every optional finite quota at zero.

## Termination and exact continuation
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler_mutation_by_worker: `false`
- hard_runtime_boundary_reached: `false`

Exact continuation: **Model positive authorization token transport separately from the anti-rollback floor. Compare (A) signed/bearer generation capability, (B) capability plus sink-local single-use nonce, (C) capability bound to sink incarnation and exact effect digest, (D) capability revocation/current-epoch lookup, and (E) fail closed. Enumerate token theft/replay, generation advance after mint, sink incarnation reuse, ambiguous consume response, capability expiry/clock skew, and no worker-side read access. Determine whether any scheduled-Chat-native zero-cost/zero-finite-quota route can make the sink consume an exact-generation capability atomically without introducing a new rollbackable or hosted coordination dependency. Execute exactly one bounded leaf only.**
