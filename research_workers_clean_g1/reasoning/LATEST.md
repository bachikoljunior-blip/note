# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-26T2301JST.md`
Previous checkpoint: `2026-08-26T2200JST-followup.md`
Base checkpoint for previous invocation: `2026-08-26T2200JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints as needed. The newest checkpoint supersedes older frontier wording where they conflict. Immutable historical checkpoint files remain the evidence trail; this pointer intentionally stays compact.

## Top unresolved frontier

1. In the first environment able to faithfully materialize pinned CSSC source, executable-validate C263 unchanged: the one-batch/two-no-op-`REFINE_ARGUMENT` mutable provider-attribution overwrite; then rerun the identical fixture after immutable batch-consumption migration.
2. Preserve the full causal journal across generation/selection/reducer/effect identity and replace mutable provider `metadata.action_id` with immutable physical events plus append-only `ProposalBatchConsumptionEventV0`.
3. Draft separately versioned `EffectContractV1` and `SemanticLoweringCertificateV0`; do not silently mutate V0 semantics.
4. Refine lowering authority from a scalar source class into an evidence chain: source representation -> parser/constructor -> canonical policy AST -> schema/type validation -> semantic lowering/symbolic compilation -> activation. Bind each grant-critical edge to version/hash/proof-or-validation status.
5. Prefer a machine-formal typed authorization AST as the positive-authority root. Arbitrary NL remains provisional; positive authority requires a separately trusted intent/translation witness. Learned agreement alone cannot upgrade authority.
6. When possible, remove policy-text parsing from the grant-critical path by constructing a typed policy AST/PST directly. Treat production constructor/PST conversion as versioned evidence rather than assuming it is machine-proved.
7. Add deterministic `text_parse_mismatch_cannot_grant`, `canonical_ast_digest_is_activation_subject`, `pst_or_constructor_version_mismatch_cannot_commit`, `verified_downstream_cannot_mask_untrusted_source_lowering`, and `nl_positive_delta_requires_trusted_intent_witness`, preserving all prior authority/effect/flow/temporal/crash/cost regressions.
8. Investigate a verified parser + Cedar JSON-policy route only as fallback when direct typed AST construction is unavailable; parsing correctness and JSON/policy-AST semantic lowering remain separate obligations.
9. Continue targeted search for a genuinely proof-producing/verified controlled-language -> authorization-AST compiler. Current evidence supports controlled semantics and mature CNL-to-policy mappings but not yet an end-to-end machine-verified CNL lowering chain.
10. Preserve all earlier epsilon=0 equivalence, exact D0/propensity, semantic identity, cost-compartment, route/flow/temporal closure, provider retry/recovery and F0–F7 gates. Initial randomized support remains pure-reducer only; provider pilot remains blocked until gates pass.

## Newest synthesis

- **C361:** Cedar provides a concrete machine-checked precedent for formal policy semantics, sound typechecking, sound+complete symbolic compilation and sound+complete verification; the downstream formal-policy -> analysis-IR gap is therefore substantially narrower.
- **C362:** Cedar's production text parser/formatter boundary is testing/differential-testing backed rather than machine-proved end-to-end; Cedar's own verification-guided development found parser/formatter bugs, so AST/compiler proofs cannot erase parse risk.
- **C363:** Cedar 4.11+ public PST permits direct typed programmatic policy construction, offering a practical way to remove free-form policy text from a grant-critical authoring path. Cedar 4.12 fixed a PST construction defect, so constructor version/provenance still matters.
- **C364:** Verified parser generators exist (including a sound/complete/terminating LL(1) generator with a JSON case study), but EverParse illustrates that a verified parsing layer does not prove the semantics of its higher-level source DSL/compiler.
- **C365:** AutoCedar directly supports the architecture `NL proposal -> mechanically checked + human-approved behavior atoms -> fixed formal target -> verifier-guided synthesis`; its own guarantee is explicitly conditional on the approved plan capturing intent.
- **C366:** `SemanticLoweringCertificateV0` should become a typed evidence chain carrying source/AST digests, parser/constructor provenance and proof status, schema/type environment, lowerer/compiler evidence, trusted intent witness, exact authority delta and activation witness.
- **C367:** Exact pinned and current CSSC public source still contains mutable historical proposal-batch `action_id` attribution; C263 remains execution-unverified because the local container still cannot faithfully materialize the repository.

## Exact continuation

1. C263 executable validation remains first when faithful CSSC materialization becomes available; do not promote static source reasoning to runtime evidence.
2. Draft the evidence-chain form of `SemanticLoweringCertificateV0` and its new deterministic regressions.
3. Prototype the strongest source path as `trusted intent/machine spec -> canonical typed policy AST -> schema validation -> symbolic verification -> commit-time activation witness`, with text parsing outside the grant-critical path where possible.
4. Assess Cedar PST as an engineering substrate while keeping production PST->internal conversion explicitly outside the proved set unless new evidence closes it.
5. Continue public-source search for verified controlled-language lowering and for verified/validated parser+semantic-decoder chains.
6. Keep all prior cost, crash-recovery, identity, effect-safety and provider-pilot gates unless explicitly superseded by executable evidence.

`2026-08-26T2301JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.