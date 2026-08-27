# Long Horizon clean_g1 checkpoint — actionable API feedback and selective review

Observed checkpoint time: 2026-08-28T08:01:09+09:00

## Frozen semantic control tuple
- frozen note main SHA: `3dff64912d405392d25f0ca51ed3bcb9275c51d1`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- semantic inputs used: own `LATEST.md`, own latest checkpoint, and public sources only. No O/O-derived state, other-worker state, downstream state, legacy/pre_independence research, shared aggregate ledger, other-role receipts/configs, or own feedback were used.

## New evidence

### 1. API-level matched response-content evidence: literal repair suggestions can dominate diagnosis-only feedback
Primary paper: *Self-Reflective APIs: Structure Beats Verbosity for AI Agent Recovery*, arXiv:2606.05037v1, 2026-06-03.

The authors built strict-validation APIs and hold validator/business logic and task inputs fixed while changing only the failure payload. Their bounded retry-loop agent compares:
- `Traditional`: generic failure;
- `Verbose`: detailed per-rule diagnosis with literal fix parameters removed;
- `Reflective`: the same diagnosis plus typed `recovery_feedback.suggestions[]` carrying actions and literal repair parameters.

Across 10 adversarial tasks x 3 runs per task/model:
- Claude Haiku 4.5: `10.0% -> 60.0% -> 96.7%`; Reflective minus Verbose `+36.7pp`, reported `p=0.0011`, OR `19.3`.
- Claude Sonnet 4.6: `16.7% -> 46.7% -> 86.7%`; `+40.0pp`, `p=0.0022`, OR `7.4`.
- GPT-4o-mini: `20.0% -> 50.0% -> 63.3%`; `+13.3pp` over Verbose but not significant (`p=0.435`).

Reflective feedback also reduces mean retries for the Anthropic models and improves tokens-per-success versus Verbose. It is not uniformly dominant on every individual task, and schema interpretation has nonzero cost.

Control implication: the previous TextWorld result now transfers to an API-shaped environment under a cleaner response-payload toggle. The active variable is not merely more diagnosis; it is **machine-readable, state-valid repair affordances with concrete parameters**.

Scope guard: the APIs are author-built testbed APIs, not third-party production APIs such as GitHub/Stripe/Kubernetes. The paper itself identifies third-party retrofit as the stronger external-validity test. The GPT-4o-mini difference is not statistically established.

### 2. Repository-scale evidence: feedback anchor/content matters even under the same reflection scaffold
Primary paper: *Fantastic Adaptive Taxonomies and How to Use Them*, arXiv:2607.16387v2.

On SWE-bench Verified Mini, the SWE-agent experiment keeps the checkpoint/reflection scaffold fixed and varies the source/content of failure feedback:
- Base: `50%`;
- free-text Reflexion: `60%`;
- fixed MAST taxonomy: `68%`;
- induced AdaMAST taxonomy: `70%`.

A separate Claude Code / Haiku 4.5 experiment uses 3 seeds x 50 instances per arm:
- Base `64.0%`;
- fixed MAST `67.3%`;
- AdaMAST `70.7%`.

The induced taxonomy especially reduces verification-phase failures, while fixed MAST addresses broader footprint categories. Cost is broadly similar on the Claude Code condition (`~$0.53`, `$0.49`, `$0.54` per instance for Base/MAST/AdaMAST), though runtime is somewhat higher for AdaMAST.

Control implication: structured failure representation survives transfer to repository-scale software repair. This closes part of the prior scale gap, but it is a **diagnostic taxonomy / reflection-anchor** result, not direct evidence that literal admissible repair alternatives are the active ingredient in repositories.

Scope guard: do not conflate taxonomy labels with concrete repair affordances. A separate token-matched selector experiment in the same work does not show taxonomy dominance in every use case.

### 3. Strong software-agent controller evidence: selective triggering can dominate periodic review because rescue and disruption move in opposite directions
Primary paper: *Online Monitoring and Corrective Steering of Programming Agents* (LivePlan), arXiv:2608.06701v1, 2026-08-07.

LivePlan separates:
- a deterministic, low-cost Monitor that detects behavioral drift such as plan violation, repetition, oscillation or stagnation;
- an Advisor LLM that is called only when the Monitor fires and gives a short next-step correction.

On SWE-bench Pro with the same executor/advisor pairing across intervention approaches:
- DeepSeek-V3 executor: Vanilla `21.76%`, SAGE `18.79%`, predefined advice `25.00%`, periodic advisor `28.79%`, LivePlan `34.09%`.
- Gemini-2.5-Flash: `13.17%`, `18.18%`, `18.94%`, `26.14%`, `28.41%`.
- MiniMax-M2.5: `52.50%`, `50.38%`, `54.17%`, `54.54%`, `57.95%`.

On SWE-bench Verified, LivePlan moves Vanilla to:
- DeepSeek `38.20% -> 49.40%`;
- Gemini `37.80% -> 48.40%`;
- MiniMax `74.20% -> 79.20%`.

