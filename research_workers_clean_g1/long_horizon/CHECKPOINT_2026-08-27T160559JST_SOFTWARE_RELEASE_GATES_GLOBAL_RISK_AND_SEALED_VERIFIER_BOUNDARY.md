# Long Horizon clean_g1 — software release gates, global risk, and sealed verifier boundary

Observed invocation start: `2026-08-27T16:02:57+09:00`.
Observed checkpoint time: `2026-08-27T16:05:59+09:00`.
Semantic-freeze control tuple: note main `af546edd969d8f6267dd6561a82366f0cfb68426`, root control revision `11`, role config revision `5`, root blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role config blob `268523da20c78ce3091344c492ad3d51f6f9e667`. Repeated pre-semantic SHA-only ref lookup matched. Later main movement was used only for write safety and was not adopted semantically.

## New primary-source evidence

### 1. AgentDevel closes the nonzero stateful software/tool release-gate sub-frontier, but not sequential-valid statistics
Primary source: **AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering**, arXiv:2601.04620v1. https://arxiv.org/abs/2601.04620

AgentDevel is the closest direct software/API-agent bridge found so far. The persistent object is an agent blueprint that may change prompts, code, or tool wrappers. Each iteration produces exactly one release candidate (RC), evaluates incumbent and RC on the same development tasks, computes example-level fail→pass and pass→fail flips, and either promotes the RC onto one canonical version line or discards it.

Empirically, the final evolved agent improves from `11.0%→22.0%` on SWE-bench Lite, `15.0%→30.0%` on SWE-bench Verified, `17.0%→35.5%` on WebArena, and `54.0%→73.5%` on StableToolBench. The StableToolBench release trace contains repeated **nonzero accepted persistent edits**: iterations `1,2,4,5,6,8,9,10` are accepted while `3,7,11` are rejected. Accepted RCs have many F→P fixes and P→F rates at or below `0.7%`; rejected RCs reach P→F rates up to `4.0%`.

A matched WebArena ablation gives an important safety/utility trade-off. Full AgentDevel reaches final test `34.2`, P→F rate `3.1%`, and `0` bad releases. Removing the flip gate slightly raises the final test metric to `35.0` but raises P→F to `14.8%` and produces `4` bad releases. The gate therefore reduces release accidents but can sacrifice some raw endpoint score.

Scope guard: this is **not** an anytime-valid or globally risk-controlled gate. The same `D_train` is reused adaptively across iterations for proposal diagnosis and RC gating; the held-out test set is used only once at the end. The authors do not prescribe universal statistical thresholds. Thus AgentDevel closes the operational question “can a stateful software/web/tool agent accept real persistent RC improvements under incumbent-vs-candidate non-regression gating?” but leaves adaptive holdout reuse, optional stopping, and cumulative false-promotion risk unresolved.

### 2. LOGOS supplies the missing run-level accounting and holdout-exposure machinery, but its positive gate evidence is not a stateful software benchmark
Primary source: **LOGOS: A Living Logic for AI Agent Teams That Evolve With Humans**, arXiv:2607.10878v1. https://arxiv.org/abs/2607.10878

LOGOS explicitly separates candidate-local and deployment-lifetime error control. A candidate-level optional anytime-valid gate turns gain/regression/safety streams into e-process evidence; across repeated candidates a LORD-style alpha-wealth ledger allocates significance levels and can recycle wealth after discoveries. The formal online interpretation is conditional on super-uniform candidate p-values, predictable spending, valid dependence assumptions, and fresh evaluation data; otherwise the ledger is only conservative audit accounting.

LOGOS also directly addresses verifier exposure. Its gate emits a proposal-safe aggregate view while withholding task identifiers and per-example failures. Root policy defines a gate-exposure budget over maximum decisions, aggregate releases, and cumulative privacy loss, and **retires or refreshes final-gate examples after exposure, repeated selection pressure, budget exhaustion, or distribution drift**. This is the clearest mechanism found so far for the previous verifier-freshness frontier.

The empirical gate evidence is useful but must stay scoped. In constructed common-candidate replay, the paired and anytime-valid gates accept only the beneficial family with no observed harmful-family adoption across 2,500/5,000 deterministic decisions; this is a semantic gate check, not a population estimate over real proposals. In gated memory evolution, LongMemEval improves `0.86→0.90` under the paired gate while the no-gate run remains flat and accumulates more report-holdout regressions. These are not stateful SWE/WebArena release experiments.

Therefore LOGOS supplies the **mechanism bridge** missing from AgentDevel — candidate-local anytime evidence, LORD-style stream accounting, holdout firewall, and exposure-triggered retirement/refresh — but does not yet prove that the complete package preserves power on persistent software/API self-evolution.

### 3. SEAL directly shows why the evaluator must stay outside the evolving state, and also shows that a fixed hidden audit is still only a proxy
Primary source: **Self-Authored Verification Is Unreliable in Heuristic Self-Improving Agents**, arXiv:2607.24300v1. https://arxiv.org/abs/2607.24300

