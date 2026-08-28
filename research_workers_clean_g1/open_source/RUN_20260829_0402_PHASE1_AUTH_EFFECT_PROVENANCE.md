# Open Source Phase-1: Authorization Provenance and Effect Binding Are Independent Capabilities

Frozen semantic tuple for this invocation: `note=63e0f497bc9157c6c5075a8c615327dc49b8e76a`, root control `21`, open_source config `6`.

This checkpoint continues `RUN_20260829_0254_PHASE1_AUTH_REVISION_FENCE.md`. The prior run established that SpiceDB can return an exact authorization-state revision (`checked_at` / ZedToken), but that the token is not by itself authority for a later external mutation. This run tested whether agent-facing MCP surfaces preserve that provenance and whether a concrete effect system accepts the authorization revision as an atomic mutation precondition.

## 1. Authzed/SpiceDB MCP surfaces have different provenance behavior

Two current official Authzed repositories expose materially different behavior.

### A. Current `authzed/zed` Dev MCP preserves the permission-check revision

Exact current `authzed/zed` main inspected: `3ed81d1ca8301affa051a13b6a87a216b499ea7e` (also the commit underlying current `v1.2.1`, published 2026-08-26).

In `internal/mcp/mcp.go`, the `check_permission` tool:

- issues a fully-consistent `CheckPermissionRequest`;
- receives `response.CheckedAt`;
- returns an MCP text result containing both the permissionship and
  `Checked at revision: <response.CheckedAt.Token>`.

Therefore this tool **does preserve a ZedToken through the agent-facing MCP result**. A client can checkpoint the exact authorization revision used by the standalone permission check.

Scope is crucial: Authzed's Zed documentation states that `zed mcp experimental-run` starts an in-memory development SpiceDB and does **not** connect to a running SpiceDB instance. This is revision provenance for a sandbox/dev authorization database, not proof of production authority.

Official sources:
- https://github.com/authzed/zed/blob/3ed81d1ca8301affa051a13b6a87a216b499ea7e/internal/mcp/mcp.go
- https://github.com/authzed/zed/releases/tag/v1.2.1
- https://authzed.com/docs/zed/installation

### B. The same Dev MCP discards mutation revisions

The Dev MCP's `update_relationships` and `delete_relationships` handlers call `WriteRelationships` but discard the returned response and emit only human-readable success/count text.

The underlying current Authzed API contract returns `WriteRelationshipsResponse.written_at` as a ZedToken, and `DeleteRelationshipsResponse.deleted_at` likewise. Those revision-bearing fields are therefore lost at this MCP adapter boundary.

This is a concrete capability-loss pattern: the backend API has durable mutation provenance, while the agent-facing adapter erases it.

### C. The hosted authorization reference checks production-configurable SpiceDB but erases `checked_at`

Exact current `authzed/mcp-server-reference` main inspected: `488d77b4660d654348a21849b9124ba65526e60c`.

Its `with-authorization` example configures a SpiceDB client from `SPICEDB_ENDPOINT` / `SPICEDB_TOKEN`, so it can target a configured SpiceDB service rather than the Dev MCP's in-memory sandbox.

For the protected `echo` tool, the handler:

1. calls `checkPermission`;
2. tests only `permissionResult.permissionship`;
3. denies unless it is `HAS_PERMISSION`;
4. on success returns only the tool output.

It never carries `permissionResult.checkedAt` into the MCP result or a durable audit object. The reference's own authorization document describes the gate as permission-check-before-execution, but the revision provenance is not exposed.

This surface therefore has the opposite shape from Dev MCP `check_permission`:
- stronger immediate request-bound enforcement against a configurable SpiceDB;
- weaker durable decision provenance for the Chat/MCP client.

Official sources:
- https://github.com/authzed/mcp-server-reference/blob/488d77b4660d654348a21849b9124ba65526e60c/with-authorization/src/app/api/%5Btransport%5D/route.ts
- https://github.com/authzed/mcp-server-reference/blob/488d77b4660d654348a21849b9124ba65526e60c/with-authorization/src/lib/spicedb-client.ts
- https://github.com/authzed/mcp-server-reference/blob/488d77b4660d654348a21849b9124ba65526e60c/with-authorization/AUTHORIZATION.md

## 2. SpiceDB mutation preconditions are transactional, but they are not authorization-revision preconditions

Current `authzed/api` main remains `d5fc38fe34ec0a74f782e4328d978a3cbac633b4`.

`WriteRelationshipsRequest` supports `optional_preconditions`. The API says all updates are applied transactionally, all preconditions must be satisfied before commit, and the whole transaction is reverted if any precondition fails.

However, those preconditions are `MUST_MATCH` / `MUST_NOT_MATCH` predicates over relationship filters. The request does **not** accept a `checked_at` ZedToken as an expected authorization revision. `WriteRelationshipsResponse` returns the *resulting* `written_at` revision after the write.

So even inside SpiceDB itself, the closest transactional primitive observed is a relationship-state predicate, not “execute this mutation only if authorization decision revision R is still authoritative”.

Official source:
- https://github.com/authzed/api/blob/d5fc38fe34ec0a74f782e4328d978a3cbac633b4/authzed/api/v1/permission_service.proto

