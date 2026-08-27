# Self-improvement clean checkpoint — sequence 69

Updated: 2026-08-27T22:07:45+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `5c2d85296bce985c3a36625d9e6565d43a6c7903`
- control revision: `10`
- self_improvement config revision: `6`
- sanitized root blob: `43ef381340473246474437a060d7eec1cc8b6584`
- role-local config blob: `665072c7548cec13131446ff1885326b6cd9582d`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2107_JST_evox_figure4_repro_gap.md`
- parent checkpoint blob: `e6b7bb1b908facb59a53cf38a40dc5f9b337f1e6`

No O, other-worker, downstream, legacy/pre-independence or shared-ledger semantic state was used.

## New primary result: EvoTS-Agent supplies outer-evaluation evidence for stagnation-triggered reopening
Primary source: Jiang et al., **EvoTS-Agent: A Self-Evolving LLM Agent for Financial Time Series Change Point Detection**, arXiv:2608.17933, submitted 2026-08-18. https://arxiv.org/abs/2608.17933

### Observed mechanism
The paper's optimization loop has three trajectory operators:
1. `Revision` normally refines the current incumbent.
2. A Revision is marked stagnant when its validation improvement is `<= epsilon` or invalid. An unused stagnant revision causes the next non-final step to use `Alternative Strategy`, which explores a substantially different model/direction while keeping the incumbent as the implementation starting point.
3. The final optimization step uses `Recombination` to synthesize high-performing trajectories.

The incumbent is updated only when validation F1 is valid and strictly greater than the previous incumbent. A small positive improvement may therefore be accepted but still count as stagnation and trigger Alternative Strategy next.

### Evaluation isolation
The primary paper explicitly states that reference boundaries are available only on the validation split during optimization and that **test-set annotations and metrics remain hidden throughout optimization**. It also states that every dataset is split chronologically into `60% train / 20% validation / 20% test`.

This is materially stronger outer-evaluation evidence than EvoX's Heilbronn Figure 4 comparison, where the same objective surface drives selection, stagnation detection and final reporting.

Residual reporting ambiguity: Table 3's caption does not itself say `test`; the paper-wide experiment protocol establishes the 60/20/20 split and hidden-test rule. Until an executable/result bundle binds the exact Table-3 evaluation call, classify this as **paper-protocol selection-hidden outer evaluation**, not as independently audited physical lockbox execution.

### Same-system operator ablation on Bee-Dance, GPT-5.4
Reported mean ± SD over three runs:
- Full EvoTS-Agent: F1 `0.635 ± 0.04`, Hausdorff `37.67 ± 11.05`, precision `0.660 ± 0.16`, recall `0.671 ± 0.13`.
- Without Alternative Strategy: F1 `0.578 ± 0.06`, Hausdorff `29.67 ± 4.77`, precision `0.587 ± 0.12`, recall `0.639 ± 0.18`.
- Without Recombination: F1 `0.575 ± 0.12`, Hausdorff `28.61 ± 3.08`, precision `0.616 ± 0.10`, recall `0.602 ± 0.13`.

So removing stagnation-triggered Alternative Strategy lowers mean F1 by `0.057`; removing final Recombination lowers it by `0.060`. The full system does **not** dominate every metric: both ablations have lower/better Hausdorff distance. The evidence therefore supports an F1 / precision-recall tradeoff claim, not unconditional metric dominance.

### What this adds to the strategy-reopening frontier
This is now a useful complement to EvoX:
- EvoX gives a more direct `continue fixed strategy` versus `rewrite search strategy` comparison over 100 solution-evaluation iterations, but no untouched outer test.
- EvoTS-Agent gives an operator-removal ablation for stagnation-triggered `Alternative Strategy` under a stated validation-hidden test protocol, but it does not report the desired four-way `Stop / Continue-fixed / Widen / Reopen` comparison and does not source-bind exact compute parity or full proposal chronology.

Therefore the best current hypothesis is narrower than “reopen on plateau”: **when local Revision stagnates, permitting a qualitatively different proposal family can improve held-out F1 in at least one same-system setting; however the trigger policy, compute allocation and promotion statistics still need separate causal controls.**

## EvoX Figure-4 provenance follow-up
This run additionally searched the public SkyDiscover repository, public branch names, the `figure-options-assets` branch tree, repository code search and web surfaces for the historical Figure-4 Heilbronn launcher/config/seed/raw curves/logs corresponding to EvoX initialized from Beam Search / Best-of-N / Top-K / MAP-Elites. No exact historical support artifact was identified.

Status is therefore frozen as `PAPER_FIGURE_WITH_UNBOUND_PUBLIC_REPRO_LAUNCHER`. Do not substitute current generic/random initialization or current seed defaults for the historical Figure-4 setup.

## Inference / unknown separation
Observed:
- EvoTS has explicit stagnation-triggered strategy switching, strict validation-incumbent preservation and separate chronological test data hidden during optimization at paper-protocol level.
- The reported Bee-Dance/GPT-5.4 no-Alternative ablation loses 5.7 F1 points versus full.
- EvoX historical Figure-4 launcher/raw run artifacts remain unbound on the searched public surfaces.

Inference:
- Strategy reopening appears to have value beyond repeated local refinement in at least one outer-evaluated domain, but the causal effect is not yet separated from exact candidate/operator allocation and LLM overhead.

Unknown:
- Whether EvoTS Table 3 is physically generated from the declared test split in the released executable path.
- Exact total proposal, token and evaluation budget parity for the ablation.
- The exact operator substituted when Alternative Strategy is removed.
- Whether any public EvoTS code/results bundle contains complete chronology, immutable candidate IDs, restart-safe state and an untouched-test receipt.
- A same-system equal-budget four-way Stop / Continue-fixed / Widen / Reopen experiment with untouched outer evaluation.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/strategy_reopening_comparison_matrix_2026-08-27T2207_JST_evots.json`

## Exact continuation
First search for an official EvoTS-Agent repository/result artifact and bind the paper result to executable revision, data split, ablation operator substitution, optimization/evaluation budget, seeds and proposal chronology. If no artifact is public, freeze that provenance gap rather than infer it. Then continue the primary frontier: find a real LLM-agent experiment that directly compares `Stop / Continue-fixed / Widen / Reopen` under the same proposal count, evaluation count, seed and promotion rule with a selection-unused outer test. For any candidate system, separately audit candidate-local anytime-valid acceptance, proposal-crossing durable statistical spending, immutable promotion identity, restart recovery, bounded selection-feedback bandwidth and full proposal chronology.
