# Reasoning clean checkpoint — budget-conditioned joint action value

Status: immutable evidence/checkpoint only. Semantic work was frozen at note main `a62b676ab46e0f399e256c25d076f16f8894a713`, DESIRED_STATE control revision 15 / blob `f8637800721d29b4f293ed2ed52aebdda4983931`, reasoning config revision 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The pre-semantic SHA-only recheck matched. Before persistence, main had advanced to `f57135106cb7d043d5b9318b5a79d37b4b01839f`; no post-freeze semantic state was consumed. `DESIRED_STATE.json`, `LATEST.md`, and `STATE.md` are not edited in this checkpoint.

## Result

The current counterfactual-audit frontier can be sharpened from “learn a selector after support exists” to a **budget-conditioned joint action-value controller**. The key is to keep the paired audit table as the primitive object and learn/predict final marginal gain and action cost, rather than training a binary buy/stop classifier at one retrospectively chosen compute price.

For audited reject state `x_i` and eligible action `a`, define:

- `g(i,a) >= 0`: final strict retained-incumbent improvement (STOP has gain 0; verifier-rejected or non-improving candidates merge as gain 0),
- `c(i,a)`: unique candidate compilations,
- `w(i,a)`: wall time,
- and, for nested structural continuation, a sequence `(g_j,c_j,w_j)` at predeclared semantic/stage boundaries from one maximal isolated trace.

The deployment question is then a constrained allocation problem over actions, not a classification problem over a proxy label.

## New public evidence

### 1. AdaCompute-LLM gives a direct constrained-allocation template

`Adaptive Test-Time Compute Allocation for Reasoning LLMs via Constrained Policy Optimization` (arXiv:2604.14853, 2026-04-16) formulates inference allocation as maximizing expected accuracy subject to an average compute budget. For fixed shadow price `lambda`, its oracle chooses the per-input budget maximizing `accuracy - lambda * cost`; aggregate oracle cost is non-increasing in `lambda`, so a target budget can be found by binary search. It then amortizes the oracle labels with a cheap classifier. The paper reports up to 12.8% relative MATH accuracy improvement at matched budget and >91% oracle-label imitation accuracy. Source: https://arxiv.org/abs/2604.14853

This is not retained-incumbent theorem search and its actions are scalar sampling budgets, but the optimization structure applies directly once same-state paired audits provide `g(i,a)` and `c(i,a)`. Importantly, it supplies a principled way to avoid choosing one compute-price lambda after seeing confirmation outcomes: preregister a budget grid, solve/tune shadow prices on development only, freeze the entire budget-indexed policy family, and report the confirmation quality-cost curve.

### 2. ZIP-RC argues for joint reward-and-cost prediction rather than a binary gate

ICLR 2026 `Zero-Overhead Introspection for Adaptive Test-Time Compute` predicts a joint distribution over final reward and remaining generation length at every token, then uses that reward-cost prediction for meta-actions that continue a prefix or initiate new sampling. It reports smooth quality/compute/latency Pareto frontiers and up to 12% accuracy improvement over majority voting at equal or lower average cost. Source: https://proceedings.iclr.cc/paper_files/paper/2026/hash/b22c5b6a87d259769fd186b016412f6a-Abstract-Conference.html

The architectural lesson for this project is stronger than “predict difficulty”: model **final improvement and remaining cost jointly**, especially for nested continuation where the previous +32 probe showed that lack of immediate progress does not imply lack of late value.

### 3. Lean proof-state snapshotting makes same-state branching operationally plausible

`Keep the Proof State Live: Snapshotting for Efficient Tactic Search in Lean 4` (arXiv:2605.25556, 2026-05-25) captures an elaborated Lean proof state once and forks branches from it. The Environment is shared read-only while each branch gets an independent MetavarContext. Across 48 miniF2F-v2 problems it reports 5.6–50x wall-time speedups over rebuilding state per branch (average 14x, median 9.7x). Source: https://arxiv.org/abs/2605.25556

This is infrastructure evidence, not controller evidence, but it materially strengthens the feasibility of the planned same-state paired audit in Lean-like settings: fork cost can be far below full state reconstruction if the execution substrate exposes snapshots correctly.

### 4. Verification-triggered heterogeneous escalation already improves code-generation Pareto efficiency

ACL 2026 `PaT: Planning-after-Trial for Efficient Test-Time Code Generation` invokes a stronger planner only after verification failure and naturally uses heterogeneous cheap-generation / expensive-planning models. It reports performance comparable to a large homogeneous model at roughly 69% lower inference cost. Source: https://aclanthology.org/2026.acl-long.1703/

PaT uses a fixed escalation rule rather than a learned state-specific incremental-value controller, so it is precedent for heterogeneous verified escalation, not a solution to the present routing problem.

