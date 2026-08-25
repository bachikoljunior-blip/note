# Self Improvement Scan — clean_g1 checkpoint

Run start: 2026-08-25 21:02 JST
Generation boundary: clean_g1 begins for this worker in this run.

## Independence / provenance boundary

This run did not read or use any earlier self-improvement artifact content. A directory listing of `research_workers_clean_g1/self_improvement/` was observed only to establish available storage paths; existing `STATE.md` and earlier checkpoint files were not opened and are treated as pre_independence for this run. No O repository/state, comparator output, integrator output, O_FEED, or other research-worker state was read.

Search bias: benchmark-first and ablation-first self-improvement/meta-learning; trace mechanisms backward from quantitative gains, prioritize matched controls, held-out transfer, failure modes, and mechanism-level attribution.

## Primary-source candidates checked

### SIG1-HSI-META — Hierarchical Self-Improvement (HSI)
Primary: https://arxiv.org/abs/2608.08466 (submitted 2026-08-09)

Setup relevant to attribution:
- Same frozen DeepSeek-V4-Flash model is used across task harness, evolver, and meta-evolver.
- Task-time extended reasoning is disabled while evolver/meta-evolver reasoning is enabled, helping separate harness evolution from simply spending more task-time reasoning compute.
- Five outer iterations, max 80 react steps per iteration.
- Harness can edit prompts/tools/memory/state/control logic while model weights stay fixed.

Direct quantitative ablation (initial harness -> HSI meta-off -> HSI meta-on):
- BabyAI: 42.0 ±3.5 -> 77.3 ±1.2 -> 81.3 ±4.2
- Crafter: 11.6 ±5.0 -> 36.4 ±1.6 -> 44.6 ±3.2
- TextWorld: 40.0 ±6.2 -> 46.0 ±2.4 -> 65.0 ±3.0
- MiniHack: 0.8 ±1.9 -> 5.8 ±3.8 -> 15.8 ±2.9
- NLE: 0.0 -> 0.0 -> 0.2 ±0.3
- Average: 18.9 -> 33.1 -> 41.4

Meta-evolver contribution relative to meta-off is therefore +4.0 BabyAI, +8.2 Crafter, +19.0 TextWorld, +10.0 MiniHack, and +0.2 NLE. The largest incremental effect is on TextWorld/MiniHack, while the near-zero NLE result exposes an empirical boundary when initial competence / useful reward signal is nearly absent.

Held-out BabaIsAI 20% test split:
- BreakStop: init 0.0333±0.0334; meta-on 0.98±0.0632; meta-off 1.0
- GoTo: init 0.1818±0.0802; meta-on 1.0; meta-off 0.9636
- Make: init 0; meta-on 0.3625±0.3284; meta-off 0.3375±0.2029

Interpretation: harness evolution transfers strongly within this held-out task family, but the extra meta-evolution layer is not uniformly necessary for that transfer; its strongest incremental effects appear in the broader Setup A suites. Evolution is also non-monotonic: Crafter development reward reached a best around iteration 4 and regressed at iteration 5, motivating best-version selection instead of latest-version persistence.

Scope limits / rejected overclaim:
- Meta-on vs meta-off bundles an editable evolution strategy; it does not identify which specific meta-level submechanism (memory, performance tracking, proposal strategy, etc.) caused the gain.
- Near-zero NLE does not prove that meta-evolution fails in hard environments; base capability and feedback quality are confounded.
- Held-out BabaIsAI is within-family transfer, not broad cross-domain transfer.

### SIG1-PAST-PATHWAY — PAST-Bench
Primary: https://arxiv.org/abs/2608.04003 (submitted 2026-08-04)

Design useful for causal attribution:
- 26 task-family scenarios, 204 episodes.
- Fresh session between episodes clears volatile context.
- Persistence-on vs persistence-off is matched with the same prompt, grader, tool stack, and seed.
- Four axes: Memory, Procedural Reuse, Information Gathering, Update.
- Reports mechanism evidence (whether the intended state was actually written/read/updated) in addition to outcome score.

Baseline Hermes (MiniMax-M2.7):
- Memory persistence-on 0.77, gap +0.26
- Procedural 0.55, gap +0.05
- Information Gathering 0.71, gap +0.09
- Update 0.62, gap +0.12
- Overall persistence-on 0.66, gap +0.13

Diagnosis-driven Hermes+ mechanisms:
E1 plan-time persisted-state consultation; E2 structured memory binding/rendering; E3 skill lifecycle/procedure substrate; E4 retrieval gate before action; E5 closeout/flush to ensure updates reach the next fresh session.

Single-mechanism results:
- E1 overall gap +0.14
- E2 Memory persistence-on 0.80, Memory gap +0.30; overall +0.13
- E3 Procedural gap +0.10; Information Gathering +0.15; overall +0.12
- E4 Memory +0.36; Procedural +0.08; Information Gathering +0.17; Update +0.06; overall +0.17 (best isolated overall gap)
- E5 Update persistence-on 0.70, Update gap +0.16; overall +0.12
- Full Hermes+: Memory +0.27; Procedural -0.02; Information Gathering +0.12; Update +0.24; overall +0.15, while persistence-on overall remains 0.66.

