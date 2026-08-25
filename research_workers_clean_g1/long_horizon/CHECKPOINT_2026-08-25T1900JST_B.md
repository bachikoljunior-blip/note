# Long Horizon clean_g1 checkpoint addendum — 2026-08-25 19:00 JST

Boundary remains unchanged: only this worker's clean_g1 directory plus public external sources were used; no O/O-derived/comparator/integrator/other-worker/legacy state was inspected.

## Frontier action completed after the first checkpoint: Atomix primary table extraction
Primary HTML rendering of arXiv v2: https://arxiv.org/html/2602.14849v2

The earlier mechanism-level Atomix finding is now backed by primary quantitative tables.

### RQ1: recoverable-state fault recovery
τ-bench retail (GPT-4.1, max_steps 30), clean task success:
- `fp=0`: Tx-Full 60%, Checkpoint-Replay 60%.
- `fp=0.10`, N=30: Tx-Full 73% [54,87], Checkpoint-Replay 63% [44,80].
- `fp=0.30`, N=30: Tx-Full 57% [37,75], Checkpoint-Replay 53% [34,72].
- Full task pool at `fp=0.10`, N=114: Tx-Full 67/114 = 58.8% [49.4,67.7] vs Checkpoint-Replay 61/114 = 53.5% [43.9,63.0], Fisher two-sided p≈0.50: statistically tied on RQ1 task success alone.

WebArena / OSWorld show the same broad tiering. At `fp=0.30`:
- WebArena: Tx-Full 57.2±6.7 vs Checkpoint-Replay 53.2±4.3.
- OSWorld: Tx-Full 37.0±8.8 vs Checkpoint-Replay 37.1±5.1.

Interpretation: the core advantage is **not** simply that transactional replay massively outperforms ordinary checkpoint replay on recoverable-state task success. On pure RQ1, the two can be statistically tied.

### RQ3: irreversible-effect leakage is where the separation becomes large
500 irreversible-send attempts:
- Tx-Full: 0/500 leaks, 0%, 95% CI [0,0.74].
- Checkpoint-Replay: 200/500 leaks, 40% [36,44].
- Saga-Compensation: 400/500, 80% [76,83].
- No-Tx: 500/500, 100% [99.3,100].
- TCC-Confirm and Mutex+WAL+Rollback also achieve 0/500 when fully wired for that effect class.
- Deliberately misclassifying an irreversible Atomix effect causes 300/500 leaks (60% [56,64]), confirming that effect classification is load-bearing rather than cosmetic.

The paper reports that Atomix released all 500 valid irreversible sends while blocking all 500 invalid ones, so zero leakage was not obtained by blanket suppression.

### Combined stress: recovery + irreversible effects + contention
The paper explicitly reports that Checkpoint-Replay's retry path re-externalizes irreversible confirmations. At `fp=0.30`, combined-stress run-clean is 65% for Tx-Full versus 25% for Checkpoint-Replay. This is the clearest quantitative evidence that checkpoint recovery and external-effect settlement are distinct capabilities.

### Fault-class isolation
τ-bench retail, `fp=0.10`, N=30 per cell:
- Tx-Full: F2 post-effect/pre-return 63% [44,80]; F4 duplicate-delivery 67% [47,83].
- Checkpoint-Replay: 57% [37,75] / 57% [37,75].
- Saga: 43% / 70%.
- OCC: 40% / 53%.
- Mutex+WAL: 33% / 57%.
- No-Frontier: 37% / 67%.
- TCC: 20% / 63%.
- No-Tx: 30% / 73%.

This isolates post-effect/pre-return failures as especially damaging to mechanisms that cannot jointly track execution and settlement. Duplicate delivery alone is much easier for conventional idempotency-style defenses.

### Bursty-fault sensitivity
At marginal fault probability ≈0.12 (entry 0.04, burst length 3, N=30): Tx-Full 67%, Checkpoint-Replay 57%, TCC 60%, No-Tx 60%, Mutex+WAL 50%, No-Frontier 47%, Saga 43%, OCC 40%. The ordering narrows relative to independent Bernoulli faults because fewer distinct failure episodes occur per task.

### Scope / negative result retained
Atomix does not claim semantic validation, distributed deployment, or full crash-safe exactly-once. Reversible eager effects may be externally visible before compensation. If multiple heterogeneous irreversible releases must commit and one succeeds before a later release irrecoverably fails, atomic externalization across endpoints is impossible above the tool layer. Missing or incorrect scope/effect annotations can fail open.

## Updated synthesis
The strongest Atomix lesson is narrower than `transactions improve agents`:
- **checkpoint replay is competitive for recoverable internal/environment state**, sometimes statistically tied with Tx-Full;
- **effect-class-aware commit/gating is what prevents checkpoint recovery from duplicating irreversible external actions**;
- therefore recovery should be evaluated on a joint surface: task success + leak/residue + stale-write/conflict + latency/cost, not task success alone.

This aligns with ACRFence's 10/10 duplicate-commit restore attack and strengthens the conclusion that agent-state rollback and world-effect rollback are separate safety domains.

## Nonempty frontier after this addendum
1. **Checkpoint frequency / rewind-depth policy**: find controlled ablations of how often to checkpoint, where to place checkpoints, and how far to rewind; measure both recovery and cost.
2. **AgentRewind primary-table verification** remains unresolved.
3. **Independent / alternative irreversible-effect defenses**: look for implemented semantic replay/fork or server-side effect-ledger evaluations beyond Atomix; distinguish proven defenses from attack-only proposals.
4. **Compression hidden-cost causal breakdown**: inspect the 2026-08-17 compression paper's oracle restoration tables for queryable vs history-dependent state.
5. **Subgoal decomposition failure**: seek controlled LLM-agent cases where wrong/rigid decomposition hurts.
6. **Active memory by demand type**, UltraHorizon CRNR extraction, and LongDS per-pattern recovery remain unresolved.
7. **Post-hoc selection vs online intervention** remains open: test cost-adjusted final success where online correction has high disruption.

## Exact continuation
Next run first action: search primary long-horizon/checkpoint-recovery papers for **checkpoint placement frequency and rewind-depth ablations**, prioritizing controlled final-task A/B plus compute/latency/storage cost. Then verify AgentRewind exact primary tables if a primary rendering is available, and keep compression/subgoal negative-evidence branches nonempty.