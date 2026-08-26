# Long Horizon clean_g1 — selector harness checkpoint

## Frozen semantic control tuple
- frozen note main SHA: `511ad1dc04c5a2b6d72e8050fb9c56bea25f3dba`
- root control revision: `9`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- semantic boundary preserved: only own clean state plus public sources were used. Repository main advanced after the semantic freeze; no newer control/config was adopted.

## New primary-source findings
### 1. Replay Gap is already very close to the missing selector-only software-agent experiment
Public implementation `AshrithaG/replay-gap` provides a branch protocol that starts a fresh SWE-bench container, replays recorded prefix actions to rebuild environment state, seeds the branch model with the exact message prefix, and then executes a live suffix from the chosen fork. `run_pilot.py` already supports multiple fork positions and same-model branch controls. This means a rollback-target-selector experiment does not need a new generic checkpoint runtime from scratch.

However, two concrete confounds must be fixed before calling the experiment selector-only:
1. In the current branching code, the resumed agent sets `n_calls = fork_step - 1` while the global step limit remains fixed. Therefore earlier rollback targets receive more remaining model/action calls than later targets. A strict target comparison needs a branch-local post-intervention budget counter so every selector arm receives the same action/token/retry budget regardless of historical depth.
2. Replay fidelity currently checks per-action return-code agreement. That is useful but weaker than state equivalence. The strict harness should additionally record a workspace/repository digest (at minimum git status/diff/tree or equivalent deterministic state hash) after prefix reconstruction, so a target is admitted only when both execution results and reconstructed workspace state match within the declared fidelity contract.

Minimal strict factorial on this substrate:
- fix one failure alarm / intervention time per base trajectory;
- precompute one admissible checkpoint candidate set shared by all arms;
- vary only target selector: random, latest-safe, static-root-cause, executed-causal/probe-based, agent-selected, and oracle ceiling;
- use identical fresh-container replay, context restoration, carry-forward policy and model;
- enforce equal branch-local action/token/retry budget after intervention;
- execute live suffixes, never factual-suffix stitching;
- include same-model control branches to estimate replay/sampling noise;
- grade final SWE-bench resolution plus actions/tokens/wall time, target coverage/abstention, replay mismatches, and disruption of trajectories that would otherwise succeed.

Scope guard: SWE-bench containers provide a strong software-agent test but do not by themselves test irreversible external effects or GUI/robotics state.

### 2. TraceElephant's bundled SWE-Agent replay is useful but is not yet an arbitrary-prefix live-continuation API
TraceElephant publicly bundles the SWE-Agent runtime including `sweagent/run/run_replay.py`. The replay runner extracts all assistant actions from a stored trajectory, replaces the model with a `ReplayModelConfig`, creates a new environment, and executes the recorded actions to reproduce environment behavior. Its documented use is demo generation and tool/environment debugging.

This is useful as a reconstruction/fidelity primitive and makes cross-harness validation easier than previously established. But as shipped it replays the recorded action sequence; it does not expose the exact missing experiment primitive of "replay only to checkpoint k, then switch to a live policy under a fixed post-intervention budget". That requires a small but material extension: prefix truncation/stop, state-fidelity assertion at k, swap ReplayModel for live model, and a branch-local budget counter.

Therefore current substrate preference is:
1. Replay Gap for the first strict selector-only SWE-bench factorial because fresh-prefix reconstruction + live continuation + multiple fork positions + same-model control already exist.
2. TraceElephant/SWE-Agent as an independent second implementation for cross-runtime replication once prefix-to-live continuation is added.
3. TraceElephant's Captain-Agent/Magentic-One systems only after per-system replay/restore semantics are separately verified; do not assume one generic checkpoint API.

## What this changes
The earlier frontier was partly "find or build a replayable selector testbed." The build gap is now narrower: a public SWE-bench harness already contains most required primitives. The unresolved scientific gap is still the actual controlled result: no located study yet fixes alarm, candidates, restore/carry-forward, model and post-intervention budget while changing only historical rollback target selector and measuring final software-agent task success.

A particularly important experimental requirement is now explicit: **equalize remaining intervention budget across historical targets**. Without this, a deeper rollback can appear better simply because it gets more subsequent decisions, or worse because it must replay more work, conflating target quality with horizon/budget.

## Exact continuation
1. Inspect learned historical-target selectors that can plug into the fixed Replay Gap candidate set, especially intervention-advantage or executed-counterfactual selectors, and require recovery plus healthy-trajectory disruption accounting.
2. Search for published SWE-bench or tool-agent experiments that already normalize post-rollback action/token budget across multiple historical targets.
3. Inspect full-inference-state restoration systems (KV/cache/session state) that can be coupled to this live-branch harness without selector-specific restore differences.
4. Define an admissibility/fidelity contract stronger than return-code equality: workspace digest, message/context prefix identity, tool/environment return-code trace, and where relevant inference-state freshness/rebinding.
5. Preserve the strict selector-only factorial gap unless the only changed variable is historical target selection.
6. Maintain a nonempty frontier; this checkpoint is not global completion.

## Public source artifacts inspected this run
- `AshrithaG/replay-gap/src/replay_gap/branching.py`
- `AshrithaG/replay-gap/scripts/run_pilot.py`
- `AshrithaG/replay-gap/configs/pilot.yaml`
- `AshrithaG/replay-gap/scripts/replay_fidelity.py`
- `TraceElephant/TraceElephant/code/agent_system/SWE-agent/sweagent/run/run_replay.py`
