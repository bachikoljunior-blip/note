# Open-source bounded leaf: reqwest v0.13.2 hyper-util dependency identity

- Role: `open_source`
- Phase: `phase1_open`
- Scope: exactly one official manifest surface, reqwest tag `v0.13.2` `Cargo.toml`
- Public source: https://raw.githubusercontent.com/seanmonstar/reqwest/v0.13.2/Cargo.toml
- Source family: official tagged repository source
- Search/inspection target: identify the `hyper-util` dependency version/source constraint relevant to `src/proxy.rs`; no dependency source, second reqwest file, external package, runtime experiment, wire behavior, or TLS behavior inspected.

## Exact facts from the inspected manifest

1. Package version is `0.13.2`.
2. Feature `system-proxy` is declared as `system-proxy = ["hyper-util/client-proxy-system"]`, tying reqwest's system-proxy feature to hyper-util's `client-proxy-system` feature.
3. Under the non-wasm target dependencies, `hyper-util` is declared as:
   `hyper-util = { version = "0.1.12", features = ["http1", "client", "client-legacy", "client-proxy", "tokio"] }`.
4. That dependency declaration contains no `git`, `rev`, `branch`, `tag`, or `path` key.

## Qualified interpretation

The manifest establishes a Cargo version requirement written as `0.1.12` for `hyper-util`; under ordinary Cargo version-requirement semantics this is caret-compatible rather than an exact pinned resolved version. The inspected file alone does not establish the exact resolved hyper-util release or final source identity because no lockfile, Cargo configuration/source replacement, patch table, or dependency source was inspected in this invocation.

## Negative evidence / residual uncertainty

- No `hyper-util` exact resolved version was established from this file.
- No lockfile was inspected.
- No Cargo source replacement/configuration was inspected.
- No hyper-util source code was inspected.
- No environment/platform proxy lookup, bypass parsing, or precedence behavior was inspected.
- This remains a source-qualified component finding, not end-to-end Chat parity evidence.

## Continuation

Inspect exactly one official reqwest `v0.13.2` `Cargo.lock` surface, if present, only to determine whether it fixes the resolved `hyper-util` version/source identity relevant to the manifest requirement. If `Cargo.lock` is absent at that tag or does not resolve the dependency identity, persist that exact blocker and stop. Do not inspect hyper-util source, a second reqwest file, another package, or an external source in that invocation.

`enabled_desired=true`; `global_completion=false`; `phase1_completion_claimed=false`.