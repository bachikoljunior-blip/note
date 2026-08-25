# Open Source clean_g1 — RUN_20260826_0502_CAPABILITY_SECRECY

Control snapshot frozen at note main `ea7a952cbd62015892b756904968de2d3c131ce6`: control revision 7, `open_source` config revision 4. The current note main advanced afterward because of unrelated concurrent writes; those changes were not used semantically. Clean-exploration boundary respected: only this worker's clean state, its own feedback path (absent), sanitized automation-control bootstrap/config, and public sources were used. No O/O-derived state, other-worker state/output/config, comparator/integrator/index/feed/audit, aggregate execution ledger, or legacy/pre-independence semantic state was read.

## Scope

Continue the highest-value frontier from the previous authority-matrix run:

1. verify whether Argus `RepairCapability` nonces are only hidden from the model interface or also physically unreadable to Engineer execution;
2. re-evaluate the suspected route/stage TOCTOU against the actual host locking architecture;
3. check the freshest public Argus upstream for a stage-capability migration;
4. find independent public implementation precedents for proposal→host gate→execution-bound authority→stale-write rejection.

No live unauthorized state mutation or secret-read exploit was executed. Findings are source/test-path analysis only.

## Source freshness

The Microsoft mirror remains at `microsoft/ArgusAgent@455da6cb2fe10e9fbaeab5126f2f3b363237cf57` (2026-08-22), but the upstream public repository is newer:

- `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` — current upstream main observed 2026-08-26 JST, commit authored 2026-08-25T20:10:08Z.

The upstream current `stage_machine.py`, `control_state.py`, `knobs.py`, `sandbox.py`, and `_mission_execution_runtime.py` were checked. The authority/sandbox properties relevant below remain present.

## Finding A — the repair nonce is interface-hidden, but not universally host-secret at the filesystem boundary

The previous run established an important positive property: the ordinary validator-repair path does **not** place the nonce in model prompt text or runner kwargs. The freshest upstream still does this:

- `_mission_execution_runtime.py` opens `CampaignControlStore` in `self.memory.root`;
- the host reads the authorization object and passes `authorization["nonce"]` itself to `claim_repair_capability`;
- it then passes the capability nonce itself to `begin_acceptance_retry`;
- the model-facing prelude contains only public identifiers (`authorization_id`, `capability_id`, `validator_id`) and allowed write paths.

That remains a strong interface-level mediator pattern.

However, `control_state.py` shows the nonce is durably written in plaintext into the Manager state root:

- `Authorization` has `nonce: str`;
- `RepairCapability` has `nonce: str`;
- `CampaignControlStore.authorization_path = state_root / "operator-authorizations.jsonl"`;
- `issue_authorization()` creates `secrets.token_urlsafe(24)` and appends `asdict(authorization)` to that JSONL, so the nonce itself is persisted;
- the active capability also carries the nonce in durable control state.

Therefore the secret is host-confined at the **API/prompt handoff**, not automatically at the **filesystem/OS isolation** boundary.

### Default execution makes the distinction material

The freshest public `knobs.py` still declares:

- `ARGUS_SKILL_SAFE_MODE = off` by default;
- `ARGUS_SKILL_ENGINEER_SANDBOX = off` by default.

`_apply_sandbox_policy()` explicitly falls back to dangerous/full filesystem-capable execution when safe mode is off.

Even when Codex `workspace-write` is enabled, Argus's `sandboxed_child_env()` copies the parent environment and strips GitHub/VCS credentials, but it does not remove `ARGUS_SKILL_SESSION_ROOT` or otherwise create a model-opaque secret store. Its principal filesystem protection is **write** confinement: forbidden roots such as `~/.argus-skill`, the active environment, and package root are excluded from writable roots.

The public OpenAI Codex permission template states that `workspace-write` permits reading files while restricting editing to the working directory and writable roots. Consequently, ordinary `workspace-write` cannot by itself establish that a plaintext nonce under the Manager state root is unreadable.

Argus has a stronger, separate `isolate_workdir`/bubblewrap mode that hides broad host roots on POSIX. That may hide a default state root under `/home` or `/root`, but it is not the ordinary Engineer `workspace-write` setting, and its fixed hidden-root list does not prove every custom `ARGUS_SKILL_HOME` layout is hidden. The macOS isolation branch also does not establish a universal `.argus-skill` read denial.

### Scope-limited conclusion

Supported by source:

> `RepairCapability` uses a host-mediated, one-shot nonce contract, but the nonce should not be described as universally “host-only secret” across supported/default deployments because it is persisted in same-user durable state and the default/sandboxed execution configurations do not universally deny reads of that state.

Not established:

- that a model actually read or abused the nonce;
- that validator-repair can currently be bypassed with it;
- that all deployment layouts expose the state path.