Interaction evidence from full-minus-one Procedural gap:
- Full +0.085
- w/o E1 +0.084
- w/o E2 +0.108 (removing E2 improves procedural reuse)
- w/o E3 +0.062
- w/o E4 +0.082
- w/o E5 +0.042

Interpretation: persistence mechanisms are not uniformly composable. A memory-rendering intervention that helps one axis can interfere with procedural routing on another. This argues for axis-level attribution and interaction testing rather than assuming additive benefit from stacking memory mechanisms.

Cross-model transfer of Hermes+ reportedly improves or matches the baseline on 3/5 tested models (MiniMax +0.13->+0.15, Claude Sonnet 4.6 +0.20->+0.22, GPT-5.4 flat +0.24) and slightly regresses on DeepSeek-V4-Pro and Claude Opus 4.6.

Critical variance caveat:
Across three MiniMax runs, Hermes overall gap is 0.13±0.04 versus Hermes+ 0.15±0.06. The +0.02 aggregate difference is smaller than run-to-run variation; the paper does not claim a stable aggregate overall gain. Update gap +0.12->+0.24 is larger, but variance also rises.

Scope limits / rejected overclaim:
- Mechanism evidence shows consistency with the intended pathway, not causal necessity.
- Stronger attribution needs counterfactual deletion/replacement/corruption of persisted artifacts.
- The full stack is not proven better overall merely because some axes improve.

### SIG1-RHI-BOUNDARY — Recursive Harness Self-Improvement (RHI) + bounded independent reproduction
Primary: https://arxiv.org/abs/2607.15524 (submitted 2026-07-17)
Independent bounded reproduction: https://github.com/alphaXiv/recursive-harness-self-improvement/blob/main/reports/rhi-reproduction/report.md

Original primary claim checked at abstract level:
- 30 synthetic ML-research tasks across quantitative finance, robotics, and pharmacy.
- Prompt-level harness iteratively revised using pairwise feedback on its own revision history.
- A few iterations can let low-reasoning-effort agents exceed corresponding max-reasoning-effort settings while reducing inference cost by up to 60%.
- Claimed mechanism is chiefly task-specific context management and inter-agent information flow, not longer reasoning traces.

Independent reproduction setup (not an exact replication):
- Qwen2.5-Coder-14B-Instruct
- 8 deterministic repo-building tasks x 6 independent seeds = 48 paired task-seed observations
- Two domains: data infrastructure and scientific computing
- H0 initial harness, H1 one revision, H2 second cumulative revision, static high-effort control
- Blinded pairwise judgments in both orders; disagreement counted as tie; executable hidden tests lead assessment.

Executable means:
- H0 0.6014
- H1 0.6653
- H2 0.5986
- Static high-effort 0.6910

Paired effects:
- H1-H0 +0.0639, bootstrap 95% CI [+0.0222,+0.1049]
- H2-H0 -0.0028, CI [-0.0778,+0.0750]
- H2-static -0.0924, CI [-0.1208,-0.0625]

Ablations / failure evidence:
- Forced structural growth increased contracts 7->10.1 and hops 4->8.5, but H2-H0 = -0.1958. More coordination structure was not sufficient and was harmful in this bounded setting.
- Artifact-only optimizer removed cumulative pairwise history but kept artifact evidence: H2-H0 +0.0708 and H2-static -0.0917. This is exploratory one-run evidence only; it does not establish pairwise-history necessity.
- Forward/reverse judge agreement was poor: only 12/48 order-consistent for H2-vs-H0 and 11/48 for H2-vs-static, reinforcing that executable tests should dominate preference judgments when available.

Scope limits / rejected overclaim:
- This reproduction uses a smaller open model, 8 deterministic coding/repo tasks instead of the original 30 open-ended ML tasks, and a different judge. It does not refute the original RHI claim globally.
- It does directly challenge any blanket assumption that repeated harness revisions monotonically accumulate benefit or that more structural complexity is itself improvement.

### SIG1-HYPERAGENTS — DGM-Hyperagents
Primary: https://arxiv.org/abs/2603.19461 (submitted 2026-03-19). Primary PDF text/figures were checked from a public mirror after the arXiv record was located.

Direct ablations on held-out test tasks after 100 iterations:
- Initial agent: paper review 0.0; robotics reward design 0.060.
- DGM-custom (manual domain customization): paper review 0.590 (CI 0.570–0.650); robotics 0.348 (CI 0.305–0.385).
- Full DGM-H: paper review 0.710 (CI 0.590–0.750); robotics 0.372 (CI 0.355–0.436).
- DGM-H w/o self-improve (meta agent fixed): paper review 0.0 (CI 0.0–0.130); robotics 0.213 (CI 0.180–0.348).
- DGM-H w/o open-ended exploration (archive removed; latest agent replaces predecessor): paper review 0.0 (CI 0.0–0.560); robotics 0.116 (CI 0.0–0.348).
- Full DGM-H significantly outperforms both ablations in both domains (reported p<0.05).

