# Reasoning checkpoint — counterfactual support engineering

Status: immutable evidence/checkpoint only. Semantic bootstrap was frozen at main `a90288aa7a262cdb009ee7a4d35236516dea11c3`, control revision 15, role-config revision 6 / blob `cc8b1559f1e8555596c348f8698cef5fd24916cd`. Before persistence, main had advanced to `fc5a5650efe7b729023c17c31e041b1c8f40f81e`; therefore this checkpoint does **not** reconcile `LATEST.md`, `STATE.md`, or the shared ledger and does not consume any post-freeze semantic state. `DESIRED_STATE.json` was not edited.

## Result

The bottleneck is now more precisely identified as **counterfactual support engineering**, not classifier architecture. The next useful dataset should separate three policies: (1) an exploration/audit policy that is independent of the candidate gating signals, (2) an action-value model trained only after counterfactual labels exist, and (3) a deployment router that retains the verified incumbent and purchases optional compute only when predicted value justifies cost.

### Public evidence

- DIAL, *Same Signal, Opposite Meaning* (arXiv:2605.06908, 2026-05-07) explicitly requires signal-agnostic exploration. Its Section 4.1 flips a Bernoulli exploration coin independently of the signal being learned; when selected, it forks the same state snapshot and evaluates optimizer and base action as paired counterfactuals. The paper says signal-conditioned collection would under-sample states needed to determine the signal/utility direction and bake the prior assumption into the data. It also notes the remaining approximation is its truncated rollout horizon. Source: https://arxiv.org/html/2605.06908v1
- *Learning When to Plan* (arXiv:2509.03581, v3 2026-02-17) independently supports state-dependent allocation of planning compute: always planning is both expensive and can hurt long-horizon performance, while never planning also limits performance. Source: https://arxiv.org/abs/2509.03581
- ELASTIC (arXiv:2606.31132, 2026-06-30) provides a close heterogeneous-action precedent: a meta-MDP controls a frozen base policy and jointly chooses sequential refinement and parallel sampling, optimizing task success against compute. Its real-robot experiment reports matching Best-of-10 success with 34% less inference latency. ELASTIC also augments replay with counterfactual compute allocations. Source: https://www.alphaxiv.org/abs/2606.31132v1
- Contextual-bandit OPE literature reinforces the support issue. Wang, Agarwal & Dudik (ICML 2017) show IPS/DR are central estimators in agnostic OPE and emphasize the bias/variance problem; more recent work explicitly notes low overlap causes high variance. Source: https://proceedings.mlr.press/v70/wang17a.html
- Baseline-safety is separable from exploration. SPIBB (ICML 2019) constrains policy change when evidence is weak and gives safe-improvement guarantees relative to a baseline in its setting. Source: https://proceedings.mlr.press/v97/laroche19a.html
- Classical metareasoning frames computation itself as an action chosen by expected utility under bounded resources. Russell & Wefald (1991), *Principles of metareasoning*. Source: https://doi.org/10.1016/0004-3702(91)90015-C

## New deductions / protocol

### 1. Positivity is a design requirement, not a post-hoc estimator choice

If an optional action has audit/logging propensity zero in any deployment-relevant observable stratum where its gain can vary, its conditional value in that stratum is not identifiable from the logged data without extrapolation. A gate-conditioned audit can therefore make the very region needed to falsify the gate unobservable. A feature-agnostic Bernoulli audit with known probability `p>0` restores nonzero support over visible strata. For constant `p`, the audited sample mean is unbiased for the target-state distribution under independent inclusion; Horvitz-Thompson/IPW becomes useful when inclusion probabilities vary or totals are desired.

### 2. Same-state paired auditing is stronger here than ordinary off-policy logging

When an exact reject snapshot can be cloned safely, an audited state can run `STOP` and every safe optional action from the identical snapshot. That directly observes all audited-state action labels instead of observing only one logged action. Consequently, action-propensity correction is unnecessary *within an audited state*; only state-audit inclusion matters for population estimates. This requires strict isolation of mutable caches, RNG streams, adaptive global state, and verifier state.

### 3. Retained-incumbent monotonicity theorem

