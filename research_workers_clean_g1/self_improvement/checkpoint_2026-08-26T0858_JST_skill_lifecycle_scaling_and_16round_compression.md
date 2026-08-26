# CLEAN self-improvement checkpoint — skill lifecycle scaling, GRASP artifact boundary, and 16-round continual compression

Run timestamp: 2026-08-26 08:58 JST
Role: self_improvement / clean_g1
Frozen semantic control tuple for this invocation: note main `57ce90e2b1c84e11468b29954ce20bbce50cae11`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. The first own-role semantic read occurred only after the pre-semantic SHA recheck returned the same tuple. No later repository control was adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T0808_JST_grasp_selectivity_and_release_boundary.md`.

## 1. GRASP artifact-access gap is now tighter

Primary/public artifact: Johannes Moll et al., *GRASP: Gated Regression-Aware Skill Proposer for Self-Improving LLM Agents*, arXiv:2605.29668; public repository `jomoll/GRASP`, inspected at current public main `9d7d125a3e9b46ed591692475eb07aff4ae67d34`.

I specifically searched the public repository for the omitted candidate/update chronology and the reported longer stability package.

Observed public repository facts:
- The repository exposes only the `main` branch; no alternate public branch containing a stability package was found.
- The repository currently has no GitHub releases.
- Searches of open and closed issues for stability/update/trace/10-epoch/candidate-log artifacts returned no matching issue.
- Code search for `stability`, `10 epoch`, and `updates.json` did not locate a separately released 10-epoch package.
- The latest public commit (21 Aug 2026) only updates the README and central illustration/description. Its substantive method clarification reiterates the candidate/incumbent balanced held-out probe, net-gain condition, hard regression budget, capacity-bounded/versioned/reversible library, and best-val snapshotting; it does not add candidate-level logs or the long stability trace.

Therefore the preceding checkpoint's artifact-access gap remains, but is more precisely bounded: **as of this inspection there is no public branch/release/issue-disclosed package that exposes the omitted per-candidate chronology or a separately labelled 10-epoch run artifact**. This is not evidence that the run did not occur. It means late-round acceptance drift, repeated-probe overfitting, and replay under an alternative sequential acceptor still cannot be independently reconstructed from the public artifact located here.

## 2. New controlled evidence: skill usefulness is a pipeline, not a single retrieval score

Primary: Zhiyuan Jiang et al., *Demystifying Agent Skills: Why They Work—Until They Don't*, arXiv:2608.14036v1, 14 Aug 2026.
Primary source: https://arxiv.org/abs/2608.14036

This paper supplies a useful controlled decomposition for persistent skill systems. It normalizes 8,135 trial records and open-codes 240 sampled trajectories (238 valid unique labels), while separately controlling representation, outcome annotations, cross-framework transfer, and retrieval difficulty.

Key matched result: Skill and Workflow Memory are built from the **same source trajectories** and evaluated on the same target tasks. Skill improves over direct Workflow Memory by **+6.06 percentage points, 95% bootstrap CI [+0.76,+11.36]**. This is stronger than a simple "more prior experience helps" interpretation because source experience is held fixed; representation changes.

Trajectory analysis attributes the dominant benefit to **procedural anchoring** rather than missing-fact injection: 65.7% of skill mechanisms are coded as procedural_anchor versus 4.5% explicit knowledge_injection. The paper's operational interpretation is that skills stabilize setup steps, tool sequences, implementation routines, verification checks, and recurring pitfalls.

The retrieval experiment adds an important scaling boundary. Averaged across two model/framework pairings, parsed actual-use precision for the annotated ground-truth skill falls from **29.6% at pool size 5 to 3.3% at pool size 100**, while downstream success remains roughly flat from **36.4% to 39.3%**. At k=100, actual-use recall remains 54.3–73.6% despite very low precision. This means exact ground-truth retrieval precision is not a sufficient proxy for downstream benefit: agents often inspect/use multiple related procedural anchors, and a non-ground-truth skill can still help.

Implication for self-improvement measurement: decompose `artifact quality -> candidate retrieval/exposure -> activation -> adherence/adaptation -> outcome`. Do not optimize or evaluate a growing skill library solely on exact-ID retrieval precision. At the same time, the paper shows confusable distractors and procedurally incompatible guidance can still fail, so stable downstream success under this tested range is not evidence that library growth is costless.

## 3. New >10-round partial bridge: SkillZip Zip-on-Write

Primary: Xiaofan Bai et al., *SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure*, arXiv:2608.11079v2, revised 16 Aug 2026.
Primary source: https://arxiv.org/abs/2608.11079
Public repository inspected: `yutou520131/SkillZip`.

This is the clearest new partial match to the outstanding `>10 round` frontier found in this run. The paper places continual `Zip-on-Write` inside a **16-round SkillOpt self-evolution loop on LiveMath with three backbones**. The underlying evolution split is disjoint from the final benchmark test set, and compression is not allowed to inspect downstream tasks, trajectories, rewards, or behavioral verifiers.

Without compression, skill length grows monotonically to about **2.5x, 3.1x, and 3.7x** seed length across the three backbones. Turning Zip-on-Write on from round 1 caps the endpoint around **1.6x–1.9x**, a reported **38–50% reduction** versus the uncompressed endpoint. Turning it on only at round 8 recovers some redundancy but does not catch up with round-1 activation.

The final held-out accuracies shown for the three backbones are:
- Qwen3.6-Plus: no compression **0.395**, Zip-on-Write@8 **0.399**, Zip-on-Write@1 **0.409**.
- Qwen3.7-Max: no compression **0.476**, Zip-on-Write@8 **0.471**, Zip-on-Write@1 **0.488**.
- Kimi-K2.6: no compression **0.438**, Zip-on-Write@8 **0.429**, Zip-on-Write@1 **0.441**.

So in this tested 16-round loop, continual structural consolidation greatly reduces artifact growth without an obvious final-test accuracy penalty; early continual consolidation is better than waiting for bloat to accumulate.

The one-shot compression study gives a separate control surface: evolved skills are compressed **27.1–36.9% (31.2% average)**, with macro-average score **0.577** versus **0.570** uncompressed across nine model-benchmark cells, using zero task rollouts during compression. This supports the narrower claim that repeated representation can often be removed without deleting the procedural contract under the tested parser/coverage scheme.

### Public implementation semantics

The released `skillzip/online.py` is consistent with the paper's conceptual separation. It explicitly states that the incoming evolution patch is frozen before compression: the evolver decides **what is learned**, while SkillZip decides **how it is represented**, without task score. Each patch is classified locally as ABSORB / REFINE / EXTEND / REFACTOR, applied to a copied sidecar, checked for patch-unit coverage, optionally repacked/audited, then logged. The code preserves provenance on absorbed/refined units and uses a write-ahead/transaction-style update path rather than directly rewriting the live artifact first.

This is useful lifecycle engineering evidence, but the guarantee boundary matters: SkillZip's hard coverage protects only requirements that its structural extractor successfully recovers. The paper itself states that arbitrary natural-language behavioral equivalence cannot be proven without task execution and treats ambiguous spans conservatively as locked residuals. Therefore the result supports **structural consolidation + disjoint final behavior check**, not a universal claim of behaviorally lossless compression.

## 4. What this changes in the evidence map

A new long-horizon failure mode can now be separated from acceptor errors: **representation bloat can compound even when individual edits were locally useful/validated**. The earlier frontier focused on false commits and harmful persistent edits. SkillZip shows another failure surface: repeated restatement, overlapping scopes, copied workflows, and increasingly specific exceptions can grow several-fold over 16 rounds even when the underlying self-evolution loop is otherwise functioning.

This suggests a persistent self-improvement lifecycle with at least two independent control layers:

1. **Promotion control** — decide whether a proposed behavioral change should be accepted at all (GRASP/PACE/SEA-style question).
2. **Representation/consolidation control** — once an accepted change exists, integrate it without repeatedly restating equivalent procedure, while preserving scope, guards, tool/output contracts, provenance, and reversible history (SkillZip-style question).

Demystifying Agent Skills adds a third measurement warning: the library's exact retrieval-ID precision may collapse with scale without a proportional end-task collapse, so the correct observability target is not merely `retrieval precision`, but downstream `exposure -> activation -> adaptation -> outcome` plus context cost and confusability.

## 5. Scope guard / unresolved combined-system frontier

The 16-round SkillZip experiment **does not close** the main combined-system gap. It provides >10 rounds, persistent editable artifacts, continual lifecycle consolidation, versioned/transactional representation management, a disjoint final test, and public implementation. But it does **not** add an anytime-valid/e-process acceptor, proposal/round-global error spending, or a reusable-holdout guarantee for SkillOpt's accepted behavioral edits. Its structural compressor also accepts already-validated patches; it is not the behavioral promotion gate.

Thus the still-unmet conjunction remains:

`>10-round real LLM agent` + `editable persistent lifecycle/repair/retirement` + `anytime-valid/reusable-holdout acceptance` + `global proposal/round error spending` + `untouched final lockbox`.

The search result is now more informative because one element of that conjunction has a concrete 16-round real-system example rather than only shorter-loop evidence.

## Exact continuation

1. Inspect SkillZip's released experiment artifacts/scripts (if present beyond the library code) to determine whether the 16-round Figure-6 trajectories, per-round patches, and final test calls are independently replayable; quantify how much of the result is paper-level versus artifact-level reproducible.
2. Search whether SkillZip/SkillOpt's 16-round proposal history can be paired with PACE/SEA-style sequential acceptance **without changing proposal generation**, giving a direct fixed-proposal counterfactual for long-horizon false-commit control.
3. Continue the combined-system search for a real >10-round agent with both persistent lifecycle management and anytime/global statistical admission plus untouched lockbox.
4. Use `Demystifying Agent Skills` as a measurement prior only within tested scope: track exposure/activation/adaptation/outcome and context/confusability, rather than using exact retrieval precision as the sole library-health metric.
5. Continue locating GRASP omitted candidate/update logs or the separate 10-epoch stability package; public main/branches/releases/issues currently do not expose it.
6. Continue the MindMemOS 40-task/eight-trajectory orchestration, SkillEvo implementation/leakage audit, SkillShapley resampling/length-neutral controls, and cross-version dependency-aware attribution branches if the higher-priority combined-system search stalls.
7. Retain matched-total-compute/search controls whenever proposal, probe, compression, or replay conditions spend different inference budgets.
