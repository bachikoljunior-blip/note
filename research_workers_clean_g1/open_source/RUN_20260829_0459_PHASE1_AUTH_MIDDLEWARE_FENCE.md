# Open Source Phase-1: Revision Provenance Is Not an Effect Lease; Request-Bound Gates Are the Safer Chat Pattern

Frozen semantic tuple for this invocation: `note=8c11c50aa491507fc1cec3ffef72887691cd0966`, root control `22` / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, open_source config `6` / blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`.

This checkpoint continues `RUN_20260829_0402_PHASE1_AUTH_EFFECT_PROVENANCE.md`. The prior run established two independent axes: durable authorization-decision provenance and effect binding. This run bounded the remaining `TRUE_EXTERNAL_REVISION_GATE` search over additional current official/open-source surfaces and extended the executable classifier with provenance-capsule validation and negative fixtures for trace IDs, policy/model versions, causal freshness tokens, and resource CAS.

## 1. Acceptance criterion for a TRUE_EXTERNAL_REVISION_GATE

A positive example must satisfy all four conditions, not merely return a version-like string:

1. an authorization decision exposes an authorization-state revision/epoch `R` to the client;
2. the later external effect request accepts `R` as an input;
3. the effect-serving authority atomically validates that `R` is still valid/current for the authorization authority at the mutation boundary; and
4. a stale/revoked `R` prevents the effect from committing.

Resource-version CAS (`ETag`, blob SHA, generation), policy/model versions, trace IDs, and causal read-freshness tokens are separate capabilities. None are upgraded into effect authority without conditions 2-4.

## 2. Permify Snap Tokens are a useful middle category, not an effect lease

Exact current Permify master inspected: `e00d0522e2e5d9ccadac42625a3d40a9ba905360`.

Official `docs/operations/snap-tokens.mdx` says a Snap Token is an encoded timestamp used so an access-control check is evaluated at a snapshot at least as fresh as the token. The documented workflow is:

- obtain the Snap Token from a relationship/data Write response;
- store it alongside the application resource, e.g. an additional database column;
- pass the token back in later permission checks so the check uses authorization data at least as fresh as that resource timestamp.

The current service proto confirms `DataWriteResponse.snap_token` and `PermissionCheckRequestMetadata.snap_token`.

This is stronger than a generic “read current-ish data” setting because it couples application resource state to an authorization freshness lower bound. It is therefore classified as `CAUSAL_AUTH_FRESHNESS_ONLY`.

It still does not bind a later external mutation. Counterexample:

- `T0`: Check with Snap Token `S` returns ALLOW using auth data at least as fresh as `S`.
- `T1`: access is revoked in Permify after that check.
- `T2`: a separate database/Git/API mutation executes using only the prior ALLOW plus its own resource CAS.

Nothing in the documented Snap Token workflow makes the external effect API validate the permission snapshot at `T2`, so the mutation can still pass its resource CAS after authorization has changed.

Official sources:
- https://github.com/Permify/permify/blob/e00d0522e2e5d9ccadac42625a3d40a9ba905360/docs/operations/snap-tokens.mdx
- https://github.com/Permify/permify/blob/e00d0522e2e5d9ccadac42625a3d40a9ba905360/proto/base/v1/service.proto

## 3. OpenFGA's current MCP guidance favors per-request gating, but exposes no tuple-state decision revision

Exact current OpenFGA main observed: `a7dfe8491dc7f9cd5905f4e9ae6c8e1d718c4bd9`.

Current OpenFGA documentation, updated 2026-08-24, explicitly models MCP authorization as “check every MCP request” before allowing a tool call. Its AuthZEN documentation likewise recommends AuthZEN for API/MCP gateways.

The native API does provide two useful controls:

- immutable `authorization_model_id`, which pins the authorization model/policy version; and
- `HIGHER_CONSISTENCY`, which bypasses query caches and reads the database directly.

But the documented Check result is `allowed`; the sampled public surface does not expose a relationship-tuple snapshot revision analogous to SpiceDB `checked_at`. The model ID pins schema/policy, not the mutable tuple state, and `HIGHER_CONSISTENCY` is a read mode rather than a durable revision token.

Therefore the current MCP pattern is `REQUEST_GATE_NO_DURABLE_REVISION` plus `POLICY_VERSION_ONLY`, not `TRUE_EXTERNAL_REVISION_GATE`. This is still operationally safer for tool effects than checkpointing `authorized=true` and replaying it later, because the authorization check is repeated on each tool request.

Official sources:
- https://openfga.dev/docs/use-cases/mcp-server-authorization
- https://openfga.dev/docs/interacting/authzen
- https://openfga.dev/docs/getting-started/immutable-models
- https://openfga.dev/docs/interacting/consistency

## 4. OPA + Envoy demonstrates why trace/policy provenance must not be mistaken for mutation authority

Exact current OPA main observed: `f1817b4b1d17cfd9f502ecff0328a461dde88f4b`.

OPA decision logs include both:

- `decision_id`, documented as a unique identifier for traceability; and
- per-bundle `revision`, the revision of the policy bundle used for evaluation.

These are valuable audit provenance, but they have different semantics from an authorization-state revision. A decision ID identifies an evaluation. A bundle revision identifies policy code/data packaging. Neither is documented as a token that an unrelated downstream effect API atomically validates before commit.

By contrast, Envoy `ext_authz` is a strong request-bound enforcement point: it calls an authorization service before allowing the request to continue upstream. The documented default is fail-closed when the authorization service is unavailable unless `failure_mode_allow=true` is explicitly enabled. OPA's Envoy plugin implements this external-authorization API.

For Chat/tool safety, this gives a useful separation:

- `decision_id` -> `TRACE_PROVENANCE_ONLY`;
- OPA bundle revision -> `POLICY_VERSION_ONLY`;
- Envoy/OPA inline gate -> `REQUEST_GATE_NO_DURABLE_REVISION`.

The gateway pattern is safer for an immediate effect even without a durable auth revision because the authorization decision is not treated as a reusable client-side lease.

Official sources:
- https://www.openpolicyagent.org/docs/management-decision-logs
- https://www.openpolicyagent.org/docs/envoy
- https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/security/ext_authz_filter.html

## 5. Cerbos agent/tool integrations reinforce the request-bound pattern

Exact current Cerbos main observed: `2101aee6ec7997a437f5dce69ce764903c150e6f`.

Cerbos describes its PDP as an authorization engine for applications, APIs, AI agents, MCP servers, services and workloads. Its current Tailscale Aperture integration intercepts each AI tool call, asks Cerbos for an allow/deny decision, and blocks denied calls before execution. Cerbos Synapse also implements Envoy external authorization natively.

Cerbos Hub versions policy bundles and provides audit history, but the inspected public integration docs do not describe an external tool/effect API accepting a prior Cerbos policy/deployment revision and atomically rejecting the effect when that authorization version is stale.

This is another `REQUEST_GATE_NO_DURABLE_REVISION` / policy-provenance pattern rather than a cross-system revision lease.

Official sources:
- https://docs.cerbos.dev/cerbos/latest/index.html
- https://docs.cerbos.dev/cerbos-hub/integrations-aperture.html
- https://docs.cerbos.dev/synapse/latest/extensions/envoy-extension.html
- https://docs.cerbos.dev/cerbos-hub/deployments.html

## 6. Bounded negative result for TRUE_EXTERNAL_REVISION_GATE

Across the current bounded sample consisting of the prior Authzed/SpiceDB findings plus this run's Permify, OpenFGA, OPA/Envoy and Cerbos surfaces, no public/open-source example satisfied all four TRUE_EXTERNAL_REVISION_GATE conditions.

This is a bounded negative result, not a claim that no such system exists.

The capability ladder now has six distinct useful rungs:

1. `TRACE_PROVENANCE_ONLY` — e.g. OPA `decision_id`.
2. `POLICY_VERSION_ONLY` — e.g. OPA bundle revision or OpenFGA authorization model ID.
3. `CAUSAL_AUTH_FRESHNESS_ONLY` — e.g. Permify Snap Token used as a lower-bound freshness fence for a later authorization check.
4. `REVISION_PROVENANCE_ONLY` — e.g. SpiceDB `checked_at` preserved to the agent, but detached from a later external effect.
5. `REQUEST_GATE_NO_DURABLE_REVISION` / `EFFECT_LOCAL_GATE` — authorization is evaluated inline with the effect request or inside the effect-serving authority.
6. `TRUE_EXTERNAL_REVISION_GATE` — prior decision revision is atomically revalidated by the external effect authority. Still unobserved in the bounded sample.

For safe Chat workflows, rung 5 should be preferred over replaying a detached ALLOW. Resource CAS should still be used independently to prevent stale-resource writes, but it does not repair authorization TOCTOU.

## 7. Executable provenance-capsule classifier v2

Created and self-tested before persistence:

`research_workers_clean_g1/open_source/AUTH_EFFECT_PROVENANCE_MATRIX_20260829_0459_V2.py`

The v2 classifier adds a structured capsule:

`{decision, subject, resource, permission, consistency_mode, token, token_semantics, source_system}`

and requires token semantics to be explicit. Fifteen fixtures plus four provenance invariants passed locally before persistence. New negative/edge fixtures include:

- Permify Snap Token -> `CAUSAL_AUTH_FRESHNESS_ONLY`;
- OPA `decision_id` -> `TRACE_PROVENANCE_ONLY`;
- OPA bundle revision -> `POLICY_VERSION_ONLY`;
- OpenFGA `authorization_model_id` -> `POLICY_VERSION_ONLY`;
- GitHub blob SHA -> `RESOURCE_CAS_ONLY`, never authorization authority;
- Envoy `ext_authz` -> `REQUEST_GATE_NO_DURABLE_REVISION`;
- an API that merely accepts an auth revision but does not atomically reject stale revisions remains only `REVISION_PROVENANCE_ONLY`;
- only the explicit hypothetical fixture with both revision input and atomic stale-revision rejection becomes `TRUE_EXTERNAL_REVISION_GATE`.

This prevents version-shaped strings from being promoted into reusable authority by naming alone.

## Semantic barrier, persistence and continuation

The first role-local semantic read froze the tuple shown above. A later SHA-only note-head observation advanced to `9c76f42557b6dee420c8ff1f424f66b619465b5f`. Frozen DESIRED_STATE blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb` and open_source config blob `3aeff2e6964079f0f2d607874f47422c54d8b30d` were verified unchanged. The connector returned the one-line config body while verifying its blob; that later-head semantic text was quarantined/discarded and not used to change the frozen semantics. The current role-local `LATEST.json` blob also remained `000891fa73311f2d6934d1271f3040d4a7aea5cf`, so no own-state reconstruction conflict existed.

Exact Phase-1 continuation:

1. Inspect capability-token systems and request-bound gateways with a strict discriminator: a bearer/capability token is not a TRUE_EXTERNAL_REVISION_GATE unless the effect authority can atomically tie acceptance to current authorization epoch/revocation state rather than merely validate token signature/expiry.
2. Search official OAuth2/DPoP/macaroons/capability-system and database-policy surfaces for explicit revocation-epoch or authorization-generation inputs at effect commit; keep token validity, resource CAS, and auth revision separate.
3. Extend the classifier with `CAPABILITY_TOKEN` and `REVOCATION_EPOCH` semantics plus negative fixtures for signed-but-revoked-later tokens and positive criteria for effect-side epoch checks.
4. Then return to the GitHub Rule Suite leaf only after this bounded capability-token probe, preserving the request-bound/effect-local recommendation if no stronger external gate appears.
5. Preserve a nonempty Phase-1 frontier; do not restore unrelated base research while the overlay remains active.

No source repository, branch/ref, PR, issue, release, workflow, DESIRED_STATE, other-worker/downstream state, O state, or shared aggregate ledger was mutated. Writes were confined to the authorized `research_workers_clean_g1/open_source/` namespace and own immutable receipt namespace.
