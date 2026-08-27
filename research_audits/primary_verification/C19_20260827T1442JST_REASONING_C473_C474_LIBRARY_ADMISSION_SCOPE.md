# Primary verification — C19 reasoning C473/C474 library-admission evidence scope

Observed: 2026-08-27T14:42+09:00
Verifier role: `primary_source_verifier`
Frozen note control/source SHA for this invocation: `5fcfb917e2b8d0db5600b30a35898c6fb128bad6`
Frozen root control revision: 11
Frozen verifier config revision: 4

## Source-qualified candidates

- namespace: `reasoning`
- sealed C19 artifact: `research_workers_clean_g1/reasoning/2026-08-27T1202JST.md`
- artifact blob: `eac14bfb057c3b7b8aa4219305a69cd12d366dfd`
- candidate ids: `C473`, `C474`

## C473 — MathlibLemma

The current official MathlibLemma repository and the current paper abstract support the worker's central facts:

- benchmark: `4,028` non-trivial type-checked Lean statements;
- screened proof library: `1,506` Lean-checked proofs;
- the paper describes those 1,506 as passing a proof-bypass screen;
- only a small curated pilot subset is described as merged into Mathlib, so expert-library acceptance applies to selected outputs, not the whole 1,506-proof library.

The official repository currently lists representative merged Mathlib PRs including `#32170` (`gronwallBound_mono`), `#32167` (`Kernel.restrict_const`), and `#31985` (`centralMoment_congr_ae`). This is direct evidence that at least selected generated discoveries can clear Mathlib's external contribution process.

**Scope:** this does not measure downstream reuse, retrieval value, proof-round reduction, repository-closure contribution, or future-task utility of all staged proofs. Therefore the worker's distinction between `STAGE_VERIFIED_LEMMA` and a stronger future-utility-based admission action remains justified; kernel checking alone is not evidence that every generated declaration deserves default durable retrieval.

## C474 — Proof-Refactor

The primary project site and paper support the numerical rubric results:

- Putnam2025, 12 problems: `Reuse` score `4.00 -> 4.29`;
- PutnamBench, 96 problems: `Reuse` score `3.84 -> 4.24`.

However, the worker wording `human/rubric Reuse scores` should be tightened. These table entries are **scores from the paper's separate LLM-as-a-judge rubric**, not per-dimension human reuse ratings. The paper's human check is a different validation: 28 valid problems were reviewed with the same rubric, and the automatic judge agreed with the human review on which of the two refactorings was better for `75.0%` of sampled theorems. The paper does not report a human `Reuse=4.00->4.29` or `3.84->4.24` table.

The paper also explicitly limits the experiment to self-contained single Lean files whose environment only adds new declarations; it does not test project/library-scale future dependency reuse. Therefore the numerical `Reuse` gain is evidence that refactored artifacts look more reusable/use helpers better under the rubric, **not evidence that future unrelated proofs actually consume those helpers under matched compute**.

## Decision consequence

- C473: `SUPPORTED`, exact-scope only.
- C474 numerical table: `SUPPORTED`.
- C474 attribution of the table to human reuse scoring: `CORRECTED` to LLM-as-a-judge rubric; human evidence is only a 28-problem pairwise sanity check with 75% agreement.
- The synthesis `verified/reusable-looking != demonstrated future reuse` remains supported.

## Primary sources checked

- https://arxiv.org/abs/2602.02561
- https://github.com/Sequential-Intelligence-Lab/MathlibLemma
- https://arxiv.org/abs/2606.03743
- https://pelicanhere.github.io/proof-refactor-site/

Verdict: **C473 supported; C474 supported with evaluator-provenance correction.**