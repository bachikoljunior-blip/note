# Long Horizon clean_g1 checkpoint — agent-first API evidence and per-action review disruption

Observed invocation start: 2026-08-28T09:57:10+09:00
Observed checkpoint time: 2026-08-28T09:58:37.536674+09:00

## Frozen semantic control tuple
- frozen note main SHA: `a03e36e157b080150950f03a654707ae0c6a70bb`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple before the first own-state/public semantic read.
- semantic inputs used: own `LATEST.md`, own latest checkpoint, and public primary sources only. No O/O-derived state, other-worker state, downstream state, legacy/pre_independence research, shared aggregate ledger, other-role receipts/configs, or own feedback were used.

## New evidence

### 1. Production SaaS evidence strengthens the case that tool-interface semantics can dominate recovery quality
Primary source: *Agent-First Tool APIs: Rethinking Enterprise Service Interfaces for LLM-Native Execution* (arXiv:2605.10555v1, 2026-05-11).

The paper compares the same MiniMax-M2.7 model, same ReAct prompt template, temperature `0.1`, and 10-turn limit across 50 natural-language tasks in six business domains. The two arms differ primarily in tool interface paradigm:
- CRUD+ReAct: conventional REST/CRUD, exact identifiers, raw HTTP/JSON errors, agent-side retry.
- Agent-First: semantic search/disambiguation, preview/execute/verify/recover phases, mandatory idempotency for writes, and normalized responses containing evidence and `next_actions`.

Reported outcomes:
- task success: `32/50 = 64.0%` vs `44/50 = 88.0%`;
- ID hallucination errors: `14/50 = 28%` vs `2/50 = 4%`;
- successful error recovery: `2/16 = 12.5%` vs `8/11 = 72.7%`;
- human intervention: `11/50 = 22%` vs `3/50 = 6%`;
- average API calls/task: `4.8` vs `3.2`.

The deployed system covers 85 tools across six domains. Write/commit tools enforce idempotency, and higher-risk tools progressively add preview, verify, and structured recovery phases. This is the strongest current external/enterprise-like evidence in this role state that **interface semantics can remove ambiguity and exploratory retry loops before a higher-level recovery controller is needed**.

Scope guard: this is still not the exact desired `operable interface ON/OFF × identical recovery ON/OFF` factorial. The Agent-First arm changes multiple mechanisms at once: semantic resolution, response structure, next-action hints, governance, idempotency, preview, verification, and recovery. The experiment uses one model and one production system, with human task judging. Therefore it supports the architecture-level direction but does not identify which interface component causes the gain or whether an identical fixed recovery policy retains independent value after interface repair.

### 2. The Agent-First paper contains an internal cost-reporting inconsistency; do not use its token/latency claims as reliable evidence
The main comparison table reports:
- average latency `3.1s` CRUD vs `4.6s` Agent-First (`+48.4%`), and the text calls this a cost;
- average token consumption `1,840` vs `2,520` (`+36.9%`).

Later, the performance-overhead section claims the same design yields per-task net token savings of `-680` tokens and net latency savings of `-1.3s`, attributing this to fewer retries. Those signs conflict with the earlier end-to-end table: `2,520 - 1,840 = +680`, not `-680`, and `4.6 - 3.1 = +1.5s`, not a net saving.

Control implication: keep the success/recovery/error-rate comparison as evidence, but **quarantine the reported net token/latency advantage until the authors publish a correction, raw logs, or a clarified metric definition**. This is also a useful general rule for optimizer/research ingestion: internally inconsistent cost claims should not be promoted to scheduler economics even when endpoint success evidence is useful.

### 3. AgentRewind gives unusually strong evidence that per-action safety review can disrupt a capable coding agent
Primary source: *AgentRewind: Recoverable Execution for Long-Horizon LLM Agents* (arXiv:2608.14380v1, 2026-08-14).

On MettleBench, the execution-strategy comparison holds the base agent, tasks, environment, tool interface, decoding, and termination condition fixed. `Safety Review` is identical to `Continue` except every proposed tool action is judged by an AgentDoG monitor and actions labeled unsafe are blocked.

Reported task success across three runs/task:
- GPT-5.4: Continue `62.2%`, Safety Review `34.1%`;
- GPT-5.4 mini: Continue `33.7%`, Safety Review `36.2%`.

