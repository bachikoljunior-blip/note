# Open-source bounded leaf: reqwest v0.13.2 system-proxy runtime application

- role: `open_source`
- phase: `phase_1_chat_parity`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- authority: manifest control 126/blob `cd061848f602ed68d8416399be5d1f26f0d6a29d`; RUN_LIFECYCLE control 3/blob `560024d46b6c26ea63ab58137be9d48863cab941`; DESIRED_STATE control 27/blob `0eee15a94c23400653d84506da1f795081a6ef24`; open_source control 14/config 7/blob `5a60eefd9ba1740088eb50e8df589aa7e6df590d`.
- frozen note main head before semantic work: `f2c590cfaa75e81b0040f93a8bfb46436cce28e4` (same on both SHA-only ref-object checks).

## Exact source inspected

Official reqwest v0.13.2 file only: `src/async_impl/client.rs`, blob `704943a04fc1ad66c5cb70adde7ae48440500484`.

Source URL: https://github.com/seanmonstar/reqwest/blob/v0.13.2/src/async_impl/client.rs

## Finding

Within this file, `ClientBuilder::new()` initializes `proxies` as empty and `auto_sys_proxy` as `true`. `ClientBuilder::build()` then appends `ProxyMatcher::system()` when `auto_sys_proxy` is true. Therefore the default builder path automatically installs the system-proxy matcher at build time.

The same file exposes explicit opt-outs: `ClientBuilder::no_proxy()` clears configured proxies and sets `auto_sys_proxy = false`; adding an explicit proxy through `ClientBuilder::proxy(...)` also sets `auto_sys_proxy = false`.

## Exact tested scope / limits

This leaf establishes only the builder/configuration path in this single official file. It does **not** establish the implementation of `ProxyMatcher::system()`, environment-variable or platform-store lookup rules, proxy precedence, per-request behavior, emitted wire bytes, TLS behavior, or end-to-end interoperability.

No O/O-derived state, downstream state, other-worker state/config/receipt, legacy research, shared ledger, or user/protected execution semantics were consumed.

## Phase-1 hard-gate assessment

- residual richer-mode/protected/manual-user execution dependency: `0` for this evidence slice
- finite monthly/trial/paid quota dependency: `0`
- incremental monetary cost: `0`
- strict Phase-1 pass: `false` — this is source-qualified component behavior, not proof of useful end-to-end Chat parity
- global completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler mutation by worker: `false`

## Exact continuation

Inspect exactly one official reqwest v0.13.2 implementation surface: `src/proxy.rs`. Determine only what `ProxyMatcher::system()`/the system-proxy matcher consults at runtime (for example environment or platform proxy configuration) and whether this file defines any precedence or bypass behavior relevant to the default builder-installed matcher. If the exact path is absent, persist that path-missing blocker and stop rather than searching alternate files. Do not inspect a second file, package, dependency, or external source in that invocation.
