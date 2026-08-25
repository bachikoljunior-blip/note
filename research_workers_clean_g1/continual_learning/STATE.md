# Continual Learning Scan — clean_g1 state

Updated: 2026-08-25T17:01:00+09:00
Generation: clean_g1
Independence: O/O-derived/comparator/integrator state not read. Legacy `research_workers/continual_learning/` not read. Initial clean directory lookup returned 404, so this is a fresh clean baseline.

## Search bias / seed trajectory
Review-to-primary expansion emphasizing forgetting, online/streaming metrics, plasticity, replay selection/scheduling, world models, continual pre-training, and external-memory consolidation. Primary venues prioritized: ICML/PMLR, CoLLAs/PMLR, ACL Anthology, arXiv when no archival version was available.

## Candidate findings

### CLG1-CL-001 — Separate shared dynamics learning from task adaptation via online world-model planning
Primary source: Liu et al., ICML 2025, `Continual Reinforcement Learning by Planning with Online World Models` — https://proceedings.mlr.press/v267/liu25p.html
Mechanism: incrementally fit a Follow-The-Leader shallow dynamics model and solve changing reward-defined tasks by MPC/CEM planning, so task adaptation occurs in planning rather than by rewriting a task policy. The paper proves a sublinear online-model regret bound under its assumptions.
Quantitative evidence: on 6-task Continual Bench, model-based OA final AP/Reg = 72.93/27.62 versus Fine-tuning 24.86/37.74, SI 39.96/33.57, Coreset 61.83/30.83, Perfect Memory 73.09/30.95. OA essentially matches Perfect Memory AP while having lower regret.
Scope/caveat: tasks share state space and dynamics and differ in reward; planner is given reward functions. This is not evidence for arbitrary nonstationary dynamics or open-ended task discovery.
Status: strong transferable architecture candidate.

### CLG1-CL-002 — Replay quantity is not monotonic; sample/task geometry can make replay harmful
Primary source: Mahdaviyeh et al., CoLLAs/PMLR 2026, `Replay can provably increase forgetting` — https://proceedings.mlr.press/v330/mahdaviyeh26a.html
Mechanism/evidence: in over-parameterized continual linear regression, forgetting can be non-monotonic in replay sample count; there are noiseless settings where randomly selected replay increases forgetting in expectation. Authors also show analogous harmful behavior with neural networks trained by SGD and benchmark sensitivity to replay composition/task relationship.
Scope/caveat: strongest theorem is for linear-subspace tasks; neural evidence broadens but does not imply replay is generally harmful. Treat as a design constraint: replay requires selection/alignment, not just more memory.
Status: strong negative-evidence constraint.

### CLG1-CL-003 — Curvature-aware replay stabilizes shifts while preserving plasticity
Primary source: Urettini & Carta, ICML 2025, `Online Curvature-Aware Replay` — https://proceedings.mlr.press/v267/urettini25a.html
Mechanism: approximate Fisher/K-FAC preconditioning with explicit KL constraints on replay data; damping controls stability-plasticity. The Fisher acts as a stabilizer for interfering directions while allowing faster movement in non-interfering directions.
Quantitative evidence: Split-CIFAR100/20 tasks: OCAR 34.9±0.6 final Acc, 48.2±1.2 Average Anytime Accuracy, 25.0±1.1 worst-case validation accuracy, versus ER 28.2±1.2 / 36.6±2.0 / 12.5±0.6 and LPR 33.3±0.6 / 42.5±0.5 / 19.3±0.3. OCAR-ACE reaches 35.6±1.2 / 48.7±1.7 / 26.5±0.4. On Split-TinyImageNet, OCAR has 21.7±1.0 / 38.3±1.4 / 17.4±0.6 and OCAR-ACE 25.6±0.4 / 39.8±2.0 / 21.5±0.9.
Scope/caveat: vision OCL benchmarks, K-FAC overhead/approximation; transfer to large autoregressive models is unverified.
Status: medium-strong mechanism candidate.

### CLG1-CL-004 — Small replay rates plus gradient alignment scale to continual LLM pre-training
Primary source: Abbes et al., CoLLAs/PMLR 2026, `Revisiting Replay and Gradient Alignment for Continual Pre-Training of Large Language Models` — https://proceedings.mlr.press/v330/abbes26a.html
Mechanism: replay plus gradient alignment / efficient meta-experience replay (MER) for continual pre-training; designed to reduce destructive gradient interference.
Evidence: Llama-family continual pre-training across languages with 100B tokens of training data per language; replay and gradient alignment both make learning more stable without forgetting across model scales and task diversity. Scaling analysis: small replay rates are a better compute use than increasing model size, but high replay rates become less compute-efficient than model scaling.
Scope/caveat: exact rate-dependent numeric tradeoff still needs extraction from primary tables before recommending a replay fraction.
Status: strong LLM-specific candidate, numeric follow-up required.

