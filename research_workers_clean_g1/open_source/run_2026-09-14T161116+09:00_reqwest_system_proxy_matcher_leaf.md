# Open-source bounded Phase-1 leaf — reqwest v0.13.2 system proxy matcher

- role: `open_source`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- bounded unit: inspect exactly one official implementation surface, `seanmonstar/reqwest` tag `v0.13.2`, `src/proxy.rs`
- source URL: https://github.com/seanmonstar/reqwest/blob/v0.13.2/src/proxy.rs
- source blob: `93a2459ae57b744382cf559311c0a33539b8df58`

## Frozen authority

- note main SHA h1: `ec621a125015f0551c55484fa98d7cebc37906b4`
- note main SHA h2: `ec621a125015f0551c55484fa98d7cebc37906b4`
- manifest: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`, blob `cd061848f602ed68d8416399be5d1f26f0d6a29d`, control revision 126
- lifecycle: `automation_control/RUN_LIFECYCLE.json`, blob `560024d46b6c26ea63ab58137be9d48863cab941`, control revision 3
- sanitized root: `automation_control/DESIRED_STATE.json`, blob `0eee15a94c23400653d84506da1f795081a6ef24`, control revision 27
- role config: `automation_control/roles/open_source.json`, blob `5a60eefd9ba1740088eb50e8df589aa7e6df590d`, control revision 14, config revision 7

## Exact finding

Within `src/proxy.rs`, reqwest's internal `Matcher::system()` constructs `Matcher_::Util(matcher::Matcher::from_system())`. Therefore this reqwest file delegates the actual system-proxy discovery/runtime semantics to `hyper_util::client::proxy::matcher::Matcher::from_system()` rather than implementing environment/platform proxy lookup itself.

The same file does define two relevant local semantics, but they do not resolve the delegated system matcher internals: (1) the public proxy documentation states that multiple explicit `Proxy` rules are checked in insertion order, so an earlier eager rule may shadow a later one; and (2) explicit non-system `Proxy` builders translate their optional reqwest `NoProxy` value into the hyper-util matcher builder's `.no(...)` input. This file does not establish which environment variables or platform settings `from_system()` consults, their precedence, or the system matcher's bypass parsing/precedence.

## Exact tested scope / negative knowledge

Verified only the official tagged `reqwest v0.13.2` file `src/proxy.rs` at blob `93a2459ae57b744382cf559311c0a33539b8df58`. No second reqwest file, dependency file, package manifest, external source, runtime experiment, wire behavior, TLS behavior, or end-to-end proxy interoperability was inspected in this invocation. In particular, `hyper-util`'s `Matcher::from_system()` implementation and the exact dependency revision used by reqwest v0.13.2 remain unresolved.

This is source-qualified component evidence, not end-to-end Chat parity evidence and not Phase-1 completion.

## Hard-gate assessment

- residual richer-mode/protected/manual-user execution dependency: 0 for this bounded inspection
- finite monthly/trial/paid quota dependency: 0
- incremental monetary cost: 0
- positive Phase-1 parity evidence: false
- scheduler mutation by worker: false
- enabled_desired: true
- global_completion: false
- phase1_completion_claimed: false

## Exact continuation

Next invocation: inspect exactly one official reqwest v0.13.2 manifest surface, `Cargo.toml`, only to identify the `hyper-util` dependency version/source constraint relevant to `src/proxy.rs`. If the exact path is absent or the dependency cannot be identified from that file, persist that exact blocker and stop. Do not inspect dependency source, a second file, another package, or an external source in that invocation.
