# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-26T2301JST-followup4.md`
Invocation chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`
Previous invocation checkpoint: `2026-08-26T2200JST-followup.md`

Read `STATE.md` for the accumulated base, then the checkpoint chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail; this pointer intentionally stays compact.

## Top unresolved frontier

1. In the first environment able to faithfully materialize pinned CSSC source, executable-validate C263 unchanged: the one-batch/two-no-op-`REFINE_ARGUMENT` mutable provider-attribution overwrite; then rerun the identical fixture after immutable batch-consumption migration.
2. Preserve the full causal journal across generation/selection/reducer/effect identity and replace mutable provider `metadata.action_id` with immutable physical events plus append-only `ProposalBatchConsumptionEventV0`.
3. Split the authorization chain into `PolicyActivationCertificateV0` -> pre-dispatch `ToolDispatchAuthorizationWitnessV0` -> atomic witness-consumption/effect commit -> `EffectReceiptV0` -> optional `OutputReleaseAuthorizationWitnessV0`; never treat post-hoc receipts as retrospective authority.
4. Policy activation must bind the evidence chain `trusted intent/source -> parser/constructor -> canonical policy AST -> schema/type validation -> symbolic verification -> activation`. Prefer a machine-formal typed AST/PST; arbitrary NL remains provisional until separately trusted intent/translation evidence exists.
5. Dispatch authorization must bind both the exact raw effect input and the canonical semantic authorization request, plus principal/delegation, resource, route, exact active policy hash/epoch, deployed schema/tool-description/compiler/config tuple, nonce, consumption domain, freshness facts, checker/authorizer version, and effect commit identity.
6. Treat learned models as untrusted policy/proof-search optimizers only. They may retrieve facts, rank safe alternatives, backtrack, or spend compute, but a deterministic proof/authorization checker alone may establish authority.
7. Fix or eliminate cross-language request-context reconstruction. Current Cedar-for-Agents Rust lowering includes typed input context, while merged WASM/Python convenience surfaces expose principal/action/resource/entities and reconstruct context outside the core generator. Prefer one canonical full request/typed context with semantic roundtrip guarantees.
8. Treat request/schema lowering version as grant-critical. Generator config changes can alter authorization semantics; historical JSON-Schema lowering issues demonstrate version-sensitive representations. Lossy/unsupported grant-relevant fields must fail closed or require an explicit conservative approval witness.
9. Add all new deterministic regressions from C366 and C373–C384, including request-vs-dispatch equality, schema/config/lowering-version binding, lossy-lowering non-amplification, two-phase output authorization, nonce consumption-domain safety, and no retrospective authorization. Preserve every earlier route/dataflow/temporal/crash/cost/identity/epsilon=0 gate.
10. Continue targeted search for proof-producing/verified controlled-language -> authorization-AST compilers and verified request-normalization boundaries. The deterministic provider pilot remains blocked; epsilon>0 remains forbidden until all pre-randomization contracts pass.

## Newest synthesis

- **C361–C367:** Cedar substantially closes formal-policy -> symbolic-analysis verification but parser/PST/production correspondence remain separate trust edges. AutoCedar supports NL-proposed -> mechanically checked + trusted-intent-approved behavior atoms -> fixed formal target. C263 remains static/source evidence only.
- **C368–C372:** Proof-carrying authorization suggests a clean role for learned reasoning: the model searches/builds authorization evidence, while a small deterministic checker controls execution. Policy activation and per-effect authorization are separate artifacts.
- **C373–C376:** request encoding config, schema/tool-description/compiler version, raw effect identity, and canonical semantic request identity all matter. Public Cedar-for-Agents convenience bindings do not themselves carry the Rust-generated typed request context through FFI.
- **C377–C380:** merged PR #73 explicitly reconstructs `context.input` in JS after `generateRequest`; historical schema-lowering issues show version-sensitive semantics; unsupported/coarse fields must not disappear from grant checks; output-dependent authorization requires a separate post-result release gate and cannot retroactively authorize dispatch.
- **C381–C384:** the current EP Internet-Draft independently converges on exact action hash, exact policy hash, nonce/freshness, and one-time consumption, but correctly scopes consume-once to a shared atomic consumption domain. Signed decision/audit receipts are useful joins, not substitutes for the semantic authorization request or pre-dispatch authority.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available; never upgrade static inspection to runtime evidence.
2. Draft the concrete schemas and join invariants for `PolicyActivationCertificateV0`, `ToolDispatchAuthorizationWitnessV0`, `EffectReceiptV0`, and `OutputReleaseAuthorizationWitnessV0`.
3. Specify atomic/recoverable witness-consumption + effect-commit semantics and request-vs-dispatch mismatch tests, including independent-consumption-domain limits.
4. Inspect Cedar-for-Agents schema/request generation and FFI canonicalization further, especially typed context, schema/config/tool digest binding and unsupported/lossy JSON-Schema constructs.
5. Continue proof-producing controlled-language lowering search and preserve all prior cost, crash-recovery, identity, effect-safety, causal-journal, authority-non-amplification and provider-pilot gates.

`2026-08-26T2301JST-followup4.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.