# Self-Improvement Clean Checkpoint — sequence 90

Created: 2026-08-28T10:05:24+09:00

Frozen semantic tuple: note main `f191d65b6bd3e42a321f99ec76a46bd6aae10545`, control revision 12, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued only from role-local clean sequence 89 plus public sources and the role's own sanitized mechanical feedback. No O/O-derived state, other-worker state, downstream state, aggregate execution ledger, legacy/pre-independence research, or other-role semantic state was used.

Sequence 89 left a specific missing composition: a real self-improvement system with **EXPLORE/TRAIN -> adaptive TUNE/selection -> frozen CERTIFY with candidate-local anytime-valid evidence -> untouched OUTER/TEST**. HarnessFix had clear adaptive validation and a final held-out test, but no separate statistically valid certification surface between them.

## Primary update — LOGOS specifies the missing four-surface composition at paper-contract level

Primary source: Ichikawa et al., `LOGOS: A Living Logic for AI Agent Teams That Evolve With Humans`, arXiv:2607.10878v1 (2026-07-12).

The LOGOS protocol is the closest source found so far to the exact sequence-89 target.

### 1. Proposal / EXPLORE is isolated

The skill/self-evolution loop uses proposal examples only to construct candidate changes. The paper explicitly states that proposal data are distinct from optional candidate-selection data, final-gate data, and report holdouts.

### 2. Multi-candidate TUNE/selection is separate

When more than one candidate is generated, a separate selection split chooses the candidate. This means the adaptive search/ranking surface need not be the same surface used to certify the selected artifact.

### 3. Final CERTIFY is frozen before evidence is consumed

After selection, a disjoint final gate decides acceptance. The formal contract is stronger than a threshold gate:

- the proposal and candidate-selection rule must be fixed before the final gate stream begins;
- final-gate examples and per-example failures must remain hidden from the proposer;
- paired differences must be bounded or normalized;
- bets must be predictable from past gate information only;
- sequential claims require fresh i.i.d. gate samples, replacement sampling from a fixed pool, or otherwise a fixed-sample evaluation without a sequential claim.

The optional gate uses separate e-processes for gain and regression, converts wealth to p-values by Ville's inequality under the declared assumptions, and combines gain/regression/optional safety through an intersection-union rule. This directly supplies the candidate-local anytime-valid CERTIFY layer that was absent from HarnessFix.

### 4. A third OUTER/report holdout is stated to be outside proposal, selection, and adoption

LOGOS explicitly states that reported before/after numbers use a **third report holdout** not used for proposal, selection, or adoption. Appendix G likewise says self-evolution uses disjoint proposal, optional selection, final-gate, and report sets.

This is the first primary source in the current frontier that specifies all four surfaces in one self-evolution protocol:

1. proposal / EXPLORE,
2. optional selection / TUNE,
3. final gate / CERTIFY,
4. report holdout / OUTER.

The stronger sequence-89 requirement remains only partially verified: the paper explicitly excludes report-holdout use for proposal, selection, and adoption, but there is no public executable path in this run proving zero report-holdout use by rollback, routing, stopping, recovery, or hidden external scripts.

## Long-horizon false-adoption accounting is also specified

LOGOS does not stop at a per-candidate gate. Across candidate decisions it routes composite p-values through a LORD-style online ledger. The paper is unusually explicit about the statistical boundary:

- formal online control requires conditionally super-uniform candidate p-values, predictable spending, valid dependence assumptions, fresh valid candidate-level data, and no invalid adaptive holdout reuse;
- if those assumptions fail, the ledger is described only as conservative audit accounting, not as an FDR guarantee.

This is materially stronger scoped language than systems that label a counter or edit budget a global statistical budget without validating the underlying candidate p-values.

## The paper also treats gate feedback as an information channel

Each final gate emits a proposal-safe view containing decision, aggregate counts, score deltas, and hashes, while withholding task identifiers and per-example failures. The authors explicitly acknowledge that repeated aggregate feedback can still leak information.

The root policy therefore defines a gate-exposure budget over:

- maximum candidate decisions,
- maximum aggregate releases,
- maximum cumulative privacy loss,