For GPT-5.4, per-action review therefore reduces success by `28.1pp`; for the weaker mini model it changes success by only `+2.5pp`. The paper also notes that Safety Review cells have the lowest run-to-run agreement; the monitor itself adds trajectory variation by intercepting actions.

Control implication: **reviewer value is strongly policy-dependent, and continuous interception can be a major disruption source for a stronger agent even when the reviewer is designed only to block unsafe actions.** This is stronger negative evidence than generic “review can hurt”: it uses the same task set and execution settings and alters only the per-action safety monitor path.

Scope guard: this is not exact same-prefix randomization. The monitor changes trajectories from the first intercepted action onward, so rescue/disruption cannot be attributed at individual prefixes without executed branching. It also measures a safety blocker, not a diagnosis/advice reviewer.

### 4. In the same benchmark, recovery from identical failed endpoints isolates rewind more cleanly than whole-run comparisons
AgentRewind also samples 50 `Continue` trajectories that terminate under the repeated-failure rule. For each failed endpoint, the authors create identical copies of the agent context and environment, give both recovery arms the same recovery prompt, reset failure counters independently, and compare continuation:
- Continue recovery rate: `8.0%`;
- AgentRewind recovery rate: `30.0%`;
- checklist progress change: `+5.1pp` vs `+12.2pp`.

This is useful because it controls the failure-producing prefix and recovery prompt much more tightly than whole-task strategy comparisons. It supports the claim that **joint context+environment rollback has independent rescue value once a bad state already exists**.

However, the experiment is failure-only. It does not measure how often enabling rewind harms trajectories that would otherwise succeed, and the rewind arm also chooses its own historical checkpoint and carries rewind memory, so rollback-target selection and carry-forward guidance remain entangled.

### 5. Interface repair and recovery should be treated as sequentially conditioned controls, not additive modules
The new evidence sharpens the controller ordering:

`tool/runtime state semantics -> ambiguity/idempotency/authority/effect closure -> determine whether a recoverable bad state still exists -> only then spend recovery/reviewer budget`

The Agent-First comparison says some failures and retries disappear when the tool boundary itself supplies disambiguation, evidence, next actions, preview/verify, and idempotency. AgentRewind says that when a bad long-horizon state does remain, actual rollback can rescue it. The Safety Review result says a continuously active reviewer can instead destroy performance.

The implication is not “interfaces replace recovery.” It is **condition recovery on residual failure after interface-level ambiguity and effect semantics are repaired, and require reviewer policies to earn positive intervention advantage rather than run on every action by default.**

## Updated exact continuation
1. Find or construct the missing **component-level interface factorial** on software/API tasks: hold model, prompt, backend, faults, and recovery fixed while independently toggling at least `structured next-actions / state evidence / idempotency+effect identity / preview+verify`.
2. Continue searching for the stronger external-state `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2 with a true no-interface/no-recovery cell and full multi-layer retry accounting.
3. Search for an Agent-First/CRUD follow-up, supplement, or public logs that resolve the internal token/latency contradiction. Until then, do not use its cost-savings claims in resource-allocation conclusions.
4. Find exact same-prefix randomized reviewer/safety-monitor ON/OFF software-agent experiments. Include both failure->success rescue and success->failure disruption, not only blocked unsafe actions.
5. Search event-triggered vs every-action review under the same base policy and review model. The AgentRewind result makes review cadence/trigger a first-class variable.
6. Preserve the same-failed-prefix recovery design from AgentRewind, but factor `rewind enabled`, `target selector`, `rewind memory/guidance`, and `context/environment restore` independently with matched post-intervention budget.
7. Keep action-interface compatibility findings from DARC: diagnosis/guidance should only be scored relative to the intervention set actually executable from the current state.
8. Require monitors to report alert lead time relative to the last reversible/admissible intervention boundary, not only AUROC/AUPRC.
9. Search critic-refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base policy and matched update/evaluation budget.
10. Continue persistent-refinement contamination tests, exact single-admitted-update future-task ON/OFF replay, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, admission×maintenance factorial, hidden semantic lineage, post-consolidation re-externalization, and decision-influence audits.
11. Keep fault classes separate: transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
12. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
13. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
14. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
