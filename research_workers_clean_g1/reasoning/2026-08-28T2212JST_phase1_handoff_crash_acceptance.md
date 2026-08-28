# Phase 1 follow-up — exclusive handoff crash/replay acceptance

Status: role-local Phase-1 continuation under frozen semantic tuple `4632516483a5fb873c0ebc4b1709cb8505a9271a` / control rev 16 / reasoning config rev 6. This follows `2026-08-28T2207JST_phase1_direct_architecture.md`. No post-freeze repository semantics were adopted.

## Result

The exclusive-handoff protocol is safest when **authorization and local progress status are separated**. The authoritative right to act is the generation-fenced ownership record; a sender's local `ACTIVE/HANDED_OFF` flag is only a replayable cache. This matters at the hardest crash point: ownership may have committed to the target while the source crashes before recording that it observed the transfer. In that state the source may still locally look active, but a correctly fenced protected resource rejects all source operations carrying the old generation.

The transfer object is:

`Owner = (task_key, action_key, owner_id, generation, handoff_id, checkpoint_digest)`

and the transfer commit remains exactly one compare-and-swap:

`Owner(source,g,...) -> Owner(target,g+1,handoff_id,...)`

A duplicate acceptance is considered **idempotent success** only if the current durable owner record already equals the exact target / generation / handoff identity expected from the original transfer. A different handoff id, target, checkpoint digest, or generation is not a duplicate success; it is a conflicting/stale request and must reconstruct current ownership before doing anything else.

## Crash/replay state machine

Persisted state:
- immutable offer `H`;
- owner record and generation;
- optional durable source-local observation status;
- protected-resource fencing generation.

Events:
1. `OFFER`: persist immutable `H1`; ownership remains `(source,g)`.
2. `ACCEPT`: if `H1` exists and owner is exactly `(source,g)`, CAS to `(target,g+1,H1)`.
3. `DUPLICATE_ACCEPT`: if durable owner is already exactly `(target,g+1,H1)`, return idempotent success without incrementing generation again.
4. `OBSERVE`: source reads durable owner and may persist local `HANDED_OFF` only if exact target/generation/handoff match.
5. `SOURCE_EFFECT`: accepted only when source is the durable owner and presents current generation.
6. `TARGET_EFFECT`: accepted only when target is durable owner and presents current generation.
7. `CRASH/REPLAY`: volatile process state disappears; durable offer/owner/fence survive and reconstruction resumes from them.
8. `STALE_ACK` or foreign handoff id: never changes ownership or local handed-off status.

## Crash-point matrix

| Crash point | Durable truth after crash | Safe replay action | Safety reason |
| --- | --- | --- | --- |
| before offer persistence | source still owns `g` | recreate/skip offer from reconstructed task state | no transfer object exists |
| after offer, before owner CAS | source still owns `g` | retry exact offer/accept | offer is advisory until CAS |
| during/after CAS with response lost | owner may already be target `g+1` | read owner; exact match => idempotent success | CAS + owner identity resolves uncertain response |
| after CAS, before source observation | target owns `g+1`, source local cache may say ACTIVE | source reconstructs owner; old-generation effects are fenced | authorization is owner record, not local flag |
| after source records HANDED_OFF | target owns `g+1` | replay observation idempotently | local status derives from durable owner |
| target crashes after transfer | target remains owner `g+1` | target reconstructs and continues exact action | ownership does not depend on process liveness |
| lease expires but external fence not checked | unsafe for external side effect | refuse exclusive action | lease alone cannot fence stale holder |

