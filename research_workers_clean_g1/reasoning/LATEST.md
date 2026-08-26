# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0033JST.md`
Current invocation chain: `2026-08-27T0033JST.md`
Previous checkpoint chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`
Earlier predecessor chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

The exact chronology correction in `2026-08-27T0006JST-followup5.md` remains authoritative for the prior invocation. `2026-08-27T0033JST.md` uses an observed automation-runtime start (`2026-08-27T00:29:49+09:00`) and an observed checkpoint clock (`2026-08-27T00:33:58+09:00`); chronology is valid for the new invocation.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Preserve immutable provider-cost events, append-only batch-consumption edges, causal decision/outcome journaling, and all crash/replay/epsilon=0 pre-randomization gates.
3. Model policy assurance as a layered evidence graph: raw text parser/CST, CST->AST, extension parser, AST semantics/validation, symbolic analysis, production compiler/runtime correspondence, complete mediation and exact per-effect authorization.
4. Track proof integration state explicitly: feature-branch proof is not main/released/deployed evidence.
5. Cedar CST->AST verification is now substantial on `frontend-formalization`, but PR #992 remains draft/open; raw policy text->CST parser correctness and production Rust correspondence remain distinct claims.
6. Track extension parser proofs separately; PR #1005 is still open against main as observed, while the earlier Decimal-only PR #979 closed unmerged.
7. Search Rego->IR / IR->Wasm and CIL->kernel-policy semantic-preservation evidence; IR schemas, ABIs and conformance tests are complementary but not substitutes for compiler-correctness claims.
8. Define `semantic_policy_identity` over all grant-relevant source language, compiler flags, target, evaluator/runtime mode, built-ins, schema/data contract and exact deployed artifact versions.
9. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact policy/request/schema/compiler/runtime/consumption-domain/freshness bindings.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C406–C407:** Cedar frontend verification materially advanced in August 2026. PR #1004 merged CST semantics plus CST->AST soundness/strong-completeness proofs into the `frontend-formalization` branch; the umbrella PR #992 is still draft/open against main.
- **C408:** the raw policy text->CST parser edge remains distinct. The inspected current parser theorem surface proves identifier/string helper properties, while the broad semantic-preservation theorem is CST->AST, not bytes/text->CST.
- **C409:** extension parser verification is separate and still integrating: PR #979 closed unmerged; PR #1005 proposes correctness proofs for Datetime/Decimal/Duration/IP parsers and remains open as observed.
- **C410:** proof evidence must bind integration state (`feature_branch | merged_main | released | deployed`) and frontend layer; a branch proof cannot certify a deployed runtime.
- **C411:** OPA's current IR v1 JSON Schema and CI drift test strengthen transport/shape correspondence, but targeted search still did not establish machine-checked Rego->IR or IR->Wasm semantic preservation. Schema/ABI compatibility is not compiler correctness.
- **C263:** faithful runtime reproduction was attempted again but the execution container could not resolve `github.com`; no runtime evidence was promoted.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Reinspect Cedar PR #992/#1005 for raw text->CST proof completion and main/release integration; keep artifact/ref exact.
3. Search for Rego->IR, IR->Wasm and CIL->kernel-policy translation-validation or proof artifacts.
4. Refine `PolicyActivationCertificateV1` / `PolicyEvidenceClaimV0` with integration state, frontend layer, supported fragment, proof artifact revision and exact source/target runtime bindings.
5. Preserve every prior deterministic gate; epsilon>0 remains forbidden.

`2026-08-27T0033JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.