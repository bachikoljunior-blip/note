# Multi-Agent Scan — clean_g1 state

Updated: 2026-08-25T16:58:23+09:00
Generation: clean_g1
Independence boundary: this worker used only public external sources plus this clean directory. It did not read O, O-derived state, comparator/integrator outputs, other workers, or legacy research_workers/multi_agent/.

## Search bias / seed trajectory

Comparative-study-first search on multi-agent scaling and architecture-task matching, followed by evolutionary / quality-diversity branches. Initial branches: (1) fixed-compute multi-agent scaling, (2) heterogeneous-vs-homogeneous agent scaling, (3) autonomous multi-agent evolution with persistent memory, (4) niching / partitioned evolutionary search in language/program spaces, (5) evolutionary generation of multi-agent system configurations.

## Candidate evidence records

### C1 — Scale diversity/effective channels, not raw homogeneous agent count
Primary source: Yingxuan Yang et al., *Understanding Agent Scaling in LLM-Based Multi-Agent Systems via Diversity*, arXiv:2602.03794, 2026-02-03. https://arxiv.org/abs/2602.03794
Evidence: The paper reports that homogeneous scaling saturates because outputs are correlated, while heterogeneous agents provide complementary channels; empirically, 2 diverse agents can match or exceed 16 homogeneous agents. It introduces an effective-channel metric K* intended to quantify effective independent channels without labels.
Scope: reasoning-style MAS configurations studied by the paper; do not generalize to all interactive agent systems without matched tests.
Mechanism hypothesis: maximize effective information-channel diversity (model/prompt/tool/role heterogeneity), not nominal N.

### C2 — Architecture-task matching dominates generic multi-agent scaling
Primary source: Yubin Kim et al., *Towards a Science of Scaling Agent Systems*, arXiv:2512.08296v3, revised 2026-04-08. https://arxiv.org/abs/2512.08296
Evidence: controlled evaluation over 260 configurations, six benchmarks, five architectures, three LLM families. Relative performance versus single-agent ranges from +80.8% on decomposable financial reasoning to -70.0% on sequential planning. Their learned framework identifies the best-performing architecture for 87% of held-out configurations. Reported patterns include capability saturation, multi-agent overhead on tool-heavy tasks, and more error propagation without centralized verification.
Scope: six evaluated agentic benchmarks and tested architectures; not evidence that centralized coordination is universally best.
Mechanism hypothesis: route tasks to Independent/Centralized/Decentralized/Hybrid topology based on measurable decomposability, sequentiality, tool intensity, and baseline capability.

### C3 — Autonomous multi-agent evolution can beat single-agent scaling even at matched larger compute
Primary source: Ao Qu et al., *CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery*, arXiv:2604.01658v2. https://arxiv.org/html/2604.01658v2
Evidence: CORAL reports SOTA on 8 of 11 tasks in one summary, 2.5x higher improvement rate and 10x fewer evaluations than fixed evolutionary search; a separate abstract summary reports SOTA on 10 tasks and 3–10x higher improvement rates depending on comparison/task. On kernel engineering, four co-evolving agents improve 1363 to 1103 cycles (~20%). Four agents find solutions a single autonomous agent does not find even with 4x compute. Ablation: knowledge accumulation (1-agent) kernel 1350 vs 1601 without knowledge; co-evolution (4-agent) kernel 1103 vs independent-best 1180, polyominoes 84.2 vs 80.8, transaction scheduling 4694 vs 4629. Trajectory analysis associates local verification and knowledge reuse with improvement; on kernel engineering, 57% of attempts used local test and 47% of tested attempts improved, while knowledge-access attempts improved 55% of the time.
Scope: open-ended mathematical/algorithmic/systems optimization with explicit evaluators; shared-memory collaboration is part of the tested mechanism and may not transfer to settings requiring strict worker independence.
Mechanism hypothesis: for evaluator-rich open-ended search, persistent knowledge + asynchronous co-evolution + local verification can outperform simply giving one lineage more compute.

### C4 — Niching improves LLM-assisted evolutionary search, but over-partitioning hurts
Primary source: Qinglong Hu, Qingfu Zhang, *Partition to Evolve: Niching-enhanced Evolution with LLMs for Automated Algorithm Discovery*, NeurIPS 2025. Proceedings: https://proceedings.neurips.cc/paper_files/paper/2025/hash/e389b15166cf98966ba058965a8c17e3-Abstract-Conference.html ; full paper/OpenReview PDF: https://openreview.net/pdf?id=OEawM2coNT
Evidence: PartEvo uses feature-assisted niches and niche-local/global operators. With population N=16, reported ablation across K={1,2,4,6} finds K=4 best overall; K=1 under-explores and K=6 over-disperses resources. On P4, objective was 13418.7 (K=1), 10572.0 (K=2), 4539.1 (K=4), 12427.2 (K=6), where lower is better. Removing EC-inspired operators produced 451.31% performance degradation; removing prompt-centric operators 553.74%; retaining only basic crossover/mutation degraded 2509.76% relative to full PartEvo. Feature-guided niches outperform random partitioning strongly on several benchmarks. The NeurIPS abstract reports up to 90.1% improvement over widely used baselines on resource scheduling tasks.
Scope: automated algorithm discovery/meta-heuristic design on the paper's four benchmarks; K=4 for N=16 is empirical, not a universal ratio.
Mechanism hypothesis: preserve multiple semantically/structurally distinct niches and allocate enough local sampling per niche; adapt niche granularity rather than maximizing niches.

