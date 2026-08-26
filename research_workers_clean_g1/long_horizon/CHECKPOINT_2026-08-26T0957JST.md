# Long Horizon clean_g1 checkpoint — 2026-08-26 09:57 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, its own sanitized feedback, and public sources. It did not read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts.

Semantic-freeze tuple:
- note main SHA at freeze: `b12d2da7cad0991a56c0920480128c5f682cb744`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

Before the first substantive semantic read, a second SHA-only head lookup still returned the frozen SHA. After semantic work had begun, a later SHA-only lookup observed note main advance to `4a35c4305c96b5e1e788aa137aff8527b050cf66`. Per the hard semantic-freeze rule, no newer control/config or semantic state was adopted in this physical invocation; this checkpoint remains bound to the frozen tuple above.

## New primary-source findings

### 1. Calibration-only oversight is now partially closed as a frontier; intervention value remains the important control object

**Calibration Is Not Control: Why LLM-Agent Oversight Needs Intervention** (arXiv:2606.21399, submitted 2026-06-19) formalizes `intervention advantage` as the expected utility difference between intervening and continuing from the same trajectory prefix. Its prefix-branching protocol evaluates candidate actions from matched prefixes rather than treating failure probability as the control target.

The strongest reported interactive result is ALFWorld control regret `0.506 -> 0.110` for a prefix-only action-conditioned controller versus scalar routing. More importantly for the open detector frontier, the paper contains a calibration decomposition that keeps the same scalar score and threshold-routing policy while recalibrating that score. In ALFWorld, Platt scaling improves a reported confidence score's ECE from `0.463 -> 0.006` while control regret remains `0.318`; for a failure score, raw and Platt-scaled routing both retain regret `0.358`, while an isotonic variant can worsen regret. Thus better calibration alone can leave the intervention decision unchanged or worse.

Implication: the previous broad question "does detector calibration improve closed-loop recovery?" is too coarse. Calibration is now directly shown insufficient under a fixed scalar-threshold controller. The remaining higher-value gap is narrower: vary detector representation/discrimination or intervention-value estimation while holding the actual recovery actuator, cut rule, carry-forward policy, model/tasks, and intervention budget fixed, and measure both recovered failures and disrupted would-have-succeeded trajectories.

Scope guard: this paper evaluates several intervention types (expert/gold-prefix/same-model re-answer/quit), not specifically a rollback actuator. It does not prove that an action-conditioned controller will improve every recovery system; gains shrink when interventions are weak or the scalar already preserves decision-relevant information.

### 2. Successor-readiness is not only diagnostic: a controlled verifier tightening recovers one chained task, but increases recovery pressure

In **Diagnosing Semantic Handoff Failures in Agent-Orchestrated Vision-Language-Action Skill Composition** (arXiv:2607.06256v2), the same VLA skill checkpoints can succeed at roughly `77–100%` from clean skill-boundary snapshots while composed long-horizon chains frequently stall. The paper also reports a controlled readiness intervention: tightening the navigation verifier from a coarse reached-area criterion to an arm-reach criterion while keeping tasks, instances, and skill checkpoints fixed.

That change moves solved tasks from `0/10 -> 1/10` and mean task score from `0.01 -> 0.10`, recovering one radio task by causing extra re-navigation. But it also increases move-to attempts `74 -> 99`, next-skill-readiness failures `23 -> 35`, target-grounding failures `31 -> 37`, and total failed attempts `115 -> 130`, while control/commit failures only move `61 -> 58`.

Implication: a stricter handoff contract can prevent premature successor invocation and recover some downstream success, but it is not free. It can surface more failed attempts/recovery cycles and leaves other failure classes dominant. The controller therefore needs both a successor-readiness predicate and a policy for what to do when readiness fails; "stricter verifier" is not itself a complete recovery mechanism.

Scope guard: this is a small robotics/VLA ablation, not a generic-agent proof. The paper explicitly leaves recovery/replanning and readiness-cadence sweeps as future work.

### 3. Context folding has a sharp stability-versus-cost trade-off; the cheapest training variant can collapse

**FoldAct: Efficient and Stable Context Folding for Long-Horizon Search Agents** (arXiv:2512.22733) gives a concrete negative regime rather than only an abstract self-conditioning warning. Without its full-context consistency loss, actor KL becomes unstable and training collapses at about step 173; after about step 50 responses become repetitive and extremely long. The no-consistency variant is computationally cheap (about `97.75 s/step`, `84.90 GB`, roughly `49.6x` faster than the full-context baseline), but that speed is not usable evidence of a good policy because the training is unstable. Adding the consistency loss is slower (about `933.70 s/step`, `405.85 GB`, about `5.19x` speedup) but stabilizes training.

