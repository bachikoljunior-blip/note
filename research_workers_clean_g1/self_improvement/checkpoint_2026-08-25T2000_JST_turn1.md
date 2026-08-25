# Self Improvement Scan — clean_g1 20:00 JST continuation

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 20:00 JST run
Boundary: this worker's clean `research_workers_clean_g1/self_improvement/` state plus public external sources only. No legacy worker state, other workers, comparator/integrator output, or any non-clean project-derived state was read.
Search bias: benchmark-first / ablation-first; trace mechanisms backward from quantitative gains and failures.

## Newly checked primary sources

1. **Rethinking Self-Evolving Agent Skills: Feedback Dynamics over Multiple Rounds** — arXiv:2608.02636, submitted 2026-07-31. https://arxiv.org/abs/2608.02636
2. **Rethinking the Evaluation of Harness Evolution for Agents** — arXiv:2607.12227, submitted 2026-07-14. https://arxiv.org/abs/2607.12227
3. **Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents** — arXiv:2607.12790 v2, 2026-07-30. https://arxiv.org/abs/2607.12790
4. **Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents** — arXiv:2605.30621, submitted 2026-05-28. https://arxiv.org/abs/2605.30621
5. **FinEvo-Bench: A Longitudinal Benchmark for Self-Evolving Agents in Professional Financial Workflows** — arXiv:2608.06144, submitted 2026-08-06. https://arxiv.org/abs/2608.06144

## New candidate evidence

### C8 — Multi-round skill evolution is sparse search, and ordinary validation selection is not a durable-safety guarantee
**Primary:** Rethinking Self-Evolving Agent Skills.

- Primary study: 42 feedback runs, 14 model-benchmark settings, five benchmarks / three main models; executor/optimizer, revision procedure, validation rule, and round budget are held fixed while feedback view varies.
- Only **55 / 388** proposed candidates become byte-distinct validation bests.
- Validation selects an evolved skill in **11 / 14** settings, but only **9 / 11** improve released-test performance: two validation-selected artifacts fail to improve the released test.
- All 11 selected evolved skills come from conditions containing failed trajectories; success-only feedback never wins primary validation selection.
- GPT-5.5 oracle parallel sampling nearly recovers the evolved SearchQA result (within **0.43 pt**) but remains **30.96 pt** behind the evolved SpreadsheetBench skill; sequential refinement recovers neither. Thus persistent adaptation is sometimes reducible to extra inference compute and sometimes not.

**Scope:** This is longitudinal evidence over 388 candidates, but it is not a direct comparison of greedy vs fixed-alpha vs anytime-valid vs global-familywise acceptance policies, and it does not establish a statistical false-commit rate.

**Mechanism hypothesis:** count proposed edits and downstream validation-to-test failures explicitly; treat evolution as sparse candidate search rather than monotonic learning. A simple non-decrease/best-validation gate does not by itself solve adaptive reuse or distribution shift.

### C9 — Reusable harness benefit must beat matched test-time discovery and disjoint held-out tasks
**Primary:** Rethinking the Evaluation of Harness Evolution for Agents.

Terminal-Bench 2.1, common initial harness and **K=5** compute budget, results averaged over two runs.

Without unit tests, pass@1 averages:
- direct initial harness **68.2**
- parallel sampling **72.3**
- sequential refinement **69.3**
- Harness Evolution **67.4**
- Harness Scaling **71.8**

Harness Evolution is below direct on average; GPT-5.4 drops **75.3 -> 69.7**.

With unit tests:
- direct avg pass@1 **72.9**
- parallel **86.0 / 86.0** pass@1/pass@5
- sequential **84.3 / 91.8**
- Harness Evolution **75.8 / 86.2**
- Harness Scaling **82.6 / 89.3**

Disjoint 45-train / 10-validation / 34-test split:
- initial **67.7** avg pass@1
- evolved harness **68.3**, only **+0.6** average (Opus +1.2; GPT-5.4 +0.0).

Qualitative audit: many persistent edits encode task-specific fixes, efficiency tricks, or checks that a competent agent can rediscover in-rollout; growing persistent text can introduce context bloat. Stable hard failures often remain model-reasoning bottlenecks.

