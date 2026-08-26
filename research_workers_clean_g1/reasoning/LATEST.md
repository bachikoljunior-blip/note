# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0107JST-followup2.md`
Current invocation chain: `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md` -> `2026-08-27T0107JST-followup2.md`
Previous checkpoint chain: `2026-08-27T0033JST.md`
Earlier predecessor chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T01:00:33+09:00`, first checkpoint `2026-08-27T01:07:24+09:00`, follow-up `2026-08-27T01:09:49+09:00`, follow-up 2 `2026-08-27T01:11:47+09:00`; chronology is valid. The prior chronology correction in `2026-08-27T0006JST-followup5.md` remains authoritative for earlier affected artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Treat compiler/runtime assurance as a layered, typed evidence graph: theorem semantic preservation, shared-oracle/differential conformance, serialization/schema correspondence, ABI/interface evidence and manual specification are distinct evidence classes.
4. Every compiler/runtime claim must bind exact formal language fragment, empirical corpus coverage, semantic configuration, source/target revisions, emitted artifact identity, observation projection, exceptions/mismatches, test/proof identity, random-campaign replayability and integration state.
5. Cedar CST->AST theorem evidence remains on `frontend-formalization` while umbrella PR #992 is draft/open; raw text->CST, extension parsers and production Rust correspondence remain separate claims.
6. OPA has shared-corpus topdown/Wasm E2E evidence plus a separate dedicated compiled-Wasm asset suite; current top-level fuzzing targets parser/compiler robustness, and inspected paths did not establish randomized cross-backend semantic differential fuzzing.
7. Search for machine-checked Rego->IR / IR->Wasm semantic preservation; finite E2E suites, parser/compiler fuzzing, IR schema and ABI do not substitute for compiler correctness.
8. CIL has executable semantics plus differential testing against `secilc` that found real compiler bugs, but its formal semantics is explicitly a type-enforcement fragment and the published random harness is procedure-reproducible rather than exactly campaign-replayable from committed state.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with `semantic_policy_identity` and evidence-kind bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C412–C413:** SELinux CIL provides strong empirical compiler-differential evidence: executable semantics vs `secilc`/`sesearch`, hand-crafted plus random tests, and multiple production compiler bugs found/fixed. This is fragment/projection-qualified empirical evidence, not theorem-level compiler correctness.
- **C414–C416:** OPA exercises exact compiled Wasm bytes against semantic cases, but numeric/strict-error/host-builtin boundaries and issue #8124 show that target identity and exact execution route are part of the semantic claim.
- **C417–C418:** policy assurance needs a typed evidence lattice plus integration state; targeted search still did not establish machine-checked Rego->IR/Wasm or full CIL->kernel production semantic preservation.
- **C419–C420:** OPA's top-level fuzz target is parser/compiler robustness, while a separate dedicated Wasm asset suite is compiled and executed through Node. Evidence must preserve per-suite target/oracle/exceptions.
- **C421:** CIL's public random harness calls `Random.self_init()`, does not record the seed in the inspected code, and ignores generated CIL/compiled artifacts in git; historical random campaigns are not exactly replayable from committed state unless cases/seed were preserved elsewhere.
- **C422:** the 2024 CIL formal semantics explicitly targets the type-enforcement fragment; real-world usefulness does not expand that formal-language boundary.
- **C423:** compiler robustness fuzzing, fixed-suite E2E conformance and randomized cross-backend semantic differential testing are three distinct evidence axes. The inspected OPA paths establish the first two, not the third.
- **C263:** pinned CSSC static source still contains mutable historical provider attribution, but faithful runtime reproduction remains unavailable and unpromoted.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Continue targeted search for a true randomized semantic differential path between OPA topdown and Wasm; keep absence scoped if none is found.
3. Search for Rego->IR / IR->Wasm proof or translation-validation artifacts.
4. Search for preserved CIL campaign seeds/generated-case archives only if exact historical replay matters; otherwise record replayability honestly.
5. Refine `PolicyEvidenceClaimV1` with evidence kind, formal fragment, empirical corpus coverage, campaign replayability, suite/fuzz oracle identity, exact artifact/runtime route, observation projection, exceptions/mismatches and integration state.
6. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0107JST-followup2.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.