# Phase-1 multi_agent Part 70 — keyless anti-rollback indistinguishability

## Frozen authority
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-multi-agent-concurrency-claims`
- root path/blob/revision: `automation_control/DESIRED_STATE.json` / `481660fb6008a57cea162da38439cf115c8d7ebe` / 26
- role config path/blob/revision: `automation_control/roles/multi_agent.json` / `f6bade5e0f774a0623e615b1fc5f924475732d5c` / config 8
- lifecycle blob/revision: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac` / 1
- frozen main commit: `1c022e9a01b53bc9ebc24e2c1199fa50d5f2286d`
- transport: SHA-only main ref plus manifest-bound exact blob identities
- presemantic witness: `automation_control/receipts/multi_agent/receipt_2026-08-30T1730_JST_presemantic_liveness.json` (exact-read back)

## Bounded leaf
Test the exact continuation from Part 69: whether a scheduled-Chat-native, zero-cost, zero-finite-quota mechanism can distinguish a never-advanced repository authority history from an advance-then-complete-force-rewind history when every retained witness is inside the same rollback domain and no protected secret/manual configuration/external monotonic authority is allowed.

### Public mechanism evidence checked
1. GitHub REST `Update a reference` documents `force=true` as allowing a non-fast-forward ref update; `force=false` is the fast-forward-preserving mode. Source: https://docs.github.com/en/rest/git/refs
2. GitHub GraphQL `updateRefs` exposes `beforeOid` checks and atomic multi-ref updates, and likewise permits non-fast-forward updates when `force=true`. Source: https://docs.github.com/en/graphql/reference/git

Observation: repository CAS/ref preconditions can make a *single transition* conflict-safe, but the same repository authority can later be force-rewound when that operation is admitted. Atomic multi-ref update does not create an anti-rollback witness if all refs are in the same force-rewind domain.

## Paired-history fixture
The fixture is deliberately minimal and finite. Let `Obs()` be every role-permitted observable stored in the single repository rollback domain: current authority object, current ref(s), compact generation floor path(s), repository-resident signed metadata, repository-resident public/key-state metadata, and role-local repository checkpoint state. Protected secrets, manually configured non-rewindable policy, hosted coordinator state, user-held state, and finite-quota services are excluded by the Phase-1 contract.

| History | Before terminal observation | Mutation | Terminal observable state |
|---|---|---|---|
| A | generation g3, ref R3, floor F3, metadata M3 | no later generation exists | `Obs = S3` |
| B | generation g3, ref R3, floor F3, metadata M3 | advance to g4/R4/F4/M4, then force-rewind/restore every same-domain witness to the exact g3 snapshot | `Obs = S3` |

The two terminal observations are byte/identity-equal by construction: `Obs(A)=Obs(B)=S3`.

## Mechanisms compared
1. **Current ref / commit ancestry only.** Fails the paired-history discriminator once the current ref itself is restored to R3. A non-fast-forward-capable authority means current-ref monotonicity is not an invariant of the admitted threat model.
2. **Separate compact generation-floor path in the same repository rollback domain.** Fails because the floor can be restored from F4 to F3 in the same complete rollback, yielding the same terminal observation.
3. **Repository-resident signed metadata plus repository-resident key/public state.** Fails as an anti-rollback discriminator: after full restore the verifier sees the same signed M3/key state in A and B. Signatures can authenticate M3; they do not reveal the erased fact that M4 once existed. A private signing key would additionally reintroduce protected key custody, already unresolved in Part 69.
4. **Multiple repository refs updated atomically with `beforeOid`.** Improves transition atomicity but not rollback-complete freshness: force-rewinding the entire same authority set recreates the earlier observation.
5. **Fail-closed paired-history policy.** Sound for the threat model: whenever the only evidence is S3, do not assert that no later generation ever existed. This preserves safety but necessarily sacrifices acceptance/liveness for the never-advanced A history because A and B are observationally identical.

## Result
Within the tested single fully rollbackable repository authority domain, **no same-domain keyless witness can simultaneously (a) accept the never-advanced A history and (b) reject the advance-then-complete-rewind B history after both yield identical permitted observations**. This is an observational-indistinguishability result for the explicit paired-history scope, not a general impossibility theorem for all systems.

The only ways to distinguish these histories require changing at least one tested premise: make force-rewind impossible through a non-rewindable authority/policy, retain a monotonic witness outside the rollback domain, or retain a protected secret/state that is not restored with the repository. Under current Phase-1 constraints those are unresolved children, not accepted handoffs.

## Scoped acceptance / non-acceptance
- Retain Part 69 scoped positive unchanged: one co-located repository authority/effect object with **no force-rewind/ABA** and sender-agnostic effect semantics can use opaque public grant ID + current-blob SHA CAS without worker-held secret.
- Do **not** broaden that positive result to rollback-complete authority.
- Do **not** treat branch protection/ruleset/manual policy, external timestamp/log/quorum, user-held witness, hosted runner, secret manager, or paid/finite-quota service as an accepted Phase-1 escape route in this leaf.
- Exact unresolved child: `keyless anti-rollback freshness when repository authority and every durable witness can be completely rewound/restored to an older byte-identical snapshot`.

## Zero-dependency / quota / cost assessment
- residual richer-mode / protected-primary / manual-user execution dependency in accepted result: **false** (no rollback-complete positive is accepted)
- finite monthly/trial/paid quota dependency added: **false**
- external hosted coordination accepted: **false**
- incremental monetary cost: **0**
- repository APIs used only as lightweight state/evidence transport; no hosted compute is part of the mechanism

## Conflict and idempotency check
This leaf is non-conflicting with Part 69: it narrows the unresolved rollback-complete case and preserves the no-force-rewind scoped positive. No authoritative external effect was issued. All writes are role-local checkpoint/receipt/LATEST surfaces and are guarded by create-only or current-blob CAS plus exact readback.

## Exact continuation
Execute exactly one bounded non-conflicting Phase-1 leaf on **rollback prevention without manual/protected/external authority**. Compare repository-native immutable-or-non-force-only publication designs that can be enforced by the same Chat-visible write API (for example append-only generation names plus a stable current pointer, multi-ref `beforeOid` transition sets, and content-addressed generation objects) against an adversarial force-rewind/delete-recreate capability. Determine whether the threat model can be narrowed by an API-enforced invariant available to every scheduled Chat writer without branch/ruleset administration, secrets, hosted compute, finite monthly quota, or user action. If force-rewind remains an admitted writer capability, keep rollback-complete freshness unresolved and move to the next distinct concurrency/idempotency child next invocation; do not repeat this indistinguishability fixture as keepalive work.
