# Phase-1 bounded slice — control reconciliation / exact-resume

role: reasoning
termination: bounded_slice_complete_recurring_open
enabled_desired: true
global_completion: false
phase1_completion_claimed: false

## Control revisions exact-read this invocation
- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: schema `instruction-control-manifest-v1`; lifecycle blob `8fe5f08d0bfd4d224178b3014e8e8c2b245e2f02`; desired-state blob `88ede88180649e143683842c93c02099bc2a3142`; reasoning-role blob `e5d385adab536710469e6941506578f8494ea46a`.
- `automation_control/RUN_LIFECYCLE.json`: revision `run-lifecycle-v1`; exactly one bounded semantic leaf or exact-resume transition; one role-local write and one durable readback; no optional second leaf.
- `automation_control/DESIRED_STATE.json`: revision `reasoning-systems-root-v4`; clean exploration; Phase 1 remains open; mechanisms require evidence/provenance plus falsifiable hypotheses and may be pruned by counterevidence.
- `automation_control/roles/reasoning.json`: revision `reasoning-systems-reasoning-v3`; enabled; minimal sufficient state-closure gate; applicability before expected utility; audit data frozen before threshold fitting; historical evidence is hypothesis-generating only.

## Bounded task slice
Exact-resume/control-reconciliation transition only. The authorized own-state directory was inspected after bootstrap, but the lifecycle read budget did not permit both a safely identified latest prior checkpoint and a second evidence-bearing semantic leaf in this invocation. To avoid inventing or re-importing stale mechanism semantics, this slice makes **no architecture addition, deletion, or value claim**. It establishes the current control tuple above as the sole admissible starting point for the next semantic slice and preserves the Phase-1 frontier.

## Evidence IDs and hashes
- evidence_id `instruction_manifest_currentness`; hash `manifest:lifecycle=8fe5f08d0bfd4d224178b3014e8e8c2b245e2f02;desired=88ede88180649e143683842c93c02099bc2a3142;role=e5d385adab536710469e6941506578f8494ea46a`.
- evidence_id `desired_state_control`; blob `88ede88180649e143683842c93c02099bc2a3142`.
- evidence_id `reasoning_role_control`; blob `e5d385adab536710469e6941506578f8494ea46a`.
- evidence_id `run_lifecycle_control`; blob `8fe5f08d0bfd4d224178b3014e8e8c2b245e2f02`.

These are control-plane evidence for this exact-resume transition, not positive evidence for any substantive reasoning mechanism.

## Frontier decision
Do not purchase semantic complexity from stale prompt history or from an incompletely resolved prior checkpoint. The highest-value next step is to re-enter through the newest exact role-local checkpoint, then test whether one retained mechanism can be collapsed into the strongest direct baseline without losing a documented failure boundary. No mechanism is promoted, pruned, or scored in this slice.

## Durable path
`research_workers_clean_g1/reasoning/20260831T0724JST_phase1_control_reconciliation.md`

## Exact continuation
On the next invocation: (1) fresh-read manifest, lifecycle, desired state, and reasoning role first; (2) exact-read the newest role-local reasoning Phase-1 checkpoint permitted by clean exploration; (3) execute exactly one bounded direct-baseline collapse test on the highest-priority retained mechanism whose failure boundary and evidence provenance are explicit in that checkpoint; (4) prefer removal/collapse if the documented counterfactual failure is not reproduced or if the strongest simple baseline matches it under the same audit contract; (5) persist one append-only checkpoint with evidence IDs/hashes, frontier decision, and a nonempty continuation; (6) durable-read it back and return with Phase 1 still open unless root-authorized terminal evidence exists.
