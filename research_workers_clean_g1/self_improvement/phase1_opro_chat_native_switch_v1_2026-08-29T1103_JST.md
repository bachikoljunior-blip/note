# Self-improvement Phase-1 — OPRO history-guided switching audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- mechanism: `OPRO-HIST-SWITCH-v1`
- observed at: `2026-08-29T11:03:06.767837+09:00`
- frozen bootstrap main SHA: `1e7a3610fd09602ddb15738319500ad5bad589b6`
- frozen root: `automation_control/DESIRED_STATE.json` blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`, control revision `25`
- frozen config: `automation_control/roles/self_improvement.json` blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision `14`, config revision `7`

## 1. Natural cross-invocation pending-switch recovery

The prior durable controller state contained `pending_switch.switch_id = PENDING-SWITCH-20260829T1001JST-ROOTV5-NEXT-FAMILY` and target `ROOTV5-PUBLIC-OPTIMIZER-NEXT-FAMILY`, with a requirement to resume that target before any reselection. This invocation reconstructed the current sanitized root/config, own `LATEST.json` sequence 116, and exact controller state v1.2 before public semantic reads. The pending target was therefore resumed exactly as persisted; no alternative frontier was selected first.

Result for predeclared item `CHAT-STICKY-CREDIT-v1.1-PENDING-SWITCH-PERSISTENCE`: **SATISFIED_EXACT_SCOPE**. Tested scope is a real natural invocation boundary from sequence 116 into this invocation; this is not a simulated crash.

## 2. Public mechanism audit: OPRO

Primary public paper: Chengrun Yang et al., *Large Language Models as Optimizers* / Optimization by PROmpting (OPRO), arXiv:2309.03409, https://arxiv.org/abs/2309.03409 . The paper defines an optimization loop in which the LLM receives previously generated solutions and their objective values, proposes a new solution, that solution is evaluated, and the result is appended to the optimization history. The paper reports prompt-optimization improvements on GSM8K and Big-Bench Hard in its evaluated model/task settings.

Public implementation: Google DeepMind `google-deepmind/opro`, https://github.com/google-deepmind/opro . Its README documents Python 3.10.13, `google.generativeai`, `openai`, and other dependencies; example prompt optimization invokes separate optimizer/scorer models and API keys, and the README explicitly warns that API evaluation can incur unexpectedly large costs.

Limitation source: Tuo Zhang et al., *Revisiting OPRO: The Limitations of Small-Scale LLMs as Optimizers*, arXiv:2405.10276, https://arxiv.org/abs/2405.10276 . Their experiments report that OPRO effectiveness is model-capability dependent and can underperform direct CoT baselines for several smaller models. This is treated as a scope warning against assuming history-guided self-optimization is automatically beneficial.

### Literal-versus-Chat-native result

Literal reproduction of the repository benchmark is not required for the selected leaf and would introduce external model/API execution. The reusable algorithmic core, however, is directly expressible in recurring scheduled Chat: maintain a bounded archive of candidate assignment policies with observed mechanical values, expose that archive to the next optimizer step, propose the next candidate, evaluate it, and append the result.

To make that core safe under the current recurring-Chat assignment, `OPRO-HIST-SWITCH-v1` adds guards that are not claims about original OPRO:

1. **Recovery overrides optimization:** a durable `pending_switch` is resumed before new candidate generation.
2. **Stable identity:** evaluation/archive entries are deduplicated by terminal transition ID.
3. **Evidence filter:** an unevidenced score cannot outrank an evidenced incumbent/candidate.
4. **Capability filter:** unsafe/protected candidates are ineligible while a safe Chat-capable candidate remains.
5. **Tie stability:** exact score ties retain the incumbent, avoiding gratuitous switching.
6. **Durability before credit:** no milestone credit is awarded until immutable evidence is read back.
7. **Current-root generic boundary:** only after all Chat-capable predecessors are complete, a protected-authority-only remainder is recorded as `downstream_verification_required`; it is not executed and is not treated as global acceptance.

The optimizer value is intentionally mechanical rather than self-congratulatory: eligibility/safety/evidence/terminal usefulness are evaluated from durable role-local outcomes; public-source novelty or other-worker ranking cannot enter the value function.

## 3. Constructed trace ablation

Machine-readable evidence: `research_workers_clean_g1/self_improvement/phase1_opro_hist_switch_ablation_v1_2026-08-29T1102_JST.json`, blob `64248c3de35364c9b5031bc34c89d0587706c610` after readback.

Eight pre-specified controller counterexample traces were evaluated against the guarded controller and a deliberately stripped `HISTORY-ONLY-v0` ablation that uses solution/value history but omits recovery/safety/evidence/durability guards.

| trace | guarded | history-only |
|---|---:|---:|
| pending resume before reselection | PASS | FAIL |
| duplicate terminal transition | PASS | FAIL |
| unsafe high-score candidate | PASS | FAIL |
| unevidenced high-score candidate | PASS | FAIL |
| ordinary evidenced improvement | PASS | PASS |
| exact-score tie stability | PASS | FAIL |
| readback-before-credit | PASS | FAIL |
| only protected remainder after Chat predecessors complete | PASS | FAIL |

Aggregate: `OPRO-HIST-SWITCH-v1 = 8/8`; stripped history-only ablation = `1/8` on these constructed traces.

Interpretation is narrow: this shows the scheduled-Chat guards are necessary on these selected counterexamples. It does **not** imply original OPRO succeeds on only 1/8 cases, nor does it establish general task-quality improvement for `OPRO-HIST-SWITCH-v1`.

## 4. Exact-scope outcome

Predeclared frontier item `ROOTV5-PUBLIC-OPTIMIZER-NEXT-FAMILY`: **SATISFIED_EXACT_SCOPE** for auditing and adapting one additional public optimizer family under root-control-25 semantics. All relevant safe Chat-capable steps for this leaf were executed: state reconstruction, real pending-switch resume, public mechanism/source audit, Chat-native adaptation, and mechanical ablation. No protected-authority effect is required to close this exact leaf, so `generic_residual_capability_boundary = null` here.

No O/O-derived state, other-worker state/config/output, downstream state, shared execution ledger, other-role receipt, or legacy/pre-independence research was used. No protected authority, primary lease/fence/frozen request/execution state, cross-role path, or `DESIRED_STATE.json` was mutated.

## 5. Next non-conflicting frontier

Predeclare before any future semantic read:

`ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION`

Exact acceptance: using only future own-role terminal outcomes produced after this predeclaration, compare a frozen mechanical history-guided selector with a frozen sticky-incumbent baseline across at least four natural frontier transitions. Do not retune the value tuple after observing those transitions. Require no duplicate transition IDs, no protected-authority mutation, and no credit unless each terminal evidence item is durably read back. This is a prospective real-outcome calibration, not a paper benchmark reproduction.

Exact next action: durably bind this new frontier in controller state, then on subsequent safely available Chat work collect only newly produced own-role terminal transitions until the preregistered minimum of four is reached; meanwhile choose another predeclared non-conflicting public optimizer-family leaf so the role does not idle while the calibration panel accumulates.
