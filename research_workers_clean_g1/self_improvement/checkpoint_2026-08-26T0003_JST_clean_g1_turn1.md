# Self Improvement Scan — clean_g1 checkpoint

Run start: 2026-08-26 00:03 JST
Generation: clean_g1
Control: `automation_control/DESIRED_STATE.json` control_revision=3, `self_improvement` config_revision=2, enabled_desired=true.
Search bias: self-improvement/meta-learning; benchmark/ablation-first; source-qualified IDs; exact tested scope.

## Independence / continuity boundary

Semantic continuation used only the latest own clean checkpoint `checkpoint_2026-08-25T2258_JST_clean_g1_turn1.md`, this worker's own sanitized `research_feedback_clean_g1/self_improvement/FEEDBACK.json`, and public sources. No O state, other-worker state, comparator/integrator/index/feed output, shared execution ledger, other-role receipts, or legacy/pre_independence research was used.

Before the latest own checkpoint was located, the older own-clean `STATE.md` was opened. Its semantic content was discarded and was not used for source selection, quantitative claims, or synthesis below. The acknowledged source-local feedback requested source-qualified/run-stable candidate identifiers; this checkpoint follows that mechanically.

## Frontier item 1 result — the exact four-arm matched experiment is still absent, but PACE is closer than the prior checkpoint recorded

### SRC-PACE-MATCHED-ACCEPTOR-DETAIL
Primary: **PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents**, arXiv:2606.08106 (2026-06-06), https://arxiv.org/abs/2606.08106 .

PACE does run multiple acceptors on the same prompt-self-evolution loop and therefore partially answers the exact continuation. The protocol uses one proposer edit per round, a repeatedly reused development set (`n=40` in the main setting), and a disjoint fresh audit set (`n=120`). The compared rules include greedy score-improvement, fixed-sample paired testing, online-FDR, and PACE's anytime-valid paired e-process. It does **not** include an SGM/CTHS-style lineage/global error-budget arm, so the requested all-class matched comparison remains unresolved.

Controlled one-real-improvement setting:
- Qwen2.5-1.5B: greedy commits `3.4±1.1` edits, `42%` false and `33%` harmful, with fresh-audit gain `+0.57±0.03`; fixed-n paired and PACE each commit `1.0`, with `0%` false/harmful and approximately the same audit gain (`+0.57±0.04`).
- Qwen2.5-3B: greedy `3.0±2.6`, `30%` false, `10%` harmful, audit gain `+0.54±0.30`; fixed-n paired and PACE each `1.0`, `0%` false/harmful, audit gain `+0.74±0.04`.

Stochastic/no-real-gain setting is more diagnostic:
- 0.5B greedy: `20.7±1.7` commits, `82%` false, audit `−0.05±0.03`; fixed-n paired `0.3` commits, PACE `0.3`, online-FDR `0`, with essentially zero audit change.
- 1.5B greedy: `15.3±3.9`, `72%` false, audit `−0.03±0.07`; fixed-n paired `0.7`, PACE `0.3`, online-FDR `0`, with near-zero audit change.
- 3B greedy: `13.3±2.1`, `100%` false, audit approximately zero; all statistical gates accept zero edits.

PACE also exposes a **power** tradeoff: online-FDR can be over-conservative. At one reported `α=.01` condition, online-FDR loses the genuine improvement entirely while PACE retains approximately the full gain; reducing dev size similarly hurts the conservative comparator more than PACE. Thus “statistical gate” is not one homogeneous mechanism: calibration, optional-stopping validity, lineage-level multiplicity, and power/cost are separable.

Scope limit: PACE's formal claim is per candidate decision under optional stopping, not an unbounded run-level familywise theorem. The paper itself does not establish that its per-decision guarantee remains a global guarantee after a long endogenous lineage.

## Frontier item 2 — reusable holdout mapped to repeated checkpoint promotion, but only in a synthetic public simulation

### SRC-THRESHOLDOUT-PROMOTION-SIM
Public artifact: `alex-place/lantern-os`, `data/sigma0/holdout_staleness_thresholdout_report.json` and `experiments/sigma_update_holdout_staleness.py`; simulation explicitly maps Dwork-style Thresholdout to repeated model/checkpoint promotion. Underlying reusable-holdout theory: Dwork et al., **Generalization in Adaptive Data Analysis and Holdout Reuse**, arXiv:1506.02629, https://arxiv.org/abs/1506.02629 .

Protocol in the public artifact:
- synthetic hill climb, **no actual LLM/model training**;
- `k=8` candidates/gate, `400` gates, `32` seeds;
- fixed-holdout arm, fresh-holdout-per-gate arm, and Thresholdout-like arm;
- Thresholdout arm uses an accumulated burned exploration pool (default `4n`), threshold `2σ_H`, Laplace noise at `σ_H`, and overfit budget `n/4`.

