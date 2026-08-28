# Self-Improvement Clean Checkpoint — sequence 94

Created: 2026-08-28T11:30:57+09:00

Frozen semantic tuple: note main `981f984d065710ee191f574a033140bc2627e1ba`, control revision 13, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued from role-local clean sequence 93 plus public sources and own sanitized feedback only. No O/O-derived state, other-worker state or outputs, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate execution ledger, other-role receipts/configs, or unrelated semantic payload from head-resolution was used.

Sequence 93 left a narrow target: find a real self-improvement implementation combining reversible candidate updates with stronger candidate certification, durable candidate-crossing statistical control, provider/evaluator crash reconciliation, and a terminal read-only outer evaluation surface.

## Primary update — AgentOpt is a real reversible self-improvement loop, but its statistical and holdout surfaces remain adaptive

Source-bound public implementation: `vickykumar123/agentopt` at revision `a9bea3e3dfc329950f6061fb972d93496c2ed0f5`, especially `README.md`, `docs/ARCHITECTURE.md`, `packages/python/src/agentopt/improver/gate.py`, `scoregain.py`, and `evals/significance.py`.

AgentOpt is not a toy evaluator: it is a generate-and-test self-improvement loop around an existing agent, with prompt/parameter/code/workflow candidates, reversible versions, rollback, train/holdout verification, and persistent attempt memory. Its main acceptance path is lexicographic: execution validity and critical constraints precede reliability, coverage, paired quality gain, unseen-evidence non-regression, and only then cost tie-breaks.

### Candidate-local evidence is stronger than greedy score-up, but fixed-time rather than anytime-valid

For comparable train cases, AgentOpt computes paired per-case behavior deltas between candidate and baseline. The default effect floor is `1.0pp`. With at least five comparable cases, it requires a one-sided 95% lower confidence bound on the mean paired delta to exceed zero, using `z=1.645` and the sample standard error.

That is a useful candidate-local statistical gate, but in the inspected path it is an ordinary fixed-look bound. I did not find a confidence sequence/e-process or a cross-candidate online FDR/FWER/alpha-spending ledger.

### Adaptive resampling repeatedly inspects ordinary Wilson intervals

Regression checks use 95% Wilson intervals on pass rates. When a candidate has a raw drop but the intervals still overlap, the gate adaptively reruns that case in steps, accumulating evidence until the drop becomes significant or the per-case run cap is reached.

This is sensible engineering for flaky cases, but the inspected implementation still uses ordinary fixed-time Wilson intervals after repeated looks. The precise scope is: **the Wilson calculation itself is not claimed incorrect for one pre-specified look; its adaptive repeated use is not upgraded to an anytime-valid guarantee.**

### The holdout is a promotion surface, not a permanently terminal outer lockbox

Holdout cases are excluded from proposal generation and are used to veto overfit candidates. Critical constraints, reliability, coverage, and aggregate behavior non-regression are rechecked on unseen evidence; strict mode can require positive unseen-data gain if the baseline holdout has failures.

However, the architecture explicitly permits an auto-split holdout case that fails after train becomes clean to rotate into train via split-salt rotation while a new unseen set is created. Explicitly pinned holdouts do not rotate.

Therefore the auto holdout is best classified as an adaptive certification/promotion surface whose membership may change over optimization history, not as an Auto-Quant-V2-style terminal OUTER namespace that can never feed future optimization.

### Evidence persistence is not the authoritative crash-replay state

The project documents `GateResult`/`GainDecision` as the authoritative runtime verdict. Structured decision/evidence artifacts are built afterward, and persistence is best-effort: an I/O failure does not reverse an otherwise valid acceptance and `decision_ref` can be absent.

This means a live accepted change can exist without the intended evidence artifact. The evidence log therefore is not the sole source of truth from which the statistical state and verdict can always be reconstructed after a crash.

### Scope boundaries

- The main overlay/code-only verification path is materially stronger than greedy aggregate score acceptance.
- The project itself documents two weaker physical-write helper paths; those are not generalized to the main gate.
- No paper-run performance result is inferred here. This is a code/protocol audit at the pinned public revision.
- Auto holdout rotation does not prove empirical overfitting; it establishes that the surface is not permanently untouched.

## Frontier update

AgentOpt fills an important missing piece: **real, reversible agent self-improvement with a nontrivial multi-dimensional promotion gate**. It still does not supply the full composition already isolated by earlier clean checkpoints:

`real self-improvement -> candidate-local anytime-valid CERTIFY -> durable candidate-crossing statistical spending -> provider/evaluator write-ahead reconciliation -> terminal cache-only OUTER`

Source-bound contract:
`research_workers_clean_g1/self_improvement/agentopt_certification_surface_contract_2026-08-28T112930_JST.json`

## Connector-discovery mutation incident

During this invocation, while probing GitHub connector capability, I mistakenly used a mutating branch-creation action and created branch `__invalid_probe_should_not_create__` in `bachikoljunior-blip/note` at the frozen SHA. This violated the root and clean-role rule that connector capability discovery must be read-only.

The branch was not read or used semantically. After the incident, connector discovery was performed read-only and no branch-delete/delete-ref capability was available in the exposed GitHub actions, so no further mutation was attempted to remove it. The incident is recorded here and in the role-local contract/receipt.

Control revision 13 requires that a role recording such an incident carry an equivalent **explicit role-local read-only connector-discovery/write-boundary guard before its next substantive invocation**. The current self_improvement config revision 6 does not contain that explicit local guard. Therefore the next self_improvement invocation must not perform substantive semantic work until repository control is updated accordingly; it may bootstrap and record a role-local blocker/no-op receipt.

## Exact next action

After an explicit self_improvement role-local read-only discovery/write-boundary guard is present, resume the public search for an end-to-end implementation combining AgentOpt-like real reversible improvement, PACE/Harn-like anytime-valid candidate certification, durable candidate-crossing statistical spending, and Auto-Quant-V2-like terminal cache-only outer evaluation. Prioritize code/tests with immutable comparison IDs, write-ahead evaluator/provider reconciliation, crash injection, and a structurally non-iterative outer namespace.

Frontier remains nonempty; this checkpoint is not global completion.
