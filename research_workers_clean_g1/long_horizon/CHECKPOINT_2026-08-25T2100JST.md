# Long Horizon external research — clean_g1 checkpoint — 2026-08-25 21:00 JST

## Boundary / provenance
- Generation: `clean_g1`
- Worker: `long_horizon`
- Search bias: failure-case-first; long-horizon agents, planning, memory, context, longitudinal benchmarks.
- Continuation input used only `research_workers_clean_g1/long_horizon/` plus public external sources.
- Did **not** read `bachikoljunior-blip/O`, O-derived state, comparator/integrator output, other workers, or legacy `research_workers/long_horizon/`.
- This checkpoint extends the prior clean state; it does not import pre-independence artifacts.

## New primary-source findings in this run

### A) LongDS-Bench reset experiment: resetting state can help corrupted trajectories and hurt healthy ones
Primary: https://arxiv.org/abs/2605.30434
Title: `LongDS-Bench: A Benchmark for Long-Horizon Data Science Agents`

The benchmark contains 68 tasks / 2,225 turns with average dependency span 11.3 turns. Its state-evolution patterns include inheritance, update, counterfactual perturbation, rollback, and multi-state composition.

Primary paper details retained this run:
- average task length is ~33 turns;
- average task includes 5.8 rollback turns and 8.6 multi-state composition turns;
- best reported model average is 48.45%;
- performance drops sharply from early to late turns and degrades as dependency breadth/span and state-transition complexity rise;
- authors report a clear decline from Initial → Update → Counterfactual → Rollback;
- long-horizon errors account for roughly 52%–69% of failures, with cascade and state-management errors prominent;
- more analysis steps are not inherently better and can introduce state drift.

Most important new controlled result: the authors reset the code environment once at a task-specific turn and compare post-reset performance against persistent execution. They stratify trajectories by persistent post-reset accuracy:
- Low: 0–30%
- Medium: 30–70%
- High: 70–100%

Reset slightly improves Low/Medium groups but **substantially hurts the High group**; reset gain is negatively correlated with the quality of the persistent state.

Scope-bounded interpretation:
- state reset / rollback is not generically beneficial;
- a reset can remove accumulated corruption, but can also erase useful validated state;
- recovery should be conditioned on estimated state quality / causal corruption, not triggered solely by elapsed horizon or a generic desire for a fresh context;
- this is a behavioral analogue of the previously retained recovery-vs-disruption trade-off for failure interventions.

### B) GUI-RobustEval / RoTS: recovery gets harder as an error propagates farther downstream
Primary: https://arxiv.org/abs/2605.29447
Title: `Recovering Policy-Induced Errors: Benchmarking and Trajectory Synthesis for Robust GUI Agents` (ICML 2026 Spotlight).

Benchmark / mechanism:
- GUI-RobustEval contains 1,216 recovery test cases across 11 error types.
- It explicitly varies error depth `d ∈ {0,1,3,5}`: an erroneous action is injected, additional post-error actions are replayed, then the evaluated agent takes over.
- The paper reports that performance decreases with error depth, attributing the decline to environment drift plus misleading post-error history.
- Planning and progress-perception errors are among the more difficult error families.

RoTS training:
- uses ~20k tasks with reproducible snapshots and ~800k synthesized trajectories/data items;
- explores fragile successful nodes and failure nodes, then launches advice-conditioned recovery from selected error/conflict states instead of training only on immediate one-step corrections;
- reported main result: RoTS-32B reaches 47.4% OSWorld success and 33.8% All-Pass@4 in the paper's headline evaluation.

Indexed renderings surfaced exact depth-wise tables and component ablations, but those exact values were not re-extracted from the primary paper text in this run. Keep them **secondary-indexed / not yet primary-verified** rather than promoting them to exact evidence.