### C5 — Evolve the MAS configuration itself; accumulated configuration pools and memory add complementary gains
Primary source: *Evolutionary Generation of Multi-Agent Systems (EvoMAS)*, arXiv:2602.06511v3. https://arxiv.org/html/2602.06511v3
Evidence: EvoMAS evolves structured MAS configurations via feedback-conditioned mutation/crossover and experience memory. It reports +10.5 points over EvoAgent on BBEH and +7.1 on WorkBench; automatic model selection reaches 58.7% BBEH and 48.9% WorkBench. On SWE-Bench-Verified it reaches 79.1% with Claude-4.5-Sonnet in the reported setup. Zero-shot/no-accumulation ablation on BBEH-Mini: Single Agent 36.6, Peer Review 39.8, EvoMAS no pool/no memory 40.4, memory only 43.7, pool only 42.6, full 49.1. Population grows rapidly then plateaus (3→22 configs over 500 SWE-Bench queries; 34 configs over 460 BBEH-Mini queries), suggesting saturation-driven archive growth. Judge ablation reports >90% agreement across judges; replacing Claude-4-Sonnet judge with Qwen3-235B reduces final accuracy only ~1.4–1.8pp.
Scope: BBEH, WorkBench, SWE-Bench family and the system's tested execution interfaces; some metrics use LLM-as-judge rewards, though structural failure signals are also used.
Mechanism hypothesis: treat role topology/model/tool assignments as an evolvable population, with separate reusable configuration pool and experience memory.

## Cross-source synthesis (not a comparator judgment)

1. Raw agent count is a weak control variable; effective independent channels and topology-task fit are stronger candidates.
2. Search benefits from diversity preservation (heterogeneous agents, niches, configuration populations), but every source showing gains also shows saturation/overhead: homogeneous N saturates; mismatched MAS can lose up to 70%; PartEvo over-partitioning degrades; EvoMAS archive growth plateaus.
3. Explicit evaluators/local tests are recurrent enabling mechanisms in open-ended evolution. CORAL and EvoMAS both separate or exploit evaluation feedback rather than relying only on peer persuasion.
4. A plausible transferable design is adaptive population allocation: maintain diverse lineages/configurations, estimate marginal information/improvement per lineage, increase resources only where marginal gain remains positive, and collapse/replace correlated or stagnant niches.

## Rejected / downgraded leads

- Generic multi-agent debate papers without matched-compute or strong ablation were deprioritized because debate gains can conflate extra tokens with architecture.
- Survey-only sources were not used as primary evidence.
- PartEvo's exact K=4 optimum is not promoted as a universal rule; it is recorded only as N=16 / tested-benchmark evidence.
- CORAL's shared persistent memory is not assumed safe/appropriate for independent exploration workers; only the underlying tested mechanism is recorded.
- Claims of universal multi-agent superiority are rejected by the strong negative results in task-topology scaling studies.

## Frontier queue (must remain nonempty)

1. Adaptive-N / adaptive-topology controllers: find controlled evidence where agent count or topology is selected dynamically from task uncertainty/decomposability and compare against fixed-N matched-compute baselines.
2. Quality-diversity archive design: compare MAP-Elites/CVT-MAP-Elites/island models/niching under equal evaluator and LLM budgets; identify when explicit behavior descriptors beat embedding similarity.
3. Population replacement/reseeding: look for ablations on stagnation detection, elite migration, archive resets, and lineage replacement in LLM evolutionary systems.
4. Heterogeneity decomposition: separate gains from model diversity vs prompt diversity vs tool diversity vs role diversity under fixed token/API budgets.
5. Coordination cost curves: quantify communication/synchronization overhead as N increases on long-horizon interactive tasks, not only QA/reasoning.
6. Independent-vs-shared-memory evolution: find matched studies that compare isolated lineages, shared notes, selective migration, and fully shared memory to identify contamination vs reuse trade-offs.
7. Verifier quality threshold: determine how reliable an evaluator must be before population search outperforms direct sampling; seek judge-noise sensitivity/causal ablations.
8. EvoMAS reproducibility branch: inspect public code/configuration representation and verify whether reported automatic model-selection gains can be reproduced with open models.

## Termination diagnostics

This run did not stop after the first useful result. After comparative multi-agent scaling evidence, it explicitly branched into quality-diversity/niching (PartEvo) and then evolutionary MAS-configuration search (EvoMAS), adding quantitative ablations from both branches. Runtime is the only reason to checkpoint now; research frontier remains nonempty.

## Exact next action

Next run: start with frontier item 1 using searches for adaptive agent-count/topology selection under matched compute; extract at least one primary controlled comparison and one failure/negative result. Then branch to item 2 (MAP-Elites/CVT-MAP-Elites/island/niching) and record archive-size or descriptor ablations under matched evaluation budgets before updating this state.