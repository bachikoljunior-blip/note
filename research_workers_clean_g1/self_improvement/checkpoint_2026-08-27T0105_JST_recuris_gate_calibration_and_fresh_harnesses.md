# Self-improvement clean checkpoint — Recuris gate calibration and fresh harness evidence

checkpointed_at: 2026-08-27T01:05:42+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier
source_qualified_id: `SIG1-RECURIS-GATE-CALIBRATION`

## Frozen semantic control tuple
- note main SHA at semantic freeze: `404199cfbfce168f401f696f291c58eb669d3c62`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0004_JST_sealed_audit_accounting_boundary.md`

Only own role-local clean state, own sanitized feedback, sanitized root/config, and public sources were used semantically. No O, other-worker, downstream, legacy, shared-ledger, or other-role semantic state was read.

## Public sources inspected in this continuation
1. `noumenal-ai/audit-compression-progress` public source, especially `experiments/cp_experiments.py`, to finish the release-channel semantics audit from the predecessor frontier.
2. `Recursive Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses`, arXiv:2608.24876v1, and its public implementation `Gen-Verse/Recuris` at observed main `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`, especially README, `src/recuris/metaagent/gate.py`, `gates.py`, and the production `driver.py` path.
3. `StarHarness: Evolving Harnesses with Stratified Search for Enterprise Environments`, arXiv:2608.24804v1.
4. `CAFE: Self-Improving Search Agents Need Co-Evolving Feedback`, arXiv:2608.24794v1.
5. Fresh public search for official PACE/SEA certificate implementations and a >10-proposal live agent satisfying the full long-loop statistical contract. No complete system satisfying that conjunction was established in this continuation.

## Material finding 1: Audit-CP's release defenses are empirically useful channel restrictions, not fresh-data mechanisms
The public E7 implementation confirms the exact semantics that were only partly resolved in the predecessor checkpoint:
- `fresh_subsample` samples a random half of the **same reusable audit panel** on every adaptive query. It does not draw a new population sample.
- `rounded` releases the same reusable-panel score after 4-bit rounding.
- `ladder` releases improvement only when it exceeds a noise-scale threshold `R/sqrt(n)` relative to the best released value.
- `one_shot` returns `0.0` scalar feedback during the attack/query loop, then the final selected parameter is evaluated afterward.
- A separate fresh/sealed panel is used for the reported final comparison.

This sharpens the contract: these defenses alter the **release-channel capacity** of one reusable panel. The measured E7 protection should not be relabeled as a theorem that repeated fresh subsampling from the same panel is indefinitely reusable. A source-version contract should test the channel semantics directly, because a label such as `fresh_subsample` can otherwise be misread as new independent data.

## Material finding 2: Recuris is a fresh practical example of deterministic, evidence-gated persistent memory evolution
Recuris keeps the downstream model frozen while a meta-agent proposes localized edits to a structured Skill Memory. The public README states that a deterministic validation gate decides survival from paired held-out evidence and that no model votes on its own patch. It reports improvement in 35/37 completed model-benchmark pairs, including +17.8 points for GPT-5.6 Sol on tau-bench and +16.6 points for Qwen3.6-27B on SkillFlow; gains grow with interaction horizon, reaching +32.2 points on the longest tasks.

The repository also exposes a useful negative boundary: on Terminal-Bench 2.1, keeping the same memory package but adapting it between repeated attempts gives 60.9% versus 58.6% for fixed M0 at four attempts, only +2.3 points, and the README explicitly says this is **not significant at the available sample size**. This is unusually good reporting discipline for a self-improvement system and prevents a small adaptation effect from being promoted into a stronger claim.

## Material finding 3: the production gate is stronger than the standalone CLI gate, so executable-path binding matters
Two gate implementations coexist:

### Standalone `src/recuris/metaagent/gate.py`
It computes a paired task-level bootstrap CI, but the actual `accept` boolean is:
- diagnosed repair improves,
- held-out net mean > 0,
- regressions <= `reg_cap`.

`lo > 0` is reported only as `significant`; a nonsignificant candidate may still print `ACCEPT` for the stack.

### Production `src/recuris/metaagent/gates.py` used by `driver.py`
The production driver imports `held_out_paired_gate` from `gates.py`. That gate accepts only if:
- the paired bootstrap lower confidence bound is > 0, and
- materially regressed held-out items <= `reg_cap`.

The driver workflow then describes Phase V as lint/leak/repair/dev-set compound validation and Phase K as the only promotion/discard boundary.

Therefore a gate contract must bind to the **exact executable path and source revision**, not only the project name or a similarly named helper. Otherwise an auxiliary CLI with materially weaker semantics can accidentally be cited as if it were the production admission rule. This is a concrete source-version regression-test target.

## Material finding 4: Recuris explicitly calibrates a small-sample failure regime instead of assuming a bootstrap is valid everywhere
The production driver contains unusually specific calibration notes for dense partial-credit tasks. Its hierarchical estimator resamples task clusters and paired trials within the selected tasks. The code/commentary records true-null false-accept rates for `p < .05` of roughly:
- 26.5% at 1 cluster,
- 9.4% at 2,
- 7.4% at 3,
- 5.7% at 4,
- 4.9% at 5,
- 4.1% at 8,
under the stated `k=2` calibration setup.

At `k=1`, even 5 and 14 clusters were reported at 9.3% and 7.5%, so the path says it cannot certify in that regime. It sets a minimum of 5 task clusters and at least 2 trials for the calibrated dense setting, and uses a material movement threshold (default 0.05) so tiny partial-credit noise does not consume the hard regression cap.

This is stronger evidence for a general design rule than the mere presence of a bootstrap: **the actual sample regime of the admission statistic must be null-calibrated, and unsupported small-n regimes should fail closed rather than return impressive-looking p-values.** This directly complements the earlier SGM theorem/implementation audit.

## Material finding 5: Recuris still does not close the long-loop sequential-selection frontier
The public quick-start evolution example is 4 rounds with `k=4`, progressive round gating, a power warning and regression cap 1. The repository states that every round writes the evidence, plan, gate arithmetic and ledger entry, and that a round admitting nothing is valid.

However, in this continuation I did **not** establish:
- a candidate-local anytime-valid e-process/confidence-sequence promotion rule for indefinite optional stopping;
- durable cross-candidate familywise error spending across proposal rounds and process restarts;
- an experiment with >10 proposals that combines those controls;
- atomic crash-safe binding among exact candidate artifact hash, statistical state, gate verdict, ledger append and live promotion;
- that the final reported benchmark test is never used by proposal generation, promotion, rollback, retirement, early stopping or checkpoint selection.

Thus Recuris is a strong practical validation-gated persistent-memory system, not yet evidence for the full long-horizon statistical contract that remains on this worker's frontier.

## Material finding 6: two new same-day papers sharpen complementary parts of the self-improvement loop
### StarHarness — search/selection/held-out task separation
StarHarness fixes model weights and evolves prompt/framing, tools, skills, MCP providers, subagent structure and loop configuration. It separates proposer-visible search tasks from proposer-hidden selection tasks and reserves held-out tasks for generalization. The paper reports +20–35 percentage points over the default harness after 4–12 accepted changes per environment across ITBench SRE, EnterpriseOps-Gym ITSM and AutomationBench Finance, with gains persisting on tasks excluded from evolution and transferring across GPT/Qwen model families.

This is useful fresh evidence that **search evidence, selection evidence and final generalization evidence should be distinct**. The abstract alone does not establish repeated-selection-safe statistics, full proposal chronology, or an untouched final lockbox, so those remain open checks rather than inferred properties.

### CAFE — the feedback policy itself can become the bottleneck
CAFE alternates a shared-parameter model between search-agent and critic roles, using comparative call-vs-skip feedback utility online and matched successful/failed trajectory preference learning offline. It reports gains across seven search benchmarks, retained gains on six OOD benchmarks and reduced answer hallucinations. One-sided ablations show that improving only the agent or only the critic plateaus, while alternating both continues improving.

This supports a narrow mechanism-level claim: when failure patterns shift as the policy improves, a **fixed feedback generator can become a stale bottleneck**. It does not directly establish safe persistent harness promotion because it is an RL/weight-update setting, so it belongs on the diagnostic/feedback-supply side of the decomposition rather than the admission-gate side.

## Structured artifact persisted
A source-bound contract was added at:
`research_workers_clean_g1/self_improvement/recuris_gate_contract_2026-08-27T0105_JST.json`

It records the exact production/auxiliary gate split, statistical unit, finite-sample calibration, nonstatistical checks, published default round configuration, unestablished long-loop properties and next executable audits.

## Self-improvement design update
The strongest current decomposition is now:

`diagnostic/feedback supply -> bounded/versioned proposal -> warrant/fingerprint/integrity checks -> source-version-bound production admission statistic -> null-calibrated finite-sample regime -> candidate-local promotion -> durable cross-candidate risk state if familywise control is required -> signed sealed-potential lineage accounting -> rollback/retirement -> untouched outer test`

Two new engineering requirements are now explicit:
1. **Executable-path identity is part of the statistical contract.** A helper/CLI with the same conceptual name but weaker acceptance semantics is not equivalent evidence.
2. **The gate's supported sample regime is part of the contract.** A p-value/CI procedure should carry empirical or formal null calibration for the actual clustering/trial design and fail closed outside it.

## Evidence limits / non-claims
- No claim that Recuris's full published gain is caused solely by the validation gate; it is a multi-component system.
- No claim that Recuris solves repeated adaptive reuse of a fixed held-out selection set.
- No claim that StarHarness's hidden selection split is reusable-holdout safe under arbitrary repeated proposals; the abstract establishes task separation, not a sequential-testing theorem.
- No claim that CAFE's critic co-evolution transfers directly to persistent memory/harness safety.
- No claim that Audit-CP `fresh_subsample` creates fresh independent audit data; it samples from the same reusable panel.
- No claim that a >10-proposal live agent satisfying all desired statistical and durability controls has been proven absent; it was not established in this continuation.

## Exact continuation frontier
1. Trace Recuris production `driver.py` from `held_out_paired_gate` through Phase K, and audit whether candidate artifact hash, gate evidence, ledger mutation and live promotion are transactionally/atomically coupled across crashes and restart.
2. Map Recuris train/repair/dev/final split use, including checkpoint/best-version/rollback/early-stop logic, to determine whether any final benchmark test is genuinely untouched by adaptive selection.
3. Inspect released Recuris round artifacts for complete proposal chronology and search for >10-proposal campaigns; test whether repeated use of the same dev/held-out set has any spending/query-budget/sequential correction.
4. Add source-version regression contracts for Audit-CP release-channel semantics and for the Recuris `gate.py` versus production `gates.py` divergence; include protected estimand, sign/clipping, independent unit, formula, sample reuse, calibration regime, spending and outer-test isolation.
5. Continue official implementation search for PACE/SEA and audit any candidate-local certificate state for restart durability plus atomic promotion coupling.
6. Read StarHarness full method/code if released to recover total proposals versus accepted changes, selection-set reuse and final held-out isolation; continue search for a >10-proposal live agent with candidate-local anytime-valid evidence, durable cross-candidate spending, complete chronology and a genuinely untouched outer test.
7. Continue randomized/crossover artifact-specific retirement searches rather than relying on pooled skill-level correlation.

This checkpoint is not completion.