This work runs ten-round self-improvement where the agent edits both `policy.py` and `tests.py`. The accepted state therefore contains both the policy and its self-authored verifier. The proposed SEAL boundary compares candidate and incumbent on a small harness-side hidden audit, returns only one accept/reject bit to the agent, and rolls back the entire policy-test candidate after a clear regression.

Across the reported cross-game comparisons, SEAL produces equal or better final deployment truth in `11/12` model–game comparisons, while ordinary self-authored constraints frequently retain high self-scores despite poor deployment behavior. This is direct longitudinal evidence that **acceptance evidence should not be writable by the object it governs** and that low-leakage feedback matters.

Negative boundary: SEAL itself is not a proof of monotonic improvement. The paper records a case where the second accepted state improves the hidden audit from `12.7→14.2` while deployment truth falls from `17.6→13.8`. A fixed finite audit can misorder candidates even when perfectly sealed. SEAL also does not provide anytime-valid repeated-decision control or an audit refresh/exposure budget.

### 4. Always-valid workflow release shows useful sequential accumulation, but it is an intra-task release controller rather than persistent self-modification
Primary source: **When Should an AI Workflow Release? Always-Valid Inference for Black-Box Generate-Verify Systems**, arXiv:2605.12947. https://arxiv.org/abs/2605.12947

This method calibrates verifier scores against hard-negative incorrect candidates and accumulates an e-process along an adaptive candidate trajectory. On held-out MBPP+ at `alpha=0.10`, it reports `0` false releases on the empirically infeasible subset while still releasing on `77.03%` of feasible tasks with `0` release-conditional failures; at `alpha=0.05`, feasible release remains `74.32%` with `0.91%` failure among released tasks. This is strong evidence that anytime-valid evidence accumulation can avoid the trivial always-abstain solution while retaining power.

Scope guard: the release decision selects one output **within a task trajectory**. It does not govern a persistent blueprint/memory/tool change that alters future tasks, and therefore does not solve cumulative false-promotion risk across self-modification rounds.

## Revised synthesis

The previous frontier is now much narrower. The required pieces exist, but in separate systems:

1. **AgentDevel**: real persistent nonzero RC acceptance on software/web/tool benchmarks, with matched incumbent/candidate flip evidence.
2. **LOGOS**: candidate-local anytime-valid evidence, LORD-style run-level accounting, aggregate-only gate feedback, and gate-example retirement/refresh after exposure.
3. **SEAL**: a direct causal warning that evaluator/test state must remain exogenous and sealed; self-authored verification can stay high while deployment performance collapses.
4. **Always-valid workflow release**: evidence that sequential e-process release can retain nontrivial power instead of merely rejecting everything.

No primary experiment found in this invocation combines all four properties in one **stateful software/API self-evolution loop**.

## Concrete experiment now justified by the evidence

A high-value next experiment is to retrofit an AgentDevel-like RC loop with the missing statistical and verifier-lifecycle controls while preserving its execution-heavy benchmarks:

- keep proposal/diagnosis data separate from a hidden final-gate stream;
- compare incumbent and RC on the same gate tasks under identical harness/model/tool conditions;
- run candidate-local gain **and** regression e-processes; promote only after both satisfy the declared acceptance contract;
- route candidate-level p-values through LORD++/alpha-wealth across the persistent RC sequence;
- return only aggregate/decision feedback to the proposer;
- enforce a gate-exposure budget and retire/refresh gate examples after repeated aggregate releases or drift;
- maintain a separate report holdout that never participates in proposal, selection, or promotion;
- freeze tool count, retrieval width, attempt budget, memory budget, and evaluator authority so extra capacity is not laundered into “better skill” credit.

At minimum compare: `(A)` original flip gate, `(B)` disjoint fixed paired gate, `(C)` candidate-local anytime-valid gate, `(D)` anytime-valid + LORD stream accounting + exposure refresh. Evaluate on SWE-bench Verified, WebArena, and StableToolBench with final task score, accepted beneficial edits, bad-release count, F→P/P→F, report-holdout false promotions, cumulative alpha wealth/spend, gate examples consumed/refreshed, and total evaluation cost.

This experiment is a **new design proposal**, not evidence that the combined stack will outperform AgentDevel. AgentDevel's ablation already warns that stronger release hygiene can slightly lower raw endpoint score while sharply reducing bad releases; power and safety must both be measured.

## Exact continuation

1. Find an existing stateful software/API self-evolution experiment that already combines matched incumbent/candidate execution with **candidate-local anytime-valid evidence**; if found, check whether it actually accepts nonzero beneficial edits rather than trivially rejecting.
2. Find an agent experiment that actually **executes LORD/online-FDR risk spending across multiple self-modification decisions**, not merely proposes the ledger mathematically.
3. Find measured verifier-exposure studies where aggregate accept/reject feedback eventually invalidates a hidden gate, and where holdout retirement/refresh restores validity.
4. Search for software/API release experiments that freeze tool/retrieval/attempt/memory/evaluator capacity while comparing evolving candidates.
5. Continue the common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` frontier; distinguish same-suite but different-seed tables from a true interaction estimate.
6. Recover numeric CASS coalition cap `k` and u-SMCO threshold `tau` only from official supplement/code.
7. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