**Scope/correction:** This is a strong negative control for same-benchmark harness-evolution claims, especially TerminalBench-style evidence, but not a universal rejection of harness evolution. One benchmark, high base capability, two-run averages, and authors explicitly note harness sensitivity/task difficulty may determine value.

**Mechanism hypothesis:** every claimed persistent self-improvement should be tested against (a) matched extra-compute/test-time search and (b) disjoint-task reuse. Same-benchmark improvement alone is insufficient evidence for a reusable self-improvement mechanism.

### C10 — If the evaluator evolves, downstream score cannot validate the evaluator; a locked outer audit is necessary
**Primary:** Who Grades the Grader? / Double Ratchet.

- The metric loop evolves transparent compositions of drawback detectors, trained against a tiny ten-item anchor and unlabeled-consensus regularization, then audited on a locked set the loop never reads.
- On code generation the evolved metric improves locked-set agreement with hidden ground truth by **+0.21** over its bare LLM judge, paired **p=0.014**.
- Removing **anchor guards** collapses the metric to a vacuous always-pass detector, while removing detector lifecycle does not. The paper explicitly notes the collapsed metric can still train downstream skills similarly, so downstream task score cannot establish evaluator validity.
- Double Ratchet retains **88–110%** of the held-out lift provided by ground truth / best available rubric across MBPP+, Spider 2.0-Snow, and report generation.
- A report-generation Goodhart episode was detected by an independent judge; adding one detector repaired the metric.

**Scope:** Held-out sets are small (roughly 40–48 items in reported experiments) and only three seeds; tiny-anchor quality and teacher-family dependence remain underexplored. This is evidence for failure-expecting evaluator architecture, not a proof that self-evolved metrics stay calibrated indefinitely.

**Mechanism hypothesis:** acceptance evidence has two independent failure axes: candidate overfit and evaluator Goodhart. Keep an outer audit channel inaccessible to both the proposer and the evolving evaluator; measure evaluator validity directly, not via downstream reward.

### C11 — Separate the ability to write useful improvements from the ability to activate and follow them
**Primary:** Harness Updating Is Not Harness Benefit.

- Controlled analysis pairs seven LLMs as evolvers/agents over SWE-bench Verified, MCP-Atlas, and SkillsBench.
- Evolver-side spread is narrow: best-vs-worst harness-updating gain is at most **3.1 pp** on any benchmark; no evolver dominates all benchmarks.
- The smallest Qwen3.5-9B evolver is best on SkillsBench at **+3.8 pp**, vs Opus 4.6 **+2.3** and Qwen3-235B **+1.5** in the paper's harness-updating metric.
- The downstream task-solving model matters far more: weak-tier models benefit little partly because they fail to invoke relevant artifacts and fail to adhere to them over long trajectories. The paper reports about **25%** harness-load rate for Qwen3-32B versus ~**96%** for strong models.

**Scope:** The fixed solve-evolve protocol and three benchmark substrates limit generalization. Flat evolver scaling does not mean proposer quality never matters; it means scaling the evolver alone produced small marginal spread in these tested settings.

**Mechanism hypothesis:** decompose persistent self-improvement into `artifact quality -> activation/retrieval -> adherence -> outcome`. Spending more capability on the improver can have low returns if the executor cannot reliably invoke or follow the artifact.

### C12 — Longitudinal paired controls show real retained-experience gains, but more memory is not automatically better
**Primary:** FinEvo-Bench.

- 120 real-case-grounded professional finance tasks, 20 scenes across six domains; each scene has six related but substantively distinct cases. Four scaffolds use the same Qwen3.7-Max backbone over three independently shuffled globally interleaved streams.
- Paired non-evolving controls estimate retained-experience effects.
- Evolving conditions improve scores by **+9.33 to +19.37 points** and reduce compliance issues by **0.12–0.44 per task** across scaffolds. Codex has the largest gain (**+19.37**); Letta's evolved score is **91.65** with **0.09** compliance issues/task.
- Within-scene ranks 4–6 gain **6.10–8.70 points more** than ranks 1–3, consistent with accumulation across related cases.
- In Claude Code, **skill-only** evolution outperforms memory-only and combined memory+skill evolution on both task quality and compliance; across all four scaffolds, rubric feedback outperforms reference-answer feedback.

