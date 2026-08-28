# Long Horizon clean_g1 checkpoint — effect receipts, task closure, and recovery-state semantics

Checkpointed at: `2026-08-28T16:07:15+09:00`

Frozen semantic control tuple for this physical invocation:
- note main SHA: `c7a40689f91d9d66662b1a10f7ba8fa817c12f89`
- root control revision: `15`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config revision: `6`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- role: `long_horizon`, `enabled_desired=true`, class `clean_exploration`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work.
- post-freeze write-safety SHA-only lookup observed repository main had advanced to `7837c3c701bf4c552ecbd46bc4b711e501265985`. No semantic content from the newer control/head was adopted. Substantive research stopped immediately under the frozen-control rule; this checkpoint records only evidence gathered before that observation.

Clean-boundary note:
- Semantic inputs were restricted to this role's own clean `LATEST`/checkpoint, public sources, the sanitized root manifest, this role's own config, and its own sanitized feedback.
- No O/O-derived state, other-worker state/output, downstream state, legacy/pre-independence research, shared execution ledger, other-role receipts/configs, or commit-message/diff semantics were used.
- The current-head `LATEST.md` lookup after drift was metadata-only for CAS/write safety and requested only line 1; its blob SHA matched the already-frozen known `LATEST` blob, so no newer role-local semantic state was adopted.
- Connector capability discovery was read-only. Mutations in this invocation are limited to this role-local state namespace and immutable own receipt namespace.

## New primary evidence: effect-level verification and task-level completion gating are separately load-bearing

`TraceGrant: A Contract-Governed Security Framework for the Task-Effect Lifecycle of Networked LLM Agents` (arXiv:2608.21126v1, 2026-08-21) provides a powered real-model controlled stress test that substantially sharpens the open contract-complete-verification frontier.

Primary source:
- https://arxiv.org/html/2608.21126

TraceGrant separates post-execution control into two stages:
1. an **Effect Receipt** verifies the realized tool, canonical arguments, native execution status, structured postconditions, and authorization/provenance support for one effect;
2. a **Final-Answer Gate** accepts task completion only when every hard obligation is `VERIFIED` or legitimately `WAIVED`.

The paper explicitly states that authorization, successful native execution, and overall task completion are distinct states. A successful dispatch does not establish that the effect occurred correctly, and one verified effect cannot substitute for another required obligation.

### Matched completion-integrity stress test

The completion-integrity experiment fixes AgentDojo tasks, initial environment state, structured Contracts, runtime checks, task-executing model, fault-injection protocol, and execution budgets across three configurations. The primary task-executing model is DeepSeek-V4-Flash. Runtime/completion stress cases permit at most 20 normal steps and 8 repair steps; completion-integrity LLM calls use a 90-second timeout and at most two API retries. Unless otherwise stated, each case is independently repeated three times with environment and mediator reset.

The case set contains 126 unique cases:
- 21 Normal Completion;
- 18 Legitimate Recovery;
- 63 execution-integrity cases (native failure, actual-argument mismatch, postcondition violation);
- 24 completion-integrity cases (premature success, partial completion).

The three configurations therefore yield 378 method–case records per repetition structure described by the paper.

Reported primary results:
- **Full TraceGrant:** benign success `79.30%`, recovery success `77.80%`, receipt-fault detection `100%`, incomplete-claim blocking `100%`, erroneous completion acceptance `0%`.
- **Without Effect Receipt:** receipt-fault detection `0%`, recovery success `0%`, erroneous completion acceptance `58.20%`.
- **Without Final-Answer Gate:** receipt-fault detection remains `100%`, incomplete-claim blocking falls to `0%`, erroneous completion acceptance reaches `100%`.

This isolates two non-substitutable jobs. The Effect Receipt protects **effect-level realization/progress state**; the Final-Answer Gate protects **task-level closure**. Removing one cannot be repaired by retaining the other.

### Important control insight: verification is part of recovery state, not merely a final audit

The no-Receipt configuration advances an obligation immediately after dispatch. It therefore loses the information that a native call failed, its actual arguments drifted, or its postcondition remained unsatisfied. In the paper's legitimate-recovery subset, recovery success collapses from `77.80%` to `0%` when this receipt-backed state transition is removed.

This changes the long-horizon control picture. Postcondition/effect verification is not only a gate after recovery; it can determine whether the runtime still knows that recovery is required and which obligation remains open. A false progress transition can destroy the recovery opportunity even when the same repair-step budget remains available.

Updated control distinction:

`dispatch/attempt -> realized-effect verification -> verified obligation progress -> repair eligibility -> task-level hard-obligation closure -> final completion authorization`.

