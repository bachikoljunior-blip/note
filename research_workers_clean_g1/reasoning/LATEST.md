# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-30T1624JST_phase1_handoff_fence_order_checkpoint.json`
Checkpoint blob: `53497ef7c56a5db91428f0d34010ee25327cbdbb`
Preserved pre-Phase-1/base continuation: `2026-08-28T1807JST_budget_conditioned_joint_value.md` (restoration metadata only; do not resume while the Phase-1 overlay is active).

Treat `LATEST` as a CAS-guarded acceleration index, not semantic source of truth. Reconstruct from immutable own checkpoints/provenance and fail closed on incompatible heads.

Frozen semantic control for the newest invocation:
- INSTRUCTION_CONTROL_MANIFEST blob `26b08f75ed25273b05e43ce77e018675c635b37a`, revision 7
- RUN_LIFECYCLE blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- reasoning config blob `e5d15694c2f3964a0be9bb69cfad60ebf237f36d`, config revision 7
- Phase `phase_1_chat_parity`
- assignment `phase1-clean-reasoning-direct-architecture`

## Current bounded Phase-1 result

The prior handoff order `offer -> ownership CAS -> ack -> side-effect fence` is falsified by a crash immediately after ownership CAS: ownership is already at generation `g+1` while an external resource still admits generation `g`. In a finite model over all 5,461 traces of length <= 6 from `{offer, cas, ack, fence}`, that ordering produced 1,701 stale-owner safety violations.

A revised experimental order `offer -> monotone fence-prepare(g+1) -> ownership CAS(source,g -> target,g+1) -> ack` produced 0 such safety violations in the same finite trace set. All five crash-prefix replays converged to the same terminal state. Duplicate old-handoff replay and an H1 stale ack delivered after an H2 generation advance were no-ops when ack was bound to the exact current target/generation.

This is finite model evidence only. It does not establish connector/server atomicity, global cross-role ownership, or an actual external fence. Under current zero-dependency Phase-1 policy, the repaired handoff is **not accepted** because shared effect-admission/fencing remains an unavailable role-local capability.

## Exact next Phase-1 action

Design and finitely test a Chat-native repository-only effect-admission protocol in which every effect is immutable and carries owner generation, and acceptance can be validated without a protected shared fence or richer-mode executor. Falsify any design where owner advancement and effect publication are two independent mutable writes that admit a stale generation after a crash. Do not start the separate negative-path acceptance-table leaf in the same invocation.

Unresolved child: `XROLE_EFFECT_FENCE_WITHOUT_SHARED_PROTECTED_EXECUTOR`.

Phase 1 remains open; `enabled_desired=true`, `global_completion=false`, `phase1_completion_claimed=false`. Scheduler mutation by this role is forbidden and was not performed.
