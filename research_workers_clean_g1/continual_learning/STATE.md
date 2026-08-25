# Continual Learning Scan — clean_g1 state

Updated: 2026-08-25T18:00:00+09:00
Generation: clean_g1
Independence: O/O-derived/comparator/integrator state not read. Legacy `research_workers/continual_learning/` not read. This run resumed only from this clean_g1 file plus newly retrieved public primary sources.

## Search bias / seed trajectory
Review-to-primary expansion emphasizing forgetting, online/streaming metrics, plasticity, replay selection/scheduling, world models, continual pre-training, active sample selection, curricula, and external-memory consolidation. Primary venues prioritized: ICML/PMLR, CoLLAs/PMLR, ACL Anthology, arXiv only when an archival PDF endpoint was inaccessible or to inspect an identical public manuscript.

## Checked primary sources
- Liu et al., ICML 2025, `Continual Reinforcement Learning by Planning with Online World Models` — https://proceedings.mlr.press/v267/liu25p.html
- Mahdaviyeh et al., CoLLAs 2026, `Replay can provably increase forgetting` — https://proceedings.mlr.press/v330/mahdaviyeh26a.html
- Urettini & Carta, ICML 2025, `Online Curvature-Aware Replay` — https://proceedings.mlr.press/v267/urettini25a.html
- Abbes et al., CoLLAs 2026, `Revisiting Replay and Gradient Alignment for Continual Pre-Training of Large Language Models` — https://proceedings.mlr.press/v330/abbes26a.html ; manuscript inspected at https://arxiv.org/pdf/2508.01908
- Singh et al., CoLLAs 2026, `Beyond Cosine Decay: On the effectiveness of Infinite Learning Rate Schedule for Continual Pre-training` — https://proceedings.mlr.press/v330/singh26b.html ; manuscript inspected at https://arxiv.org/pdf/2503.02844
- Feng et al., ACL 2026, `FOREVER: Forgetting Curve-Inspired Memory Replay for Language Model Continual Learning` — https://aclanthology.org/2026.acl-long.1144/
- Lee et al., ACL 2026, `OASIS: Online Sample Selection for Continual Instruction Tuning` — https://aclanthology.org/2026.acl-long.158/
- Hu, Long & Wang 2026, `When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents` — https://arxiv.org/abs/2604.27003

## Candidate findings

### CLG1-CL-001 — Separate shared dynamics learning from task adaptation via online world-model planning
Primary source: Liu et al., ICML 2025, `Continual Reinforcement Learning by Planning with Online World Models`.
Mechanism: incrementally fit a Follow-The-Leader shallow dynamics model and solve changing reward-defined tasks by MPC/CEM planning, so task adaptation occurs in planning rather than by rewriting a task policy. The paper proves a sublinear online-model regret bound under its assumptions.
Quantitative evidence: on 6-task Continual Bench, model-based OA final AP/Reg = 72.93/27.62 versus Fine-tuning 24.86/37.74, SI 39.96/33.57, Coreset 61.83/30.83, Perfect Memory 73.09/30.95. OA essentially matches Perfect Memory AP while having lower regret.
Scope/caveat: tasks share state space and dynamics and differ in reward; planner is given reward functions. This is not evidence for arbitrary nonstationary dynamics or open-ended task discovery.
Status: strong transferable architecture candidate; external replication outside fixed-dynamics/reward-only sequences still needed.

### CLG1-CL-002 — Replay quantity is not monotonic; sample/task geometry can make replay harmful
Primary source: Mahdaviyeh et al., CoLLAs/PMLR 2026, `Replay can provably increase forgetting`.
Mechanism/evidence: in over-parameterized continual linear regression, forgetting can be non-monotonic in replay sample count; there are noiseless settings where randomly selected replay increases forgetting in expectation. Authors also show analogous harmful behavior with neural networks trained by SGD and benchmark sensitivity to replay composition/task relationship.
Scope/caveat: strongest theorem is for linear-subspace tasks; neural evidence broadens but does not imply replay is generally harmful. Treat as a design constraint: replay requires selection/alignment/scheduling, not just more memory.
Status: strong negative-evidence constraint.

