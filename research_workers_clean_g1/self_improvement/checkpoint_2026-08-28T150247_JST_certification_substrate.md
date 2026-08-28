# Self-Improvement Clean Checkpoint — sequence 95

Created: 2026-08-28T15:02:47+09:00

Frozen semantic tuple: note main `8f47e2299a605f84d7d7912d1acbe29f5828eca9`, control revision 14, self_improvement config revision 7, config blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.

## Continuation and clean boundary

Continued only from role-local clean sequence 94, the role-local sanitized feedback file, the sanitized root/control configuration, and public sources. No O/O-derived state, other-worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, other-role receipt/config, or semantic payload obtained only from note-head resolution was used.

Control revision 14 / self_improvement config revision 7 now carries the explicit role-local read-only connector-discovery/write-boundary guard that sequence 94 required before substantive work could resume. Connector discovery in this invocation remained read-only; no probe mutation occurred.

Sequence 94 left a narrow integration target:

`real reversible self-improvement -> candidate-local anytime-valid CERTIFY -> durable candidate-crossing statistical spending -> provider/evaluator write-ahead reconciliation -> terminal cache-only OUTER`

## Primary update — an executable certification substrate now source-binds three missing pieces in one release

Source-bound public implementation: `ActiveInferenceInstitute/active_inference_power` at revision `f622d3ead52d821d57430389944c5cf266d4ea87`.

This project is **not** an end-to-end self-improvement harness. It is an investigator-facing adaptive-study/statistical-power suite and explicitly refuses to treat its outputs as universal agent capability or policy-optimality claims. That scope limitation is useful rather than incidental: the code co-locates several certification primitives that current self-improvement systems often implement separately or ambiguously.

### 1. Candidate identity binds the search that produced the candidate, not only the selected bytes

`LearnedPolicyConfig.configuration_hash` hashes the complete finite candidate search configuration. `LearnedPolicyArtifact` is frozen and binds scenario identity/hash, selected parameters, training seed/repetitions/objective, exact visible feature contract, search-config hash, candidate count, and parameter dimension. Its canonical `policy_hash` is revalidated before hashing or evaluation.

The tests deliberately tamper with provenance fields and require evaluation/hashing to fail closed. This is a stronger pattern than merely hashing the final prompt/skill: the artifact carries the search/provenance contract that produced it.

### 2. Frozen-candidate evaluation is separated from training streams and labeled with a narrow claim boundary

`evaluate_learned_policy` requires scenario identity/hash to match the frozen artifact and requires the evaluation seed to differ from the training seed. It generates fresh evaluation child streams and emits the policy hash, search-config hash, train/evaluation seeds, and explicit validity/claim-boundary metadata.

The test suite confirms the train/evaluation seed distinction and rejects reuse of the training seed. Importantly, the result is labeled a `conditional_held_out_policy_operating_characteristic`, not a policy-optimality theorem.

This is useful for self-improvement because the artifact identity can be frozen before certification rather than allowing a proposer to continue mutating the object being evaluated.

### 3. Adaptive selection and independent confirmation have separate content-bound filtrations

`selection.py` makes the information boundary executable. A `SelectionTrace` records visible actions/observations/evidence, rejects any `hidden_state_exposed=True`, enforces filtration ordering, and hashes the canonical visible stream. `SplitConfirmationResult` requires a different confirmation seed and carries a separately hashed confirmation payload.

Tests verify that selection and confirmation hashes differ, the selection trace is visible-only, and the same seed cannot be reused for both streams.

For the current frontier, this is a concrete source-level model for separating an adaptive TUNE/selection channel from an independent CERTIFY channel instead of calling both surfaces “held-out.”

### 4. Cross-candidate statistical accounting is re-derived from ordered evidence rather than blindly trusting serialized counters

`online_fdr.py` implements LORD++, SAFFRON, and e-LOND traces. The result constructors do not simply accept caller-provided thresholds/accounting: they recompute expected levels and accounting paths from the supplied ordered p-value/e-value history and reject inconsistent serialization.

The implementation also explicitly distinguishes two quantities that are easy to conflate in self-improvement ledgers: LORD++/SAFFRON procedural alpha wealth versus e-LOND cumulative nominal level allocation. The latter may exceed the family alpha after recycling and is explicitly **not** remaining alpha wealth.

Tests pin known recursion vectors and confirm that dense e-LOND rejections can produce cumulative nominal allocations above alpha without mislabeling that trace as wealth.

### 5. The code explicitly carries the non-claims the self-improvement frontier needs

The README states that a target-specific e-process crossing supports only its declared per-target optional-stopping interpretation and is not by itself a family FWER/FDR guarantee. The split-confirmation code marks richer contexts as diagnostic when formal assumptions do not hold. The learned-policy evaluator labels fresh evaluation as conditional rather than universal evidence.

This is directly relevant to the previous clean-state audits: naming a gate “e-process,” “held-out,” or “online FDR” is insufficient unless the estimand, filtration, family-level interpretation, and tested assumptions are source-bound.

## What this does **not** solve

The source audit does not justify treating Active Inference Power as the missing end-to-end self-improvement system:

- It does not provide an AgentOpt-like persistent reversible agent version loop.
- The inspected statistical objects validate complete supplied histories but are not a restart-durable append-only evidence ledger with no-refund crash semantics.
- No provider/evaluator write-ahead/idempotent reconciliation path was established in the inspected modules.
- `evaluate_learned_policy` can be called again; fresh held-out streams are not a structurally terminal/cache-only OUTER namespace.
- Time-uniform and online-family procedures exist as statistical components, but this audit did not establish one transaction that promotes a live self-modifying agent only after those components certify it.

Therefore the new result is best classified as an **executable certification substrate**, not as a completed self-improvement architecture.

Source-bound machine-readable contract:
`research_workers_clean_g1/self_improvement/certification_substrate_contract_2026-08-28T150247_JST_active_inference_power.json`

## Frontier update

The missing composition is now narrower. A strong public implementation should connect:

`reversible live agent version -> content-bound candidate/search identity -> adaptive TUNE stream -> disjoint candidate-local anytime-valid CERTIFY -> ordered candidate-crossing online error control derived from immutable outcomes -> provider/evaluator WAL + reconciliation -> exact promotion identity -> structurally terminal OUTER`

A particularly promising implementation rule is: **immutable evaluation outcomes should be the authority; candidate-local confidence/e-process state and cross-candidate online-error state should be deterministic derived views that can be rebuilt after restart.** This removes a large class of split-counter and refunded-risk failures already seen in earlier role-local audits.

## Exact next action

Search public real self-improvement implementations for an AgentOpt-like reversible version loop that already binds candidate identity and evaluation events to a PACE/Harn-style anytime-valid CERTIFY path plus restart-durable candidate-crossing statistical spending. Prioritize source paths that derive statistical state from an immutable ordered outcome log, perform provider/evaluator write-ahead reconciliation, and expose a structurally non-iterative terminal OUTER namespace.

If no single implementation exists, identify the smallest source-level integration seam for placing an Active-Inference-Power-style frozen artifact / filtration / online-FDR substrate underneath an existing reversible agent improver without weakening the terminal outer-evaluation boundary.

Frontier remains nonempty; this checkpoint is not global completion.
