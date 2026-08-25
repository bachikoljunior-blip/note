# Long Horizon external research — clean_g1 checkpoint — 2026-08-25 20:00 JST

## Boundary / provenance
- Generation: `clean_g1`
- Worker: `long_horizon`
- Search bias: failure-case-first; long-horizon agents, planning, memory, context, longitudinal benchmarks.
- Read continuation only from `research_workers_clean_g1/long_horizon/` and public external sources.
- Did **not** read `bachikoljunior-blip/O`, O-derived state, comparator/integrator output, other workers, or legacy `research_workers/long_horizon/`.
- This checkpoint extends the prior clean state; it does not import pre-independence artifacts.

## New primary-source findings in this run

### A) Accurate failure prediction can make end-to-end performance much worse
Primary: https://arxiv.org/abs/2602.03338
Title: `Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention` (submitted 2026-02-03).

Setup:
- binary critic: Qwen3-0.6B + LoRA rank 16
- trained on 7,636 trajectory steps from HotPotQA and GAIA
- task-disjoint splits; ALFWorld is complete domain transfer
- intervention budget: max 3 interventions within a 15-action agent budget
- two intervention mechanisms: `ROLLBACK` (undo latest action + restore environment + retry) and `APPEND` (execute action but append warning)
- threshold in calibrated setting: predicted failure probability > 0.6

Critic quality, held-out test:
- Qwen-3-8B backbone: AUROC 0.982, F1 0.989, n=474
- GLM-4.7: AUROC 0.966, F1 0.976, n=234
- MiniMax-M2.1: AUROC 0.897, F1 0.937, n=664
- overall: AUROC 0.936, F1 0.963, n=1,372

Yet final task outcomes under intervention (Table 4 in primary arXiv HTML):

HotPotQA:
- Qwen-3-8B baseline 57.0%; best intervention 54.7% => best delta -2.3 pp
- GLM-4.7 baseline 70.3%; best intervention 70.3% => 0.0 pp
- MiniMax-M2.1 baseline 64.0%; best intervention 38.5% => -25.5 pp

GAIA:
- Qwen-3-8B baseline 18.9%; best intervention 14.5% => -4.4 pp
- GLM-4.7 baseline 34.4%; best intervention 31.1% => -4.4 pp
- MiniMax-M2.1 baseline 46.7%; best intervention 16.7% => -30.0 pp

ALFWorld, critic zero-shot transfer:
- Qwen-3-8B baseline 5.8%; best intervention 8.6% => +2.8 pp
- GLM-4.7 baseline 14.7%; best intervention 15.8% => +1.1 pp
- MiniMax-M2.1 baseline 16.1%; best intervention 16.6% => +0.5 pp
- primary abstract reports Qwen's +2.8 pp as p=0.014.

Mechanistic formalization from the paper:
- baseline failure rate `p`
- recovery rate `r`: baseline-fail -> intervention-success
- disruption rate `d`: baseline-success -> intervention-fail
- net change in success = `p*r - (1-p)*d`
- intervention helps only when `p > d/(r+d)`.

For a 50-task Qwen-3-8B ALFWorld pilot, the paper reports approximately p=89%, r=12%, d=56%, giving threshold p*=82%; since 89% > 82%, a positive effect is predicted.

Additional negative evidence:
- scaling critic size to 14B did not improve prediction quality in this data regime.
- oracle analysis says even perfect failure prediction has only ~4–8 pp upside in the tested systems because the agent's ability to absorb correction is the bottleneck.

Scope-bounded interpretation:
- detector AUROC/F1 is not a deployment objective.
- a long-horizon failure monitor must be evaluated together with the actual intervention policy and base agent.
- the correct pre-deployment quantities are at least `(p,r,d)` and final success delta, not detection accuracy alone.
- high-success regimes can be especially vulnerable because false/disruptive interventions destroy trajectories that would otherwise finish successfully.

### B) A positive matched repair result shows the opposite regime can exist
Primary: https://arxiv.org/abs/2608.02464
Title: `Real-Time Detection and Repair of LLM Agent Failures` (submitted 2026-08-03).

