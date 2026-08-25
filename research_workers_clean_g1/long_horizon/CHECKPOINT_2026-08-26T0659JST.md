# Long Horizon clean_g1 checkpoint — 2026-08-26 06:59 JST

## Run boundary / semantic freeze
- Worker: `long_horizon`; class: `clean_exploration`.
- Semantic control tuple was frozen before any role-local/public-source semantic read, per control revision 9:
  - frozen note main SHA: `bef75c9992d531894760890e0a092f1e7eb0da0e`
  - `automation_control/DESIRED_STATE.json`: control revision `9`, blob `2e1f998368a6848e737aa108c838edb4ad355cdb`
  - `automation_control/roles/long_horizon.json`: config revision `5`, blob `268523da20c78ce3091344c492ad3d51f6f9e667`
  - `enabled_desired=true`.
- After the semantic-freeze barrier, a SHA-only head recheck observed note main at `f04a4a0b7c6d2d400c8389d32989068b2ced9dc4`. Per the freeze contract, no newer control/config was read or adopted and no result below was reinterpreted under it; any new control is deferred to the next invocation.
- Semantic inputs used: own `LATEST.md`, own latest checkpoint, own sanitized feedback, own role-local config/root manifest, and public primary sources only.
- Forbidden inputs were not read: O/O-derived state, other workers, downstream state, legacy/pre_independence research, shared aggregate execution ledger, other-role receipts/configs.
- The existing own feedback item about observability boundaries was honored.

## Research question advanced
Can the failure-sensing and recovery parts of long-horizon intervention be decomposed more cleanly, and what does a matched comparison say about (a) what crosses the restart boundary and (b) when the interrupted run should actually be cut?

This run primary-verified the richer FailFast/RestartSmart tables that the previous checkpoint intentionally left unpromoted, and extracted Atomix RQ3/combined-stress tables directly from the current arXiv v2 HTML plus the first-party repository README.

## 1) FailFast/RestartSmart gives a near-factorial decomposition of alarm, carry-over, and cut timing
Primary paper: `Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE Agentic Tasks`, arXiv:2608.03222v1, 4 Aug 2026.
Primary PDF: https://arxiv.org/pdf/2608.03222

### 1.1 Same alarm family, different recovery mechanism
Table 3 reports Qwen3.6-27B with vanilla resolve rate `66.6%`:
- 10% FPR:
  - FailFast + RestartSmart: `69.8%` (`+3.2 pp`), FP-lost `15.2%`, TP-recovery `27.6%`, net token overhead `+30.3%`.
  - FailFast + Cold Restart: `67.2%` (`+0.6 pp`), FP-lost `36.4%`, TP-recovery `19.7%`, net token overhead `+17.8%`.
- 25% FPR:
  - FailFast + RestartSmart: `71.8%` (`+5.2 pp`), FP-lost `8.8%`, TP-recovery `28.9%`, net token overhead `+43.8%`.
  - FailFast + Cold Restart: `66.8%` (`+0.2 pp`), FP-lost `27.5%`, TP-recovery `20.2%`, net token overhead `+18.2%`.

The appendix states that reported comparisons reuse the same seeded trajectories and are paired. It also reports paired exact McNemar tests against cold restart pooled over the three policies: `p=8.8e-3` at 10% FPR and `p=4.5e-4` at 25% FPR.

Scope guard: RestartSmart and cold restart do **not** differ only in carry-over. RestartSmart normally waits for a coherent post-alarm edit boundary while cold restart can stop immediately, so Table 3 alone is not a pure recovery-mechanism factorial.

### 1.2 Cut timing is independently load-bearing under aggressive intervention
Table 6 isolates edit-completion patience within RestartSmart on Qwen3.6-27B:
- 10% FPR:
  - Immediate cut: FP-lost `21.2%`, TP-recovery `28.9%`, resolve `69.6%` (`+3.0 pp`).
  - Wait for settled edit: FP-lost `15.2%`, TP-recovery `27.6%`, resolve `69.8%` (`+3.2 pp`).
