# CLEAN self-improvement checkpoint — DarwinX held-out regression and replay boundary

Run timestamp: 2026-08-26 12:57 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `33bbbaf6ca1d718842b393bea574e0b6a96f0616`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1157_JST_transactional_rollback_and_outer_lockbox.md`.

Semantic inputs used were only predecessor/own role-local state, own sanitized mechanical feedback, and public sources/public implementation repositories. No O/O-derived state, other worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used. Source-qualified IDs continue per acknowledged mechanical feedback.

## SIG3-DARWINX-OUTER-MERGE-REGRESSION

Official DarwinX project artifacts materially sharpen the distinction between an in-loop preserve-and-extend contract and actual hidden-distribution monotonicity.

TerminalWorld protocol on the official project page:
- evolution uses 94 verifier-scored training tasks;
- after evolution the harness is frozen and evaluated once on 41 disjoint held-out tasks;
- held-out evaluation is single-attempt pass@1 with no retries/best-of-k, so held-out reward cannot feed back into the archive;
- four evolved specialists solve 24/25/26/27 of the 41 held-out tasks; their union covers 29;
- the realized merged harness solves 28/41;
- the merge solves `tw_448247`, which none of the four specialists solve, but loses `tw_449421` and `tw_498533`, which at least one specialist solves;
- 21 held-out tasks are solved by all four specialists and 12 by none.

This is a useful counterexample to treating an admission-time `preserve inherited solves + extend coverage` contract as a guarantee of outer monotonicity. The project describes preserve-and-extend on measured evolution evidence, while the disjoint held-out panel shows that the realized recombination can both add a capability unseen in any parent and lose capabilities present in its parents. This is not a protocol contradiction: the merge contract is enforced on in-loop evidence, whereas the losses occur on unseen tasks. It is direct evidence that in-loop Pareto preservation does not entail preservation on a hidden outcome distribution.

Scope guard: these are single attempts on only 41 tasks, one task = 2.4 points. The authors explicitly report the matched Opus comparison 25/41 vs 28/41 at McNemar p=0.45, so the aggregate improvement is suggestive rather than decisive. The specific gain/loss task identities are still valuable as mechanism-level evidence of hidden-distribution recombination error.

Design implication: merged persistent artifacts should themselves be treated as new candidates, frozen and independently validated. A deterministic `union-of-known-wins` rule on visible evidence should not be interpreted as a no-regression certificate. Where evidence is stochastic, promotion should preserve uncertainty/confidence bounds and retain parent snapshots for rollback.

Primary/official project source:
- https://huggingface.co/spaces/CoderDoge/darwinx/commit/7a3b3da1bb12d33c7ce5d6e6d10ac4f5252afa4b
- https://arxiv.org/abs/2608.07545

## SIG3-DARWINX-PROXY-GAP-SUPPORTS-DIVERSITY-BUT-NOT-COMPONENT-CAUSALITY

The same official TerminalWorld artifacts expose a large proxy/generalization gap:
- training-subset proxy increases from 0.505 to 1.000;
- held-out pass@1 is 68.3%, a 31.7-point gap;
- the variant that best fits the proxy is not the best held-out generalizer;
- the four high-scoring specialists cover overlapping but different held-out subsets and the realized merge reaches 28/41.

This supports preserving multiple lineages when the adaptive proxy is overfit: scalar best-tracking can discard complementary capabilities. It does **not** isolate the causal contribution of the archive, recombination, parent selector, or inference effort. The project limitations explicitly say those operators are not independently randomized.

Operational implication: a self-improver should track at least `(visible fitness, capability-set evidence, lineage/diversity, outer outcome)` rather than collapse selection into one scalar. Diversity is an insurance mechanism against proxy misspecification, but recombination still needs its own promotion test.

## SIG3-DARWINX-PUBLIC-CURVE-IS-SUMMARY-REPLAYABILITY-NOT-FIXED-PROPOSAL-REPLAYABILITY

The official project page releases more run-derived observability than was visible in the paper alone. It says eight interactive figures are generated from real run artifacts or paper plotting scripts, and `assets/data.js` contains all 37 WebArena-Infinity screening scores from `notes/tw_dynamics.json -> wai_adaptive_scores`:

`[19.67, 58.33, 41.67, 50.0, 50.0, 50.0, 50.0, 58.33, 70.0, 51.79, 58.33, 57.14, 51.79, 67.86, 55.56, 58.93, 60.71, 70.0, 57.14, 67.86, 55.56, 38.42, 70.0, 77.78, 70.0, 34.42, 77.78, 77.78, 70.0, 62.5, 70.0, 77.78, 70.0, 77.78, 70.0, 77.78, 70.0]`.

Simple deterministic analysis of that released curve gives only four strict new scalar bests (indices 0, 1, 8, 23), eight later ties with the then-best, and 25/37 variants strictly below the running best. This is evidence that the search trajectory is highly non-monotone and that persistent best-state/versioning matters. It is **not** an accepted/rejected-candidate count because DarwinX admission depends on per-task evidence and archive classification, not scalar score alone.

Crucially, fixed-proposal counterfactual replay is still unavailable from the public project page:
- the project README says archive lineage node/edge data lives in a cluster `state.db` and is not present on the project-page machine;
- code is currently offered "on request" rather than as a public implementation bundle;
- the public curve gives scalar screening scores, but not candidate hashes/diffs, parent hashes, full paired task evidence, admission verdicts, rejected variants, merge lineage, or per-candidate compute.

Thus DarwinX currently provides **summary replayability** (important curves/per-task held-out matrices can be regenerated) but not **fixed-proposal replayability** sufficient to hold proposals constant while swapping acceptance rules.

Minimum useful future release for acceptor replay: immutable candidate id/hash + full diff/snapshot; parent ids; per-task incumbent/candidate trials; evaluator version/config; structured admission verdict; accept/reject/rollback result; merge parents; compute/token/tool budget; archive state transition; final hidden outcome bound to the promoted candidate hash.

## SIG3-ADAPTIVEHARNESS-CANONICAL-RELEASE-STILL-LACKS-PAPER-RUN-BUNDLE

Artifact search was extended from the mirror to the canonical `A-EVO-Lab/a-evolve` release branch. GitHub branch discovery confirms `release/adaptive-auto-harness`; the inspected release branch contains source, experiments, data, evaluations, scripts and seed workspaces, but recursive tree/code search did not surface committed `nav_evo_*` trajectory outputs, `history.jsonl` paper-run logs, or a workspace Git bundle. Search results locate writer/orchestration code rather than paper-run output.

The public AdaptiveHarness issue #1 asks authors to host PolyBench/CTF-Dojo/FutureX datasets on Hugging Face, remains open with no comments, and does not expose a run-history bundle. Therefore the prior artifact-access conclusion survives a stronger canonical-release check: the system can generate replay-oriented local telemetry, but the currently inspected public release does not supply the exact paper-run proposal chronology needed for fixed-proposal acceptor replay.

Public sources:
- https://github.com/A-EVO-Lab/a-evolve/tree/release/adaptive-auto-harness
- https://github.com/A-EVO-Lab/AdaptiveHarness/issues/1

## SIG3-HARNESSOPT-OUTER-LOCKBOX-ARTIFACT-LOCATION-UNRESOLVED

Fresh public search confirms HarnessOpt-Bench remains a strong outer-lockbox design: the held-out test partition stays inaccessible throughout search, a trusted execution environment enforces the boundary/meters resources, candidate versions are preserved, and one final nominee is scored on test. Scale Labs lists the paper dated 2026-08-06.

However, an official public artifact bundle/repository containing the execution traces and candidate versions described in the paper was not surfaced in the fresh searches conducted here. `scaleapi/vero` is relevant infrastructure but no HarnessOpt-specific public path was identified. This is an artifact-location gap, not evidence that the artifacts do not exist.

Primary source:
- https://arxiv.org/abs/2608.06301
- https://labs.scale.com/papers

## Updated synthesis

The long-horizon self-improvement target is now better decomposed:

1. **Population/diversity can hedge an overfit adaptive proxy**, as DarwinX TerminalWorld shows, but scalar archive fitness and hidden generalization can diverge sharply.
2. **Recombination is itself a risky edit.** A merge that preserves/extends visible evidence can lose parent capabilities on untouched tasks; parent snapshots and independent merge admission are required.
3. **Outer lockbox and inner promotion are separate controls.** DarwinX has useful disjoint outer evaluation; HarnessOpt has a particularly strong physical test boundary; neither observation supplies repeated-selection-safe promotion inside a >10-cycle persistent lifecycle with fixed-proposal replay.
4. **Replayability must bind decisions to immutable candidates.** Public score curves are insufficient for causal acceptor comparison unless the exact candidate stream and paired evidence are also released.
5. **Transactional candidate isolation remains relevant.** AdaptiveHarness's prior untracked/exception rollback and mutable-verifier boundary remains a concrete implementation reason to prefer disposable immutable candidate environments.

The highest-information experiment remains: freeze a real >10-cycle proposal stream; materialize every candidate as an immutable disposable worktree; run a read-only structured verifier against paired incumbent/candidate evidence; replay greedy, fixed-alpha, per-candidate anytime-valid, and global-spending admission over the identical stream; preserve parallel lineages; validate merges as fresh candidates; and perform one final HarnessOpt-style partition that has never influenced proposal generation, routing, rollback, retirement, merging, best-state selection or early stopping.

## Exact continuation

1. Search the official DarwinX/Salesforce release surfaces for a later public code/run-artifact drop containing `state.db`, archive lineage, candidate diffs, trial evidence or compute logs; if released, reconstruct exact accepted/rejected/merge chronology and test fixed-proposal acceptor replayability.
2. Search HarnessOpt/Scale Labs/VeRO releases for the exact trace/candidate artifact location promised by the paper; identify the minimum signed binding between final candidate commit and hidden-test record.
3. Search >10-cycle real-agent systems for a merge/recombination admission rule with paired evidence or confidence bounds, especially systems that explicitly test merged descendants rather than infer safety from parent wins.
4. Continue the broader target search for one system combining immutable candidate snapshots, read-only structured verifier, exception-safe whole-worktree rejection, repeated-selection-safe admission, complete proposal chronology, persistent lineage lifecycle, and a genuinely untouched final partition.
5. Preserve matched-total-compute controls, source-qualified IDs, exact tested scope, and separate observability for artifact quality, exposure, activation/adherence, promotion, persistence, and outer outcome.

Frontier remains nonempty. No global completion is claimed.