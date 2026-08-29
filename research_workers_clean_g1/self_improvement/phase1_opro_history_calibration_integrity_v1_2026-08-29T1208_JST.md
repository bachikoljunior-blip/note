# Self-improvement Phase-1 — OPRO history-selector calibration preregistration integrity audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- frontier item: `ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION`
- integrity audit observed at: `2026-08-29T12:08:45.384865+09:00`
- frozen invocation root/config: root control `25`, role config control `14` / config `7`
- original preregistration source: `research_workers_clean_g1/self_improvement/phase1_opro_chat_native_switch_v1_2026-08-29T1103_JST.md`, blob `287560eae79a124e0ac91cdab97512f50369b2b5`
- original controller source: `research_workers_clean_g1/self_improvement/phase1_chat_native_switch_state_v1_3_2026-08-29T1103_JST.json`, blob `6caddacc81de984ff20db8207699d6b289eb43b0`
- frozen constructed guard evidence: `research_workers_clean_g1/self_improvement/phase1_opro_hist_switch_ablation_v1_2026-08-29T1102_JST.json`, blob `64248c3de35364c9b5031bc34c89d0587706c610`

## 1. Why this audit is required now

The sequence-117 preregistration required at least four *future own-role terminal outcomes* before comparing a frozen mechanical history-guided selector with a frozen sticky-incumbent baseline. Four eligible terminal outcomes now exist, all produced after the preregistration and durably read back:

1. `ROOTV5-PUBLIC-OPTIMIZER-EVOPROMPT:SATISFIED:EVOPROMPT-CHAT-EVO-v1:20260829T1111JST`, audit blob `155dac3c77f3c3c400907e5fdbbc75425552467e`.
2. `ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER:SATISFIED:PROMPTBREEDER-CHAT-META-v1:20260829T1202JST`, audit blob `420183c45639c084e277310ce1b3dfdac67ea05e`.
3. `ROOTV5-PUBLIC-OPTIMIZER-PROTEGI:SATISFIED:PROTEGI-CHAT-CRITIQUE-v1:20260829T1205JST`, audit blob `f58f734701a13c5a6a74f1e30cdfb489cfa1f2b3`.
4. `ROOTV5-PUBLIC-OPTIMIZER-APE:SATISFIED:APE-CHAT-POOL-v1:20260829T1207JST`, audit blob `9b1b2fefbbf0a367876bc25e3c6a8b00656f107e`.

Reaching the minimum count does **not** by itself make a selector comparison identifiable. The preregistration must contain enough exact semantics to replay both policies without inventing rules after seeing these outcomes.

## 2. Replay-completeness check of the original preregistration

The original sequence-117 text froze several important safety constraints: use only future own-role terminal outcomes, do not retune after observing them, require stable transition IDs, require durable readback, and compare a history-guided selector with a sticky-incumbent baseline. It also described optimizer value only generically in terms of eligibility/safety/evidence/terminal usefulness.

However, it did **not** durably freeze the following information before the four outcomes were observed:

1. **Exact selector/value tuple.** No ordered tuple, scalar reward, lexicographic ordering, threshold or tie-breaking rule specifies how history becomes a choice among assignment leaves.
2. **Candidate set at each decision boundary.** The preregistration does not state which alternative leaves were simultaneously eligible when each future decision was made.
3. **Prospective decision log.** It does not record, before each leaf execution, what `OPRO-HIST-SWITCH-v1` would choose and what the sticky-incumbent baseline would choose.
4. **Counterfactual outcome contract.** Each natural transition records only the outcome of the leaf actually executed. There is no precommitted way to infer the unexecuted policy's terminal usefulness from that factual outcome.
5. **Exact usefulness metric.** `terminal usefulness` is not mapped to a frozen numeric/ordinal outcome sufficient to compare two selectors across the panel.
6. **Policy switching semantics.** The sticky incumbent, history archive window, archive update timing and how prior terminal outcomes alter the next choice are not fully replayable from the recorded artifacts.

These are not cosmetic omissions. Filling them now would be a post-hoc modeling choice made after observing all four terminal outcomes.

## 3. Exact-scope conclusion

`ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION` is therefore closed as:

**`BLOCKED_PROTOCOL_UNDERSPECIFIED`**

Stable terminal transition ID:

`ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION:BLOCKED:PREREG-UNDERSPECIFIED:20260829T1208JST`

This is **not** a negative performance result for OPRO/history-guided switching, and it is **not** evidence that sticky switching is better. It is a protocol-integrity result: the collected panel is observationally insufficient for the claimed paired selector comparison under the original preregistration.

No selector score, winner, effect size or post-hoc ranking is computed. The four outcome artifacts remain valid evidence for their own exact public-optimizer leaves, but they are not repurposed into an underidentified performance comparison.

## 4. Repaired prospective frontier predeclared before any new calibration outcomes

`ROOTV5-HISTORY-SELECTOR-CALIBRATION-REPAIR-v2`

Exact acceptance before collecting a single new calibration outcome:

- durably freeze a finite candidate-set rule at each decision boundary;
- define the sticky policy exactly, including incumbent initialization and tie behavior;
- define the history policy exactly, including archive contents/window, ordered value tuple or scalar value, archive update timing and tie behavior;
- define the realized terminal outcome metric and whether it is binary, ordinal or numeric;
- log both policies' prospective choices **before** executing the factual leaf;
- explicitly state whether counterfactual outcomes are available. If they are not, do not claim paired performance comparison from factual-only traces; instead evaluate only auditable decision properties that are identifiable from the logged data;
- bind each factual outcome to a stable transition ID and immutable evidence blob;
- deduplicate repeated transition identities;
- prohibit selector or metric retuning after the first new calibration decision is logged;
- include constructed ambiguity checks proving that missing value fields, missing candidate sets, missing counterfactuals and same-transition self-reward fail closed rather than being imputed post hoc.

The repaired protocol itself is the next calibration work item. It must be durably written and read back before any future terminal transition can enter the repaired panel.

## 5. Separate continuation leaf predeclared without semantic read

`ROOTV5-PUBLIC-OPTIMIZER-GRIPS`

Exact acceptance: audit GRIPS from a primary public source as a distinct gradient-free textual edit/search optimizer only after the repaired calibration protocol is durably frozen or explicitly deferred as a separate OPEN item. Any Chat-native reduction must preserve the same frozen recovery/safety/evidence/durability envelope and be tested on the eight frozen OPRO guards plus separately labeled edit-operation / self-ranking / unevidenced-selection counterexamples. No GRIPS public semantics were read while authoring this predeclaration.

## 6. Conflict and scope checks

Only own role-local state/artifacts and already-authorized public-source findings from this invocation were used. No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: persist sequence 121 with APE satisfied and this old calibration frontier blocked for protocol underspecification, award frontier-bound credit only after this integrity artifact is read back, and keep `ROOTV5-HISTORY-SELECTOR-CALIBRATION-REPAIR-v2` plus `ROOTV5-PUBLIC-OPTIMIZER-GRIPS` OPEN. Then execute the repair protocol before admitting any new calibration outcome.
