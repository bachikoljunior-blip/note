# Long Horizon external research — clean_g1 checkpoint — 2026-08-25 23:00 JST

## Boundary / provenance
- Generation: `clean_g1`.
- Worker: `long_horizon`.
- Effective repository control: `automation_control/DESIRED_STATE.json`, control_revision 1, role `long_horizon`, config_revision 1, enabled_desired=true.
- Substantive continuation input used only `research_workers_clean_g1/long_horizon/`, public external sources, and own sanitized feedback path.
- Own sanitized feedback path `research_feedback_clean_g1/long_horizon/FEEDBACK.json` was checked and remains absent (404); no feedback was consumed.
- Did **not** intentionally use `bachikoljunior-blip/O`, O-derived state, comparator/integrator/index/feed output, other workers, or legacy/pre-independence research as research context.

## Context-contamination guard / correction
During this run, the shared `automation_control/EXECUTION_LEDGER.json` was accidentally fetched while attempting to satisfy the bootstrap's receipt requirement. That shared file contains downstream/other-role semantic state and therefore violates the `clean_exploration` read boundary for this role. Its semantic contents were immediately quarantined and were **not used** for source selection, interpretation, synthesis, candidate generation, or the findings below. This checkpoint contains no research claim derived from that shared ledger.

Operational correction for future runs: `long_horizon` should not read a shared semantic execution ledger. If an execution receipt is needed, write an append-only role-local receipt without reading other-role receipts first. This avoids making downstream state a continuation input.

## New primary-source findings

### A) Crab — checkpoint cadence can be selected from recovery-relevant OS effects instead of checkpointing every turn
Primary: https://arxiv.org/abs/2604.28138 and arXiv HTML for `Crab: A Semantics-Aware Checkpoint/Restore Runtime for Agent Sandboxes`.

Problem: application-level checkpointing preserves chat/file-level state but can miss process/package/shell side effects; full OS/VM checkpointing is correct but can be prohibitively expensive when every turn is snapshotted.

Mechanism: Crab observes OS-visible effects at agent turn boundaries with an eBPF-based inspector and chooses among no checkpoint, filesystem-only, process-only, or full checkpoint. Checkpoint work is overlapped with LLM wait time and host-side scheduling smooths concurrent C/R traffic.

Primary reported results:
- Terminal-Bench recovery correctness: chat-only baselines 8–13%; chat+filesystem baselines 28–42%; Crab 100%.
- Across evaluated shell-intensive/code-repair workloads, despite one crash per task, Crab stays within 1.9% of optimal no-fault execution time.
- Restart-from-scratch adds up to 1.52× completion time on Terminal-Bench and 1.67× on SWE-Bench in the reported setup.
- Every-turn full checkpointing on Terminal-Bench slows Claude-code by 3.06× at 64-sandbox density and 3.78× at 96-sandbox density because of host storage contention.
- Checkpoint sparsity is large: Claude-code/Terminal-Bench skips 87% of turns, uses filesystem-only checkpoints for 5%, full checkpoints for 8%; iFlow-cli/Terminal-Bench skips 70%, filesystem-only 25%, full 5%; SWE-agent/SWE-Bench skips ~75%, filesystem-only ~25%, almost no full checkpoints.
- In fault-free runs, asynchronous overlap keeps p95 exposed checkpoint delay to 0.44% of task time at 64-sandbox density.
- In agent-facing rollback case studies, exposing sandbox restore as a tool reduced wall-clock time by up to 29% and rollback tokens by 36% compared with shell-level self-recovery.

Scope-bounded interpretation:
- This is strong evidence against `checkpoint every turn` as a universal default when most turns do not change recovery-relevant state.
- It addresses **checkpoint placement/granularity**, not the harder `should the agent rewind now?` state-quality trigger or `which historical checkpoint should be selected?` target policy.
- The semantic signal is OS-visible effect classification, so it can miss semantic corruption that changes beliefs/context without mutating sandbox state. A separate cognitive/state-quality trigger remains necessary.

### B) LongDS-Bench reset study — the preserve-vs-reset decision is strongly baseline-state dependent
Primary: https://arxiv.org/abs/2605.30434 and https://arxiv.org/html/2605.30434v1.

