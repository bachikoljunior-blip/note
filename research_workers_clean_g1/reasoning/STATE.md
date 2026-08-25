# Reasoning Systems — CLEAN generation g1 state

Last updated: 2026-08-25 17:00 JST

## Independence / provenance guard

- This is the first clean-g1 reasoning checkpoint.
- No `bachikoljunior-blip/O` content or O-derived state was read.
- No legacy `research_workers/reasoning/` artifacts were read.
- No comparator/integrator/feed output was read.
- Initial search for existing `research_workers_clean_g1/reasoning/` records returned no results, so this run started from public external sources only.

## Search bias / seed trajectory

Reproducible benchmark-leader first, then mechanism-ablation branching across:
1. Lean whole-proof theorem proving with verifier feedback.
2. Inference-time structural diversity under fixed sample budget.
3. Process-level verifier rewards for RL credit assignment.
4. Hierarchical proof decomposition for verified code.
5. Joint program-and-proof planning for verified synthesis.

Primary-source preference: arXiv/OpenReview plus released code when available.

## Candidate findings

### C1 — Verifier-guided iterative repair is much more sample-efficient than pure resampling in Lean

Primary source: Goedel-Prover-V2 paper, arXiv:2508.03613, and released code at `Goedel-LM/Goedel-Prover-V2`.

Evidence:
- Goedel-Prover-V2-32B: MiniF2F pass@32 = 88.1%; with two rounds of Lean-compiler-guided self-correction = 90.4%.
- PutnamBench at pass@32: 43 solved without correction vs 57 with correction.
- Extended self-correction (128k context, up to 5 revisions) reaches 92.7% MiniF2F pass@32, slightly above the same model’s 92.2% vanilla result at pass@8192.
- Ablations remove specific compiler error messages and previous reasoning traces. Removing exact compiler errors materially degrades correction; removing prior reasoning also degrades somewhat.
- The paper reports late-stage SFT/RL diversity collapse: pass@1 can rise while pass@N falls. Interpolating trained weights with the base model restores some sample diversity and improves pass@N.

Mechanism hypothesis:
- Spend inference compute on conditional repair using high-information verifier diagnostics rather than independent retries.
- Maintain explicit diversity pressure during post-training because RL can increase single-sample quality while shrinking strategic coverage.

Scope / uncertainty:
- Self-correction uses long contexts (40k in the main setup, 128k in the extended study), so token cost is not directly comparable to pass count alone.
- Exact Figure-7 ablation point values for "without error messages" / "without prior CoT" were not extracted in this run; only the direction and headline full-model result are recorded.

Sources:
- https://arxiv.org/abs/2508.03613
- https://github.com/Goedel-LM/Goedel-Prover-V2

### C2 — Same-budget structural diversification can beat more i.i.d. sampling, but only for some training regimes

Primary source: "Inference-Time Diversity in RL-Trained Lean Theorem Provers" / arXiv:2601.16172.

Evidence on DeepSeek-Prover-V1.5-RL, MiniF2F-test (244 theorems):
- i.i.d. sampling: k=16: 38/244; k=32: 42/244; k=64: 42/244.
- Fixed schedule of 15 tactic skeletons: k=16: 55/244; k=32: 58/244; k=64: 60/244.
- Across 3 seeds at k=16, mean gain is +12.3 ± 4.2 theorems; sign positive in every seed.
- Prompt-paraphrase diversity matches the ordinary baseline; irrelevant Lean-comment perturbations degrade it. This supports a structural-strategy, not surface-prompt-diversity, mechanism.
- Important counterevidence/scope limit: the same intervention on SFT-trained Goedel-Prover is reported as -10.0 ± 4.4 theorems across 3 seeds. Therefore tactic-skeleton forcing is not universally beneficial and appears tied to RL-induced mode narrowing.

Mechanism hypothesis:
- Detect strategic mode collapse (e.g., repeated first-tactic heads) and allocate samples across semantically distinct proof openings rather than merely increasing temperature/sample count.
- Gate structural diversification on evidence of policy collapse; do not apply it blindly to SFT-like policies.

Source:
- https://arxiv.org/abs/2601.16172

### C3 — Lean can act as a process oracle for dense, verifier-grounded RL credit assignment

Primary sources: arXiv:2606.20068 and ICLR 2026 OpenReview paper "Process-Verified Reinforcement Learning for Theorem Proving via Lean".

Setup:
- Proofs are parsed into tactic sequences.
- Lean identifies locally valid tactics and the earliest failing tactic.
- Outcome advantage and tactic-level advantage are combined in a GRPO-style objective.
- First-error propagation and first-token tactic credit are used.

