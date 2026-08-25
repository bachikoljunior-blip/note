# Long Horizon external research — clean_g1 checkpoint — 2026-08-25 21:57 JST

## Boundary / provenance
- Generation: `clean_g1`
- Worker: `long_horizon`
- Search bias: failure-case-first; long-horizon agents, planning, memory, context, longitudinal benchmarks.
- Continuation input used only `research_workers_clean_g1/long_horizon/` plus public external sources.
- Own sanitized feedback path `research_feedback_clean_g1/long_horizon/FEEDBACK.json` was checked and was absent (404); no feedback was consumed.
- Did **not** read `bachikoljunior-blip/O`, O-derived state, comparator/integrator/index/feed output, other workers, or legacy/pre-independence research.

## New primary-source findings in this run

### A) AgentRewind exact tables are now primary-verified
Primary: https://arxiv.org/abs/2608.14380 and primary PDF https://arxiv.org/pdf/2608.14380

The previously verification-needed exact values were checked directly in the primary PDF.

MettleBench / mini-SWE-agent, GPT-5.4 (mean ± sample SD over n=3):
- Continue: task success 62.2 ± 2.1; checklist 81.4 ± 1.0.
- Restart with Experiences: 78.0 ± 2.4; checklist 88.8 ± 1.2.
- Safety Review: 34.1 ± 1.2; checklist 54.4 ± 2.1.
- AgentRewind: 87.8 ± 1.2; checklist 94.3 ± 0.5.

GPT-5.4 mini:
- Continue: 33.7 ± 0.7; checklist 64.6 ± 1.1.
- Restart with Experiences: 43.1 ± 1.4; checklist 64.5 ± 1.3.
- Safety Review: 36.2 ± 1.9; checklist 64.5 ± 0.8.
- AgentRewind: 51.2 ± 4.2; checklist 73.5 ± 3.0.

Component ablation, GPT-5.4 / mini-SWE-agent:
- Full AgentRewind: 87.8 success / 94.3 checklist.
- w/o environment rewind: 43.9 / 63.5.
- w/o context rewind: 65.9 / 77.9.
- w/o rewind memory: 51.2 / 69.4.

Paired recovery from 50 identical failed Continue endpoints:
- Continue: 8.0% recovery; +5.1 pp checklist progress.
- AgentRewind: 30.0%; +12.2 pp.

Terminal-Bench 2.0 provides an important restart counterexample:
- Continue: 78.7 success / 88.7 average criteria.
- Restart with Experiences: 70.8 / 79.2.
- AgentRewind: 83.1 / 90.2.

Scope-bounded interpretation:
- aligned context + reversible-environment restoration plus compact failed-branch memory has strong behavioral support in these engineering/terminal tasks;
- whole restart can destroy useful validated progress and can be worse than ordinary continuation;
- a generic per-action safety/review layer can severely disrupt task completion in the tested GPT-5.4 setting, reinforcing that intervention quality must be judged by final outcomes, not by nominal caution;
- these exact results do not establish an optimal rewind-target policy: AgentRewind exposes up to 80 checkpoint candidates and lets the agent choose, but the paper does not compare learned/agent-selected targets against random, fixed-depth, latest-good, or semantic-admissibility policies.

### B) RoTS exact primary recovery-depth ablation is now verified
Primary: https://arxiv.org/abs/2605.29447 and https://arxiv.org/html/2605.29447v1

GUI-RobustEval contains 1,216 cases across 11 policy-induced error types and controlled error depths `d ∈ {0,1,3,5}`. The environment and injected history are replayed to the chosen depth before agent takeover; recovery degrades as error depth grows.

Most useful new exact ablation: maximum recovery depth in the RoTS reflection/recovery training data, under a fixed 100k/7B data budget and fixed reflection mixture.
- no recovery data: post-error success 12.1; GUI AP@4 8.0; OSWorld AP@4 8.6; OSWorld success 18.5.
- depth ≤2: 15.5 / 10.5 / 10.0 / 19.5.
- depth ≤5: 20.7 / 13.4 / 12.8 / 21.1.
- depth ≤7: 21.5 / 13.8 / 13.5 / 21.3.
- no cap: 22.1 / 14.1 / 14.1 / 21.4.

The largest marginal gain occurs by moderate depth ≤5 (+8.6 post-error-success points versus no recovery data); gains beyond depth 7 are small (+0.8 to no-cap on post-error success).

Experience-informed recovery ablation also separates recognition from recovery:
- base actor: awareness 60.4; post-error success 42.9.
- reflector without experience: awareness 62.6.
- reflector with experience: awareness 67.1.
- EIR without advice: awareness 67.1; post-error success 44.3.
- full EIR with advice-conditioned actor: awareness 67.1; post-error success 46.1.

