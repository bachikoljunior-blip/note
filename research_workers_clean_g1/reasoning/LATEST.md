# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST-followup2.md`
Current invocation chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the predecessor chain, then the current invocation chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all pre-randomization crash/replay/epsilon=0 gates.
3. Treat policy assurance as separate claims: source faithfulness; certified semantic core; source-to-core lowering; production compiler/runtime correspondence; complete mediation; exact per-effect authorization.
4. Use a certified authorization semantic anchor such as ACCPL/TEpla-like or equivalently mechanized Cedar/Datalog core where possible. Prove equivalence or authority-non-amplifying refinement from the authoritative source with clause coverage.
5. Arbitrary NL remains proposal-only for positive authority. Missing/uncovered grant-relevant clauses cannot default allow.
6. Search for verified/translation-validated compilers from real policy languages (XACML/SELinux/CIL/Rego/Cedar-like or controlled policy DSLs) into certified cores/executable policy formats. Distinguish verified analysis from verified compilation.
7. Bind the full semantic compiler/build tuple. SELinux CIL evidence shows options such as disabling `neverallow` checks and changing unknown-action handling can alter security meaning even for the same source policy.
8. Record evidence as claim-scoped artifacts (`evaluation_semantics`, `conflict_analysis`, `compiler_refinement`, `production_correspondence`, `runtime_complete_mediation`, etc.) rather than a single “verified” flag.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact policy/request/schema/compiler/runtime/consumption-domain/freshness bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C385–C390:** controlled-formal source + verified parsing helps, but source-clause coverage and semantic lowering/non-amplification remain the critical activation edge. AgentGuardUtil exposes coverage-silence risk; production NL-policy evidence uses validator-gated human confirmation; FORGE enforcement still assumes faithful policy encoding.
- **C391–C393:** certified access-control languages already exist (ACCPL/TEpla), so the gap is not formal authorization semantics itself. Cedar demonstrates a distinct production-correspondence boundary: mechanized Lean model proofs plus differential/property testing of Rust, with parser outside the Lean model.
- **C394:** production policy compiler flags are grant-semantic. Exact compiler version/config/target policy version/unknown-action mode must be part of policy identity.
- **C395:** verified XACML conflict detection is a valuable activation-time analysis but cannot satisfy unrelated claims about evaluator/compiler/runtime correctness.
- **C396:** the practical target is a mixed-evidence but explicitly scoped chain from source faithfulness through certified IR and production correspondence to per-effect authorization, not a misleading global `verified=true` bit.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Search for actual verified/translation-validated policy compilers from XACML/SELinux/CIL/Rego/Cedar-like sources to executable/runtime formats.
3. Inspect ACCPL/TEpla extraction and verified firewall-policy extraction for a reference-oracle pattern.
4. Define `PolicyActivationCertificateV1` with clause coverage, semantic translation proof/refinement, certified-core digest, semantic compiler/build tuple, typed `PolicyEvidenceClaimV0` records, production correspondence evidence level, and exact deployed runtime digest.
5. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0006JST-followup2.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.