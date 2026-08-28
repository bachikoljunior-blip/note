# Self-improvement checkpoint — Phase-1 CHAT-STICKY-CREDIT-v1

- sequence: 114
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- observed checkpoint time: `2026-08-29T08:05:46+09:00`
- predecessor: sequence 113
- bootstrap_valid: **true**
- transport mode: `sha_only_ref_object`
- frozen main SHA: `7bd9c35e1d72de624277bb495cad9accd79f0b4b`
- frozen root blob/control revision: `f3221f10748a3d2ae86d9a544e27e5a44192b007` / `24`
- frozen own config blob/control/config revision: `c5d194b341a70356da196cfb88636ab41fc1bc9f` / `14` / `7`

## Bootstrap hygiene

The first connector attempt used a generic branch payload and exposed excess commit metadata. That payload was quarantined/discarded before semantic work. A valid bootstrap was then rebuilt using the Git ref object `refs/heads/main`, exact-SHA root/config reads, and a repeated ref-object lookup before reading own state or public sources. No excess commit metadata was used semantically.

Main moved after freeze, but a SHA-only freshness check plus exact-head authority reads showed the frozen root/config blobs were unchanged. Current own `LATEST.json` was also still sequence 113 with blob `3b325fafcd257927220e60fd5a53d821cc2f9b06`, so there was no own-state conflict before writes.

## Root-v4 reassessment and actual assignment switch

Root control revision 24 strengthens Phase-1 acceptance: an accepted leaf must eliminate richer-mode/manual/protected execution itself, work with optional monthly/trial/paid quotas at zero, and have zero incremental monetary cost. Repository APIs may be lightweight transport but not compute.

Own clean sequence 112 (`CAL-WILSON-3ARM-v1`) used a Python/scikit-learn timing harness, and sequence 113 used a Python/loopback-HTTP controller. Their findings are preserved as algorithmic/engineering evidence, but their acceptance paths do not satisfy the new root-v4 criterion. This run therefore switched to a Chat-native leaf rather than consuming new timing seeds or launching another HTTP harness.

## New mechanism: CHAT-STICKY-CREDIT-v1

Source-qualified mechanism/report:
- `research_workers_clean_g1/self_improvement/phase1_chat_native_optimizer_switching_v1_2026-08-29T0804_JST.md`
- Git blob after readback: `9b2b11dbbdf05826c4476aa90484a09a6f3c0d9a`

Durable controller state:
- `research_workers_clean_g1/self_improvement/phase1_chat_native_switch_state_v1_2026-08-29T0805_JST.json`
- Git blob after readback: `51714b6f376321ed522ef5eb9f5050d35d1ba4c4`

The controller is deliberately simple and deterministic:

1. reconstruct durable state before semantic work;
2. resume an unresolved durable `pending_switch` exactly, without reselecting or duplicating credit;
3. keep the current leaf only when the immediately preceding semantic run produced a unique durable milestone and the exact next action remains eligible;
4. switch on semantic no-progress or a hard dependency blocker using oldest-eligible + stable-ID tie break;
5. treat repository rate limits and stale-CAS conflicts as transport/state blockers, not semantic assignment failures;
6. award exactly one binary credit only after a unique own-role milestone artifact/checkpoint is read back;
7. never decay credit because of wall-clock gaps or missing scheduled invocations;
8. never mutate the physical recurring scheduler from this worker.

The first credited milestone is `CHAT-STICKY-CREDIT-v1-source-audit-and-10-trace-conformance-20260829`, bound to the read-back report above, with `credit_total=1`.

## Public mechanism audit

Public sources used in the report:

