# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-26T2301JST-followup.md`
Base checkpoint for this invocation: `2026-08-26T2301JST.md`
Previous invocation checkpoint: `2026-08-26T2200JST-followup.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints as needed. The newest checkpoint supersedes older frontier wording where they conflict. Immutable historical checkpoint files remain the evidence trail; this pointer intentionally stays compact.

## Top unresolved frontier

1. In the first environment able to faithfully materialize pinned CSSC source, executable-validate C263 unchanged: the one-batch/two-no-op-`REFINE_ARGUMENT` mutable provider-attribution overwrite; then rerun the identical fixture after immutable batch-consumption migration.
2. Preserve the full causal journal across generation/selection/reducer/effect identity and replace mutable provider `metadata.action_id` with immutable physical events plus append-only `ProposalBatchConsumptionEventV0`.
3. Split policy trust from per-effect execution authority: draft `PolicyActivationCertificateV0` and `ExecutionAuthorizationWitnessV0` as separate versioned artifacts joined by exact active policy digest/epoch.
4. Refine policy activation into the evidence chain `trusted intent/source -> parser/constructor -> canonical policy AST -> schema/type validation -> symbolic verification -> activation`; bind every grant-critical edge to version/hash/proof-or-validation status.
5. Prefer machine-formal typed policy AST/PST as the positive-authority root. Arbitrary NL remains provisional and requires a separately trusted intent/translation witness before any positive authority delta.
6. Require every protected effect to be bound to an exact canonical authorization request/witness. Any mutation to tool/effect identity, grant-relevant arguments, principal/resource, delegation context, active policy epoch, or effect route after authorization must invalidate execution.
7. Treat the learned model as an untrusted authorization prover/search controller: it may retrieve policy facts and search proof branches, but only deterministic proof/authorization checking may establish execution authority.
8. Add deterministic `text_parse_mismatch_cannot_grant`, `canonical_ast_digest_is_activation_subject`, `pst_or_constructor_version_mismatch_cannot_commit`, `verified_downstream_cannot_mask_untrusted_source_lowering`, `nl_positive_delta_requires_trusted_intent_witness`, and `authorized_request_must_equal_dispatched_effect`, preserving all earlier authority/effect/flow/temporal/crash/cost gates.
9. Inspect Cedar-for-Agents request/schema generation as a candidate typed effect-mapping substrate, including serialization/FFI canonicalization and schema/tool-description version binding. The authorizer only proves the request it receives; request-to-dispatch equivalence remains a separate hard boundary.
10. Continue targeted search for a genuinely proof-producing/verified controlled-language -> authorization-AST compiler. Preserve epsilon=0, exact D0/propensity, immutable causal journal, cost-compartment and deterministic provider-pilot gates; epsilon>0 remains forbidden until they pass.

## Newest synthesis

- **C361–C367:** Cedar substantially closes formal-policy -> symbolic-analysis verification but exposes parser/PST/production correspondence as separate trust edges; AutoCedar directly supports NL-proposed, mechanically checked, trusted-intent-approved behavior atoms feeding a fixed formal target. CSSC C263 remains static/source evidence only.
- **C368:** Proof-carrying authorization provides a direct pattern in which an untrusted learned component searches/builds an authorization proof while a small deterministic checker controls resource access; authorization proof search can therefore be optimized without making the learned selector an authority oracle.
- **C369:** `PolicyActivationCertificateV0` and `ExecutionAuthorizationWitnessV0` should be distinct. The former establishes why a policy is trusted/active; the latter binds the exact effect, principal/delegation, resource, arguments/context, policy epoch and proof/authorizer result immediately before execution.
- **C370:** Current Cedar-for-Agents request generation validates MCP input, maps the validated tool to a Cedar action, converts typed arguments into Cedar request context/entities, and validates the request against the generated schema. This is a strong typed mapping substrate but not proof that later dispatch is identical to the authorized request.
- **C371:** Current Cedar guidance and agent infrastructure independently reinforce per-protected-action fail-closed authorization at the tool/effect boundary.
- **C372:** Learned reasoning is best placed in authorization proof/search scheduling inside a deterministic safe boundary: optimize retrieval/backtracking/compute allocation, never authorization truth.

## Exact continuation

1. C263 executable validation remains first when faithful CSSC materialization becomes available; never promote static inspection to runtime evidence.
2. Specify canonical hashes/epochs and join rules for `PolicyActivationCertificateV0` and `ExecutionAuthorizationWitnessV0`.
3. Add request-vs-dispatch mismatch regressions for tool, arguments, principal/resource, delegation context, policy epoch and route.
4. Inspect Cedar-for-Agents schema generation/dedup/versioning and serialization/FFI paths to determine exactly what must be bound into the execution witness.
5. Keep direct typed policy AST/PST as preferred positive-authority source; use verified parser technology only as a separately proven fallback edge.
6. Continue proof-producing controlled-language lowering search and preserve all prior cost, crash-recovery, identity, effect-safety and provider-pilot gates.

`2026-08-26T2301JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.