There is also a limiting detail favorable to the existing validator-repair design: the host claims the authorization and starts the single acceptance retry **before** the Engineer runner is invoked. Thus even a later nonce disclosure does not automatically recreate an unused authorization. This run is correcting the secrecy claim, not asserting an exploit.

## Finding B — the ordinary route/stage TOCTOU concern is substantially mitigated by an existing outer pipeline lock

The previous frontier asked whether `persist_vertical` and stage mutation could race because they both ultimately rewrite pipeline state without an internal revision CAS.

Tracing the host architecture changes the assessment:

- `manager_pipeline_lock()` is a cross-process advisory lock intended to serialize Manager pipeline commits with daemon mission execution.
- the daemon main loop obtains `manager.pipeline_lock()` and wraps the whole `supervisor.run()` under that lock;
- Manager vertical/route commits also enter `self.pipeline_lock()` before `persist_vertical` / replacement reset.

Therefore, in the normal host architecture, route mutation cannot interleave with supervisor planning/execution/stage-transition work. A stage decision generated inside `supervisor.run()` is protected for the duration of that run by the same outer lock.

This is a material scope correction:

> A normal Manager-route vs daemon-stage lost-update race is **not supported** by the current source architecture.

The remaining authority gap is lower-level bypass/defense-in-depth, not normal host concurrency:

- `advance_stage`, `rollback_stage`, `reset_stage_for_replacement_intent`, and `complete_final_stage` do not themselves require the pipeline lock or a caller capability;
- current upstream `advance_stage` still says caller identity is unauthenticated;
- current upstream `complete_final_stage` still documents the run-13 wrong-path direct import incident and explicitly calls its boolean protection “a lock, not a signature”.

So a privileged primitive invoked outside the intended host route can still bypass orchestration-level serialization/identity. The candidate should target **mutator-bound authority** rather than claiming the current normal pipeline has an observed TOCTOU bug.

## Finding C — no public stage-capability migration is visible yet in the freshest upstream

The upstream current `lbx154/Argus@962cb065...` still has:

- free-text actor fields at stage mutators;
- no nonce/capability argument on stage transition primitives;
- the same explicit statement that caller identity is not authenticated;
- the same `complete_final_stage` warning that a determined caller can pass `allow_early_completion`.

Repository code search and public issue/PR search did not surface a stage-authority/capability migration. This is absence-of-public-evidence, not proof no private/in-progress work exists.

## Finding D — independent public runtimes support the same host-admission pattern

### OpenHands software-agent-sdk — proposal before host execution gate

Current public `SecurityAnalyzerBase` evaluates `ActionEvent`s before execution. Analyzer errors are converted to HIGH risk rather than silently allowing the action. Confirmation-mode tests explicitly produce an LLM tool call and assert the conversation enters `WAITING_FOR_CONFIRMATION` before action execution is allowed.

Transferable part:

`model action proposal -> host risk/policy gate -> execution`

This supports moving semantic transition authority out of a model-provided actor string/boolean and into a host gate.

### Temporal — execution-bound token invalidation

Temporal's public WorkflowService API uses task tokens for Activity task completion/failure/cancellation and documents rejection when a token is no longer valid because the task timed out, was already completed, or never existed.

Transferable part:

`execution-bound token -> stale/already-consumed request is rejected server-side`

Temporal normally gives the token to the worker, so it is not a direct secret-storage blueprint. The useful precedent is one-shot execution identity and stale-token rejection.

### Kubernetes — state-version conditional update

Kubernetes' resource model uses `resourceVersion` for optimistic concurrency: updates can be made conditional on the version read, and a stale update receives a conflict rather than overwriting newer state.

Transferable part:

`read state revision -> conditional mutation -> stale revision fails with no write`

This complements, rather than replaces, Argus's existing outer pipeline lock. The lock serializes ordinary host operation; revision-bound mutation protects against wrong-path/stale callers and makes the low-level primitive self-defending.

## Candidate refinement — `clean-os-g1-005`

The candidate is retained, but narrowed and strengthened.

### What already works

Argus already has:

- an outer Manager/daemon pipeline lock for normal orchestration;
- deterministic evidence admission on forward/final stage transitions;
- atomic pipeline-file replacement;
- read-side completion/authority revalidation;
- a strong one-shot revision/evidence/tree-bound capability implementation for validator repair.

### Missing primitive-bound property

Stage mutation primitives do not consume current durable authority. They rely on host-path correctness plus evidence/shape checks. That leaves direct-import/wrong-path calls outside the primitive's own trust boundary.

### Proposed minimal transition contract