### CLG1-CL-003 — Curvature-aware replay stabilizes shifts while preserving plasticity
Primary source: Urettini & Carta, ICML 2025, `Online Curvature-Aware Replay`.
Mechanism: approximate Fisher/K-FAC preconditioning with explicit KL constraints on replay data; damping controls stability-plasticity. The Fisher acts as a stabilizer for interfering directions while allowing faster movement in non-interfering directions.
Quantitative evidence: Split-CIFAR100/20 tasks: OCAR 34.9±0.6 final Acc, 48.2±1.2 Average Anytime Accuracy, 25.0±1.1 worst-case validation accuracy, versus ER 28.2±1.2 / 36.6±2.0 / 12.5±0.6 and LPR 33.3±0.6 / 42.5±0.5 / 19.3±0.3. OCAR-ACE reaches 35.6±1.2 / 48.7±1.7 / 26.5±0.4. On Split-TinyImageNet, OCAR has 21.7±1.0 / 38.3±1.4 / 17.4±0.6 and OCAR-ACE 25.6±0.4 / 39.8±2.0 / 21.5±0.9.
Scope/caveat: vision OCL benchmarks, K-FAC overhead/approximation; transfer to large autoregressive models is unverified.
Status: medium-strong mechanism candidate.

### CLG1-CL-004 — In large-scale continual LM pre-training, replay has a compute sweet spot and cheap gradient alignment can improve the tradeoff
Primary source: Abbes et al., CoLLAs/PMLR 2026, `Revisiting Replay and Gradient Alignment for Continual Pre-Training of Large Language Models`.
Mechanism: mix old-language examples into the current stream at replay fraction alpha, optionally combine with MER/Reptile-style gradient alignment. Reptile interpolation is applied every k=500 batches with epsilon=0.1; its extra cost is approximately three model-size FLOP terms every 500 batches, negligible relative to normal gradient updates.
Setup: Spectra/Llama-family models 99M, 560M, 1B, 6B; DCLM English → French → German, 100B tokens per language. A 1B extension adds Arabic and Japanese for five tasks. Replay fractions tested include 25% and 50%. 25% replay implies about 1.33x compute relative to pure sequential training; 50% implies about 2x.
Retained-loss evidence after the 3-language sequence (DCLM/French/German/AVG):
- 6B sequential: 2.00/1.30/1.10/1.47.
- 6B +25% replay: 1.30/1.05/0.90/1.08.
- 6B +50% replay: 1.17/0.93/0.80/0.97.
- 6B Reptile only: 1.70/1.21/1.09/1.33.
- 6B +25% replay+Reptile: 1.11/0.86/0.77/0.91.
- 6B +50% replay+Reptile: 1.05/0.80/0.74/0.86.
For 1B, average retained loss is 2.50 sequential, 2.29 with 25% replay, 2.08 with 50%, 2.18 with 25% replay+Reptile, and 1.99 with 50% replay+Reptile.
Plasticity evidence from learned loss immediately after each task also improves rather than simply trading off retention at 6B: average 1.37 sequential, 1.00 at 25% replay, 0.87 at 50%, 0.80 at 25% replay+Reptile, 0.76 at 50% replay+Reptile.
Downstream example: for 6B, HellaSwag/PiQA/PubMedQA average is 69.3 sequential, 75.5 with 25% replay, 71.0 with 50% replay, 76.8 with 25% replay+Reptile and 77.1 with 50% replay+Reptile; joint training is 76.0. Thus retention loss and downstream capability are not interchangeable metrics, and more replay is not monotonically better on every downstream measure.
Scaling conclusion from the primary paper: moving from zero to 25% replay is generally more compute-efficient than spending the same budget on model-size scaling, while moving an already-large model from 25% to 50% replay can be less compute-efficient than scaling the model; replay+alignment can improve this frontier.
Scope/caveat: fixed language sequence, mostly three tasks; one five-task experiment at 1B; replay buffer is effectively not a tiny-memory setting; factual-knowledge preservation is not directly isolated. Some extracted 560M downstream table text conflicts with nearby prose, so those 560M downstream numbers are intentionally not used here pending visual table verification.
Status: strong LLM-specific evidence against treating replay fraction as a scalar “more is better” knob; cheap gradient alignment is a high-value companion mechanism.

