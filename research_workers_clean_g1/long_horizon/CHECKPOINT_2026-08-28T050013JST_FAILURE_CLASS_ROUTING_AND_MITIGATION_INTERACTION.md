# Long Horizon clean_g1 checkpoint — failure-class routing and mitigation interaction

Observed checkpoint time: 2026-08-28T05:00:13+09:00

## Frozen semantic control tuple
- frozen note main SHA: `79ca1416ce33c2b73f74f41ef284a6e4168bce32`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- semantic inputs used: own `LATEST.md`, own latest checkpoint, own sanitized feedback, and public sources only. No O/O-derived state, other-worker state, downstream state, legacy research, shared ledger, or other-role receipts/configs were used.

## New evidence

### 1. AgentCheck provides same-suite, mitigation-specific evidence that generic recovery bundles are not monotonic improvements
Primary paper: AgentCheck: A Reproduce-Intervene-Mitigate Workbench for LLM Agents over MCP, arXiv:2607.11098, revised 2026-07-15, https://arxiv.org/abs/2607.11098
Official repository: https://github.com/aritra741/AgentCheck
Relevant public artifacts inspected read-only:
- `experiments/run_mitigation_impact.py`
- `agentcheck/agent_factory.py`
- `results/mitigation_impact/mitigation_report.json`

The official experiment runner evaluates the same scenario suite under five mitigation configurations: baseline, retry-only, schema-validation-only, injection-scan-only, and an `all` bundle combining all three. The published result artifact gives 10 scenarios per fault type.

Code/result-grounded examples:
- A1 timeout: baseline `3/10`, retry-only `10/10`, all-bundle `6/10`.
- A2 API error: baseline `5/10`, retry-only `10/10`, schema-only `7/10`, injection-scan-only `10/10`, all-bundle `9/10`.
- A4 schema drift: baseline `10/10`, schema-only `9/10`, all-bundle `9/10`.
- B1 stale data: baseline `4/10`, retry-only `3/10`, all-bundle `3/10`.
- B2 contradiction: baseline `6/10`, retry-only `7/10`, schema-only `4/10`, injection-scan-only `5/10`, all-bundle `5/10`.
- B3 wrong answer: baseline `3/10`, retry-only `2/10`, injection-scan-only `2/10`, all-bundle `4/10`.

The repository's own mitigation-effect table labels several of these as regressions. This is unusually useful because it verifies the exact treatment definitions in code and the released outcomes in the same public repository.

Control implication: reliability modules should be selected by failure class rather than accumulated indiscriminately. A generic `all mitigations` policy is not a safe monotone default, even when every component is individually plausible. Retry is especially class-sensitive: it strongly helps visible execution failures in this suite while slightly harming stale/wrong-data classes.

Scope guard: AgentCheck's mitigation set is retry backoff, schema validation and injection scanning. It is not the desired `operable interface × sophisticated recovery` factorial, and it does not include rollback, critic refresh or postcondition verification. The 10-scenario cells are small and model-specific. Treat the result as evidence for class-conditioned routing and non-additivity, not as a universal ranking of mitigations.

### 2. BENCH2ROBUST explicitly separates retry, switch and abstain as different solvability classes
Primary paper: Retry, Switch, or Abstain? Learning Strategy-Aware Tool-Use Policies via Controlled Error Injection, arXiv:2608.11977, submitted 2026-08-12, https://arxiv.org/abs/2608.11977

BENCH2ROBUST constructs stochastic tool environments with three scenario-controlled recovery classes:
- `retry_works`: transient failures where persistence is correct;
- `switch_needed`: the current path is persistently blocked and an alternative tool/path is required;
- `impossible`: all viable paths are blocked and continued attempts should terminate/abstain.

Across seven models from four families and two multi-turn benchmark families, 69/70 noisy configurations reduced pass rate relative to clean tools. On held-out Retail tasks, Bayesian Tool Memory (BTM) improves robustness by up to `+16.8 pp` without retraining. RL learns complementary behavior for persistent and silent failures, and BTM+RL reaches roughly `40.8–45.5%` under injection while preserving clean-environment performance in the tested conditions.

The most useful point for long-horizon control is structural: the same observable fact that a tool call failed does not determine a universal recovery action. The correct action depends on latent recoverability: retry, switch, or abstain. This supports making `recoverability/action class` an explicit state before allocating additional reasoning/recovery budget.

Scope guard: BTM contains hand-structured fallback maps and heuristic constraints, and RL changes the policy. The combined gain does not isolate a runtime selector from training. The benchmarks are controlled stochastic environments, not irreversible real external systems.

## Current synthesis delta
- The strongest current ordering is now: `interface/state evidence -> classify recoverability/action class -> choose one competing recovery action -> verify terminal/effect state`, rather than `failure detected -> stack more reliability modules`.
- `Retry` should be treated as an action available only to a subset of recoverability classes. AgentCheck gives code-verified evidence that retry can improve execution faults while regressing stale/wrong-data cases; BENCH2ROBUST independently formalizes retry/switch/abstain as distinct required strategies.
- Module interaction remains a first-class variable. AgentCheck's `all` bundle can underperform a targeted single mitigation on the exact same fault family; previous verify+retry and reflection+verification evidence is consistent with this non-additivity.
- A practical controller should therefore have an explicit null/abstain option and route by class, not merely score each mitigation as globally helpful.

## Exact continuation
1. Find a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` complete 2×2. Prefer a public benchmark where the true no-recovery/no-interface cell exists and where success, duplicate/unsafe effects, rescue, disruption and cost are all observable.
2. Use AgentCheck only as a public experimental substrate candidate: inspect whether custom mitigation combinations can produce the missing cells without changing scenario semantics. Runnable possibility is not evidence; do not report unrun cells as results.
3. Search critic-refresh cadence experiments with a fixed base-policy checkpoint and matched total critic-update/evaluation budget across `frozen / periodic-k / drift-triggered / continuous`.
4. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials with both failed and benign/success prefixes to measure rescue and disruption together.
5. Search recovery policies that explicitly classify `retry / switch / abstain` or a richer action set under a fixed model/runtime budget, and report class-conditional confusion or wrong-action cost rather than only aggregate success.
6. Preserve rollback-selector-only comparison with alarm, candidate checkpoints, restore/carry-forward/inference state, model, guidance, stochastic coupling and post-intervention budget fixed.
7. Keep failure classes separate: transient interruption, state loss, ambiguous effect, schema error, stale/contradictory data, authority/permission, rate limit, irreversible effect, terminal-belief error, repetitive loop, missing procedure and impossible/no-valid-path conditions should not be pooled into one generic failure bucket.
8. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
9. Locate official SymTrace/SymFail source if publicly discoverable; paper methodology remains evidence but runtime/API behavior stays unverified until code is identified.
10. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
11. Preserve exact tested scope and nonempty frontier; this checkpoint is not global completion.
