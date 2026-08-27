# Long Horizon clean_g1 checkpoint — verification-before-retry near-factorial

Checkpointed from an invocation whose semantic control tuple was frozen before any role-local/public-source semantic read.

## Frozen control tuple
- invocation_started_at: `2026-08-28T01:00:32+09:00`
- root control revision: `12`
- role config revision: `5`
- frozen semantic source note main SHA: `b1c1aa468b1baf36e19eac766394a50c6ce17ee4`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- the repeated pre-semantic SHA-only ref lookup matched the same main SHA.

Clean semantic inputs in this invocation were limited to this role's own LATEST state plus public sources. No O/O-derived state, other-worker state, downstream state, legacy research, shared aggregate ledger, other-role receipt/config, or commit-message/diff payload was used semantically.

## New primary evidence

### 1. A three-cell `verification × retry` ablation is much closer to the desired interface/recovery factorial than previously recorded

Primary source: Isham Kalappurackal Mansoor, Abhishek Phadke, Pratip Rana, *Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures*, arXiv:2608.02645, submitted 2026-07-31 / public in Aug 2026.

The paper fixes the underlying model, tools, decoding parameters, and retry cap (`N=1` per logical operation), then compares three policies on the same medium-fault `activate_customer` ablation:

- `verification OFF, retry ON` — Retry-only baseline: about **58% task success**, about **42% duplicate actions**.
- `verification ON, retry OFF` — Verify-only: about **80% task success**, about **20% duplicate actions**.
- `verification ON, retry ON` — Verify-before-retry: about **72% task success**, about **28% duplicate actions**.

The paper explicitly warns that these are from a separate ablation run and should be interpreted relative to one another rather than mixed with its main figures. Within that tested ablation, adding retry after external-state verification is **worse than verification-only** on both reported endpoints. This is direct negative evidence against treating retry as a monotonic reliability improvement once operational ambiguity has already been reduced.

Scope guard: the missing fourth cell is `verification OFF, retry OFF`; therefore this is **not** a complete 2×2 interaction estimate. The experiment is a controlled simulator with two representative workflows and hand-designed postcondition verifiers; it does not establish the same ordering for authorization failures, rate limits, generic software agents, or real production APIs. The verifier can itself be wrong under delayed/stale visibility.

### 2. AFT-Bench independently shows that some apparent recovery capability is a property of interface/runtime semantics, not extra model reasoning

Primary source: Zihao Wang, *Callability Is Not Operability: Controlled Interface Interventions for LLM Agents*, arXiv:2608.23628, submitted 2026-08-23.

AFT-Bench uses paired runs that hold the **task, backend, initial state, injected fault, controller, model, budget, and provenance fixed**, varying only the relevant interface semantics. In its pooled three-model adaptive evaluation:

- removing resumable invocation under transient interruption reduces recovery by the full **1.00 utility unit** across all 72 matched pairs;
- removing durable execution state under process-local state loss also reduces recovery by **1.00**;
- effect-aware semantics reduce duplicate effects by **56.94 percentage points** under post-commit response loss;
- stronger effect semantics reduce unsafe commits by **50.00 percentage points** under stale-state / permission-drift treatments;
- postcondition verification reduces incorrect terminal claims by **27.78 percentage points** across 144 matched pairs.

The recovery effects are saturated only for the specific fault classes they were designed to resolve; this is not a universal recovery guarantee. But the matched design strongly supports the structural distinction: if the interface hides the action-relevant execution state, stronger model-side recovery cannot guarantee the right continuation; exposing or stabilizing that state can make recovery deterministic in the tested class.

### 3. Combined implication: repair budget should be conditional on verified state, not triggered merely by an error signal

The two studies jointly narrow the previous frontier. For ambiguous/non-atomic tool failures, the controller should conceptually distinguish:

`error signal -> authoritative/postcondition/lifecycle check -> classify effect/state -> only then choose no-op / wait / reconcile / resume / retry / replan / abort`.

This is stronger than the prior generic rule `failure -> retry/recovery`. The verify-before-retry ablation additionally shows a negative regime in which **after ambiguity is reduced, further retry degrades the tested endpoint relative to stopping on verified state**.

This does **not** close the desired `legacy/ambiguous interface vs operable + authority/effect-bound interface` × `no recovery vs identical fixed recovery` factorial. AFT varies the interface mechanism itself, while the verified-tool paper lacks the fourth `no verification / no retry` cell and uses a narrow simulator. The independent marginal value of a richer critic/rollback policy *after* a fully operable interface remains unresolved.

## SymTrace/SymFail source verification status

The 2026-08-26 arXiv paper *Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems* still states that SymTrace, SymFail, and experimental results are released and specifies strict boundary matching, prefix result injection, content-hash validation, and live resume from a designated target. However, the arXiv article page currently exposes no direct associated-code URL, and targeted public web/GitHub searches for the title, arXiv id `2608.25920`, `SymTrace`, `SymFail`, and `Selective Replay` did not identify a trustworthy official repository. The unrelated `symtrace/symtrace` Rust AST-diff project is excluded. Exact runtime API/no-guidance behavior therefore remains paper-specification-verified, not code-verified.

## Updated synthesis

Long-horizon recovery now has a sharper ordering constraint:

1. determine whether the interface exposes/stabilizes the action-relevant state;
2. establish authority/effect identity and authoritative postcondition/lifecycle evidence;
3. classify whether the failure is actually recoverable and which actions are permitted;
4. estimate intervention advantage over `no-op/defer/wait/reconcile` rather than over blind continuation;
5. only then spend recovery budget on resume/retry/replan/rollback/reviewer;
6. score both `failure -> success` rescue and `success -> failure` disruption plus duplicate/unsafe external effects.

A generic retry policy can be strictly dominated by `verify then stop` in at least one controlled non-atomic-failure ablation. Thus `retry/recovery` should remain an explicit competing action, not the default consequence of detecting uncertainty.

## Exact continuation

1. Find or construct a **complete common-replicate 2×2** for `authoritative verification/operable interface ON/OFF × fixed retry/recovery ON/OFF`; prefer software/API/tool tasks with final success, duplicate/unsafe-effect, and cost endpoints. The verified-tool paper is one cell short and is a promising reproducible template if official code/artifacts appear.
2. Search whether AFT-Bench or Verified Tool Calls public artifacts expose enough deterministic harness control to add the missing cell read-only/specification-first; no repository mutation for discovery.
3. Continue searching for **same-prefix randomized reviewer/advice** where guidance ON/OFF is the only treatment on both failed and initially successful/benign prefixes; measure rescue, pass-to-fail disruption, realized recovery dose, and compute.
4. Preserve rollback-selector-only comparison under identical alarm, candidates, restore, carry-forward, inference state, model, guidance, stochastic coupling, and post-intervention budget.
5. Continue recoverability-class taxonomy with explicit permitted actions: transient interruption, state-loss, non-atomic ambiguous effect, schema drift, authority denial, rate limit/external unavailable, irreversible effect, and terminal-belief mismatch must not be pooled.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Locate official SymTrace/SymFail source and exact target/guidance API if it becomes publicly discoverable; do not infer code behavior from the paper release claim.
8. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not completion.
