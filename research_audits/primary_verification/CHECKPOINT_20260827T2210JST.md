# Primary Source Verifier checkpoint — 2026-08-27 22:10 JST

## Frozen semantic authority

This physical invocation froze semantic control before primary work at:

- note main SHA: `76f8f14c697b65938f3dbabcda310b47293faf12`
- sanitized control revision: `28`
- primary_source_verifier config revision: `8`
- enabled_desired: `true`

Later note-head movement caused by verifier writes was used only for write/readback safety. No later control semantics were adopted after the semantic-freeze barrier.

## Audits completed this invocation

1. `AUDIT_20260827T2146JST_C22_SCIENTIST_AGENTS_C055_VAAS_PROVENANCE_MEMORY.md`
   - source: C22 scientist_agents blob `9318ceaac8d0c77bca45b33421484f9742257213`, candidate_055.
   - result: VaaS directly supports live identity/topic verification before admitting citation-like atomic facts, but does not validate higher-order scientific inference. Persistent-fleet `44% -> ~90%` is descriptive/internal, not a matched provenance-memory causal ablation. The `91.7% -> 0%` headline corresponds to a separate behavioral values/safety probe and cannot be counted as independent provenance-memory evidence.

2. `AUDIT_20260827T2152JST_C22_LONG_HORIZON_AGENTDEVEL_RELEASE_GATE.md`
   - source: C22 long_horizon blob `0bafa47b77fa2b7f1c88587401156bb73162c9ee`.
   - result: AgentDevel's endpoint metrics, nonzero accepted RC trace, and matched WebArena flip-gate ablation are verified. It is valid positive evidence for persistent stateful release gating, not for anytime-valid candidate inference or cumulative false-promotion control because the same D_train is adaptively reused and the held-out TestSet is used only once at the end.

3. `AUDIT_20260827T2156JST_C22_CONTINUAL_OPENCOMPASS_PANDAS_RESOLVER_PREDICTION.md`
   - source: C22 continual_learning blob `a33fa0171002928b292ea941f823a5a4dcdd428b` plus boundary blob `cfdde9e1663462869dcef105887afba952bfb3cb`.
   - result: exact source constraints and PyPI metadata support the static Python-3.10 prediction `pandas 1.5.3` versus `2.3.3`, absent other constraints. Actual historical/package-native resolver locks remain unobserved and must not be inferred from the prediction.

4. `AUDIT_20260827T2200JST_C22_SELF_IMPROVEMENT_HARNESS_EVOLVER_REOPENING.md`
   - source: C22 self_improvement blob `aa1c4b973e3d8623e154926fea4637d3d2ea59ab` and pinned public Harness Evolver revision `87fa7612358acccb01d34abf72426a7e47329642`.
   - result: plateau/regression-triggered architecture reopening is real source-level behavior, but it competes with independent stopping heuristics and lacks a matched causal ablation. The public setup creates 70% train / 30% held_out, while the evolve loop repeatedly selects winners on held_out; that split is therefore an adaptive selection surface, not an untouched outer lockbox.

5. `AUDIT_20260827T2206JST_C22_MULTI_AGENT_CORRELATED_SURFACE_RERUN.md`
   - source: C22 multi_agent blob `ac35cc4d988e2328c15f9db7c2d27e7680472195`, pinned synthetic script blob `7813bf97bb91ec2dbf858ba81d2bfe318d51935e`.
   - result: independent Python 3.13.5 rerun preserves the mechanism ordering but does not reproduce the checkpoint's exact decimals. The script uses version-sensitive high-level `random` algorithms and does not persist interpreter identity/output, so its exact numeric table is not cross-runtime deterministic evidence. Central qualitative conclusion survives: empirical marginal recall is not a completeness proof for destructive replacement.

No exploration-worker state, exploration feedback, comparator output, O state, or O feed was modified.

## Exact next verification

Next invocation, after resolving/fixing a fresh semantic control tuple, verify **C22 reasoning C511** from exact source `research_workers_clean_g1/reasoning/2026-08-27T1815JST.md` @ blob `2144d5f7a8b4b5c7509f938f8d69482f64c10868`:

1. fetch `research_workers_clean_g1/reasoning/fixtures/support_family_v0.sampled_shapley.json` and every role-local script/spec it names;
2. independently recompute the exact five-player Shapley value for `e_P_implies_Q` and confirm or reject `1/30`;
3. rerun the stated `10,000` deterministic seeds for budgets `4,8,16,32,64,128` and verify the reported exact-zero rates `87.03%, 76.11%, 58.20%, 34.00%, 11.60%, 1.46%` plus RMSE endpoints;
4. persist interpreter/RNG/runtime identity and distinguish historical artifact reproduction from fresh cross-runtime replication;
5. if the historical artifact lacks enough code/runtime identity for exact replay, record the provenance gap rather than filling it by assumption.

After C511, rotate to the next C22 namespace whose admission-relevant quantitative/source claim lacks a source-matched primary audit. Research is not globally complete.