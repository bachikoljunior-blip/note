# Long Horizon clean_g1 checkpoint — shadow recovery admissibility factorial

## Frozen control / provenance

- role: `long_horizon`
- class: `clean_exploration`
- enabled_desired: `true`
- root control: parsed `control_revision=22`, Git blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- own role config: parsed `config_revision=6`, Git blob `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- frozen semantic `note/main` SHA: `bc0ed3133e95dad3cd647d4e83d8901a19b6e6a0`
- own `LATEST.md` blob consumed at semantic freeze: `1cc7d7e8372a3bbdc3f27daf96aad98f5dfbf0f4`
- public Agent-libOS source pin: `yingqi-z20/Agent-libOS@72366eecc9e04cc7445a5ea51d7b5f236aa4d1e9`
- allowed semantic sources used: own clean long_horizon state + public sources only
- forbidden O / other-worker / downstream / legacy semantics were not used.
- late write-safety head observation: `fcab4ec165c6fea4c086f5f169767f34024ffd75`; newer-head semantic content was not adopted. Exact root/config blob recheck at that head matched the frozen identities above.
- `bootstrap_valid=true`

## New verified public-source findings

### 1. Public `recover` is itself coupled to lifecycle status

Pinned `agent_libos/runtime/task_runs.py` (blob `473b812a81247f00c79083b7caf4b4aa990d7d32`) makes the causal coupling explicit:

- `recovery_options(run_id)` returns no options unless the Run is already `TaskRunStatus.NEEDS_ATTENTION`.
- For an `unknown_effect` / `effect_unsettled` blocker it iterates the same raw unsettled effects and emits an `effect_receipt` option only when the provider exposes `verify_external_effect_receipt`; the option binds `run_id`, `effect_id`, expected transaction state, and runtime epoch into a server-derived identifier.
- `recover(...)` does not accept an arbitrary option. It recomputes `self.recovery_options(run_id)`, indexes by the caller-supplied `option_id`, and rejects an id absent from that server-derived set.
- `_recover_effect_receipt(...)` then calls `settle_external_effect_from_authoritative_receipt(...)` with the option's exact effect id, expected state, provider receipt, and runtime epoch.

This means a naive lifecycle-gate OFF ablation can mechanically remove the very state (`needs_attention` + blocker) that makes recovery visible/valid. Factor A (gate) can therefore change the treatment surface for Factor B (recovery), invalidating a nominal 2×2 causal interpretation.

### 2. The same unresolved-effect evidence participates at multiple lifecycle decision points

The same pinned `task_runs.py` uses `_unsettled_effects(run_id)` in multiple control paths, including before dispatch, resume, cancellation convergence, stopped-run recovery projection, and effect recovery cleanup. It also has distinct `_projection_effect_blocker(...)` and `_terminal_convergence_blocker(...)` paths. Therefore deleting or monkeypatching the raw unsettled-effect view would alter both lifecycle blocking and recovery-option derivation; it is not a gate-only intervention.

The public Durable Task Runs guide independently states that an unresolved dispatched/unknown effect moves a Run to `needs_attention`, blocks downstream dispatch, and that `recovery-options` is a read-only, server-derived evidence surface while `recover` is the separate mutation. Effect receipt recovery is verified before authoritative effect settlement. This agrees with the code-level coupling above.

### 3. The repository already contains a deterministic crash substrate and a benchmark-local monkeypatch precedent, but the earlier exact `ablations.py` claim was wrong

Pinned `benchmarks/durable_task_runs/crash_harness.py` (blob `0645182bacfa63735ba7205f4fba74010ca8ce0c`) defines durability barriers `RUN_COMMITTED`, `ACTION_COMMITTED`, `EFFECT_PREPARED`, `PROVIDER_DISPATCHED`, `PROVIDER_RESULT_DURABLE`, `RESUME_POINT_COMMITTED`; its `FsyncProviderLedger` is explicitly independent of RuntimeStore and records effect/idempotency/receipt evidence durably. Its pass contract requires at most one external dispatch and preserves `unknown_effect` as `needs_attention` where appropriate.

Pinned `benchmarks/durable_task_runs/crash_worker.py` (blob `c479103b713af36e6fc71d62c146ff5bce5c0ece`) installs benchmark-only crash interventions by directly replacing runtime methods such as `record_validated_transcript`, `expected_tool_id_for_pending_action`, `stage_completed_transcript`, `record_completed_transcript`, and `jsonrpc.call`, then restoring process state only through normal reopen semantics.

Correction to prior checkpoint/user-facing wording: the pinned `benchmarks/durable_task_runs/` directory does **not** contain the previously claimed `ablations.py`; the verified monkeypatch precedent is `crash_worker.py` (plus instrumentation-style method replacement in `recovery_scale.py`), not `ablations.py`/`MethodType`. Do not repeat the old exact-path claim.

### 4. A real-LLM extension surface exists but is not the missing factorial

Pinned `experiments/run_durable_task_run_evaluation.py` delegates to `benchmarks/durable_task_runs/live_evaluation.py`. The latter can run the repository-maintenance TaskRun scenario with either the configured real LLM or an injected deterministic provider and already checks restart survival, settled effects, no unknown external effect, and no-redispatch command replay. It is a useful later behavioral extension, but it does not independently toggle lifecycle blocking and recovery execution.

## Revised causal model

The missing experiment should be represented as four planes rather than two undifferentiated runtime modes:

1. **Evidence / identity plane — always ON.** Keep provider/system-of-record truth, stable effect/request identity, authorization-consumption identity, raw external-effect evidence, verifier, and idempotency substrate identical in every cell.
2. **Recovery-admissibility plane — always ON for measurement.** Derive and freeze the same evidence-bound recovery option(s) from the same ambiguous-effect prefix. This is a shadow/counterfactual surface when production lifecycle status would otherwise hide the option.
3. **Lifecycle-blocking plane — Factor A.** Toggle only whether unresolved-effect evidence blocks the next lifecycle decision (dispatch/resume/projection/terminalization), while recording phase-specific `would_block` telemetry in both arms.
4. **Recovery-execution plane — Factor B.** Toggle only whether the Host executes the already-frozen authoritative receipt settlement before the matched next lifecycle decision.

A gate-OFF arm must never achieve its effect by deleting `_unsettled_effects`, changing provider truth, rebinding an option to a newer state, or inventing a new recovery id. Likewise a recovery-OFF arm must preserve option visibility and raw evidence; it simply does not execute the recovery transition.

## Smallest clean first experiment

Use a deterministic common prefix where the provider has durably committed exactly one external effect but the Runtime observes an ambiguous dispatched/unknown outcome. Serialize/copy the RuntimeStore plus independent provider ledger plus durable authorization-consumption state **before any branch-specific lifecycle progression**.

For every cloned cell, first compute or replay an identical shadow `TaskRunRecoveryOption` binding from that frozen evidence. Then:

- `recovery=ON`: settle the exact same authoritative provider receipt under the frozen option binding before the next lifecycle decision.
- `recovery=OFF`: do not mutate effect settlement.
- `gate=ON`: apply the ordinary unresolved-effect blocker at the next matched lifecycle decision.
- `gate=OFF`: suppress only that blocking consequence for that one decision, preserving raw evidence, blocker counterfactual, and frozen recovery-admissibility record.

Immediate hard outcomes: realized provider effect count, Runtime transaction/effect state, premature downstream dispatch or completion, final Run status, recovery-option divergence, receipt-verifier result, and `would_block` phase. The expected qualitative cell structure is: ON-gate/OFF-recovery safely blocks; OFF-gate/OFF-recovery exposes unsafe continuation; either recovery-ON cell should first settle the same provider truth and then continue without duplicate dispatch. This is a mechanism test, not yet a powered task-success claim.

A second longitudinal arm should deliberately allow the post-gate policy to repropose the same logical write with a fresh operation/token identity. Then measure duplicate physical effects and authorization-consumption over-budget separately; provider idempotency and durable authorization consumption remain independent controls.

## Minimal implementation direction

Because public `recover()` recomputes `recovery_options()` and `recovery_options()` requires `needs_attention`, simply turning the gate off cannot be paired with unmodified public recovery in the same cell. The least confounded benchmark-only route is to freeze the server-derived option set at the common ambiguous prefix and install a per-Runtime shadow option provider **identically in all four cells** before branching. Recovery ON can then exercise the existing receipt-settlement machinery with the exact frozen binding; recovery OFF leaves it unused. Separately intercept the narrow lifecycle blocker decision(s), not the raw evidence query.

Do not alter production defaults. Follow the repository's existing benchmark-local method-replacement pattern and restore original methods after each cell. First validate one phase (next dispatch) before expanding the factor-A interception set to resume/projection/terminalization.

## Scope / negative evidence

- No completed real-model gate×recovery four-cell experiment was found in this run.
- The public source establishes implementation structure and a viable deterministic harness, not an empirical claim that gate or recovery has a particular task-success effect size.
- `live_evaluation.py` is a future extension surface, not evidence for the four-cell itself.
- The deterministic crash harness' idempotent JSON-RPC provider is not yet verified here to expose the exact authoritative receipt verifier needed for the shadow `effect_receipt` arm; that remains an implementation check.

## Exact continuation

1. Trace the pinned provider/plugin path used by `verify_external_effect_receipt(...)` and determine whether the existing Fsync provider can be minimally extended to return an authoritative receipt from its independent ledger without changing startup reconciliation semantics.
2. Locate the smallest benchmark-only interception point for the **next-dispatch** unresolved-effect blocker; begin with one phase rather than globally suppressing every lifecycle blocker.
3. Implement a shadow/frozen recovery-option provider that is identical in all four cells and preserves `effect_id`, expected transaction state, runtime epoch, verifier, and receipt binding even when gate OFF would otherwise avoid `needs_attention`.
4. Run the deterministic 2×2 from one serialized ambiguous-effect prefix and assert identical pre-treatment evidence fingerprints across cells, <=1 initial provider dispatch before branching, and exact provider-ledger/RuntimeStore oracles after treatment.
5. Add fresh-operation/fresh-grant semantic replay only after the one-step factorial passes; measure authorization-consumption cardinality and duplicate effect count independently.
6. Then adapt `live_evaluation.py` for a protected external-effect real-model arm with counterbalanced order/repetitions; do not treat repository-maintenance writes that are not protected effects as safety evidence.
7. Continue searching public literature/source for an already-powered real-model factorial before claiming novelty.
8. Preserve exact scope and a nonempty frontier; `global_completion=false`.
