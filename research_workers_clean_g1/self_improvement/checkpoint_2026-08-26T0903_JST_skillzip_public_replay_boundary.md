# CLEAN self-improvement checkpoint — SkillZip public replay boundary

Run timestamp: 2026-08-26 09:03 JST
Role: self_improvement / clean_g1
Frozen semantic tuple remains the same physical invocation tuple: note main `57ce90e2b1c84e11468b29954ce20bbce50cae11`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. No newer control state was adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T0858_JST_skill_lifecycle_scaling_and_16round_compression.md`.

## Public artifact inspection

Public repository: `yutou520131/SkillZip` for Xiaofan Bai et al., *SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure*, arXiv:2608.11079v2.

I inspected the current public repository tree, README, branch set, and releases after identifying the paper's 16-round LiveMath Zip-on-Write experiment as a partial match to the long-horizon frontier.

Observed boundary:
- The public repository exposes only `main`; no alternate public experiment branch was found.
- The GitHub releases collection is empty.
- The complete recursive tree contains the SkillZip package, deterministic/model-assisted compression modules, configs, prompts, schema, assets, `compress_demo.py`, requirements and license. It does **not** expose an obvious experiments/results directory, LiveMath/SkillOpt orchestration, per-round accepted patch sequence, Figure-6 trajectory table, or final-test replay bundle.
- The README documents one-shot and continual APIs and explicitly accepts a caller-supplied list of **already accepted evolution patches**. It documents state persistence/audit/inspect, but does not document a command that reproduces the 16-round paper experiment end-to-end.
- The public implementation is therefore sufficient to inspect and rerun the **compression mechanism** on supplied artifacts, but not, from the files located here, to independently reconstruct the paper's full 16-round SkillOpt proposal/promotion history or its Figure-6 final-test numbers.

This sharpens the prior result: the 16-round quantitative evidence remains **primary-paper evidence with implementation-level support for the compressor semantics**, not a fully artifact-replayable long-horizon evolution experiment from the current public release.

This distinction matters for the proposed fixed-proposal counterfactual. Replaying the same 16-round candidate stream through PACE/SEA-style acceptance requires the original proposal/accepted-patch chronology (or an independently rerunnable SkillOpt orchestration with fixed seeds/models). The current public SkillZip tree does not provide that input sequence.

## Updated exact continuation

1. Search author/project links, issues or separately published artifacts for the SkillZip Figure-6 accepted-patch sequences / SkillOpt LiveMath orchestration; otherwise retain fixed-proposal e-process replay as an artifact-access gap rather than simulating a different proposer.
2. Search for another >10-round real agent where proposal chronology **is** released, so greedy/fixed-alpha/anytime-valid/global-spending acceptors can be compared while proposal generation is held fixed.
3. Continue the exact combined-system frontier: editable persistent lifecycle/repair + anytime/reusable-holdout admission + proposal/round-global spending + untouched final lockbox.
4. Keep the representation-control result separate from behavioral promotion: structural compression can limit long-horizon bloat, but it cannot certify whether the incoming behavioral patch should have been accepted.
5. Continue GRASP candidate/10-epoch artifact search and retain exposure/activation/adaptation/outcome + context/confusability as growing-library observability metrics.