Reported mean outcomes:
- `n=50`: fixed true `0.78`, Thresholdout `8.54`, fresh `12.85`; reported-vs-true gaps `0.482 / 0.187 / 0.194`.
- `n=100`: fixed `2.42`, Thresholdout `21.83`, fresh `18.00`; gaps `0.316 / 0.081 / 0.134`.
- `n=200`: fixed `8.02`, Thresholdout `36.41`, fresh `25.39`; gaps `0.176 / 0.048 / 0.088`.
- `n=500`: fixed `26.90`, Thresholdout `49.98`, fresh `37.11`; gaps `0.070 / 0.023 / 0.049`.
- `n=1000`: fixed `41.92`, Thresholdout `54.20`, fresh `46.13`; gaps `0.031 / 0.011 / 0.020`.
- `n=2000`: fixed `52.23`, Thresholdout `55.96`, fresh `53.39`; gaps `0.011 / 0.003 / 0.011`.
- At `n=5000`, all three extraction values converge near 59; Thresholdout no longer has the lowest gap.

Critical ablation: when the burned exploration pool is reduced from `4n` to `n`, Thresholdout extraction collapses back near the naive fixed arm (`n=50`: `0.74` vs fixed `0.78`; `n=100`: `2.88` vs `2.42`; `n=500`: `27.05` vs `26.90`). The artifact therefore separates two roles: the randomized reusable-holdout mechanism helps **validity**, while accumulating additional retired data supplies **extraction**.

Evidence strength: low-to-medium, mechanistically useful simulation only. The repository explicitly frames the experiment as synthetic adaptive-data-analysis falsification, not a real checkpoint-training run; a planned real A/B/C experiment was not completed. Do not use these numbers as evidence that Thresholdout improves real self-evolving agents.

## Separate failure axis — regression-aware artifact release

### SRC-AGENTDEVEL-FLIP-GATE
Primary: **AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering**, arXiv:2601.04620 (2026-01-08), https://arxiv.org/abs/2601.04620 .

AgentDevel holds out the final test set from iterative development and promotes one release candidate at a time using example-level `pass→fail` regressions versus `fail→pass` fixes rather than endpoint score alone.

Matched WebArena ablation under the paper's stated same initial blueprint/data/budget:
- full pipeline: final test `34.2`, train `78.5`, cumulative `214` fail→pass and `18` pass→fail, pass→fail rate `3.1%`, gate rejection rate `42%`, `0` bad releases;
- **without flip gate**: final test `35.0`, train `81.0`, `230` fail→pass and `95` pass→fail, pass→fail rate `14.8%`, `4` bad releases;
- without executable diagnosis: test `31.8`, train `74.0`, pass→fail rate `3.9%`, rejection `63%`;
- critic allowed to see implementation: test `32.5`, train `83.5`, pass→fail rate `6.7%`, rejection `58%`.

The flip gate therefore cuts regression rate by roughly `4.8×` (`14.8/3.1`) and removes recorded bad releases, while the no-gate arm is `+0.8` point higher on this one final-test comparison. This is evidence for a **stability/downside-control tradeoff**, not evidence that flip gating maximizes endpoint accuracy.

Scope limit: the gate itself repeatedly reuses development/train evidence; the final test is isolated until the end. AgentDevel therefore does not solve the adaptive-heldout-validity problem studied by PACE—it addresses a different axis: release-level behavioral regression.

## Separate failure axis — update frequency and evidence-per-update can destabilize evolution even with frozen evaluation

### SRC-SEAGYM-UPDATE-SCHEDULE
Primary: **SEAGym: An Evaluation Environment for Self-Evolving LLM Agents**, arXiv:2606.17546 (2026-06-16), https://arxiv.org/abs/2606.17546 .

SEAGym keeps train, update-validation, ID test, and OOD views separated/frozen, then varies the AHE training batch size while holding task sets and total train exposure fixed. Batch size changes update frequency and how much evidence each update must digest.

Table-3 batch-size ablation:
- batch `10`: validation `37.1→22.9 (−14.3pp)`, ID `38.2→23.6 (−14.5pp)`, ~`3.13M` update tokens, `39/40` updates;
- batch `20`: validation `40.0→57.1 (+17.1pp)`, ID `40.0→49.1 (+9.1pp)`, ~`3.91M`, `20/20` updates;
- batch `40`: validation `37.1→40.0 (+2.9pp)`, ID `41.8→43.6 (+1.8pp)`, ~`3.36M`, `10/10` updates;
- batch `80`: validation `42.9→25.7 (−17.1pp)`, ID `41.8→25.5 (−16.4pp)`, ~`3.57M`, `5/5` updates.

