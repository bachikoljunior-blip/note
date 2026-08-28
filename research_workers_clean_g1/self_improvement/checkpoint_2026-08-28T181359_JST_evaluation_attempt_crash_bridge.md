# self_improvement checkpoint — sequence 99

Created: 2026-08-28T18:13:59+09:00

## Frozen control tuple

- note main SHA at semantic barrier: `6b4ee5c48a7e2987b57c5c05751657fc8738e97c`
- root control revision: `15`
- self_improvement role config revision: `7`
- role config blob: `c5d194b341a70356da196cfb88636ab41fc1bc9f`
- clean inputs used: own sequence-98 state, public sources, own mechanical feedback only

A later SHA-only control-head observation returned `60210482eb5e8bd4ac5bef60fc21880ee0cf321d`, so semantic exploration stopped under the frozen-control rule. The findings below were obtained before that stop and are checkpointed without adopting newer control semantics.

## Material update

The crash-safe OUTER-evaluation frontier is now more concrete. Four public systems expose complementary pieces, and one gives a direct counterexample to a superficially "certify once" API:

1. **cap-evolve** (`skillberry-ai/cap-evolve@323ed3b5e1236b99544827f9c6b25820dc5aab8f`) has post-score consumption detection. Current `RunDir.begin_test_attempt()` explicitly documents the real incident that motivated it: a finalize killed by a foreground timeout had already scored TEST, retry scored TEST again, and the reported headline became the second look. The current guard scans `rollouts/test/*.json` and refuses another finalize if any TEST rollout exists while the seal is uncommitted. PR #366 records the same real-run incident. Open #361 documents that direct `harness.evaluate_candidate(split="test")` can still query TEST outside finalize and brick the later honest finalize; open #341 documents that the rescore override promises durable disclosure but currently records none.

2. The exact `evaluate_candidate()` write path shows the remaining hard-kill gap. TEST is only reserved before evaluation. `adapter.run_target`, `run_batch`, or `run_trials` executes before `_persist_trial()` writes `<task>__<tag>__t<k>.json`. Therefore provider/evaluator acceptance or completion followed by controller death before the first local rollout leaves no consumption evidence and is indistinguishable from never-dispatched. Retry is then allowed. In batch modes this uncertainty window can cover a whole returned batch. Once even one local rollout exists, the guard protects honesty by refusing the whole next finalize, but there is no missing-cell continuation.

3. **Koboi** (`hedypamungkas/koboi-agent@d9356933ad0b11ab16dbb14ed449edd0580cb09c`) supplies the missing *shape* of a pre-dispatch marker: `StepJournal.record_step()` eagerly commits a `running` row before an LLM call, and resume converts surviving running rows to interrupted. Its crash-recovery benchmark rebuilds a fresh agent and re-executes only missing tool calls after a simulated mid-turn interruption. This is not yet enough for evaluation authority: the benchmark tools are deliberately idempotent, the benchmark says literal cross-process SIGKILL is follow-up work, the journal identity is session/turn/step rather than a semantic request digest/provider token, and the server Idempotency-Key registry is in-memory TTL only.

4. **Auto-Research-AI-Scientist** (`cxcscmu/Auto-Research-AI-Scientist@7a6dbc8543172042d7be4f14b39f8f4c0abd6c92`) is an especially useful negative example. Its README/Runbook promise inner-CV-only search plus a separate outer certification command, frozen source hashes, fresh evaluator subprocesses, and `holdout_certification.json`. But `CampaignRunner.certify()` calls `self.evaluator.holdout(workspace)` **before** checking whether that certificate already exists. Only after the fresh holdout query does it compare against the old certificate. `tests/test_runner.py` explicitly invokes `certify()` twice and accepts matching source hashes. Thus its second `certify` is not cache-only: the terminal artifact exists, yet OUTER is queried again before cache/reuse logic runs.

5. **Swiss-AI evals-post-train** (`swiss-ai/evals-post-train@72409217c6c9eeefc447935edcc42af80fb72712`) demonstrates a practical missing-cell/task continuation pattern. Its graceful launcher reconstructs a `COMPLETED_MAP` from result directories/requested-task manifests, computes `MISSING_TASKS`, and launches only missing groups. `--force_tasks` explicitly opts into re-evaluation. This is useful recovery plumbing, but it is not a terminal holdout authority and has no content-bound pre-dispatch evaluation WAL in the inspected path.

## Six-boundary kill matrix for cap-evolve

| kill boundary | durable state today | restart behavior | assessment | required stronger rule |
|---|---|---|---|---|
| before evaluator/provider dispatch | TEST seal checked/reserved; no rollout; no logical eval intent | retry allowed | safe only if dispatch truly never occurred | persist content-bound `OuterEvaluationIntent` before dispatch |
| remote accepted/completed, before first local rollout | no rollout, no outcome authority | looks like never-dispatched; retry allowed | duplicate/second-look risk | stable logical cell ID + provider idempotency or `UNKNOWN → reconcile` |
| after first local rollout | one or more TEST rollout JSON files | next finalize refused by default | honesty fail-closed, availability lost | resume same attempt from immutable cells |
| after partial cells | some rollout JSON files | whole finalize refused | no second look, but missing cells stranded | deterministic completed/missing partition; run only provably missing cells |
| after final result write, before seal commit | rollouts exist; final artifact may exist; seal uncommitted | re-score attempt is refused by rollout detection | should reconcile/commit without evaluator access | derive/verify final from cells, then finish terminal transition |
| after seal commit | committed TEST-used state + result | normal second finalize refused | strongest current in-run terminal state, but override/out-of-band query holes remain | core capability gate + durable override disclosure or no override |

## Minimal composition now justified by source

`candidate/evaluator/dataset/split freeze → durable content-bound OuterEvaluationIntent → stable per-cell IDs → provider idempotency or UNKNOWN/reconciliation → immutable cell outcomes → missing-cell-only resume → deterministic aggregate/certificate → terminal seal → later certify is cache-only before any evaluator access`.

The critical ordering rule exposed by Auto-Research is simple and testable: **look up terminal certificate/attempt state before calling the holdout evaluator**. A second `certify()` must have evaluator invocation count exactly zero for that call. Checking equality after re-evaluation is already too late.

## Falsification plan

A source-complete implementation should survive real cross-process SIGKILL at all six boundaries. Tests should additionally reject generic `evaluate(test)` outside the terminal authority, reject semantic digest changes under a reused attempt ID, prove partial restart calls only missing cells, and prove a second certificate read never calls the evaluator. If any rescore override remains, its disclosure event must be durable before the second dispatch and bound into every report surface.

## Scoped negative result

In the targeted public source/issue search performed before the frozen-control drift stop, I did **not** find one audited self-improver/evaluation service that combines all of: content-bound pre-dispatch evaluation WAL, provider reconciliation, per-cell partial resume, and mechanically cache-only/non-queryable OUTER. This is a scoped search result, not an impossibility claim.

## Nonempty frontier / exact next action

On the next fresh-control invocation, first inspect newer branches/PRs of `cxcscmu/Auto-Research-AI-Scientist` for a fix that checks the existing certificate **before** `evaluator.holdout()` or adds a durable certification-attempt state. Then search public evaluation services/workflow engines for a content-bound pre-dispatch evaluation/cell WAL with missing-cell resume. Prioritize a system where an instrumented second `certify` call proves evaluator invocation count stays exactly one total and generic evaluation APIs cannot query OUTER outside the terminal authority. If no integrated implementation appears, build a minimal executable reference state machine from the six kill points above and test it with actual cross-process SIGKILL.
