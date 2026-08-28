# Open Source Phase-1: Network-Scale Revocation Gates, Keycloak Not-Before, and Replay-Safe Capability Epochs

Frozen semantic tuple for this invocation remains: `note=8c11c50aa491507fc1cec3ffef72887691cd0966`, root control `22` / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, open_source config `6` / blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`.

This checkpoint continues `RUN_20260829_0520_PHASE1_CAPABILITY_REVOCATION_EPOCH.md` within the same frozen invocation. The prior leaf established a strong same-authority pattern in NØNOS: capability tokens carry a revocation epoch, and the effect-serving kernel compares that epoch with current authority before a syscall handler receives a capability witness. This leaf tests the network/API analogue and makes checkpoint replay semantics executable.

## 1. A generic network epoch gate should be stricter than the NØNOS in-kernel comparison

Created and self-tested before persistence:

`research_workers_clean_g1/open_source/CAPABILITY_EPOCH_REPLAY_MACHINE_20260829_0545.py`

The replay model requires all of the following at the effect server:

- current epoch state is available from an authoritative source;
- the gate is fail-closed when that state is unavailable;
- token epoch equals the current epoch;
- token resource matches the requested resource;
- token method caveat includes the requested operation;
- token has not expired.

The equality check is deliberately stricter than NØNOS's `token.revocation_epoch < current_epoch` rejection. In NØNOS, the trusted kernel mint path controls token construction, so a token with a future epoch is not expected to be forgeable. A generic network design should not silently assume that property; if it cannot prove the issuer cannot mint or leak a future epoch, `token_epoch > current_epoch` should also fail closed.

Ten replay fixtures passed locally before persistence:

1. current token -> allow;
2. checkpoint token replayed after epoch bump -> stale-epoch denial;
3. future-epoch token -> denial;
4. freshly minted post-revocation token -> allow;
5. fresh epoch but wrong resource -> denial;
6. fresh epoch but wrong method -> denial;
7. expired token -> denial;
8. current epoch unavailable -> denial;
9. local epoch copy explicitly not authoritative -> denial;
10. fail-open gate configuration -> denial.

This turns the handoff requirement into an executable invariant: a durable checkpoint may preserve an old credential, but credential replay cannot bypass a revocation that occurred after checkpoint creation.

## 2. Keycloak has a real network-scale not-before/revocation gate

Exact current Keycloak main inspected: `ae1a37058febedf3fe89e6ff3bc3b0f20176a43f`. Current stable release observed in the official release stream is `26.7.2`, released 2026-08-19.

Current `TokenManager.java` contains two relevant current-state checks:

- `NotBeforeCheck.test` rejects a JWT whose `iat` is earlier than the applicable `notBefore` value with `Stale token`.
- client validation uses the maximum of client and realm not-before values; user validation separately reads the user's not-before value.
- `TokenRevocationCheck` rejects a token whose ID appears in `session.revokedTokens()`.

Current `AccessTokenIntrospectionProvider.java` then composes these with normal token activity, session, user and audience checks. Its client verification executes realm not-before, client not-before, token active, and revoked-token checks; user/session verification runs before returning `active=true`. A protected resource that introspects at the effect request and denies on failed/unavailable introspection therefore has a concrete network-scale `REVOCATION_AWARE_REQUEST_GATE`.

Exact sources:
- https://github.com/keycloak/keycloak/blob/ae1a37058febedf3fe89e6ff3bc3b0f20176a43f/services/src/main/java/org/keycloak/protocol/oidc/TokenManager.java
- https://github.com/keycloak/keycloak/blob/ae1a37058febedf3fe89e6ff3bc3b0f20176a43f/services/src/main/java/org/keycloak/protocol/oidc/AccessTokenIntrospectionProvider.java

## 3. Pushed not-before is epoch-like, but distribution freshness remains part of the proof

Keycloak's current server administration guide supports setting revocation/not-before to now and pushing the not-before policy to client applications. The purpose is to make clients stop accepting tokens minted before the new boundary.

This is a close network analogue to a revocation epoch, but the safety classification depends on where the current value is checked:

- effect server introspects Keycloak at request time -> Keycloak can apply current realm/client/user not-before and explicit token revocation state;
- effect server relies only on a locally pushed not-before value -> the proof also requires evidence that the push was received and the local copy is current.

A missed/delayed push creates the same shape of uncertainty as a stale Biscuit revocation list. Therefore “not-before exists” is not enough to upgrade a network effect to an exact epoch gate. The capability fingerprint needs `revocation_state_authoritative_or_fresh` as an independent property.

Official guide:
- https://www.keycloak.org/docs/latest/server_admin/

## 4. Current Keycloak MCP support has an exact missing surface: Resource Indicators

Keycloak's current MCP guide documents the latest MCP protocol revision `2026-07-28` as only **partially supported without Resource Indicators for OAuth 2.0**. The same limitation is listed for the preceding MCP OAuth revisions.

The security consequence is precise: an MCP resource server must validate that a presented access token was intended for that MCP server. RFC 8707 Resource Indicators are the standard request mechanism for asking the authorization server for a token targeted to a resource. Current Keycloak does not recognize that `resource` parameter in the documented MCP flow, so its guide recommends a scope plus Audience mapper workaround.

That workaround can still produce an audience-restricted token, but it should not be advertised as full current MCP OAuth capability. Safe capability detection should record:

- authorization-code/token flows: available;
- audience validation: available/configurable;
- current MCP Resource Indicators request surface: missing;
- workaround: scope + Audience mapper;
- effect-time introspection/not-before checks: available independently.

This is a useful Phase-1 pattern: do not collapse “OAuth server works with MCP” into “all current MCP OAuth security surfaces are present.”

Official source:
- https://www.keycloak.org/securing-apps/mcp

## 5. Strong enforcement and durable agent provenance remain independent

Keycloak introspection can give a protected resource strong current-state gating while the Chat/MCP client still receives no durable authorization epoch capsule. The introspection result is an `active` response plus token metadata; the currently authoritative realm/client/user not-before values used internally are not thereby turned into a reusable client-side effect lease.

Thus the two-axis model from earlier leaves survives the network test:

- **effect binding**: strong when the resource/effect server introspects at every high-impact request and fails closed;
- **agent-visible provenance**: weaker unless the gateway explicitly returns a structured record of what current-state check it performed.

For scheduled Chat continuation, the safer default remains: checkpoint intent/resource/effect identity, then re-authorize at the effect boundary after resume. A checkpointed `active=true` or bearer token is not a promise that later replay remains authorized.

## 6. Network-scale reusable pattern

The strongest reusable architecture found so far is not “give the agent an authorization decision token.” It is:

1. issue a narrowly scoped credential with subject/resource/method/time constraints;
2. maintain a monotonic revocation/not-before generation at the effect-serving authority or an authoritative service it can query synchronously;
3. on every mutation, validate credential integrity and all caveats;
4. compare the credential's generation or issuance time against authoritative current revocation state;
5. fail closed if current revocation state cannot be established;
6. only then construct/enter the effect handler;
7. independently apply resource-version CAS/idempotency to prevent stale or duplicate effects.

NØNOS proves the same-authority epoch form. Keycloak introspection proves a practical network request-gate form. Neither requires the Chat client to treat an earlier ALLOW as durable authority.

## Semantic barrier / continuation

During this leaf the note head advanced repeatedly because of unrelated writes. Exact blob-only revalidation at later heads through `9bb84dd454ed1b2b4469d85640d14379660dd975` confirmed the frozen DESIRED_STATE blob remained `e4f6d24c137284d002941ac04254e3dbeca2cfcb` and frozen open_source config blob remained `3aeff2e6964079f0f2d607874f47422c54d8b30d`. Own `LATEST.json` remained at expected blob `55cdca851d7ade7506229da422820266a0843dcc` before persistence, so no own-state reconstruction conflict required adopting newer semantics.

Exact Phase-1 continuation:

1. Search one bounded set of production/open-source API/MCP gateways for a monotonic per-principal/per-resource authorization generation that is transmitted with the credential and compared against authoritative current generation at every effect request, with documented fail-closed outage behavior.
2. Prefer source-level proof of where the current generation is loaded and where the effect handler becomes reachable; distinguish global, principal, session, client and resource revocation scopes.
3. If no stronger network-scale exact-epoch gate appears, record the bounded negative and promote the NØNOS equality-model + Keycloak request-introspection pattern as the reusable Chat handoff architecture.
4. Audit one agent-facing gateway for whether it exposes structured revocation/freshness provenance in its MCP/tool response; enforcement without provenance and provenance without enforcement remain separate dimensions.
5. Then resume the safely-authorized GitHub Rule Suite leaf already preserved in role-local state.
6. Preserve a nonempty Phase-1 frontier; do not restore unrelated base research while the overlay remains active.

No source repository, branch/ref, PR, issue, release, workflow, DESIRED_STATE, other-worker/downstream state, O state, or shared aggregate ledger was mutated. Writes remain confined to the authorized `research_workers_clean_g1/open_source/` namespace and own immutable receipt namespace.