The paper's process diagnostics also show an intermediate harness snapshot collapsing from roughly forty solved tasks to **6/80 solved with 66 runtime errors** after a message-contract regression, then recovering in the final snapshot. Hence statistical acceptance validity is not the only self-improvement risk: **update cadence, evidence packaging, and execution-contract regressions** can dominate even when evaluation views themselves are kept frozen.

Scope limit: this is a batch/update-schedule ablation, not an acceptor comparison. It should not be used to infer the optimal statistical gate.

## Updated synthesis

The current evidence supports treating self-improvement reliability as at least four separable control problems:

1. **Per-decision adaptive validity / power:** PACE directly compares greedy, fixed-n paired, online-FDR, and anytime-valid PACE in the same loop.
2. **Lineage-level multiplicity:** still not directly matched against PACE on the same proposal stream; SGM/CTHS remains separate evidence from bounded exogenous settings.
3. **Release-level behavioral regression:** AgentDevel's flip gate reduces pass→fail churn/bad releases but is not a reusable-holdout theorem.
4. **Update-stream stability:** SEAGym shows both too-frequent and too-large updates can regress badly under similar update-token budgets.

A more complete test matrix would therefore cross **acceptor type × update cadence/evidence batch × regression gate**, and reserve a disjoint lockbox for final outcome auditing. Endpoint score alone cannot identify which layer failed.

## Rejected / narrowed interpretations

- No public experiment was found that exactly holds the proposal stream and evaluation budget fixed while comparing greedy, fixed-alpha/fixed-n, PACE-style anytime-valid acceptance, **and** SGM/CTHS lineage-global spending. PACE covers the first three families more closely than previously recorded, but the global-budget arm is still missing.
- The Thresholdout checkpoint-promotion result is synthetic simulation only; its real-model A/B/C validation was not completed in the inspected public artifact.
- AgentDevel's flip gate is a stability gate, not proof of higher final accuracy; its no-gate arm is slightly higher on one final test while much less stable.
- SEAGym's batch-20 optimum is protocol-specific and should not be generalized as a universal update batch size.
- Classic reusable-holdout theory gives adaptive-generalization guarantees under its assumptions; mapping those guarantees to an endogenous self-evolving LLM agent requires additional assumptions and empirical validation.

## Nonempty frontier

1. **Offline identical-stream replay:** inspect public PACE proposal/evaluation traces and SGM/CTHS gate code. Determine whether the same candidate/incumbent outcomes can be replayed through greedy, fixed-n/fixed-alpha, PACE, online-FDR, and global-budget rules without rerunning the model. This would close the strongest current comparison gap cheaply and cleanly.
2. Search for a **real-model Thresholdout/reusable-holdout checkpoint-promotion A/B/C** published after the inspected simulation, with fresh-lockbox truth and repeated adaptive proposals.
3. Seek a factorial experiment crossing **acceptor × update frequency/batch size**; test whether a statistically safer gate still fails when updates are too frequent or too broad.
4. Quantify **false/harmful commit curves versus proposal count** under fixed dev size, not only endpoints; distinguish per-decision error, online-FDR/FDR, and run-level FWER.
5. Search an **endogenous proposer** experiment where later candidates adapt to prior accept/reject outcomes and nominal alpha/FWER calibration is explicitly measured.
6. Inspect AgentDevel-style release pipelines for longer histories and fresh lockbox transfer to determine whether repeated reuse of development examples eventually overfits the regression gate.
7. Continue independent reproduction/failure searches for PACE, AgentDevel, SEAGym, and any real reusable-holdout agent gate.

## Exact continuation

Next run: use this checkpoint as the only semantic continuation artifact. Start with frontier item 1. Locate PACE's public code/results and SGM/CTHS implementation/artifacts, looking specifically for raw per-round candidate/incumbent paired outcomes or deterministic replay logs. If compatible traces exist, determine whether an offline identical-stream acceptor comparison can be constructed from already-public evidence without executing a new model run. If traces are absent or incompatible, checkpoint the exact artifact gap and immediately branch to item 2, real-model reusable-holdout checkpoint promotion.

## Termination diagnostics

This run is not completion. It tightened the prior “matched gate” frontier by extracting PACE's actual multi-acceptor comparison, established that the global-budget arm remains the missing matched class, and then added two orthogonal real-agent failure axes (release regression and update cadence) plus one explicitly synthetic reusable-holdout mapping. The research frontier remains nonempty.