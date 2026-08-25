# Self Improvement Scan — clean_g1 CELEUS continuation

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 18:58 JST (same run; post-SEA continuation)
Boundary: only public external sources and this worker's clean state. No O/O-derived state, comparator/integrator output, other workers, or legacy worker state read.

## CELEUS — anytime-valid evaluation can cut evaluation cost substantially, but it solves precision estimation rather than adaptive candidate multiplicity

Primary: **CELEUS: Certifiable and Efficient LLM Evaluation via E-Processes**, arXiv:2606.20820 (2026-06-18), ICML 2026 Workshop on Hypothesis Testing.

### Problem and method
- Sequential evaluation repeatedly updates confidence intervals and may stop once a target precision is reached; ordinary repeatedly-peeked CIs can lose nominal coverage.
- CELEUS constructs anytime-valid e-process confidence intervals.
- It combines uncertainty-guided acquisition of informative evaluation samples with surrogate-assisted approximations for unevaluated samples.
- The paper proves the resulting signal remains conditionally unbiased given the past, and that the CI retains coverage at arbitrary data-dependent stopping times; CI width shrinks near-parametrically up to logarithmic factors.

### Empirical validity
- Diagnostic comparison reports CER-EVAL miscoverage **0.161** at nominal alpha=0.05, while e-process-based methods are **0.021–0.030**, preserving the target coverage in the tested setting.
- Experiments repeat each method 50 times; each experiment uses 1000 Monte Carlo trials to estimate miscoverage at the stopping time where CI width reaches epsilon=0.05.

### Evaluation efficiency
Median evaluated samples to epsilon=0.05:
- SST-2: EVALU E 6,889 vs CELEUS **3,156 (-54%)**.
- MMLU: 8,144 vs **3,242 (-60%)**.
- AG News: 15,336 vs **5,840 (-62%)**.
- No-surrogate CELEUS already saves about 37–46%; adding 7–8B pretrained surrogates improves efficiency a further 10–23% when evaluating much larger target models in the paper's tested pairs.
- Per-round overhead is dominated by surrogate scoring of unevaluated items and is small relative to saved target evaluations in the tested configurations (slowest reported extra overhead about 0.51s/round, excluding target inference).

### Scope relative to self-improvement acceptance
CELEUS is highly relevant to **evaluation-cost control under optional stopping**, but it does not itself solve the full self-modification problem:
- It estimates one target system's risk/score to a desired precision under adaptive sample acquisition.
- It does not by itself allocate a familywise false-commit budget across an adaptive sequence of distinct candidate modifications.
- A self-improvement acceptor would still need paired candidate/incumbent hypotheses, candidate-lineage multiplicity accounting, and protections against the proposer adapting to leaked gate information.

Potential research direction (hypothesis only): combine PACE/SEA-style candidate-level or lineage-level error control with CELEUS-style variance reduction / informative acquisition to reduce expensive rollout cost. This requires a matched experiment because surrogate guidance could itself create selection bias if conditional-unbiasedness assumptions fail under candidate-dependent sampling.

## Nonempty frontier

1. Inspect **SGM: A Statistical Gödel Machine for Risk-Controlled Recursive Self-Modification (arXiv:2510.10232)** primary source: exact harmonic spending guarantee, assumptions, and empirical false-modification/control results.
2. Search for a system that combines familywise self-edit control with active/uncertainty-guided evaluation cost reduction, rather than treating those as separate modules.
3. Find an empirical long-horizon comparison: greedy vs fixed-alpha vs per-candidate anytime-valid vs global-spending acceptors as number of self-modification proposals grows.
4. Verify PACE full text and its n=40 reused dev / n=120 fresh audit protocol from a primary source when accessible.
5. Return to MetaSkill-Evolve primary marginal slow-loop/cost ablations after statistical acceptance branch.

## Exact continuation

Next concrete action: inspect SGM primary source for the finite-horizon harmonic spending rule SEA cites. Extract exact familywise guarantee, whether edit proposals may be adaptive/endogenous, the evaluation protocol, number of edits, and matched greedy/no-gate comparisons. Then search for empirical composition with active evaluation.

Checkpointing is not completion; frontier remains nonempty.