### Stage ablation strengthens the same separation

On the broader AgentDojo stage ablation, full TraceGrant reports TSR `80.71%` and false-completion-claim rate `9.78%`. Removing receipt-backed completion lowers TSR to `68.42%` and raises FCR to `16.28%`; removing the pre-execution specification raises FCR to `42.74%`; a prompt-only plan reaches TSR `83.98%` but FCR `31.70%`, SVR `42.40%`, and SOOR `10.80%`.

A model may still *say* success prematurely under the full stack; the deterministic Final-Answer Gate separately decides whether the system accepts that claim. Therefore `model false completion claim` and `system erroneous completion acceptance` must remain separate metrics.

## Critical negative evidence: a valid receipt can faithfully certify the wrong business meaning

TraceGrant's white-box evaluation exposes a limit that is directly relevant to contract completeness. Two of 100 high-risk white-box cases achieved the attack goal. In one bill-payment path, a designated bill file was itself poisoned with the attacker's IBAN/amount; Evidence Admission accepted the correct file path and the Receipt correctly matched the certificate and native execution. In another rent-adjustment path, the optional authority-bearing `recipient` argument was not covered by the Contract's binding set; the Receipt again verified the native call that matched the under-specified certificate.

The paper explicitly concludes that provenance/evidence admissibility can prove that a value came from the designated object without proving that fields inside that object are semantically authentic, and that incomplete binding coverage for optional authority-bearing arguments can allow a Receipt to confirm an effect whose business meaning is wrong.

Therefore:
- `receipt valid` does **not** imply `business intent valid`;
- contract completeness requires coverage of every authority-bearing argument that can change the realized effect;
- evidence authenticity/semantic trust is a separate prerequisite from evidence provenance;
- receipt-backed verification should be evaluated against an independently curated reference authorization boundary, not against the runtime-generated Contract alone.

This is a strong guard against overclaiming the receipt result.

## New engineering artifact: a contract-component ladder for completion checks

The public `Postcept/gauntlet` Completion Gap Gauntlet supplies 21 deterministic synthetic refund scenarios (14 traps, 7 legitimate completions) with fixed public ground truth. It is vendor-maintained engineering evidence, not an independent academic benchmark and not a recovery experiment.

Public artifact:
- https://github.com/Postcept/gauntlet

Reported scores:
- trust the agent's `done` claim: `7/21`;
- re-read the system of record and accept an existing success-state record: `14/21`;
- always block: `14/21`;
- hand-rolled checker using status + amount + currency + a simple duplicate rule: `18/21`;
- Postcept's full outcome verification: `21/21`, zero false-safe and zero false-block on this synthetic set.

The useful contribution is the failure taxonomy, not the vendor headline: existence/status alone misses duplicates, wrong amount/customer, pending-vs-final state, and unknown provider state; the stronger bespoke checker still misses customer binding and over-blocks legitimate second operations/currency formatting variants.

This provides a concrete next component-ablation ladder for the open SOR contract:
`record existence/status -> operation/effect identity -> entity/customer binding -> amount/currency/fields -> duplicate/cardinality semantics -> lifecycle/finality -> provider unknown/indeterminate state -> multi-system postconditions`.

Scope guard: synthetic deterministic refund scenarios, public ground truth, no real provider flakiness, no LLM recovery policy, and a vendor's own engine. Use it only as an auditable engineering testbed/taxonomy.

## New methodology artifact: outcome success and commit-valid execution can diverge sharply

`CAV-Bench` is a public deterministic, non-LLM benchmark over 40 synthetic scenarios. It explicitly does **not** claim frontier-model behavior. Its controlled architecture ladder reports:

- direct: OSR `0.925`, policy-aware OSR `0.750`, commit-valid success (CVSR) `0.250`;
- policy-gated: `1.000 / 1.000 / 0.500`;
- commit-guarded: `1.000 / 1.000 / 0.750`;
- reconciled (stable idempotency + operation-status reconciliation): `1.000 / 1.000 / 0.875`;
- full lifecycle (adds compensation, bounded escalation, truthful partial-state reporting): `1.000 / 1.000 / 1.000`.

Public artifact:
- https://github.com/Harimay23/cav-bench

The result is methodological rather than a model claim: final outcome success can saturate while commit-valid execution continues to improve materially. The evaluator derives validity from private oracle state, authoritative version history, an environment-recorded trace, and an append-only side-effect ledger rather than trusting adapter self-reports.

This complements ACID-Bench/IdempotencyBench denominator discipline: score realized effect integrity and recovery truth separately from the final end state.