Primary abstract reports:
- 2,823 committed agent episodes across 3 frameworks, qwen2.5 7B/3B, llama3.1 8B, and gemini-2.5-flash.
- one-class telemetry monitor: AUROC 0.872; detects 0.71 of failures at 5% false-alarm budget.
- ranking transfers without retraining to AFTraj-2K at 0.745 and ATBench at 0.779.
- cold transfer of the monitor itself fails: AUROC 0.527 cold vs 0.885 after recalibration, establishing a deployment-specific healthy-null burden.
- deterministic verification catches 60% of failures, or 96% with coverage check, with 0/63 false positives; monitor catches 54% at 17% false positives.
- deterministic layer trips on 0/1,825 healthy episodes and transfers unchanged to llama3.1:8b (110/110 targeted cases, 0/10 false positives in the reported comparison).
- closing detection into live repair by rollback + rerun recovers 45% of failures vs 16% resampling control (p=0.0005), increasing task success from 52% to 73%, for about one extra model call per run.
- runtime monitor cost reported ~200 microseconds per step.

Interpretation alongside paper A:
- online repair is not intrinsically good or bad; its net value depends on false/disruptive intervention rate, failure prevalence, intervention mechanics, and the base agent's ability to recover.
- deterministic/evidence-grounded checks may dominate learned monitoring when the task exposes verifiable invariants, because they can reduce the disruption term `d` toward zero.
- learned monitor transfer requires explicit recalibration; cross-deployment AUROC should not be assumed.

### C) Irreversible effects require compensation semantics, not just snapshots
Primary: https://arxiv.org/abs/2604.23283
Title: `Revisable by Design: A Theory of Streaming LLM Agent Execution` (submitted 2026-04-25).

The paper separates epistemic state (context/beliefs; rollbackable) from world state (only partially rollbackable), and classifies actions into:
- `I` Idempotent/no world-state modification
- `R` Reversible/exact inverse exists
- `K` Compensable/no exact inverse, but a compensation can produce an acceptable state (e.g. send correction after sent email; cancel a booking with fee)
- `X` Irreversible/no feasible compensation (e.g. settled transaction; unique data deleted without backup)

Formal consequence:
- incompatible `K` actions impose unavoidable compensation cost after they have executed.
- incompatible `X` actions make full satisfaction of the revised specification impossible.
- these costs cannot be fixed by a better planner/model/context window; only changing the tool/action semantics (adding compensation endpoints, reversible defaults, or deferring irreversible actions) can reduce them.

Rollback-selection result:
- under compatibility-separability plus monotone compensation/waste assumptions, the structurally optimal rollback point is immediately before the **earliest conflicting K/X action** (`Earliest-Conflict Rollback`).
- adaptation cost = compensation cost + wasted discarded work.

Experiment:
- StreamBench, DeepSeek-V3 agent, n=1,008 runs.
- primary paper reports Revision Absorber quality statistically indistinguishable from brute-force Full-Restart while wasting 14.6x fewer already-completed steps.

Scope-bounded interpretation:
- checkpoints should not be treated as universal undo.
- rollback policy should be coupled to an action-effect ledger that records reversibility/compensation semantics.
- for truly irreversible actions, safety must act **before commit**; after commit there may be no recovery algorithm that restores the original feasible set.
- for compensable actions, recovery success should include compensation cost and semantic residue, not just internal state restoration.

## AgentRewind verification status
Primary: https://arxiv.org/abs/2608.14380

This run attempted to obtain the arXiv PDF directly, but the web fetch was blocked. Primary abstract still confirms the mechanism and broad gains, while exact values remain visible through indexed secondary renderings only:
- GPT-5.4 Continue 62.2%, Restart-with-experiences 78.0%, AgentRewind 87.8%
- GPT-5.4 mini Continue 33.7% -> AgentRewind 51.2%
- ablations: no environment rewind 43.9%; no context rewind 65.9%; no rewind memory 51.2%
- 11/12 task-level comparisons reportedly remain significant after Holm correction, exception task-success vs Restart

Do **not** upgrade those exact figures to primary-verified until the paper PDF/source or author artifact is inspected directly. The primary abstract is enough only for the qualitative claim: aligned context + controlled-environment checkpoints + failed-branch memory improve task success/checklist progress across tested models/strategies/harnesses.

## Cross-source synthesis added this run
1. **Intervention has a disruption-recovery operating curve, not a universal benefit.** Measure p/r/d and final outcome, not critic AUROC alone.
2. **The base agent is part of the intervention mechanism.** Same critic/mechanism can be neutral, catastrophic, or mildly beneficial across models/task regimes.
3. **Use deterministic verification where invariants permit.** It can reduce false alarms/disruption dramatically and can transfer better than a learned monitor.
4. **Rollback and irreversible-effect handling are distinct layers.** Context/filesystem rewind cannot undo every external-world effect.
5. **Reversibility should be an action-space property recorded before execution.** I/R/K/X or an equivalent taxonomy enables safe checkpoint/commit policy.
6. **High-impact irreversible actions should be delayed/gated.** Once an X-class action conflicts with a later correction, full satisfaction may be impossible.
7. **Rollback point selection should target the earliest causal conflict, not blindly rewind a fixed number of steps**, when effect dependencies/reversibility metadata are available.

