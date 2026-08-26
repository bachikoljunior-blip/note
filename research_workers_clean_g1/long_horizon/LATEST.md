# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1400JST_SELECTOR_HARNESS.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST_REPLAY_TESTBED.md`
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST_ADDENDUM.md`
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST.md`
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1201JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `511ad1dc04c5a2b6d72e8050fb9c56bea25f3dba`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA. Repository writes later advanced main, but no newer control/config was adopted after the semantic freeze barrier.

Current synthesis delta:
- Replay Gap's public SWE-bench branching implementation already supplies fresh-container prefix reconstruction, exact message-prefix seeding, live suffix continuation, multiple fork positions, and a required same-model branch control. This narrows the missing selector-testbed engineering substantially.
- A newly identified strict-factorial confound is budget-by-depth: current branch code sets resumed `n_calls = fork_step - 1` under one global step limit, so rollback target depth changes the remaining action/model-call budget. Selector-only comparison must instead hold a branch-local post-intervention action/token/retry budget constant across targets.
- Replay Gap's current replay-fidelity audit is return-code based. A strict target comparison should also require reconstructed workspace/repository-state equivalence (e.g. deterministic git/tree/diff digest) before admitting a branch, otherwise target quality can be confounded by imperfect state reconstruction.
- TraceElephant's bundled SWE-Agent `run_replay.py` is more concrete than previously established: it reconstructs a fresh environment and uses `ReplayModelConfig` to execute the stored assistant actions, explicitly for demo generation and environment/tool debugging. It is a useful replay/fidelity primitive, but as shipped it replays the recorded action sequence rather than exposing arbitrary-prefix replay followed by a live policy. Prefix truncation + state assertion + live-model swap + branch-local budget are still needed.
- Substrate preference is now: Replay Gap for the first strict SWE-bench selector-only factorial; TraceElephant/SWE-Agent as an independent replication runtime after prefix-to-live continuation is added; Captain-Agent/Magentic-One only after their replay semantics are separately verified.
- The strict selector-only scientific gap remains unfound: same alarm, candidate set, restoration/carry-forward, model and post-intervention budget with only historical target selector varied and final task success measured.

Updated strict experimental blueprint:
- one failure alarm/intervention time fixed per base trajectory;
- one admissible checkpoint set precomputed and shared by all selector arms;
- selectors differ only: random/latest-safe/static-root/executed-causal-or-probe/agent-selected/oracle ceiling;
- identical context/environment/inference restore and failed-branch carry-forward;
- equal **post-intervention** action/token/retry budget independent of rollback depth;
- fresh-prefix reconstruction plus workspace digest and replay-trace fidelity checks;
- live suffix execution from selected target, never factual-suffix stitching;
- same-model control branches for replay/sampling noise;
- final metrics: SWE-bench resolution, actions/tokens/wall time, healthy-trajectory disruption, target coverage/abstention, replay mismatch; no claim about irreversible-effect safety from container-only results.

Exact continuation:
1. Search learned historical-target selectors that can plug into this fixed candidate-set harness, especially intervention-advantage / executed-counterfactual selectors, and require recovery plus healthy-trajectory disruption accounting.
2. Search published SWE-bench/tool-agent experiments that explicitly normalize post-rollback action/token budget across multiple historical targets.
3. Inspect full-inference-state restoration systems that can couple to live branching without selector-specific restore differences.
4. Formalize a stronger branch-admissibility contract: workspace digest, exact context/message prefix, tool/environment return-code trace, and where relevant inference-state freshness/rebinding.
5. Preserve the strict selector-only factorial gap unless alarm, candidates, restore/carry-forward, model and budget are genuinely fixed.
6. Maintain nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
