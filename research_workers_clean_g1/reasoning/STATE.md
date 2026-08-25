# Reasoning Systems — CLEAN generation g1 state

Last updated: 2026-08-25 18:15 JST

## Independence / provenance guard

- No `bachikoljunior-blip/O` content or O-derived state was read.
- No legacy `research_workers/reasoning/` artifacts were read.
- No comparator/integrator/feed output was read.
- Continuation used only this clean-g1 state plus public external sources.

## Search bias / seed trajectory

Reproducible benchmark-leader first, then mechanism-ablation branching across:
1. Lean whole-proof theorem proving with verifier feedback.
2. Inference-time structural diversity under fixed sample budget.
3. Process-level verifier rewards for RL credit assignment.
4. Hierarchical proof decomposition for verified code.
5. Joint program-and-proof planning for verified synthesis.
6. Learned refinement/search policies over compiler failure modes.
7. Repository-context selection for real-world verification.

Primary-source preference: arXiv/OpenReview plus released code/artifacts when available.

## Candidate findings

### C1 — Verifier-guided iterative repair is more sample-efficient than pure resampling in Lean

Primary source: Goedel-Prover-V2, arXiv:2508.03613.

Evidence:
- Goedel-Prover-V2-32B MiniF2F pass@32: 88.1%; with two rounds Lean-compiler-guided self-correction: 90.4%.
- PutnamBench pass@32: 43 solved without correction vs 57 with correction.
- Extended correction reaches 92.7% MiniF2F pass@32, slightly above vanilla 92.2% at pass@8192.
- Compiler-error ablations show exact verifier feedback is materially useful; prior reasoning context also helps.
- Late-stage SFT/RL can raise pass@1 while reducing pass@N diversity; checkpoint/model averaging restores some strategic coverage.

Scope:
- Long-context repair means pass count alone is not a token-cost comparison.

Source: https://arxiv.org/abs/2508.03613

### C2 — Same-budget structural diversification can beat more i.i.d. sampling, but it is training-regime dependent

Primary source: arXiv:2601.16172.

Evidence on DeepSeek-Prover-V1.5-RL / MiniF2F-test:
- i.i.d.: k=16 38/244; k=32 42/244; k=64 42/244.
- 15 tactic-skeleton schedule: k=16 55/244; k=32 58/244; k=64 60/244.
- Across 3 seeds at k=16: +12.3 ± 4.2 solved theorems; positive in every seed.
- Paraphrase diversity matches baseline; irrelevant comments degrade, supporting structural rather than surface-prompt diversity.
- Counterevidence: on SFT-trained Goedel-Prover the intervention is -10.0 ± 4.4 theorems across 3 seeds.

Mechanism hypothesis:
- Detect RL-induced strategic mode collapse and diversify proof openings only when collapse is present.

Source: https://arxiv.org/abs/2601.16172

### C3 — Lean can supply dense process-level RL credit, but gains are modest and benchmark-dependent

Primary sources: arXiv:2606.20068 and ICLR 2026 OpenReview `Process-Verified Reinforcement Learning for Theorem Proving via Lean`.

Evidence on STP-Lean / MiniF2F:
- supervised: 55.9% / 56.7% pass@32/64.
- outcome-only GRPO: 55.7% / 57.9%.
- outcome+tactic reward: 57.1% / 59.2%.
- tactic advantage on first tactic token: 57.1% / 59.2%; all tactic tokens: 56.3% / 57.8%; last token: 56.7% / 57.5%.
- removing first-error propagation: 56.4% / 58.2%.
- ProofNet results are mixed, including one pass@64 setting roughly flat/slightly worse than supervised.

Mechanism hypothesis:
- Symbolic verifier feedback is most useful when credit is placed at decision boundaries rather than smeared across all generated tokens.

Sources:
- https://arxiv.org/abs/2606.20068
- https://openreview.net/pdf?id=P00k4DFaXF

### C4 — Hierarchical decomposition is the dominant contributor on long verified-code proofs; RL is a smaller refinement

Primary source: Goedel-Code-Prover, arXiv:2603.19329.

Verina module-swap evidence:
- no decomposition + Gemini-3-Flash completion: 19.6%.
- GPT-5.2-Pro decomposition + Gemini completion: 54.4%.
- trained decomposer + Gemini completion: 58.2%.
- GPT-5.2-Pro decomposition + trained completion: 59.2%.
- trained decomposer + trained completion: 68.8%.

