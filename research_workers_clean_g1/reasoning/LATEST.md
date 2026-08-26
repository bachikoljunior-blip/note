# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0107JST.md`
Current invocation chain: `2026-08-27T0107JST.md`
Previous checkpoint chain: `2026-08-27T0033JST.md`
Earlier predecessor chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

`2026-08-27T0107JST.md` uses observed automation-runtime start `2026-08-27T01:00:33+09:00` and observed checkpoint time `2026-08-27T01:07:24+09:00`; chronology is valid. The prior chronology correction in `2026-08-27T0006JST-followup5.md` remains authoritative for earlier affected artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Treat compiler/runtime assurance as a layered, typed evidence graph: theorem semantic preservation, shared-oracle/differential conformance, serialization/schema correspondence, ABI/interface evidence and manual specification are distinct evidence classes.
4. Every compiler/runtime claim must bind exact supported fragment, semantic configuration, source/target revisions, emitted artifact identity, observation projection, exceptions/mismatches and integration state.
5. Cedar CST->AST theorem evidence remains on `frontend-formalization` while umbrella PR #992 is draft/open; raw text->CST, extension parsers and production Rust correspondence remain separate claims.
6. OPA now has strong shared-corpus topdown/Wasm E2E evidence on exact compiled Wasm bytes, but explicit >64-bit-integer and strict-error differences show that target equivalence is fragment-qualified.
7. Search for randomized/fuzz topdown-vs-Wasm differential testing and machine-checked Rego->IR / IR->Wasm semantic preservation; finite E2E suites, IR schema and ABI do not substitute for compiler correctness.
8. CIL has executable semantics plus differential testing against `secilc` that found real compiler bugs, but the inspected random generator covers a bounded fragment and comparison is primarily allow-edge projection; recover exact campaign bounds/replayability before stronger claims.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with `semantic_policy_identity` and evidence-kind bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C412–C413:** SELinux CIL provides strong empirical compiler-differential evidence: executable semantics vs `secilc`/`sesearch`, hand-crafted plus random tests, and multiple production compiler bugs found/fixed. This must be certified only for the exact tested fragment/projection and is not theorem-level compiler correctness.
- **C414:** current OPA runs the same v0/v1 semantic test corpus through the Go topdown evaluator and through source->Wasm compilation followed by evaluation of the exact compiled bytes. This motivates `shared_oracle_cross_backend_conformance` as a distinct evidence class.
- **C415:** current OPA Wasm exceptions expose known semantic-domain boundaries, notably >64-bit integers; strict builtin errors also differ. Target/runtime tuple and supported fragment are grant-relevant identity.
- **C416:** OPA issue #8124 shows that a nominal `-t wasm` route may recompile rather than execute precompiled bundle bytes. Validation must execute the exact artifact/runtime route being certified or separately prove artifact identity.
- **C417:** policy assurance should use a typed evidence lattice plus integration state rather than a global verified boolean.
- **C418:** targeted search still did not establish machine-checked Rego->IR/Wasm or full CIL->kernel production semantic preservation; stronger empirical conformance narrows but does not close that proof gap.
- **C263:** pinned CSSC static source still contains mutable historical provider attribution, but faithful runtime reproduction remains unavailable and unpromoted.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Inspect OPA for randomized/fuzz cross-backend topdown-vs-Wasm differential testing beyond the shared finite corpus.
3. Search for Rego->IR / IR->Wasm proof or translation-validation artifacts.
4. Recover exact CIL test-campaign bounds/seeds/replayability and any comparison projection beyond allow edges.
5. Refine `PolicyEvidenceClaimV1` with evidence kind, exact semantic fragment/configuration, artifact/runtime identity, suite/proof revision, observation projection, exceptions/mismatches and integration state.
6. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0107JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.