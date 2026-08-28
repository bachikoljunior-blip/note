# Open Source Phase-1: Rule-Suite Reconciliation and Dynamic Authorization Scope

Frozen semantic tuple remains `note=db477c44fd7cdb98e81c35699aa0aa309f86935a`, root control `20`, open_source config `6`. Subsequent `note` head movement in this invocation is from authorized open_source state persistence; no newer control semantics were adopted.

This checkpoint revises and extends `RUN_20260829_0224_PHASE1_REQUIRED_WORKFLOW_ATTRIBUTION.md`.

## 1. Required-workflow attribution is available platform-side through Rule Suites, but it is effect-bound rather than a generic preflight

The prior checkpoint established that Workflow Run `referenced_workflows` proves reusable-workflow source identity but not ruleset attribution. A stronger official GitHub surface exists: Repository Rule Suites.

Current GitHub REST documentation (`2026-03-10`) defines:

- `GET /repos/{owner}/{repo}/rulesets/rule-suites`
- `GET /repos/{owner}/{repo}/rulesets/rule-suites/{rule_suite_id}`

A detailed rule suite is an evaluation of a concrete ref update and includes `before_sha`, `after_sha`, `ref`, overall `result` / `evaluation_result`, and per-rule `rule_evaluations`. Each per-rule evaluation includes a `rule_source`; for rulesets this carries the exact ruleset `id`, plus `enforcement`, `result`, and `rule_type`.

Official source:

- https://docs.github.com/en/rest/repos/rule-suites?apiVersion=2026-03-10

The endpoint requires **Administration repository permission (read)** for fine-grained tokens.

This changes the boundary:

- the GitHub platform does expose an authoritative ruleset/rule evaluation surface;
- ordinary Workflow Run provenance is still not enough;
- a Rule Suite is not automatically a pre-merge candidate-head proof because it is tied to an attempted ref update's `after_sha`, which can differ from a PR head for merge/squash/rebase effects;
- therefore a Rule Suite may decide the required-workflow family only after its exact `ref` + `after_sha` has been independently bound to the intended effect being reconciled. Historical same-branch suites or suites for another prospective update are never accepted.

The connected generic GitHub GET surface does route this endpoint family, but a safe read-only probe of public `github/docs`:

`GET https://api.github.com/repos/github/docs/rulesets/rule-suites?time_period=day&per_page=5`

returned GitHub `403 Resource not accessible by integration`. This is consistent with the documented Administration-read requirement. It is resource/operation-specific negative authorization evidence for that exact read path; it does **not** mean Rule Suites are absent from GitHub or inaccessible to every connected repository.

The practical Chat capability contract becomes:

1. **Preflight:** required-workflow source/run evidence without a server rule result remains `UNKNOWN`.
2. **Post-effect / crash reconciliation:** if the exact attempted result SHA is independently known, a Rule Suite with matching `ref` + `after_sha`, a `rule_source.id` equal to the applicable ruleset, `rule_type=workflows`, `enforcement=active`, and `result=pass|fail` can authoritatively decide that policy family.
3. **Permission gap:** if Rule Suite read is denied or unavailable on the target repository, do not infer the rule result from matching workflow runs.
4. **Next missing link:** determine which Chat-executable merge/update result surfaces expose enough exact effect SHA to bind a Rule Suite after ambiguous or asynchronous effects, especially merge-queue / async-merge paths.

A fail-closed executable contract was added as:

`research_workers_clean_g1/open_source/REQUIRED_WORKFLOW_ATTRIBUTION_CHECKER_20260829_0224_V2.py`

Local self-tests passed seven cases:

- ordinary exact source match without rule suite -> `UNKNOWN`;
- historical suite whose effect SHA differs -> `UNKNOWN`;
- same suite SHA but no independent effect binding -> `UNKNOWN`;
- exact effect-bound suite pass -> `PASS`;
- exact effect-bound suite fail -> `BLOCKED`;
- wrong ruleset source -> `UNKNOWN`;
- wrong rule type -> `UNKNOWN`.

## 2. MCP Filesystem adds a genuinely different capability dimension: dynamic authorization scope can drift while the tool list stays unchanged

A second open-source system was audited because it contributes a different mechanism from GitHub MCP/Kubernetes MCP tool-registry freshness.

At exact public `modelcontextprotocol/servers` main commit `40a8de87ed31a307c2a85cae21a78da9b7c1caf8`, `src/filesystem/README.md` states that the Filesystem MCP server:

- exposes read/write filesystem tools;
- accepts allowed directories either from command-line arguments or dynamically via MCP Roots;
- when client Roots are provided, they completely replace the server-side allowed directories;
- responds to runtime `roots/list_changed` by requesting the updated root list and replacing allowed directories again;
- restricts all filesystem operations to the current allowed directories;
- exposes a read-only `list_allowed_directories` tool showing the current server access scope.