Matched hierarchical SFT→RL:
- pass@1 26.9→29.1; pass@10 44.9→46.0; pass@20 53.9→57.1; pass@32 66.1→68.8.
- decomposition score predicts downstream provability with AUROC 0.903.
- cheap quickcheck/reconstruction filters reject a large fraction of bad branches before expensive completion.

Scope:
- whole-proof vs hierarchical headline comparisons are not compute-matched.

Sources:
- https://arxiv.org/abs/2603.19329
- https://github.com/goedelcodeprover/Goedel-Code-Prover

### C5 — Jointly planning program and proof beats sequential build-then-prove planning

Primary source: P^3, arXiv:2608.09277.

Evidence:
- Across 4 frontier backends × 3 Lean verification benchmarks, P^3 beats the stronger baseline in all 12 cells by +4.6 to +11.2 pp.
- Claude-Opus-4.7 controlled planning ablation: Verina 69.8→74.6; AlgoVeri 44.8→48.1; Lean4Commit0 13.9→22.2.
- On difficult subsets, API cost drops by up to 39.6% and wall-clock by up to 37.2%.

Scope:
- One run per task/model/method; no within-task variance estimate.
- Frontier-model transfer to small open models remains untested.

Source: https://arxiv.org/abs/2608.09277

### C6 — Learned refinement search over compiler failure modes gives large fixed-budget gains and adaptively balances restart vs repair

Primary source: `Compile to Compress: Boosting Formal Theorem Provers by Compiler Outputs`, arXiv:2604.18587.

Core idea:
- Lean maps many syntactically diverse failed proofs into a compact distribution of recurring compiler-error classes.
- The method learns conditional repair on `(problem, failed proof, compiler feedback)` and performs a tree search where expanding the root means a fresh proof and expanding an internal node means repairing a failure.
- A learned value function chooses which state to expand rather than always preferring restart or repair.

Fixed sampling budget = 64:
- Kimina base: MiniF2F 77.46, ProofNet 14.56, MOBench 7.78, Putnam 10 solved.
- Kimina + random refinement tree: 81.15, 15.63, 8.61, Putnam 17.
- Kimina + value-guided tree: 81.97, 15.36, 8.61, Putnam 20.
- Goedel-V2 base: 84.43, 15.63, 14.72, Putnam 32.
- Goedel + random refinement: 84.43, 23.72, 30.28, Putnam 63.
- Goedel + value-guided: 86.89, 24.26, 34.44, Putnam 63.

Putnam scaling:
- Goedel random: 63 / 80 / 104 solved at budgets 64 / 128 / 256.
- Goedel value: 63 / 82 / 110.
- Kimina value: 20 / 23 / 25.

Controlled evidence against the explanation “just more supervised data”:
- Under inference budget 2 on 477 MiniF2F val+test problems: two independent Kimina samples solve 277; Kimina + Claude repair solves 280; SFT repair model solves 284.
- Goedel cold-start direct-SFT vs expert-iteration refinement under random search on Putnam: direct 32 solved; base refinement 46; cold-start SFT refinement 47; expert-iteration refinement 63. This isolates most of the gain to on-policy iterative repair training rather than merely adding Claude-generated examples.

Search-policy evidence:
- On a Putnam case study, random tree expansion found a proof after 45 node expansions; value-guided search found one after 5. This is anecdotal, not an aggregate efficiency estimate.
- Value guidance can select the root when restart is predicted to be better, so the useful mechanism is adaptive budget allocation between exploration and repair, not unconditional repair.

Token accounting:
- Goedel-V2 vs Goedel-Expert at Putnam budget 256: avg input 336.49 vs 3560.39 tokens; avg output 10145.58 vs 3555.41. Refinement spends more prompt/input context but far fewer generated tokens.
- On MiniF2F budget 64: input 271.30 vs 2799.80; output 6267.47 vs 3538.73.

Important scope:
- This is the closest Lean study found to a fixed-budget composite of direct exploration + verifier-guided repair, but it does not explicitly impose tactic-skeleton/semantic branch diversity like C2.
- Therefore the exact composite “structurally diversified initial branches + learned compiler-guided repair” remains untested in a matched Lean benchmark.

Source: https://arxiv.org/abs/2604.18587