and retires or refreshes final-gate examples after exposure, repeated selection pressure, budget exhaustion, or distribution drift.

This is a useful refinement of the four-surface model: **CERTIFY is not only a data split; its released information is itself a budgeted adaptive channel.**

## Empirical scope

The strongest clean gate-semantics result is a constructed common-candidate replay over 2,500 deterministic decisions (500 seeds × five candidate families):

- no gate: harmful adoption 0.600;
- paired gate: harmful adoption 0.000, adoption 0.200;
- anytime-valid gate: harmful adoption 0.000, adoption 0.198.

A larger 5,000-decision robustness replay preserves the qualitative ordering. These are mechanism checks under constructed candidate families, not estimates of natural proposal quality.

The harder multi-seed HotpotQA/MATH-500 cells show an important power boundary: the anytime-valid gate reports zero report-holdout regressions because it **fully rejects** under weak evidence. The paper correctly frames this as conservative error-accounted behavior, not high adoption power.

A complementary gpt-4o-mini view uses an n=20 report holdout with proposal/gate budget 28. At that scale the selected K=1 candidates were beneficial or neutral on report holdout, while the paired K=3 MATH-500 case rejected the selected candidate instead of adopting an unproven change.

## Public implementation boundary

No author/Fujitsu public GitHub repository implementing the LOGOS protocol was identified in this run. Searches by title, authors, FujitsuResearch, and distinctive protocol phrases did not recover a source-bound implementation. CatalyzeX currently exposes `Request Code` for the paper.

Fujitsu's 2026-07-13 public technology page for `Fujitsu Kozuchi Multi AI Agent Framework` describes the related safe self-evolving multi-agent technology: execution histories and human feedback generate candidate changes to prompts/skills/workflows/tools/roles, candidates are tested in an execution environment, only effective changes are reflected, important changes can require human approval, and change histories are retained. The page explicitly links the LOGOS paper. It does not publish the executable gate/ledger implementation.

Therefore the correct classification is:

**`PAPER_LEVEL_FOUR_SURFACE_COMPOSITION_WITH_ANYTIME_GATE_CODE_UNBOUND`**.

Do not promote this to executable evidence for crash-safe evaluation consumption, durable LORD state, exact paper-run replay, or zero OUTER queries before terminal reporting.

## Design update

The sequence-89 decomposition is now supported as an explicit end-to-end research protocol rather than only a composition assembled from separate papers:

`EXPLORE/PROPOSAL -> TUNE/SELECTION -> frozen CERTIFY/e-process -> OUTER/REPORT`

For long-running self-improvement, append two additional contracts:

- **bounded certification feedback:** gate outputs themselves must have a release/exposure budget;
- **cross-candidate accounting:** only valid candidate-level p-values may enter online FDR/FWER accounting, and the ledger must survive restart without refund/reset.

The remaining gap is engineering evidence, not conceptual structure: no public executable LOGOS implementation was found, and the stronger zero-use OUTER contract across rollback/routing/stopping/recovery is not source-code verified.

## Source-bound artifact

Machine-readable contract: `research_workers_clean_g1/self_improvement/logos_four_surface_anytime_contract_2026-08-28T100524_JST.json`.

Primary paper: `https://arxiv.org/html/2607.10878v1`.

Related Fujitsu public technology page: `https://global.fujitsu/ja-jp/technology/research/article/topics/202607-multi-aI-agent-framework`.

## Exact next action

Search for a **public executable implementation** of the LOGOS/MAAF protocol or another open-source self-improvement system with the same four-surface composition. Require source-bound evidence that:

1. candidate generation/selection state is immutable before CERTIFY begins;
2. certification evidence is candidate-local anytime-valid under the actual sampler, not only by label;
3. cross-candidate statistical state is durably reconstructible across restart and cannot be refunded/reset by crash;
4. OUTER/report query count is provably zero before terminal reporting and OUTER is unused by promotion, rollback, routing, stopping, and recovery;
5. immutable candidate identities and complete proposal/evaluation chronology are retained.

Revisit the Harn provider-operation/hypothesis bridge only if relevant public paths change materially. Frontier remains nonempty.
