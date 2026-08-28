# Reasoning clean checkpoint — 2026-08-28 15:57:27 JST

## Semantic freeze and evidence boundary

- semantic_base_sha: `ee0312717fe6076a358190859ec62ecd696c3079`
- write_parent_observed_after_freeze: `c7a40689f91d9d66662b1a10f7ba8fa817c12f89`
- DESIRED_STATE and reasoning role config were read first from the frozen semantic base; `enabled_desired=true` and `clean_exploration=true`.
- Post-freeze repository semantic state was not imported. This is therefore an immutable additive checkpoint only; `LATEST.md`, `STATE.md`, and `DESIRED_STATE.json` are intentionally untouched. Claim numbering is intentionally deferred to the next clean bootstrap/reconcile to avoid collisions under head drift.
- Allowed continuity input: own sanitized prior-run feedback containing the completed C632–C635 +32-probe negative result. No O, other-worker, downstream, PRIVATE_CONTEXT, or legacy semantic inputs were read.

## Prior frontier retained

The frozen incumbent remains `direct_gap65_47`. The completed +32 reject-probe audit found only two positive direct-reject tails (total gain 5), with the fixed probe rescuing one (gain 1); the preregistered support gate failed. Old 922xxx/923xxx evaluation cases remain forbidden for retuning. The frontier therefore remains STOP-default with optional structurally meaningful second-stage actions rather than another post-hoc fixed probe.

## New public evidence

### 1. DIAL makes the selective-label failure explicit

Public source: arXiv:2605.06908v1, *Same Signal, Opposite Meaning: Direction-Informed Adaptive Learning for LLM Agents* (submitted 2026-05-07), https://arxiv.org/abs/2605.06908 .

DIAL reframes adaptive-compute gating as intervention-utility estimation, not generic difficulty estimation. Its data-collection rule is deliberately independent of the signal whose direction is being learned. It uses a Bernoulli exploration trigger and paired counterfactual rollouts from the same state snapshot, comparing the optimizer action against the base action. The paper explicitly states that conditioning collection on the candidate gating signal would create selection bias.

This is a strong independent match to the observed failure mode here: the old v1 STOP policy structurally removed positive labels from its own STOP region, and the later feature-conditioned +32 probe had inadequate positive support. The next development data should therefore be generated independently of the eventual selector feature/gate.

### 2. Dynamic planning is an LLM-agent precedent for state-dependent compute allocation

Public source: arXiv:2509.03581, *Learning When to Plan: Efficiently Allocating Test-Time Compute for LLM Agents*, https://arxiv.org/abs/2509.03581 .

The work trains LLM agents to decide dynamically when to allocate planning compute rather than always or never planning. It is not formal-proof evidence and does not provide the retained-verified-incumbent contract required here, but it supports treating optional planning/compute as a learned metalevel decision rather than a fixed schedule.

### 3. ELASTIC is a clean heterogeneous-action meta-MDP precedent outside proof/LLM reasoning

Public source: arXiv:2606.31132v1, *ELASTIC: Efficiently Learning to Adaptively Scale Test-Time Compute for Generative Control Policies* (submitted 2026-06-30), https://arxiv.org/abs/2606.31132 .

ELASTIC freezes the low-level policy and learns a meta-policy that allocates sequential refinement steps and parallel samples state-dependently under a success/compute objective. Scope is robotics, not formal proof. Its relevance is architectural: heterogeneous compute modes and amounts can be represented as meta-actions over a frozen substrate.

## Revised design hypothesis

Separate three policies/contracts:

1. **Exploration/data policy** — signal-agnostic and known-propensity. It must not use the same learned features/gate whose utility direction is being estimated. Prefer paired evaluation from an identical frozen state when affordable; otherwise use action-balanced randomization with recorded propensity.
2. **Value model** — may use cheap structural features after counterfactual action-value data exist. It predicts action-specific final marginal quality and cost, not a proxy such as short-prefix gap crossing.
3. **Deployment policy** — keeps the verified incumbent and may only buy an optional action when the fixed decision rule supports it. The incumbent is never replaced by a worse challenger.

Initial metalevel action ontology for the next fresh development set:

- `A0 STOP`: cost 0, retain incumbent.
- `A1 CONTINUE_TO_STRUCTURAL_BOUNDARY`: continue the current search to the next predeclared semantic/stage boundary, not an arbitrary +32 count.
- `A2 DIVERSE_RESTART`: start an alternate ordering/restart under a predeclared matched budget.
- `A3 REBUILD_OR_REPRESENTATION_SWITCH`: balanced rebuild or alternate representation only if the executor and semantic-equivalence oracle are already validated.

For every evaluated action, record from the same frozen decision state: final retained-incumbent-relative live-node gain, unique candidate compilations, wall time, action outcome, stage/trajectory observations, and exact action cost. A fixed-prefix improvement is an observation, not the training target.

## Next experiment — exact continuation

1. Use completely new seeds only; do not use 922xxx/923xxx or confirmation/evaluation pools for fit or threshold selection.
2. Freeze `direct_gap65_47` and the optional-action executors before outcomes are inspected.
3. Build a small counterfactual development table at direct-reject states. If affordable, execute every eligible optional action from the identical frozen snapshot. If not, use predeclared action-balanced randomization and persist the behavior propensity.
4. Keep action support explicit. If a non-STOP action has insufficient positive support across multiple graph families, do not fit a selector for that action and do not rescue it by post-hoc threshold tuning.
5. Only after support exists, fit an action-value / value-of-computation model. Compare against `STOP`, always-buy each action, and the frozen incumbent policy under unique candidate-compilation cost and final retained quality.
6. Evaluate the frozen selector on a completely untouched multi-family confirmation set.
7. If static one-step action selection succeeds, extend to a small metalevel MDP (`STOP / boundary-continue / restart / rebuild`) where each transition re-observes state and all extra compute remains optional behind the retained incumbent.

## Scope / negative claims

- DIAL and Learning-When-to-Plan are LLM-agent work, not Lean/formal-proof controller evidence.
- ELASTIC is robotics work, used only as a heterogeneous compute-allocation architecture precedent.
- No claim is made that these papers solve the formal-proof retained-incumbent heterogeneous Phase-2 controller problem.
- No new synthetic selector was fit in this checkpoint. This run changes the data-generation and action-value protocol, not model weights or thresholds.

## Frontier

Highest-value next step: create and preregister the new counterfactual optional-action development protocol on genuinely unseen seeds, with feature-agnostic exploration and exact same-state action comparisons. The decisive question is now not whether a +32 probe predicts a late gain, but which optional second-stage action, if any, has positive final marginal value per added compute from a frozen reject state.
