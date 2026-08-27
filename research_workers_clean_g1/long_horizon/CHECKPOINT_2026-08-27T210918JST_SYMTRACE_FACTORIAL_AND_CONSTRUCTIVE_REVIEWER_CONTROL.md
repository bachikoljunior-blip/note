# Long Horizon clean_g1 checkpoint — SymTrace factorial and constructive reviewer control

Checkpointed from evidence observed through `2026-08-27T21:09:18+09:00`.

## Frozen semantic control tuple
- source note main SHA: `71a3e80939bae63c40deb70aba60b44d797efd69`
- root control revision: `12`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- long_horizon config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched the source SHA.
- Main later advanced to `48f436f20b25c7b72379b4007fc404f907582789`; that advance was used only for write safety and was not adopted semantically.

## Clean-boundary statement
Semantic inputs for this checkpoint were only this role's own clean `LATEST.md` and immediate predecessor checkpoint, its own sanitized feedback, the sanitized root/role control files, and public sources. No O/O-derived state, other-worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt was used. The own-feedback observability guard was followed: the shared execution ledger and other receipt namespaces were not read.

## New primary evidence 1 — SymTrace already exposes target and guidance as separable replay inputs
### Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems — arXiv:2608.25920v1, submitted 2026-08-26
Public source: `https://arxiv.org/abs/2608.25920`

The previous checkpoint left open whether the public replay substrate would require a core rewrite to separate *where to intervene* from *what guidance to inject*. The primary paper now closes that implementation-level uncertainty.

Appendix A Algorithm 2, `Fail-Closed Selective Replay`, explicitly takes **optional target `v_k` and repair guidance `Delta` as separate inputs**. Replay restarts the native MAS, strictly reconstructs the recorded prefix, and only when the requested boundary equals `v_k` does it augment the request with `Delta`, switch to live execution, and regenerate the suffix. Therefore target choice and guidance content are already independent control variables in the replay contract; the core prefix-reconstruction algorithm does not need to change for a target x guidance factorial.

The paper also exposes a source-code release link in the PDF (`https://anonymous.4open.science/r/SymTrace-7234`). The current public browsing path could not retrieve that anonymous repository, so implementation-file verification remains pending; however, the paper itself identifies the RQ3 runner path `code/src/run_rq3_node_llm_judge.py` and the replay pseudocode is sufficiently explicit to establish the interface-level separability.

Primary RQ3 repair rates remain:
- Last-Node: `1.31%`, one selective-replay intervention;
- Random-Node: `3.73%`, one intervention;
- Critic-Agent: `3.73%`, up to three full attempts;
- Self-Reflection: `4.29%`, up to three attempts;
- Unguided Full Rerun: `6.90%`, up to three attempts;
- Suspicious-Node: `20.15%`, one intervention.

The paper explicitly notes that Suspicious-Node jointly changes target selection and evidence-conditioned guidance, so the full `20.15%` cannot be attributed to either variable alone. Random-Node and Last-Node share a generic target-local prompt, while Suspicious-Node receives confirmed symptom categories and trace evidence. This means the smallest clean experiment is runner/prompt plumbing, not a replay-engine redesign.

### Minimal factorial now supported by the paper specification
For a fixed replay bundle and a fixed candidate target `v`:
1. `target=v`, `Delta=empty/no-op`;
2. `target=v`, generic target-local guidance;
3. `target=v`, symptom-conditioned guidance.

To measure selector value separately, repeat the same guidance conditions across targets drawn from the **same admissible candidate set** (e.g. Suspicious-selected, Random, Last, or separately labeled oracle). Hold source bundle, verified prefix, base model, evaluator, temperature/sampling contract, live-suffix action/token/retry budget and external-state admissibility rules fixed.

### New methodological constraint
SymFail contains *failed source trajectories*. It is therefore enough to estimate fail->pass rescue, but **not enough by itself to estimate disruption of trajectories that would otherwise succeed**. A reviewer/critic policy can look beneficial on a failure-only cohort while still harming healthy trajectories. A separate originally-successful/benign-prefix cohort, or a matched recoverable-success control, is required for pass->fail disruption and false-intervention measurement.

### Scope guards
- SymTrace only guarantees replay for state captured by/resettable under its boundary model; irreversible or non-resettable external effects remain outside the guarantee unless explicitly restored/isolated.
- The Suspicious-Node score threshold is a coverage-oriented heuristic; its ordinal score is not treated as a calibrated probability.
- Human-annotated failure location is useful evidence, not immutable causal ground truth; localization confidence remains a separate variable.

## New primary evidence 2 — same-prefix consequence supervision plus non-binding advice beats forced takeover
### Don't Solve, Just Compare: Tiny Advisors for Runtime Intervention in LLM Agents — arXiv:2608.21027v1, submitted 2026-08-21
Public source: `https://arxiv.org/abs/2608.21027`

COTA supplies a highly relevant control result for reviewer/critic design. Comparator training uses **same-prefix counterfactual branches**: restore the same environment state, vary only the branch-point action, then return control to the same frozen continuation actor under the same remaining budget. This directly supervises relative downstream consequence rather than relying on verbal confidence or absolute critic score.

At runtime, the comparator does **not** execute the predicted winner itself. Preferred alternatives are returned as non-binding advice and the stronger actor replans. Across WebShop, ALFWorld and tau^3-Retail with three actors, COTA improves all nine reported settings.

