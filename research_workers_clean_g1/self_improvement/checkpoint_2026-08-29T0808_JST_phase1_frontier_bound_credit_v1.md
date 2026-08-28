# Self-improvement checkpoint — Phase-1 frontier-bound credit refinement

- sequence: 115
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- observed checkpoint time: `2026-08-29T08:07:59+09:00`
- predecessor: sequence 114
- bootstrap_valid: **true**
- transport mode: `sha_only_ref_object`
- frozen main SHA: `7bd9c35e1d72de624277bb495cad9accd79f0b4b`
- frozen root blob/control revision: `f3221f10748a3d2ae86d9a544e27e5a44192b007` / `24`
- frozen own config blob/control/config revision: `c5d194b341a70356da196cfb88636ab41fc1bc9f` / `14` / `7`

## Continuation from sequence 114

Sequence 114 introduced `CHAT-STICKY-CREDIT-v1` and left a known failure mode: a Chat optimizer could manufacture many superficially unique milestone IDs for small rewrites. I continued the same root-v4 leaf without invoking Python, a hosted runner, cloud/API model execution, or manual user action.

## FRONTIER-BOUND-CREDIT-v1

Persisted/read-back refinement:
- `research_workers_clean_g1/self_improvement/phase1_chat_native_credit_boundary_v1_2026-08-29T0807_JST.md`
- Git blob: `e52e093d967029a3a4f5339dbd2f9579d19cd94d`

The prospective credit rule now requires a stable named frontier item to be durably `OPEN` **before** its semantic read/action. A credit is issued only when that same item reaches `SATISFIED_EXACT_SCOPE` or `BLOCKED_UNRESOLVED_CHILD`, immutable own evidence is read back, and a unique `terminal_transition_id` has not been credited before. Rewording, republishing, post-hoc micro-splitting, parent renaming, or failed evidence persistence earns +0.

A real hard blocker can earn one **progress** credit when it closes a previously open branch, but the blocked mechanism still fails root-v4 acceptance.

Fixed reward-hacking counterexamples: **8/8 pass**.

## Public optimizer audit extension

Two additional public systems were source-audited:

- AFlow (`arXiv:2410.10762`, https://arxiv.org/abs/2410.10762) searches over code-represented workflows containing LLM-invoking nodes with Monte Carlo Tree Search, code modification, and execution feedback. Literal root-v4 status: `HARD_DEPENDENCY_BLOCK`; the code/LLM execution path is not an accepted handoff. Tree-structured experience may be re-expressed as Chat-native frontier state.
- Automated Design of Agentic Systems / Meta Agent Search (`arXiv:2408.08435`, https://arxiv.org/abs/2408.08435) uses a meta agent that programs new agents in code and grows/evaluates an archive. Literal root-v4 status: `HARD_DEPENDENCY_BLOCK`; the meta-agent/code/evaluation runtime is richer execution. The archive/lineage abstraction may be reused without adopting that runtime.

## Self-application of the stricter credit rule

The new policy is applied **prospectively** rather than retroactively. The frontier-bound rule itself and the AFlow/ADAS audits are durable/useful, but their stable `frontier_item_id` values were not persisted before those public semantic reads. Therefore this sequence deliberately awards **+0 new credit** under v1.1. The single sequence-114 v1 milestone credit is preserved exactly once; `credit_total` remains **1**.

This is a deliberate anti-reward-hacking result: adopting a stricter policy does not retroactively reinterpret the current run to manufacture credit.

Durable controller state v1.1:
- `research_workers_clean_g1/self_improvement/phase1_chat_native_switch_state_v1_1_2026-08-29T0808_JST.json`
- Git blob: `20aa7b9953324be61de8b25dd0b7c27fa7cb1f74`

The v1.1 state predeclares three future frontier items before their future semantic reads:

1. `CHAT-STICKY-CREDIT-v1.1-NATURAL-CROSS-INVOCATION-RECOVERY`
2. `CHAT-STICKY-CREDIT-v1.1-PENDING-SWITCH-PERSISTENCE`
3. `PUBLIC-OPTIMIZER-NEXT-FAMILY-LITERAL`

## Phase-1 assessment

- scheduled-Chat-native controller/credit logic: **yes**
- richer-mode/protected/manual-user execution required by the accepted mechanism: **none identified**
- optional hosted-runner/Codespaces/artifact/LFS/package/cloud/external API-model compute dependency: **none**
- optional monthly/trial/paid quota dependency: **none beyond the already-granted scheduled-Chat substrate itself**
- incremental monetary cost: **zero**
- repository use: **state/evidence transport only, CAS/rate-limited and fail-closed**
- symbolic switching/recovery trace coverage: sequence 114 `10/10`
- credit reward-hacking counterexample coverage: sequence 115 `8/8`
- natural cross-invocation recovery under root-v4: **not yet observed**

## Termination / blocker

No authoritative-control or own-state blocker. This is an intermediate checkpoint, not global completion. The recurring task remains logically enabled and no scheduler mutation was performed.

## Frontier / exact next action

Frontier is nonempty. Exact next action: **on the next fresh scheduled-Chat invocation, before any public semantic read, fetch the current root/config, current own `LATEST`, and `phase1_chat_native_switch_state_v1_1_2026-08-29T0808_JST.json`; close or fail the predeclared `CHAT-STICKY-CREDIT-v1.1-NATURAL-CROSS-INVOCATION-RECOVERY` item by verifying `credit_total=1` and the one preserved credited transition appears exactly once, with no reconstruction-time reselection or new credit. If it passes, persist one real `pending_switch` at the natural invocation boundary for the already-predeclared persistence item, so a later fresh invocation must resume that exact target before reselection. Audit the predeclared next public optimizer family only after the recovery check.**
