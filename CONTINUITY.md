# O / Chat continuity

Updated: 2026-08-23 JST

Mandatory continuity: read this before O-related reasoning/actions where history matters and update it when standing context materially changes. Before sending new semantic context to O, show the wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Standing context
- Goal: materially accelerate genuine real-world AGI; O is instrumental/replaceable.
- User-side work should be minimized; repository/tool work belongs on the automated/Work side.
- Treat O and this chat as same-base-model for idea-generation overlap. Prefer genuine context asymmetries over duplicating reasoning O can readily derive.
- External ideas and user proposals are hypotheses, not automatic truth.
- Context is an intervention with information value and interference cost; more context is not monotonically better. Prefer minimal, gated, on-demand context and judge usefulness by downstream behavior/results.
- Do not turn anti-locality into a rigid breadth heuristic; depth/breadth tradeoffs must be outcome-driven.
- Evaluation itself is fallible. Distinguish measured improvement from metric validity; evaluator design may itself need falsification/calibration.

## O inbox / behavioral uptake
- Revisions 7-12 cover context-conditioning, asynchronous state freshness, recursive context selection, context-to-action gaps, behavioral/outcome evaluation, and scientist-agent external baselines.
- Revision 13 transfers primary execution to ChatGPT Work and stops Claude as executor while preserving shared results.
- Revision 14 requires durable-authority reconciliation to effective directions/latest verified state and asks for a recurring, falsifiably verified stale/conflict reconciliation mechanism rather than one-time cleanup.
- Revision 14 was formally acknowledged at 2026-08-23T08:40:17Z. The current Work owner remains generation-5 ChatGPT primary. `WORK_MODE.md` and `WORK_STRATEGY.json` have been materially reconciled to the real-world AGI objective and optional-gate interpretation; `CONTINUATION.json` is also reconciled in objective/ownership but can still lag live execution details, so recurrence/freshness remains something to observe.

## Current execution
- Latest observed heartbeat/progress: 2026-08-23T10:02:43Z (19:02:43 JST), so the primary is fresh.
- Revision 14 ack is recorded in `WORK_EXECUTION_STATE.json`.
- PR 265 is merged and remotely read back. Execution has moved beyond the original checkpoint-harness publication into a native CI-sharding cycle on branch `work/native-ci-sharding-cycle-v1`.
- Current native continuation has one pending post-result Candidate Evaluate invocation. The bounded CI unit is PASS while the upper task verdict remains FAIL; no AGI claim or Candidate activation occurred.
- Scientist-agent/context work has shown context -> behavior uptake. The stronger claim behavior -> better outcome remains a measurement question.

## Current chat policy
- Do not keep adding context merely because a new thought is plausible. Prefer observation now unless there is a concrete externally informative failure, context gap, evaluator blind spot, or result that O cannot readily derive from its current context.
- In particular, the evaluator meta-loop is not yet an explicit O revision; send it only if O treats a scorer/evaluator as authoritative without calibration or a real mismatch exposes the blind spot.
- For revision 14, do not count acknowledgement or one-time file cleanup as full success. Look for recurrent detection/reconciliation under intentionally or naturally stale/conflicting authority conditions.
