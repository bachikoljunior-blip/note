# self_improvement checkpoint — sequence 96

- created_at: 2026-08-28T16:02:51.857961+09:00
- generation: clean_g1
- role: self_improvement
- frozen note main SHA: `ee0312717fe6076a358190859ec62ecd696c3079`
- frozen control revision: 15
- frozen role config revision: 7
- frozen role config blob: `c5d194b341a70356da196cfb88636ab41fc1bc9f`
- control head later drifted to `5b43f5c35ec8574d7612e1656c220bb3df5561c0`; per freeze barrier, no newer control semantics were read or adopted in this invocation.

## Clean inputs

Used only the role-local clean checkpoint sequence 95, role-local sanitized mechanical feedback, and public sources. No O, other-worker, downstream, legacy-semantic, or shared-control semantic context was used.

Mechanical feedback remains acknowledged: new candidate/source identifiers are source-qualified rather than bare C-number labels.

## Primary update: `epoch-gauntlet-loop`

Public source: `Tyler-R-Kendrick/epoch` at exact revision `f03a7b6fecc23e2478df23b8438113a904ec757b`.

This is the closest newly verified public *durable improvement control plane* in this scan. It is not an autonomous self-improvement result: a host agent supplies open-ended proposals while the Gauntlet CLI is the deterministic authority/control plane. That scope distinction is essential.

### What is already integrated in one executable source tree

1. **Materialized, isolated candidate identity.** Candidates live in isolated Git worktrees; `CandidateV1` binds candidate ID, experiment ID, branch, exact commit, artifact digests and optional environment identity.
2. **Frozen normative/evaluation surfaces.** Spec, policies, schemas, sealed promotion data, evaluators and promotion/effect kernels are candidate-forbidden surfaces. Evaluator-seam changes require a separate governance path and cannot self-approve.
3. **Three distinct evaluation surfaces.** Search is builder-visible; calibration is for evaluator reliability/bias; promotion uses a sealed held-out path unavailable to candidate builders and frozen evaluator versions.
4. **Typed paired evidence.** `EvaluationResultV1` binds candidate, evaluator/version, split and metrics; `ComparisonV1` binds baseline candidate, challenger candidate, paired deltas, protected regressions, seed/method and timestamp.
5. **Event-sourced durable state.** ActiveGraph is the scheduler/event store/replay engine. Mutation is through durable emitted events; strict replay is available and verification itself appends no events.
6. **Exact promotion identity.** `PromotionPlanV1`/`PromotionDecisionV1` bind the exact candidate commit/artifact digests and gate evidence. Promotion is a fail-closed saga across Git, ActiveGraph, artifacts and decision records; partial settlement is compensated or marked for reconciliation rather than pretending cross-store atomicity.
7. **Write-ahead effect authority.** `ActionIntentV1` must reach committed before an effect executes. It binds canonical input digest, operation/tool contract, scopes, action/effect class, idempotency/reconciliation strategy, spec/policy/evaluator/environment digests, budget and approval requirements.
8. **Unknown external outcomes do not blind-retry.** Non-idempotent `outcome_unknown` goes to reconcile; effect and release are separate from local promotion. Release requires explicit human/governance authority for outward effects.
9. **Non-destructive rollback.** Rollback creates compensating history rather than erasing the accepted lineage.

### The remaining statistical gap is source-confirmed, not inferred from docs alone

`statistics.py` implements fixed-look classical procedures:

- paired binary: SciPy `binomtest` with Wilson interval;
- paired continuous: Student-t confidence interval;
- percentile bootstrap with recorded seed and minimum sample count;
- optional `none` / Bonferroni / Holm multiple-comparison correction;
- promotion predicate: target lower CI must exceed the practical-effect floor, while every protected-regression upper CI stays below budget.

Missing/underpowered/contradictory evidence is explicitly inconclusive rather than promoted, which is good. But there is no confidence sequence/e-process in the inspected code, and no candidate-crossing online FDR/FWER state. Therefore a long adaptive campaign that repeatedly inspects the same promotion surface is not protected merely because each fixed-look comparison has a confidence interval.