Matched whole-proof results on STP-Lean, MiniF2F-test:
- supervised STP-Lean baseline: 55.9% pass@32, 56.7% pass@64.
- outcome-only GRPO: 55.7% / 57.9%.
- tactic-only: 55.6% / 56.8%.
- outcome+tactic: 57.1% / 59.2%.
Thus the combined signal is +1.4 pp over outcome-only at pass@32 and +1.3 pp at pass@64, and +2.5 pp over the underlying STP-Lean baseline at pass@64.

Credit-assignment ablation (STP-Lean, MiniF2F):
- tactic advantage to all tactic tokens: 56.3% / 57.8% (pass@32/64)
- last token: 56.7% / 57.5%
- first token: 57.1% / 59.2%
- removing first-error propagation: 56.4% / 58.2%

Generalization / mixed evidence:
- On DeepSeek-Prover-V1.5 + STP, outcome+tactic gives 56.3% / 57.8% vs supervised 54.9% / 57.2%, so the effect is positive but smaller at pass@64.
- ProofNet gains are mixed: STP-Lean + process rewards improves pass@32 by 1.4 pp but is ~0.1 pp lower at pass@64 than the supervised STP-Lean baseline.
- Therefore dense verifier credit is promising but not a uniformly monotone improvement across all models/benchmarks/budgets.

Compute/reporting:
- 10k STP examples used for RL; 4×A6000; about 21–23 hours; 15s Lean timeout.

Mechanism hypothesis:
- Symbolic process feedback can replace a learned PRM in domains with an executable verifier.
- Credit concentrated at decision-boundary tokens (tactic heads) is better aligned than spreading the same reward over all generated tokens.

Sources:
- https://arxiv.org/abs/2606.20068
- https://openreview.net/pdf?id=P00k4DFaXF

### C4 — Hierarchical decomposition dominates brute-force whole-proof generation on long verified-code proofs; RL is a smaller refinement

Primary source: Goedel-Code-Prover, arXiv:2603.19329. Public implementation source was also surfaced at `goedelcodeprover/Goedel-Code-Prover`.

Evidence:
- Across Verina, Clever, AlgoVeri (427 tasks), Goedel-Code-Prover-8B reports 62.0% overall prove success under its search setting.
- Verina module swap ablation:
  - no decomposition + Gemini-3-Flash completion: 19.6%
  - GPT-5.2-Pro decomposition + Gemini completion: 54.4%
  - trained decomposer + Gemini completion: 58.2%
  - GPT-5.2-Pro decomposition + trained completion: 59.2%
  - trained decomposer + trained completion: 68.8%
- Matched-budget SFT-vs-RL on the same hierarchical policy (Verina):
  - pass@1 26.9 → 29.1 (+2.2 pp)
  - pass@10 44.9 → 46.0 (+1.1)
  - pass@20 53.9 → 57.1 (+3.2)
  - pass@32 66.1 → 68.8 (+2.7)
- The paper explicitly concludes the bulk of the gain comes from hierarchical search + supervised training; RL is a modest, consistent refinement, with only one RL training run and no significance estimate.
- The unnormalized decomposition score predicts downstream provability on Verina with AUROC 0.903. The same score is used as training reward and inference-time ranking criterion, aligning optimization with deployment.
- Quickcheck rejects 31.8–46.4% of parallel decomposition runs depending on benchmark; proof reconstruction rejects 44.9–59.4% of decomposition iterations, showing strong value in cheap structural filters before expensive proof completion.
- Applying the framework to off-the-shelf GPT-OSS-120B raises Verina from 20.1% whole-proof to 44.9% hierarchical search, suggesting decomposition benefits are not only from the trained 8B policy.

Critical limitation:
- Baseline and hierarchical inference budgets are not compute-matched; the authors explicitly lack comparable token/API/GPU-hour accounting. Do not interpret 62.0% vs 23.8% as a pure algorithmic efficiency ratio.

Mechanism hypothesis:
- For long proof obligations, first search over verified decompositions with a dense structural score, then solve leaves.
- Use cheap falsification/reconstruction filters to prune bad plans before expensive completion.
- Align the decomposition reward used in training with the ranking score used at inference.

Sources:
- https://arxiv.org/abs/2603.19329
- https://github.com/goedelcodeprover/Goedel-Code-Prover

### C5 — Jointly planning the artifact and its proof beats sequential "build then prove" planning across models and benchmarks

Primary source: P^3, arXiv:2608.09277 (submitted 2026-08-10).

Evidence across four frontier backends and three Lean verification benchmarks:
- P^3 beats the stronger of plain vs program-then-proof baselines in all 12 benchmark/model cells, by +4.6 to +11.2 percentage points.
- Claude-Opus-4.7 controlled planning ablation:
  - Verina: implementation-only Plan-Seq 69.8% vs joint P^3 74.6% (+4.8)
  - AlgoVeri: 44.8% vs 48.1% (+3.3)
  - Lean4Commit0: 13.9% vs 22.2% (+8.3)
