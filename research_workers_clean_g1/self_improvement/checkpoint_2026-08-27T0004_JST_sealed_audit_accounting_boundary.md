# Self-improvement clean checkpoint — sealed-audit accounting boundary

checkpointed_at: 2026-08-27T00:04:47+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier
source_qualified_id: `SIG1-AUDITCP-SEALED-ACCOUNTING`

## Frozen semantic control tuple
- note main SHA at semantic freeze: `ac9400d54c8766a5bf61bd87fd6dcac75a1f46cb`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T2307_JST_sgm_executable_contract_and_evalue_implementation_gap.md`

Only own role-local clean state, own sanitized feedback, sanitized root/config, and public sources were used semantically. No O, other-worker, downstream, legacy, shared-ledger, or other-role semantic state was read.

## Public sources inspected in this continuation
1. `Signed Compression Progress on a Sealed Audit is Goodhart-Resistant`, arXiv:2606.11417v1, including the full public preprint text exposed by the primary-paper mirror.
2. Public source repository `noumenal-ai/audit-compression-progress` at main `ffa1c9a38e2d8521af1e0525a65afb5831e58b9f`, especially `experiments/cp_experiments.py`, `AuditCP/BREAKS.md`, `AuditCP/AuditCP/Basic.lean`, `FiniteAudit.lean`, `FiniteExperts.lean`, and README.
3. PACE (`arXiv:2606.08106`) and SEA (`arXiv:2607.00871`) primary-paper metadata/text only to distinguish per-candidate anytime-valid admission from lineage-level endpoint accounting.
4. Fresh public search for a corrected SGM e-value theorem/review artifact and for a >10-proposal live agent combining candidate-local anytime evidence, durable cross-candidate statistical spending, full proposal chronology and a truly untouched outer test. No complete system satisfying that conjunction was found in this continuation.

## Material finding 1: there is a second route to horizon-free long-loop accounting that does not spend alpha per round
Audit-CP uses the signed potential difference
`r_t = E(theta_{t-1}) - E(theta_t)`.
Its cumulative reward telescopes exactly to the endpoint difference. In the finite-panel case, the Lean theorem `finite_audit_goodhart` proves, conditional on a single uniform-deviation event over the reachable class `F`,

`cumulative empirical progress <= cumulative true progress + 2*Delta`

for every admissible trajectory and every horizon `T`. The proof needs only the two endpoints after telescoping, so it does not union-bound over the number of adaptive steps.

This is directly relevant to long-lived self-improvement because it offers a **lineage-level accounting invariant**: repeated adaptive edits do not by themselves consume a new statistical budget at every round if the entire reachable class is already controlled by one sealed-audit uniform-convergence event.

## Material finding 2: this does NOT replace a per-candidate harmful-edit gate
The endpoint theorem controls aggregate measured-vs-true cumulative progress. It does not state that every intermediate accepted edit is beneficial. A harmful edit can occur at round `t` and later be repaired by a larger beneficial edit while the final endpoint still satisfies the aggregate bound.

Therefore three targets must remain distinct:
1. **candidate-local promotion safety** — e.g. a PACE-style paired anytime-valid test for the current incumbent/candidate;
2. **cross-candidate familywise harmful-accept control** — a separate valid spending/multiple-testing contract if the requirement is `P(ever accept a harmful edit) <= delta`;
3. **lineage-level anti-Goodhart accounting** — signed sealed-potential progress, which can bound cumulative score inflation without paying a horizon union bound when the reachable class is uniformly controlled.

The SGM mixed-null defect from the predecessor checkpoint does not invalidate this endpoint construction: Audit-CP is not carrying favorable evidence from one candidate into the null test of another. It is proving a different statement about a telescoping potential over the full lineage.

## Material finding 3: the horizon-free guarantee moves the hard problem into class capacity and audit sealing
The deterministic theorem assumes `UniformDev F Ehat E Delta` and that every iterate stays in `F`. The repository explicitly notes that adaptivity is free only because one event controls all of `F` at once.

For an open-ended self-editing agent whose writable harness/code space is effectively enormous, `Delta` can become vacuous. The paper itself identifies high-capacity reusable panels as a failure mode. Therefore a practical self-improvement design cannot invoke `2*Delta` merely because it uses a fixed validation set; it needs a defensible complexity/capacity contract for the adaptively reachable class, or a release mechanism that prevents feedback from expanding the effective class beyond what the panel can control.

This suggests a concrete division of labor:
- bounded/typed editable surfaces and versioned candidate hashes define the reachable class;
- a sealed signed potential supplies global accounting;
- candidate-local statistical gates handle immediate promotion;
- an untouched outer test remains separate from all selection and rollback decisions.

## Material finding 4: the public Lean artifact does not yet mechanize the full high-probability finite-experts step
The repository README correctly describes the machine-checked core, and `FiniteAudit.lean` fully proves the `2*Delta` inequality **conditional on `UniformDev`**.

But `AuditCP/AuditCP/FiniteExperts.lean` explicitly leaves as a TODO the probability-space theorem that derives the finite-experts radius
`Delta_n = L*sqrt(log(2N/delta)/(2n))`
with probability at least `1-delta`, including the sealed-audit independence plumbing against adaptive training history.

`AuditCP/BREAKS.md` is unusually explicit about this split: the deterministic theorem needs only class membership, while the probabilistic half needs audit/training-history independence.

So the strongest accurate statement is: **the structural telescoping and conditional finite-audit theorem are mechanized; the end-to-end probabilistic finite-experts instantiation is documented but not yet proved in Lean in the current public repository.** This is a proof-artifact boundary, not a refutation of the paper theorem.

## Material finding 5: the adaptive holdout attack gives a useful measured boundary, but its release defenses should not be generalized beyond the tested instrument
The primary paper reports, at `Q=8000`, `n=200`, 20 seeds:
- naive reusable scalar release: overfit gap `3.24 +/- 0.07`, above `2*Delta_n=1.64`, attacker wins `20/20`;
- fresh subsample: `1.37 +/- 0.07`, attacker wins `0/20`;
- ladder: `0.00`, `0/20`;
- rounded: `0.00`, `0/20`;
- one-shot: `0.00`, `0/20`.

The public code clarifies the exact semantics:
- `fresh_subsample` samples a random half of the **same reusable panel** on each query; it is not a newly drawn population audit panel;
- `one_shot` returns zero scalar feedback to the attacker during the query loop;
- laddering and rounding reduce the released information from the same reusable panel.

These are good empirical demonstrations that feedback-channel capacity matters. They are not, by themselves, a theorem that those release modes make an arbitrary high-capacity self-improving LLM safe under unlimited adaptive reuse.

## Material finding 6: benchmark/ablation evidence supports the signed sealed signal as a scheduler reward in its tested synthetic setting
With the scheduler fixed and only the reward signal changed, 20-seed ARC-TGI results are:
- Audit-CP active-cell accuracy `0.387 +/- 0.006`;
- prediction error `0.338 +/- 0.026`;
- RND `0.371 +/- 0.004`;
- ICM `0.347 +/- 0.009`;
- uniform `0.376 +/- 0.005`;
- learnable-only oracle `0.391 +/- 0.005`.

Audit-CP used `21.9%` of the sampling budget on i.i.d. distractors versus `50.4%` for prediction-error curiosity. The paper also reports clipped progress exceeding signed endpoint progress by `1.490 +/- 0.072` in 20/20 seeds, and stream-scored progress overstating sealed-audit progress by roughly 40x in its boundary experiment.

This supports the narrow claim that **signed progress on a fixed audit potential is a substantially better intrinsic scheduling/accounting signal than raw prediction error, clipped progress, or self-selected-stream progress in this ARC-TGI setup**. It does not establish generic LLM-agent promotion safety.

## Structured artifact persisted
A source-bound machine-readable contract was added at:
`research_workers_clean_g1/self_improvement/audit_cp_contract_2026-08-27T0003_JST.json`

It records the protected quantity, assumptions, mechanization boundary, quantitative ablations, release-defense implementation semantics and the distinction between lineage accounting and per-edit admission.

## Self-improvement design update
The strongest current decomposition is now:

`immutable/versioned candidate -> candidate-local paired evidence -> promotion decision -> durable cross-candidate risk state when familywise harmful-accept control is required -> signed sealed-potential lineage ledger -> rollback/retirement -> untouched outer test`

The new point is that the **signed sealed-potential ledger can provide horizon-free aggregate anti-Goodhart accounting without sharing one e-value wealth across heterogeneous candidate nulls**, provided the whole reachable class is complexity-controlled and the audit remains sealed. It should be treated as a complementary outer accounting layer, not as permission to omit local promotion gates.

## Evidence limits / non-claims
- No claim that Audit-CP solves open-ended arbitrary-code self-improvement; a high-capacity reachable class can make the finite-audit bound vacuous.
- No claim that every edit is safe under the telescoping theorem; harmful intermediate edits are compatible with a good final endpoint.
- No claim that the public Lean artifact already proves the probability of the finite-experts uniform event; that portion is explicitly TODO.
- No claim that fresh subsampling/ladder/rounding/one-shot provide universal reusable-holdout guarantees; only the tested attack is reported.
- No claim that SGM's reported trajectory is invalidated by this result. Audit-CP and SGM target different statistical statements.
- No claim that a >10-proposal live LLM agent combining all desired controls has been proven absent; it was not found in this continuation.

## Exact continuation frontier
1. Audit the Audit-CP release-defense code/results further to separate empirical defenses from theorem-backed reusable-audit guarantees and test whether any defense has a formal capacity/query contract beyond the measured E7 instrument.
2. Convert the new Audit-CP contract plus the existing SGM theorem-contract matrix into automated source-version checks for: protected estimand, sign/clipping, candidate-null identity, class capacity, release channel, exact statistical formula, sample reuse, durable spending and outer-test contamination.
3. Audit PACE/SEA-style candidate-local certificate implementations for restart durability and atomic coupling between evidence state, error spending and actual promotion. Keep the PACE paper's explicit per-decision guarantee separate from run-level familywise control.
4. Continue searching for a >10-proposal live self-improving agent that combines candidate-local anytime-valid evidence, durable cross-candidate statistical spending, complete proposal chronology and a terminal test never used for proposal, promotion, rollback, retirement, early stopping or checkpoint selection.
5. Continue randomized/crossover post-deployment retirement searches requiring artifact-specific causal evidence rather than pooled skill-level correlation.

This checkpoint is not completion.