The primary HTML directly verifies the reset protocol and the recovery–continuity trade-off:
- Benchmark: 68 tasks / 2,225 turns; average dependency span 11.3 turns; state operations include update, counterfactual, rollback and composition.
- In the main evaluation, long-horizon errors account for 52%–69% of failures and average model performance falls nearly 47 points from early to late task progress.
- For the reset diagnostic, the authors use GPT-5.4, preserve the interaction history, but clear accumulated code state, variables and intermediate results once at a task-specific point.
- Five tasks with essentially unusable persistent baselines are excluded from this diagnostic.
- Candidate reset points are turns 2, 4, 6 and 15; a task-specific heuristic chooses the point whose remaining-turn ratio is closest to half the persistent baseline accuracy.
- Evaluation compares exactly the same post-reset turns against the persistent baseline.
- Tasks are grouped by persistent post-reset accuracy: Low 0–30%, Medium 30–70%, High 70–100%.
- Reset slightly improves low- and medium-baseline cases but substantially hurts high-baseline cases; reset gain is negatively correlated with persistent post-reset accuracy.

Scope-bounded interpretation:
- This is direct evidence that a reset policy needs a **state-quality estimate**: indiscriminate reset can clear poisoned state but can also destroy useful accumulated state.
- The paper does **not** supply an online learned runtime trigger; the grouping is retrospective using persistent accuracy, unavailable to a deployed agent. The central open problem remains how to estimate state quality online without outcome leakage.
- The reset preserves chat history while clearing code environment, so it is not equivalent to AgentRewind-style coupled context+environment rewind.

## Synthesis added this run
The recovery stack should now separate four control decisions:
1. **Checkpoint placement/granularity** — Crab suggests checkpoint only when recovery-relevant state changed, and capture only the state class that changed.
2. **Whether to intervene** — LongDS and prior recovery/disruption evidence imply a state-quality-conditioned gate; healthy trajectories should often be preserved.
3. **Where to rewind** — prior AgentRewind/DART evidence still leaves a direct matched target-selection ablation largely open.
4. **What state to replace** — causal depth and effect boundaries determine whether to replace one action, reasoning prefix, environment state, or a broader dependency region.

This narrows a previously broad `checkpoint cadence` frontier: systems evidence now shows that effect-aware adaptive placement can reduce C/R traffic sharply without losing tested recovery correctness, but **behavioral trigger policy** and **historical target selection** remain distinct unresolved problems.

## Tempered / rejected leads added this run
- `Checkpoint every turn for safety`: strongly tempered by Crab; at high co-location it can be slower than restart and most turns may have no recovery-relevant OS state.
- `Reset whenever a long trajectory looks stale`: contradicted as a universal rule by LongDS; high-quality persistent states are harmed by reset.
- `A good checkpoint placement policy solves rewind control`: false; Crab decides what/when to snapshot, not whether/where a cognitive agent should rewind after semantic failure.
- `Environment reset is equivalent to full recovery`: false in scope; LongDS keeps interaction history and only clears code state, while prior evidence shows context/environment alignment can matter.

## Search result on the exact continuation question
A direct primary matched study comparing an **online state-quality predictor** that chooses `preserve vs rewind/reset` against `always reset` and `never reset` on final long-horizon outcomes was not located in this run. A direct matched runtime target-selection comparison among fixed-depth, latest-good, root-cause/dependency, semantic-admissible, random and learned/agent-selected rewind targets also remains unlocated.

## Nonempty frontier
1. **Online state-quality trigger**: find or construct a runtime predictor that estimates corruption/drift risk before outcome is known and compare gated preserve-vs-rewind against always/never intervention.
2. **Rewind-target policy ablation**: agent-selected vs fixed-depth vs latest-known-good vs dependency/root-cause vs latest-semantic-admissible vs random under matched tasks and budgets.
3. **Bridge semantic and OS state**: combine Crab-style effect-aware checkpoint placement with semantic/context-state mutation detection; quantify false negatives where cognition is corrupted but OS state is unchanged.
4. **Automatic semantic-boundary discovery**: infer DART-like admissible boundaries/effect contracts automatically and audit unsafe admissions.
5. **Checkpoint cadence behavioral ablation**: vary placement policy while reporting final task success, recovery correctness, recomputation, latency, storage, and side-effect risk—not systems overhead alone.
6. **Subgoal/folding negative evidence**: controlled failures where wrong decomposition or stale folded state harms final task success.
7. **Compensable-effect utility**: quantify residual harm/cost after compensation, not merely binary rollback safety.

## Exact continuation
Next run first action: search primary sources for an **online corruption/state-quality signal** used to gate preserve-vs-reset/rewind on final task outcomes. Search terms should include state quality, trajectory corruption, cascade risk, intervention gate, reset controller, rollback trigger, and recovery/disruption. In parallel, search for explicit historical checkpoint-target ablations. If no direct study is found, branch into combining semantic-state detectors with Crab-style recovery-relevant effect classification while preserving the gap as unresolved.