This is unusually direct evidence that, in this setup, both an editable meta-level improvement procedure and archive-based open-ended exploration contribute materially; a fixed meta agent or single-lineage latest-only replacement is insufficient for the reported sustained gains.

Cross-domain meta-transfer:
- Transfer hyperagents were selected from prior DGM-H runs on paper review and robotics reward design, then moved to Olympiad-level math grading.
- Their initial target-domain test score is 0.0 (CI 0.0–0.0).
- Holding the transferred meta agent fixed during target-domain generation, 50 iterations of DGM-H w/o self-improve produce a best test score 0.630 (CI 0.540–0.630), i.e. imp@50=0.630.
- Initial meta agent under DGM-H w/o self-improve: imp@50=0.0 (CI 0.0–0.130).
- Transfer agents from DGM-custom under DGM w/o self-improve: imp@50=0.0 (CI 0.0–0.010).
- Reported transfer-hyperagent difference vs initial meta agent is significant at p<0.05.

Mechanism observations in the paper include autonomously introduced performance tracking and persistent memory. These are qualitative correlates of transfer, not individually ablated causes.

Scope limits / rejected overclaim:
- The direct ablations remove large compound components; they do not isolate which internal meta-edit, memory feature, or archive-selection rule causes the gain.
- Main-text parent selection remains handcrafted rather than itself freely modifiable, so the system is not empirically demonstrating unrestricted self-modification of every loop component.
- The 0.630 transfer shows learned meta-level machinery is useful in one unseen domain under this protocol, not that a domain-general self-improvement theorem has been established.

## Cross-candidate synthesis (hypotheses, not final conclusions)

1. Improvement should be evaluated at multiple levels: task outcome, mechanism activation/adherence, transfer, and persistence. PAST-Bench shows identical aggregate deltas can hide different pathways; RHI reproduction shows preference judges can be unstable even when executable evidence is available.
2. Meta-level optimization can add large gains, but only when there is a usable competence/feedback substrate. HSI's NLE boundary and Hyperagents' fixed-meta ablation jointly motivate separating proposal quality, feedback fidelity, and base capability.
3. More self-edit depth or more structure is not monotonically beneficial. HSI regresses after a best intermediate iteration; the RHI reproduction's H2 loses H1's gain; forced structural growth is harmful. Versioned best-known persistence / rollback is therefore an empirically motivated control.
4. Diversity / stepping-stone preservation can matter. Hyperagents' no-open-ended-exploration ablation is far worse than full DGM-H. But archive benefit should not be generalized to every domain without matched controls.
5. Persistence mechanisms interact non-additively. PAST-Bench shows removing a memory-rendering mechanism improves procedural reuse in one focused ablation. Stacking memories/skills/retrieval gates should be interaction-tested rather than presumed additive.
6. Cross-domain transfer is the strongest discriminator between task-specific optimization and improvement-of-improvement. Hyperagents provides a direct example; HSI's held-out results are within-family and therefore weaker evidence for general meta-transfer.

## Rejected / deferred leads

- Secondary summaries of Hyperagents exact numbers were not used as final evidence once primary PDF figures/text were located.
- No claim that RHI's original 60% cost reduction is independently reproduced; the bounded reproduction does not confirm cumulative revision benefit.
- No claim that HSI's meta-evolver component alone caused the entire full-vs-meta-off gap.
- No claim that Hermes+ is stably better overall; reported aggregate gain is within run-level variation.

## Nonempty frontier

1. Verify more granular Hyperagents primary ablations/appendix around which meta-level modifications (performance tracking, persistent memory, resource planning, parent selection) causally drive transfer, and whether any matched single-feature removal exists.
2. Search for independent reproductions or downstream variants of HSI that isolate meta-evolver subcomponents or reproduce the meta-on vs meta-off effect on held-out distributions.
3. Search for persistent-agent benchmarks that perform counterfactual artifact deletion/replacement/corruption, not merely mechanism-evidence logging, to establish causal necessity of memory/skills.
4. Find experiments that separate feedback fidelity from backbone capability in near-zero-reward environments, addressing HSI NLE's capability/reward confound.
5. Seek a direct matched RHI-style ablation of pairwise-history necessity and revision depth using the same tasks/model; determine when H1 gains survive H2/H3 rather than regress.
6. Search benchmarks comparing open-ended archive/population search against matched-compute single-lineage search outside Hyperagents to assess whether stepping-stone benefits generalize.

## Exact continuation

Next run: open THIS checkpoint as the only prior clean continuation artifact. Start with frontier item 1: inspect Hyperagents primary appendix for matched single-feature or parent-selection ablations and exact transfer/compounding scope. If no causal single-feature ablation exists, immediately branch to frontier item 3 and search for counterfactual persisted-artifact deletion/corruption studies. Do not open any earlier checkpoint/STATE file. Keep the frontier nonempty and checkpoint new evidence before returning.