- 25% FPR:
  - Immediate cut: FP-lost `18.8%`, TP-recovery `22.8%`, resolve `68.8%` (`+2.2 pp`).
  - Wait for settled edit: FP-lost `8.8%`, TP-recovery `28.9%`, resolve `71.8%` (`+5.2 pp`).

The wait policy finds the first edit at/after the abort signal and cuts after five edit-free steps; the paper's stated purpose is to avoid inheriting a fragmented overlay.

Bounded synthesis: the benefit of waiting is tiny at 10% FPR (`+0.2 pp` resolve) but large at 25% FPR (`+3.0 pp`), while false-positive destruction falls from `18.8%` to `8.8%`. This supports treating **alarm time** and **safe cut time** as separate controls, especially when intervention is aggressive.

### 1.3 Carry-over appears useful even before the patience improvement, but significance for this derived contrast is not reported
At 25% FPR, the primary tables allow a useful three-arm point-estimate comparison under the same policy/FPR family:
- cold restart: `66.8%`;
- immediate RestartSmart overlay: `68.8%`;
- waited/settled RestartSmart overlay: `71.8%`.

At 10% FPR the analogous values are `67.2%`, `69.6%`, and `69.8%`.

This suggests two distinct contributions: carrying an optional prior diff can help relative to cold restart, and waiting for a coherent edit boundary can add further value under the higher-FPR regime. However, the paper does not report a dedicated significance test for the `Immediate RestartSmart` vs `Cold Restart` contrast, so this decomposition is a **point-estimate inference**, not a separately established causal result.

### 1.4 Forced prompt correction can reverse sign with policy strength
Table 3 also reproduces SWE-PRM:
- Qwen3.5-9B: `48.2% -> 52.4%` (`+4.2 pp`).
- Qwen3.6-27B: `66.6% -> 63.4%` (`-3.2 pp`).
- Gemma4-31B: `62.2% -> 63.0%` (`+0.8 pp`).

Scope-bounded implication: intrusive correction that helps a weaker policy can harm a stronger one; optional artifact carry-over is a materially different intervention from forcing textual guidance into the active reasoning stream.

### 1.5 Reproducibility artifact status
The primary paper appendix specifies seeds, paired reuse of trajectories, model/scaffold versions, monitor training ranges, and the official SWE-bench Docker harness. In this run I did not identify a first-party repository URL for FailFast/RestartSmart in the primary paper text; the only explicit GitHub URL found in the appendix refers to the reimplemented AgentStop baseline. Treat a first-party code release for this paper as unresolved rather than assuming one exists or does not exist.

## 2) Atomix cleanly separates task recovery from external-effect safety
Primary paper: `Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows`, arXiv:2602.14849v2, 29 May 2026.
Primary HTML: https://arxiv.org/html/2602.14849v2
First-party code: https://github.com/mpi-dsg/atomix

The first-party README describes an alpha Python runtime with core runtime, baseline protocols, serializability checker, sinks, reproducible experiment configs, and local experiment bundle scripts. Generated results are intentionally excluded from git.

### 2.1 Pure task recovery can be statistically tied
At the full tau-bench retail pool (`N=114`, three trials/task, fp=0.10):
- Tx-Full: `67/114 = 58.8%` clean task success.
- Checkpoint-Replay: `61/114 = 53.5%`.
- Fisher exact two-sided `p≈0.50`: statistically tied on RQ1 task-success alone.

This is a strong negative/control result against the simplification `transactional runtime must visibly beat checkpoint replay on ordinary task success`.

### 2.2 The same two mechanisms diverge sharply on irreversible effects
RQ3 uses a real append-only SMTP/webhook sink with five abort sources, `100` invalid-send trials per abort source and baseline (`500` invalid + `500` valid positive controls per row):
- Tx-Full: `0/500` invalid irreversible leaks; `500/500` valid sends released.
- Checkpoint-Replay: `200/500` invalid leaks (`40%`, 95% CI `[36,44]`); `500/500` valid sends released.
- Saga-Compensation: `400/500` invalid leaks (`80%`).
- No-Tx: `500/500` invalid leaks (`100%`).