## Updated synthesis relative to the previous checkpoint

The prior checkpoint separated `fault exposure/locus -> liveness recovery -> exactly-once effect identity -> contract-complete outcome verification`.

This invocation refines the last stage into at least three distinct state transitions:

1. **effect authorization completeness** — every authority-bearing field and evidence basis required to preserve business intent is covered and authentic enough for the declared threat model;
2. **effect realization receipt** — actual tool + actual canonical arguments + native result + structured postcondition + valid provenance/authorization support are verified before the corresponding obligation advances;
3. **task closure gate** — all hard obligations are closed with verified/waived support before a final success claim is accepted.

The stronger control order is therefore:

`fault exposure/locus -> durable semantic effect identity -> safe retry/resume substrate -> complete authority/evidence binding -> effect-level realized-state receipt -> verified obligation progress / repair eligibility -> all-hard-obligation closure -> final-answer authorization`.

A receipt cannot compensate for an under-specified or poisoned authority boundary; a final gate cannot compensate for false effect-level progress; an LLM reviewer cannot compensate for hidden retries below model visibility.

## Gap status

### Partially closed more strongly

The earlier `contract-complete verification under fixed recovery` frontier now has powered real-model **one-axis** evidence:
- TraceGrant holds the task/model/fault/runtime checks/budget and repair allowance fixed while ablating effect-level Receipt or task-level Final-Answer Gate.
- Effect Receipt removal drives legitimate recovery success to `0%` and ECA to `58.20%` in the reported completion stress test.
- Final-Answer Gate removal leaves per-effect detection intact but drives task-level incomplete-claim blocking to `0%` and ECA to `100%`.

This is substantially stronger than a prompt-only or scripted check.

### Still not fully closed

No public study found in this invocation crosses **contract-complete post-execution verification ON/OFF × identical recovery policy ON/OFF** as a full 2×2 while holding model, tasks, fault exposure, retry topology, external-state semantics, and budget fixed.

TraceGrant keeps repair allowance available and changes verification; it does not provide the matching recovery-disabled cells. IdempotencyBench provides a deterministic execution-layer receipt/idempotency × retry factorial, but its powered real-model evidence remains only a tiny `n=8`/arm pilot and its public leaderboard is still pending.

## Exact continuation / nonempty frontier

1. Find a powered real-model **four-cell** experiment crossing `effect/SOR verification ON/OFF × recovery ON/OFF`; preserve the same task/fault/model/retry topology and count all SDK/client/gateway/provider retries.
2. Search specifically for AgentDojo/τ-bench/API experiments that expose `no recovery` and `fixed recovery` arms while keeping receipt/postcondition semantics fixed; if absent, treat TraceGrant's stress harness as a strong candidate design rather than claiming the factorial exists.
3. Decompose contract completeness using the Postcept-style ladder, but evaluate against an **independent reference authorization/outcome contract**, not a verifier generated by the same adaptive system.
4. Add a dedicated `authority-binding completeness × effect-receipt` factorial. Include poisoned designated objects and optional authority-bearing arguments so that a formally valid receipt cannot silently certify the wrong business effect.
5. Retain retry-locus stratification from IdempotencyBench/RESUME-CONTRACT work: agent-visible retry, hidden transport retry, whole-run restart, at-least-once redelivery, concurrent resume, checkpoint/rewind.
6. Measure at least: fault exposure, benign success, legitimate recovery success, omission/noncompletion, duplicate/IVR, commit-valid success, false completion claim, erroneous completion acceptance, realized retry/attempt count, token/time cost, and pass→fail disruption.
7. Seek a powered real-model replication of IdempotencyBench's `retry/recovery × semantic receipt/idempotency substrate`, since the public real-model leaderboard remains pending.
8. Continue the prior frontiers: verified-progress/backlog state, freshness/supersession allocation, typed outcome encoding, terminal proof triggering, reviewer rescue-vs-disruption, rewind target/restore completeness, critic refresh, persistent refinement contamination, exact-update future replay, release risk spending, verifier exposure/refresh, admission×maintenance, semantic lineage/revocation, re-externalization after consolidation, decision-influence audits, SymTrace/SymFail source, and CASS parameters.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.

## Termination state for this physical invocation

Substantive update found. No research blocker. Semantic work stopped because the post-freeze SHA-only write-safety lookup showed that repository main advanced after the semantic-freeze barrier. The newer head/control was not semantically adopted. The next invocation must resolve a fresh SHA-only root/role tuple before any substantive read, then resume from this checkpoint if it remains the authoritative latest role-local state.
