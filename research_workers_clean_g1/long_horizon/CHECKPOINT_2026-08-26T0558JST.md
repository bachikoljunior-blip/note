# Long Horizon clean_g1 checkpoint — 2026-08-26 05:58 JST

## Run boundary / control provenance
- Worker: `long_horizon`
- Generation/class: `clean_g1` / `clean_exploration`
- Frozen note main SHA for substantive work: `5478ae1096aa60c44b78a4fb397b2de450e8f09d`
- Sanitized root control: `automation_control/DESIRED_STATE.json`, control revision `8`, blob `508c9f92dd965d2b5074932b99847411cb66bef4`
- Role-local config: `automation_control/roles/long_horizon.json`, config revision `5`, blob `268523da20c78ce3091344c492ad3d51f6f9e667`
- `enabled_desired=true`.
- Semantic inputs used in this run: this worker's own clean state, this worker's own sanitized feedback, the sanitized control root, this role-local config, and public sources only.
- The own feedback item about observability boundaries was honored: the shared `automation_control/EXECUTION_LEDGER.json`, other-role receipts/configs, O/O-derived state, downstream state, other workers, and legacy/pre-independence research were not read or used.
- Scope rule remains: no positive or negative claim is broadened beyond the exact tested setting.

## Research question advanced in this run
What conditions make an online long-horizon failure detector *actually useful when it is allowed to intervene*, and what extra recovery contracts are required once an agent can leave persistent external effects?

The key refinement is that detector quality, intervention policy, rollback/restart mechanics, carried-forward state, and external-effect settlement are separate control problems. A high-AUROC detector can still reduce final success if intervention disrupts trajectories that would otherwise succeed.

## 1) Accurate failure prediction can make the agent worse after intervention
Primary: `Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention`, arXiv:2602.03338
https://arxiv.org/abs/2602.03338

The paper trains a small binary trajectory critic and then closes the loop with actual interventions rather than evaluating AUROC alone.

Primary-reported detector quality:
- Qwen3-0.6B LoRA critic, trained on 7,636 trajectory steps from HotPotQA/GAIA.
- Held-out 1,372 samples: overall AUROC `0.936`, F1 `0.963`.
- By base-agent backbone: Qwen3-8B AUROC `0.982`, GLM-4.7 `0.966`, MiniMax-M2.1 `0.897`.

Yet final-task effects reverse across settings:
- HotPotQA:
  - Qwen3-8B baseline `57.0%`; best intervention `54.7%` (`-2.3 pp`).
  - GLM-4.7 baseline `70.3%`; best intervention approximately no gain.
  - MiniMax-M2.1 baseline `64.0%`; best intervention `38.5%` (`-25.5 pp`).
- GAIA:
  - Qwen3-8B baseline `18.9%`; best intervention lower by about `4.4 pp`.
  - MiniMax-M2.1 baseline `46.7%`; best intervention `16.7%` (`-30.0 pp`).
- ALFWorld:
  - Qwen3-8B baseline `5.8%`; best intervention `8.6%` (`+2.8 pp`, reported `p=0.014`).
  - GLM-4.7 `14.7% -> 15.8%` (`+1.1 pp`).
  - MiniMax-M2.1 `16.1% -> 16.6%` (`+0.5 pp`).

The paper formalizes the mechanism using:
- `p`: baseline failure prevalence,
- `r`: recovery probability when intervening on a trajectory that would fail,
- `d`: disruption probability when intervening on a trajectory that would otherwise succeed.

Expected success change is:
`ΔSuccess = p*r - (1-p)*d`.

Intervention is beneficial only when:
`p > d / (r + d)`.

A 50-task ALFWorld pilot for Qwen3-8B estimated roughly `p≈0.89`, `r≈0.12`, `d≈0.56`, yielding a threshold around `0.82`, which correctly predicts that this unusually failure-heavy setting can benefit despite a disruptive intervention.

Scope-bounded implication:
- Do not choose a long-horizon intervention from critic AUROC/F1 alone.
- Estimate `p`, `r`, and `d` on a small deployment-matched pilot and evaluate final task success.
- The same critic/intervention pair can be benign, harmful, or useful depending on base agent and failure prevalence.
- These results concern the tested simple rollback/warning interventions and benchmarks; they do not imply that all intervention mechanisms have the same disruption rate.

## 2) Closed-loop repair can work, but learned monitors need deployment calibration
Primary: `Real-Time Detection and Repair of LLM Agent Failures`, arXiv:2608.02464
https://arxiv.org/abs/2608.02464

Primary-reported setup/results:
- 2,823 committed agent episodes across three frameworks and multiple models.
- One-class echo-state ensemble + CUSUM detects `0.71` of failures at a `5%` false-alarm budget; AUROC `0.872`.
- Benefit over a memoryless detector grows with post-onset horizon: `+0.09` for <=3 steps and `+0.40` for >=9 steps.
- Ranking transfer without retraining: AFTraj-2K `0.745`, ATBench `0.779`.
- But cold deployment transfer is weak: AUROC `0.527`; after per-deployment recalibration `0.885`.