The paper attributes Checkpoint-Replay leakage to tool-failure/timeout retry paths that re-externalize the irreversible send.

### 2.3 Joint stress exposes the hidden difference that task-success-only evaluation misses
Combined stress requires run-clean = zero invariant violations, stale commits, confirmation leaks, and duplicates.
At mixed faults, fp=0.30:
- Tx-Full: `65%` run-clean.
- Checkpoint-Replay: `25%`.
At fp=0.10:
- Tx-Full: `84%`.
- Checkpoint-Replay: `63%`.

A real-LLM validation with GPT-4o-mini at fp=0.10 reports:
- Tx-Full `90%` run-clean;
- Checkpoint-Replay `73%`;
- TCC `93%`;
- Saga `80%` (`N=30`).

Scope guard: Atomix is a ~2,000-line single-process research prototype. It does not claim semantic validation, distributed deployment, or full distributed crash-safe exactly-once. Its safety depends on complete adapter mediation, accurate scopes/effect classes, compensation handlers where needed, and correct frontier advancement. Misclassification is explicitly unsafe.

## 3) Refined control decomposition
This run strengthens a modular long-horizon recovery model:
1. failure sensing / alarm calibration;
2. intervention decision under recovery-vs-disruption economics;
3. **safe cut timing after the alarm**;
4. historical restore target;
5. carry-forward artifact policy;
6. local reversible-state restore;
7. external-effect settlement / residue accounting;
8. commit-time revalidation;
9. repair stopping.

The FailFast tables now directly support keeping (3) separate from (1): the detector can fire at one step while the best restart boundary is a later coherent edit boundary. Atomix supports keeping (7) separate from ordinary task recovery: checkpoint replay can tie transactional recovery on task success yet be dramatically worse on irreversible-effect leakage and joint run-clean.

## Tempered / rejected simplifications added this run
- `Abort immediately when the monitor fires`: contradicted in the tested Qwen3.6-27B RestartSmart setting at 25% FPR; edit-settling patience improves resolve `68.8 -> 71.8` and cuts FP-lost `18.8 -> 8.8`.
- `Cold restart is a clean baseline and therefore safe`: false-positive loss is much larger than RestartSmart in the tested Qwen3.6-27B runs (`27.5%` vs `8.8%` at 25% FPR), despite lower token overhead.
- `A recovery mechanism that ties on task success is equivalent`: contradicted by Atomix RQ3 and combined stress; Checkpoint-Replay ties Tx-Full on RQ1 full-pool task success but leaks `200/500` invalid irreversibles vs `0/500` and falls to `25%` vs `65%` run-clean under mixed fp=0.30 stress.
- `Prompt correction is generally helpful`: contradicted by the paper's own reproduction on Qwen3.6-27B (`66.6 -> 63.4`).

## Nonempty frontier
1. Find a **strict detector-quality factorial**: hold recovery mechanism, cut rule, carry-forward, policy, tasks, and FPR budget fixed while varying detector quality/calibration, then measure final success/disruption. FailFast varies monitor size for recall but does not report the corresponding full recovery outcome for that ablation.
2. Find a **strict historical-target selector factorial**: same alarm, same candidate checkpoints, same restore/carry-forward, same model, same retry/token budget; vary only which prior checkpoint is selected.
3. Search controlled negative evidence on subgoal decomposition/folding: wrong subgoal boundaries, stale folded summaries, or over-aggressive compression that reduce final task success.
4. Verify commit-time authorization/freshness studies that revalidate authority/resource versions immediately before durable effects after recovery.
5. If a first-party FailFast/RestartSmart code artifact appears, verify the exact cut/pairing implementation against Tables 3/6 rather than inferring from prose.

## Exact continuation
Next run: first resolve current control again under the SHA-only semantic-freeze protocol. Then prioritize a detector-quality factorial where the recovery actuator is fixed, followed by a historical-target-only selector comparison. Keep the subgoal/folding negative-evidence branch alive. Do not re-read shared observability state; write only role-local receipts.