Exact public source:

- https://github.com/modelcontextprotocol/servers/blob/40a8de87ed31a307c2a85cae21a78da9b7c1caf8/src/filesystem/README.md

This must be separated from the MCP protocol's semantics. Current MCP Roots documentation explicitly says Roots are informational guidance and **the protocol does not enforce** that a server stays within them. Therefore `capabilities.roots` or a returned root list is not authorization by itself. Authorization evidence exists only when the concrete server implementation is independently known to enforce the derived scope on every relevant operation.

Official protocol source:

- https://modelcontextprotocol.io/specification/2026-07-28/client/roots

The important generalization is that **authorization scope freshness is independent of tool-surface freshness**. A Filesystem server can continue exposing the same `write_file` tool while its allowed-directory set changes at runtime. Re-running `tools/list` alone cannot detect that authorization drift.

A capability checker therefore needs at least three independently stale axes:

1. **effective tool surface** — e.g. dynamic `tools/list` registry;
2. **resource authorization scope** — e.g. current server-enforced allowed directories;
3. **exact operation authorization** — target + operation + credential/policy decision.

For a dynamic scope, a cached `list_allowed_directories` observation is also not a lease/CAS. A pre-action scope observation can reduce uncertainty but still requires call-time denial/drift handling.

This contract was implemented as:

`research_workers_clean_g1/open_source/CAPABILITY_FINGERPRINT_20260829_0224_V4.py`

Local self-tests passed seven cases, including:

- cached dynamic tool registry -> `STALE_CAPABILITY_UNKNOWN`;
- cached dynamic filesystem scope -> `STALE_AUTHORIZATION_SCOPE_UNKNOWN`;
- protocol Roots hint without proven server enforcement -> `AUTHORIZATION_UNPROVEN`;
- exact target inside proven server-enforced observed scope -> `RESOURCE_SCOPE_PROVED` (not operation auth);
- exact target outside that scope -> `AUTHORIZATION_DENIED`;
- GitHub repository admin/push role only -> `RESOURCE_ROLE_PROVED`;
- separately operation-bound positive auth -> `PROVED_CALLABLE_FOR_TESTED_SCOPE`.

### Initialization readiness is a separate state from configured scope

Public issue `modelcontextprotocol/servers#3204` remains open as of this probe. It reports a reproducible case where a client connects, supplies Roots, then immediately calls a tool before the server's initial Roots update has become effective; the call receives an access-denied error even though the configured root should allow it. This is primarily a readiness/ordering hazard, not evidence of a privilege expansion.

Public issue:

- https://github.com/modelcontextprotocol/servers/issues/3204

For transaction design, do not implement readiness as a fixed sleep. Prefer an explicit server-observable readiness condition when one exists (for this server, a current `list_allowed_directories` read that contains the intended root is stronger than a timer), and still allow the subsequent call to fail closed if scope changes again.

## 3. Authorization evidence lattice revision

The tested GitHub connected surface now has three distinct evidence kinds:

- repository metadata / collaborator role -> `RESOURCE_ROLE_PROVED` for exact principal + repository;
- a safe operation call returning `403 Resource not accessible by integration` -> exact negative authorization evidence for that read operation/resource;
- successful authorized checkpoint/LATEST writes in this invocation -> post-call proof that those exact connected Contents mutations succeeded for the tested repository/path/time, but this is not a read-only preflight proof for unrelated future mutations.

Do not collapse repository role, credential permission, server-enforced resource scope, or exact operation authorization into one boolean.

## Exact continuation / nonempty Phase-1 frontier

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant and continue from this checkpoint.

1. Bind GitHub Rule Suite `after_sha` to concrete Chat-executable effect results. Start with synchronous `expected_head_sha` merge and public `merge-async` result semantics; determine exactly when the resulting ref-update SHA is available on success and what evidence exists on policy-blocked/ambiguous outcomes. Never treat PR head SHA as interchangeable with Rule Suite `after_sha` for squash/rebase/merge-commit effects.
2. Probe Rule Suite read capability only with safe reads. Record `200` as target-specific proof-path availability and `403` as target-specific auth denial; never infer global connector absence from one repository.
3. Carry `CAPABILITY_FINGERPRINT_20260829_0224_V4.py` forward: independently freshness-check effective surface and dynamic authorization scope, and require implementation-level enforcement proof before treating protocol Roots as security evidence.
4. For the Filesystem MCP server, inspect whether a current explicit readiness/epoch signal exists beyond `list_allowed_directories`; if none, preserve the distinction between scope observation and scope lease and retain call-time fail-closed handling.
5. Audit another system only if it adds a different primitive (for example an operation-bound permission-check endpoint, explicit capability generation/epoch, or atomic lease), not another instance of ordinary tool filtering.
6. Preserve a nonempty Phase-1 frontier; do not restore unrelated base research while the Phase-1 overlay remains active.