### C7 — A direct diversity+repair composite exists in deductive program verification, though not yet as a matched Lean theorem-proving study

Primary source: `Diversifying to Verify: When Task-Equivalent Programs Differ in Verifiability`, arXiv:2607.09366.

Setup:
- 73 programming tasks.
- For each task, generate four structurally distinct Why3/WhyML variants: array-recursive, array-imperative, list-recursive, list-imperative.
- Freeze the accepted representation-specific contract, then perform bounded verifier-guided annotation repair for up to two passes.

Evidence:
- 292 artifacts total; 96 verify initially (32.9%).
- Repair pass 1 verifies 35 more; pass 2 verifies 23 more; final 154/292 (52.7%).
- Task level: at least one variant verifies for 49/73 tasks (67.1%).
- Strongest single family verifies 44/73 tasks, so cross-structure diversity adds 5 solved tasks beyond that family.
- Per-family final rates: array-recursive 60.3%, array-imperative 47.9%, list-recursive 54.8%, list-imperative 47.9%.

Interpretation:
- This supports a composite architecture: diversify artifact structure first, then perform local verifier-guided repair within each branch.
- The benefit is not merely multiple stochastic samples; the variants deliberately alter representation/control structure.

Critical limitations:
- Why3/SMT-backed program verification, not Lean theorem proving.
- No same-compute comparison against four i.i.d. implementations, so the marginal gain attributable specifically to structural diversity is not fully isolated.
- Representation-specific contracts are intended to express the same task semantics but are not formally proved equivalent to one another.

Source: https://arxiv.org/abs/2607.09366

### C8 — Targeted repair supervision can make a 4B model outperform a 32B prover on isolated Lean repair, but end-to-end impact is not established

Primary source: `Learning to Repair Lean Proofs from Compiler Feedback` (APRIL), arXiv:2602.02990.

Dataset:
- ~260k supervised tuples of erroneous proof, fixed proof, compiler diagnostics/proof state, natural-language explanation, and repair suggestion.
- Errors are constructed by mutating known verified proofs; theorem-level splitting is used to limit direct leakage.

Single-shot repair accuracy:
- Goedel-Prover-V2-8B baseline: 15.5% overall.
- Goedel-Prover-V2-32B baseline: 26.8%.
- Kimina-Prover-8B baseline: 11.1%.
- Qwen3-4B-Instruct baseline: 1.1%.
- finetuned Goedel-8B: 34.6%.
- finetuned Kimina-8B: 31.9%.
- finetuned Qwen3-4B: 27.4%, slightly above the 32B Goedel baseline under this repair-only protocol.

Error-type results for finetuned Goedel-8B:
- tactic 41.7%, line 18.5%, theorem 36.8%, multi-line 20.8%.

Interpretation:
- Explicit supervised error diagnosis/repair is a learnable capability distinct from end-to-end proof generation, and specialized repair data can outweigh model scale on that narrow task.

Critical limitations:
- Evaluation is on the same synthetic mutation family used to construct the training distribution; transfer to naturally occurring failed proofs is not established here.
- The paper evaluates isolated single-shot repair, not whether APRIL finetuning improves end-to-end theorem-solving pass@K when integrated with a search policy.
- Therefore APRIL is best treated as a candidate training signal for a repair module, not evidence by itself of system-level theorem-proving gains.

Source: https://arxiv.org/abs/2602.02990

### C9 — Repository-scale verification needs retrieval/context selection; curated dependency context materially beats dumping the repository

Primary source: VeriSoftBench, arXiv:2602.18307.

Benchmark:
- 500 Lean proof obligations from 23 real-world formal-methods repositories.
- Average 68 transitive dependencies per task, max 480; project-specific definitions/lemmas are common.
- General-purpose models use pass@8 plus up to 3 compiler-feedback repair rounds.

Curated dependency context vs full-repository context:
- Gemini-3-Pro: 41.0% vs 34.8%.
- Claude Opus 4.5: 31.2% vs 23.2%.
- GPT-5.2: 12.6% vs 10.8%.
- Goedel-Prover-v2: 5.6% curated on 496 tasks; 0% full-context on a 44-task subset constrained by context limits.

