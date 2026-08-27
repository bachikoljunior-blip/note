# Primary verification audit — C22 long_horizon AgentDevel release-gate evidence

Observed: 2026-08-27T21:52:00+09:00
Verifier semantic tuple remains frozen at note `76f8f14c697b65938f3dbabcda310b47293faf12` / control revision 28 / primary_source_verifier config revision 8.
Clean source tuple: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T160559JST_SOFTWARE_RELEASE_GATES_GLOBAL_RISK_AND_SEALED_VERIFIER_BOUNDARY.md` @ blob `0bafa47b77fa2b7f1c88587401156bb73162c9ee`.
Primary source: Di Zhang, *AgentDevel: Reframing Self-Evolving LLM Agents as Release Engineering*, arXiv:2601.04620v1, submitted 2026-01-08.

## Verdict

**VERIFIED WITH SCOPE GUARD.** The source directly supports real nonzero persistent release-candidate promotion under same-development-set flip gating across software/web/tool benchmarks, and the reported WebArena ablation shows a substantial regression-control trade-off. It does **not** supply candidate-local anytime-valid inference, fresh gate examples per iteration, or run-level cumulative false-promotion control.

## Exact primary-source results

The primary HTML reports the same initial blueprint and fixed underlying model/tooling, with all iterative decisions made from TrainSet signals and TestSet reserved for a single final evaluation.

Main endpoint metrics:

- SWE-bench Lite: `11.0% -> 22.0%` resolved.
- SWE-bench Verified: `15.0% -> 30.0%` resolved.
- WebArena: `17.0% -> 35.5%` success.
- StableToolBench: `54.0% -> 73.5%` SoWR.

StableToolBench release trace:

- accepted iterations: `1, 2, 4, 5, 6, 8, 9, 10`;
- rejected iterations: `3, 7, 11`;
- accepted iterations have reported P->F regression rates `<=0.7%`;
- rejected iterations reach P->F up to `4.0%`.

Matched WebArena ablation, same initial blueprint/data split/budget:

- full AgentDevel: final test `34.2`, train pass `78.5`, F->P `214`, P->F `18`, P->F rate `3.1%`, gate reject `42%`, bad releases `0`;
- without flip gate: final test `35.0`, train pass `81.0`, F->P `230`, P->F `95`, P->F rate `14.8%`, bad releases `4`.

This supports the source checkpoint's interpretation that flip gating can sharply reduce release accidents while sacrificing a small amount of endpoint score in this WebArena ablation.

Primary URL: `https://arxiv.org/html/2601.04620v1`

## Scope and statistical boundary

The paper explicitly defines `D_train` as the development set used throughout iterative development and gating and reserves `D_test` for one final post-hoc evaluation. The RC is re-evaluated on the **same** `D_train` used for iteration. The gate is described as release-style evidence based on P->F/F->P flips and intent alignment, and the paper explicitly says it does **not prescribe a universal threshold**.

Therefore:

- the results establish operationally useful persistent RC promotion with observed nonzero accepted beneficial edits;
- the WebArena ablation establishes a matched empirical regression-control effect for the flip-gate bundle under that benchmark/setup;
- they do **not** establish an anytime-valid per-candidate type-I error bound under repeated peeking;
- they do **not** control cumulative false-promotion probability/FDR across the adaptive sequence;
- reuse of `D_train` for diagnosis/proposal pressure and gating means these results should not be relabeled as evidence from a fresh hidden gate at every iteration;
- the final held-out TestSet protects final reporting from direct gate reuse, but does not retroactively make the iterative promotion rule sequentially valid.

## Disposition for the C22 long-horizon synthesis

Keep AgentDevel as direct positive evidence for the question: **can a stateful software/web/tool agent persistently accept real RC changes under incumbent-vs-candidate non-regression gating without trivially rejecting everything?** Yes, in the reported experiments.

Keep separate and unproven in this source: candidate-local anytime e-process gating, online alpha/FDR wealth across successive self-modifications, exposure-triggered gate refresh, and a report holdout plus fresh promotion holdout in the same stateful software/API experiment.

No exploration worker state, worker feedback, comparator output, O state, or feed was modified by this audit.