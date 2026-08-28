# Open Source Phase-1: Obot Shows the Practical MCP Pattern — Recheck Current Access on Every Effect-Bearing POST

Frozen semantic tuple for this invocation remains: `note=8c11c50aa491507fc1cec3ffef72887691cd0966`, root control `22` / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, open_source config `6` / blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`.

This checkpoint continues `RUN_20260829_0600_PHASE1_SHIFTLOCK_EFFECT_BINDING.md`. The prior leaf established the negative side of the linearization problem: a strong token verifier is still detached if the effect manager consumes only an ID. This leaf found a mature current MCP gateway call path that implements the practical positive pattern for normal user traffic: the exact MCP route is re-authorized against current, uncached access-control state on each HTTP request before the proxy forwards it.

## 1. Exact current Obot surface

Exact current `obot-platform/obot` main inspected: `3fabdab1b22ddd8810cddf18815d0cfb2682fcfb`.

Latest public release observed: `v0.25.2`, published 2026-08-26.

The current router registers the gateway endpoints:

- `/mcp-connect/{mcp_id}`
- `/mcp-connect/{mcp_id}/{rest...}`

The authorization resource table assigns `GET`, `POST`, and `DELETE /mcp-connect/{mcp_id}` (plus slash variants) to the MCP group. `evaluateResources()` extracts `mcp_id` from the request and calls `checkMCPID()`.

Exact sources:
- https://github.com/obot-platform/obot/blob/3fabdab1b22ddd8810cddf18815d0cfb2682fcfb/pkg/api/router/router.go
- https://github.com/obot-platform/obot/blob/3fabdab1b22ddd8810cddf18815d0cfb2682fcfb/pkg/api/authz/resources.go

## 2. Normal-user MCP access is checked from uncached current state on the request path

Current `pkg/api/authz/mcpid.go::checkMCPID()` performs a special anonymous pass only so the MCP handler can return the authentication challenge; the handler itself rejects unauthenticated access before proxying.

For a normal authenticated user, `checkMCPID()` calls:

`CheckMCPIDAccess(req.Context(), a.uncached, a.acrHelper, user.Info, resources.MCPID)`

The use of `a.uncached` is important. `CheckMCPIDAccess` then reads the current MCP server/instance/catalog entry and, where applicable, asks the access-control helper whether the current user has access through the current catalog/workspace rule.

If the access check returns false or error, authorization returns false/error; the proxy handler is not reached as an authorized request.

Therefore, for effect-bearing MCP messages that arrive as `POST /mcp-connect/{mcp_id}`, the current call path has a concrete authorization linearization point at request admission: the gateway re-evaluates current MCP access before the request is reverse-proxied upstream.

Exact source:
- https://github.com/obot-platform/obot/blob/3fabdab1b22ddd8810cddf18815d0cfb2682fcfb/pkg/api/authz/mcpid.go

## 3. Long-lived session counterexample is avoided for POST tool calls

The relevant failure shape is:

1. MCP `initialize` succeeds while user has access;
2. administrator revokes MCP access;
3. existing client later invokes `tools/call`;
4. gateway incorrectly trusts only the old session authorization and forwards the tool call.

For current Obot's HTTP gateway, an effect-bearing `POST /mcp-connect/{mcp_id}` is independently in the authorized route table and passes through `evaluateResources -> checkMCPID -> CheckMCPIDAccess` before `mcpgateway.Handler.Proxy` forwards it. The proxy then constructs the upstream HTTP request and reverse-proxies only after authentication/current resource authorization has already succeeded.

So, in this path, an old MCP connection/session is not itself the authorization lease for a later POST. Access can change between initialize and the next tool call, and the next effect-bearing POST is checked again.

This is classified as `REQUEST_BOUND_CURRENT_AUTH`, not `TRUE_EXTERNAL_REVISION_GATE`: the gateway's request-admission decision is current and fail-closed with respect to its own access read, but there is still no authorization revision token atomically consumed by an unrelated upstream effect system. Revocation concurrent with an already-admitted proxy request is ordered around the gateway admission point rather than a shared cross-system transaction.

## 4. Important scope exceptions are explicit, not hidden

The same `checkMCPID` source has two branches that should not be misclassified as stale normal-user authorization:

- **Hosted agent principal:** comments state that a hosted agent is authorized by what it was granted, not by what its owner can currently reach. The `authorized_mcp_ids` grant list is the agent principal's authority. Revoking the owner's later access is therefore not, by itself, a revocation of that independently granted agent authority.
- **System MCP server:** `CheckMCPIDAccess` allows an enabled system MCP server and explicitly says the system server will enforce its own authorization. The authorization linearization point moves downstream and must be audited there.

The capability fingerprint therefore needs to record *which principal's authority* is being re-evaluated. “Owner no longer has access” is not a valid stale-session counterexample when the system deliberately minted a distinct agent grant.

## 5. Current enforcement is stronger than agent-visible provenance

`checkMCPID` returns a boolean/error authorization result. The `Proxy` path checks authenticated context, obtains server config, applies hooks/audit, and reverse-proxies the request. The source inspected here does not turn the current ACR evaluation into a structured revocation epoch/provenance capsule returned to the MCP client.

That is acceptable for effect safety because current authorization is enforced on the request path. It reinforces the two-axis rule:

- agent-visible authorization revision/provenance can be absent;
- effect binding can still be strong when the gateway rechecks current authority before every effect-bearing request.

A Chat client should therefore checkpoint intent and effect identity, not assume it can replay an old “authorized” observation. The gateway remains responsible for current authorization when the replayed request actually arrives.

## 6. Capability fingerprint V6

Created and self-tested before persistence:

`research_workers_clean_g1/open_source/CAPABILITY_FINGERPRINT_20260829_0630_V6.py`

V6 adds explicit `authorization_binding` evidence:

- `strong_verifier_available`
- `verification_occurs_in_effect_path`
- `credential_consumed_by_effect`
- `current_authority_rechecked`
- `state_uncertainty_fails_closed`
- `auth_id_only`
- `long_lived_session`
- `tool_call_rechecks_current_auth`
- `session_revocation_synchronously_invalidates`
- `revocation_state_freshness_proved`
- `authorization_linearization_point`
- `cross_system_atomic_revision_gate`

New fail-closed verdicts include:

- `REQUEST_BOUND_CURRENT_AUTH`
- `VERIFIER_STRONG_EFFECT_DETACHED`
- `SESSION_AUTHORIZATION_STALE_RISK`
- `FAIL_OPEN_CURRENT_AUTH_GATE`

Eleven fixtures passed locally before persistence, including:

- ShiftLock ID-only manager -> detached;
- initialize-only session auth -> stale-session risk;
- Obot per-POST uncached ACR recheck -> request-bound current auth;
- Keycloak per-effect introspection -> request-bound current auth;
- ContextForge fail-open revocation lookup -> fail-open gate;
- synchronous proven session invalidation -> request-bound current auth;
- unproven push freshness -> stale-session risk.

## 7. Revised practical Chat architecture

The Phase-1 capability scan now has a stable practical conclusion:

- Do not require the Chat client to possess a reusable authorization decision lease.
- Require every high-impact effect-bearing request to pass through a current, fail-closed authorization boundary.
- For long-lived MCP sessions, never treat successful `initialize` as authority for later `tools/call`; recheck the tool-call POST or prove synchronous session invalidation on revocation.
- Keep resource CAS/idempotency independent from authorization freshness.
- Record the authorization linearization point in capability metadata so recovery logic knows what must be re-evaluated after a checkpoint.

This architecture is weaker than a hypothetical cross-system atomic authorization-revision precondition, but it is directly realizable in current gateways and avoids detached-ALLOW replay.

## Semantic barrier / exact continuation

All public repository reads were exact-current or exact-commit. The frozen root/config identities remain unchanged and newer note-head semantics were not adopted.

Exact Phase-1 continuation:

1. Treat the capability-token/revocation leaf as bounded-complete unless a newly encountered source exposes a true cross-system atomic revision precondition; do not continue searching version-shaped tokens without new evidence.
2. Carry `authorization_linearization_point` and long-lived-session freshness into the GitHub Rule Suite/effect reconciliation work already preserved in role-local state.
3. Resume the GitHub server-derived merge/effect leaf: determine how Rule Suite evaluation result, async/queue merge result, exact head SHA, and effective policy evidence should be joined without treating pre-merge authorization/policy observations as leases.
4. Preserve `REQUEST_BOUND_CURRENT_AUTH` vs `PROVED_EFFECT_FOR_TESTED_INVOCATION`: current authorization proves the request gate, while only exact merge/result readback proves the effect.
5. Keep nonempty frontier and persist exact continuation before termination.

No source repository, branch/ref, PR, issue, release, workflow, DESIRED_STATE, other-worker/downstream state, O state, or shared aggregate ledger was mutated. Writes remain confined to the authorized `research_workers_clean_g1/open_source/` namespace and own immutable receipt namespace.
