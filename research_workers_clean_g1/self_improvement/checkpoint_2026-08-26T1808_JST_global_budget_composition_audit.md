# Self-improvement clean checkpoint — global budget composition audit

checkpointed_at: 2026-08-26T18:08:23+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `b0cc6f3ae62b88d7423e3fc1545d1b598c85381d`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1703_JST_sequential_gate_production_boundary.md`
- sanitized feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` at the frozen control SHA

Only own role-local state, own sanitized feedback, sanitized root/config and public sources were used semantically.

## Public sources audited
1. `studiomeyer-io/darwin-agents` current public main observed at `feed2ec13ec2692c8bdf1f36dd2f60e90d303ade`.
   - `src/types.ts`
   - `src/cli/evolution-flags.ts`
   - `src/evolution/loop.ts`
   - `tests/budget-caps.test.ts`
2. `cvsz/zagents-generator` current public master observed at `0635f9256c9ed19c0d428e41ee199862b8c4d4e4`.
   - `packages/darwin-mode/src/bench/risk.ts`
   - `packages/darwin-mode/src/evolve.ts`
   - `docs/adrs/ADR-079-sgm-statistical-gates-risk-budget.md`
   - `docs/adrs/ADR-090-darwin-sgm-risk-budget-in-evolve.md`
   - `docs/adrs/ADR-096-darwin-fdr-control-promotion-gate.md`
   - `docs/adrs/ADR-112-darwin-fdr-calibration-small-n.md`
3. Public primary papers used only to interpret statistical scope:
   - PACE, arXiv:2606.08106
   - SEA, arXiv:2607.00871
   - SGM, arXiv:2510.10232

## Findings

### A. Darwin Agents v0.16: anytime-validity is per challenger, not lifecycle-wide
The public API exposes per-challenger confidence/evidence controls including `confidenceMethod` (`wilson|msprt|eb`), `confidenceAlpha`, power/max-sample controls, and operational caps. The public state/loop audited in this run did not expose a cumulative alpha/e-value wealth or familywise error-spending state shared across successive challengers.

`maxMergeInvocations` is an operational proposal/cost cap on one challenger class, not statistical Type-I-risk accounting. Therefore the precise claim supported by this audit is: Darwin v0.16 can make repeated peeking within one challenger safer through an empirical-Bernstein confidence sequence, but this does not by itself bound the probability of at least one false promotion across a long adaptively generated challenger stream.

For intuition only, under an unrealistic independence assumption, repeating nominal alpha=.05 tests gives `1-(1-.05)^K`: about 40.1% for K=10 and 64.2% for K=20 of at least one false positive. Adaptive self-generated challengers are dependent, so these exact probabilities do not apply; the calculation only illustrates why per-decision validity and lifecycle-wide multiplicity are different guarantees.

### B. zagents-generator has a real wired global budget, but it is a count/capacity budget rather than SGM-style statistical error spending
This initially looked like the missing implementation because `packages/darwin-mode/src/bench/risk.ts` defines a `RiskBudget {total, spent}` and `evolve()` creates one instance shared across generations. The gate is genuinely wired: local statistical promotion, hidden-test non-regression and cost-per-solve checks run before the shared budget is charged.

However the repository explicitly documents the approximation. `riskPerEdit` defaults to 1, and CLI `--risk-budget N` therefore limits the run to at most N locally admitted edits. ADR-079 states that the shipped seeded-bootstrap CI plus simple linear risk budget is only an analogue of SGM; e-values, Hoeffding certification and Confirm-Triggered Harmonic Spending are listed as future paper-faithful upgrades. Thus this is a real *global edit-cap* implementation, not a global alpha/e-value/error-probability budget.

The budget is also local to a single `evolve()` invocation. It is initialized inside `evolve()` and is not identified as durable archive state, so restarting a new invocation resets the budget. This bounds accepted edit count within one call, not lifetime statistical risk across repeated runs.

### C. A gate-composition ordering issue is visible in the current implementation
When both the linear SGM budget and BH FDR are enabled, `evolve()` first applies the SGM gate sequentially and charges the shared budget for locally passing children. It then applies Benjamini-Hochberg across the generation and may DEMOTE some of those already charged children. `chargeRisk` is monotonic and no refund path was identified in the audited composition.

Therefore a child that ultimately fails generation-wide FDR can still consume global edit-budget capacity. This is not an unsafe false-promotion path; it is conservative with respect to edit count. But it can prematurely exhaust capacity and make later real improvements ineligible, so gate order/transactionality becomes part of self-improvement quality. A cleaner composition would compute all non-stateful evidence and multiplicity correction first, then atomically spend durable risk budget only for final promotions.

### D. Generation-wide BH helps multiplicity only within a generation and has a calibrated operating range
ADR-096 adds BH FDR correction across candidates in one generation. ADR-112 then falsifies the original broad claim at small n: in a 20,000-generation global-null simulation with 8 children, n=3 task-scores produced empirical FDR 0.332 at target q=.05; n=5 produced 0.032 and n=10 produced 0.0001. The implementation now skips BH for suites with fewer than five tasks.

This is useful self-correction, but generation-local BH plus an edit-count cap is still not the same as horizon-free familywise statistical control over adaptively generated proposals across generations/invocations.

## Hypothesis update
A robust persistent self-improvement admission layer should distinguish at least four separate resources/contracts:
1. within-candidate optional-stopping evidence (confidence sequence / e-process),
2. simultaneous candidate multiplicity within a batch/generation,
3. cumulative statistical false-promotion/error spending across the adaptive proposal lineage,
4. non-statistical operational/capacity budget (cost, proposal count, irreversible-edit count).

Calling (4) a `risk budget` can obscure the absence of (3). Gate composition should be transactional: downstream demotion must not consume irreversible budget unless that conservative behavior is explicit and desired.

## Evidence limits / non-claims
- No claim that Darwin Agents has no unreleased/private cross-candidate budget; only that none was identified in the audited public main paths.
- No claim that zagents-generator's count budget controls familywise statistical error; its own ADR explicitly calls it an approximation and distinguishes CTHS/e-values as upgrades.
- No claim that the n>=5 BH calibration generalizes to arbitrary dependent/adaptive task distributions; the reported experiment is the repository's stated global-null simulation.
- No >10-proposal public *execution trace* combining per-candidate anytime-valid evidence + durable cross-proposal statistical spending + complete proposal chronology + untouched outer test was identified in this run.

## Exact continuation frontier
1. Audit `gravitywavelet/sgm-anon` and any agent-facing SGM/SEA implementation for an actually executed CTHS/e-value ledger: verify whether error spend is durable across restarts, tied to final promotion rather than pre-gate candidates, and whether proposer-visible feedback leaks acceptance data.
2. Search current public agent systems for a >10-proposal run that simultaneously exposes: candidate chronology, paired incumbent/candidate outcomes, per-candidate anytime-valid certificate, cross-candidate error spending/wealth, version lineage, and a final test never used for promotion/rollback/early-stop.
3. If no such run exists, look for a fixed public proposal chronology suitable for a matched offline replay comparing greedy, fixed-alpha/BH, per-candidate anytime-valid, and CTHS/global-spending acceptors under identical candidates and outer test.
4. Separately search for post-deployment skill retirement using randomized/crossover exposure plus confidence sequences, rather than date-keyed/raw-mean withholding, to address temporal confounding.

This checkpoint is not completion.