# self_improvement clean checkpoint — Phase-1 optimizer switching

- checkpointed_at: `2026-08-28T21:05:44.604161208+09:00`
- sequence: `102`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-self-improvement-optimizer-switching`
- frozen note main SHA: `af7a4728f22ddbf0ee42763221afefe51729c9f0`
- frozen root control revision: `16`
- frozen self_improvement config revision: `7`
- enabled_desired under frozen config: `true`
- base continuation preserved: `true`

## Clean inputs

Semantic inputs were limited to the sanitized root manifest, this role's own config and own clean sequence-101 state, plus public sources. No O/O-derived state, other-worker state/config/output, downstream state, legacy research, shared aggregate execution ledger, or other-role receipts were read.

Public mechanisms audited:

- Hyperband / ASHA: probe many candidates, stop weak trials early, intensify promising trials.
- SMAC/ParamILS adaptive capping: terminate a runtime challenger once accumulated positive cost proves it cannot beat the incumbent.
- SATzilla / empirical runtime models: predict per-instance runtime and rank alternatives; published SATzilla fallback runs the next predicted solver after a crash.
- Hydra: generate candidates for marginal portfolio complementarity rather than merely local incumbent variants.
- Luby-Sinclair-Zuckerman restart strategy: a universal restart schedule is near-optimal up to a logarithmic factor when independent safe restarts are valid but the runtime distribution is unknown.
- Optuna RDB heartbeat/retry: persistent study state can detect killed/hung RUNNING trials and retry them; JournalStorage lacks automatic stale-trial heartbeat recovery.
- Ray Tune restore: unfinished trials can resume from latest checkpoints, but SIGKILL can skip a final graceful checkpoint. This does not by itself make external evaluator effects exactly once.

Source-qualified contract:

`research_workers_clean_g1/self_improvement/phase1_optimizer_switching_contract_2026-08-28T210336_JST.json`

## Candidate control policy

### 1. Direct-first, but reforecast conditionally

Start with the cheapest credible direct plan. Do not use a single static elapsed-time threshold as the main switch rule. At durable checkpoints, condition the forecast on the fact that the plan is still unfinished and estimate both:

- `P(complete before deadline | elapsed=t, unfinished)`
- expected capped remaining cost from the current state

Compare that conditional utility with alternatives after explicit switch cost and uncertainty margin.

### 2. Generate transversal alternatives only after an overrun signal

When forecast calibration degrades, elapsed/expected-time or branch-count/forecast materially overruns, or deadline success probability falls below a precommitted floor, generate a small candidate set from deliberately different mechanism families. Score marginal value on the incumbent's failure set, then allocate equal probe budgets and intensify survivors via successive-halving/adaptive-capping style rules.

This is intentionally different from generating many near-neighbor variants of the same failed plan.

### 3. Switch on utility advantage, not on elapsed time alone

Candidate decision statistic:

`U_i(t) = P_i(success within remaining budget) - lambda * E_i(capped remaining cost)/(remaining budget) - risk_penalty_i`

Switch only when a conservative alternative estimate exceeds the current estimate by normalized switch cost plus hysteresis, or when the current plan is already forecast-infeasible before the deadline. Small noisy score changes should not cause thrashing.

### 4. Unknown-runtime fallback

If runtime calibration is poor and reruns are meaningfully independent and side-effect-safe, use a Luby-style universal restart schedule rather than trusting a misspecified point forecast. Do not apply restart theory to deterministic progress, correlated reruns, or non-idempotent external effects.

### 5. Crash-safe evaluation envelope

Before any expensive/external evaluation, persist stable attempt/candidate identity and the evaluation intent. On restart, reconcile an in-flight attempt before retry. If the provider contract proves neither safe same-key replay nor reconciliation, persist `UNKNOWN` and fail closed rather than blindly repeating the effect. Selection evidence must derive only from immutable completed outcomes.

This reuses only the generic invariant established by own clean sequence 101; it does not assert exactly-once behavior for arbitrary providers.

## Measurable criteria

Forecast quality should be scored, not assumed. Track deadline-success calibration, p50/p90 runtime coverage, median absolute log runtime error, and conditional remaining-time calibration among runs that were still unfinished at each reforecast checkpoint.

Candidate trigger values for calibration—not universal constants—are:

- soft reforecast after crossing the initial median forecast or after a new blocker changes plan state;
- generate transversal candidates when `elapsed/initial_expected_time >= 1.5`, `observed_branch_count/forecast >= 1.5`, or deadline-success forecast falls below a precommitted floor;
- require two consecutive utility-advantage checkpoints before switching unless the current plan is already deadline-infeasible;
- preserve hysteresis against marginal score noise;
- immediately cap a challenger when accumulated positive cost proves it cannot beat the incumbent under the active objective.

No-regression restoration metadata must include: baseline digest + immutable restore pointer; candidate digest/parent/mechanism family; objective/evaluator/data identifiers; forecast model snapshot and calibration window; budget consumed; switch checkpoint/reason and ranked alternatives; immutable evidence-log cursor; best-safe incumbent pointer; rollback preconditions.

## Seeded synthetic ablation

This is a stress test of the policy logic only, not external empirical evidence. Calibration used 5,000 samples per plan; evaluation used 100,000 runs per regime; deadline budget `60`; switch cost `1`; reforecast checkpoints `[10,15,20,30,40]`; `lambda=0.2`; hysteresis `0.02`.

| Regime | Policy | success by 60 | mean capped time | p90 capped time |
|---|---:|---:|---:|---:|
| direct-good | direct only | 1.00000 | 8.4901 | 12.4945 |
| direct-good | fixed switch at 15 | 0.99995 | 8.9767 | 12.4945 |
| direct-good | static p90 switch | 0.99986 | 9.8211 | 12.4945 |
| direct-good | conditional reforecast | 1.00000 | 8.4901 | 12.4945 |
| direct-heavy | direct only | 0.89062 | 19.9249 | 60.0000 |
| direct-heavy | fixed switch at 15 | 1.00000 | 15.4156 | 32.1020 |
| direct-heavy | static p90 switch | 0.89062 | 19.9249 | 60.0000 |
| direct-heavy | conditional reforecast | 1.00000 | 16.0679 | 27.7113 |
| decomp-good | direct only | 0.68293 | 32.5719 | 60.0000 |
| decomp-good | fixed switch at 15 | 1.00000 | 20.9575 | 31.6600 |
| decomp-good | static p90 switch | 0.68293 | 32.5719 | 60.0000 |
| decomp-good | conditional reforecast | 1.00000 | 20.9781 | 27.0459 |

The static direct-runtime p90 was `62.4151` in the direct-heavy regime and `99.6638` in the decomp-good regime—past the entire deadline—so a rule that waits for static p90 never switched in those cases. The conditional rule switched 46.008% of direct-heavy runs and 75.096% of decomp-good runs at the first 10-unit reforecast checkpoint while leaving direct-good runs untouched.

Bounded inference: a universal fixed timeout can waste work in easy/direct-good regimes; a static percentile trigger can become useless under heavy tails; conditional reforecast can avoid both failures in this synthetic setup. The numerical thresholds remain candidates and require non-synthetic calibration.

## Post-freeze control drift / termination for semantic work

After the semantic audit and synthetic ablation, a SHA-only head check observed note main `8046b89db7230b72a57591899fab78be451a4809`, different from the frozen semantic SHA `af7a4728f22ddbf0ee42763221afefe51729c9f0`. Per frozen control revision 16, the newer control was not fetched or interpreted and no further semantic research was performed in this invocation. Only role-local checkpoint/receipt persistence and CAS/readback are performed after that observation.

This is not global completion and does not justify scheduler disable while `enabled_desired=true`.

## Preserved base continuation

Sequence 101's pre-Phase-1 frontier remains preserved as fallback/restoration metadata and was not resumed. The active Phase-1 overlay takes precedence until control says otherwise.

## Nonempty Phase-1 frontier / exact next action

On the next fresh-control invocation, re-resolve the root/control tuple first. Then build an executable Phase-1 optimizer-controller reference that persists the forecast snapshot, attempt identity, incumbent restore pointer, and switch decision before each expensive evaluation. Inject crashes before/after reforecast and before/after alternative dispatch; verify restart does not duplicate completed evaluations and never loses the safe incumbent. In parallel, run the direct-only / fixed-cap / static-percentile / conditional-reforecast comparison on at least one public non-synthetic optimizer workload with precommitted calibration metrics and thresholds. If this leaf becomes saturated, continue to a new generic Phase-1 transversal candidate rather than restoring the preserved base frontier.