Important nuance:
- Curated context is derived using dependencies of the ground-truth proof, so it is an oracle/best-case premise-selection condition, not a deployable retrieval method by itself.
- Full context can sometimes contain useful analogous proofs/abstraction patterns absent from the curated set, so “less context is always better” is not supported.
- The real unresolved problem is learned retrieval/selection that approximates the dependency closure without access to the ground-truth proof while retaining useful structural analogies.

Source: https://arxiv.org/abs/2602.18307

## Cross-finding synthesis (hypotheses, not universal laws)

The evidence now supports a more precise search architecture than “sample more”:

1. **Allocate test-time compute adaptively between fresh branches and repair** (C1, C6), rather than choosing only restart or only refinement.
2. **Diversify at semantic/structural decision points when policy collapse exists** (C2), while gating because forced structure can hurt SFT policies.
3. **Repair locally using high-information verifier diagnostics** (C1, C6, C8), ideally with a repair model explicitly trained on failures.
4. **Search over artifact/proof structure before local completion** (C4, C5, C7).
5. **Use verifier-compatible dense scores/cheap rejectors to route budget early** (C3, C4, C6).
6. **Treat premise/context selection as part of reasoning** on repository-scale problems (C9), not as a passive prompt-construction detail.
7. **Do not infer system-level theorem-solving gains from isolated repair benchmarks** (C8), and do not infer structural-diversity gains without matched i.i.d. controls (C7).

A high-value composite experiment remains:
- same base Lean prover and same total verifier-call/token/wall-clock budget;
- initial branches allocated either i.i.d. or by structural tactic/opening diversity;
- each failed branch optionally repaired by a learned compiler-conditioned model;
- a learned value/router chooses restart vs which failed branch to refine;
- repository tasks add a learned context selector;
- evaluate both pass@budget and efficiency, plus diversity/repairability diagnostics.

## Rejected / deprioritized leads

- **Pure pass@K scaling as the primary mechanism:** repeated plateaus/diminishing returns.
- **Surface prompt paraphrases as structural diversity:** controlled evidence says no.
- **Unconditional structural forcing:** can hurt SFT provers.
- **Unconditional repair:** C6 shows value-guided search sometimes correctly prefers fresh generation.
- **Treating extra SFT data as the explanation for refinement gains:** C6 expert-iteration ablation argues against this.
- **Using APRIL headline “4B > 32B” as evidence of a generally stronger prover:** it is repair-only and distribution-specific.
- **Raw full-repository context as a substitute for premise selection:** C9 consistently degrades relative to oracle-curated dependencies and can exceed model context limits.
- **Leaderboard comparisons with unmatched compute or different tool budgets:** preserve as descriptive only.

## Nonempty frontier queue

1. **Exact Lean composite test remains open:** find a study combining explicit structural/tactic diversity with learned compiler-guided repair/value routing under matched verifier-call/token budgets. `Compile to Compress` covers adaptive fresh-vs-repair search but not explicit structural branch diversification.
2. **End-to-end APRIL integration:** search for follow-up work integrating APRIL-style repair finetuning into theorem-solving search and report pass@K/compute, not isolated repair accuracy.
3. **Mode-collapse diagnostics:** find cheap predictors for when tactic-skeleton diversification helps vs hurts (first-tactic entropy, proof-state diversity, semantic tactic clusters, verifier-error diversity).
4. **Learned context selection on VeriSoftBench:** identify retrieval methods that approximate oracle dependency closure without using ground-truth proofs, and compare against full context under the same model/repair budget.
5. **Hierarchical search compute accounting:** seek token/verifier-call/wall-clock matched replication of Goedel-Code-Prover-style decomposition.
6. **P^3 open-model replication:** distinguish planning benefit from frontier-model capability.
7. **Cross-verifier generalization:** compare CEGIS/SMT counterexample loops, Why3 repair, Lean compiler repair, and Dafny/Verus feedback using normalized generation/verifier budgets.
8. **Failure-mode routing:** test whether compiler-error category predicts repair success sufficiently well to allocate attempts per error class rather than a single global repair policy.

## Exact next action

Begin with frontier item 1 using targeted queries for Lean systems that combine explicit tactic/semantic branch diversity with compiler-guided learned repair or restart-vs-repair routing. If no matched study is found, move immediately to item 3 and extract quantitative predictors of RL mode collapse / strategy diversity that could serve as a routing gate. Preserve “no direct matched study found” as a research gap rather than assuming the combination is synergistic.