**Scope:** Primary abstract provides these aggregate ablations; exact per-condition table cells remain a follow-up for full primary-table verification. Finance workflow structure may strongly favor reusable procedural skills and should not be generalized to unrelated domains.

**Mechanism hypothesis:** persistence substrate should be ablated, not assumed additive. Combining memory and skills can interfere; concise procedural artifacts plus structured error/rubric feedback may outperform raw episodic retention.

## Cross-candidate synthesis (hypothesis, evidence-scoped)

The frontier now suggests self-improvement evidence should be decomposed into at least five independently testable stages:

`proposal quality -> acceptance validity -> persistent artifact quality -> activation/adherence -> disjoint-task outcome`

and two external controls:

1. **matched test-time compute**: can repeated sampling/refinement recover the same gain without persistent update?
2. **locked outer audit**: is the evaluator itself still valid after adaptive/evolving optimization?

This sharpens the earlier held-out-gate picture. A candidate can pass its ordinary validation gate and still fail released test; an evolved evaluator can reward downstream skills while itself collapsing; and an excellent persistent artifact is useless if the executor fails to activate or obey it.

## Rejected / deprioritized interpretations

- Do **not** infer that harness evolution is generally ineffective from Terminal-Bench 2.1 alone; evidence is task-sensitive and stronger persistent gains exist elsewhere.
- Do **not** infer that success trajectories are useless. In Rethinking Skills, success-only never wins primary selection, but Normal (success+failure) can beat failure-only depending on setting.
- Do **not** infer that a stronger evolver is useless; only the marginal spread under the tested fixed protocol is small.
- Do **not** use downstream skill score as a proxy for evaluator validity after the evaluator itself is optimized.
- Online-FDR/e-value methods are promising for reversible/high-throughput candidate selection, but FDR is not a direct substitute for familywise control when one harmful irreversible commit is unacceptable; keep as theory frontier until matched self-improvement evidence exists.

## Nonempty frontier

1. **Long-run acceptance-policy benchmark remains missing:** locate or construct evidence comparing greedy, fixed per-edit alpha, per-candidate anytime-valid, and global/familywise spending while proposal count is varied and fresh-audit harmful/false commits are measured.
2. Inspect the public Rethinking-Skills candidate trajectory artifacts to quantify by round: proposal count, validation-best replacement count, and released-test/robustness/transfer disagreement. Determine whether false-looking selection risk increases with rounds.
3. Verify full primary-table details for **FinEvo-Bench** skill-only vs memory-only vs combined and rubric-feedback vs reference-answer ablations, including absolute score/compliance cells and variance across the three streams.
4. Inspect **Harness Updating Is Not Harness Benefit** tables for exact activation and adherence diagnostics by capability tier; test whether the failure is retrieval/activation or post-activation instruction-following.
5. Verify **Double Ratchet** anchor-guard and Goodhart ablation tables beyond abstract-level numbers; identify how locked outer-audit frequency affects false evaluator promotion.
6. Resume **MetaSkill-Evolve** primary marginal slow-loop / cost-matching verification: isolate how much value comes from evolving the improver itself after controlling fast-loop iterations and inference budget.
7. Search independent replications / negative results for longitudinal self-evolution, especially cases where validation-selected persistent artifacts regress under distribution shift.
8. Search for a combined acceptor that couples evaluator-validity auditing, paired candidate evidence, global risk spending, and evaluation-cost reduction; do not assume modular statistical guarantees compose under endogenous proposals.

## Exact continuation

Next concrete action: inspect the public `rethinkskill` artifacts / released candidate histories and compute whether validation-best updates become less reliable as adaptive rounds accumulate (released-test/robustness/transfer disagreement by round). If the artifacts do not expose enough per-round outcomes, inspect FinEvo-Bench full primary tables for substrate/feedback ablations, then return to MetaSkill-Evolve slow-loop marginal-value verification.

Checkpointing is not completion; frontier remains nonempty.