The most decision-relevant result is closed-loop repair:
- flagged runs are rolled back and rerun live,
- recovery of failures: `45%` vs `16%` for a resampling control (`p=0.0005`),
- task success: `52% -> 73%`,
- roughly one extra model call per run.

The paper also reports deterministic verification that catches many failures with zero false positives in the tested invariant checks, including transfer to another model without learned recalibration.

Scope-bounded implication:
- learned anomaly scores can be useful, but they should not be assumed portable across deployments;
- whenever hard invariants exist, deterministic checks are attractive because false-positive disruption can dominate long-horizon benefit;
- final repair success is the relevant metric, not detector AUROC by itself.

## 3) Restart policy and carried-forward artifacts are first-class recovery variables
Primary: `Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE Agentic Tasks`, arXiv:2608.03222
https://arxiv.org/abs/2608.03222

Primary abstract-level results verified in this run:
- a 0.6B monitor observes visible trajectory prefixes;
- trained only on Qwen3.6-27B, it transfers to three other policies including a closed API model;
- at a target `5%` false-positive rate, it saves `14.6–20.4%` execution tokens;
- on Qwen3.6-27B, token savings are `20.4%` vs `12.5%` for AgentStop;
- at `25%` FPR, RestartSmart raises SWE-bench Verified resolution `66.6% -> 71.8%`;
- a cold restart reaches only `66.8%`.

RestartSmart starts a fresh same-policy rollout without prior prompt history, but exposes the interrupted repository diff as an optional artifact that the new rollout may inspect/apply/discard.

Important verification guard:
- richer details surfaced in secondary/indexed renderings (including intervention-cut timing and a correction-prompt reversal) were *not* promoted here because the corresponding primary table text was not directly verified in this run.

Scope-bounded implication:
- clearing stale reasoning history and preserving selected durable artifacts can outperform a pure cold restart;
- `what to carry forward` must be treated separately from `whether to restart` and `where to restart`.

## 4) Checkpoint restore can duplicate external effects even when local state looks correct
Primary: `ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore`, arXiv:2603.20625
https://arxiv.org/abs/2603.20625

The paper studies semantic rollback attacks created by restoring an agent checkpoint after an irreversible tool effect has already committed.

Primary proof-of-concept results:
- testbed: Claude Code CLI + Qwen3-32B with bank/cloud/approval MCP tools;
- checkpoints are placed just before irreversible actions;
- **Action Replay:** all `10/10` checkpoint-restore trials produced duplicate commits; no-checkpoint baseline `0/10`;
- **Authority Resurrection:** stateless validation allowed all tested token reuses (`2/2`), whereas stateful server-side revocation rejected them.

Core mechanism:
- after restore the model can synthesize a semantically equivalent action with a new request/idempotency identifier;
- server-side request-ID deduplication therefore does not imply semantic exactly-once behavior.

The proposed ACRFence design records irreversible effects and after restore should:
- replay the recorded response for semantically equivalent calls,
- block semantically different calls and require an explicit fork,
- reject consumed credentials.

Critical limitation:
- the paper validates the attacks but does **not** implement/evaluate the full ACRFence defense; defense overhead and analyzer failure modes remain future work.

Scope-bounded implication:
- a recovery checkpoint must bind not only model/context/environment state but also already-committed external effects;
- successful local rollback is not evidence of safe global rollback.

## 5) Recovery success and external-effect safety are distinct metrics
Primary: `Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows`, arXiv:2602.14849 v2
https://arxiv.org/abs/2602.14849

Atomix tracks epochs/resource frontiers, stages or classifies effects, and settles them transactionally at commit. It distinguishes reversible, bufferable, irreversible-gated, and idempotent-known-outcome effects.

Important negative/control result:
- under the pure recovery benchmark, Checkpoint-Replay can be statistically tied with transactional execution.
- one reported subset: Checkpoint-Replay `16/30 = 53%`, Tx-Full `17/30 = 57%`, Fisher exact `p=1.0`.
- across the larger reported comparison (`N=114`) the paper likewise does not establish a significant pure-success gap.

But external-effect safety is a separate dimension:
- the paper reports `0/500` invalid irreversible sends leaked under the transactional design while all `500` valid sends were released.
- the prototype also eliminates conflict-cycle witnesses in the tested multi-agent overlap setting, while weaker locking/no-transaction baselines exhibit invariant violations.

Critical limitations:
- prototype is a roughly 2,000-line single-process Python system;
- it does not claim semantic validation, distributed deployment, or full crash-safe exactly-once behavior;
- correctness depends on adapter mediation and accurate effect/resource metadata.

Scope-bounded implication:
- final task completion alone can hide unsafe duplicate/residual effects;
- evaluate at least two outcome axes: task success/recovery and residue/effect safety.

## 6) Mid-execution revision theory also separates rollback from irreversibility
Primary: `Revisable by Design: A Theory of Streaming LLM Agent Execution`, arXiv:2604.23283
https://arxiv.org/abs/2604.23283

The paper classifies actions as Idempotent, Reversible, Compensable, or Irreversible. Conflicting compensable actions incur unavoidable repair cost; conflicting irreversible actions can make full specification satisfaction impossible.