### CLG1-CL-005 — Repeated LR re-warm itself can cause forgetting; an infinite schedule improves retention even without replay
Primary source: Singh et al., CoLLAs/PMLR 2026, `Beyond Cosine Decay: On the effectiveness of Infinite Learning Rate Schedule for Continual Pre-training`.
Mechanism: use a warmup → cooldown to a nonzero eta_const → constant plateau → final anneal schedule; later task phases resume from the pre-annealed eta_const checkpoint instead of repeatedly re-warming the learning rate. This targets overwrite caused by repeated high-LR restarts.
Small self-supervised MAE evidence (CIFAR10 sequence):
- no replay, repeated cosine: 58.16 Acc / -17.65 BWT; infinite cosine: 60.03 / -12.61.
- 40% replay, repeated cosine ER: 53.98 / -21.55; infinite: 61.45 / -12.76.
- 50% replay, repeated cosine ER: 57.94 / -18.53; infinite: 62.16 / -12.61.
This is direct evidence that the LR schedule can matter independently of replay and can strongly interact with replay.
Large ViT-B/16 sequence ImageNet→Places2→FireRisk, with replay buffer B=0.05|D_i| per task:
- repeated cosine: Avg Acc 48.87, FWT 15.51, BWT -3.61.
- infinite: Avg Acc 50.18, FWT 15.23, BWT -1.37.
Without replay:
- repeated cosine: Avg Acc 39.69, FWT 15.43, BWT -17.91.
- infinite: Avg Acc 41.22, FWT 15.68, BWT -15.06.
After FireRisk, no-replay ImageNet retention is 33.39 with cosine vs 36.38 infinite; Places2 is 23.40 vs 25.19; current FireRisk is essentially tied, 62.30 vs 62.11. This is useful separation: most of the gain is old-task retention rather than current-task acceleration.
LLM setup: LLaMA-3-like 570M, DCLM→Stack→German, 100B tokens/task. Zero-shot normalized-average results:
- cosine DCLM→Stack sequential 38.58; +50% replay 46.37.
- infinite eta_const=1e-4: 40.09; +50% replay 46.39.
- infinite eta_const=2e-4: 39.31; +50% replay 46.81.
For DCLM→Stack→German:
- cosine sequential 33.92; +50% replay 44.65.
- infinite 1e-4: 34.66; +50% replay 44.21.
- infinite 2e-4: 34.21; +50% replay 45.00.
German current-task evaluation is effectively tied: cosine 28.09 avg, infinite 1e-4 28.10, infinite 2e-4 28.06. Do not overclaim a plasticity gain from the LM table; the clear effect is retention/overall zero-shot balance.
Scope/caveat: the large MAE setup resets optimizer states before each task, so this isolates an LR-schedule intervention rather than proving that seamless optimizer-state continuation is optimal. LM gains are modest compared with the vision BWT gains.
Status: strong low-complexity retention candidate; now quantitatively verified and partly disentangled from replay.

