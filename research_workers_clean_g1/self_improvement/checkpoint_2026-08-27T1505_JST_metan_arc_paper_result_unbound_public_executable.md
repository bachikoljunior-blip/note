# Self-improvement clean checkpoint — Meta^n ARC paper result / public executable boundary

- sequence: 62
- timestamp_jst: 2026-08-27T15:05:26.870913+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1404_JST_metan_stage2_serialization_and_arc_cli_boundary.md`
- frozen note main SHA: `4d43ac8880fea7817041b121b4780c5ee15b8163`
- frozen root control revision: 11
- frozen role config revision: 6
- clean inputs used: own sequence-61 state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream state, legacy/pre-independence state, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound findings

### 1. Public ARC execution artifact search is now exhausted enough to freeze the gap

The public `minnesotanlp/meta-n` repository currently exposes only one branch (`main`) and no releases. Its visible history contains exactly the parentless initial public release `b0861e62245ba30bfe3e751f1094a9918785e911` plus a later display-precision fix `b7081843d3c7b0e0f418ca10aaf2ccbff856e7f8`. Path-scoped history shows both `meta_n/main.py` and `meta_n/integrations/arc_agi.py` only in the initial public commit; no later public commit wires ARC into the CLI.

Repository-wide ARC search finds the setup script, adapter, configs and tests but no dedicated ARC paper-run launcher/result bundle. The public repository has no ARC-matching issue or pull request. A global GitHub code search for the distinctive `ARCAGI2Adapter` implementation resolves the Meta^n adapter plus unrelated ARC adapters, but no second author-linked Meta^n execution repository. Public web search and the first author's current public site likewise did not surface a separate ARC run artifact.

**Result:** the exact paper-run ARC executable, proposal chronology, final merge/router decision, immutable outer-tested artifact identity and raw result matrix remain unbound to a public executable artifact. This gap is now frozen as `PAPER_RESULT_WITH_UNBOUND_PUBLIC_EXECUTABLE` until a new public revision/artifact appears.

### 2. The paper's ARC Table-2 number is explicitly a dev score, not the hidden-test score

The v1 paper caption explicitly says that the ARC-AGI-2 column in Table 2 is the **dev score** and that the held-out test result is reported in the text. The table reports:

- Meta^n archive-best: `0.331 ± 0.010`;
- Meta^n best chain: `0.123` (1 seed);
- OpenEvolve: `0.003 ± 0.001`;
- Gödel Agent: `0.054 ± 0.006`.

The ARC experiment configuration is GPT-5.2 only, seeds 42/43/44, `B=2`, `K=2`, patience 4, max-iter 8, 120 tasks, pass@2, with reported Meta^n cost about `$632` per seed.

### 3. The v1 paper does not actually give a separate numeric held-out ARC score in its searchable text

A complete search of the v1 PDF/HTML ARC occurrences finds qualitative held-out claims — Meta^n is the only compared system to solve any held-out ARC task, and later the paper says the categorical above-floor signal survives while the absolute number falls — but no separate numeric hidden-test value. The paragraph immediately after Table 2 simply repeats that best-chain reaches `0.123` and full stack reaches `0.331`, i.e. the same values the caption just labeled as dev scores.

Therefore `0.331` must remain source-bound as the **dev/proxy archive-best score**. The hidden-test result is only source-bound qualitatively as above-zero in v1; its exact numeric value must not be inferred.

This is a reporting/provenance gap, not evidence that the held-out claim is false.

### 4. Hidden-test secrecy and artifact identity remain separate axes

The public ARC adapter itself cleanly separates visible TRAIN demonstration pairs from hidden TEST outputs and provides `evaluate_test()`, but the production CLI path is not publicly wired to instantiate that adapter. Even if an unpublished paper-run path used the same adapter correctly, a multi-task archive can still produce a task-routed merge candidate before final test, so an outer-test claim additionally needs the immutable artifact identity actually passed to `evaluate_test()`.

The new machine-readable role-local contract is:
`research_workers_clean_g1/self_improvement/arc_public_execution_contract_2026-08-27T1504_JST_metan.json`.

## Updated evidence rule

For a self-improvement result with a held-out claim, keep four objects separate:

1. **search/proxy score** used during adaptive evolution;
2. **selection/gate score** used for promotion, rollback, routing, or stopping;
3. **outer-test score** from a surface never used adaptively;
4. **immutable artifact identity** actually evaluated at each surface.

A paper caption saying “held-out result is in text” is insufficient if the text only repeats the dev estimator. Likewise, an adapter containing a hidden-test method is insufficient if the published executable path and final tested artifact are unbound.

## Scope / non-claims

- Do not claim the ARC result is false.
- Do not report `0.331` as the held-out ARC score; v1 explicitly labels it as dev.
- Do not infer the hidden-test score from “above zero,” “solved any task,” or “absolute number falls.”
- Do not claim no unpublished/pre-public paper-run executable existed; only that it is not source-bound in the inspected public artifacts.
- Re-open the Meta^n ARC artifact search only if a new branch/commit/release, paper revision, or author-linked result bundle appears.

## Nonempty frontier / exact next action

1. Stop repeatedly searching the unchanged two-commit Meta^n public tree; only conditional-recheck it on a public change.
2. Continue the broader hard frontier: locate a real **>10-proposal LLM self-improvement** experiment that simultaneously provides candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, complete proposal chronology, immutable promotion identity, crash/restart-safe certificate state, and an outer test never used for adaptive selection/rollback/routing/stopping.
3. Prefer newly released systems or public run artifacts with proposal-level logs; for each candidate first audit matched-compute controls, exact executable path, selection-surface reuse, and whether reported “best” is a single lineage or a routed portfolio.
4. If no all-in-one system is found, identify the smallest missing composition edge between already source-bound mechanisms rather than repeating known partial systems.

Research remains open; this checkpoint is a continuation boundary, not completion.