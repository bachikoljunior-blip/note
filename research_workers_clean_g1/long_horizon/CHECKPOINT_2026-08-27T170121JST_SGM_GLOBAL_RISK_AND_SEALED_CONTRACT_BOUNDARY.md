# Long Horizon clean_g1 — global risk spending and sealed-contract boundary

Observed invocation start: `2026-08-27T16:59:25+09:00`.
Observed checkpoint time: `2026-08-27T17:01:21+09:00`.
Semantic-freeze control tuple: note main `c33d34e55bd4f14f242961562c0f8eb5f3c12d34`, root control revision `11`, role config revision `5`, root blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role config blob `268523da20c78ce3091344c492ad3d51f6f9e667`. The repeated pre-semantic SHA-only ref lookup matched. Later note-main movement was used only for write safety and was not adopted semantically.

## New primary-source evidence

### 1. SGM executes cumulative risk spending across persistent recursive modifications, but not in an LLM-agent loop
Primary source: **SGM: A Statistical Gödel Machine for Risk-Controlled Recursive Self-Modification**, arXiv:2510.10232v1, 2025-10-11. https://arxiv.org/abs/2510.10232

SGM directly addresses a frontier left open by candidate-local gates: an accepted edit changes the incumbent and persists into later rounds, so the safety target is not only a per-candidate false-commit probability. The paper allocates a global error budget across rounds and explicitly argues that persistent harmful commits motivate familywise control rather than ordinary FDR. Its Confirm-Triggered Harmonic Spending (CTHS) spends risk only on candidates that escalate to confirmation.

In the controlled CIFAR-100 power analysis, CTHS spends `0.0748 < delta=0.10`, accepts the injected genuine improvement on the first confirmation, and later rejects noisy positives; the ordinary harmonic schedule spends `0.0388` but makes no accepts because its power is diluted by round-index spending. In the real CIFAR-100 stress test, iterations 1–5 are rejected, iteration 6 is confirmed on 30 seeds and accepted at `56.05% -> 61.56%` (`+5.51pp`, lower confidence bound `+0.31`), and iterations 7–10 are rejected. This is actual repeated persistent candidate gating with nonzero accepted improvement under a global risk budget.

The strongest scope boundary is equally important: the paper does **not** test an LLM-based software/API agent loop. Its proposers are preset/random hyperparameter changes, and the empirical domains are CIFAR, ImageNet-100, CartPole/LunarLander and Rastrigin. The authors explicitly leave LLM-agent loops and larger-scale pipelines as future work. The i.i.d./bounded paired-difference and stable-harness assumptions are also narrower than adaptive software-agent deployment.

### 2. Current public SGM repository does not substantiate its README's advertised long-horizon Ex7/SSL artifacts
Public repository: https://github.com/gravitywavelet/sgm-anon

The current README advertises `PGM_Ex7/` as a 40-iteration ImageNet-100 long-horizon experiment with two acceptances and cumulative risk below `delta=0.1`, and also advertises an `SSL/` RL directory. However, a current public root-contents read shows only `PGM_Ex4/`, `PGM_Ex5/`, `PGM_Ex6/`, `PGM_ImageNet100/`, README, figure and requirements; `PGM_Ex7/` and `SSL/` are absent from the root listing. Therefore the README's 40-iteration/120-decision result is **not treated as code-verified in this run**. The paper's published 10-iteration CIFAR-100 sequence remains primary evidence; the extra README claim is a reproducibility lead requiring artifact recovery or later release.

This is a useful governance lesson by itself: a repository README can become semantically newer than the actual published paper and simultaneously advertise artifacts that are not present in the current tree. Long-horizon evidence should bind headline claims to actual source/artifact identity, not README prose alone.

### 3. AQuA gives fresh evidence for structural capacity/evaluator sealing in a recursive research loop
Primary source: **AQuA: Recursively Self-Improving Quantitative Trading Research Agents**, arXiv:2608.12841v2, 2026-08-17. https://arxiv.org/abs/2608.12841

AQuA runs two separate recursive research systems that retain validated evidence and use it to guide later proposals while keeping the experimental contract fixed. The agent acts only through a restricted DSL/config diff; data splits, labels, feature definitions and evaluator are fixed outside the adaptive surface. The final report window is scored only after the configuration is frozen and is not returned to the search loop. Part II uses a train/validation/test chronology with 2020 as an embargo gap and untouched 2021–2025 reporting; the search loop sees only inner validation.

This directly strengthens the previous capacity-freeze/sealed-evaluator frontier: the recursive object can improve while the definition of success and leakage-sensitive data path remain structurally outside its writable surface. AQuA reports a per-stock IC of `+0.0843` versus `+0.0613` for the strongest GRU baseline and a held-out Sharpe up to `+2.50`; a stricter walk-forward remains about `+2.0`.

Scope guard: this is quantitative-research recursion, not software-agent release engineering. It also does not provide candidate-local anytime-valid tests or global sequential false-promotion accounting. The authors explicitly note that test isolation is a governance property rather than a cryptographic barrier if an operator can access the store.

## Revised synthesis

The global-risk frontier should now be split more carefully:

1. **Candidate-local optional-stopping control**: PACE-like e-process gates.
2. **Persistent-run cumulative harmful-commit control**: SGM provides executed familywise risk spending across recursive edits with nonzero accepted gains, but outside LLM-agent loops.
3. **Persistent software/web/tool release operation**: AgentDevel provides real accepted RCs, but lacks anytime/global statistical risk control.
4. **Verifier/capacity sealing**: AQuA and SEAL support keeping evaluator/data path outside the adaptive surface; AQuA additionally freezes the search contract and uses a never-fed-back report window.
5. **Long-run gate exposure/refresh**: LOGOS provides an explicit mechanism, but positive evidence is not yet a stateful software-agent release study.

A new conceptual correction follows from SGM: because a single harmful persistent edit can poison every later incumbent, **FWER-like 'probability of any harmful commit' may be a more appropriate primary safety objective than FDR in some recursive-release settings**. FDR/LORD can still be useful when errors are reversible/independent enough, but should not be imported automatically as the global objective. The right comparison is now FWER/event-triggered spending versus FDR/wealth-style spending under explicit persistence and recovery assumptions.

## Exact continuation

1. Find a stateful software/API/LLM-agent release loop that actually executes **global cumulative risk spending** across many persistent self-modifications with nonzero beneficial accepts; distinguish FWER from FDR objectives.
2. Search for direct experiments comparing FWER/event-triggered spending versus LORD/online-FDR-like spending under persistent harmful-commit costs, not only simulations of temporary hypotheses.
3. Recover or falsify the SGM README's advertised `PGM_Ex7/` 40-iteration artifact from an official release, branch, tag, archive or later paper version; do not accept README-only numbers meanwhile.
4. Search for recursive software/API release experiments with AQuA-style structural capacity freeze: fixed tools, retrieval width, attempt budget, memory budget, data path and evaluator authority, plus a never-touched report holdout.
5. Find measured verifier-exposure studies where aggregate accept/reject feedback degrades a hidden gate and retirement/refresh restores validity.
6. Continue the common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` frontier.
7. Recover numeric CASS coalition cap `k` and u-SMCO threshold `tau` only from official supplement/code.
8. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
