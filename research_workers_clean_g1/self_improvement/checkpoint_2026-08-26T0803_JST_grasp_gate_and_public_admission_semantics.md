# CLEAN self-improvement checkpoint — regression-gated editing and public admission semantics

Run timestamp: 2026-08-26 08:03 JST
Role: self_improvement / clean_g1
Frozen semantic control tuple: note main `9c2ca150e7c708cb3e36aa6cfb0d21720cd41c18`; sanitized root `automation_control/DESIRED_STATE.json` control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`.
Continuation source: own `LATEST.json` -> `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T0706_JST_primary_verification_and_protocol_gap.md`. The semantic control tuple was rechecked with a SHA-only Git ref lookup immediately before the first substantive read and then frozen for this invocation. Later repository-head advances were used only for safe persistence and did not change semantic control. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipts/configs were used semantically.

## SIG-GRASP-REGRESSION-GATED-EDITING

Primary: Johannes Moll et al., *GRASP: Gated Regression-Aware Skill Proposer for Self-Improving LLM Agents*, arXiv:2605.29668, 28 May 2026.
Primary source: https://arxiv.org/abs/2605.29668
Public implementation inspected at `jomoll/GRASP@9d7d125a3e9b46ed591692475eb07aff4ae67d34`.

### Mechanism and primary quantitative result

GRASP treats persistent self-improvement as edits to a bounded, versioned, reversible skill library. After each development batch, it proposes candidate `ADD`, `MODIFY`, or `REMOVE` edits. Every candidate is re-run on a balanced probe drawn from previously failing and previously passing development examples and compared against a freshly re-run incumbent on exactly the same probe. A candidate is admitted only when its net fixes-minus-regressions improvement is positive and it introduces no more regressions than the incumbent baseline. Rejected candidates leave the live library unchanged.

On MedAgentBench with gpt-oss-120b, the no-skills baseline is 40.6% and full GRASP reaches 88.8±5.8% held-out test accuracy. The strongest reported self-improvement baseline is 21.0 points lower. The paper uses disjoint development, validation, test, and for the MedAgentBench variants OOD task-type splits; the final test/OOD splits are not used for training or checkpoint selection.

### Acceptance-gate causal evidence

The matched three-seed ablation is unusually informative:

- full GRASP: validation-best 86.0±4.4, test **88.8±5.8**;
- without regression budget: test **81.8±1.8**;
- fixes-only selection: **80.2±13.7**;
- append-only: **80.2±9.4**;
- without acceptance gate, K=4: **63.5±3.9**;
- without acceptance gate, K=1: **40.1±11.3**, statistically indistinguishable from the 40.6 no-skills baseline at this resolution;
- matched-compute proposer selection: **70.8±14.0**;
- matched-compute random selection: **67.2±10.2**.

The matched-compute rows still execute the full candidate probe but discard the probe verdict when choosing the edit. Therefore the large gap between 88.8 and the 67–71 range cannot be explained merely by extra validation inference. Within this protocol, the *decision rule* that uses comparative behavioral evidence carries substantial causal weight.

Granting the same gate to five alternative memory/skill baselines improves every one in-domain at K=1 but does not materially improve their OOD results. Full GRASP with the same gate and comparative K=4 generation remains far ahead. This narrows the mechanism further: held-out validation alone is not sufficient; the useful package is the gate applied to a bounded editable library with comparative proposals and explicit regression protection.

### Public-code verification

The public implementation's core loop documents the same structure: per epoch it shuffles development examples, runs batches, samples K single-change proposals, builds a balanced failing/passing probe, forks the repository for each candidate, evaluates each fork, applies only the best regression-gated proposal, then runs validation without learning from validation. It snapshots the learned skill directory whenever validation improves and restores the best checkpoint after training.

The updater persists provenance on learned skills, including birth epoch/update cycle, probe score, fixes and regressions, and runtime effectiveness estimates. It allows `ADD`, `MODIFY`, and `REMOVE`; when the library is full, adding a replacement requires removing an existing learned skill. This is concrete implementation support for bounded capacity and lifecycle editing rather than paper-only architecture.

The public code also makes an important attribution limitation explicit: its per-skill ongoing effectiveness statistics assign credit/blame to every learned skill present when a sample changes from fail→pass or pass→fail. That is a correlation heuristic, not causal lineage attribution. Thus GRASP has strong candidate-level causal probing at promotion time, but its longer-term per-skill effectiveness accounting should not be interpreted as descendant-level causal credit.

### Long-horizon boundary

The main results use five epochs. The paper includes a separate **10-epoch stability run with one seed per method**, explicitly longer than the main five-epoch protocol, but this still does not satisfy the current >10-round frontier and does not add anytime-valid confidence sequences or global proposal/round error spending. Repeated adaptive reuse of development probes/validation remains a statistical-selection issue; the untouched test/OOD split protects final reporting but does not make every intermediate acceptance decision anytime-valid.

## SIG-MINDMEMOS-PUBLIC-LIVE-ACTIVATION

Primary paper: Kaichao Liang et al., *MindMemOS: A Portable and Self-Evolving Memory Operating Layer for AI Agents*, arXiv:2608.12428, 12 Aug 2026.
Public implementation inspected at `mindscale-noah/MindMemOS@c1befcb73646b54f7a96724ea5463edb21c03ee0`.

The previous checkpoint established a mismatch between the published SpreadsheetBench protocol (40 executed tasks per evolution cycle, trajectory groups of eight) and the generic public CLI (`--evolve-every` defaults to one). This run resolves the generic public admission semantics more precisely.

Server-side skill evolution defaults to `min_aggregate=8` and `max_aggregate=8`. It summarizes eligible injected trajectories, groups pending summaries in add-time order, proposes/applies a patch for each eight-summary batch, and serially mints child versions. `use_trajectory_score=True` switches the patch proposer into a supervised prompt whenever trajectory scores are present; otherwise it uses the unsupervised prompt. Freshly minted server versions have default lifecycle status `draft`.

However, the public benchmark client does not treat `draft` as a behavioral quarantine. After a successful `/v1/skills/evolve`, it immediately fetches the returned `new_version_id`, writes that version's bundle into the **live local skill directory**, updates the managed version id/content hash, and therefore causes the next task batch to execute against the new version. The generic public runner records each batch's trajectories/scores, calls evolution at the batch boundary, and repeats. No independent candidate/incumbent held-out behavioral A/B gate is present between minting and next-batch activation on this path.

This is an implementation-level observation about the current public generic runner, **not proof that the paper's exact Table-4 40-task Sup./Unsup experiment used this orchestration unchanged**. No searched public path surfaced the exact 40-task/8-trajectory paper experiment script. A plausible implementation could set the external runner batch to 40 while the server internally emits up to five serial eight-summary versions, but that is only a code-derived possibility and must not be attributed to the published experiment without the missing script/config.

The evidence implication is narrower but important: a framework can have version statuses and a self-evolution API while still activating newly minted behavior without an independent promotion gate in a concrete execution path. Evaluation of self-improvement systems must inspect the *actual activation path*, not infer gating from lifecycle labels or architecture diagrams.

## SIG-SKILLEVO-SEPARATED-REVIEW-AND-HUMAN-PRODUCTION-GATE

Primary: Qianxi Yan et al., *SkillEvo: Self-Renewing Evolution Gradients from Multi-Turn Interaction Feedback*, arXiv:2608.13120, 13 Aug 2026.

Further primary inspection sharpens its governance scope. The Skill Editor uses `deepseek-v4-pro`, while the Verifier, User Agent, Attributor, and Governor use `minimax-m3`; the paper explicitly separates generator and evaluator model families to reduce circular self-review. Evaluation agents are headless and expose only skill loading/read-only retrieval, with write tools deregistered. The pipeline persists evidence and outcomes, limits inner repair attempts, runs full evaluation at outer boundaries, and requires human confirmation before production rollout.

Therefore SkillEvo's positive four-round result should be classified as a **governed separated-review skill-evolution system with an untouched final quarter and human production confirmation**, not as autonomous recursive self-modification. This strengthens evidence that generator/evaluator separation and production promotion boundaries can coexist with large gains, while leaving the >10-round adaptive-statistics problem unresolved. No official public code or independent reproduction was located in the searches performed in this run, so implementation-level leakage auditing remains blocked by artifact availability.

## SIG-SKILLSHAPLEY-STABILITY-BOUNDARY

Primary: Chang Liu et al., *SkillShapley: Boundary-Adaptive Shapley Valuation for Skill Step Attribution in LLM Agents*, arXiv:2608.13173, 13 Aug 2026.

The exact-reference experiments are smaller and less robustness-complete than a headline Shapley result can suggest. Each coalition configuration is evaluated on only **three benchmark instances**, giving reward values {0, 1/3, 2/3, 1}. The same small benchmark subset and fixed OpenHands harness are used across methods, with temperature zero. No public code repository was located, and the primary paper does not report task-resampled or model-resampled ranking stability, nor a length-neutral padding control.

Consequently SkillShapley remains good evidence for **within-version, fixed-player, fixed-panel procedural attribution**, but not for robust cross-task/model attribution, not for prompt-length-normalized content value, and not for cross-version descendant credit. Those require separate tests.

## SEARCH-LONG-HORIZON-STAT-GATE-UPDATE

A fresh search still did not surface a real persistent LLM-agent experiment that combines in one matched study:

1. more than 10 adaptive persistent-improvement rounds;
2. an editable lifecycle with repair/retirement/rollback of previously promoted artifacts;
3. reusable-holdout or anytime-valid/e-process acceptance;
4. proposal/round-global multiplicity/error spending; and
5. a final untouched task-level lockbox.

GRASP materially strengthens the lifecycle+behavioral-gate+outer-test side and includes one 10-epoch single-seed stability run, but it lacks anytime-valid/global-spending control and does not exceed ten rounds. PACE/SEA-like methods remain stronger on statistical acceptance but do not close the persistent-lifecycle conjunction. This remains a negative search result, not a nonexistence proof.

## Synthesis update

The strongest new causal lesson is that **promotion is a first-class mechanism**. In GRASP, writing skills without an acceptance verdict collapses to near the no-skills baseline, and equal validation compute without using the verdict fails to recover the full gain. Conversely, the MindMemOS generic public runner shows that merely minting a `draft` version does not imply behavioral quarantine: activation can still be immediate.

An evidence-aligned persistent self-improvement stack should therefore distinguish:

`diagnostic evidence`
-> `bounded comparative proposals`
-> `candidate/incumbent behavioral replay`
-> `hard regression protection`
-> `statistical/multiplicity-aware admission`
-> `versioned activation boundary`
-> `best-known checkpoint / rollback`
-> `cross-version provenance and downstream contribution audit`
-> `matched-total-compute control`
-> `untouched outer evaluation`.

GRASP directly validates several middle layers; MindMemOS provides a concrete counterexample showing why the activation boundary must be inspected in executable code. Neither closes the long-horizon statistical-adaptation gap.

## Nonempty frontier / exact continuation

1. Inspect GRASP's released per-seed result artifacts and 10-epoch stability configuration to quantify candidate counts, acceptance rate and whether repeated-probe reuse shows late-round overfitting or gate saturation. Search for a clean way to re-score the same public trajectories under a sequential/e-process acceptor without changing proposal generation.
2. Continue the exact missing-system search for **>10 rounds + editable persistent lifecycle + anytime-valid/reusable-holdout gate + global spending + untouched lockbox**. Prioritize post-PACE/SEA work and explicit proposal-count reporting.
3. Locate the exact MindMemOS Table-4 paper orchestration for the **40-task evolution cycle / eight-trajectory groups / Sup.-vs-Unsup modes**. Determine whether the published run had hidden validation, candidate selection, rollback, or a different activation path than the generic CLI. Preserve as a reproducibility gap if not public.
4. Find SkillEvo code or an independent reproduction and audit whether the untouched final quarter can leak indirectly through retrieval indexes, prompts, caches, simulators, or operational ticket metadata; preserve its human-confirmed production boundary in the mechanism classification.
5. Seek SkillShapley artifacts or independently recreate its small fixed-player evaluation with **task-resampling, model-resampling, and length-neutral padding/deletion controls** before treating step ranks as robust utility estimates.
6. Extend promotion-time causal probing into **cross-version/cross-descendant provenance-aware attribution**. Prefer selective replay or intervention on dependency edges over presence-based correlation heuristics.
7. Retain matched-total-compute/search controls: when an evolution system spends extra candidate/probe/evolution inference, compare against equal-budget resampling or candidate search before assigning the entire gain to persistent adaptation.
