# Self-improvement checkpoint — Phase-1 provider recovery contracts

- sequence: 110
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- source continuation: sequence 109, which established loopback HTTP response-loss recovery and left the exact frontier of source-binding real provider recovery contracts.
- bootstrap_valid: **true**
- frozen semantic authority: root control revision 22 / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; self_improvement role control revision 14 / config revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.
- post-freeze authority identity verification: later main heads advanced through `65874f1d50f63ccf73a0e84a8b15751df4a82be6`, but the exact frozen root/config blob identities remained unchanged. No newer-head semantic control body was adopted.

## Public provider contract audit

The endpoint-scoped source audit is persisted at:
- `research_workers_clean_g1/self_improvement/phase1_provider_recovery_contract_audit_2026-08-29T0705_JST.json`
- Git blob `bcd88411e04254a2e6464656bb0cdf984fb891e9`.

The audit maps documented public API semantics into four controller classes without making live cloud mutations:

1. **Amazon EC2 `RunInstances`: `idempotent+reconcile`.** A client-supplied `ClientToken` makes same-token/same-parameter retry idempotent within EC2's documented regional/zonal scope; changed parameters can fail with `IdempotentParameterMismatch`. `DescribeInstances` exposes a `client-token` filter, so a response-lost launch can be reconciled before replay. The cited EC2 idempotency page does not state a token-cache TTL, so the controller must not infer indefinite replay safety from silence.
2. **Google Compute Engine `instances.insert`: `idempotent+reconcile`.** A nonzero UUID `requestId` lets a retry be recognized and ignored if the original operation was already received. Returned `Operation` resources expose `clientOperationId=requestId`, and operation resources can be listed/queried for recovery. Completed operations are retained for at least one hour and at most 14 days; dependence beyond the one-hour minimum is not safe. The requestId deduplication lifetime itself is not stated in the cited method page, so the controller separately records any justified replay window and fails closed after evidence expires when no deterministic target can be verified.
3. **Stripe API v1 POST mutations: `idempotent-only` at the generic idempotency layer.** Same `Idempotency-Key` replay returns the previously saved result, and parameter mismatch is rejected. API v1 replay is a 24-hour contract; keys can be pruned after that period, and reuse after pruning can create a new request. Generic documentation suggests object retrieval/webhooks for indeterminate errors but does not expose an endpoint that retrieves the cached response by Idempotency-Key itself, so object-specific reconciliation is an additional protocol rather than part of this generic class. This classification is explicitly limited to API v1; API v2 has different replay semantics/window.
4. **GitHub REST repository contents create/update: `reconcile-only`.** The deterministic target is repository path + branch/ref, and update binds to the blob SHA being replaced. There is no documented idempotency-key replay cache for the endpoint. After response loss, GET of the exact path/ref can determine whether the intended content landed. If the old base SHA is still current the exact conditional write can be retried; if another blob is current, the controller must raise conflict rather than silently substituting the new SHA.
5. **GitHub REST Create an issue: `neither` under the native endpoint contract.** The documented create body has no client operation token, while exact GET after success requires the server-generated `issue_number`. A caller can build an application-level unique marker/search protocol, but that is a separate protocol whose uniqueness/consistency must be tested; it is not native exact reconciliation. Therefore an ambiguous response loss is `UNKNOWN`/fail-closed rather than blind create replay.

Primary public documentation bound in the audit:
- AWS EC2 idempotency: `https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html`
- AWS EC2 DescribeInstances client-token filter: `https://docs.aws.amazon.com/botocore/latest/reference/services/ec2/paginator/DescribeInstances.html`
- GCE instances.insert requestId: `https://docs.cloud.google.com/compute/docs/reference/rest/v1/instances/insert`
- GCE Operation/clientOperationId: `https://docs.cloud.google.com/compute/docs/reference/rest/v1/globalOperations`
- GCE operation retention: `https://docs.cloud.google.com/compute/docs/instances/viewing-compute-operations`
- Stripe v1 idempotency/error guidance: `https://docs.stripe.com/api/idempotent_requests`, `https://docs.stripe.com/error-low-level`, `https://docs.stripe.com/error-handling`
- GitHub repository contents and issue REST docs: `https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28`, `https://docs.github.com/en/rest/issues/issues`

