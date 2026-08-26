# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST-followup3.md`
Current invocation chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the predecessor chain, then the current invocation chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all pre-randomization crash/replay/epsilon=0 gates.
3. Treat policy assurance as separate claims: source faithfulness; verified parser/frontend; certified semantic core; source-to-core lowering; symbolic-analysis/compiler correctness; production compiler/runtime correspondence; complete mediation; exact per-effect authorization.
4. Use a certified authorization semantic anchor such as ACCPL/TEpla-like or equivalently mechanized Cedar/Datalog core where possible. Prove equivalence or authority-non-amplifying refinement from the authoritative source with clause coverage.
5. Arbitrary NL remains proposal-only for positive authority. Missing/uncovered grant-relevant clauses cannot default allow.
6. Search for verified/translation-validated compilers from real policy languages (XACML/SELinux/CIL/Rego/Cedar-like or controlled policy DSLs) into certified cores/executable formats. Distinguish verified analysis from verified compilation and model proof from production correspondence.
7. Bind the full semantic compiler/build tuple. SELinux CIL evidence shows compiler flags and unknown-action handling can alter security meaning even for the same source policy.
8. Record claim-scoped, versioned evidence (`parser_correctness`, `evaluation_semantics`, `conflict_detection`, `symbolic_compiler_correctness`, `compiler_refinement`, `production_correspondence`, `runtime_complete_mediation`, etc.) rather than a global “verified” bit.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact policy/request/schema/compiler/runtime/consumption-domain/freshness bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C385–C390:** controlled-formal source + verified parsing helps, but source-clause coverage and semantic lowering/non-amplification remain critical. AgentGuardUtil exposes coverage-silence risk; production NL-policy evidence uses validator-gated human confirmation; FORGE enforcement still assumes faithful encoding.
- **C391–C396:** certified access-control languages already exist (ACCPL/TEpla), so the missing chain is source faithfulness -> certified core -> production correspondence. Cedar demonstrates model-vs-production evidence separation; SELinux shows compiler flags are policy-semantic; verified XACML conflict analysis cannot stand in for unrelated compiler/runtime claims.
- **C397:** TEpla already contains executable decision semantics in Coq (`TEpolicy_EvalTE`) and proves properties over them; the paper's future-work extraction boundary is deployment/extraction, not absence of an executable formal evaluator.
- **C398:** current Cedar main now has sound/complete Lean proofs for its symbolic compiler and verification stack. This advances a model-level proof frontier relative to the 2024 paper, but does not erase the separate Rust production correspondence boundary.
- **C399:** current Cedar activity still treats frontend/parser formalization as a distinct frontier. Parser correctness cannot be inferred from evaluator/symbolic-compiler correctness.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Search for concrete extracted certified policy evaluators and verified/translation-validated real-policy-language -> core-policy compilers.
3. Inspect current Cedar frontend/parser formalization as public evidence but distinguish draft/in-progress work from completed proof.
4. Define `PolicyActivationCertificateV1` with source clause coverage, semantic lowering/refinement proof, certified-core digest, exact semantic build tuple, typed and version-bound `PolicyEvidenceClaimV0` records, production correspondence evidence level, and exact runtime digest.
5. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0006JST-followup3.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.