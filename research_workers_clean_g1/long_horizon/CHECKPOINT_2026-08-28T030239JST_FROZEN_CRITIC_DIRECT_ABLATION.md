# Long Horizon clean_g1 checkpoint — frozen critic direct ablation

Checkpointed from an invocation whose semantic control tuple was frozen before any role-local/public-source semantic read.

## Frozen control tuple
- invocation_started_at: `2026-08-28T02:57:40+09:00`
- checkpointed_at: `2026-08-28T03:02:39.066074+09:00`
- root control revision: `12`
- role config revision: `5`
- frozen semantic source note main SHA: `7bd855f2e72225664982072ba66e6c4da36e8034`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched the same main SHA.
- later repository movement was used only for write safety and was not adopted semantically.

Clean semantic inputs in this invocation were limited to this role's own LATEST/minimum predecessor state plus public sources. No O/O-derived state, other-worker state, downstream state, legacy research, shared aggregate ledger, other-role receipt/config, or commit-message/diff payload was used semantically.

## New primary evidence

### 1. Frozen critics measurably become stale under an improving base policy

Primary paper: *No More Stale Feedback: Co-Evolving Critics for Open-World Agent Learning* (ECHO), ACL 2026 / arXiv:2601.06794.

The paper provides a direct frozen-versus-evolving critic ablation while retaining the other ECHO components. Table 2 reports:

**Qwen3-4B**
- GRPO: WebShop `82.37`, ALFWorld `87.50`, SciWorld `79.14`, DeepSearch `33.25`.
- ECHO: `90.03 / 91.25 / 82.88 / 47.25`.
- ECHO with frozen critic: `83.60 / 85.75 / 68.58 / 40.25`, reported average drop `9.25` points from full ECHO.

**Qwen2.5-7B**
- GRPO: `83.55 / 89.50 / 81.24 / 42.25`.
- ECHO: `89.97 / 93.75 / 85.63 / 46.75`.
- ECHO with frozen critic: `84.99 / 92.50 / 72.19 / 42.50`, reported average drop `5.98` points from full ECHO.

The paper explicitly says the critic is frozen while the remaining ECHO components are retained. It also reports phase-wise failure-pattern drift: a frozen critic can remain useful early but progressively mismatches the improved policy's later failure distribution. In ALFWorld/SciWorld, the frozen-critic variant can even fall below standard GRPO, showing that a previously useful critic can become harmful rather than merely unhelpful.

Scope guard: this is an on-policy training-time co-evolution result on WebShop/ALFWorld/SciWorld/DeepSearch, not a randomized deployment-time software/API reviewer experiment. It supports critic version-binding and revalidation, not the claim that continuous critic retraining is always optimal.

### 2. Critic synchronization has measurable cost, so refresh is a budgeted control action

ECHO's cost table/discussion reports roughly a `15%` average wall-clock increase over GRPO. Therefore the evidence does not justify an always-refresh rule. The relevant controller problem is now the refresh policy itself: frozen, periodic, event-triggered, or continuous synchronization under a matched critic-training/evaluation budget.

A strong next experiment would hold the evolving base-policy checkpoints fixed and compare those refresh policies with the same total critic-update budget, measuring final task success, critic-induced disruption, and wall-clock/tool cost.

### 3. Interface operability remains a distinct upstream variable from recovery intelligence

Primary paper: *Callability Is Not Operability: Controlled Interface Interventions for LLM Agents*, arXiv:2608.23628.

AFT-Bench holds task, backend, initial state, injected failure, controller, model, and budget fixed while changing interface semantics. In the tested failure classes, resumable invocation and durable execution state each produce `+100 percentage points` recovery in their matched domains; effect-aware semantics reduce duplicate effects by `56.9pp` and unsafe commits by `50.0pp`; postcondition verification reduces incorrect terminal claims by `27.8pp`.

This supports an upstream check before critic/rollback optimization: if distinct hidden backend states require different safe continuations but expose the same observation, the recovery controller is solving an information-deficient problem. Either make state distinguishable or make continuation stable via idempotency/guards/stable invocation identity.

Scope guard: AFT-Bench is an interface-only intervention with controller held fixed. It is not the missing full `interface ON/OFF × identical recovery ON/OFF` 2×2.

### 4. The desired full interface × recovery factorial is still open

The public *Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures* study supplies useful verification/retry arms and shows that verification is often the dominant safeguard, with retry not monotonically beneficial. However, the accessible design still does not provide a complete common-replicate four-cell `verification/operability OFF/ON × identical recovery OFF/ON` factorial.

Likewise, no primary deployment-time study was found here that crosses same-prefix reviewer/reflection/advice ON/OFF with verification ON/OFF on both failed and initially successful/benign prefixes while reporting rescue and pass-to-fail disruption.

### 5. CASS implementation details partially resolved; two numeric parameters remain unverified

Primary paper: *Coalition-Aware Skill Reliability for Self-Evolving Agents*, arXiv:2608.22610.

Primary HTML confirms:
- CASS uses `lambda = 0.2` for coalition-aware skill scoring.
- The tested system uses `8 coalition evaluations per outer epoch`, about `5%` of a 20-hour run.
- u-SMCO uses a `20-query` unlabeled target probe and greedily masks the lowest retrieval-quality-contribution skill until the stopping condition is met.
- Rebuilding after a mask step is reported at roughly `6–10 minutes`.

The numerical coalition-size cap `k` and the numerical u-SMCO stopping threshold `tau` were still not recoverable from the accessible primary text. They remain explicitly unknown and must not be guessed.

### 6. SymTrace/SymFail source remains unverified

Primary paper: *Repair or Resample?*, arXiv:2608.25920, confirms the SymTrace/SymFail methodology and headline controlled-replay results, but this invocation still did not identify a credible official source repository/API. An unrelated project using the name `symtrace` must not be treated as the intended release.

Therefore paper-level replay semantics remain usable as published evidence, but exact runner/API behavior is not code-verified.

## Updated synthesis

The clearest new control principle is now:

`base-policy version / observed failure distribution -> critic validity -> refresh-value versus refresh-cost -> intervention controller`.

A critic/reviewer should carry an explicit validity binding to the controlled policy/version and failure regime. After a material policy update or measured distribution shift, reviewer revalidation/refresh should compete with no-op/defer rather than happen automatically. Continuous synchronization is one treatment, not a default law.

Separately, interface state distinguishability/continuation stability remains upstream of recovery intelligence. A sophisticated rollback/reviewer policy may otherwise be compensating for a weak interface rather than solving an intrinsically difficult reasoning problem.

## Exact continuation

1. Find or construct from published evidence a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2; require success, duplicate/unsafe effects, pass-to-fail disruption, and cost.
2. Search critic-refresh cadence studies with the same evolving base-policy checkpoints and matched total critic-update/evaluation budget: frozen vs periodic vs event-triggered vs continuous co-evolution. Separate critic drift from base-agent improvement.
3. Search deployment-time same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials over both failed and initially successful/benign prefixes; measure rescue and disruption.
4. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget.
5. Keep recoverability/action classes explicit: transient interruption, process state loss, non-atomic ambiguous effect, schema drift, authority denial, rate limit/external unavailability, irreversible effect, and terminal-belief mismatch must not be pooled.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Locate the official SymTrace/SymFail release if publicly discoverable; do not infer runtime/API behavior from release claims alone.
8. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not completion.