Task-level ablations are also non-monotone. For local RAG, adding consistency improves HotpotQA F1/EM from `34.9/26.7` to `38.5/29.5`, while displayed PopQA scores do not uniformly improve. Selective segment training at `p_drop=0.5` versus `p_drop=0` also produces mixed final outcomes across WebWalker, GAIA, BrowseComp and XBench rather than a universal gain.

Implication: folding policy evaluation must jointly score final-task outcome, summary-induced distribution shift/training stability, and compute. The remaining open frontier is specifically fold frequency/depth/summary-quality under matched final-task conditions; component-loss/dropout ablations do not answer that question.

### 4. Version-target selection can be evaluated independently from rollback QA, but current evidence is conversational-memory-specific

**ChronoMem: Versioned Memory for Long-Horizon LLM Agents** (arXiv:2607.27773) treats version selection and state restoration as distinct evaluation axes. Its version-target metrics show materially better version retrieval than BM25/dense/hybrid baselines; on its MAB table, ChronoMem reports Recall@1 `33.4`, Recall@5 `60.2`, Scope@2 `58.0`. Its rollback-consistent QA tables then evaluate post-selection behavior separately.

This is useful methodological evidence for decomposing `where to rollback` from `what happens after rollback`, but it does not close the strict historical-target selector frontier because the setting is conversational/versioned memory, selector methods differ in retrieval/reranking machinery, and final QA comparisons also include different restoration architectures. A source-quality note is retained: the paper prose elsewhere reports different MAB retrieval numbers than the displayed table; use the table values until that discrepancy is resolved.

### 5. Exact execution-edit safety has stronger pinned implementation/formal evidence, with important non-claims

The first-party repository linked from **When Can Agents Safely Checkpoint, Fork, Restore, and Merge?** is pinned here at public commit `d0c855afa93d9c8301e9983bedffc0058f68baba`. Its Lean development pins Lean/Mathlib `v4.30.0`; the documented audit builds the theorem set, checks proof placeholders/axioms, rejects `sorryAx` and non-allowlisted foundational dependencies, and fresh-replays the main development with `leanchecker`.

The theorem matrix includes exact-checker equivalence, exact six-edit derivation, trace-safety installation and lifecycle preservation results. However, the repository explicitly limits these to a finite abstract authority model. It does not yet prove that Go projection construction, JSON decoding, hashing or numeric limits refine the Lean definitions; nor does it establish complete tool mediation, correct natural-language binding, truthful external receipts, or safety of unmodified production agents.

Implication: the evidence for an admissibility filter before restore/fork/merge is now stronger at the implementability/formal-model level, but it must remain separated from behavioral task-success evidence and production-runtime refinement.

## Updated synthesis

The controller decomposition is refined from a pure failure-detector framing to:

`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> historical target selector -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

The new key distinction is that **risk estimation is not the control objective**. A recovery controller should estimate whether a specific available intervention improves expected outcome at the current prefix, ideally through same-prefix counterfactual evidence where feasible. Calibration can be excellent while the decision target is still wrong.

## Remaining gaps and exact continuation

1. Find a strict historical-target-selector factorial with identical alarm, candidate checkpoint set, restore/carry-forward, model, retry/token budget and final software/tool/GUI task outcome, varying only the rollback target selector. Keep Hydra/WebRollback/ChronoMem as near-factorials, not closure.
2. Narrow the detector frontier to representation/discrimination or intervention-value quality under a fixed recovery actuator, safe-cut rule and carry-forward policy; calibration-only insufficiency is now directly evidenced.
3. Search for prefix-branching/action-conditioned oversight where the intervention is local rollback/replay rather than expert handoff or re-answer, ideally with recovered-failure and disruption accounting.
4. Inspect handoff studies for explicit recovery policies after successor-readiness failure, especially matched `no recovery vs local repair/replan` and readiness-check cadence ablations.
5. Inspect folding studies for matched fold-frequency/depth/summary-quality sweeps with final-task outcomes and training-stability costs, not token savings alone.
6. Inspect the pinned execution-edit repository's concrete Go certificate tests/runtime adapter refinement evidence; preserve the formal-model/production boundary.
7. Continue searching for a first-party Hydra code artifact without treating search failure as evidence of absence.
8. Maintain a nonempty frontier; this checkpoint is not global completion.
