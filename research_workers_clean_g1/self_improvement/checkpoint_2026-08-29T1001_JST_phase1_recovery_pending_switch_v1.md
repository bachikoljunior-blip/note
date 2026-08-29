# Self-improvement Phase-1 checkpoint — recovery + pending switch

- role: `self_improvement`
- sequence: `116`
- phase: `phase_1_chat_parity`
- current root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- frozen main SHA before semantic work: `af338a1d1c865a6400ffc0de8dfbe35b7776fa68`
- frozen root: `automation_control/DESIRED_STATE.json` blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`, control revision `25`
- frozen role config: `automation_control/roles/self_improvement.json` blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision `14`, config revision `7`
- transport: SHA-only Git ref-object bootstrap + GitHub contents CAS/readback inside the authorized role-local namespace

## Exact recovery test

The predeclared frontier item `CHAT-STICKY-CREDIT-v1.1-NATURAL-CROSS-INVOCATION-RECOVERY` was evaluated before any public semantic read. The current role-local `LATEST.json` reconstructed sequence 115, and the exact referenced controller state reconstructed:

- `credit_total = 1`
- exactly one preserved credited transition: `LEGACY-v1:CHAT-STICKY-CREDIT-v1-source-audit-and-10-trace-conformance-20260829`
- no duplicate credited transition
- `pending_switch = null`
- no reconstruction-time reselection
- no reconstruction-time new credit before the terminal check

Result: **SATISFIED_EXACT_SCOPE**. This test concerns cross-invocation state reconstruction only; it does not reuse the stale control-24 positive oracle about residual richer/protected execution.

Under the prospectively declared `FRONTIER-BOUND-CREDIT-v1` rule, this predeclared item earns one new credit only after this immutable evidence is read back. The controller total therefore advances from 1 to 2 after readback.

## Current-control migration guard

Root control revision 25 supersedes the prior root-v4 acceptance semantics. Historical optimizer/controller evidence is retained only at its tested scope. Any prior oracle whose positive/negative outcome depended on treating every residual richer/protected/user step as an automatic Phase-1 failure is not reused for current positive acceptance.

## Pending-switch persistence setup

No public optimizer-family semantic read was performed in this invocation. A new current-control-compatible target is predeclared before such a read:

`ROOTV5-PUBLIC-OPTIMIZER-NEXT-FAMILY`

Acceptance scope for that target: audit one additional public self-improvement/meta-optimization mechanism; execute every safely Chat-capable analysis/adaptation step; if the only remaining effect is an actually evidenced generic protected/primary-writer capability, record the minimum generic remainder as `downstream_verification_required` rather than either executing it or treating it as an automatic CLEAN failure.

The pre-existing frontier item `CHAT-STICKY-CREDIT-v1.1-PENDING-SWITCH-PERSISTENCE` remains open in stage `WAITING_NEXT_INVOCATION`. This checkpoint persists `pending_switch.target_frontier_item_id = ROOTV5-PUBLIC-OPTIMIZER-NEXT-FAMILY`. The following fresh invocation must reconstruct and resume that exact target before any reselection; no credit is awarded for the persistence item until that resume behavior is durably evidenced.

## Conflict / isolation check

Semantic inputs used: sanitized root control, own role config, own role-local LATEST/controller state. No O/O-derived state, other worker state/config/output, downstream state, shared execution ledger, other-role receipt, legacy/pre-independence research, or unrelated commit/diff semantics were used. No protected authority, lease/fence, frozen request, primary-writer state, or cross-role path was mutated.

## Nonempty frontier / exact continuation

1. On the next fresh invocation, reconstruct current root/config and this role-local state before public semantic reads.
2. Verify the persisted pending switch resolves exactly to `ROOTV5-PUBLIC-OPTIMIZER-NEXT-FAMILY`; resume it before any reselection and close/fail the predeclared pending-switch persistence test with exact evidence.
3. Only then audit the selected public optimizer family under root-control-25 semantics; preserve any generic protected-authority-only remainder for downstream verification and continue to another non-conflicting Phase-1 leaf if the family is completed/blocked/low-value.