1. The model/agent emits only a semantic proposal (`advance`, `rollback`, `reset`, `complete`, target, reason).
2. The host remains serialized by the existing pipeline lock.
3. The host validates current route/workflow, `from_stage`, target legality, deterministic evidence, and decision provenance.
4. The host mints/holds a one-shot transition capability bound to at least:
   - campaign/objective/epoch;
   - exact control/pipeline state revision or digest;
   - transition kind;
   - exact `from_stage`;
   - allowed target stage(s);
   - route/workflow digest;
   - evidence-contract/evidence fingerprint where applicable;
   - decision/plan id;
   - expiry/replay status.
5. **Do not persist the capability secret in a model-readable same-user path.** Keep it host-only in memory, OS-protected state, or behind a server-side opaque handle. A public capability id may be model-visible; the authority secret should not be.
6. The low-level stage mutator atomically consumes the capability and performs a conditional revision check before writing. Stale revision, action/from/target/route mismatch, evidence drift, expiry, or reuse fail closed with no mutation.
7. Keep read-side revalidation to reject pre-existing/external corrupt state.

### Why both capability and CAS

The two solve different failure modes:

- capability: *who/path is authorized for this semantic transition?*
- revision/CAS: *is the state still exactly the state that authorization covered?*

The existing outer lock is still valuable and should remain. The proposed primitive check is defense-in-depth against bypass paths and stale/replayed calls, not a replacement for orchestration serialization.

## Adversarial regression matrix

A production-quality implementation should add negative tests where `PIPELINE_STATE.json` remains byte-identical for:

1. direct stage-mutator call without a transition capability;
2. public capability id/handle without host secret;
3. capability minted at revision N after any route/stage revision advances to N+1;
4. replay of an already consumed capability;
5. transition-kind mismatch (`advance` token used for reset/complete);
6. `from_stage` mismatch;
7. target-stage mismatch;
8. route/workflow digest mismatch;
9. evidence fingerprint drift;
10. expired capability;
11. capability secret attempted through model-visible prompt, env, workspace, or default/safe sandbox filesystem;
12. host crash after mint but before consume, and after consume but before durable receipt;
13. direct importer bypassing `manager_pipeline_lock`;
14. stale pre-existing completion state still rejected by read-side authority checks.

For secret confinement, test at least the default configuration, Codex `workspace-write`, and the stronger isolated-workdir layout separately; do not infer one from another.

## Tested scope / uncertainty

- Source audit only; no unauthorized mutation or secret exfiltration was executed.
- Public upstream `lbx154/Argus@962cb065...` is fresher than the Microsoft mirror and is the freshness authority for these code claims in this run.
- The existing repair flow may remain safe against the specific hypothesized nonce abuse because the host consumes/starts its one retry before model execution; the finding is about secret confinement and reuse suitability.
- The normal route/stage host path is serialized by the outer pipeline lock; this run retracts the stronger normal-path TOCTOU suspicion.
- Independent OpenHands/Temporal/Kubernetes evidence supports architecture patterns, not an Argus benchmark-effect claim.
- No quantitative performance gain is claimed for capability-bound stage transitions; current evidence is reliability/authority engineering evidence.

## Nonempty frontier

1. Enumerate every production call site of `advance_stage`, `rollback_stage`, `reset_stage_for_replacement_intent`, `complete_final_stage`, and `persist_vertical` in the freshest upstream; classify whether each is covered by `manager_pipeline_lock` and identify any real production bypass path outside it.
2. Trace the model-visible environment in default, `workspace-write`, and isolated layouts and write an exact reachability table for `operator-authorizations.jsonl`, campaign-control snapshots, and `ARGUS_SKILL_SESSION_ROOT`; keep “readable” separate from “usefully exploitable”.
3. Search the freshest upstream history after `962cb065...` and issues/PRs for a capability-bound stage mutation or secret-store hardening migration; if one appears, compare instead of duplicating.
4. Find an independent agent/runtime implementation that combines **opaque host authority + stale state revision** at the actual tool/durable-state mutation boundary (not just human confirmation), and inspect adversarial tests.
5. If no stronger precedent appears, specify the smallest reuse of `CampaignControlStore` that avoids persisting plaintext transition secrets while preserving crash recovery.
6. Secondary branch: retain the unresolved Memento Table-4 control-operator provenance question; resume only if a paper-era manifest/seed/order/aggregation artifact appears.

## Exact continuation

Start with the freshest upstream production-call-site sweep. Build a table with columns: caller/path, outer pipeline lock held?, model can directly invoke path?, evidence gate?, capability/identity gate?, state revision/CAS?, atomic write?, read-side revalidation. Then build a three-layout secret-readability matrix (default, workspace-write, isolated-workdir) for Manager authorization state. Use that to decide whether the smallest robust patch is (a) capability+CAS only, (b) secret-store isolation only, or (c) both. In parallel, search one independent open-source agent runtime for a tested opaque host capability bound to an exact state revision.
