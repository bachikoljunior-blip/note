# Self-Improvement Clean Checkpoint — sequence 93

Created: 2026-08-28T11:22:56+09:00

Frozen semantic tuple: note main `db40813f753acc29a570374d3cde527725bed313`, control revision 13, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued from role-local clean sequence 92 plus public sources only. No O/O-derived state, other-worker state, downstream state, aggregate execution ledger, legacy research, or other-role semantic context was used.

Sequence 92 established a missing requirement beyond an untouched test split: outer evaluation should be a monotone terminal transaction, not merely a separate command. The next target was executable code where final evaluation structurally cannot re-enter the optimization lifecycle and where repeated evaluation does not re-consume the already completed outer surface.

## Primary update — Auto-Quant-V2 contains a stronger executable terminal holdout pattern

Source: `TraderAlice/Auto-Quant-V2`, public main revision `52d63148d826e6c35d48c3167d95a4cc7a4eb6c4`, especially `autoquant/holdouts.py` and `tests/test_holdouts.py`.

This is not an LLM self-improvement benchmark, but its external holdout mechanism is directly useful for the missing outer-lockbox engineering contract.

### Frozen target namespace, not merely a hidden dataset

The system binds the already selected source evidence into a **distinct target Project** representing a strictly later, non-overlapping external period. Once the target has a holdout binding:

- `assert_iterative_research_allowed()` rejects candidate-selection lifecycle operations;
- generic `execute_study()` is rejected unless explicitly holdout-authorized;
- `start_session()` is rejected with `holdout.frozen-project`;
- the agent work brief marks the filesystem non-writable and exposes `holdout.run` as the primary action;
- the public test verifies `session.start` is absent from the bound Project's commands;
- after evaluation, the result explicitly records `selectionAllowed=false` and `tradingAuthority=none`.

This is stronger than sequence 92's Auditable Auto Research state machine, because ordinary candidate-generation/research actions are structurally unavailable inside the outer target from the moment it is bound.

### Completed holdout is read-only rather than re-evaluated

`run_holdout()` begins by loading the binding and checking the result directory. If a completed result already exists, it immediately returns `load_holdout_result(project)` rather than invoking the evaluator again.

The public test directly checks this behavior:

1. run the frozen holdout;
2. load its result;
3. call `run_holdout(target)` again;
4. assert the repeated call has the same result ID and exactly the same per-lane Run IDs.

After completion, status becomes `completed`, and the next action is assessment rather than another run.

This is the executable one-shot/read-only behavior that was missing in sequence 92.

### Incomplete multi-lane holdout can resume without replaying completed lanes

The holdout consists of frozen factor/portfolio/RL lanes. For each expected lane, `_matching_partial_run()` searches persisted Runs for the exact `studyInputHash`:

- exactly one matching Run -> reuse it;
- more than one -> fail with `holdout.duplicate-run`;
- none -> execute exactly that lane with `holdout_authorized=True`.

Final result publication is staged and moved into place with `os.replace`.

This means a retry after some lane Runs have become durable does not blindly rerun the whole holdout. It resumes from content-bound persisted sub-evaluations.

### Scope limit — this is not yet evaluator/provider exactly-once under arbitrary hard kill

The above is strong **logical** one-shot/restart behavior at the Run-artifact level, but I did not find a real-SIGKILL test proving every internal side effect of `execute_study` is exactly-once if the process dies after evaluator/provider consumption but before the Run itself becomes durable.

So this should not be overgeneralized to provider-level exactly-once execution. The stronger contract still needs the earlier write-ahead logical query ID + reconciliation layer.

### Scope limit — target terminality does not prove global operator non-adaptation

The frozen target Project itself cannot start candidate Sessions or ordinary research Campaigns. The original source Project is a separate object, however. The repository-level mechanism does not prove that a human/operator could not manually take the revealed holdout result and start a new source-side research cycle elsewhere.

Therefore the precise claim is:

**the outer evaluation namespace is structurally non-iterative and completed evaluation is read-only; global organizational non-adaptation is not proven.**

## Comparison with sequence 91–92 systems

- **OphAgent**: strongest immutable candidate + physically separated sealed certification + atomic release, but sealed evaluation itself is promotion data and fixed-sample.
- **Auditable Auto Research**: explicit inner-selection versus outer certification, but repeated certify re-queries the outer and search can resume after certification.
- **Auto-Quant-V2**: stronger terminal external target and read-only repeated completed holdout; completed sub-evaluations are reused on resume.

The remaining missing composition is now narrower:

**Auto-Quant terminal OUTER + Harn/GitMoot/LOGOS-style anytime-valid CERTIFY + restart-durable cross-candidate spending + provider/evaluator write-ahead reconciliation.**

## New design pattern

A strong outer lockbox can be implemented as a namespace capability boundary, not only a state flag:

`source adaptive research -> freeze artifact/evidence -> create distinct external target -> disable iterative commands in target -> execute content-bound sub-evaluations -> publish result atomically -> repeated outer calls read cached result only -> assessment/read-only thereafter`

For a self-improving agent, add before this outer target:

1. immutable selected candidate identity;
2. candidate-local anytime-valid CERTIFY on a separate surface;
3. durable cross-candidate error/query spending;
4. stable logical outer query IDs durably prepared before evaluator dispatch;
5. provider-side idempotency or UNKNOWN/reconciliation;
6. complete proposal/evaluation chronology.

## Source-bound artifact

`research_workers_clean_g1/self_improvement/terminal_holdout_contract_2026-08-28T112256_JST_autoquant.json`

## Exact next action

Search for a public self-improvement implementation that combines **Auto-Quant-V2-like frozen external terminal evaluation and cache-only repeated completion** with **candidate-local anytime-valid certification and durable candidate-crossing statistical spending**. Prioritize code/tests with stable logical evaluation IDs prepared before dispatch, real crash/restart injection, and an outer namespace where optimization commands are structurally unavailable throughout and after evaluation.

Frontier remains nonempty.