Scope-bounded interpretation:
- deeper recovery supervision is useful, but its marginal value saturates; at least in this training-data setting, moderate recovery horizons capture most of the gain;
- recognizing an error and actually repairing it are separable capabilities;
- this is a training-data recovery-depth ablation, not a runtime checkpoint-depth policy experiment. Do not promote it as proof that runtime rollback should always use five steps.

### C) DART: the latest mechanically restorable checkpoint can be semantically invalid
Primary: https://arxiv.org/abs/2605.23311 and https://arxiv.org/html/2605.23311v1

DART formalizes **semantic recoverability** for structured tool agents. Its runtime:
1. localizes the failed subtask instance;
2. certifies reviewed recoverable boundaries;
3. binds checkpoints to that instance;
4. restores the most recent **admissible** checkpoint only if dependency/effect constraints allow it, otherwise blocks local rollback and falls back to whole-task rerun.

A candidate boundary must satisfy decidability, closure, separability, and controllability. Even a stable checkpoint is rejected if a committed downstream consumer depends on the output being rewound or if the effect policy disallows crossing the boundary.

Commitment-sensitive core-domain results:
- navigation: Retry-Only succeeds with 18 replay actions; entry-only local restore fails the contract; admissible frozen restore succeeds with 1 replay action and preserves 2 completed instances.
- schedule-form: Retry-Only succeeds with 29 replay actions; entry-only has no recovery; admissible frozen restore succeeds with 1 replay action and preserves 5 completed instances.
- diagnosis: Retry-Only succeeds with median 16.5 replay actions; entry-only has no recovery; admissible frozen restore succeeds with 2 replay actions and preserves 2.5 completed instances.

External LangGraph-based decisive schedule-form case:
- Retry-Only: 1.00 success, 25.5 replay actions, ~32.6 s failure-to-milestone.
- LangGraph checkpoint-aligned restore: 0.00 success.
- DART admissible restore: 1.00 success, 1 replay action, ~1.11 s.

Five-domain semantic audit:
- 54/54 comparable rows safe-equivalent;
- 0/35 unsafe admitted events;
- 0/12 false-blocked events and 0/16 false-blocked checkpoints under the paper's frozen audit specifications.

Checkpoint-granularity diagnostic in navigation (synthetic latency harness):
- Retry-Only: 12 average replay steps / 8 upstream / ~8209.75 ms.
- entry-only: 4 / 0 / ~3751 ms.
- reviewed admissible commit checkpoint: 1 / 0 / ~872 ms.

Scope/limitations:
- failures are observable at action boundaries; silent semantic failure detection and automatic universal boundary synthesis are outside scope;
- reviewed boundary/interface/effect contracts are required;
- the dependency relation is intentionally conservative and may block some otherwise safe rollbacks.

Interpretation:
- checkpoint availability and checkpoint admissibility are different problems;
- choosing the **latest safe semantic boundary** can preserve more validated work than entry-only or whole-task restart, but only if downstream commitments and effects are explicitly checked;
- this complements AgentRewind: AgentRewind demonstrates the benefit of aligned state rewind in open-ended engineering tasks; DART provides a stricter target-admission criterion in structured runtimes.

### D) CLEANER/SAAR: rollback granularity should match causal error depth; local credit can be actively harmful
Primary: https://arxiv.org/abs/2601.15141 and https://arxiv.org/html/2601.15141v2

CLEANER targets agentic-RL trajectory contamination from repeated code-tool failures. SAAR temporarily exposes an execution error to obtain a successful correction, then retrospectively purifies the training trajectory.

Granularity rule:
- high code-similarity correction → shallow replacement: keep original reasoning, replace failed code/error with corrected code/result;
- low-similarity correction → deep replacement: replace the failed reasoning as well as action, because keeping incompatible upstream reasoning would create semantic dissonance.

Matched Qwen3-4B tool-RL ablation:
- tools baseline: AIME24 66.7/84.4 Pass@1/16; AIME25 59.4/84.2; GPQA 56.9; LiveCodeBench 26.6.
- +SAAR: 72.7/87.6; 67.1/84.1; 60.2; 26.8.

Qwen2.5-7B tools baseline → +SAAR:
- AIME24 40.2/59.1 → 44.6/64.3.
- AIME25 27.3/46.3 → 31.0/54.7.
- GPQA 35.9 → 40.0.
- LiveCodeBench 13.0 → 13.1.

The authors also report an explicit failed approach: using the failed tool call as an online-DPO negative while masking credit to the tool-call segment slightly improved local snippet self-repair but failed to improve complex-task success and later caused training collapse. Their analysis attributes this to many tool failures being rooted in faulty preceding reasoning; penalizing only the action breaks causal alignment.