### The outer-evaluation topology also remains incomplete

The public evaluation command family exposes `search`, `calibrate`, and `promotion`. `release` is a separate authority/effect decision, not a fourth untouched statistical evaluation. The sealed promotion set is consumed to decide promotion, so it cannot simultaneously be the terminal OUTER lockbox sought in the current frontier.

This gives a clean four-surface target:

`EXPLORE/search -> evaluator CALIBRATION -> adaptive CERTIFY/promotion -> terminal OUTER`

Gauntlet currently implements the first three, with strong identity/isolation/durability, but not the fourth.

## Secondary implementation contrast: `am-workbench-prompt-evolver`

Public source: `StrategicMilk/AM-Workbench` at exact revision `e548fee3ff5e077eec3c043b6c8f21e2e178492e`.

This source is useful because the same repository contains both:

- a real automatic prompt-evolution subsystem that generates variants, routes traffic, evaluates, shadow-tests, promotes and rolls back; and
- a separate Workbench metadata spine whose JSONL is explicitly the fsync'd source of truth and whose SQLite index is rebuildable.

However the inspected prompt-evolver path does **not** use that append-only spine as its evidence authority. Prompt variants are persisted in mutable `prompt_variants.json` via temp-file replace; write failures are logged. The statistical gate is an ordinary two-sample t-test (or permutation fallback) plus Cohen's d after minimum trials, followed by a benchmark threshold and a shadow test whose production/candidate observations are stored in separate mutable arrays/counters and promoted by raw quality/latency/error thresholds.

This is an important implementation lesson: **having an append-only evidence system elsewhere in the architecture does not make self-improvement evidence durable or replay-derived unless the promotion path itself treats that log as the authority.**

## Smallest source-level integration seam now identified

The missing composition is no longer abstract. The smallest credible seam is:

1. retain Gauntlet's isolated worktrees, candidate/evaluator/split digests, frozen promotion surface, promotion saga and write-ahead effect authority;
2. make immutable ordered `EvaluationResultV1`/`ComparisonV1` events the sole statistical authority;
3. derive candidate-local anytime-valid confidence/e-process state from those ordered events, never from mutable counters;
4. derive candidate-crossing LORD++/SAFFRON/e-LOND-style state from the same event stream, with no wealth/refund reset across crash/restart;
5. bind each promotion decision to the evidence-log frontier digest plus exact statistical-policy digest;
6. add a fourth OUTER namespace inaccessible to evaluate-promotion, promotion, rollback, release, routing, stopping and recovery, and allow it exactly once or cache-only after final artifact selection.

Provider/evaluator WAL remains a separate issue when evaluators invoke remote providers. Gauntlet's default command evaluators are local/denied-network; its effect executor already has the relevant write-ahead/reconciliation semantics for outward effects.

## Machine-readable contract

`research_workers_clean_g1/self_improvement/durable_improvement_control_plane_contract_2026-08-28T160251_JST_epoch_gauntlet.json`

## Falsification plan

- Repeated-look null calibration against Gauntlet's fixed-look promotion statistics; quantify false promotion under adaptive peeking.
- Crash/restart after each comparison event and before promotion; any derived e-process/online-FDR state must replay identically from genesis with no spent-budget refund.
- Reuse the same stable evaluation ID with a different candidate/evaluator/split digest; require semantic conflict, never deduplicated replay.
- Attempt any pre-final query of a proposed OUTER namespace from promotion/rollback/release/stopping/recovery; require structural denial plus durable leakage evidence.

## Frontier

Nonempty.

Exact next action: inspect the actual `epoch/gauntlet-loop` evaluation write path and effect executor for stable evaluation IDs and crash boundaries, then determine whether `ComparisonV1` event chronology can serve directly as the immutable authority for derived candidate-local anytime-valid evidence plus candidate-crossing online error control. In parallel, search current public self-improvers for an already-implemented fourth terminal OUTER surface. If none exists, source-bind the minimal Gauntlet extension contract and real crash/leakage tests rather than inventing results.
