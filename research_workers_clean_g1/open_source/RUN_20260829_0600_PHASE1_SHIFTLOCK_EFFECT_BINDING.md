# Open Source Phase-1: Strong Capability Epochs Still Fail If the Effect Consumes Only an ID

Frozen semantic tuple for this invocation remains: `note=8c11c50aa491507fc1cec3ffef72887691cd0966`, root control `22` / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, open_source config `6` / blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`.

This checkpoint continues `RUN_20260829_0545_PHASE1_NETWORK_EPOCH_MCP.md`. The prior leaf derived a replay-safe network pattern and showed Keycloak request-time introspection as a practical revocation-aware gate. This leaf found a particularly useful open-source counterexample: a system can implement an excellent capability-epoch primitive and still lose the guarantee at the final effect API if that API consumes only an opaque capability identifier.

## 1. ShiftLock v0.11.0 has a strong epoch-capability primitive

Exact current `theworker02/shiftlock` main inspected: `abd9c0cb2c5018689678ef551b53d8775729dc6b`. The current `v0.11.0` annotated tag, published 2026-08-14, resolves to the same commit.

`capability/capability.go` has the desired primitive-level properties:

- every token carries `Epoch`, subject, permission, resource, expiry, constraints, nonce and optional signature;
- `AdvanceEpoch()` advances the authority security epoch and is documented to invalidate prior capabilities;
- `Verify()` rejects explicit revocation, rejects any `tok.Epoch != a.epoch`, checks expiry and optional signature, and consumes single/max-use state;
- delegation may only reduce scope;
- the test suite contains `TestEpochInvalidates`, which issues a token, advances epoch and requires `ErrEpochMismatch` on verification.

The current security model likewise states that security epochs do not decrease and advancing an epoch invalidates prior capabilities. Hardened/maximum profiles set `RequireCapabilityForPrivileged=true` and turn on other fail-closed controls.

Exact source-qualified evidence:
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/capability/capability.go
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/capability/capability_test.go
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/docs/security-model.md
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/security.go

## 2. Maintenance shows the detached-verification TOCTOU shape explicitly

`control/maintenance/maintenance.go` defines `EnterRequest.CapabilityID` with the source comment:

`CapabilityID is recorded for audit (verification done by caller).`

`Manager.Enter()` then validates maintenance state/reason/duration and commits durable maintenance state, but does not receive the capability token, verifier, permission, resource or epoch. Therefore the manager cannot tell whether the capability was revoked or its security epoch advanced after a caller's earlier `Verify()` and before `Enter()`.

The current `examples/secure-control-plane/main.go` demonstrates exactly this composition shape:

1. issue `maintenance.enter` capability;
2. call `capAuth.Verify(tok)`;
3. execute unrelated steps;
4. call `rt.Maintenance().Enter(...)` with only `CapabilityID: string(tok.ID)`.

A concurrent `Revoke(tok.ID)` or `AdvanceEpoch()` between steps 2 and 4 makes `capAuth.Verify(tok)` fail if repeated, but `Manager.Enter()` has no current-authority input with which to repeat it. The strong epoch primitive has become detached provenance rather than an effect-bound gate.

This is not a claim that every ShiftLock application is vulnerable. The manager's source contract explicitly assigns verification to the caller. It is a concrete API-composition counterexample showing that **caller-side verification is insufficient to prove revocation-safe effect binding unless the verification and effect share a linearizable boundary**.

Exact sources:
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/control/maintenance/maintenance.go
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/examples/secure-control-plane/main.go

## 3. Lockdown unlock is an even clearer “ID is not proof” interface

`control/lockdown/lockdown.go` documents `UnlockRequest.StrongAuthID` as a separate stronger capability/auth ID. The manager's `Unlock()` requires:

- active lockdown;
- `Confirm=true`;
- exact expected lockdown ID;
- `StrongAuthID != ""`.

It does not receive a capability verifier and does not validate that the ID names an existing, unrevoked, unexpired capability with `lockdown.unlock` permission.

The secure-control-plane example issues a single-use `lockdown.unlock` capability and passes its ID to `Unlock`, but it does not call `capAuth.Verify(strong)` before the effect. The manager's source therefore treats a non-empty identifier as caller-supplied evidence, not as executable proof of current authorization.

Again, this is best interpreted as a composition boundary rather than a blanket product-security conclusion: applications may layer an external check before calling the manager. The important Phase-1 lesson is that an ID field named `StrongAuthID` must not be fingerprinted as a strong authorization gate unless the effect-serving path itself verifies the referenced credential/current authority.

Exact source:
- https://github.com/theworker02/shiftlock/blob/abd9c0cb2c5018689678ef551b53d8775729dc6b/control/lockdown/lockdown.go

## 4. Runtime configuration names are not enough to prove enforcement either

`SecuritySettings.RequireCapabilityForPrivileged` is present and hardened profiles enable it. `NewRuntime()` uses the setting to instantiate the capability authority. But current source search for `capability.Token` outside the capability package found runtime exposure/issuance rather than privileged effect-manager parameters, and `AuthorizeCommand(actor, name, permission)` has no capability argument; it applies control gates and guard policy.

This means capability detection must be call-graph based, not configuration-name based. Seeing `RequireCapabilityForPrivileged=true`, a token type, and a successful verifier test is not sufficient. A Phase-1 verifier must establish where the verified credential is consumed relative to the irreversible effect.

## 5. Source-shaped TOCTOU fixtures

Created and self-tested before persistence:

`research_workers_clean_g1/open_source/CAPABILITY_EFFECT_BINDING_FIXTURES_20260829_0600.py`

The fixtures model the observed contract shape:

- authority verifies exact epoch, permission/resource and explicit revocation;
- detached manager accepts only a non-empty auth ID;
- effect-bound manager validates current authority at its boundary.

Acceptance/counterexample sequence:

- epoch 0 token verifies;
- authority advances to epoch 1;
- the stale token no longer verifies;
- detached ID-only manager still commits because the ID is non-empty;
- effect-bound manager denies the stale token;
- explicit per-token revocation has the same shape;
- an arbitrary non-empty `forged-nonempty-auth-id` is accepted by the ID-only fixture.

All fixtures passed locally before persistence.

This does **not** establish an exploit in ShiftLock; it establishes the exact guarantee that is missing from an ID-only manager contract when current capability verification is expected to happen elsewhere.

## 6. Revised reusable Chat/effect pattern: prove the linearization point

The capability fingerprint now needs one more mandatory question:

**Where is the authorization linearization point relative to the effect commit?**

A safe classification requires at least one of:

- same-authority effect method verifies token/current epoch while serializing the state mutation;
- effect server performs authoritative request-time validation and defines the request-acceptance point as the revocation ordering boundary;
- downstream effect API atomically accepts a current authorization generation/revision as a mutation precondition.

The following are insufficient on their own:

- a prior `Verify(token)` call in application code;
- a capability/token ID copied into an effect request;
- a `strong_auth_id` string whose existence/current validity is not checked;
- a security setting named “require capability” without a call path showing effect-bound consumption;
- a durable checkpoint that says the token was valid earlier.

For Chat resume safety this matters directly: `checkpoint -> revoke/epoch bump -> resume -> effect` must fail at the effect boundary, not merely be detectable by rerunning a verifier that the effect path does not require.

## Semantic barrier / exact continuation

The frozen root/config identities remain unchanged. All ShiftLock research used the exact public release/current-main commit above; no source repository mutation occurred.

Exact Phase-1 continuation:

1. Add `authorization_linearization_point` / `effect_consumes_current_credential` to the capability fingerprint and classifier taxonomy. Distinguish `VERIFIER_STRONG_EFFECT_DETACHED` from `EFFECT_BOUND_CURRENT_AUTH`.
2. Audit one mature production MCP/API gateway call path from bearer/token validation through tool/upstream forwarding, looking specifically for whether revocation/current-user/ACL checks are repeated after long-lived session establishment or only at connection creation.
3. Add a long-lived MCP session counterexample: authorization valid at `initialize`, revoked before `tools/call`; classify safe only if the tool-call path rechecks current authorization or the session itself is invalidated reliably.
4. If no stronger cross-system atomic revision gate appears, treat effect-local/request-bound current authorization plus resource CAS/idempotency as the practical Chat architecture; do not keep searching for version-shaped tokens as a substitute.
5. Then resume safely-authorized GitHub Rule Suite joins from the preserved Phase-1 frontier.
6. Keep the frontier nonempty until runtime/tool termination.

No source repository, branch/ref, PR, issue, release, workflow, DESIRED_STATE, other-worker/downstream state, O state, or shared aggregate ledger was mutated. Writes remain confined to the authorized `research_workers_clean_g1/open_source/` namespace and own immutable receipt namespace.
