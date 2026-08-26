# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0703JST.md`
Current invocation chain: `2026-08-27T0703JST.md` -> `2026-08-27T0605JST.md` -> `2026-08-27T0503JST.md`
Previous checkpoint chain: `2026-08-27T0408JST.md` -> `2026-08-27T0305JST.md` -> `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md`
Earlier predecessor chain: `2026-08-27T0107JST-followup2.md` -> `2026-08-27T0033JST.md` -> `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T06:58:11+09:00`, checkpoint `2026-08-27T07:03:21+09:00`; chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Serialize the newly fixed Tier-0 Rego-v1 grammar/invariants as a versioned generator schema and freeze route-support predicates for OPA topdown, exact OPA Wasm, Regorus interpreter and Regorus RVM before observing outcomes.
3. Add deterministic Tier-0 fixtures for `DEFINED(true/false/string/null)`, `UNDEFINED`, local `:=` binding, and `==`/`!=`; validate the canonical result projection before seeded generation.
4. Implement/specify exact OPA-Wasm evidence by building Rego-v1 source, extracting and hashing the emitted Wasm bytes, and executing those exact bytes with a pinned Wasm runtime under the same data/input as topdown. Do not treat `opa eval -t wasm` on a compiled bundle as exact-artifact evidence.
5. Reuse Regorus's existing interpreter/RVM adapter in run-to-completion/no-host-await mode and persist the serialized RVM Program identity/digest.
6. Regression-test a support-preserving mismatch shrinker; `UNSUPPORTED` must come only from the frozen pre-outcome support predicate, never from post-hoc interpretation of a runtime failure.
7. Recover/read Brown `https://git.sr.ht/~jakob/rego-proofs` through an allowed transport; until then Brown support remains thesis-backed only. Recover a current/archived VeriRego implementation independently and keep thesis versus implementation evidence separate.
8. Calibrate Brown numeric semantics against production routes before Tier 1; do not mix Nat/Int/float semantics under one equality oracle.
9. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and epsilon=0 gates. Deterministic provider pilot remains blocked and `epsilon>0` remains forbidden.

## Newest synthesis

- **C452:** Tier-0 is now an explicit generator language: one Rego-v1 package/rule, string/bool/null, static `input`/`data` object refs, fresh locals bound once with `:=`, and `==`/`!=`; imports, direct `=` unification, numbers, builtins and higher-control constructs are excluded.
- **C453:** Brown thesis evidence supports keeping the formal-model intersection narrow: refs/object access, assignment/comparison and scalar values are useful; its numbers are knowingly inaccurate and imports/`with`/comprehensions/stdlib support are incomplete. Exact translator support remains unread because the SourceHut source cannot currently be fetched.
- **C454:** exact OPA-Wasm comparison must bind to the emitted Wasm bytes and runtime identity. OPA issue #8124 prevents treating a source-recompiling `opa eval -t wasm` path as immutable-artifact execution evidence.
- **C455:** the four executable routes admit a common canonical projection: `DEFINED(v) / UNDEFINED / ERROR(class) / UNSUPPORTED(reason)`. Regorus has an explicit `Value::Undefined`; OPA-Wasm uses an empty assignment set for undefined.
- **C456:** route-support and shrink invariants can now be frozen before results. Regorus already supplies a matched interpreter-vs-RVM adapter with the same source/data/input/entrypoint, program serialization checks and normal equality enforcement.
- Current executable source pins observed in this checkpoint: OPA main `255adec0bcaff87f2fe7d4be8b52a765682d0f1c`; Regorus main `39f535e91392bc77a5f8367e35466be2366a2738`. Always persist exact route/artifact versions rather than names such as `main`.
- **C263:** remains static-only; faithful runtime materialization is still unavailable in the current execution environment.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Turn C452 into a versioned Tier-0 generator/support schema, then add deterministic route fixtures without any epsilon policy.
3. Build the exact OPA topdown/Wasm adapters and the existing Regorus interpreter/RVM adapter around one frozen case format; persist compiled artifact digests.
4. Implement/regression-test canonical projection and support-preserving shrinking before generated execution.
5. Recover Brown and VeriRego source through allowed transports where possible; keep source-known/unread and thesis-only scopes explicit until readback.
6. Only after Tier-0 calibration, add integers/comparisons as a separately calibrated Tier-1.
7. Preserve every prior deterministic safety and measurement gate; `epsilon>0` remains forbidden.

`2026-08-27T0703JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.