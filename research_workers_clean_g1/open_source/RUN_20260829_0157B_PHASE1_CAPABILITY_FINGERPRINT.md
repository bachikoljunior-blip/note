# Open Source Phase-1 Amendment: Effective Capability Fingerprint

Frozen semantic tuple remains `note=91fdb502f413a8d9c660d339d04525aca5ce5100`, root control `20`, open_source config `6`, assignment `phase1-clean-open-source-chat-capability-patterns`.

## Artifact

Persisted `CAPABILITY_FINGERPRINT_20260829_0157.py`, a pure fail-closed checker that separates four facts which Chat tool integrations often collapse:

1. a platform may publicly support an operation;
2. the operation's tool may or may not be present in the **effective runtime enumeration** after toolset/read-only/denylist/target filters;
3. that enumeration may be stale if the registry can change without a reliable tool-change notification;
4. visible/callable surface does not by itself prove resource-specific authorization.

The checker deliberately scopes positive output to `PROVED_CALLABLE_FOR_TESTED_SCOPE`; it does not claim that mutation preconditions hold or that the effect will succeed.

## Precommitted controls / self-test result

All six local fixtures passed before persistence:

- GitHub-App-style visible tool with API-enforced permissions -> `AUTHORIZATION_UNPROVEN`
- classic-PAT scope-filter fail-open possibility -> `AUTHORIZATION_UNPROVEN`
- Kubernetes MCP dynamic registry + stateless/no notification + cached list -> `STALE_CAPABILITY_UNKNOWN`
- fresh effective enumeration with desired tool absent -> `SURFACE_MISSING` scoped only to the tested runtime surface
- fresh tool + resource/operation-bound safe authorization evidence positive -> `PROVED_CALLABLE_FOR_TESTED_SCOPE`
- same bound evidence negative -> `AUTHORIZATION_DENIED`

## Public mechanism evidence

GitHub MCP Server at public commit `febc3293a4feb70e62399f39a26b082f78b9b176` documents that read-only mode removes write tools even if requested, excluded tools override enabled toolsets, lockdown is not an authorization boundary, classic PAT scope detection filters tool visibility, scope-detection failure continues without filtering, and fine-grained PAT/GitHub App/server tokens expose tools while the API enforces permissions.

- https://github.com/github/github-mcp-server/blob/febc3293a4feb70e62399f39a26b082f78b9b176/docs/server-configuration.md
- https://github.com/github/github-mcp-server/blob/febc3293a4feb70e62399f39a26b082f78b9b176/docs/scope-filtering.md

Kubernetes MCP Server at public commit `4568a4fa6668e9af9df0d5fd8366f3859a7961e5` documents `read_only`, destructive filtering, allowlist then denylist filtering, optional target-compatibility filtering, SIGHUP registry rebuild, and `stateless=true` disabling tool/prompt change notifications.

- https://github.com/containers/kubernetes-mcp-server/blob/4568a4fa6668e9af9df0d5fd8366f3859a7961e5/docs/configuration.md

The resulting counterexample is concrete: a client can have a once-valid cached tools list, the server can rebuild its registry after configuration reload, and stateless mode can suppress the notification that would invalidate the cache. Therefore a safe mutation path needs a pre-action effective re-enumeration rule whenever registry mutability is possible and notification freshness is not guaranteed.

## Exact continuation

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant. Next: (1) find or falsify an end-to-end live required-workflow provenance path from ruleset source tuple to exact target run; (2) extend the fingerprint with a safe notion of authorization evidence that never requires a noop mutation, using server/API permission metadata or read-only preflight where available; (3) audit a third official MCP/tool server for whether capability-change notification semantics are discoverable or only operator-configured; (4) keep a nonempty Phase-1 frontier.