Scope-bounded interpretation:
- the longer a wrong decision is allowed to propagate, the harder recovery becomes;
- checkpoint/rewind systems should prefer locating the earliest causally relevant error/conflict rather than waiting for a late visible failure and blindly rewinding a fixed number of steps;
- this evidence supports causal/root-error localization, but it does not itself compare checkpoint frequencies or prove an optimal rewind policy.

### C) Checkpoint frequency remains a behavioral evidence gap; systems overhead is becoming small enough to study it directly
Primary: https://arxiv.org/abs/2605.22781
Title: `DeltaBox: Scaling Stateful AI Agents with Millisecond-Level Sandbox Checkpoint/Rollback`.

Primary abstract reports approximately:
- 14 ms checkpoint latency;
- 5 ms rollback latency;
- evaluation on SWE-bench / RL-style stateful-agent workloads;
- faster snapshot/restore allows more search nodes under a fixed time budget.

A related systems paper, `Toward Systems Foundations for Agentic Exploration` (https://arxiv.org/abs/2510.05556), compares multiple sandbox snapshot/restore mechanisms and likewise focuses on systems latency rather than behavioral checkpoint-policy quality.

Research-gap result from this run:
- broad primary-source searches did **not** locate a controlled long-horizon agent study that sweeps checkpoint frequency/placement while simultaneously reporting end-to-end task success, recomputation, latency, storage, and side-effect risk.
- therefore do not substitute low checkpoint latency for evidence that 'checkpoint more often' improves agent behavior.

Interpretation:
- checkpointing is becoming cheap enough that checkpoint policy can be an explicit experimental variable;
- the unresolved question is not whether snapshots can be fast, but when they should be taken and when restoring them improves final outcomes after accounting for lost good state and external effects.

### D) Atomix branch verification: pure task-recovery success can tie ordinary checkpoint replay while effect safety differs radically
Primary: https://arxiv.org/abs/2602.14849
Title: `Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows`.

Primary paper distinctions:
- ordinary agent-memory/workspace rollback cannot undo already-sent email, booking changes, or remote API effects;
- effects are classified operationally into reversible/compensable, bufferable, and irreversible-gated categories;
- compensable actions may leave cost/residue even when a compensating action succeeds;
- irreversible effects must be gated/deferred before commit if later rollback is to remain semantically safe.

Important quantitative nuance from τ-bench fault injection:
- at fault probability 0.30, transactional full mode reports 57% clean task success and Checkpoint-Replay about 53%; the reported comparison is statistically tied;
- over the full reported τ-bench set, pure recovery success likewise does not cleanly separate the two approaches.

But effect safety / concurrency behavior differs:
- under the irreversible-send stress test, transactional gating leaks **0/500 invalid sends** while releasing all 500 valid sends;
- under forced multi-agent overlap, the transactional design records zero conflict-cycle/invariant-violation witnesses in the reported tests, whereas weaker baselines exhibit conflicts/violations;
- the paper separately tracks clean abort, leaked effects, unresolved compensation/residue, and partial commit rather than collapsing all recovery into task success.

Scope-bounded interpretation:
- compensation/gating can be essential even when ordinary checkpoint replay is competitive on a narrow final-success metric;
- evaluating long-horizon recovery only by task completion misses irreversible-effect leakage, compensation residue, and concurrency correctness;
- checkpoint policy and effect-commit policy should be evaluated as distinct layers.

## Cross-source synthesis added this run
1. **Reset/rollback has a state-quality-conditioned operating regime.** LongDS directly shows that reset can help low/medium-quality persistent state while harming high-quality state.
2. **Recovery difficulty rises with error propagation depth.** GUI-RobustEval operationalizes error depth and finds later takeover harder, supporting earlier causal localization rather than fixed-late rollback.
3. **Checkpoint frequency itself remains under-evaluated behaviorally.** Fast systems primitives such as DeltaBox solve part of the overhead problem but do not establish an optimal behavioral checkpoint cadence.
4. **Effect safety can be orthogonal to task-recovery success.** Atomix and Checkpoint-Replay can tie on a narrow success metric while differing radically on invalid irreversible effects and concurrency semantics.
5. **A useful recovery policy should estimate both corruption and preservation value.** It should ask not only 'is something wrong?' but also 'how much validated state would this reset destroy?' and 'which external effects cannot be undone?'.

## Tempered / rejected leads added this run
- `Fresh reset is always safer after a long trajectory`: contradicted by the LongDS reset experiment; healthy persistent state can be damaged by reset.
- `Later rollback is equivalent if the agent knows what went wrong`: unsupported; GUI-RobustEval shows recovery degrades as post-error depth increases.
- `Millisecond snapshots imply frequent checkpoints improve task success`: unsupported; available DeltaBox-style evidence is primarily systems overhead/search-capacity evidence, not a behavioral cadence ablation.
- `Final task success is sufficient to evaluate recovery semantics`: contradicted as an evaluation principle by Atomix's effect-leak/concurrency results.
- `Checkpoint replay and transactional effect handling are the same problem`: false; one restores controlled state, the other constrains/compensates external effects.

## Checked sources this run
Primary/high priority:
- https://arxiv.org/abs/2605.30434 — LongDS-Bench full primary HTML, including state-pattern breakdown and reset experiment.
- https://arxiv.org/abs/2605.29447 — GUI-RobustEval/RoTS full primary HTML, error-depth design, recovery synthesis, headline results.
- https://arxiv.org/abs/2605.22781 — DeltaBox primary abstract; systems checkpoint/rollback cost.
- https://arxiv.org/abs/2510.05556 — systems snapshot/restore comparison; retained only as infrastructure evidence.
- https://arxiv.org/abs/2602.14849 — Atomix full primary HTML; effect taxonomy, fault-recovery comparison, irreversible-send and contention tests.

Secondary/indexed only:
- indexed RoTS renderings that expose exact depth-wise and component-ablation values. Do not treat those exact tables as primary-verified until source/PDF/table artifact is directly inspected.

## Nonempty frontier after this checkpoint
1. **State-quality-conditioned reset policy.** Find a controlled agent method that explicitly predicts whether to reset/rewind versus preserve current state, and compare learned/heuristic gating against always-reset / never-reset baselines on final task success.
2. **Primary RoTS table verification.** Inspect paper source/code/author artifacts to verify exact depth-wise recovery values and FDE/EIR ablation numbers rather than relying on indexed secondary renderings.
3. **Checkpoint cadence behavioral ablation.** Continue searching for studies that vary checkpoint interval/placement under the same tasks and report success plus recomputation/latency/storage/effect cost. If absent, preserve the gap explicitly.
4. **Rewind-depth selection.** Find matched comparisons among fixed-depth, latest-good, root-cause/dependency-selected, learned-selection, and earliest-conflict policies.
5. **Compensation utility, not just effect safety.** Seek email/API/database/booking-like agent studies measuring user/task utility after compensation, including residual fees, duplicate messages, stale notifications, or other semantic residue.
6. **AgentRewind exact primary tables.** Verify the previously indexed 62.2/78.0/87.8 and component-ablation values from a primary PDF/source/author artifact.
7. **Deterministic-verification boundary.** Quantify where invariant checks stop covering semantic goal/state errors and learned monitoring remains necessary.
8. **Subgoal/folding negative evidence.** Find controlled cases where wrong decomposition or stale folding loses task success despite context/token savings.
9. **CRNR / context-refresh numbers.** Extract trustworthy primary quantitative deltas from UltraHorizon or its artifacts.

## Exact continuation
Next run first action: search for **state-quality-conditioned reset/rollback selection** with matched always-reset / never-reset / gated policies and end-to-end outcomes. Then inspect the RoTS primary source/code/author artifact for exact error-depth and FDE/EIR tables. If that branch stalls, return to the checkpoint-cadence gap and compensable external-effect utility branch. Preserve at least one unresolved frontier at checkpoint time.
