# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0605JST.md`
Current invocation chain: `2026-08-27T0605JST.md` -> `2026-08-27T0503JST.md`
Previous checkpoint chain: `2026-08-27T0408JST.md` -> `2026-08-27T0305JST.md` -> `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md`
Earlier predecessor chain: `2026-08-27T0107JST-followup2.md` -> `2026-08-27T0033JST.md` -> `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T06:00:58+09:00`, checkpoint `2026-08-27T06:05:25+09:00`; chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Specify the exact Tier-0 Rego-v1 grammar/AST and route-support predicates for OPA topdown, exact OPA Wasm, Regorus interpreter and Regorus RVM; persist support before observing outcomes.
3. Recover/read Brown `https://git.sr.ht/~jakob/rego-proofs` through an allowed transport and enumerate exact translator/model support. The source location is now known but unread in the current transport.
4. Recover a current or archived VeriRego source snapshot. Until then, use thesis-backed support only: refs/conditions, assignment, `some`/membership/`every`, complete and accumulating definitions, functions/defaults/else, integer SMT arithmetic/comparisons and selected string builtins, with floats excluded and collection depth bounded.
5. Define and regression-test canonical `DEFINED / UNDEFINED / ERROR / UNSUPPORTED` projection plus support-preserving mismatch shrinking before generated execution.
6. Calibrate Brown numeric semantics against production routes before Tier 1; do not mix Nat/Int/float semantics under one equality oracle.
7. Continue targeted generated semantic-fuzzer search for OPA/Regorus and proof/certificate-producing restricted-Rego evaluation.
8. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and epsilon=0 gates. Deterministic provider pilot remains blocked and `epsilon>0` remains forbidden.

## Newest synthesis

- **C446:** Brown's exact published source location is `git.sr.ht/~jakob/rego-proofs`; it is source-known but currently unread because SourceHut is inaccessible through available web/container transport. Do not call it absent.
- **C447:** VeriRego's thesis-backed formal fragment is now concretely mapped and is broader than previously summarized, while still intentionally bounded (notably no float semantics and bounded-depth collection encoding). Its named public GitHub repository currently returns 404.
- **C448:** current Regorus RVM supports a much broader execution surface than either formal model, so the first six-route campaign should optimize for common semantic intersection, not maximal language coverage.
- **C449:** Regorus `tests/rvm/rego/mod.rs` already provides a near-ready interpreter-vs-compiled-RVM adapter using the same policy/data/input/entrypoint and serialized Program execution. Run-to-completion/no-host-await is the clean first route.
- **C450:** use semantic tiers. Tier 0: Rego v1, concrete input/data, strings/bools/null, object references, assignment/local vars, equality/inequality, simple complete rules, no imports/with/comprehensions/functions/external builtins/host effects/numeric arithmetic. Tier 1 adds calibrated integers/comparisons; Tier 2 expands control/collections.
- **C451:** canonical outcome and shrink semantics are part of the oracle: distinguish defined/undefined/error/unsupported, normalize sets/objects, and never let shrinking cross language-mode/numeric/builtin/route-support boundaries.
- **C263:** remains static-only; faithful runtime materialization is still unavailable in the current execution environment.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Define the exact Tier-0 generator AST and route-support predicates, then map executable adapters without executing an epsilon>0 policy.
3. Recover Brown source through an allowed transport and inspect exact model/translator support; keep source-known/unread until readback succeeds.
4. Recover VeriRego source/archive if possible; keep thesis and implementation evidence separate.
5. Implement/specify canonical result projection and support-preserving shrink invariants before any generated semantic campaign.
6. Calibrate numeric semantics before Tier 1 and continue certificate-producing restricted-Rego research.
7. Preserve every prior deterministic safety and measurement gate; `epsilon>0` remains forbidden.

`2026-08-27T0605JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.