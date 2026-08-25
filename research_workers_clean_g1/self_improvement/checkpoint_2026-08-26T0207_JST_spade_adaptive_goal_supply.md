# CLEAN self-improvement checkpoint — SPADE adaptive goal supply

Time: 2026-08-26 02:07 JST
Role: self_improvement / clean_g1
Source lineage: `checkpoint_2026-08-26T0204_JST_bat_long_loop_and_feedback_audit.md`.
Independence: only current own clean continuation + public primary/author sources. No O, other-worker, downstream, or legacy semantic state.

## Why this branch matters

The prior checkpoint isolated a missing control-plane problem: repeated adaptive evaluation needs stronger statistical/outer-audit protection. A separate self-improvement bottleneck is *goal/environment supply*: if training tasks are fixed, the learner can saturate them. SPADE gives unusually direct matched evidence that adapting the training environment itself can outperform fixed environment pools, while also exposing the external-novelty dependence and failure modes.

### Source `arxiv:2608.19197` / `spade-rl:spade`
Primary paper: https://arxiv.org/abs/2608.19197 (submitted 2026-08-19)
Author project page: https://spade-rl.github.io/
Author technical overview: https://benjamin-eecs.github.io/blog/2026/spade/
Public code: https://github.com/spade-rl/spade

Observed primary/author-source facts:
- SPADE trains a shared policy in two roles: Environment Designer (ED) writes executable stateful reset()/step() environments; Reasoning Agent (RA) learns inside them.
- Designer reward uses hint-based regret: the gap between RA return with versus without a privileged hint. This targets tasks that are feasible with guidance but difficult unaided.
- Candidate environments undergo syntax/executability/solvability checks before entering the training pool.
- The public games recipe for Qwen3-30B-A3B runs 400 rollouts on one 8-GPU node. The repo exposes matched fixed-environment baselines and paper-ablation launchers.
- At 30B-A3B, the author-reported eight-benchmark suite average is 58.3, versus 50.2 base and about 53.0 for the strongest fixed-environment RLVE baseline: +8.1 over base and +5.3 over the strongest fixed-environment baseline.
- Author-reported individual held-out gains include GPQA-Diamond +5.4, LiveCodeBench-v6 +4.1, and Reasoning-Gym categories roughly +5.8 to +18.3; AIME is roughly retained. Tool-use transfer is reported at +5.7 on BFCL-v4 multi-turn and +13.9 on ACEBench-Agent at 30B scale.
- Scaling pattern: author reports SPADE gain over base rising from +5.2 at 4B to +5.7 at 8B and +8.1 at 30B-A3B, while matched fixed-environment gain stays near +1.2. Tested scope is the published model/settings; this is evidence that adaptive task supply becomes more valuable with learner capacity in these runs, not a general scaling law.

## Component ablations

Author/project materials and released ablation recipes support the following 30B games comparison:
- full SPADE: 58.3 suite average
- no environment memory: 53.2
- no corpus grounding: 53.5
- no ED training + no memory: 40.5
- frozen GPT-5.5 environment designer with corpus + memory: 53.0
- replace hint-regret with EMA-style learning-potential control: 55.9

Interpretation guards:
- The no-ED-training control also removes memory, so `ED gradient update alone` is not isolated by the 40.5 result.
- Frozen GPT-5.5 changes designer identity as well as trainability, so it is a useful fixed-designer control but not a pure trainability ablation.
- The learning-potential reward comparison is cleaner because ED training remains active while the reward mode changes; 55.9 vs 58.3 supports the tested hint-regret blend over that EMA alternative, not each reward subcomponent individually.

Public repo provenance:
- `cmd/ablations/README.md`, blob `f127a89bef96816b0190bb7893c542cc4cab4a13`, explicitly lists paper controls: no corpus, no memory, no ED training+memory, frozen GPT-5.5 pool/designer control, two-skill restriction, learning-potential reward, solve-rate reward.
- Repo README states fixed-env GPT-5.5 corpus has 7,872 validated Python environments with per-environment SHA-256 checksums and that paper ablations are run from `cmd/ablations/*.sh`.

## Diversity / novelty supply mechanism

The strongest mechanism evidence is corpus grounding:
- Author project materials report normalized Vendi diversity ~0.68 with corpus versus 0.04 without corpus.
- In one no-corpus interval, the designer repeatedly emitted the same rotating-maze family; author materials report 41 consecutive repeats, and the project explorer describes 413/865 rewrites of the maze with a 296-run sequence in one view.
- Thus external corpus grounding clearly prevents mode collapse in the reported environment-generation process. This also means SPADE is **not self-sufficient novelty creation**: much of topic diversity is injected from external pretraining documents.
- Memory appears to serve a different role: move generation away from already-seen/mastered environments and sustain curriculum progress. No-memory stays above base but peaks/fades earlier than full SPADE in author curves.

## Self-improvement implication

SPADE supports a two-level improvement design:

`learner improvement` <-> `goal/environment generator improvement`

A fixed task pool is a consumable signal source. Once mastered, extra learner capability can be under-trained. Adapting the generator to maintain a capability-frontier task distribution can produce additional held-out transfer under matched RL compute.

But the useful version is not `unbounded self-generated tasks` alone. The evidence points to a controlled generator with:
1. external grounding for diversity,
2. memory to avoid repeated/mastered tasks,
3. a learnability/frontier signal (hint-regret),
4. executable/solvable environment validation,
5. held-out downstream evaluation.

This complements, rather than replaces, the prior checkpoint's acceptance/audit gates: an adaptive generator can make *training supply* better while still overfitting or exploiting its verifier unless candidate environments and downstream gains are audited separately.

## Failure / overclaim guards

- Do not call SPADE open-ended AGI self-improvement: the optimizer, reward mix, corpus, validation rules, training schedule and evaluation suite remain human-fixed.
- Do not say it generates novelty from itself; the no-corpus collapse shows external documents are a major diversity source.
- Do not infer ED training alone causes the entire 17.8-point gap between full and no-ED/no-memory, because memory is removed simultaneously.
- Do not treat author/project checkpoint selection as a pristine final test without checking selection protocol; project materials show repeated held-out benchmark curves and best-checkpoint reporting. This deserves the same adaptive-evaluation scrutiny identified in the BaT branch.
- No independent replication was located in this run; current evidence is author-reported + public code/data/checkpoints.

## Nonempty frontier / exact next action

1. Inspect SPADE evaluation/checkpoint-selection code and model cards: determine how often the held-out benchmark suite is queried, how the released/best checkpoint is selected, and whether a separate untouched final checkpoint/task set exists.
2. Compare full SPADE against its fixed-env baselines at **matched number of generated environments, RL rollouts, optimizer steps and evaluation queries**, not only headline compute budget.
3. Verify the exact memory ablation mechanism in code: what memory is stored, retrieval/update rule, whether memory content is itself evaluated/retired, and whether memory can induce curriculum fixation.
4. Search for independent reruns/failure reports of SPADE once available; especially small-model negative-regret periods and environment reward hacking.
5. Cross the two branches: look for an adaptive environment generator like SPADE whose generated-task admission and repeated downstream evaluation are protected by BaT-style content isolation plus PACE/SEA-style sequential evidence control.

Exact continuation: first audit `spade-rl/spade` evaluation/checkpoint-selection path and public 30B model card; if no untouched outer test exists, formalize this as a second instance of the recurring `adaptive controller uses its evaluation suite as a selection instrument` risk and search for systems that explicitly separate curriculum-controller, model-selection, and final-lockbox task sets.
