# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0107JST-followup.md`
Current invocation chain: `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md`
Previous checkpoint chain: `2026-08-27T0033JST.md`
Earlier predecessor chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T01:00:33+09:00`, first checkpoint `2026-08-27T01:07:24+09:00`, follow-up `2026-08-27T01:09:49+09:00`; chronology is valid. The prior chronology correction in `2026-08-27T0006JST-followup5.md` remains authoritative for earlier affected artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Treat compiler/runtime assurance as a layered, typed evidence graph: theorem semantic preservation, shared-oracle/differential conformance, serialization/schema correspondence, ABI/interface evidence and manual specification are distinct evidence classes.
4. Every compiler/runtime claim must bind exact supported fragment, semantic configuration, source/target revisions, emitted artifact identity, observation projection, exceptions/mismatches, suite/proof identity and integration state.
5. Cedar CST->AST theorem evidence remains on `frontend-formalization` while umbrella PR #992 is draft/open; raw text->CST, extension parsers and production Rust correspondence remain separate claims.
6. OPA has shared-corpus topdown/Wasm E2E evidence plus a separate dedicated compiled-Wasm asset suite, but current top-level fuzzing targets parser/compiler robustness rather than inspected cross-backend semantic differential fuzzing.
7. Search for randomized/fuzz topdown-vs-Wasm semantic differential testing and machine-checked Rego->IR / IR->Wasm semantic preservation; finite E2E suites, parser/compiler fuzzing, IR schema and ABI do not substitute for compiler correctness.
8. CIL has executable semantics plus differential testing against `secilc` that found real compiler bugs, but the inspected random generator covers a bounded fragment and comparison is primarily allow-edge projection; recover exact campaign bounds/replayability before stronger claims.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with `semantic_policy_identity` and evidence-kind bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C412–C413:** SELinux CIL provides strong empirical compiler-differential evidence: executable semantics vs `secilc`/`sesearch`, hand-crafted plus random tests, and multiple production compiler bugs found/fixed. This must be certified only for the exact tested fragment/projection and is not theorem-level compiler correctness.
- **C414–C416:** OPA exercises exact compiled Wasm bytes against expected semantic cases, but known numeric/strict-error/host-builtin boundaries and issue #8124 show that target identity and exact execution route are part of the semantic claim.
- **C417:** policy assurance should use a typed evidence lattice plus integration state rather than a global verified boolean.
- **C418:** targeted search still did not establish machine-checked Rego->IR/Wasm or full CIL->kernel production semantic preservation; stronger empirical conformance narrows but does not close that proof gap.
- **C419:** OPA's current top-level fuzz target fuzzes AST parsing/module compilation; inspected code does not provide a cross-backend topdown-vs-Wasm semantic oracle.
- **C420:** OPA has a separate `v1/test/wasm/assets` compiled-Wasm suite executed through a Node path in addition to the shared semantic corpus. Evidence records must preserve per-suite target/oracle/exceptions instead of collapsing all tests into one boolean.
- **C263:** pinned CSSC static source still contains mutable historical provider attribution, but faithful runtime reproduction remains unavailable and unpromoted.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Continue targeted search for a true randomized/fuzz semantic differential path between OPA topdown and Wasm; keep parser/compiler fuzz separate if none is found.
3. Search for Rego->IR / IR->Wasm proof or translation-validation artifacts.
4. Recover exact CIL test-campaign bounds/seeds/replayability and any comparison projection beyond allow edges.
5. Refine `PolicyEvidenceClaimV1` with evidence kind, test-suite/fuzz-oracle identity, exact semantic fragment/configuration, artifact/runtime identity, suite/proof revision, observation projection, exceptions/mismatches and integration state.
6. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0107JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.