## Finite model check

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2212JST_phase1_handoff_crash_properties.py`
Git blob: `36c19ec79bcf22b23e4f3d5444f88eadb2e9c2b6`

The model exhaustively enumerated **299,593 event sequences** of length 0 through 6 over eight events: offer, correct accept, foreign accept, owner observation, stale acknowledgement, source effect, target effect, and crash.

Checked invariants:
- ownership generation never decreases;
- the transfer generation advances at most once;
- source local `HANDED_OFF` implies exact durable target ownership at generation 8 for handoff `H1`;
- after target ownership commits, a source effect at generation 7 is never newly accepted;
- foreign acceptance, stale acknowledgement, and crash cannot mutate durable ownership;
- replaying the same accept after a successful transfer is state-idempotent.

No invariant violation was found in the enumerated model. This is a finite protocol-model check, not proof that any particular distributed storage/resource implementation enforces the assumed CAS and fencing semantics.

Public support: Temporal training material explicitly recommends idempotent Activities because a failed/retried Activity can execute again, reinforcing the need to make replayed external effects conditional/idempotent rather than assuming exactly-once process execution. Source: https://learn.temporal.io/assets/files/temporal-102-with-java-replay2025-468b8109d5a9ce33b36c2910c48433d9.pdf

## Negative-path acceptance table

| Trigger | Detectable evidence | Required fail-closed response | Recovery evidence required |
| --- | --- | --- | --- |
| stale `LATEST` alias | source-qualified same-role checkpoint later than pointer target | ignore pointer as authority; reconstruct candidate heads | validated checkpoint provenance/chain and later CAS pointer repair |
| missing predecessor | checkpoint names predecessor unavailable/unverifiable in allowed state | `INVALID_PROVENANCE`; do not adopt as latest | predecessor restored or explicit independently verifiable root checkpoint contract |
| `exact_diff_on_overlap != ∅` | incomparable heads changed same key to different values | `AMBIGUOUS(overlap_diff)` | explicit resolver/migration/contradiction decision |
| policy/config mismatch | heads use semantics that can change eligibility/effects | `AMBIGUOUS(policy_mismatch)` | migration/equivalence proof under authorized control |
| pointer CAS failure | current blob/version differs from preread token | keep immutable checkpoint; do not overwrite pointer | clean-bootstrap reconstruction then fresh guarded promotion |
| duplicate handoff delivery | owner already exact `(target,g+1,handoff_id,digest)` | idempotent success; no second generation increment | exact owner tuple readback |
| stale/foreign acknowledgement | ack identity/generation differs from owner record | ignore ack; reconstruct owner | matching durable owner tuple |
| missing global ownership surface | no authorized shared CAS/fencing record | handoff is advisory only; do not claim exclusivity | authorized registry or equivalent transactional owner primitive |
| lease-only external lock | TTL/lease may expire without old client knowing | refuse external exclusive action unless resource validates generation | resource-side fencing/version validation |
| runtime/tool hard stop | parent task not semantically completed | durable checkpoint + exact continuation | next run reconstructs same frontier |

## Revised handoff proof obligations

**H4 uncertain-response resolution.** After an `ACCEPT` response is lost, reading the exact owner tuple distinguishes committed transfer from non-transfer without issuing a second semantic transfer.

**H5 duplicate-delivery idempotency.** Re-delivering an identical transfer cannot increment the ownership generation more than once.

**H6 acknowledgement non-authority.** A sender/recipient acknowledgement cannot establish ownership; only durable owner CAS does.

**H7 stale-local-status safety.** A source-local ACTIVE cache after transfer cannot authorize effects because the protected resource checks current generation/owner.

**H8 liveness separation.** A crashed target still owns the action until a separately authorized ownership transition occurs; liveness/lease policy must not silently rewrite semantic ownership without fencing.

## Exact next Phase-1 action

Model the **durable checkpoint publication crash matrix** across `checkpoint create -> verify -> pointer CAS -> postread -> receipt`, including an intervening concurrent pointer update and duplicate invocation replay. Prove that every crash point yields either (a) no published semantic checkpoint, or (b) a durable checkpoint discoverable by clean reconstruction, while never producing a false `LATEST`/receipt claim or overwriting a concurrent pointer.

Keep the pre-Phase-1 base continuation frozen at `2026-08-28T1807JST_budget_conditioned_joint_value.md`.

Termination for this leaf: handoff crash/replay safety and negative-path acceptance matrix completed; Phase-1 parent remains open with the durable-publication leaf above.