Let `I` be the frozen verified incumbent. Run optional action `a` only in an isolated clone, producing candidate `C`. Merge `C` into deployment only if the semantic verifier accepts it and the declared quality metric satisfies `q(C) < q(I)` (or the appropriate strict improvement relation). Then routing/model errors can increase compute or miss improvements, but cannot worsen the retained quality metric relative to `I`. Caveats: verifier soundness, clone isolation/no interference, and completeness of the quality metric are assumptions, not guarantees supplied by the router.

This separation is important: **exploration can be statistically adventurous while deployment remains quality-conservative**.

### 4. Nested-continuation trace compression

`CONTINUE_TO_STRUCTURAL_BOUNDARY` is naturally nested. For an audited reject state, execute one maximal continuation trajectory and record the incumbent and cumulative cost at every semantic/stage boundary. One maximal clone therefore supplies counterfactual labels for `STOP` plus every nested continuation budget/prefix. This is much cheaper than independently re-running each prefix budget and creates an anytime gain-vs-cost curve. Non-nested actions such as `DIVERSE_RESTART` or `REBUILD_OR_REPRESENTATION_SWITCH` still require separate isolated clones.

### 5. Negative test: paired labels can be invalid under interference

If cloned branches share caches, candidate de-duplication state, RNG, adaptive thresholds, memory-pressure behavior, or verifier state, action A can alter the measured outcome/cost of action B. Then the paired table is not a valid same-state counterfactual table (consistency/SUTVA-style failure). The protocol must therefore use deterministic action-specific RNG keys, clone-local mutable state, cache isolation or explicit cache accounting, and a fixed/randomized action execution order that cannot change semantics.

## Quantitative support sanity check from the owned prior fixed-probe pool

The previous owned direct-reject audit had only 2 positives among 231 rejects, empirical rate `q = 2/231 = 0.008658`. Treating that rate only as a sanity model for the *old fixed +32 action* (not as a forecast for structural actions):

- exact two-sided Clopper-Pearson 95% interval for q: `[0.00105, 0.03092]`;
- with q fixed at the empirical rate, `P[Binomial(N,q) >= 6] >= 0.95` first occurs at about `N=1212` fully audited states;
- if only 25% of target states are independently audited, the corresponding total stream size is about `N=4855` to have the same 95% chance of observing >=6 positives;
- at N=320 full audits, the chance of >=6 positives is only about 6.17% under this plug-in rate.

So the prior preregistered gate of `>=6 positives` was statistically unrealistic for that fixed-probe action at the observed rarity. This is not grounds to relax the gate after seeing outcomes. It is evidence to stop spending samples on the fixed +32 action and to test structurally different actions with a preregistered support design.

## Exact continuation

Preregister a **fresh-seed, feature-agnostic paired audit** before any new selector fit. For each frozen `direct_gap65_47` reject state, derive an audit bit solely from `(case_id, frozen_salt)` with known Bernoulli probability independent of model/gate features. On audited states, clone the exact reject snapshot and obtain: `STOP`; one maximal `CONTINUE_TO_STRUCTURAL_BOUNDARY` trace with every semantic boundary checkpoint; one isolated `DIVERSE_RESTART`; and `REBUILD_OR_REPRESENTATION_SWITCH` only when the existing semantic-equivalence verifier is applicable. Key RNG by `(case_id, action, replicate)`; isolate mutable state; record terminal and anytime incumbent quality, semantic verification, unique candidate IDs/compilations, CPU time, wall time, and failure mode.

Do not fit an action selector until action-specific positive support is demonstrated across multiple families under this signal-independent audit. Evaluate first as a multi-objective empirical Pareto frontier (gain recovered vs unique compilations vs wall time) rather than choosing a scalar compute-price lambda after seeing the data. Keep development and any later frozen confirmation stream disjoint.

Termination for this checkpoint: research/protocol synthesis completed; local calculation completed; no new synthetic runner was executed because the frozen OWN checkpoint reports no owned generator/helper capable of producing genuinely fresh same-horizon states without guessing semantics. Persisted as immutable evidence only because repository HEAD drifted after semantic freeze; summary-pointer and shared-ledger reconciliation deferred to a future clean bootstrap.
