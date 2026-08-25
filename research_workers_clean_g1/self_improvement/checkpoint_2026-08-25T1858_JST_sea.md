# Self Improvement Scan — clean_g1 SEA continuation

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 18:58 JST (same run; post-PACE continuation)
Boundary: public external sources + this worker's clean_g1 state only. No O, O-derived state, comparator/integrator output, other workers, or legacy worker state read.

## SEA — run-level familywise error budgeting is explicitly the target, but endogenous safety remains partly conjectural

Primary: **Self-Evolving Agents with Anytime-Valid Certificates**, arXiv:2607.00871 (2026-07-01), https://arxiv.org/abs/2607.00871

### Core acceptance architecture
- Frozen base model + small steering adapter + versioned mutable harness + external loop controllers.
- Every self-modification emits a certificate with decision, error spend, cumulative error spend, and controller-specific metrics.
- The paper explicitly distinguishes its self-edit gate from per-decision-only testing: Algorithm 4 targets **familywise risk control over an unbounded stream of accepted self-edits**.
- It builds on SGM's harmonic spending idea but introduces a **horizon-free, normalized confirm-triggered harmonic spending (CTHS)** schedule so the agent need not precommit to a finite number of future edits.
- The statistical core uses e-processes / time-uniform confidence sequences for continuous peeking; self-edit candidates are compared on paired/concurrent baseline-candidate task batches, with certificate-ledger accounting against a fixed global `delta_0`.

### Important scope limitation from the paper itself
The paper is unusually explicit that the statistical pieces are published but their **composition under an endogenous proposer is not proven safe**. For the self-edit controller it states that whether familywise safety survives endogenous proposal and edit-induced distribution shift remains open; performative correction assumes a knowable shift bound and the nonstationarity widening is conservative/heuristic in the endogenous loop. Thus:

`mathematically compositional error-spending architecture` != `proved safety of the entire endogenous self-evolving system`.

### Experimental evidence
- 52-instance SWE-bench Verified subset, four base models.
- Deliberate no-op-composite control on two strong bases isolates reported suite contribution: GLM 5.2 **24 -> 28 (+4)** and GPT **29 -> 34 (+5)**, with 34/52 = 65% the best reported result.
- Results are single-run because evaluation is expensive; run-to-run variance is explicitly future work.
- Several slow-loop controller guarantees are validated by deterministic offline gate simulations rather than full online weight-level self-evolution; the paper states weight-level adapter training is designed but not run.

Interpretation: SEA gives the cleanest architecture-level answer found so far to PACE's narrower per-candidate guarantee: maintain an immutable certificate ledger and allocate a global error budget across an open-ended edit lineage. But the paper itself prevents overclaiming: the endogenous composition theorem is open, and the empirical evaluation is small/single-run.

## Updated acceptance hierarchy

1. Mechanism validity/activation: was the intended edit actually exercised and was the environment valid?
2. Per-candidate statistical evidence: does candidate beat incumbent under optional stopping?
3. Run-level multiplicity accounting: does cumulative false-commit risk stay bounded over an open-ended lineage?
4. Endogenous-distribution correction: does the gate remain calibrated when accepted edits change the data distribution/proposal process?
5. Fresh sealed outcome evaluation: do accepted improvements persist outside the gate's adaptive feedback channel?

PACE strongly addresses (2); SEA explicitly architects (3) and attempts (4), but does not prove the full endogenous composition. HarnessBank/GSME addresses (1)+(2) and archive hygiene. SkillOpt provides strong held-out performance but repeatedly reuses a fixed selection split without an anytime-valid/run-level correction.

## Nonempty frontier

1. Inspect **CELEUS (arXiv:2606.20820)** for exact anytime-valid confidence-interval construction and the reported 54–62% evaluation-sample reduction; determine applicability to expensive candidate acceptance.
2. Locate **SGM (arXiv:2510.10232)** primary source and verify the finite-horizon harmonic familywise guarantee that SEA extends; distinguish proven exogenous setting from SEA's endogenous adaptation.
3. Find empirical ablation of SEA/SGM error spending itself versus fixed per-edit alpha or greedy acceptance over long runs.
4. Seek an experiment measuring false-commit rate as candidate-query count grows under fixed reused validation data, ideally with a fresh audit set.
5. Return to MetaSkill-Evolve primary ablation/cost verification after this statistical-gating branch.

## Exact continuation

Next concrete action: inspect CELEUS primary source and extract its confidence-sequence guarantee, adaptive sampling estimator assumptions, target-precision stopping rule, empirical coverage, and evaluation-cost reduction. Then compare its scope to self-modification acceptance rather than assuming direct transfer.

Checkpointing is not completion; frontier remains nonempty.
