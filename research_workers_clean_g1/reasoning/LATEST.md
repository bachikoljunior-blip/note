# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the checkpoint chain above, then `2026-08-27T0006JST.md`. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail; this pointer intentionally stays compact.

## Top unresolved frontier

1. In the first environment able to faithfully materialize pinned CSSC source, executable-validate C263 unchanged: the one-batch/two-no-op-`REFINE_ARGUMENT` mutable provider-attribution overwrite; then rerun the identical fixture after immutable batch-consumption migration.
2. Preserve the full causal journal across generation/selection/reducer/effect identity and replace mutable provider `metadata.action_id` with immutable physical events plus append-only `ProposalBatchConsumptionEventV0`.
3. Refine `PolicyActivationCertificateV1` around a separate source-faithfulness edge: authoritative source/clause digests -> verified/validated parse -> canonical source denotation -> target authorization AST -> clause-complete equivalence or conservative/non-amplification certificate -> formal-policy verification -> activation.
4. Treat arbitrary NL compilation as a proposal, not positive authority. Positive authority requires machine-formal/controlled-formal semantics plus machine-checked lowering, or separately trusted confirmation. Uncovered grant-relevant clauses cannot default allow.
5. Continue proof-producing/verified controlled-language or policy-DSL -> authorization-IR compiler search. Verified parser infrastructure exists, but parser correctness and semantic-lowering correctness are separate obligations.
6. Preserve the per-effect authorization chain: `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic witness consumption/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`. No post-hoc receipt may retrospectively authorize dispatch.
7. Dispatch authorization remains bound to raw effect input digest, canonical semantic request digest, principal/delegation/resource/route, active policy hash/epoch, exact schema/tool/compiler/config tuple, nonce/consumption domain/freshness, authorizer/checker version, and commit identity.
8. Fix/eliminate cross-language request-context reconstruction; request/schema lowering versions and unsupported/lossy grant-relevant fields remain grant-critical.
9. Add coverage regressions from C388–C390: `uncovered_grant_relevant_clause_cannot_default_allow`, `compiler_silence_requires_deny_or_trusted_confirmation`, `rule_coverage_witness_must_bind_source_clause_digests`, while preserving every earlier route/dataflow/temporal/crash/cost/identity/epsilon=0 gate.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until all deterministic pre-randomization contracts pass.

## Newest synthesis

- **C385:** controlled English such as RECON/ACE can provide a formal source language, but no end-to-end machine-checked controlled-language -> authorization-AST lowering was established.
- **C386:** verified parser technology can remove syntax/AST parsing from the trust gap; semantic lowering remains a separate proof obligation.
- **C387:** proof-producing/translation-validating compilation suggests an untrusted policy compiler can emit an AuthAST plus machine-checkable equivalence or authority-non-amplification certificate.
- **C388:** AgentGuardUtil shows useful deterministic enforcement over compiled rules, but explicitly silent behavior when no compiled rule covers a task exposes a fail-open coverage risk for authority semantics.
- **C389:** an ACL Industry 2026 production NL-policy system uses validator-gated, human-confirmed publication rather than treating raw induced trees as autonomous executable authority.
- **C390:** formal Datalog/reference-monitor enforcement guarantees still assume policy faithfulness; source-clause coverage/entailment must therefore be a separate activation-certificate edge.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available; never upgrade static inspection to runtime evidence.
2. Specify `PolicyActivationCertificateV1` with `source_clause_digest_set`, `compiled_rule_digest_set`, `clause_to_rule_map`, `coverage_status`, `uncovered_clause_set`, semantic proof/refinement certificate, and trusted-confirmation fallback.
3. Define the machine-checkable authority-non-amplification relation between controlled-formal source semantics and target AuthAST, including explicit denies/obligations.
4. Continue targeted search for proof-producing controlled-language/policy-DSL lowering and translation-validation methods that prove semantic refinement rather than parser correctness alone.
5. Preserve all prior cost, crash-recovery, causal-journal, route/dataflow/temporal, request/schema, output-release, consumption-domain, identity and epsilon=0 gates.

`2026-08-27T0006JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.