### CLG1-CL-006 — Replay timing should follow model-time/update magnitude, not fixed wall-clock steps
Primary source: Feng et al., ACL 2026, `FOREVER: Forgetting Curve-Inspired Memory Replay for Language Model Continual Learning`.
Mechanism: define model-time from cumulative optimizer-update magnitude over trainable parameters, map an Ebbinghaus-style forgetting curve into replay thresholds, and adapt regularization strength from recent update intensity. This makes both “when to replay” and “how strongly to stabilize” state-dependent rather than fixed by batch count.
Main Qwen3-0.6B results, OP/BWT on Standard CL / Long Sequence / SuperNI:
- Fine-tuning: 47.2/-12.6, 36.0/-17.5, 8.2/-27.4.
- MixReplay: 65.8/-8.0, 65.1/-11.4, 34.6/-14.1.
- SSR: 68.4/-7.1, 67.5/-9.0, 40.1/-5.4.
- AIMMerging: 71.9/-5.0, 67.9/-6.3, 41.0/-3.4.
- VBM: 71.5/-5.2, 68.1/-6.1, 41.3/-3.7.
- FOREVER: 72.9/-4.7, 69.4/-5.0, 42.1/-2.9.
MTL upper-bound OP is 77.4/77.8/48.2. The paper reports mean OP 61.5 versus SSR 58.7, and mean BWT around -4.2 versus AIMMerging -4.9.
Model scaling: on LLaMA3.1-8B SuperNI, FOREVER OP/BWT = 50.6/-2.1 versus VBM 49.0/-2.9.
Ablation on SuperNI task order 7, OP/BWT:
- FOREVER 42.5/-2.8.
- fixed-interval replay 40.1/-5.2.
- reversed replay 37.2/-7.8.
- end-only replay 40.9/-6.9.
- step-time calibration instead of model-time 41.3/-3.9.
- removing intensity-aware regularization 39.9/-4.4.
- parameter-importance regularization 42.7/-3.0.
- intensity-aware + parameter-importance 42.8/-2.6.
This is unusually useful component evidence: replay ordering, model-time calibration, and intensity-aware regularization each materially contribute; parameter-importance adds little on top.
Memory-size OP: VBM/FOREVER at 2%,5%,10%,50% memory = 41.2/42.5, 42.4/43.5, 43.0/43.9, 45.4/46.4. Replay epochs: 1 epoch 42.2/-3.0, 2 epochs 42.5/-2.8, 4 epochs 42.6/-2.9, indicating saturation rather than benefit from aggressive repeated replay.
Per-epoch runtime (MixReplay/AIMMerging/VBM/FOREVER): Qwen3-0.6B 1.3/1.5/1.4/1.4; Qwen3-4B 3.5/4.9/3.9/3.8; LLaMA3.1-8B 5.6/8.0/7.2/6.9; LLaMA2-13B 6.8/9.9/9.1/8.5.
Empirical SuperNI forgetting rate decays strongly over time: steps 0–60 0.0023; 60–120 0.0018; 120–180 0.0010; 180–240 0.0005; 240–300 0.0003, roughly sevenfold early-vs-late difference. Scheduler sensitivity S: 3→41.8/-3.8, 6→42.1/-3.7, 12→42.0/-3.4, 24→42.5/-2.8, 48→42.3/-3.0, 96→41.2/-4.4.
Long 30-task sequence: Recurrent-KIF 24.7/-15.0, AIMMerging 26.1/-11.6, VBM 26.7/-12.8, FOREVER 27.9/-10.8.
Scope/caveat: uses 2% per-task replay memory in the main configuration and known task segmentation; many experiments are parameter-efficient/LoRA-style continual tuning. It is not yet evidence for task-free streaming or full-parameter continual pre-training.
Status: upgraded to strong, primary-verified scheduling candidate.

### CLG1-CL-007 — External memory relocates rather than eliminates stability/plasticity; abstract strategies can dominate raw trajectories
Primary preprint: Hu, Long & Wang 2026, `When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents`.
Mechanism: disentangle memory key organization from value representation; abstract procedural insights reduce retrieval pollution compared with raw episode trajectories.
Quantitative evidence, A→B: ALFWorld raw trajectory FWT -9.5pp versus abstract insight +6.5pp; BabyAI raw -7.5pp versus insight +9.0pp. On ALFWorld hard baseline-fail subset, raw memory ΔNL=-26.1pp while insight gives +3.3pp. Storage/retrieval granularity is task-dependent: BabyAI A→B individual memories give +15.0pp FWT vs aggregate +9.0pp, but step-wise retrieval can reverse gains on homogeneous tasks.
Scope/caveat: two environment/task pairs, preprint; retrieval effects are highly directional and task-structure dependent.
Status: strong design warning/candidate for memory representation and retrieval-policy evaluation.

