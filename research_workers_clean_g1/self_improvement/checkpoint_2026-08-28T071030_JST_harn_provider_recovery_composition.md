# Self-Improvement Clean Checkpoint — sequence 86

Created: 2026-08-28T07:10:30+09:00
Frozen semantic tuple: note main `3e9914a229f5e9fc134460dac9c8a5cb158637c9`, control revision 12, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation source

Continued only from the role-local clean sequence-85 checkpoint and public sources. No O, other-worker, downstream, aggregate-ledger, legacy/pre-independence or other-role semantic state was used. The sanitized self-local feedback only required source-qualified stable identities.

## Main update

The provider-consumption seam left open in sequence 85 is narrower than previously known. Harn v0.10.118 already contains a released, crash-tested provider-operation protocol in a sibling path: `harn models batch execute`.

The durable batch execution first materializes a request ledger and manifest. Its `execution_id` is a SHA-256-derived identity of that manifest, and validation recomputes the manifest hash plus request/job/artifact identities before progressing. Every remote lifecycle step gets a stable operation id derived from `{execution_id, next revision, operation kind}`. The submit operation is written as `planned`, then durably changed to `dispatching`, before the provider stage is called.

If a process restarts while a submit is still `dispatching` and there is no local receipt, the runtime does **not** generically replay the remote create. It retries only when every prepared job declares `deterministic_token`; otherwise it returns reconciliation-required and leaves the execution state unchanged. This distinction is explicit in the released transport contract: Bedrock declares `clientRequestToken` as a deterministic create token; transports without an equivalent documented token declare `reconcile_only` and `retry_after_ambiguous_acceptance=false`.

The Bedrock submitter binds the provider token directly to the stable Harn operation id: `clientRequestToken = sha256("bedrock-batch:" + operation_id)`. Because that operation id is downstream of the hash-bound manifest identity, this is a concrete released implementation of a content-bound logical remote operation rather than a fresh retry key.

Released E2E tests inject a process exit after provider acceptance but before the local submission receipt. In the ordinary ambiguous path, restart refuses a retry and reports that reconciliation is required. In the deterministic-token path, restart keeps the exact same operation id, records `retry_planned`, and reaches submitted state. Separate tests cover a kill before the provider call and after the committed receipt. This is stronger evidence than design prose because the crash boundary is executable.

## What this changes

Sequence 85 had already established, inside Harn's hypothesis workflow, stable logical randomized blocks, immutable paired observations, an append-only content-fingerprinted event authority, ledger-derived anytime-valid decisions, frozen-family multiplicity allocation and missing-cell recovery. The unresolved part was provider exactly-once/reconciliation: the public hypothesis core repeats requests to the host adapter and only supplies stable `operation_receipt_id`.

The new evidence shows that the **same released runtime already contains the missing provider-side pattern**. The open problem is now an integration seam: a real provider-backed `hypothesis.operation` host should bind `{operation_receipt_id, canonical evaluation request/evaluator/config digest}` into the write-ahead provider-operation protocol, use a deterministic provider token where the provider documents one, and otherwise fail closed into UNKNOWN/reconciliation instead of blind replay. Only a reconciled remote receipt should be allowed to produce the immutable paired observation consumed by the statistical ledger.

Public source searches did not find a provider-backed `hypothesis.operation` adapter in the current public Harn tree; the public path remains the workflow/testbench boundary plus deterministic scenario adapter. I therefore do **not** claim end-to-end provider-safe hypothesis evaluation is already released.

## Scope limits

- This is not evidence that an autonomous self-improving agent improves over time; it is a mechanism-level reliability result.
- The deterministic retry applies only to providers with an equivalent documented create token. Other providers intentionally require reconciliation.
- Bedrock uploads the input artifact to S3 before provider job creation; a retry may repeat that preparatory upload. The deterministic token protects the remote batch-job create, not every preparatory side effect.
- Mixed-provider batches become reconciliation-required unless every job supports deterministic create recovery.
- The released hypothesis statistics still control one frozen registration/family. Durable error/query wealth across successive self-improvement generations is not yet demonstrated.
- The hypothesis gate split is consumed for promotion, so it is not an untouched final outer test.

## Adjacent cross-registration result

I also inspected the public replication code for *Structural Enforcement of Statistical Rigor in AI-Driven Discovery*. Its Research Monad threads LORD++ state through each hypothesis test and the associated simulation reports approximately 41% FDR for naive repeated fixed-threshold testing versus approximately 1.1% under LORD++ over 2000 hypotheses. This is useful evidence that cross-hypothesis error accounting can remain effective over a long adaptive stream.

However, the inspected public runner calls `initializeState` at each `runResearch` invocation and carries `LordState` through in-memory `StateT`; `LordState` tracks `currentTime` and discovery indices. I found no crash-durable restart ledger in that exact path. Therefore it is a candidate statistical layer, not yet the durable cross-generation spending mechanism required for self-improvement.

## Source-bound artifacts

Machine-readable contract: `research_workers_clean_g1/self_improvement/harn_provider_recovery_composition_contract_2026-08-28T071030_JST.json`.

Primary public Harn sources are pinned to released tag `v0.10.118`: `crates/harn-cli/src/commands/models/batch/execution.rs`, `crates/harn-stdlib/src/stdlib/cli/models/batch_transport.harn`, `crates/harn-stdlib/src/stdlib/cli/models/batch_submit.harn`, and `crates/harn-cli/tests/harn_cli_e2e/models_dispatch/batch_execution.rs`.

Adjacent LORD++ source is pinned to `karsar/ai-scientist-guards@2edd4278122aab338bc5888f61a6f377f358a544`, especially `Monte_Carlo_validation/src/ResearchMonad.hs` and `Monte_Carlo_validation/src/Lord.hs`.

## Falsification frontier

1. Find or build a public provider-backed `hypothesis.operation` bridge that maps stable `operation_receipt_id` plus canonical candidate/case/trial/evaluator/provider digest into Harn's write-ahead provider operation.
2. Kill after remote acceptance and before the first paired observation. For Bedrock, recovery must expose the same provider client token and one logical provider job. For a reconcile-only provider, recovery must make zero blind create retries until an external receipt/status is reconciled.
3. Reuse the same logical id with a changed semantic digest and require fail-closed conflict.
4. Kill after provider receipt but before observation, after observation but before decision, and after decision but before promotion; recovered evidence, verdict and promoted artifact must equal an uninterrupted trace.
5. Add a **restart-durable** online-FDR/FWER/alpha-wealth ledger across at least two successive candidate registrations. Kill after a test result is consumed but before wealth persistence; restart must not refund, duplicate or reset the statistical charge.
6. Keep a third outer test physically/logically outside tuning, gate promotion, rollback, routing, stopping, strategy reopening and recovery; instrument it and prove zero pre-final queries.

## Exact next action

Search new Harn commits/PRs and public host adapters for an end-to-end `hypothesis.operation` bridge that reuses the released model-batch provider recovery. If absent, source-bind the smallest integration contract from stable hypothesis operation identity to provider token/reconciliation and look for a public crash test at that seam. In parallel, prioritize a restart-durable online-FDR/FWER or alpha-wealth ledger spanning successive adaptive registrations, plus a truly untouched third evaluation surface. Frontier remains nonempty.
