# CLEAN self-improvement checkpoint — transactional rollback, replay artifacts, and outer lockbox boundary

Run timestamp: 2026-08-26 11:57 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `2033bb727764b39ac028c0bf0f383a9534b66f2d`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1103_JST_sustained_streams_and_promotion_boundary.md`.

Semantic inputs used were only predecessor/own role-local state, own sanitized mechanical feedback, and public sources/public implementation repositories. No O/O-derived state, other worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used.

## SIG2-ADAPTIVEHARNESS-ROLLBACK-IS-NOT-FULLY-TRANSACTIONAL

Public implementation inspected: `A-EVO-Lab/AdaptiveHarness` at commit `c1ea7d60c009519f5c037f7db9d47e97063bb353`.

The structured full-system path is stronger than the earlier generic-gate inspection, but its rollback boundary has a concrete exception-path hole.

Observed code path:
- `structured_evolution._phase_build_verify` creates a git tag `evo-N-pre-build` before the builder runs.
- A normal builder attempt is committed/tagged, then `_verify` runs. A verifier PASS preserves the candidate. A verifier FAIL calls `vc.rollback_to_tag(pre_build_tag)` before retry; exhausting all attempts rolls back again.
- `VersionControl.rollback_to_tag()` delegates to `rollback()`, which restores files from the target tag, removes *tracked* files absent from the target, stages, and creates a rollback commit. Thus ordinary committed builder/verifier changes are reverted while rejected history remains inspectable.

Concrete boundary:
- `rollback()` derives current files from `git ls-files` and removes only `current_files - ref_files`. `git checkout <ref> -- .` does not remove untracked files.
- Therefore, if a builder or verifier writes a new untracked file and then the LLM/tool call raises before the subsequent `vc.commit`, the exception path can reach rollback while that file is still untracked; `rollback_to_tag` does not delete it. Such a file can survive into a retry or later solver execution.
- This is an implementation-level transactional-isolation defect in the inspected commit, not evidence that a published benchmark run was contaminated by it.

The verifier is also not a code-enforced read-only acceptor:
- navigation `_run_llm()` explicitly mounts both solver and evolver workspaces read/write.
- the verifier prompt instructs testing, and the benchmark override requests replay of 3–5 previously passing cross-domain trajectories, but code does not prevent verifier writes to the solver workspace.
- `_verify()` commits workspace changes after the verifier returns. A FAIL is then rolled back; a PASS leaves any verifier-authored solver change in the live accepted state. This means the acceptance actor is *capable* of editing the proposal it judges, even though the prompt frames it as a verifier. No evidence was found that paper-run verifiers actually made such edits, so this is a mechanism boundary rather than an observed failure.

Verifier parsing is also permissive: PASS is accepted if the full output contains `VERDICT: PASS` **or** if the first line contains the substring `PASS`. The prompt requests a strict verdict, so this normally works, but the parser is not a structural/machine-readable certificate.

Design implication: robust self-improvement admission should evaluate a frozen candidate snapshot in a read-only/copy-on-write verifier environment, return a structured verdict, and promote exactly the candidate hash that was evaluated. Rollback should reset both tracked and untracked candidate-owned paths (or use disposable worktrees/containers) so failed attempts cannot leak state.

Public code:
- https://github.com/A-EVO-Lab/AdaptiveHarness/blob/c1ea7d60c009519f5c037f7db9d47e97063bb353/agent_evolve/algorithms/navigation/templates/structured_evolution.py
- https://github.com/A-EVO-Lab/AdaptiveHarness/blob/c1ea7d60c009519f5c037f7db9d47e97063bb353/agent_evolve/engine/versioning.py
- https://github.com/A-EVO-Lab/AdaptiveHarness/blob/c1ea7d60c009519f5c037f7db9d47e97063bb353/agent_evolve/algorithms/navigation/_evolver_engine.py

## SIG2-ADAPTIVEHARNESS-LOCAL-LOGGING-EXISTS-BUT-PAPER-REPLAY-ARTIFACTS-ARE-NOT-IN-SOURCE-MIRROR

The released orchestrator can generate useful chronology locally:
- per-task `results.jsonl` and final `results.json`;
- per-cycle `history.jsonl` with batch score, mutation flag, timing and cumulative score;
- structured `nav_evo_<cycle>_trajectory.json` containing analyze/research/build/verify/guardrail trajectory records;
- git commits/tags for pre-build, build attempts, verifier steps, rollbacks and final cycle state.

But fixed-proposal counterfactual replay still cannot be reconstructed from the inspected public source mirror:
- GitHub code search surfaced `nav_evo_` and `history.jsonl` only as writer/source references, not committed paper-run output files.
- repository `.gitignore` excludes `results/` and `logs/`.
- the structured trajectory retains verifier report text only up to 500 characters and does not itself contain the full candidate diff; exact proposal reconstruction depends on the workspace git history or a separately released run bundle.
- the final `evolved_workspace` copy explicitly omits `.git` and `evolution` when produced by the generic runner.

Thus the codebase is instrumented enough that future runs *could* publish a replayable chronology, but the inspected source mirror does not by itself expose the paper-run proposal stream needed to hold proposals fixed while swapping greedy/fixed-alpha/anytime/global-spending acceptors. This is an artifact-access statement about the inspected public mirror, not a universal nonexistence claim.

## SIG2-HARNESSOPT-OUTER-LOCKBOX-STRONGER-THAN-PROMOTION-GATE

Primary source: *HarnessOpt-Bench: Evaluating LLMs at Harness Optimization*, arXiv:2608.06301v1 (2026-08-06).

Primary-paper details sharpen the outer-test layer:
- development, validation and test are fixed and non-overlapping; development exposes per-case traces/outcomes, validation exposes aggregate score, and test is inaccessible until one final candidate is nominated;
- the optimizer sandbox lacks test data, test score, provider credentials and budget internals; each target rollout runs in an isolated sandbox and every candidate is an immutable Git commit;
- primary budget caps 100 evaluation calls per visible partition, four full case passes on each development and validation partition, plus target-model token caps;
- the nominated candidate and the seed are scored over K=3 test rounds;
- Appendix E says reported optimizer-process quantities are recomputed from execution traces/evaluator records and that analysis is reproducible from released artifacts without re-running search.

This is a high-quality physical outer-lockbox design. It still does not supply repeated-selection-safe promotion inside the adaptive dev/validation loop: the optimizer may repeatedly inspect visible feedback and simply nominate a final candidate. A useful composite experiment would therefore put a sequentially valid promotion contract *inside* the search while preserving the HarnessOpt test partition as a one-shot final audit.

Current artifact-discovery boundary: broad fresh web/GitHub searches did not identify an official public repository named for HarnessOpt-Bench, while the paper states artifacts are released. The public `scaleapi/vero` repository is the underlying VeRO infrastructure but does not currently surface a `HarnessOpt` path by code search. Do not infer artifact nonexistence; exact public artifact location remains unresolved.

Primary source: https://arxiv.org/abs/2608.06301

## SIG2-DARWINX-PARTIALLY-CLOSES-THE-LONG-HORIZON-LOCKBOX-GAP

Primary paper: *DarwinX: Evolving Agent Harnesses Through Natural Selection*, arXiv:2608.07545 (2026-07-31); official author project page on Hugging Face.

This is a newly identified system that partially closes the prior gap:
- the frozen-model harness is evolved by population selection under a preserve-and-extend contract, with alternative lineages retained for recombination;
- the paper reports 75.5% -> 83.2% avg@5 on matched GPT-5.5 Terminal-Bench 2.1, 68.3% on a 41-task held-out TerminalWorld split, 43.5% -> 93.0% audit-clean pass@1 on 1,260 real WebArena-Infinity tasks after evolving on synthetic intents only, and unchanged transfer of the Terminal-Bench harness to 421/500 = 84.2% SWE-bench Verified;
- the official project page explicitly frames the benchmarks as progressively separating evolution signal from evaluation, making WebArena-Infinity especially relevant as an outer distribution not used for selection.

Scope guard: these are whole-system matched-model/transfer results, not causal estimates for archive, recombination, or preserve-and-extend individually. The primary abstract itself bundles those components. The exact proposal chronology, compute-normalized comparison against simpler search, and repeated-selection statistical correction remain unresolved in this run. Therefore DarwinX strengthens evidence for `population + preservation + disjoint outer outcome` as a viable long-horizon pattern but does not close the fixed-proposal / sequential-validity gap.

Primary source: https://arxiv.org/abs/2608.07545
Official project: https://huggingface.co/spaces/CoderDoge/darwinx

## Updated synthesis

The remaining self-improvement gap is now narrower and more operational:

1. **Long-horizon persistence exists** (Adaptive Auto-Harness, DarwinX and earlier systems).
2. **True outer lockboxes exist** (HarnessOpt-Bench; DarwinX has strongly separated held-out/transfer regimes in some arms).
3. **Local regression checks and rollback exist**, but AdaptiveHarness shows why rollback semantics must include untracked/exception state and why the verifier should not share mutable proposal state.
4. **Repeated-selection-safe promotion exists in separate statistical work**, but is not yet located as the admission controller inside the same >10-cycle real harness lifecycle with full artifact replay.
5. **Replayability remains the limiting observability requirement**: exact candidate hash/diff, incumbent hash, paired evidence, structured verdict, accept/reject, rollback effect, lineage/branch, evaluation budget and final hidden outcome must be durably released.

The highest-information experiment is now: use a long-lived population/specialized harness substrate, freeze the exact candidate proposal stream, run each candidate in an immutable worktree, compare incumbent/candidate under identical evidence, and replay four admission rules (greedy, fixed-alpha, per-candidate anytime-valid, global error spending). The acceptor must be read-only and output a signed/structured decision bound to candidate hash. Failed attempts must discard the whole worktree including untracked files. Final evaluation should use a HarnessOpt-style TEE partition never consulted for proposal generation, routing, rollback, retirement, best-state selection or early stopping.

## Exact continuation

1. Search the AdaptiveHarness/A-Evolve release issues, external artifact stores and author releases for actual `nav_evo_*`, workspace git bundles, or paper-run output archives; if found, test whether candidate hashes/diffs and full verifier evidence can reconstruct a fixed proposal chronology.
2. Inspect `scaleapi/vero` public evaluation/run-store schemas and any newly surfaced HarnessOpt artifact location to determine the minimum outer-lockbox audit record needed to bind a nominated candidate hash to its hidden-test result.
3. Deep-audit DarwinX's official project/paper artifacts for exact iteration counts, rejected/accepted candidate records, archive/recombination history, proposal compute and whether any released run artifacts permit fixed-proposal replay. Keep whole-system transfer results separate from component causality.
4. Search for a >10-cycle real agent that already combines: immutable candidate snapshot; read-only structured verifier; exception-safe transactional rejection; repeated-selection-safe admission; complete proposal chronology; and a genuinely untouched final partition.
5. Preserve matched-total-compute, representation-vs-promotion separation, source-qualified IDs, and exposure/activation/adherence/outcome observability.

Frontier remains nonempty. No global completion is claimed.