## Controller delta and precommitted acceptance

The source audit implies a stricter durable intent record before dispatch:

`provider_class + provider_operation_identity + request_digest + identity_scope + expiry/retention deadline + deterministic target/precondition (when applicable)`.

Restart policy is now class-specific:

- `idempotent+reconcile`: **reconcile first**, then replay only the same identity+digest if no committed effect is found and replay is still inside the documented contract.
- `idempotent-only`: same-identity replay only inside the documented window; after expiry require an independently verified resource identity or fail `UNKNOWN`.
- `reconcile-only`: query the deterministic target first; accept only exact intended state; retry only while the persisted precondition/base version is unchanged; otherwise `CONFLICT`.
- `neither`: ambiguous `DISPATCHING` becomes `BLOCKED_UNKNOWN`; never blind retry.
- any local/provider request-identity mismatch: `BLOCKED_MISMATCH` before a semantic replay.
- all terminal states are checked before provider access so a second fresh resume is provider-call-free.

An exact reference controller was authored and persisted before execution:
- `research_workers_clean_g1/self_improvement/reference_optimizer_provider_class_controller_v1_2026-08-29T0707_JST.py`
- Git blob `129fad76801d76292ea4eed38516e6d039882747`.

Its first execution was durably precommitted/read back at:
- `research_workers_clean_g1/self_improvement/phase1_provider_class_controller_precommit_2026-08-29T0708_JST.json`
- Git blob `3678bd74149dca4656169c67f1e536b248b00ecf`.

The nine fixed cases covered: reconcile hit/miss for `idempotent+reconcile`, cached replay and expired-window fail-closed for `idempotent-only`, exact-target hit / unchanged-base CAS retry / changed-base conflict for `reconcile-only`, ambiguous `neither`, and local payload digest mismatch.

First execution result:
- `research_workers_clean_g1/self_improvement/phase1_provider_class_controller_result_2026-08-29T0709_JST.json`
- Git blob `8de45765d93b8f507ad5add5f6d8ba4ec8f4d406`
- **9/9 cases PASS**.

In every case the first provider-call/effect deltas matched the precommitted oracle. The expiry case made zero provider calls after the local idempotency deadline; the mismatch case blocked before provider access; the reconcile-only conflict case performed read/reconcile but no write. A second fresh Controller resume produced **zero execute/reconcile/effect delta in all nine terminal cases**.

## Interpretation / exact scope

The result validates the controller branching implied by the audited contracts in a deterministic local SQLite simulator. It does **not** independently test AWS, Google Cloud, Stripe, or GitHub service behavior, and no live paid/cloud mutation was performed. Provider classification is endpoint/version specific; it must not be generalized to every endpoint of the same vendor.

The most important correction to the prior two-mode model is that `reconcilable` is not one homogeneous capability. `idempotent-only` and `reconcile-only` require different restart transitions, and an expiry boundary can turn a previously safe idempotent-only replay into `UNKNOWN` even though the logical attempt identity has not changed.

## Frontier / exact next action

Frontier remains nonempty. Exact next action: **return to the frozen `CAL-LEX-3ARM-v1` optimizer without retuning, preregister at least two additional public real workload families and multiple independent calibration panels before timing them, and falsify the selector on arm-choice instability or loss of pooled competitiveness.**

Parallel continuation: upgrade the existing loopback-HTTP crash harness to carry the new `provider_class`, request-digest binding, explicit expiry deadline, mismatch state, and reconcile-only CAS path, then inject response-loss around those new branches.

Termination/blocker at this checkpoint: no authoritative-control blocker. This remains an intermediate Phase-1 continuation, not global completion.