## 3. Stronger alternative pattern: put authorization inside the effect-serving authority

No inspected open-source surface in this run provided a positive example of a cross-system external effect API accepting a prior authorization decision revision as an atomic mutation precondition.

A different pattern is stronger than a detached check: **do not transfer the decision at all; evaluate authorization in the same authority that performs the effect.**

Two current examples:

- Kubernetes API requests are authenticated and authorized inside the API server; requests that are not allowed are rejected, and allowed modifying requests proceed through admission/validation before being written to the object store. This is request-bound authorization at the effect service, not a reusable client-side decision token.
- PostgreSQL Row-Level Security evaluates policy expressions as part of the query. `USING` controls which existing rows can be processed, and `WITH CHECK` rejects proposed inserted/updated rows that do not satisfy policy. For row mutations subject to RLS, authorization and the data effect are co-located in the database operation/transaction.

PostgreSQL scope exceptions must remain explicit: superusers and `BYPASSRLS` roles bypass row security; table owners normally bypass unless `FORCE ROW LEVEL SECURITY` is used; whole-table operations such as `TRUNCATE` and `REFERENCES` are not governed by RLS.

This produces a more useful capability lattice for Chat workflows:

1. `REVISION_PROVENANCE_ONLY` — exact auth revision is returned, but later external effect is detached.
2. `REQUEST_GATE_NO_DURABLE_REVISION` — effect request is gated immediately, but the decision revision is not surfaced for durable continuation.
3. `EFFECT_LOCAL_GATE` — authorization/policy is evaluated within the effect-serving system itself.
4. `TRUE_EXTERNAL_REVISION_GATE` — an external effect API atomically accepts an auth decision revision/epoch as mutation precondition. **Not observed in the inspected scope.**

The axes “does the client get durable decision provenance?” and “is authorization bound to the effect?” are independent. A robust Chat transaction should record both rather than collapsing them into a single `authorized=true` bit.

Official sources:
- https://kubernetes.io/docs/concepts/security/controlling-access/
- https://kubernetes.io/docs/reference/access-authn-authz/authorization/
- https://www.postgresql.org/docs/18/ddl-rowsecurity.html
- https://www.postgresql.org/docs/current/sql-createpolicy.html

## 4. Executable classifier

Created and locally self-tested before persistence:

`research_workers_clean_g1/open_source/AUTH_EFFECT_PROVENANCE_MATRIX_20260829_0402.py`

Seven fixtures passed:

1. Zed Dev MCP standalone check -> `SANDBOX_REVISION_CHECK`.
2. Authzed reference protected echo -> `REQUEST_GATE_NO_DURABLE_REVISION`.
3. Zed Dev MCP relationship write -> `MUTATION_REVISION_ERASED`.
4. PostgreSQL RLS row update -> `EFFECT_LOCAL_GATE`.
5. PostgreSQL BYPASSRLS exception -> `UNPROVED`.
6. production SpiceDB revision check followed by detached external write -> `REVISION_PROVENANCE_ONLY`.
7. hypothetical effect API that atomically accepts the auth revision -> `TRUE_EXTERNAL_REVISION_GATE`.

The last fixture is intentionally hypothetical so the classifier cannot accidentally upgrade “revision returned by a check” into “effect authorization lease”.

## 5. Design requirement for agent-facing authorization adapters

For durable Chat continuation, an authorization wrapper should expose a structured provenance capsule such as:

`{decision, checked_at, subject, resource, permission, consistency_mode}`

and mutation wrappers should separately expose their own effect identity/revision.

If the tool only returns `Access granted` or normal tool output after an internal check, the client can treat that as request-bound enforcement for that invocation but cannot later reconstruct or fence the authorization snapshot. Conversely, exposing `checked_at` without an effect-bound gate is audit/replay evidence, not mutation authority.

## Semantic barrier / continuation

A SHA-only note head check immediately before persistence still matched frozen `63e0f497bc9157c6c5075a8c615327dc49b8e76a`; no control/config identity revalidation was needed at that point.

Exact Phase-1 continuation:

1. Search for a genuine public/open-source `TRUE_EXTERNAL_REVISION_GATE`: an effect API whose mutation request accepts an authorization decision revision/epoch and atomically rejects if that authorization version is no longer valid. Keep resource-version CAS (ETag/SHA/generation) separate from authorization-version fencing.
2. Inspect additional production-oriented MCP authorization middleware (OPA/Envoy, Cedar/AVP-compatible OSS adapters, OpenFGA/Permify/Authzed integrations) for the two independent axes: request-bound effect enforcement and durable decision provenance.
3. Extend the classifier with a structured provenance-capsule validator and negative fixtures for `decision_id` or policy/bundle revision that is trace-only, not authorization-state/effect authority.
4. If no cross-system revision-gated effect is found after bounded official-source sampling, record that negative scope explicitly and elevate effect-local authorization as the recommended Chat pattern.
5. Resume the existing GitHub Rule Suite leaf only after these authorization/effect-binding probes, and only with safely-authorized exact reads.

Argus remains dormant while the Phase-1 overlay is active.
