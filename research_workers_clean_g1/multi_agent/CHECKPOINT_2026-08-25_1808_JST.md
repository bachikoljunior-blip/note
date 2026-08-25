# Multi-Agent Scan — clean_g1 continuation checkpoint

Timestamp: 2026-08-25T18:08:00+09:00
Generation: clean_g1
Independence boundary: only public external sources and `research_workers_clean_g1/multi_agent/` were used. O, O-derived state, comparator/integrator outputs, other workers, and legacy `research_workers/multi_agent/` were not read.

## New candidate evidence

### C6 — Adaptive per-query pruning of both agent count and communication topology
Primary: Boyi Li et al., *Adaptive Graph Pruning for Multi-Agent Communication*, arXiv:2506.02951v3, ECAI 2025. https://arxiv.org/abs/2506.02951

AGP jointly learns hard pruning over agents/nodes and soft pruning over communication edges so team size and topology can change by task. The paper reports +2.58% to +9.84% task improvements and >90% token reduction in its strongest comparisons. Detailed ablation: full AGP scores MMLU 87.65, GSM8K 95.01, HumanEval 90.62; without soft pruning 83.49/90.13/85.63; without hard pruning 85.20/91.56/88.41. The authors also report that reproduced fixed-size teams peak only within a narrow team-size range on GSM8K/HumanEval/MMLU; adding irrelevant agents can reduce accuracy while increasing cost.

Scope: mostly text benchmarks and gpt-4o-mini; do not assume transfer to long-horizon tool/embodied systems.
Mechanism hypothesis: treat marginal utility of each role and edge as task-dependent; prune both nodes and links instead of scaling nominal N.

### C7 — QD/search strategy is landscape-dependent, not universally superior
Primary: Antonis Antoniades et al., *Heuresis: Search Strategies for Autonomous AI Research Agents Across Quality, Diversity and Novelty*, arXiv:2606.25198v2, 2026-07-01. https://arxiv.org/abs/2606.25198

Heuresis holds the research-agent loop fixed and compares Greedy, MAP-Elites, Go-Explore, Islands, Omni and Curiosity over three ML research domains, with 300 executed ideas per strategy/domain cell (5,400 executions; 3,222 scored). NanoGPT: Greedy best val_bpb 0.9567, top-10 0.9579. On-policy RL: MAP-Elites best single/top-10 1.582/1.572; Islands 1.563; Go-Explore 1.561; Greedy 1.368. Model unlearning: Greedy best 1.0309, Curiosity 1.0012. Thus MAP-Elites wins one landscape and is last on nanoGPT.

Held-out RL retest on MinAtar Asterix: Islands 3.991±0.041, MAP-Elites 2.755±0.186, Go-Explore 0.734±0.060; Greedy/Omni had no valid held-out top-5 result due timeouts/failures. Novelty remains a hard failure mode: 0/3,222 ideas rated fully Original, and only one novel-side idea also lands in the top quality tier. The system records 40 confirmed reward-hacking fabrications among 1,628 scored runs in the relevant audit set.

Scope: prompts/search algorithms intentionally untuned and 300 executions/cell. Do not infer a universal ranking.
Mechanism hypothesis: choose outer search strategy from landscape properties such as recombinability, branchability, novelty density and evaluator reliability.

### C8 — Learned dynamic role+edge dropout gives a concrete accuracy–cost frontier
Primary: Zhexuan Wang et al., *AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration*, ACL 2025. https://aclanthology.org/2025.acl-long.1170/

The paper reports average reductions of 21.6% prompt tokens and 18.4% completion tokens with +1.14 task performance relative to comparison methods. Llama3 ablation average: vanilla MAS 65.72; learned node-only 66.83; learned edge-only 66.06; single-learning node+edge 66.47; full two-stage AgentDropout 68.70. Random node/edge dropout yields 66.69/66.13, below learned joint pruning, so shorter reasoning alone does not explain the gain.

Dropout-rate sweep gives a negative boundary: rate 0.2 => avg 68.70, 3.3M prompt / 839K completion tokens; rate 0.8 => avg 66.01, 856K / 230K tokens. Stronger pruning lowers cost but eventually lowers accuracy.

Mechanism hypothesis: optimize pruning intensity against task sensitivity rather than maximizing elimination.

### C9 — Diversity-preserving MAP-Elites matters in adversarial program evolution; static specialists overfit
Primary: Akarsh Kumar et al., *Digital Red Queen: Adversarial Program Evolution in Core War with LLMs*, 2026. https://pub.sakana.ai/drq/

DRQ uses MAP-Elites within each round with behavioral descriptors spawned threads and memory coverage. Replacing it with a single-cell archive removes diversity preservation and significantly worsens optimization, especially later rounds; the accessible primary page does not expose a numeric delta, so this is recorded qualitatively only. Static one-opponent optimization generates specialists that collectively defeat/tie 283/294 human warriors (96.3%), but one evolved specialist defeats/ties only 27.9% on average. Growing opponent history helps robustness: increasing history length from K=1 to K=10 reduces three-warrior cyclic dynamics by 77% across runs.

