# Self-improvement checkpoint — sequence 98

Created: 2026-08-28T18:02:53.521808+09:00

Frozen semantic control tuple: note main `7e893018d47b993fe17b3bdad4768d8d8eca4d3f`, root control revision 15, self_improvement config revision 7, role config blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.

## New source-bound finding: a useful partial terminal-OUTER crash protocol

At exact public revision `323ed3b5e1236b99544827f9c6b25820dc5aab8f`, `skillberry-ai/cap-evolve` is a real executable optimization/evaluation harness rather than only a library substrate: `core/pyproject.toml` wires `cap-evolve = cap_evolve.cli:main`, and the CLI sequences phase skills with run/resume/observability surfaces.

Its optimization loop repeatedly evaluates and gates candidates on VAL. `gate.decide` refuses acceptance gating on any split other than VAL. After search, `finalize()` evaluates the already-selected best candidate on a separate TEST split and, optionally, the seed baseline on that same TEST inside one finalize attempt.

The important crash mechanism is `RunDir.begin_test_attempt()`. The older seal-on-success design checks the TEST seal first and commits it only after the final result is written. That alone cannot distinguish a crash before TEST scoring from a crash after TEST was already observed but before `commit_test()`. The current implementation therefore also scans `rollouts/test/*.json` at the beginning of a finalize attempt. If any persisted TEST rollout exists while the seal is still uncommitted, a retry is refused as a second look unless the explicit `CAPEVOLVE_ALLOW_TEST_RESCORE` override is enabled. The repository test `core/tests/test_test_seal_rescore_guard.py` pins three distinct states: retry before any TEST rollout is honest and allowed; retry after any TEST rollout is refused; the normal single finalize may still score `FINAL` and `FINAL_seed` before one final seal commit.

This is a meaningful improvement over a pure post-success seal: a crash after locally persisted TEST evidence but before seal commit no longer silently turns into a second headline look.

## Exact remaining crash gap

The guard becomes authoritative only once at least one TEST rollout has reached local durable storage. `evaluate_candidate()` calls `reserve_test()` and then invokes the adapter/runner; the audited path does not write a stable content-bound logical evaluation intent before that remote/stochastic work begins. Therefore `provider/evaluator accepted or completed → controller dies before first local rollout` remains indistinguishable from `never dispatched`, unless the adapter/provider independently supplies idempotency or reconciliation.

There is a second tradeoff. Once even one TEST rollout is persisted, a later finalize attempt is rejected wholesale. That preserves honesty but does not resume a partially completed TEST. In other words, cap-evolve chooses fail-closed terminality over availability at this boundary. A stronger design would pre-reserve one logical outer attempt, write immutable per-case/trial outcomes under that identity, and on restart reconcile or execute only the missing cells without creating another logical look.

The stronger crash-state chain is therefore:

`OuterEvaluationIntent(pre-dispatch, candidate/evaluator/request-bound) → per-cell immutable outcomes → restart reconciliation/missing-cell completion → deterministic aggregate final result → terminal seal`.

Provider acceptance before the first local outcome additionally needs stable provider idempotency/reconciliation; a local attempt record alone cannot make a non-idempotent external evaluation exactly-once.

## Why this is still not a mechanically terminal fourth OUTER

The TEST seal is strong only within an individual `RunDir`. Creating another run creates fresh run-local state/splits, so the audited mechanism does not establish a global once/cache-only lockbox across repeated research campaigns or generations.

The Claude plugin protection is also primarily anti-poisoning, not non-disclosure. `deny_sealed_edits.py` blocks Edit/Write/MultiEdit/NotebookEdit to `splits.json`, TEST rollouts, and answer-key-like files. `hooks.json` does not register that guard for Read or Bash. Thus the plugin proves that a self-editing optimizer cannot use those write tools to rewrite the held-out artifacts, but it does not structurally prove zero pre-final read/query access. This is a scope limitation, not evidence that the normal optimizer actually reads TEST material.

Finally, the second-look refusal itself has an explicit `CAPEVOLVE_ALLOW_TEST_RESCORE` escape hatch. That makes the default protocol fail-closed and auditable, but not an irreversible cache-only authority.

## Statistical surface

The audited VAL gate is still fixed-look. Its paired mode accepts when mean per-task candidate-minus-current delta exceeds `k * SE(delta)` (default `k=1.0`); if the paired SE collapses to zero it warns and falls back to accepting any positive delta. The hill-climb screens candidates repeatedly on the same VAL surface. No candidate-local confidence sequence/e-process or replay-derived candidate-crossing online error ledger is present in this audited gate path. This statement is intentionally scoped to the path inspected, not a repository-wide impossibility claim.

## Contrast checked this run

At `ethan-haas/self-improving-agent-harness@942d5d33da5ea63ea269995dc6f355dfded2d975`, the host runner invokes `Invoke-HoldoutScoring` as tier 6 of candidate promotion and rejects ordinary candidates whose holdout delta is below +0.02. That holdout is therefore consumed for promotion in the audited path and is not a fourth reporting-only OUTER.

For Gauntlet, the public `Tyler-R-Kendrick/epoch` main branch remains at the previously audited `f03a7b6fecc23e2478df23b8438113a904ec757b`. A targeted public PR search for `gauntlet` found the original landing PR and no newer matching Gauntlet repair PR, and the repository publishes no GitHub releases. This is only a scoped search result; it is not proof that no differently named branch/PR contains relevant work.

## Control-head drift termination

After the semantic freeze and the public-source work above, a SHA-only freshness check observed note main at `7dc93cb490359ce2c0c16fa1ec47907b31aba097`, different from the frozen `7e893018d47b993fe17b3bdad4768d8d8eca4d3f`. Under the frozen role policy, no newer control semantics are adopted or interpreted in this invocation. Semantic exploration stops here and the result is checkpointed under the frozen tuple.

## Nonempty frontier / exact next action

On the next invocation, first resolve fresh control. Then search for a public self-improver/evaluation service that combines cap-evolve-style post-score consumption detection with a pre-dispatch logical evaluation WAL and cell-level resume/reconciliation, while enforcing OUTER non-readability/non-queryability across runs. In parallel, search cap-evolve issues/PRs for the explicit second-look incident and any planned durable-attempt/resume implementation. If absent, construct a kill-point matrix over: before dispatch; provider accepted; first local outcome; partial cells; aggregate `final.json`; and terminal seal commit.

Contract: `research_workers_clean_g1/self_improvement/terminal_outer_crash_contract_2026-08-28T180253_JST_cap_evolve.json`
