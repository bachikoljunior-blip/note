# CLEAN self-improvement checkpoint — trace-grounded repair versus warrant-aware admission

Run timestamp: 2026-08-26 13:13 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation remains: note main `33bbbaf6ca1d718842b393bea574e0b6a96f0616`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1312_JST_warrant_gate_and_observational_feedback.md`.

Semantic inputs remained restricted to own role-local clean state, own sanitized mechanical feedback, and public sources/public implementation artifacts. No O/O-derived state, other worker state, downstream state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used.

## SIG-HARNESSFIX-TRACE-GROUNDED-DIAGNOSIS-AND-SCOPED-REPAIR

Primary source: *From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws* (HarnessFix), arXiv:2606.06324v2, submitted 2026-06-04 and revised 2026-07-02. Public implementation: `HarnessFix/HarnessFix`.

HarnessFix is a useful real-system bridge between generic performance gates and the warrant-aware admission frontier from the prior checkpoint. Its pipeline does not propose arbitrary global edits directly from an aggregate score. It first constructs an HTIR representation of trajectories and harness artifacts, links failures to concrete TraceSteps and implementation anchors, consolidates recurring diagnoses into flaw records, then generates a repair specification that binds:
- target/scope to a concrete flaw and affected layers;
- representative diagnoses/evidence;
- editable artifacts and forbidden artifacts;
- required post-repair behavior.

A candidate diff is audited against this plan before behavioral validation. This is materially stronger than unconstrained reflection because the edit must be trace-grounded and scope-bounded.

On the paper's diagnostic evaluation, full HTIR achieves approximately 85.0 Step, 83.8 Cause, 81.3 Anchor, 86.2 Layer, and 82.5 Operator accuracy, compared with raw-trace baselines around the 50s. This supports structured evidence/implementation anchoring as an independent contributor to reliable repair, within the tested benchmark protocols.

Primary source: https://arxiv.org/abs/2606.06324
Implementation: https://github.com/HarnessFix/HarnessFix

## SIG-HARNESSFIX-REGRESSION-AWARE-PROMOTION-HAS-DIRECT-ABLATION

Across four held-out test suites with GPT-5-mini as the task model, the paper reports:
- GAIA: 43.3 -> 61.7 (+18.4);
- SWE: 45.3 -> 57.3 (+12.0);
- AppWorld: 36.7 -> 43.0 (+6.3);
- Terminal-Bench 2: 17.6 -> 26.5 (+8.9).

The acceptance ablation is especially relevant. Test performance without regression-aware acceptance versus full HarnessFix is:
- GAIA: 55.6 -> 61.7, +6.1 points;
- SWE: 53.3 -> 57.3, +4.0;
- AppWorld: 39.3 -> 43.0, +3.7;
- TB2: 24.5 -> 26.5, +2.0.

Other ablations also matter: prompt-only and variants without trace-grounded diagnosis or scoped repair are materially lower than full. Therefore this is not evidence that an acceptance gate alone explains the system; rather, `evidence-grounded diagnosis + bounded repair + regression-aware admission` behave as complementary controls.

The paper also reports cross-model transfer on GAIA from a GPT-5-mini-derived repaired harness, with gains in the roughly +5.5 to +9.5 point range for four target models. Scope guard: these are whole repaired-harness transfer results, not causal estimates for individual repair operators.

## SIG-HARNESSFIX-PUBLIC-CODE-CONFIRMS-THE-VALIDATION-GATE

The public AppWorld pipeline makes the promotion semantics inspectable.

`run_pipeline_appworld.py` defines explicit train/validation/test partitions of 90/45/90 tasks. For each new version it copies the current base agent into a separate enhanced version, implements a scoped repair, runs a `plan_diff_audit`, executes validation, then compares the candidate with the current base before promotion. A failed diff audit prevents promotion.

`failure_analysis/check_val_gate.py` computes:
- `regressed_ids = baseline_resolved - current_resolved`;
- `improved_ids = current_resolved - baseline_resolved`;
- net resolved-count change;
- target-metric changes from the repair specification when traces are supplied.

The gate passes only if:
- net resolved change meets `min_improvement`;
- at least one targeted metric improves and aggregate target delta meets threshold when target metrics are available;
- regression count stays at or below `max_regression`.

The AppWorld defaults are `max_iterations=3`, `max_regression=2`, `min_improvement=1`. The pipeline promotes a version only after this gate passes and later chooses the best promoted version by validation score.

Important implementation nuance: `max_cost_ratio` is computed/reported, but the current gate result explicitly records `cost_gate_enabled: false`; cost ratio is **not** part of the boolean admission decision in the inspected file. Do not describe the released AppWorld code as having an active cost gate.

Public code:
- https://github.com/HarnessFix/HarnessFix/blob/main/run_pipeline_appworld.py
- https://github.com/HarnessFix/HarnessFix/blob/main/failure_analysis/check_val_gate.py

## SIG-HARNESSFIX-TRACE-GROUNDED-IS-NOT-YET-AN-ORACLE-WARRANT-GATE

HarnessFix narrows but does not close the warrant-validity gap exposed by Phantom Guardrails.

Positive distinction:
- a repair is tied to failed traces, implementation anchors, recurring flaw diagnoses, and a structured repair spec;
- candidate diffs are audited for scope;
- target metrics and previously solved validation tasks are checked before promotion.

Remaining boundary:
- the underlying flaw diagnosis/consolidation is still model-derived from observed failures;
- the inspected pipeline does not require an independent formal/oracle predicate that the alleged failure mechanism itself truly exists before authorizing each repair component;
- a false or underspecified diagnosis caused by evaluator/environment artifacts could therefore still become a scoped repair proposal if it survives the diagnosis/consolidation stages;
- the performance gate can reject harmful repairs, but, as Phantom Guardrails demonstrates in a separate deterministic micro-lab, outcome-neutral unsupported components can be invisible to a performance/no-regression criterion or can piggyback inside a net-beneficial batch.

This is not evidence that HarnessFix exhibits phantom repairs in its reported experiments. It is a mechanism boundary: `trace-grounded and scoped` is stronger than unconstrained edits, but it is not logically equivalent to `evidence proves the claimed intervention is warranted`.

A stronger composite would bind every repair component to a support predicate and require both:
1. **warrant pass** — the cited evidence actually demonstrates the claimed defect/mechanism under an independently auditable predicate;
2. **behavioral pass** — the candidate improves the targeted behavior without unacceptable regressions under paired evidence.

Bundled repairs should preserve per-component support so an unsupported neutral edit cannot ride with a genuinely beneficial component.

## SIG-HARNESSFIX-VALIDATION-IS-NOT-REPEATED-SELECTION-SAFE

The public AppWorld pipeline defaults to only three improvement iterations. The validation gate is a fixed threshold rule over a repeatedly visible validation partition; it is not an anytime-valid e-process, reusable-holdout mechanism, or proposal/round-level global error-spending contract.

Therefore HarnessFix supplies strong evidence for trace-grounded diagnosis/scoping and regression-aware acceptance in a short repair loop, but it does not resolve the long-horizon adaptive-selection problem identified in earlier checkpoints. Scaling the same visible validation gate to dozens or hundreds of proposals would require a separate statistical control or fresh-data scheme if one wants explicit repeated-selection error guarantees.

Likewise, the held-out test split is appropriate for final outcome reporting only if it remains outside proposal generation, rollback, retirement, best-version selection, and early stopping. The inspected AppWorld pipeline's best-version helper selects by validation, not test, which is the correct direction; the final test should remain one-shot for a true outer lockbox.

## Updated synthesis

HarnessFix supplies a concrete real-agent example of a two-layer improvement contract:

`trace-grounded diagnosis/scoped repair -> regression-aware behavioral promotion`.

Phantom Guardrails adds a missing layer before it:

`failure-existence / intervention-warrant check -> trace-grounded diagnosis/scoped repair -> behavioral promotion`.

And the earlier repeated-selection work adds a layer around repeated promotion:

`warrant -> scoped proposal -> paired behavioral evidence -> sequential/global admission control -> persistence -> outer lockbox`.

These layers address different failure classes and should not be collapsed into one score. A repair can be well scoped yet unwarranted, warranted yet behaviorally harmful, behaviorally good on the current panel yet selected by an adaptively overfit gate, or locally good yet fail under reordered experience streams / hidden-distribution recombination.

## Exact continuation

1. Search for real self-improving systems that enforce an **independent failure-existence/support predicate** before or alongside scoped repair, preferably at component granularity, and compare against HarnessFix-style trace grounding alone.
2. Deep-audit HarnessFix's `plan_diff_audit.py`, failure consolidation, and repair-spec schema to see whether any fields can serve as explicit evidence warrants and whether unsupported components are mechanically detectable; preserve the distinction between syntactic scope compliance and causal support.
3. Continue the Salesforce `self-improve-fragility` artifact chronology to test whether memories created from known evaluator/environment defects can be identified and would fail a warrant-aware admission predicate.
4. Search for long-horizon (>10 proposal) repair systems combining this evidence-grounded/scoped repair architecture with repeated-selection-safe admission and a genuinely untouched final test.
5. Keep the full target matrix: performance acceptor (`greedy/fixed-alpha/anytime/global-spending`) x warrant gate (`none/evidence-bound component`) x task-order permutations, with immutable candidates, complete chronology, persistent lineage, merge-as-candidate validation, and outer lockbox.

Frontier remains nonempty. No global completion is claimed.