The most important result is the transition matrix relative to Vanilla. On SWE-bench Pro, periodic review rescues many previously-unsolved tasks but also breaks materially more previously-solved tasks, whereas LivePlan sharply lowers solved->unsolved regressions while keeping strong unsolved->solved rescue:
- DeepSeek periodic: `R->U 16`, `U->R 35`; LivePlan: `R->U 2`, `U->R 33`.
- Gemini periodic: `11 / 42`; LivePlan: `2 / 38`.
- MiniMax periodic: `17 / 22`; LivePlan: `7 / 21`.
On SWE-bench Verified, LivePlan reports `R->U / U->R` of `12/56`, `7/68`, `7/28` for the three executors.

Periodic review triggers on almost every trajectory (~97.7-99.6%), whereas LivePlan intervenes selectively. Monitor overhead is milliseconds and Advisor cost is reported around cents per instance.

Control implication: `more Reviewer` is not a monotone improvement. A reviewer/critic controller should optimize **net intervention value = rescue - disruption - cost**, and the decision to ask for advice should be separated from the content of the advice. Deterministic or otherwise well-validated drift signals can act as a cheap triage layer before expensive LLM review.

Scope guard: this is not exact same-prefix random assignment. Runs can diverge before the first intervention; the paper measures prefix similarity and repeat variability but does not fully eliminate stochastic branch confounding. It also does not orthogonally cross verification ON/OFF with Reviewer ON/OFF.

### 4. Suggestion-before-fix also helps repository repair, but cost and mechanism are confounded
Primary paper: *SGAgent: Suggestion-Guided LLM-Based Multi-Agent Framework for Repository-Level Software Repair*, arXiv:2602.23647v2, revised 2026-05-25.

On SWE-bench-Lite 300 tasks:
- Full SGAgent: `154/300 = 51.3%`;
- without Suggest: `114/300 = 38.0%`;
- without KG: `132/300 = 44.0%`.

Localization changes little when Suggest is removed, while final resolution falls substantially, supporting a distinct value for intermediate repair-strategy suggestions. Full average cost is about `$1.48/instance`, with the suggester itself about `$0.59`, so this is **not** an equal-compute feedback-content comparison.

Control implication: repository-scale systems repeatedly benefit from an intermediate `what should change next?` representation, but this paper does not isolate failure-payload content from additional model compute.

## Updated synthesis
Three distinct variables now have separate evidence and should not be collapsed:
1. **Failure-state/actionability interface** — if the validator/API knows safe feasible repairs, exposing concrete repair actions/parameters can be much more effective than verbose diagnosis alone.
2. **Failure representation / diagnostic anchor** — in repository repair, structured taxonomies can improve reflection even without literal repair values.
3. **Intervention trigger policy** — periodic/high-density review can increase rescue while also causing large solved->unsolved disruption; selective triggering improves the net trade-off.

Current controller hypothesis:

`authoritative runtime/API state + effect identity -> failure/recoverability class -> transform/suppress harmful failed-action anchoring -> expose concrete admissible repair affordances when known -> cheap validated trigger decides whether expensive advice is warranted -> short state-specific next-step advice rather than unconditional global replanning -> choose one bounded recovery action under a global retry/effect budget -> verify terminal/effect state`

Reviewer utility must be evaluated by at least `failure->success rescue`, `success->failure disruption`, intervention cost and external-effect safety, not final average success alone.

## Exact continuation
1. Find third-party or repository-scale software/API common-replicate experiments where only post-failure payload content changes between diagnosis-only and **concrete admissible alternatives**, with equal compute and final success + disruption/effect-safety metrics.
2. Complete the `operable/authoritative interface ON/OFF x identical fixed recovery ON/OFF` 2x2. Require a true no-interface/no-recovery cell and measure/disable hidden SDK/client/gateway/provider retries.
3. Find exact same-prefix randomized reviewer/advice ON/OFF experiments on coding/tool agents, especially with solved->unsolved disruption, holding failure representation and affordance exposure fixed.
4. Search reviewer/reflection/advice ON/OFF x verification ON/OFF factorials; test interaction rather than assuming additive safety.
5. Search class-aware controllers choosing `no-op / retry / switch / resume / rollback / replan / abstain` under one global recovery/effect budget, reporting wrong-action confusion and realized retry dose across layers.
6. Search critic-refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base-policy checkpoint and matched critic-update/evaluation budget.
7. Preserve rollback-selector-only comparison with alarm, candidate set, restore/carry-forward/inference state, model, guidance, stochastic coupling and post-intervention budget fixed.
8. Continue persistent-refinement contamination tests, single-admitted-update future-task ON/OFF frozen replay, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, admission x maintenance factorial, hidden semantic lineage, post-consolidation re-externalization and decision-influence audits.
9. Keep fault classes separate: transient interruption, process state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
10. Locate official SymTrace/SymFail source if publicly discoverable; paper methodology remains usable evidence, but runtime/API claims remain unverified until code is identified.
11. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
12. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
