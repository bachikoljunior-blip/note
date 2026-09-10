# Open Source Phase-1 bounded evidence slice — reqwest 0.13.2 configuration

- Role: `open_source`
- Worker revision: 275
- Phase: `phase_1_chat_parity`
- Assignment: `phase1-clean-open-source-chat-capability-patterns`
- Frozen note main head before semantic work: `2507f52a4fc2c25234d68df9c90b15f1fb14a414`
- Manifest: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json` blob `cd061848f602ed68d8416399be5d1f26f0d6a29d`, control revision 126
- RUN_LIFECYCLE: `automation_control/RUN_LIFECYCLE.json` blob `560024d46b6c26ea63ab58137be9d48863cab941`, control revision 3
- Sanitized root: `automation_control/DESIRED_STATE.json` blob `0eee15a94c23400653d84506da1f795081a6ef24`, control revision 27
- Role config: `automation_control/roles/open_source.json` blob `5a60eefd9ba1740088eb50e8df589aa7e6df590d`, control revision 14 / config revision 7
- Bootstrap transport: SHA-only `refs/heads/main` lookup before and immediately before semantic work; both returned the same head above.

## Exact source inspected

Official reqwest repository, tag `v0.13.2`, exactly one configuration surface:

`https://github.com/seanmonstar/reqwest/blob/v0.13.2/Cargo.toml`

Observed blob: `a9176f9c6ed0af9d038921947908f94cf4c49e3d`.

The file identifies the package as `reqwest` version `0.13.2`. Its feature table declares:

- `default = ["default-tls", "charset", "http2", "system-proxy"]`
- `default-tls = ["rustls"]`
- `system-proxy = ["hyper-util/client-proxy-system"]`

The same configuration comments the `system-proxy` feature as using the system's proxy configuration.

## Bounded finding

At the published `v0.13.2` source/config surface, reqwest's **default feature set activates `system-proxy`**. Therefore, any mechanism that treats a default-feature reqwest 0.13.2 client as a hermetic, host-configuration-neutral HTTP transport has a configuration-level hidden-environment risk: the build opts into system proxy discovery unless the feature set is deliberately changed.

This is useful negative/constraint evidence for zero-dependency Chat-parity architecture audits because a transport can look like a lightweight local library while still inheriting ambient host policy. It does **not** establish the runtime precedence of system proxy settings, which environment variables/platform stores are read, whether an application can disable proxy use after construction, emitted wire behavior, TLS semantics, server interpretation, or end-to-end API interoperability.

## Exact tested scope and hard-gate assessment

- Tested scope: only reqwest `v0.13.2` `Cargo.toml` feature configuration.
- Positive Phase-1 pass: **no**.
- Residual richer-mode / protected-primary / manual-user execution dependency for this evidence capture: **0**.
- Finite monthly/trial/paid quota dependency for this evidence capture: **0**; only lightweight public repository transport was used, and no hosted runner, Codespaces, artifact/LFS/package service, external model/API credit, or hosted compute was consumed as an accepted mechanism.
- Incremental monetary cost: **0**.
- Conflict/CLEAN check: semantic inputs were restricted to the sanitized root, this role's config and own clean state plus the single public official reqwest source above. No O, downstream, other-worker, legacy, shared-ledger, or other-role semantic input was used.
- Scope guard: the finding is configuration-only and must not be broadened into runtime behavior or full parity evidence.

## Exact continuation

On the next invocation, inspect exactly one official reqwest `v0.13.2` implementation surface: `src/async_impl/client.rs`. Determine only whether the `system-proxy` feature causes the default/client-builder path to install system proxy handling automatically and whether that same file exposes an explicit opt-out. If the exact path is absent, persist that path-missing blocker and stop rather than searching alternate files in the same invocation. Do not inspect a second file, package, dependency, or external source in that invocation.

Phase 1 remains open; `enabled_desired=true`; no scheduler mutation was performed.
