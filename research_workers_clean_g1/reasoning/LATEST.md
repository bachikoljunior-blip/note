# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST-followup5.md`
Current invocation chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the predecessor chain, then the current invocation chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

The exact chronology correction in `2026-08-27T0006JST-followup5.md` is authoritative for this invocation: earlier current-invocation `Observation time` fields were manually composed artifact labels and must not be treated as exact event timestamps (`chronology_valid=false` for those fields). Subsequent receipt timestamps must come from actual clock observations.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Treat policy assurance as separate claims: source faithfulness; parser/frontend correctness; certified semantic core; source-to-core lowering; static/symbolic analysis correctness; production compiler/runtime correspondence; complete mediation; exact per-effect authorization.
4. Prefer a certified semantic authorization anchor, with source-clause coverage and machine-checked equivalence or authority-non-amplifying refinement. Arbitrary NL remains proposal-only for positive authority.
5. Search for verified/translation-validated real policy compilation: XACML/Rego/OPA/SELinux/CIL/Cedar-like source -> certified core/IR/compiled runtime artifact. Distinguish verified analysis/model proof from compiler/runtime correspondence.
6. Define `semantic_policy_identity` over all grant-relevant source language, compiler flags, target, evaluator/runtime mode, built-ins, schema/data contract and exact deployed artifact versions. Identical policy text under different semantic configuration is not the same authorization policy identity.
7. Record claim-scoped, versioned evidence rather than a global “verified” bit. Formal proof, static analysis, conformance/differential testing, known production deviations, and complete mediation are complementary but non-substitutable.
8. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact policy/request/schema/compiler/runtime/consumption-domain/freshness bindings.
9. Preserve coverage, unsupported-feature, route/dataflow/temporal, request-vs-dispatch, lossy-lowering, crash/recovery, cost, output-release, nonce-consumption-domain and epsilon=0 regressions.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C385–C390:** controlled-formal source + verified parsing helps, but source-clause coverage and semantic lowering/non-amplification remain critical. AgentGuardUtil exposes coverage-silence risk; production NL-policy evidence uses validator-gated human confirmation; FORGE enforcement still assumes faithful encoding.
- **C391–C399:** certified access-control languages already exist; TEpla has executable Coq policy evaluation, current Cedar verifies symbolic compilation, while frontend/parser and production correspondence remain separate claims.
- **C400–C402:** Brown's XACML/Rego work explicitly leaves source compilation unverified; IFCIL documents production CIL compiler/manual disagreement; formal semantics and empirical correspondence are complementary evidence, not substitutes.
- **C403–C405:** OPA and SELinux independently show that compiler/evaluator/runtime configuration is grant-semantic. Rego version, strict error mode, compile target, host built-ins, compiler flags and exact artifacts must be part of semantic policy identity where relevant.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Search for Rego->IR/Wasm and CIL->kernel-policy semantic-preservation proofs/translation validators, and current Cedar frontend/parser proof completion status.
3. Search for concrete extracted certified evaluators and source-policy -> certified-core compilers.
4. Define `PolicyActivationCertificateV1`, typed `PolicyEvidenceClaimV0`, and `semantic_policy_identity` with exact supported-fragment and artifact/configuration bindings.
5. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0006JST-followup5.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.