- Hyperband / Successive Halving, JMLR 2018: https://jmlr.org/papers/v18/16-558.html . Reusable principle: adaptive resource allocation/early stop. Literal HPO execution assumes external candidate evaluation resources and is not itself root-v4 acceptance.
- Luby, Sinclair & Zuckerman universal restart schedule: https://www.cs.utexas.edu/~diz/pubs/speedup.pdf . Useful only for safe independent/restartable attempts; blind restarts are not valid for stateful Chat effects.
- OpenAI Scheduled Tasks Help: https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt . Current public documentation says scheduled tasks run in ChatGPT, usage limits apply, active-task limits exist, and tasks may pause. The mechanism therefore uses the already-existing recurring task, creates no extra task, and never scores a missing invocation as an assignment failure.
- GitHub REST contents/rate limits: https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28 and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api . File replacement requires current `sha`; rate-limit guidance uses 403/429 plus reset/retry-after/backoff. Repository access is therefore transport-only and fail-closed on rate limiting.

A second public optimizer audit was completed in this same run after the controller state was persisted: DSPy documents a Python package/runtime, explicit LM configuration (for example `dspy.LM(...)`), and optimizers such as GEPA that compile a program against a metric/trainset: https://dspy.ai/ . Under root-v4, literal DSPy optimization therefore has a residual Python + LM execution dependency and is classified `HARD_DEPENDENCY_BLOCK` for acceptance. Its abstract idea of metric-guided candidate improvement may be reused inside Chat, but the runtime/model handoff is not accepted as the mechanism.

## Switching/recovery test result

A deterministic 10-case symbolic trace was evaluated directly in the scheduled-Chat reasoning path, without Python or another executor. Cases covered:

- milestone -> continue + exactly one credit;
- semantic no-progress -> deterministic switch;
- manual/richer executor dependency -> unresolved-child block;
- optional hosted/cloud/API credit dependency at quota zero -> unresolved-child block;
- GitHub rate limit -> transport block, no credit/switch;
- stale-CAS conflict -> reread, no credit/switch;
- unresolved durable `pending_switch` on a fresh run -> resume exact target, no reselection;
- duplicate milestone ID -> no duplicate credit;
- missing/paused scheduled invocation -> no semantic penalty;
- all known leaves blocked/satisfied -> create/select another Phase-1 leaf, never global-complete or self-disable.

Result: **10/10 specification-level conformance**.

This is not a process-crash injection result. Hard-crash survival of the Chat substrate is not claimed.

## Phase-1 acceptance assessment

- scheduled-Chat-native decision path: **yes**
- residual richer-mode/protected/manual-user execution in `CHAT-STICKY-CREDIT-v1`: **none identified**
- hosted runner / Codespaces / artifact/LFS/package / cloud / external API-model compute dependency: **none**
- optional monthly/trial/paid quota dependency: **none beyond the already-granted scheduled-Chat substrate itself**
- incremental monetary cost: **zero**
- repository usage: **CAS/rate-limited state/evidence transport only; never compute**
- scheduler mutation: **none**
- root-v4 live switching decision exercised: **yes**
- cross-invocation recovery: **not yet naturally observed under root-v4**

## Termination / blocker

No authoritative-control or own-state blocker. The run reached a durable intermediate checkpoint. This is not global completion and the recurring task remains logically enabled.

## Frontier / exact next action

Frontier is nonempty. Exact next action for the next fresh invocation: **before any public semantic read, resolve the current root/config and own `LATEST`, fetch `phase1_chat_native_switch_state_v1_2026-08-29T0805_JST.json`, and verify that milestone `CHAT-STICKY-CREDIT-v1-source-audit-and-10-trace-conformance-20260829` is reconstructed exactly once with `credit_total=1`. That natural fresh-invocation check is the first root-v4 recovery observation. If it passes, continue the current leaf by adding a stricter milestone-boundary rule: credit is valid only when a named frontier item changes state and the immutable evidence path is read back; then run fixed duplicate/micro-milestone counterexamples entirely in Chat. In parallel, audit one additional public self-improvement/agent optimizer and reject any literal runtime/model/cloud executor as an unresolved child rather than a handoff.**
