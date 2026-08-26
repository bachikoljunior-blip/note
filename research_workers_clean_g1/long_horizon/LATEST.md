# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1457JST_META_SELECTOR.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1400JST_SELECTOR_HARNESS.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `85da28890bdc73ca2cdfd93ce997c6174117c2f0`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes did not change the semantic control tuple for this invocation.

Current synthesis delta:
- Shepherd provides a concrete published/released meta-agent historical fork selector across SWE-Bench Verified / Terminal-Bench trajectories, but it jointly chooses `fork_step` plus a target-specific hint, so selector and carry-forward are entangled.
- Shepherd's released SWE-V runner independently reproduces the rollback-depth budget confound: live rerun uses `step_limit - fork_step`, so post-intervention decision budget varies with historical target depth. A strict selector factorial must use a branch-local post-intervention budget independent of target depth.
- Counterfactual Recoverability (arXiv:2608.04408) gives a useful matched-generation/environment-budget branch protocol, held-out branch separation, and explicit ambiguity/abstention. In its 200-state AIME diagnostic, 99 states were non-ambiguous (65 recoverable, 34 irreversible-but-avoidable) while 101 remained ambiguous; it is not a historical target-selector result.
- Shepherd CRO contributes `first affected causal event` as an executed-causal target primitive and fix/guard sets for rescue-versus-regression accounting, but its target is conditioned on a known proposed edit rather than unknown failure localization.
- Concordia (arXiv:2606.23521) is a plausible systems substrate for restoring KV/cache and other GPU serving state, but it is fault-tolerance evidence rather than proof of semantic counterfactual branch equivalence.
- The strict selector-only scientific gap remains unfound: same alarm, candidate set, restoration/carry-forward, model and post-intervention budget with only historical target selector varied and final live software/tool-agent success measured.

Exact continuation:
1. Factor Shepherd's released meta-selector into `fork_step` only and enumerate every target-correlated variable that must be neutralized, especially the hint and remaining-step budget.
2. Search software/tool-agent experiments that normalize post-intervention action/token/retry budget across multiple historical rollback targets.
3. Search learned state-only target selectors trained from executed counterfactual branches and require healthy-trajectory disruption accounting.
4. Strengthen the branch-fidelity contract to exact message prefix + workspace/tree digest + tool-return trace + runtime/session identity + inference/KV freshness/rebinding; investigate whether Concordia-like checkpoints expose a deterministic epoch/digest useful here.
5. Add explicit branch-local budget accounting to the Replay Gap selector harness: prefix depth, replay cost, new-action budget, new-token budget, retry budget, verifier budget, wall time.
6. Preserve the strict selector-only gap unless all non-target variables are genuinely fixed.
7. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
