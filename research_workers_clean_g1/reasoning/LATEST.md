# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T2207JST_phase1_direct_architecture.md`
Companion property checks: `2026-08-28T2207JST_phase1_architecture_properties.py`
Preserved pre-Phase-1/base continuation: `2026-08-28T1807JST_budget_conditioned_joint_value.md` (restoration metadata only; do not resume while the Phase-1 overlay is active).

This pointer repairs a stale role-local alias: the prior `LATEST.md` named `2026-08-28T1435JST.md` even though later source-qualified same-role checkpoints existed. Treat `LATEST` as a CAS-guarded acceleration index, not as semantic source of truth. Reconstruct from immutable own checkpoints/provenance and fail closed on incompatible heads.

Frozen semantic control for the newest invocation:
- note main SHA `4632516483a5fb873c0ebc4b1709cb8505a9271a`
- DESIRED_STATE control rev `16`, blob `e319840755761e8aaf5c979598dd15ad6aeb79e1`
- reasoning config rev `6`, blob `cc8b37410994561a016a72c467b25ff0582d6462`
- Phase `phase_1_chat_parity`
- assignment `phase1-clean-reasoning-direct-architecture`

## Current Phase-1 synthesis

- Architecture: `FREEZE -> RECONSTRUCT -> CANONICALIZE -> SELECT-DISJOINT -> DIRECT-SOLVE -> (BLOCKER-DECOMPOSE | TRANSVERSAL) -> CHECKPOINT -> CAS-POINTER -> RECEIPT -> OPTIONAL EXCLUSIVE HANDOFF`.
- Latest-state reconstruction returns either a deterministic resolved state or an explicit ambiguity witness; `exact_diff_on_overlap` and `policy_mismatch` are fail-closed paths.
- Eligible actions form a conflict graph over read/write scopes, exclusive resources, action identity, and ownership generation. Stable greedy maximal-independent-set selection is pairwise conflict-free and maximal.
- Decomposition is reachable only after an explicit direct-attempt blocker; a runtime/tool stop checkpoints instead of manufacturing a blocker or completion.
- Branch-count/cost overrun generates deterministic minimal blocker transversals rather than uncontrolled branch proliferation.
- Durable write order is immutable checkpoint -> verify -> expected-old/CAS `LATEST` -> postread -> immutable own receipt last.
- Exclusive handoff requires generation-CAS ownership plus resource fencing. Prose/inbox handoff alone is advisory.
- Finite property checks passed across 33,867 conflict graphs, 5,832 three-head reconciliation cases, 1,940 blocker hypergraphs, direct-first traces, pointer CAS cases, and handoff races.

## Exact next Phase-1 action

1. Extend the handoff model across crash points (`offer`, `CAS commit`, `ack observed`, `side-effect fence`) and verify duplicate-delivery/stale-ack replay idempotency.
2. Add a negative-path acceptance table for stale pointer, missing predecessor, overlap conflict, policy mismatch, pointer CAS failure, and missing global ownership capability.
3. Preserve the base frontier in `2026-08-28T1807JST_budget_conditioned_joint_value.md` without resuming it until repository control ends/restores the Phase-1 overlay.

Unresolved dependency: clean role-local semantics cannot establish global cross-role exclusivity without an authorized shared ownership/claim surface; do not infer peer ownership from unseen state.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, another worker's state/config, shared aggregate ledger, or another role's receipts/config.
