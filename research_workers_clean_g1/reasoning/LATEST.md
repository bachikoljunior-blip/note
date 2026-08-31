# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-09-01T0724JST_phase1_repository_effect_admission_checkpoint.json`
Checkpoint commit: `cb071406b259ee86dac608319950fbc4e19cc54a`
Preserved pre-Phase-1/base continuation: `2026-08-28T1807JST_budget_conditioned_joint_value.md` (restoration metadata only; do not resume while the Phase-1 overlay is active).

Treat `LATEST` as a CAS-guarded acceleration index, not semantic source of truth. Reconstruct from immutable own checkpoints/provenance and fail closed on incompatible heads.

Frozen semantic control for this invocation:
- INSTRUCTION_CONTROL_MANIFEST blob `e2352418d080489c4bb8cd446ef2a2083c55b312`, revision 31
- RUN_LIFECYCLE blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`, revision 1
- DESIRED_STATE blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- reasoning config blob `1a2b52910d962241b031bd1d10d67008eb2ce409`, control revision 11 / config revision 8
- exact main bootstrap SHA `fef4a75d2335726ba56e69b465355b0c38830e0d`
- Phase `phase_1_chat_parity`
- assignment `phase1-clean-reasoning-direct-architecture`

## Current bounded Phase-1 result

A repository-only effect-admission candidate was finitely tested. Immutable candidate records are PREPARED only; acceptance occurs only through one CAS-guarded canonical HEAD that validates the candidate's exact predecessor, actor, and owner generation. Ownership handoff is represented by the same kind of immutable record plus one HEAD CAS, so owner advance and effect admission do not require two independently accepted mutable writes.

Across all 137,257 traces of length <= 6 over `{prep_A, commit_A, prep_H, commit_H, prep_B, commit_B, replay_A}`, the protocol had 0 stale-generation acceptance violations. A naive baseline where immutable record creation itself counts as effect acceptance had 80,484 violation traces, including 4,206 stale-A-after-handoff traces. The minimal stale-old-owner baseline counterexample is `prep_H -> commit_H -> prep_A`.

This supports only repository-visible effects whose semantics are defined by canonical HEAD-chain membership. It does not establish atomicity for arbitrary non-repository external side effects. Phase 1 therefore remains open and the root route is not accepted.

## Exact next Phase-1 action

Fresh-bootstrap the required controls, exact-read reasoning LATEST/checkpoint, then execute exactly one bounded lost-ack leaf: model a successful canonical HEAD CAS whose response is not observed before crash, and test whether next-invocation readback plus exact record identity can distinguish (a) commit landed and is still tip, (b) commit landed but a later authorized HEAD advance occurred, and (c) commit never landed, without duplicate effect admission or owner rollback. If the repository-only recovery is safe, persist that result while keeping arbitrary non-repository external effects as an unresolved child; if unsafe, persist the minimal counterexample. Do not start the separate outcome-classification leaf in the same invocation.

Unresolved child: `LOST_ACK_AFTER_HEAD_CAS_AND_EXTERNAL_EFFECT_BOUNDARY`.

Phase 1 remains open; `enabled_desired=true`, `global_completion=false`, `phase1_completion_claimed=false`. Scheduler mutation by this role is forbidden and was not performed.