### CLG1-CL-008 — Online sample selection should be history-relative and redundancy-aware, not a fixed top-k per batch
Primary source: Lee et al., ACL 2026, `OASIS: Online Sample Selection for Continual Instruction Tuning`.
Mechanism: ORIS estimates sample informativeness from a last-layer Fisher-information approximation and normalizes it against an EMA/EMV of the previously observed stream, creating relative informativeness rather than batch-local ranking. SIREN then adjusts remaining candidate scores using cosine similarity of last-layer gradients to already-selected samples, suppressing redundancy. Selection is probabilistic and targets a desired long-run ratio without requiring the total stream length.
Component ablation at only 6.25% retained samples, LLaVA-1.5-7B, Aavg/Alast:
- MICVIT fixed-top-FI baseline 62.54±0.55 / 67.16±0.39.
- + ORIS 65.55±0.41 / 72.45±0.30.
- + ORIS + SIREN 67.58±0.46 / 74.51±0.48.
- COAST fixed-top-FI 21.35±0.38 / 29.39±0.26; +ORIS 25.80±0.32 / 35.28±0.52; +ORIS+SIREN 27.83±0.50 / 37.29±0.13.
- Adapt fixed-top-FI 46.36±0.53 / 38.57±0.38; +ORIS 50.52±0.42 / 44.65±0.10; +ORIS+SIREN 51.33±1.16 / 46.22±0.57.
Thus stream-relative quota adaptation is the largest component and explicit redundancy suppression adds another material gain.
Adapt-20, 20 tasks/19 shifts, 12.5% selection, LLaVA-1.5-7B AAUC/Alast:
- Random 51.42±0.74 / 42.11±0.47.
- GradNorm 52.94±1.11 / 45.02±0.91.
- DivBS 54.10±0.37 / 43.21±1.02.
- InfoBatch 54.34±0.68 / 44.59±0.59.
- Adapt-infinity 53.62±0.54 / 43.87±0.66.
- OASIS 55.04±0.89 / 46.84±0.42.
At 12.5%/25% on Adapt, OASIS is 51.73±0.33/49.02±0.85 and 54.58±0.14/51.87±0.49 Aavg/Alast, versus DivBS 49.96/47.17 and 52.36/50.02; InfoBatch 49.77/47.54 and 51.55/49.04. On COAST OASIS at 12.5% is 27.13±0.70/35.42±0.49 versus DivBS 25.13±0.12/33.30±0.87; at 25% OASIS 28.72±0.63/37.55±0.28 versus DivBS 26.91/35.01.
At 25% on MICVIT with Qwen-VL2.5-7B, OASIS reaches 70.23±0.27 Aavg / 76.41±0.41 Alast versus full-data 71.80±0.44 / 79.66±0.43: substantial data reduction with near-full but not equal performance.
Information metric ablation at 6.25%: on MICVIT, FI 64.39±0.58/71.26±0.72 vs entropy 62.75/70.08, perplexity 59.86/64.49, EL2N 60.36/67.15. On COAST, FI 25.67±0.35/34.23±0.38 vs entropy 22.53/30.42, perplexity 20.01/28.64, EL2N 23.28/31.81.
Compute: Table 19 marks OASIS, GradNorm and DivBS as last-layer-gradient methods with normalized selection-compute cost 1.000; forward-only selection methods are 0.976, TIVE full-layer gradient is 2.038, Adapt-infinity middle-layer gradient 1.507. The paper describes OASIS as roughly 3.4% more selection compute than forward-only baselines.
Paper-quality warning: the Limitations text contains a contradictory sentence claiming the method requires only a forward pass and no backward computation. This conflicts with Sec. 3, Algorithm 1, and Table 19, which explicitly compute last-layer sample gradients. Treat the method as requiring last-layer gradient computation; do not propagate the forward-only claim.
Hyperparameter caveat: EMA beta matters; reported COAST-style example Aavg/Alast is 22.24/31.93 at beta=0.7, 24.36/33.28 at 0.9, 22.80/32.73 at 0.99, 23.05/32.94 at 0.999. It is not truly tuning-free.
Scope/caveat: continual instruction-tuning benchmarks, primarily multimodal plus text model experiments; retained-sample training still incurs normal training cost. These results show data/compute-efficient online selection, not by themselves that FI selection is a universal catastrophic-forgetting optimizer.
Status: strong new sample-selection candidate. Most transferable principle is state-dependent learning allocation relative to the entire observed stream, plus explicit redundancy control.