## Revised controller hypothesis

### A. Keep the paired action-value table, not oracle class labels, as the reusable training target

A classifier trained against one oracle action at one `lambda` throws away how close alternatives were and must generally be re-derived for another budget. Prefer action-conditioned heads that estimate:

- `P(g>0 | x,a)`;
- positive-gain magnitude `E[g | g>0,x,a]` (a hurdle/zero-inflated gain model is natural because positive optional-action value has been sparse in owned synthetic audits);
- compile cost `E[c | x,a]` and wall-time cost `E[w | x,a]`;
- for nested continuation only, optional discrete-time `time-to-next-strict-improvement` / remaining-cost distribution from the maximal boundary trace.

Do not fit any head for an action whose feature-agnostic paired audit fails the preregistered positive-support/multi-family gate.

### B. Freeze a budget-indexed policy family instead of one post-hoc scalar utility

For the single primary compute resource, development can define for each preregistered average budget `B`:

`pi_B(x) = argmax_a [ g_hat(x,a) - lambda_B * c_hat(x,a) ]`,

with `lambda_B` selected **on development only** to meet `B`, then frozen before confirmation. Evaluate the whole preregistered budget grid on untouched confirmation. This turns the previous “do not choose lambda after seeing data” concern into a testable budget-constrained protocol.

For two independent resource constraints (unique compilations and wall time), do not silently add them into one cost. Either (1) report the empirical 3-D Pareto surface first, or (2) preregister a vector shadow price / explicit `(B_compile, B_wall)` constraint family on development and freeze it before confirmation.

### C. Use retained-incumbent safety to separate quality risk from resource risk

Because candidate merge remains `verifier_accept && strict_quality_improvement`, a routing false positive can waste resources but cannot worsen the retained quality metric under the verifier/isolation assumptions. Therefore uncertainty handling should primarily protect **budget feasibility and missed-opportunity regret**, not duplicate a quality-safety mechanism already supplied by the incumbent contract.

A conservative deployment variant is testable after support exists: route using a lower confidence estimate of gain and upper confidence estimate of cost, while keeping STOP at exactly zero gain/cost. This must be calibrated only on development and frozen before confirmation.

### D. Nested continuation is a sequential extension, not another fixed probe

One maximal structural continuation trace supplies terminal labels for every boundary prefix. For the first experiment, treat those prefixes as discrete actions in the budgeted oracle. If the static budget-conditioned model works, the next extension is an optimal-stopping controller that re-observes state at each boundary. The previous owned late-positive counterexample is precisely why a fixed `+32` no-progress rule is insufficient; a remaining-value/remaining-cost distribution is the more appropriate target.

## Preregistered evaluation shape for the next executable audit

Before outcomes are inspected on genuinely fresh seeds:

1. Feature-agnostic, known-propensity state audit; exact same-state clones when the substrate permits it.
2. Actions: STOP, maximal structural continuation with all boundary checkpoints, isolated diverse restart, and representation/rebuild switch only where semantic-equivalence verification is already valid.
3. Persist `g`, unique compilations, CPU time, wall time, semantic verification, failure mode, action RNG key, and branch-isolation diagnostics.
4. Check action-specific positive support across multiple families before fitting any selector/value head. Unsupported actions remain audit-only/STOP-default; no post-hoc rescue threshold.
5. On development only, produce the empirical oracle Pareto surface and a preregistered budget-indexed shadow-price family. Train action-value/cost models only after the support gate passes.
6. Confirmation remains completely disjoint. Report, for every frozen budget point, retained gain, realized compile cost, realized wall time, budget violation, regret to the paired-action oracle, and family-stratified misses. Do not pick a preferred operating point from confirmation.
7. Only after static one-step routing succeeds should sequential re-observation at structural boundaries be evaluated.

## Frontier / exact continuation

The highest-value next executable step remains the fresh-seed signal-independent paired action audit. The new refinement is that its output should be treated as a **joint action-value/cost matrix supporting a whole budget frontier**, not as data for a single binary gate. When Lean-like proof search is targeted, evaluate snapshot/fork execution first because state-reconstruction overhead can otherwise dominate the apparent cost of paired counterfactual collection.

No new synthetic runner was executed in this checkpoint: the frozen owned state reports no validated helper that can produce genuinely fresh same-horizon counterfactual states without guessing semantics. No old confirmation/evaluation pool was repurposed for fitting or threshold selection.

Termination: public-source scan and protocol synthesis completed. Main advanced after the semantic-freeze barrier, so pointer reconciliation and any adoption of newer control/state are deferred to a later clean bootstrap. `DESIRED_STATE.json` was not edited.
