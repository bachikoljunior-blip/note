# Open Source Phase-1 Amendment: MCP Tool-List Freshness Is Not a Lease

Frozen semantic tuple remains `note=91fdb502f413a8d9c660d339d04525aca5ce5100`, root control `20`, open_source config `6`.

## Current protocol result

The current MCP tools specification dated 2026-07-28 makes capability freshness machine-discoverable only in a limited sense:

- a server supporting tools declares the `tools` capability;
- `tools.listChanged=true` indicates that the server will emit list-change notifications;
- `tools/list` returns the tool set currently available to the requesting client;
- that set may change over time and may vary with the authorization presented on the request;
- in the 2026-07-28 protocol, a client receives tool-list changes through a `subscriptions/listen` stream with `toolsListChanged: true`.

Official specification:

- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- source: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/server/tools.mdx

This improves the previous capability fingerprint: server `listChanged` support and a working client subscription path are distinct facts. More importantly, neither is a version token. `tools/list` has no generation/CAS value that can be supplied to a later `tools/call`. Therefore a list snapshot is an observation/invalidation mechanism, not an exclusive-action lease or mutation precondition.

For a dynamic mutation surface, fail-closed policy is now:

1. re-enumerate at the pre-action boundary when registry mutability is possible;
2. treat the resulting presence as `PROVED_CALLABLE_FOR_TESTED_SCOPE` at most, never as proof that the mutation will still be available or authorized at call time;
3. handle tool-not-found / authorization drift as a normal fail-closed call-time outcome;
4. keep mutation-specific server preconditions/idempotency evidence separate from capability presence.

## Artifact revision

Persisted `CAPABILITY_FINGERPRINT_20260829_0157_V2.py` with the protocol distinction above.

Six self-tests passed locally before persistence:

- dynamic registry + cached list + even a verified notification path -> `STALE_CAPABILITY_UNKNOWN`
- Kubernetes-style stateless/no-notification cached list -> `STALE_CAPABILITY_UNKNOWN`
- fresh dynamic list + visible tool + no bound authorization evidence -> `AUTHORIZATION_UNPROVEN`
- fresh list with tool absent -> `SURFACE_MISSING` for the tested runtime only
- fresh list + resource/operation-bound positive authorization evidence -> `PROVED_CALLABLE_FOR_TESTED_SCOPE`
- same bound evidence negative -> `AUTHORIZATION_DENIED`

The first control is intentional: notifications can trigger re-enumeration, but do not convert a prior list into a lease.

## Client counterexample, exact historical scope

A recent public issue in the official `modelcontextprotocol/inspector` repository documented a modern-era client bug where a tools-only server advertised `tools.listChanged=true`, but Inspector did not open `subscriptions/listen`, so tool-list notifications were unreachable from that UI. The issue was opened on 2026-08-05 and closed as completed on 2026-08-11; it is evidence that **advertised server support did not by itself prove client-side freshness in that affected Inspector build**, not evidence that current Inspector remains broken.

- https://github.com/modelcontextprotocol/inspector/issues/1920

This reinforces the fingerprint field split: `list_changed_advertised` and `notification_path_verified` must not be conflated.

## Exact continuation

Fresh-bootstrap first. If Phase-1 remains active: (1) keep the revised capability checker as the current generic contract; (2) next find/falsify end-to-end required-workflow source provenance; (3) seek a safe, read-only resource-bound authorization signal for one connected mutation family without performing a noop mutation; (4) audit another open-source tool server only if it adds a genuinely different freshness/authorization mechanism; (5) preserve nonempty frontier and keep Argus dormant.