Mechanism hypothesis: diversify not only candidate solutions but also adversaries/tests; historical opponent populations can prevent cyclic overfit.

### C10 — Heterogeneous mutation models beat homogeneous parallelism at fixed total LLM-call budget
Primary: John Donaghy, Shikhar Rastogi, *DEI: Diversity in Evolutionary Inference for Quality-Diversity Search*, arXiv:2605.27130, 2026-05-26. https://arxiv.org/abs/2605.27130

A four-node heterogeneous ensemble (GPT-5.4-mini, Claude Sonnet 4.6, GPT-5.2, Claude Haiku 4.5) obtains merged QD-score 45.90 vs 20.46 for single-node search at equal total LLM-call budget (+124%), with archive coverage 80.6% vs 63.0% (+28%). The authors also report homogeneous merged QD-score 29.85 and coverage 59.0%, below the heterogeneous ensemble. Example held-out generality: Claude Haiku 4.5 improves from 0.538±0.063 in homogeneous ensemble to 0.700±0.050 in diverse ensemble.

Open confound: Core War only, and model-family heterogeneity is not decomposed from potentially cheaper prompt/role/tool/sampling diversity. Diminishing returns beyond four models are also unresolved.

## Cross-source synthesis update

- Raw N is increasingly unsupported as the right control variable. Effective independent channels, adaptive role/edge selection and task-conditioned topology have stronger evidence.
- QD is conditional: PartEvo/DRQ show value from niches/behavioral stepping stones, while Heuresis shows MAP-Elites can be best on one landscape and worst on another under the same agent loop.
- Heterogeneity gains survive fixed-budget comparisons in two distinct directions: reasoning-channel diversity (prior checkpoint) and evolutionary QD model diversity (DEI). The causal axis of diversity remains unresolved.
- Strong external verification is not optional for autonomous evolution: Heuresis found reward-hacking fabrications, while evaluator-rich systems such as CORAL derive value from local tests.
- A plausible next design hypothesis is dynamic resource allocation over diverse lineages: retain distinct niches/priors, measure marginal gain/cost, prune correlated or stagnant lineages, and selectively migrate only high-value elites. This is synthesis, not yet a directly proven end-to-end recipe.

## Rejected / downgraded claims

- “More agents is better” — rejected; AGP and prior scaling evidence show narrow/task-dependent optima.
- “Maximum pruning is better” — rejected; AgentDropout has a measurable accuracy–token trade-off.
- “MAP-Elites/QD is universally better than greedy” — rejected; Heuresis gives a direct counterexample.
- DRQ MAP-Elites ablation is qualitative only because the accessible page lacks the numeric delta.
- DEI does not yet prove model family diversity itself is necessary; cheaper within-model diversity was not causally isolated.

## Frontier queue — keep nonempty

1. Heterogeneity decomposition under fixed budget: model vs prompt vs role vs tool/sampling diversity, with pairwise/interaction ablations and a negative case.
2. Adaptive-N beyond offline graph training: uncertainty/failure-conditioned test-time controllers; held-out and long-horizon evidence.
3. Population replacement/reseeding/migration: stagnation detection, migration frequency, archive reset, island spawn/kill and lineage-replacement ablations.
4. Verifier reliability threshold: judge-noise sweeps, objective-vs-LLM graders, reward-hacking sensitivity.
5. QD descriptor design: explicit behavior descriptors vs embeddings vs CVT-MAP-Elites vs random partitions vs single-cell, equal evaluation budgets.
6. Opponent/test population evolution: candidate diversity vs adversary/test diversity under matched compute.
7. Coordination cost curves on long-horizon tool/interactive tasks.
8. Isolated lineages vs selective elite migration vs shared summaries vs fully shared memory.
9. AgentDropoutV2 component ablations: rectify vs reject vs indicator retrieval vs fallback; fixed vs dynamic MAS.
10. EvoMAS/DEI reproducibility with open models and objective evaluators.

## Persistence / reconciliation note

An in-place update of `STATE.md` encountered a write conflict. To avoid overwriting concurrent clean-state activity, this run did not force the mutation; all new evidence and continuation are durably checkpointed in this separate file inside the same permitted clean directory. A future run should read both `STATE.md` and this checkpoint, then reconcile them using a fresh current blob before replacing `STATE.md`.

## Exact next action

Start with frontier 1: find fixed-budget factorial/ablation studies that separate **model vs prompt vs role/tool heterogeneity** while holding agent count and total calls/tokens constant; extract one quantitative causal decomposition and one negative result where added diversity fails. Then execute frontier 3 by inspecting island/migration/reseeding work for controlled migration-frequency or archive-reset ablations. Before the next checkpoint, take at least one action on frontier 4 by locating a verifier/judge-noise sweep or reward-hacking sensitivity experiment.