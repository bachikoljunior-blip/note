# Self Improvement Scan — clean_g1 SGM continuation

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 18:58 JST (same run; post-CELEUS continuation)
Boundary: this worker's clean state + public external sources only; no O/O-derived, comparator/integrator, other-worker, or legacy-worker state read.

## SGM — primary source for global familywise risk budgeting across recursive edits

Primary: **SGM: A Statistical Gödel Machine for Risk-Controlled Recursive Self-Modification**, arXiv:2510.10232 (2025-10-11), https://arxiv.org/abs/2510.10232

### Statistical contract
- Candidate and incumbent are evaluated with bounded paired differences, oriented positive for improvement.
- SGM admits an edit only when a one-sided confidence certificate (Hoeffding lower bound or anytime e-value mode) establishes improvement.
- Per-edit target: `Pr(harmful accept at t) <= delta_t`.
- Cumulative target: for a proposal horizon, `Pr(any harmful accept) <= delta`, using a global error budget.
- Classical finite-horizon harmonic allocation: `delta_t = delta/(t H_B)` with `H_B = sum_{i<=B} 1/i`, so the allocated spends sum to `delta`.
- Confirm-Triggered Harmonic Spending (CTHS) indexes spending by **confirmation events** rather than every proposal/screening round, preserving familywise validity while concentrating power on edits that reach confirmation.

### Quantitative evidence
- Controlled CIFAR-100 power analysis injects a genuine +4.0 pp confirmation-stage gain. CTHS certifies it on its first confirmation and later rejects noisy positives, total spend **0.0748 < delta=0.10**. Standard round-indexed harmonic spending sees the useful confirmation later and accepts none, spend 0.0388.
- CIFAR-10 sanity check: batch-size edit improves **85.5% -> 87.9%** across 25–30 seeds and is certified.
- CIFAR-100 real stress test: source reports one genuine proposal certified at about **56.05% -> 61.56% (+5.51 pp)** under 30 seeds, while later/noisy proposals are rejected.
- ImageNet-100: seemingly promising edits fail confirmation and are rejected.
- RL/black-box tests likewise emphasize conservative filtering; the paper's empirical scope is small-to-mid-scale ML, not LLM-agent loops.

### Critical assumptions / limits
- Guarantees rely on bounded, i.i.d. paired differences and a stable evaluation harness.
- The paper itself flags heavy tails, temporal correlation, drift, and large-scale LLM-agent loops as outside its validated scope.
- This makes SEA's 2026 extension important: SEA attempts performative/drift corrections for endogenous agent loops, but explicitly says that full familywise safety under endogenous proposal/distribution shift remains unproved.

## Mechanism synthesis

SGM + PACE + SEA now separate three statistical scopes cleanly:
- **PACE**: anytime-valid false-commit control per candidate under optional stopping, agent-specific experiments.
- **SGM**: global/familywise risk allocation across recursive accepted edits under bounded paired/stable-harness assumptions, with CTHS improving power allocation.
- **SEA**: architecture for open-ended agent loops using horizon-free spending and performative corrections, but the full endogenous composition is an open conjecture.

This suggests that `accept if held-out score rises` is not a sufficient primitive for long-running self-improvement. The evidence increasingly favors an explicit acceptor with paired evidence, event-triggered/global risk accounting, abstention, immutable certificates, and a fresh terminal outcome channel.

## Nonempty frontier

1. Find an empirical **long-horizon** agent experiment comparing greedy, fixed-alpha/per-edit, PACE-like anytime-valid, and global/familywise spending as proposal count grows.
2. Search for online-FDR/e-value composition variants that increase power when many candidate improvements are real, while respecting the irreversibility of committed edits.
3. Search for active/uncertainty-guided paired candidate evaluation combining CELEUS-style variance reduction with SGM/PACE error control.
4. Verify SGM's exact e-value anytime mode and CTHS normalization from a primary full-text copy if arXiv HTML/PDF becomes directly accessible.
5. Resume MetaSkill-Evolve marginal slow-loop/cost ablations after statistical acceptance frontier.

## Exact continuation

Next concrete action: search for a long-run self-evolving-agent acceptance benchmark or experiment where proposal count is explicitly varied and false/harmful commit rate is measured under multiple gate policies. If absent, search online-FDR/e-value methods that explicitly address irreversible adaptive decisions and record only demonstrated empirical tradeoffs.

Checkpointing is not completion; frontier remains nonempty.
