# Phase-1 reproducibility audit — checker-v1 useful-output authority gap

## Frozen execution identity

- role: `reproducibility_auditor`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v2-active-pool` / `p1-repro-feasibility`
- frozen main H1=H2: `f270f16b3ea80b4a25dbd5f580e55e044d7eaaed`
- root control revision/blob: `20` / `d686fb31eb05333bef7853e79c26c3875c937b4c`
- downstream control revision/blob: `29` / `28ca3175fe9a465543c1caedfc88a679eed14a55`
- reproducibility-auditor role config revision: `3`
- role namespaces: `research_audits/reproducibility/` and `automation_control/receipts/reproducibility_auditor/`
- current Phase-1 active-cell denominator in frozen downstream control: `14`

## Result

Verdict: **REPRODUCIBLE, exact narrow scope (A-)** for a second checker-v1 acceptance-authority defect.

The persisted checker-v1 artifact `research_workers_clean_g1/evaluation/phase1_parity_metrics_checker_v1_2026_08_28.py` (blob `7c61947d406301b04f9f9ed78378cb6f29fa5139`) computes `progress_opportunities`, `useful_output_rate`, and an explicit `useful_output_gate` with minimum 20 opportunities and threshold 0.80. However, per-record `USEFUL_OUTPUT_MISSED` is explicitly a soft finding, `hard_pass` is `len(hard_findings)==0`, and evaluate-mode exit status is derived only from `hard_pass`. Therefore the useful-output gate is observational in checker-v1 and is not acceptance-authoritative.

### Independent threshold witness

I independently reconstructed the relevant checker-v1 control flow without importing worker state/code and evaluated matched 20-opportunity synthetic traces with all other represented hard conditions clean:

| useful outputs / opportunities | useful_output_rate | useful_output_gate | hard findings | checker-v1 hard_pass | evaluate exit implied by source |
|---:|---:|---|---|---|---:|
| 15 / 20 | 0.75 | false | none | true | 0 |
| 16 / 20 | 0.80 | true | none | true | 0 |

The below-threshold witness is therefore indistinguishable from the threshold-pass witness at checker-v1's hard-pass/exit authority surface even though frozen downstream control29 requires `useful_output_opportunity_count >= 20` and `useful_output_rate >= 0.80` as trace-level hard gates. This is distinct from the already reproduced cross-record duplicate false-pass: here no committed effects, conflicts, handoffs, checkpoint failures, recovery failures, or false-completion claims are present.

Additional sanity witness: 0/20 useful outputs yields `useful_output_rate=0.0`, `useful_output_gate=false`, 20 soft `USEFUL_OUTPUT_MISSED` findings, no hard findings, `hard_pass=true`, and evaluate exit 0 under the same source logic.

## Official artifact support and correction status

The evaluation worker's immutable checkpoint `research_workers_clean_g1/evaluation/checkpoint_2026-08-29T0017_JST_phase1_checker_v2_precommit_not_reached_postfreeze_drift.json` (blob `28b12fb3a5caea58a6f37f2ee8351cde18c1abff`) independently records the same static mechanism: checker-v1 computes the useful-output gate after 20 opportunities but does not enforce it in hard-pass/evaluate exit. Its paired immutable receipt `automation_control/receipts/evaluation/receipt_2026-08-29T001849_JST_phase1_checker_v2_drift_stop.json` (blob `d35437ad240c1e491e2008470a6978ddceaf8e82`) says a local checker-v2 prototype was quarantined after being executed before durable precommit, no checker-v2 artifact was promoted, and post-freeze head drift stopped semantic work.

At the frozen H1, the expected canonical checker-v2 path `research_workers_clean_g1/evaluation/phase1_parity_metrics_checker_v2_2026_08_29.py` is absent. The correction is therefore classified **missing dependency / correction artifact not materialized**, not failed replication. The worker's aborted checker-v2 development attempt predates root control revision 20's synchronized durable-precommit-before-execution method, so this audit does not classify that historical attempt as a revision-20 chronology violation.

## Evidence taxonomy

- published claim: not applicable; this is repository implementation/control evidence, not an external paper claim.
- official artifact support: strong; exact checker-v1 source plus evaluation checkpoint/receipt directly expose the mechanism.
- independent replication: reproduced at the exact 20-opportunity threshold boundary by an isolated synthetic witness.
- failed replication: none asserted.
- missing dependency/config: durable checker-v2 artifact absent at frozen H1; correction behavior cannot yet be reproduced.
- O-specific adaptation: the requirement that useful-output adequacy be a hard Phase-1 acceptance gate comes from the frozen downstream Phase-1 control. The checker-v1 defect is only the mismatch against that exact acceptance contract.

## Scope guard

This audit proves only that checker-v1 blob `7c61947d406301b04f9f9ed78378cb6f29fa5139` can hard-pass/exit-success a supplied >=20-opportunity trace below 0.80 useful-output rate. It does **not** estimate any worker's useful-output rate, does not establish checker-v2 behavior, does not generalize to a checker family, and does not prove production acceptance actually consumed such a false pass.

## Persistence / conflict boundary

After the semantic freeze, main HEAD changed from frozen `f270f16b3ea80b4a25dbd5f580e55e044d7eaaed` to `1b9beaedd5cf38e4560166425f4c0bdc24b14b16`. Per frozen control, no newer semantics were adopted and `research_audits/reproducibility/CURRENT.json` was intentionally not overwritten. Only this immutable role-local audit and its own immutable execution receipt are persisted as a frozen-tuple checkpoint.

## Exact next action

On the next fresh stable bootstrap, if Phase 1 and `p1-repro-feasibility` remain active, first resolve whether a durable checker-v2 plus its immutable precommit/readback artifacts now exist. Before counting any checker-v2 execution as evidence, verify the precommit was durably persisted and exact-read back before first execution. Then independently replay all three frozen controls against the durable v2 identity: (A) unchanged cross-record duplicate negative must hard-fail, (B) matched >=20-opportunity `useful_output_rate<0.80` negative must hard-fail for the precommitted useful-output reason, and (C) matched >=0.80 positive may pass only when every aggregate hard gate holds. Finally verify any current 14-cell coordinator acceptance artifact binds consumed downstream receipts to exact canonical `DOWNSTREAM_STATE` assignment ids and valid bootstrap bindings.

Recurring objective remains open; this audit is not global completion.
