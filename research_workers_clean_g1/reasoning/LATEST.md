# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST-followup4.md`
Current invocation chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the predecessor chain, then the current invocation chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Treat policy assurance as separate claims: source faithfulness; parser/frontend correctness; certified semantic core; source-to-core lowering; static/symbolic analysis correctness; production compiler/runtime correspondence; complete mediation; exact per-effect authorization.
4. Prefer a certified semantic authorization anchor (ACCPL/TEpla-like or equivalently mechanized Cedar/Datalog core), with source-clause coverage and machine-checked equivalence or authority-non-amplifying refinement.
5. Arbitrary NL remains proposal-only for positive authority. Missing/uncovered or unsupported grant-relevant clauses/features cannot default allow.
6. Search for verified/translation-validated compilers from real policy languages (XACML/Rego/OPA/SELinux/CIL/Cedar-like or controlled policy DSLs) into certified cores/executable formats. Brown's XACML/Rego implementation explicitly isolates this source-compiler proof edge as future work.
7. Bind the full semantic compiler/build tuple and supported language fragment. SELinux CIL evidence shows compiler flags, unknown-action handling, and production/compiler-versus-manual discrepancies can alter effective semantics.
8. Record claim-scoped, versioned evidence rather than a global “verified” bit. Formal model proofs, static analyses, conformance/differential testing, and production correspondence are complementary but non-substitutable claims.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact policy/request/schema/compiler/runtime/consumption-domain/freshness bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C385–C390:** controlled-formal source + verified parsing helps, but source-clause coverage and semantic lowering/non-amplification remain critical. AgentGuardUtil exposes coverage-silence risk; production NL-policy evidence uses validator-gated human confirmation; FORGE enforcement still assumes faithful encoding.
- **C391–C396:** certified access-control languages already exist (ACCPL/TEpla). Cedar demonstrates model-vs-production evidence separation; SELinux shows compiler flags are policy-semantic; verified XACML conflict analysis cannot stand in for compiler/runtime correctness.
- **C397–C399:** TEpla has executable policy evaluation inside Coq; deployment extraction remains separate. Current Cedar main now verifies symbolic compilation soundness/completeness, but frontend/parser and Rust production correspondence remain distinct claims tied to exact revisions.
- **C400:** Brown's Lean XACML/Rego work makes the source-compiler boundary explicit: target executable semantics can be formal while an OCaml source translator remains opaque; verified compilation is future work in that implementation.
- **C401:** IFCIL documents production CIL compiler/manual disagreements and compiler bugs; empirical correspondence testing can discover semantic disagreements but does not itself choose which semantics is authoritative.
- **C402:** activation should retain formal proofs, supported-fragment evidence, source-translation evidence, conformance/differential evidence, known exceptions, and production digests as separate claims.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Search for later/current verified XACML/Rego/OPA translators/decision engines and verified SELinux/CIL production-compilation correspondence.
3. Search for source-policy -> certified-core translation validators; inspect ACCPL/TEpla extraction and current Cedar frontend formalization only within observed scope.
4. Define `PolicyActivationCertificateV1` and `PolicyEvidenceClaimV0` with source clause/feature coverage, semantic-authority source, translation proof/refinement, certified-core digest, semantic compiler/build tuple, evidence level, known model/compiler disagreements, and exact deployed runtime digest.
5. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0006JST-followup4.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.