Its Revision Absorber rolls back to the earliest conflict instead of restarting everything. On StreamBench (`n=1,008` runs, DeepSeek-V3), reported quality is statistically indistinguishable from Full-Restart while discarding `14.6x` fewer already-completed steps.

Scope guard:
- this is a user-revision/streaming-execution setting, not generic autonomous failure recovery;
- it nevertheless supplies a useful formal reason to keep `where to rewind` separate from `how to settle irreversible effects`.

## 7) Supporting primary lead: semantic transactions
Primary abstract: `Cordon: Semantic Transactions for Tool-Using LLM Agents`, arXiv:2606.17573
https://arxiv.org/abs/2606.17573

The primary abstract describes task-scoped transactional boundaries that track derived-result lineage, reversible state, staged external effects, delegated authority, and audit metadata. It reports reduced irreversible-effect failures while preserving benign completion with modest overhead, but exact numeric table values were not extracted from primary text in this run. Keep this as a mechanism lead rather than a quantified result.

## Cross-source synthesis: a refined long-horizon recovery controller
The evidence now supports decomposing recovery into separate modules instead of a single `critic -> rollback` operation:

1. **Detection / trigger**
   - learned monitor, deterministic invariant, or hybrid;
   - report deployment calibration and false-positive rate.
2. **Intervention decision**
   - estimate failure prevalence `p`, recovery probability `r`, and disruption `d`;
   - intervene only when expected final-task gain is positive, not merely when critic confidence is high.
3. **Cut point / timing**
   - when the currently executing action can be safely interrupted or settled.
4. **Historical target**
   - which prior semantic/checkpoint boundary to restore.
5. **Carry-forward policy**
   - which branch lessons, patches, validated artifacts, or memories survive into the new attempt.
6. **Local reversible-state restoration**
   - context, filesystem/workspace, environment, and any model-serving state required for coherent rewind.
7. **External-effect ledger and settlement**
   - durable record of committed effects, idempotent replay rules, compensation, irreversible gating, and explicit fork semantics.
8. **Commit-time revalidation**
   - before new irreversible effects, revalidate authority/freshness/resource frontier rather than trusting pre-rollback assumptions.
9. **Repair stopping rule**
   - stop when expected incremental repair value is non-positive; repeated repair itself can disrupt good state.

This decomposition explains otherwise puzzling results: a very accurate critic can be net-harmful when disruption is high; a pure checkpoint replay can match task-success recovery yet remain unsafe at the tool/effect boundary; and a cold restart can underperform a restart that selectively carries forward durable artifacts.

## Tempered / rejected simplifications added this run
- `High AUROC => enable the critic in production`: directly contradicted in the tested HotPotQA/GAIA settings.
- `If rollback helps failed runs, always rollback when signaled`: false when disruption of successful runs outweighs recovery.
- `A detector trained once is portable`: tempered by cold AUROC `0.527` vs recalibrated `0.885` in the real-time monitor study.
- `Checkpoint restore + idempotency key is enough for exactly-once effects`: contradicted by semantic request regeneration in ACRFence's proof-of-concept.
- `Task success is sufficient to judge recovery safety`: tempered by Atomix, where pure recovery success can tie checkpoint replay even though irreversible-effect handling is a distinct safety property.
- `Cold restart is the cleanest recovery`: tempered by RestartSmart's `71.8%` vs cold restart `66.8%` in its SWE-bench Verified setup.

## Nonempty frontier after this checkpoint
1. **Primary-verify full Fail-Fast / Restart-Smart tables and code artifacts** for false-positive disruption, intervention cut-point semantics, and any correction-prompt ablations. Keep secondary-only details out of claims until verified.
2. **Extract Atomix's exact primary RQ3/combined-stress tables** to quantify when checkpoint replay and transactional recovery diverge on residue/irreversible-effect metrics despite similar task success.
3. **Find a matched detector-vs-intervention factorial study** that holds the recovery mechanism fixed while varying detector quality/calibration, or holds the detector fixed while varying recovery mechanism. This would isolate whether benefit comes from sensing or actuation.
4. **Search commit-time authorization/freshness studies** that revalidate authority/resource versions immediately before durable effects after long trajectories or recovery.
5. **Checkpoint-target selection remains open**: prioritize studies fixing alarm, checkpoint candidate set, restore semantics, model and retry/token budget while varying only historical target policy.
6. **Subgoal/folding negative evidence remains open**: find controlled degradation from wrong decomposition, stale folded summaries, or over-aggressive compression.
7. **Active-memory axis decomposition remains open**: test intervention separately on online update, interference resistance, episodic binding, and hypothesis revision rather than aggregate task success.

## Exact continuation
Next run first action: obtain primary table/code artifacts for `Fail-Fast, Restart-Smart` and verify the richer false-positive-disruption and safe-cut-point claims without relying on secondary renderings. Then inspect Atomix RQ3/combined-stress primary tables for exact effect-safety counts and search for matched detector-vs-intervention designs that isolate sensing quality from recovery mechanics. Keep at least one unresolved checkpoint-target-selection or subgoal/folding negative-evidence branch alive after checkpointing.