### CLG1-CL-005 — Avoid repeated LR re-warm as a source of forgetting in continual pre-training
Primary source: Singh et al., CoLLAs/PMLR 2026, `Beyond Cosine Decay: On the effectiveness of Infinite Learning Rate Schedule for Continual Pre-training` — https://proceedings.mlr.press/v330/singh26b.html
Mechanism: replace repeated cosine annealing/re-warming with an infinite schedule so new task phases do not repeatedly spike learning rate and overwrite prior features.
Evidence: primary paper reports repeated cosine re-warm inherently induces forgetting and infinite schedule consistently improves continual pre-training on image SSL and autoregressive language-model zero-shot benchmarks. Small MAE setup uses ViT-B/16, constant LR 3.75e-5, with/without replay buffer B=0.05*|D_i|, 300 epochs/task.
Scope/caveat: exact table deltas and interaction with replay must be extracted before ranking against other mechanisms.
Status: promising low-complexity intervention, quantitative follow-up required.

### CLG1-CL-006 — Replay should run on model-time, not wall-clock training steps
Primary source: Feng et al., ACL 2026, `FOREVER: Forgetting Curve-Inspired Memory Replay for Language Model Continual Learning` — https://aclanthology.org/2026.acl-long.1144/
Mechanism: define model-time from cumulative optimizer-update magnitude, schedule replay according to a forgetting curve in that model-time, and adapt replay intensity with regularization rather than fixed step intervals.
Evidence: archival ACL paper evaluates 3 continual-learning benchmarks and models from 0.6B to 13B parameters and reports consistent catastrophic-forgetting mitigation. A secondary extraction reports Qwen3-0.6B average Overall Performance 61.5%, +2.8 points over SSR; this exact number is not yet accepted here as primary-verified.
Scope/caveat: need primary PDF table verification for OP/BWT and compute overhead.
Status: strong scheduling hypothesis, primary numeric verification pending.

### CLG1-CL-007 — External memory relocates rather than eliminates stability/plasticity; abstract strategies can dominate raw trajectories
Primary preprint: Hu, Long & Wang 2026, `When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents` — https://arxiv.org/abs/2604.27003
Mechanism: disentangle memory key organization from value representation; abstract procedural insights reduce retrieval pollution compared with raw episode trajectories.
Quantitative evidence, A→B: ALFWorld raw trajectory FWT -9.5pp versus abstract insight +6.5pp; BabyAI raw -7.5pp versus insight +9.0pp. On ALFWorld hard baseline-fail subset, raw memory ΔNL=-26.1pp while insight gives +3.3pp. Storage/retrieval granularity is task-dependent: BabyAI A→B individual memories give +15.0pp FWT vs aggregate +9.0pp, but step-wise retrieval can reverse gains on homogeneous tasks.
Scope/caveat: two environment/task pairs, preprint; retrieval effects are highly directional and task-structure dependent.
Status: strong design warning/candidate for memory representation and retrieval-policy evaluation.

## Rejected / downgraded leads
- `Tokenized Transformer World Models for Continual RL` (ICLR 2026 submission) was withdrawn; do not prioritize over archival ICML world-model evidence.
- Generic replay-as-more-memory is downgraded because 2026 theory and neural experiments show harmful replay is possible; any replay proposal must specify selection/scheduling/alignment.
- Pure final accuracy is insufficient for OCL ranking when anytime/worst-case metrics are available; prefer AAA, regret, BWT/FWT, worst-case accuracy, or explicit forgetting metrics.

## Unresolved frontier (must remain nonempty)
1. Extract primary tables from FOREVER and verify OP/BWT gains, model-size scaling, replay compute, and ablations for model-time vs intensity regularization.
2. Extract rate-by-rate replay/gradient-alignment tables from Abbes et al.; quantify the small-replay sweet spot and where scaling beats replay.
3. Extract primary quantitative tables from Infinite LR Schedule; separate gains due to avoiding re-warm from gains due to replay and test LM-specific zero-shot deltas.
4. Follow OASIS (ACL 2026) online sample selection for continual instruction tuning; quantify accuracy/compute at fixed selection rates and determine whether global-history informativeness + redundancy updates outperform top-k under distribution shift.
5. Compare example selection signals: learning speed (SBS), feature-angle/mid-angle sampling, curvature/Fisher sensitivity, gradient alignment, and optimizer-update-based replay timing under matched memory/compute budgets.
6. Search for external replications/failures of online world-model FTL outside fixed-dynamics/reward-only task sequences.
7. Investigate plasticity interventions (AdaLin, selective weight reinitialization, replay+Transformer) with explicit separation between new-task learning speed and old-task forgetting.

## Exact continuation
Next run: start with frontier item 1 (FOREVER primary PDF table/ablation extraction). If primary PDF access is blocked, switch to item 4 (OASIS ACL primary paper) and persist exact selection-rate/compute/accuracy metrics. Then branch to item 2 for replay-rate scaling. Do not read legacy or downstream state.

## Termination diagnostics
No platform hard-stop encountered. This run intentionally did not treat the first useful finding as completion; after constructing the main candidate set, an additional unresolved-frontier search was executed on curriculum/sample-selection literature, which surfaced OASIS and curriculum-driven continual DQN branches. Frontier remains nonempty by design.