Additional scope:
- this is primarily **training-time trajectory purification**, not a runtime rollback controller;
- retry limit K=3 was reported as the best recovery/cost balance in their setup, with diminishing returns above 3;
- post-hoc introduction after an unstable policy had already developed improved AIME24/AIME25 by 5.2/1.0 points but did not catch up to training with SAAR from the start, suggesting path dependence from earlier contaminated training.

Interpretation:
- when a failure originates upstream in reasoning/state, repairing or penalizing only the visible action can preserve an inconsistent causal prefix and make learning worse;
- recovery granularity should be conditioned on how far the error reaches upstream, not fixed to one action.

## Synthesis added this run
A stronger recovery architecture hypothesis emerges, but the *combined stack itself is not yet directly tested*:
1. **Gate whether intervention is warranted**, because restart/review/reset can disrupt healthy trajectories.
2. **Localize the causal error**, distinguishing a superficial action failure from upstream reasoning/state corruption.
3. **Choose a semantically admissible boundary**, not merely the newest mechanically restorable checkpoint; preserve committed downstream work and respect effect boundaries.
4. **Restore coupled reversible state** (internal context + controlled environment), not one side alone.
5. **Retain only minimal validated lessons from the discarded branch**, avoiding re-injection of the full contaminated suffix.
6. **Prefer limited recovery depth when sufficient**; RoTS training ablations show diminishing returns from increasingly deep recovery examples, while AgentRewind/Terminal-Bench shows indiscriminate full restart can destroy useful progress.
7. **Evaluate final task success, preservation of validated work, replay cost, and effect safety separately**; awareness/proxy gains alone are not enough.

This synthesis sharpens the earlier frontier from “how often/how far to rewind” into three separate decisions: **whether to rewind, which semantic boundary is admissible, and how much causal state must be replaced**.

## Tempered / rejected leads added this run
- `Always restart after a failure`: contradicted by AgentRewind's Terminal-Bench result where Restart with Experiences (70.8%) trails Continue (78.7%).
- `Any recent checkpoint is safe if the runtime can restore it`: contradicted by DART commitment-sensitive cases and LangGraph external validation.
- `Repair the visible failed action and keep all upstream reasoning`: unsafe as a general learning rule; CLEANER's failed local-negative experiment can collapse training when the true error is upstream.
- `More/deeper recovery data is always proportionally better`: tempered by RoTS depth-cap ablation; most marginal gain appears by moderate depth and then saturates.
- `Error awareness is equivalent to recovery`: contradicted by RoTS EIR ablation; awareness can rise without a comparable end-to-end repair mechanism.
- `Safety review necessarily improves final task safety/utility`: tempered by AgentRewind's Safety Review baseline, which severely lowers GPT-5.4 task success in the tested setup.

## Remaining evidence gaps / nonempty frontier
1. **State-quality-conditioned runtime rewind trigger.** Current search still did not locate a direct long-horizon matched study that predicts whether to preserve vs reset/rewind and compares gated policy against always-reset and never-reset on final task outcomes.
2. **Runtime rewind-target policy ablation.** Compare agent-selected, fixed-depth, latest-known-good, root-cause/dependency-selected, latest-semantic-admissible, and random checkpoint policies under matched tasks.
3. **Checkpoint cadence behavioral ablation.** Vary snapshot interval/placement while reporting task success, recomputation, latency, storage, and effect safety; systems latency alone is not enough.
4. **Automatic semantic-boundary discovery.** DART currently depends on reviewed boundary/interface/effect contracts; find methods that learn or infer these boundaries without sacrificing soundness.
5. **Open-ended semantic admissibility.** Test whether DART-like dependency/effect constraints transfer from explicit structured runtimes to open-ended trajectories such as MettleBench.
6. **Irreversible/compensable effect utility.** Measure residual user/task harm after compensation (fees, duplicate sends, stale notifications, external API residue), not just binary effect safety.
7. **Subgoal/folding negative evidence.** Find controlled failures where wrong decomposition or stale folded summaries lose task success despite token savings.
8. **CRNR/context-refresh quantitative extraction.** Verify UltraHorizon refresh/notes-recall deltas from a primary artifact.
9. **Deterministic-verification boundary.** Identify where invariant checks cease to cover semantic goal/state errors and learned monitoring becomes necessary.

## Exact continuation
Next run first action: search for a **runtime state-quality / rewind-trigger controller** with matched preserve-vs-rewind baselines. In parallel, search for explicit **rewind-target selection ablations** (fixed depth vs latest-good vs root-cause/dependency vs learned/agent-selected) rather than generic rollback systems. If no direct study is found, preserve the gap and branch into automatic semantic-boundary discovery and compensable-effect utility. Keep at least one unresolved frontier at checkpoint time.
