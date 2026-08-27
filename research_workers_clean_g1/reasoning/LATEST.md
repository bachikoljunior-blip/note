# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0904JST.md`
Current invocation chain: `2026-08-27T0904JST.md` -> `2026-08-27T0805JST.md` -> `2026-08-27T0703JST.md` -> `2026-08-27T0605JST.md` -> `2026-08-27T0503JST.md`
Previous checkpoint chain: `2026-08-27T0408JST.md` -> `2026-08-27T0305JST.md` -> `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md`
Earlier predecessor chain: `2026-08-27T0107JST-followup2.md` -> `2026-08-27T0033JST.md` -> `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T08:58:36+09:00`, checkpoint `2026-08-27T09:04:22+09:00`; chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Recover the exact older CSSC commit bound to C263 and execute the full two-node same-batch no-op path through `StructuredController`; current-main helper runtime evidence does not by itself close C263.
2. Regression-test an immutable attribution design where provider cost events remain unchanged and two same-batch consumers produce two append-only consumption edges.
3. Materialize pinned OPA and Regorus toolchains and run `rego_tier0_fixtures_v0.json` through OPA topdown, exact OPA Wasm, Regorus interpreter and Regorus RVM before any seeded generation.
4. Bind OPA-Wasm evidence to exact emitted `policy.wasm` bytes, compiler identity, Wasm ABI and pinned runtime/SDK; preserve raw output plus canonical projection.
5. Reuse Regorus's matched interpreter/RVM adapter in run-to-completion/no-host-await mode and persist serialized `Program` identity/digest.
6. Block seeded generation on any deterministic fixture mismatch; shrink only while preserving `reasoning.rego_tier0_generator.v0` support.
7. Recover/read Brown `https://git.sr.ht/~jakob/rego-proofs` and current VeriRego source through an allowed readable transport; until then keep thesis-backed and implementation-backed claims separate.
8. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and epsilon=0 gates. Deterministic provider pilot remains blocked and `epsilon>0` remains forbidden.

## Newest synthesis

- **C462:** at current public CSSC main `f40a3d3aa3054f4b07bb17e3fe5aa6d55e3d28f8`, the exact `attribute_proposal_batch` helper was executed under matching immutable-ledger replacement semantics. One batch consumed by `node-1` then `node-2` changed all historical matching event `action_id`s from null -> node-1 -> node-2. Durable runtime evidence: `cssc_cost_attribution_microrepro_f40a3d3.json`, blob `d7e2e23852cb87cca1a193fa9031aafccc67e4bc`.
- **C463:** current action execution calls attribution before structured action dispatch, while current `REFINE_ARGUMENT` reducer semantics include deterministic no-op paths when refined IDs hit nothing. This keeps the full two-consumer reachability concern live, but the complete controller path was not executed here.
- **C464:** deterministic Rego Tier-0 execution remains blocked by toolchain materialization: the container has Python/Go/Node but no `opa` or Rust/Cargo, GitHub DNS is unavailable from the container, and the available binary-download path did not yield an executable. No route result was fabricated.
- **C263:** remains pending as an exact older-pin end-to-end runtime reproduction; current-main helper runtime evidence is intentionally scoped separately.

## Exact continuation

1. Recover and run C263 unchanged at its exact older pin; keep helper-level and end-to-end evidence distinct.
2. Build/test the append-only `proposal_batch -> consumer` edge oracle against the demonstrated current-main overwrite behavior.
3. Run the frozen deterministic Tier-0 fixtures through pinned OPA/Regorus routes with exact artifact identities; only then permit seeded generation.
4. Recover Brown and VeriRego source through allowed readable transports; keep source-known/unread and thesis-only scopes explicit until readback.
5. Preserve every prior deterministic safety and measurement gate; `epsilon>0` remains forbidden.

`2026-08-27T0904JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.