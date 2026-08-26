# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0805JST.md`
Current invocation chain: `2026-08-27T0805JST.md` -> `2026-08-27T0703JST.md` -> `2026-08-27T0605JST.md` -> `2026-08-27T0503JST.md`
Previous checkpoint chain: `2026-08-27T0408JST.md` -> `2026-08-27T0305JST.md` -> `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md`
Earlier predecessor chain: `2026-08-27T0107JST-followup2.md` -> `2026-08-27T0033JST.md` -> `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T08:00:55+09:00`, checkpoint `2026-08-27T08:05:35+09:00`; chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Materialize pinned OPA and Regorus toolchains and run `rego_tier0_fixtures_v0.json` through OPA topdown, exact OPA Wasm, Regorus interpreter and Regorus RVM before any seeded generation.
3. Bind OPA-Wasm evidence to the exact emitted `policy.wasm` bytes, compiler identity, Wasm ABI and pinned runtime/SDK; preserve raw output plus canonical projection.
4. Reuse Regorus's matched interpreter/RVM adapter in run-to-completion/no-host-await mode and persist the serialized `Program` identity/digest.
5. Block seeded generation on any deterministic fixture mismatch; shrink only while preserving `reasoning.rego_tier0_generator.v0` support.
6. Recover/read Brown `https://git.sr.ht/~jakob/rego-proofs` and current VeriRego source through an allowed readable transport; until then keep thesis-backed and implementation-backed claims separate.
7. Only after Tier-0 executable calibration, add integers/comparisons as a separately versioned Tier-1 with explicit numeric-semantics calibration.
8. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and epsilon=0 gates. Deterministic provider pilot remains blocked and `epsilon>0` remains forbidden.

## Newest synthesis

- **C457:** serialized `rego_tier0_generator_v0.json` freezes the Tier-0 grammar, route-support predicates, canonical projection and support-preserving shrink rules before generated outcomes. Readback blob `e6d109206f6172038491ebbd8cc0e8a53d587b68`.
- **C458:** serialized `rego_tier0_fixtures_v0.json` freezes eight deterministic fixtures covering defined bool/string/null, undefined missing ref, local `:=`, equality and inequality. Readback blob `70192b610086742f25e8b3601698445b83acf135`.
- **C459:** OPA's documented Wasm path and official `@open-policy-agent/opa-wasm` SDK support loading raw `policy.wasm` bytes, setting data and evaluating input; this gives the exact-artifact adapter shape needed for the campaign.
- **C460:** Regorus's pinned RVM harness already compiles the same policy/entrypoint, checks Program serialization, executes run-to-completion with the same data/input and compares against the ordinary interpreter.
- **C461:** June 2026 VUT thesis materials independently corroborate VeriRego's Go implementation and source URL `https://github.com/VeriFIT/VeriRego`, but the current GitHub connector returns 404/no result; repository content remains unread. Brown SourceHut remains source-known but transport-blocked.
- **C263:** remains static-only; faithful runtime materialization is still unavailable here.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Run the frozen deterministic Tier-0 fixtures through pinned OPA/Regorus routes, persisting exact artifacts and raw/canonical outputs.
3. Only after deterministic route calibration passes, start seeded Tier-0 generation and support-preserving mismatch shrinking.
4. Recover Brown and VeriRego source through allowed readable transports; keep source-known/unread and thesis-only scopes explicit until readback.
5. Preserve every prior deterministic safety and measurement gate; `epsilon>0` remains forbidden.

`2026-08-27T0805JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.