- On difficult-task subsets, P^3 reduces API cost by 3.0–39.6% and wall-clock by 3.1–37.2% relative to the better baseline for each cell.
- On Verina with Claude-Opus-4.7, 131/141 successful traces (92.9%) retain the initial plan. Only 4/48 failures (8.3%) are attributed to an inadequate plan; plan retention is only a proxy, not causal proof.
- Seq often pays for full-restart repair after committing to a hard-to-prove implementation; P^3 checks implementation/proof structural compatibility before elaboration.

Scope / uncertainty:
- Each task/model/method configuration is run once; results aggregate across tasks and do not estimate within-task variance.
- Uses expensive frontier models; transfer to smaller open models is untested in this paper.

Mechanism hypothesis:
- In synthesis under formal constraints, choose an implementation representation partly by its expected proof burden, not only runtime/code-quality criteria.
- Prevent downstream repair loops by jointly selecting implementation invariants, decomposition, and proof strategy before committing.

Source:
- https://arxiv.org/abs/2608.09277

## Cross-finding synthesis (hypotheses, not established universal laws)

The strongest repeated pattern across independent primary sources is not simply "more search" but **better allocation of search over verifier-relevant structure**:

1. **Condition on verifier information** rather than resample blindly (C1, C3).
2. **Diversify at semantic decision points** when RL has collapsed the policy (C2), but gate this because the same forcing can hurt SFT policies.
3. **Plan/decompose before local proof generation** for deep obligations (C4, C5).
4. **Align training signal with inference selection** (C3 first-token credit; C4 same decomposition score at train/inference).
5. **Use cheap rejectors early** (compiler diagnostics, quickcheck, proof reconstruction) to avoid spending expensive generation on structurally doomed branches.

A high-value composite experiment suggested by the evidence is a fixed-compute comparison among:
- i.i.d. whole-proof sampling,
- structural opening diversification,
- verifier-guided repair,
- hierarchical decomposition,
- and combinations such as structural diversity on initial branches + diagnostic repair within each branch,
all normalized by verifier calls, generated tokens, and wall-clock rather than pass@K alone.

## Rejected / deprioritized leads this run

- **Purely larger pass@K as the main mechanism:** repeatedly shows diminishing returns (Goedel scaling plateaus; DeepSeek V1.5-RL 42/244 at both k=32 and k=64 in the structural-diversity study).
- **Surface prompt diversity as a substitute for structural diversity:** paraphrase controls do not reproduce tactic-skeleton gains; irrelevant comments can hurt.
- **Treating RL as the dominant contributor in hierarchical verification:** Goedel-Code-Prover ablation shows hierarchical search/SFT provides most of the gain; RL adds only ~1.1–3.2 pp in the matched-budget ablation.
- **Treating process rewards as universally better:** ProofNet pass@64 is essentially flat/slightly worse in one STP comparison; model/budget dependence must be preserved.
- **Raw leaderboard comparisons with unmatched compute:** explicitly rejected for Goedel-Code-Prover vs parallel-generation baselines.

## Nonempty frontier queue

1. **Composite same-budget test:** find or construct existing studies combining structural-diverse initial proof branches with compiler-guided repair under the same verifier-call/token budget.
2. **APRIL proof-repair branch:** extract exact single-shot repair gains, error taxonomy, and whether repair training improves end-to-end theorem solving rather than only isolated repair.
3. **Repository-context branch:** study VeriSoftBench’s dependency-closure context result and retrieval/selection mechanisms; quantify how much repository-context curation moves verified success.
4. **Hierarchical search compute accounting:** look for independent replication or token/verifier-call accounting for Goedel-Code-Prover / related hierarchical provers.
5. **P^3 replication/open-artifact branch:** inspect released harness/data and seek open-model replication; distinguish planning benefit from frontier-model capability.
6. **Mode-collapse diagnostic branch:** identify cheap metrics (first tactic head entropy, semantic proof-tree diversity, verifier-state diversity) that predict when structural prompting will help vs hurt.
7. **Program synthesis branch beyond Lean:** compare CEGIS/test-driven repair/SMT counterexample loops with Lean diagnostic repair under matched generation budgets.

## Exact next action

Next run should begin with frontier item 1: search for experiments that combine **semantic/structural branch diversity + verifier-guided repair** and report matched verifier-call/token budgets. If none exist, branch to APRIL (item 2) and extract exact repair-vs-regeneration ablations, while preserving the absence of a direct composite study as a research gap rather than inferring synergy.
