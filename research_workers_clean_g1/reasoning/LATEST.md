# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0006JST-followup.md`
Current invocation chain: `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md`
Previous checkpoint chain: `2026-08-26T2301JST.md` -> `2026-08-26T2301JST-followup.md` -> `2026-08-26T2301JST-followup2.md` -> `2026-08-26T2301JST-followup3.md` -> `2026-08-26T2301JST-followup4.md`

Read `STATE.md`, then the predecessor chain, then the current invocation chain above. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail; this pointer intentionally stays compact.

## Top unresolved frontier

1. In the first environment able to faithfully materialize pinned CSSC source, executable-validate C263 unchanged: the one-batch/two-no-op-`REFINE_ARGUMENT` mutable provider-attribution overwrite; then rerun the identical fixture after immutable batch-consumption migration.
2. Preserve the full causal journal and immutable physical provider-cost events plus append-only batch-consumption edges.
3. Treat policy assurance as three separate proof/evidence edges: **source faithfulness**, **lowering to a certified authorization semantic core**, and **production-runtime correspondence**. Never collapse them into one “compiler verified” bit.
4. Prefer a certified authorization semantic anchor (ACCPL/TEpla-like or equivalently mechanized Cedar/Datalog core) over an ad hoc target AST. Prove source->core equivalence or authority-non-amplifying refinement with clause coverage.
5. Arbitrary NL compilation remains proposal-only for positive authority. Uncovered grant-relevant clauses cannot default allow; machine-checked conservative lowering or separately trusted confirmation is required.
6. Search specifically for verified compilers/translation validators from real policy languages or controlled policy languages into certified authorization cores; certified core policy languages themselves now count as established precedent, not an open gap.
7. Separately prove or accurately classify production correspondence. Cedar-style Lean model proofs plus differential/property testing are strong evidence but are not a formal theorem that the deployed Rust parser/engine equals the model.
8. Preserve the per-effect chain: `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic witness consumption/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, with exact request/policy/schema/compiler/runtime digests and consumption-domain/freshness binding.
9. Preserve coverage, route/dataflow/temporal, request-vs-dispatch, lossy-lowering, crash/recovery, cost, identity, output-release, nonce-consumption-domain and epsilon=0 regressions.
10. Deterministic provider pilot remains blocked; epsilon>0 remains forbidden until all deterministic pre-randomization contracts pass.

## Newest synthesis

- **C385–C390:** controlled language can reduce ambiguity and verified parsing can remove syntax from the TCB, but policy activation still needs source-clause coverage and a machine-checked semantic lowering/non-amplification edge. AgentGuardUtil exposes a fail-open risk when no compiled rule covers a task; a production ACL Industry system uses validator-gated, human-confirmed publication; FORGE/PCAS formal enforcement still assumes faithful policy encoding.
- **C391:** formally certified access-control languages already exist. TEpla and ACCPL encode authorization semantics and correctness properties in Coq. TEpla still describes program extraction/certified tools as future work; ACCPL positions extraction and use as an intermediate target but source-language certification remains future work.
- **C392:** this makes a certified policy language a plausible semantic anchor IR for translation validation. The missing chain is source faithfulness -> certified core -> deployed evaluator correspondence.
- **C393:** Cedar's verification-guided development proves properties of Lean models while using differential/property testing for production Rust correspondence; its parser is not Lean-modeled. Record that evidence level accurately rather than calling it an end-to-end deployment proof.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available; never upgrade static inspection to runtime evidence.
2. Inspect TEpla/ACCPL Coq artifacts for the executable/extraction boundary and suitability as a small reference authorization oracle.
3. Search for verified/translation-validated compilers from controlled policy languages, XACML/SELinux/Rego/Cedar-like languages, or other real policy DSLs into certified cores.
4. Define `PolicyActivationCertificateV1` fields for source clause coverage, semantic translation proof/refinement relation, certified-core digest, production correspondence evidence level, and exact deployed runtime digest.
5. Preserve every prior deterministic pre-randomization gate; epsilon>0 remains forbidden.

`2026-08-27T0006JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.