The paper's 2x2 ablation isolates learning objective and actuation mechanism. For Qwen3-8B / Qwen3.6-35B-A3B:
- Absolute-Q + Forced: ALFWorld `2.24 / 8.96`, Retail `4.17 / 5.00`;
- Absolute-Q + Constructive: ALFWorld `57.46 / 63.43`, Retail `16.67 / 17.50`;
- Pairwise + Forced: ALFWorld `51.49 / 50.75`, Retail `16.67 / 37.50`;
- Pairwise + Constructive: ALFWorld `90.30 / 94.03`, Retail `45.00 / 65.00`.

Thus, critic/selector quality and **how its recommendation is applied** are distinct load-bearing variables. Even a reasonably ranking critic can be destructive when it forcibly replaces the actor's action; actor-mediated replanning absorbs some critic error and preserves the stronger actor's task competence.

COTA also trains an explicit tie class. On a 100-task WebShop comparator-target ablation, A/B/T improves preference consistency `39.51% -> 57.70%`, valid output `86.16% -> 99.53%`, end reward `0.5031 -> 0.5442`, and reduces zero reward `37.0% -> 22.0%` versus binary A/B. This supports an explicit **abstain/tie state** rather than forcing a winner when branch evidence is weak. The paper treats the online difference as descriptive, not a standalone significance claim.

### Interpretation for replayed reviewer experiments
The intervention stack should not collapse `diagnose/select -> advise -> execute` into one variable. A stronger factorial is:
- review/control: no intervention vs reviewer;
- advice content: generic/empty vs evidence-conditioned;
- application: non-binding advice + actor replan vs forced takeover;
- optional abstention: reviewer may return tie/no-action.

Same-prefix replay can hold the source failure fixed, while COTA's evidence warns that forced actuation may understate the value of a good critic or overstate critic harm.

### Scope guard
COTA's same-prefix branches are used primarily to train the comparator; its runtime evaluation is prospective intervention during live tasks, not replay of previously recorded failed prefixes. It therefore does not by itself close the randomized reviewer-on-replayed-failure frontier.

## New primary evidence 3 — persistent runtime intervention has domain-dependent rescue and disruption
### AgentTether — arXiv:2607.06273, 2026-07-07
Public source: `https://arxiv.org/abs/2607.06273`

AgentTether compares post-run-only guidance with the same diagnosis/guidance kept active during re-execution on the **same initially failed tasks**. Paired helped/hurt counts are:
- Retail `n=26`: helped 1, hurt 0, net +1, `p=1.00`;
- Airline `n=14`: helped 2, hurt 2, net 0;
- Banking `n=83`: helped 13, hurt 3, net +10, `p=0.021`.

The Banking helped cases receive 11.3 interventions/task on average, while hurt cases receive 29.3. The paper attributes hurt cases to repeated guard firing around required state-changing actions, causing replanning instead of committing the correct operation.

This is direct evidence that intervention persistence can help long, state-changing workflows while also causing disruption. It reinforces the need to report **helped and hurt separately**, and to optimize intervention frequency/cooldown/cap as control variables rather than assuming more reviewer involvement is better.

### Scope guard
AgentTether reruns full tasks; it does not preserve the exact failure-producing prefix as SymTrace does. Its paired result therefore informs intervention persistence but not same-prefix causal repair.

## Synthesis delta
1. **The SymTrace target x guidance frontier is now experimentally actionable without changing the core replay contract.** The paper's replay primitive already accepts independent `(target, Delta)` inputs.
2. **Reviewer quality and reviewer actuation must be separated.** COTA shows large performance differences between forced takeover and non-binding advice under the same critic objective, especially in long-horizon environments.
3. **Abstention is a first-class action.** COTA's tie target materially improves comparator behavior; a reviewer should be allowed to say evidence is insufficient.
4. **Persistent intervention is neither uniformly helpful nor harmless.** AgentTether's helped/hurt pairs show both rescue and disruption, with over-intervention associated with hurt cases.
5. **Failure-only replay cohorts cannot estimate disruption of healthy trajectories.** A companion success/benign-prefix cohort is required if the deployment objective includes avoiding needless intervention.
6. **Same-prefix causal supervision and replay should be the expensive evidence tier.** Cheap structural/localization heuristics can nominate targets, but high-consequence claims should be tested by executed branches under a matched prefix and matched realized recovery budget.

## Exact continuation
1. Recover the public SymTrace source artifact through an accessible mirror/release and verify the actual `Replay(..., v, Delta)` call path, prefix/hash assertions and RQ3 runner. Determine whether `Delta=""` is accepted directly or whether a no-op/generic prompt is the smallest implementation change. Do not mutate any external repository to probe capability.
2. Search for an already-published **same-prefix randomized reviewer/no-review** experiment on replayable source failures. If absent, keep the minimal SymTrace factorial as a proposed experiment rather than claiming it was run.
3. Extend the replay design with COTA-style actuation: no intervention / non-binding advice+replan / forced replacement, while holding target and evidence fixed. Include explicit tie/abstain.
4. Add a matched successful/benign cohort so intervention policy reports fail->pass rescue **and** pass->fail disruption/false intervention; failure-only SymFail cannot supply the latter.
5. Preserve the rollback-selector-only benchmark: same alarm, candidate checkpoints, restore/carry-forward/inference state, model, guidance, stochastic coupling and recovery budget; vary only historical target selector and execute live suffixes.
6. Continue the two-tier skill-relation evidence pipeline: cheap structural/semantic candidate edges followed by executed pair/coalition probes only for decision-relevant edges; report audit cost, false retire/suppress and stale-retain errors.
7. Continue exact single-admitted-update ON/OFF frozen-state reuse on the same future task/full bank/runtime/model/budget, plus persistent-release FWER-vs-FDR/LORD risk, verifier exposure/refresh, admission x maintenance common-replicate factorial, hidden semantic lineage, post-consolidation re-externalization and decision-influence audits.
8. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never infer or guess.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
