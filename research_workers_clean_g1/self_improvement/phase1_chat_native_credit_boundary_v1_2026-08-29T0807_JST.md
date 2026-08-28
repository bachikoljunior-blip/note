# Phase-1 self-improvement — frontier-bound credit refinement for CHAT-STICKY-CREDIT

Observed in the same frozen root-v4 invocation as sequence 114. No Python/runtime benchmark or external model/API execution was used.

## Problem

`CHAT-STICKY-CREDIT-v1` awards a binary credit for a unique durable milestone. That prevents exact duplicate credit, but a Chat optimizer could still game the reward by inventing many superficially distinct milestone IDs for small rewrites or by splitting a known frontier item after observing evidence.

## Refinement: FRONTIER-BOUND-CREDIT-v1

Credit is valid only when a **predeclared named frontier item changes durable state**.

Each frontier item must exist in the durable controller snapshot before semantic work on that item and has:

- `frontier_item_id`: stable source-qualified ID
- `declared_before_semantic_read`: boolean
- `status`: `OPEN`, `SATISFIED_EXACT_SCOPE`, or `BLOCKED_UNRESOLVED_CHILD`
- `acceptance_or_blocker`: exact falsifiable condition
- `evidence_path`: null until terminal
- `terminal_transition_id`: null until terminal

A credit event is keyed by `terminal_transition_id`, not by prose/artifact filename.

### Credit rule

A frontier item earns exactly +1 when and only when all conditions hold:

1. the item was durably `OPEN` before the semantic read/action that generated the evidence;
2. the item transitions to `SATISFIED_EXACT_SCOPE` or `BLOCKED_UNRESOLVED_CHILD`;
3. an immutable own-role evidence artifact is written and read back;
4. the transition has a unique stable `terminal_transition_id`;
5. the evidence satisfies root-v4: no residual richer-mode/protected/manual-user execution is counted as success, no optional monthly/trial/paid quota is required, and incremental monetary cost is zero for an accepted success;
6. the same transition ID has not already been credited.

Rewording, expanding, or republishing evidence for an already terminal item earns +0. Splitting a terminal item into post-hoc micro-items earns +0 for the historical evidence; new child items may be opened only as future frontier with their own later evidence.

A hard dependency discovery can earn one progress credit when it legitimately transitions a previously open leaf to `BLOCKED_UNRESOLVED_CHILD`, because it closes a search branch and creates a precise unresolved child. It is not acceptance credit for the blocked mechanism.

## Fixed counterexample test

| Case | Trace | Expected credit | Result |
|---|---|---:|---|
| M1 | predeclared `OPEN` item -> exact root-v4 success -> immutable evidence read back -> terminal | +1 | PASS |
| M2 | same terminal transition/evidence is read again next run | +0 | PASS |
| M3 | create a second report that merely rephrases the same already-terminal item | +0 | PASS |
| M4 | after seeing evidence, split one terminal item into three new labels and claim three credits retroactively | +0 retroactive | PASS |
| M5 | predeclared `OPEN` item -> exact hidden Python/LM/cloud executor discovered -> evidence read back -> `BLOCKED_UNRESOLVED_CHILD` | +1 progress credit, mechanism still fails acceptance | PASS |
| M6 | evidence is generated but repository write/readback fails | +0 and no terminal transition | PASS |
| M7 | parent leaf name changes but no named frontier item changes state | +0 | PASS |
| M8 | a new child frontier item is declared only after its parent becomes terminal | +0 now; may earn at most +1 after future evidence | PASS |

Counterexample conformance: **8/8**.

## Additional public optimizer audit

### AFlow

Public source: `AFlow: Automating Agentic Workflow Generation`, arXiv:2410.10762, https://arxiv.org/abs/2410.10762 . AFlow formulates workflow optimization as search over code-represented workflows whose nodes invoke LLMs, using Monte Carlo Tree Search, code modification, and execution feedback.

Root-v4 classification: **HARD_DEPENDENCY_BLOCK** for literal adoption. Its acceptance path requires code execution plus repeated LLM workflow execution/evaluation. The reusable abstraction is tree-structured experience and search over alternatives; those ideas can be represented as Chat-native frontier state, but the literal runtime is not an accepted handoff.

### Automated Design of Agentic Systems / Meta Agent Search

Public source: `Automated Design of Agentic Systems`, arXiv:2408.08435, https://arxiv.org/abs/2408.08435 . The paper describes a meta agent that programs new agents in code and grows an archive of discoveries, evaluating them across tasks.

Root-v4 classification: **HARD_DEPENDENCY_BLOCK** for literal adoption. The meta-agent/code/execution/evaluation loop is an external/richer execution path relative to the scheduled-Chat-only target. The reusable abstraction is the archive of source-qualified discoveries and explicit candidate lineage, which can be kept as role-local Chat state without adopting the code-execution loop.

## Resulting controller semantics

`CHAT-STICKY-CREDIT-v1.1` = `CHAT-STICKY-CREDIT-v1` switching/recovery rules + `FRONTIER-BOUND-CREDIT-v1`.

This refinement removes a concrete reward-hacking path: arbitrary milestone-ID proliferation is no longer sufficient for credit. Credit requires a predeclared frontier transition backed by read-back evidence.

## Exact scope

This is still a deterministic scheduled-Chat protocol test. It does not prove model-independent judgment quality, hard-process-crash recovery, or throughput superiority. It proves only the specified credit invariants over the eight fixed counterexamples plus source-qualified blocking of two literal public agent-optimizer runtimes under root-v4.

## Frontier / exact next action

On the next fresh invocation, reconstruct the v1.1 controller state before public semantic reads and verify both prior credited transition IDs are present exactly once. Then run a natural cross-invocation recovery check and test one `pending_switch` persistence boundary using only role-local repository state: the next run must resume the durable target before any reselection and must not award credit until a predeclared frontier item reaches a terminal state with read-back evidence. Continue auditing public optimizer families, but count code/runtime/model/cloud execution as unresolved children rather than accepted mechanisms.