## Cross-paper synthesis (hypotheses, not additional primary facts)
1. **Continual learning is a control problem over update allocation, not a scalar replay-rate problem.** The current evidence decomposes at least four decisions: what to update on (OASIS, gradient alignment), when to replay (FOREVER), how strongly to constrain updates (FOREVER intensity-aware regularization / curvature-aware replay), and how much compute/memory to allocate (Abbes replay scaling; Mahdaviyeh negative result).
2. **State-dependent schedules repeatedly beat fixed schedules.** OASIS adapts sample quota to stream-relative informativeness; FOREVER adapts replay timing to optimizer update magnitude; Infinite LR removes repeated fixed re-warm events. This convergence across different settings is a high-value mechanism family to test under matched compute.
3. **More memory/replay is not reliably monotonic.** Mahdaviyeh provides a formal harmful-replay construction; FOREVER replay epochs saturate; Abbes shows 25→50% replay has a nonlinear compute frontier and can worsen some downstream scores; Infinite LR shows a poor LR schedule can make large replay actively worse in a small MAE sequence. Therefore any future replay candidate must specify selection, timing, update geometry, and compute budget.
4. **Retention and plasticity must be reported separately.** Infinite LR's LM current-task German metric is essentially tied despite better overall retention; Abbes learned-loss and retained-loss tables can both improve at large scale; FOREVER reports BWT and OP. Final-average accuracy alone is not sufficient.

## Rejected / downgraded leads and cautions
- `Tokenized Transformer World Models for Continual RL` (ICLR 2026 submission) was withdrawn; do not prioritize it over archival ICML world-model evidence.
- Generic replay-as-more-memory remains downgraded. Harmful replay is possible and current empirical evidence shows timing/selection/compute interactions.
- Pure final accuracy is insufficient for OCL ranking when anytime/worst-case/regret/BWT/FWT metrics are available.
- OASIS “forward-only/no backward” wording is rejected as internally inconsistent with its method and compute table; treat last-layer gradients as required.
- Do not use the currently ambiguous 560M downstream-table extraction from Abbes as evidence until visually reconciled with the paper prose.
- Do not interpret Infinite LR's essentially tied German current-task result as evidence of materially improved LM plasticity; its stronger evidence is retention and BWT.

## Unresolved frontier (must remain nonempty)
1. Inspect Infinite LR Appendix F / dynamic replay variants and optimizer-reset details; determine whether the best replay interaction survives equalized per-task sample proportions and whether a no-reset optimizer experiment exists.
2. Inspect OASIS public implementation/artifact, if available, to reconcile the forward-only wording error and verify exactly where per-sample last-layer gradients are computed; search for text-only/task-free replications and explicit BWT/forgetting metrics under matched compute.
3. Extract/visually verify Abbes 5-task extension and the ambiguous 560M downstream table; quantify how replay/gradient alignment scale from 3 to 5 tasks and whether uniform replay composition is a hidden limitation.
4. Search external replications/failures of FOREVER-style model-time scheduling and compare with task-free replay triggers, full-parameter fine-tuning, optimizer changes, and non-LoRA regimes.
5. Design a matched-budget evidence comparison across fixed replay vs OASIS-style selection (what) vs FOREVER timing/intensity (when/how strongly) vs MER gradient alignment (update geometry) vs Infinite LR (global LR trajectory), holding total optimizer FLOPs and memory fixed.
6. Search external replications/failures of online world-model FTL outside fixed-dynamics/reward-only task sequences.
7. Investigate plasticity interventions (AdaLin, selective weight reinitialization, replay+Transformer) with explicit separation between new-task learning speed and old-task forgetting.
8. Follow curriculum/active-learning branches that adapt task order rather than only sample inclusion, prioritizing online metrics and causal ablations over final accuracy.

## Exact continuation
Next run: begin with frontier item 1 by reading Infinite LR Appendix F/dynamic-replay experiments and optimizer-state handling. Then execute frontier item 2 by checking OASIS code/artifacts and task-free/text-only evidence, specifically reconciling the last-layer-gradient compute path. Then move to frontier item 3 and visually reconcile Abbes 5-task/560M results. If any branch blocks, immediately switch to frontier item 4 (FOREVER replication/task-free scheduling) rather than ending. Do not read legacy or any downstream state.

## Termination diagnostics
No platform hard-stop encountered. This run resumed the exact clean frontier and did not stop after the first resolved item: it primary-verified FOREVER tables/ablations, then opened the OASIS branch, then quantified Abbes replay-rate/gradient-alignment scaling, then separated Infinite-LR schedule effects with and without replay. The frontier remains deliberately nonempty and the next exact actions are persisted above.