## Tempered / rejected leads added this run
- `High critic AUROC means critic intervention is safe`: directly contradicted by arXiv:2602.03338.
- `Calibration solves harmful intervention`: contradicted; calibrated and uncalibrated variants can both degrade, especially MiniMax-M2.1.
- `Rollback is always safer than append-warning`: contradicted as a universal claim; net effect is model/benchmark dependent.
- `A learned monitor trained on one deployment transfers as-is`: contradicted by cold AUROC 0.527 vs 0.885 recalibrated in arXiv:2608.02464.
- `Checkpoint restore means external effects are undone`: contradicted by the reversibility taxonomy and by AgentRewind's own controlled-workspace limitation.
- `Fixed-depth rollback is the right generic checkpoint-selection rule`: unsupported; earliest causal conflict/reversibility boundary has a stronger theoretical basis when metadata exist.

## Checked sources this run
Primary/high priority:
- https://arxiv.org/abs/2602.03338 — full primary arXiv HTML with critic metrics, Table 4 intervention outcomes, theory, pilot threshold.
- https://arxiv.org/abs/2608.02464 — primary arXiv abstract with telemetry-monitor and live-repair quantitative outcomes.
- https://arxiv.org/abs/2604.23283 — primary arXiv HTML with reversibility taxonomy, irreversibility principle, earliest-conflict theorem, and n=1,008 / 14.6x headline experiment.
- https://arxiv.org/abs/2608.14380 — primary metadata/abstract; direct PDF fetch attempted but blocked.

Secondary/indexed, retained only for unresolved exact AgentRewind tables:
- alphaXiv/Paperlayer renderings of arXiv:2608.14380. Do not treat them as primary confirmation.

Not elevated:
- generic checkpointing blog/documentation results without controlled behavioral outcome data.
- training-checkpoint papers unrelated to execution-time agent state recovery.

## Nonempty frontier after this checkpoint
1. **AgentRewind primary-table verification remains open.** Obtain PDF/source/author artifact and verify 62.2/78.0/87.8, 33.7/51.2, 43.9/65.9/51.2, and Holm-significance details.
2. **Checkpoint frequency / cost trade-off.** Find controlled agent experiments varying checkpoint frequency/placement and measuring task success, rewind/recompute cost, storage/latency, and side-effect risk. Existing search results mostly discuss infrastructure rather than behavioral ablation.
3. **Checkpoint selection / rewind depth.** Seek execution-time agent studies comparing fixed-depth, latest-good, learned selection, causal/dependency-guided, and earliest-conflict policies under the same tasks.
4. **Subgoal/folding negative evidence.** Find primary controlled cases where wrong decomposition, stale folded state, or aggressive compaction lowers final success despite token savings.
5. **Deterministic verification boundaries.** Identify long-horizon tasks where deterministic checks cannot cover semantic/goal-drift failures and quantify the residual need for learned monitoring.
6. **Compensation effectiveness.** Find real or controlled LLM-agent studies with K-class actions (email/API/database/booking-like effects) that measure whether compensation restores task/user utility, including compensation cost and residual side effects.
7. **Active memory vs specific GAMBIT demands.** Determine whether selective proactive memory separately improves online updating, interference resistance, episodic binding, and hypothesis revision.
8. **CRNR numeric extraction / context refresh.** Still need trustworthy UltraHorizon refresh/notes-recall deltas.
9. **LongDS per-pattern intervention.** Inspect primary benchmark/code for inherit/update/rollback/multi-state composition breakdown and any state-recovery mechanism.

## Exact continuation
Next run first action: search **primary controlled agent studies that vary checkpoint placement/frequency or rewind selection/depth**, prioritizing end-to-end task success plus compute/latency/storage and side-effect measurements. If no behavioral ablation exists, document that gap rather than substituting systems-only latency results. Then make a second branch into **compensable external effects** (email/API/database/bookings) with matched compensation-vs-no-compensation outcomes. Keep at least one frontier unresolved when checkpointing.
