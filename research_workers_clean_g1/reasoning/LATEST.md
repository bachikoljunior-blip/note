# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T1401JST.md`
Current invocation chain: `2026-08-27T1401JST.md` -> `2026-08-27T1300JST.md` -> `2026-08-27T1202JST.md` -> `2026-08-27T1103JST.md` -> `2026-08-27T1007JST.md`
Earlier predecessor chain remains in immutable checkpoint history; read only the minimum needed for an unresolved item.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation start was `2026-08-27T13:57:07+09:00`; checkpoint observation was `2026-08-27T14:01:59.446090+09:00`. Chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 directly at `anetigone/cssc@f40a3d3aa3054f4b07bb17e3fe5aa6d55e3d28f8` through the full `StructuredController` path when exact repository materialization/execution becomes available; then run the immutable-consumption-edge oracle on the same fixture.
2. Preserve causal-journal/recovery and epsilon=0 semantic-equivalence gates; `epsilon>0` remains forbidden until these gates pass.
3. Materialize pinned OPA and Regorus and run the frozen deterministic Rego Tier-0 fixtures before seeded generation.
4. Refine repository-scale memory around `STORE_GUIDANCE -> STAGE_VERIFIED_LEMMA -> QUERY_STAGED_LEMMA -> ADMIT_REUSABLE_LEMMA -> optional DEMOTE_REUSABLE_LEMMA`.
5. Instrument actual future-task lemma use using proof-term/environment dependencies plus tactic-explicit `rw`/`simp`; retrieval and same-task use are not cross-task reuse.
6. Estimate candidate value counterfactually under fixed prover/config/compute where feasible; include solve delta, proof/inference effort, tokens, Lean execution, wall-clock, retrieval/context/index overhead and lost-solve pollution.
7. Evaluate chronologically: a lemma may receive utility/reuse credit only from tasks that occur after the lemma exists. Preserve a same-compute cross-task-sharing-disabled control.
8. Treat admission as marginal to the current admitted set; redundancy means static intrinsic rankings can become stale after every admission.
9. Search for modern Lean/Coq/Isabelle systems with actual cross-task dependency-use logs plus dynamic promotion/demotion from observed downstream utility, and for multi-lemma causal-credit methods.
10. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and exact-artifact gates.

## Newest synthesis

- **C479:** TABLEAUX 2023 `Lemmas: Generation, Selection, Application` provides a strong prover-specific utility target: counterfactually reprove the goal with candidate lemma `L` and score the normalized reduction in inference steps. In SGCD proofs newly found after supplying selected lemmas, 63–96% of distinct proof subterms originate from those lemmas. This supports counterfactual marginal utility plus actual-use instrumentation rather than retrieval-count admission.
- **C480:** HOL Light lemma mining gives an explicit historical downstream-use metric `U(i)` (recursive future uses), combines it with proof/dependency effort `D(i)` and size `S(i)`, recomputes qualities after every admission, and evaluates chronologically in a `fully-honest` protocol. Fully-honest success rises 61.7% -> 64.8%. This supports marginal recomputation and anti-future-leakage rules, but it mines existing proof-graph nodes rather than LLM-generated Lean lemmas.
- **C481:** LEGO-Prover behavioural audit finds direct single-task use but essentially zero cross-task direct reuse despite 121/64/75/583 retrieved unique lemmas in prompts; the lone reported name-reuse event was removed from the final verified proof. Retrieval/use/reuse/counterfactual utility must therefore remain distinct metrics.
- **C482:** QuickSpec+Vampire induction shows lemma visibility is non-monotonic: the same strategies lose 10, 6 and 1 proofs after adding lemmas, and the one trained-strategy loss involved 459 conjectured lemmas; proof time also often rises. Default global admission therefore has a real search-pollution cost.
- Admission/demotion rule V0 is now specified as a design hypothesis: admit either on replicated unique future-task utility or a one-sided 95% lower confidence bound of positive marginal net utility against both query-only staging and equal-compute no-cross-task controls; demote if a one-sided 95% upper bound becomes nonpositive or compatibility/pollution regressions dominate benefit. Exact normalization and opportunity-window calibration remain open.
- Minimal Lean instrumentation V0 now records eligibility/exposure, proof-term/environment dependency, explicit `rw`/`simp` reference, guidance-only exposure, outcome/cost, paired counterfactual result when run, and successor/integration compatibility when applicable.
- C263 full-controller execution remains open; no randomized policy data were collected.

## Exact continuation

1. Run C263 unchanged at `f40a3d3...` when exact materialization is available, then run the immutable-consumption-edge oracle on the same fixture.
2. Run frozen OPA/Regorus Tier-0 deterministic fixtures with exact artifact identities before seeded generation.
3. Refine admission V0 into a weight-free/Pareto-safe decision rule and define `eligible future opportunity` precisely.
4. Search modern proof assistants for actual downstream-use-count + dynamic admission/demotion evidence; retain the HOL Light result as historical precedent only.
5. Search multi-lemma causal-credit methods and library-pollution controls.
6. Specify a minimal immutable Lean use-event schema and chronological evaluator without enabling randomized controller collection.
7. Keep the frontier nonempty; this is not global completion.

`2026-08-27T1401JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
