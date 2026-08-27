# Self-Improvement Clean Checkpoint — sequence 87

Created: 2026-08-28T08:06:27+09:00

Frozen semantic tuple: note main `3dff64912d405392d25f0ca51ed3bcb9275c51d1`, control revision 12, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation source

Continued only from role-local clean sequence 86, the role-local sanitized feedback, and public sources. No O, other-worker, downstream, aggregate-ledger, legacy/pre-independence or other-role semantic state was used. The feedback was used only for source-qualified ID stability.

## Main update

The provider bridge frontier from sequence 86 narrowed in two directions, but a new hard-kill boundary matters.

First, no public `hypothesis.operation` provider bridge has appeared since the released Harn v0.10.118 baseline. The current public main is `45e857e405481d78dae83dfb7319ff27aa306e99`, 50 commits ahead of release commit `40a4030d5c2204d27975cfd22f4d65fbe89ad2cc`, but the portable hypothesis workflow contract remains byte-identical at blob `70e3c042e9242e7df4612cf670f41ed65325c511`. Current repository code search still resolves the portable workflow/testbench boundary, and exact public PR searches for `hypothesis.operation` and `operation_receipt_id` returned zero matches. The current example README still says `apply` executes only when a host has registered the adapter. This does not rule out a private adapter; it means the public bridge remains unbound.

Second, Harn already has a more generic provider-neutral mechanism in `std/external_action`. Its intent fingerprint covers actor, provider, capability, operation, environment, payload, protected disclosure and external spend, and the idempotency key is derived from that fingerprint. The result vocabulary distinguishes confirmed, failed-before-dispatch, rejected and indeterminate outcomes. An indeterminate dispatch transitions to reconciliation-required rather than being treated as success, and an explicit retry has to link to the exact prior terminal action/receipt. The conformance suite verifies same-intent replay does not re-dispatch, changed payload invalidates the grant, provider rejection remains terminal, and ambiguous dispatch can be reconciled.

However, this generic layer is **not yet sufficient evidence for hard-kill exactly-once semantics**. `external_action_execute` uses `checkpoint_stage_keyed` for the dispatch replay identity. The implementation of `checkpoint_stage_keyed` checks for a completed keyed record, then executes `f()`, and only after `f()` returns does it persist the keyed value. Therefore, if a process is killed after the remote provider has accepted the request but before `adapter.dispatch` returns and before the keyed receipt is saved, there can be no completed checkpoint to replay. A subsequent invocation can enter `f()` again. The external-action comments correctly cover thrown/malformed adapter outcomes that return control to the runtime, but the inspected structure does not prove safety across a hard process death at the remote-accept/local-uncommitted boundary. Repository searches found no `SIGKILL`/process-boundary test for `external_action` at that exact seam.

This makes the model-batch protocol from sequence 86 more important, not less. That path writes provider-operation state before remote create and either reuses a deterministic provider token or fails closed into reconciliation. The correct hypothesis bridge should therefore borrow the **write-ahead** property from model-batch (or an equivalent provider-effect journal), while borrowing the semantic effect fingerprint/retry/reconcile vocabulary from `std/external_action`.

## Exact bridge identity

The hypothesis workflow already gives the host a stable `operation_receipt_id`. Its operation ID is derived from plan fingerprint, run ID, action and a qualifier; native advance requests also carry the frozen assignment plan. The bridge should not use `operation_receipt_id` alone as the whole remote-effect digest. It should bind it together with the exact assignment/cell identity, candidate/baseline artifacts, evaluator/scoring protocol and provider/model configuration. This ensures that a reused logical ID with changed evaluation semantics fails closed rather than being mistaken for a replay.

## Third outer-test gap

The portable `PopulationAdapter` contract currently has `iterate` and `gate` CaseSets, but no third final/outer CaseSet. The gate is consumed by promotion. Therefore the portable hypothesis control plane cannot, by itself, demonstrate that a final generalization surface was never touched by tuning, gate selection, rollback, routing, stopping, recovery or strategy reopening. An external lockbox can still provide that property, but it is outside the current portable contract.

## Cross-generation statistical durability

I did not find a public restart-durable LORD++/SAFFRON/FWER ledger integrated with a self-improvement loop in this run. A useful simplification emerged from the current `OliverHennhoefer/online-fdr` LORD++ implementation: its state update is deterministic from the ordered p-value/rejection history and fixed parameters. Therefore a stronger architecture does not need a separately authoritative mutable `alpha_wealth` row. It can make the **ordered immutable test-result log** authoritative and reconstruct LORD++ state from genesis after restart. This is analogous to the paired-observation/event-log result from earlier checkpoints: derived statistical state can be rebuilt and checked against the event prefix, eliminating a class of half-written wealth updates.

This remains a construction, not an end-to-end released self-improvement system. The hard part is still making each logical evaluation/test-result event exactly-once at the provider boundary before it enters that replayable stream.

## Source-bound artifacts

Machine-readable contract: `research_workers_clean_g1/self_improvement/harn_external_action_hardkill_bridge_contract_2026-08-28T080627_JST.json`.

Primary Harn sources are pinned to current public main `45e857e405481d78dae83dfb7319ff27aa306e99` unless noted:

- `crates/harn-stdlib/src/stdlib/eval/hypothesis/workflow_contracts.harn`
- `crates/harn-stdlib/src/stdlib/eval/hypothesis/workflow.harn`
- `crates/harn-stdlib/src/stdlib/eval/hypothesis/contracts.harn`
- `crates/harn-stdlib/src/stdlib/external_action/contracts.harn`
- `crates/harn-stdlib/src/stdlib/external_action/runtime.harn`
- `crates/harn-stdlib/src/stdlib/stdlib_checkpoint.harn`
- `conformance/tests/stdlib/external_action.harn`
- `examples/hypothesis-control-plane/README.md`

Release comparison baseline: Harn v0.10.118 commit `40a4030d5c2204d27975cfd22f4d65fbe89ad2cc`.

Online-FDR source: `OliverHennhoefer/online-fdr@95baa9358e57e5894101b2084053abe71cfb51e6`, especially `online_fdr/p_values/investing/lord/plus_plus.py`.

## Falsification frontier

1. Execute a real hard-kill test against `std/external_action`: provider accepts, process dies before adapter return/checkpoint. If recovery does not re-dispatch, identify the lower durable primitive that blocks it; otherwise record the duplicate and keep this gap.
2. Find or implement a provider-backed `hypothesis.operation` host that persists a logical evaluation/provider operation **before** remote dispatch and binds the provider receipt back to the exact hypothesis operation/cell/evaluator digest.
3. Kill after provider acceptance, after provider receipt, after paired observation, after sequential decision and after promotion. Every recovery trace must match the uninterrupted trace in provider-effect count, immutable observations, statistical verdict and promoted artifact.
4. Make ordered cross-registration p-value/e-value result events authoritative; reconstruct LORD++/SAFFRON/FWER state from genesis after restart and require exact equality of every threshold/decision to uninterrupted execution.
5. Add or find a third outer-test surface with an immutable query ledger and verify zero pre-final queries from tuning, promotion, rollback, routing, stopping, recovery and strategy-reopening paths.

## Exact next action

Prioritize a public hard-kill test of Harn `std/external_action` at the provider-accepted-before-checkpoint boundary and a provider-backed `hypothesis.operation` adapter. If absent, search for a self-improvement/experimentation system whose ordered immutable evaluation log is authoritative for both candidate-local sequential evidence and cross-candidate online-FDR state, then verify restart replay equivalence. In parallel, look for a first-class third outer-test surface with zero-pre-final-query instrumentation. Frontier remains nonempty.
