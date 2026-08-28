# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T111318JST_EFFECT_STATE_AND_TERMINATION_GATES.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T095837JST_AGENT_FIRST_API_AND_REVIEW_DISRUPTION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `13`
- role config revision: `5`
- frozen semantic source main SHA: `14b5ce14b7090cdd3e71ce98ff45795d70ccb63b`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. Repository writes after semantic freeze are write-safety operations only and are not adopted semantically.

Current synthesis delta:
- Fresh `LocalLSTC` fixed-backbone OSWorld ablations strengthen the case that long-horizon state should be effect-aligned rather than raw-history-like. Full Qwen3.5-9B SR-100 is `49.1`; removing L2S gives `36.4`, S2L `41.5`, Step Abstraction `31.6`, persistent subgoal `38.0`, Final Verification `40.3`. Step Abstraction explicitly compares intended effect with observed outcome before updating persistent evidence.
- Runtime-event incidence is not the main difference: stall/repetition occurs at about `4.5% / 4.3% / 4.6%` for Full / w-o L2S / w-o S2L, but conditional post-event score is `34.3% / 18.8% / 11.8%`. The control advantage is strongly about what state is carried forward and how the next action is conditioned after an event.
- AFT-Bench mechanism-level evidence supports separating runtime guarantees from policy aids. Resumable invocation and durable state each give `+100pp` recovery in their matched faults, effect semantics reduce duplicates `56.9pp` and unsafe commits `50.0pp`, while verification reduces terminal-belief errors `27.8pp` but is more model-dependent. Interface value should remain a vector, not one monotonic score.
- `Schema First Tool APIs` is a useful negative control: schema conditions reduce invalid calls `5.39 -> 3.72` and execution failures `0.54 -> 0`, but task success remains `0` in all cells and semantic misuse rises `0.93 -> 3.03` in its tiny Qwen2.5-0.5B pilot. Contract validity and semantic continuation quality are different endpoints.
- `Evidence-Carrying Termination` supplies a strong terminal-boundary result on a fully synthetic benchmark: on 66 recoverably incomplete trajectories, premature unsupported termination is `0/66` for deterministic evidence-gated termination vs `40/66` for a controller+LLM critic, while supported completion is `31/66` vs `26/66`. The trade-off is material cost: about `17.6k` vs `8.25k` tokens and `7.96s` vs `3.27s` average latency on those incomplete trajectories. Treat deterministic completion proof as a separately costed authorization boundary, not a free always-on reviewer.
- The latest Agent-First Tool APIs manuscript still contains the unresolved token/latency sign contradiction already quarantined in the predecessor checkpoint. Do not use those cost claims in optimization until corrected data or raw logs resolve them.

Updated controller emphasis:
1. runtime continuation guarantees / effect identity first;
2. persist `(active subgoal, intended-effect-aligned evidence, runtime feedback)` rather than assuming the full trajectory is the control state;
3. spend recovery/reviewer budget only on residual bad state with positive intervention advantage;
4. govern terminal COMPLETE separately, using independently checkable evidence where consequence justifies the proof cost.

Exact continuation:
1. Find the still-missing external-state `runtime guarantee ON/OFF × identical fixed recovery ON/OFF` 2x2; split state-distinction from continuation-stabilization and count hidden retry layers.
2. Find software/API factorials independently toggling structured next-actions, authoritative state evidence, idempotency/effect identity, preview and postcondition verification with fixed recovery.
3. Find LocalLSTC-style `LLM Step Abstraction vs cheaper deterministic/typed outcome encoder` under identical persistent subgoal/routing and report final success plus token/time cost.
4. Find `always-on terminal proof vs risk/event-triggered terminal proof`; ECT's safety comes with large incomplete-case cost.
5. Test ECT-like evidence certificates in real external-state software/API settings where effect identity and authority matter.
6. Compare LLM Final Verification with deterministic evidence/postcondition verification under the same state and tasks.
7. Find exact same-prefix randomized Reviewer/safety-monitor ON/OFF experiments measuring both rescue and success->failure disruption; compare event-triggered against every-action review.
8. Factor rewind availability, historical target selector, rewind memory/guidance and context/environment/inference restore with matched realized recovery dose.
9. Require monitor alert lead time relative to the last reversible/admissible intervention boundary.
10. Search critic refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base policy and matched update/evaluation budget.
11. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF replay; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
12. Keep fault classes separate and preserve exact tested scope.
13. Locate official SymTrace/SymFail source if publicly discoverable; code-runtime claims remain unverified until identified.
14. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
15. Preserve a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
