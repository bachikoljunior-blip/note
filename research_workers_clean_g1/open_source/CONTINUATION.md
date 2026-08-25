# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260826_0258.md`.
Previous detailed run: `RUN_20260826_0202.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; Memento's public evaluation artifacts leave two protocol gaps

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent behavior. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's later released parametric CBR uses multiple concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged labels, and a pair classifier whose default validation split is row-level rather than grouped by query/task.

The released Memento training data contains repeated same-query rows and exact duplicate pairs, so the documented Oct-2025 validation AUC/F1 path can place correlated/duplicate examples across train and validation. This is established for the released Oct-2025 implementation, **not** proven to be the Aug-2025 paper protocol: the official paper-date repository did not yet contain the memory/retriever training implementation.

The paper explicitly defines `w/o CBR` as keeping episodic memory disabled, yet Table 4 rises across five iterations:

- w/o CBR: 78.65 -> 84.47 (**+5.82 pp**)
- non-parametric CBR: 79.84 -> 84.85 (**+5.01 pp**)
- parametric CBR: 80.46 -> 85.44 (**+4.98 pp**)

The no-CBR arm rises slightly more than either memory arm. ArXiv v2 explains convergence via the ~3k Case Bank saturating and later iterations having fewer unseen/potentially failing cases, but does not specify what changes between iterations for the explicitly memory-disabled DeepResearcher control. It separately specifies a three-iteration accumulate-memory protocol for GAIA, so that does not resolve Table 4's no-CBR operator.

The last official commit before the paper-v2 timestamp (`f1aa7e3b46f7b2e737bb1e8c2d38e97db368972f`) contains only the basic runtime/figures/server tools. Its `client/agent.py` resets `shared_history` per query; no five-iteration dataset control loop, Case-Bank experiment harness, seed/order manifest or aggregation rule is present. Fresh searches of the current public repo for the exact Table-4 sequence / DeepResearcher iteration harness also did not surface a primary run manifest.

Current status: **`control slope protocol unknown`**. The shared upward curve is not evidence of memory-specific continual learning unless the matched no-memory/no-write control uses the same iteration/order/resampling/accounting operator. Supported memory evidence should come from same-iteration arm differences or frozen held-out transfer under a matched protocol.

Reproducibility remains limited by open Memento issue #36: a reproducer reports Musique PM 44.92% using the repository's default 8-entry memory versus Table 3's 51.0% at K=4 and requests the paper's training-derived case-bank trajectories. Missing artifacts support a reproducibility-gap conclusion only.

Primary sources:
- https://arxiv.org/html/2508.16153v2
- https://github.com/Memento-Teams/Memento/tree/f1aa7e3b46f7b2e737bb1e8c2d38e97db368972f
- https://github.com/Memento-Teams/Memento/issues/36

### `clean-os-g1-005` — Argus: evidence validity and transition authority are separate gates; current sandbox is write containment, not transition-capability revocation

Public `main` remains `455da6cb2fe10e9fbaeab5126f2f3b363237cf57` (2026-08-22). `stage_machine.py` explicitly says `advance_stage`/`rollback_stage` are intended Manager-only but **nothing authenticates the caller**: `advanced_by` is free text and any role able to import the module can invoke them. Deterministic stage validators protect evidence validity, not role/path authority.

`tests/skills/test_stage_completion_authority.py` documents the actual run-13 failure where an Engineer imported `complete_final_stage(...)` at stage 1 and minted a structurally valid terminal record skipping later stages. The repair refuses off-final-stage completion unless `allow_early_completion=True` and adds read-side revalidation, but the regression module explicitly calls it **"a lock, not a signature"**: `completed_by` is free text, the fingerprint is recomputable, and a determined caller can still pass the argument.

The latest sandbox audit resolves the previous uncertainty about importability more strongly. `argus_skill/core/sandbox.py` is explicitly a **write-containment** design: it protects the gate brain, package source, Codex config and venv from writes; sets `PYTHONSAFEPATH=1` to prevent workdir shadowing; starts bubblewrap from a read-only `/`; and explicitly re-exposes `sys.prefix` read-only. The project workdir remains the intended writable root. For an installed deployment in which the package is available from the active Python environment, this preserves authentic package read/execute access while protecting it from modification; it does not provide a non-forgeable call capability at the state-machine mutator.

The public Engineer sandbox test suite is strong on write roots, symlink/venv persistence escapes, rootless workspace confinement, VCS credential scrubbing and worktree metadata. It does **not** contain an Engineer-subprocess regression proving that importing `argus_skill.skills.stage_machine` and requesting a privileged project-state transition is rejected by caller authentication. Instead, the authority regression explicitly acknowledges the residual determined-caller path.

Containment is also source-level conditional: the public feature is opt-in/default-OFF for compatibility, and tests retain a legacy full-access path when safe mode is not enabled. This does not establish how every deployment configures it.

`reset_stage_for_replacement_intent(...)` remains a high-priority non-forward surface: it is a low-level reset mutation over `_set_stage`, downgrades downstream state and is intended for Manager-confirmed replacement logic, but caller identity is still represented semantically rather than by an opaque host capability.

Stronger transferable invariant:

`filesystem integrity != semantic transition authority`.

Preferred architecture:

`semantic/model decision -> narrow host mediator -> host-derived unforgeable capability bound to authoritative state + transition kind -> deterministic evidence validation -> fail closed before write -> atomic durable mutation -> read-side authority revalidation`.

This worker has **not** executed a live unauthorized Argus mutation. The result is source-level reachability/authentication analysis supported by current code, regression tests and the repository's documented incident.

Primary sources:
- https://github.com/microsoft/ArgusAgent/tree/455da6cb2fe10e9fbaeab5126f2f3b363237cf57
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/tests/skills/test_stage_completion_authority.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/skills/stage_machine.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/core/sandbox.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/tests/test_engineer_sandbox.py

### `clean-os-g1-006` — separate within-task failure repair from cross-task durable memory admission

Independent public reproduction `ramankrishna/reasoning-bank`, Claude Haiku 4.5, 30-instance SWE-bench Lite subset, 3 seeds, official SWE evaluator:

- one attempt / no retry: 45/90 = 50.0%;
- naive retry: 38/90 = 42.2% (-7.8 pp);
- fresh per-instance ReasoningBank: 45/86 = 52.3% (+10.1 pp vs naive retry, +2.3 pp vs one-shot);
- persistent cross-instance bank: 21/45 = 46.7% (-3.3 pp vs one-shot, -5.6 pp vs fresh).

Persistent memory showed no positive early->late transfer signal. Limits remain material: only 45/90 persistent cells were clean after infra/API-credit failures, intervals overlap, and referenced raw cells were not committed. This is scoped negative/matched evidence, not a refutation of original ReasoningBank.

The public `google-research/reasoning-bank` repository exposes runner/evaluation code but this worker has not found a checked-in per-instance SWE result bundle joinable to the online LLM induction labels. Public label agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence labels are wrong.

## Cross-branch synthesis

1. **Adaptive evaluation needs a fully specified intervention/control operator.** A shared iteration slope is not an intervention effect if the matched control changes too and its inter-iteration operator is unspecified.
2. **Durable agent-state mutation needs both evidence admission and path/caller admission.** A verifier can establish valid evidence without establishing that the caller is entitled to mutate durable control state.
3. **Write containment is not authority confinement.** Keeping an agent from modifying its gate/framework does not prevent it from invoking authentic privileged APIs unless the API itself checks an unforgeable authority.

Reusable contract candidate:

`explicit intervention/control operator + source-qualified immutable provenance + matched no-intervention control + capability-bound mutation authority + deterministic evidence gate + atomic write + rollback/read-side verification`.

## Nonempty frontier

1. **Highest priority — Argus non-forward authority surface:** trace `reset_stage_for_replacement_intent`, `persist_vertical(force_replacement=...)`, rollback/replacement and completion/reset paths. Classify each by evidence check, caller authentication/capability, writable state and read-side revalidation.
2. Search Argus public history after run-13 for any newer opaque capability, privileged mutation service or process separation. Current public `main` is still `455da6c`; do not infer private fixes.
3. Search for a contrasting open-source agent runtime that routes privileged durable-state mutation through a host service/opaque capability and has adversarial or matched tests.
4. Continue Memento author-mirror/fork/notebook/supplement searches for the paper-era Table-4 no-CBR operator, seeds/order and aggregation manifest. If absent, retain `control slope protocol unknown`.
5. Continue independent matched persistent-memory evaluations only where exact adapter/config/raw evidence is public.

## Exact continuation

Audit every Argus non-forward mutator and its public call sites, beginning with `reset_stage_for_replacement_intent` and vertical replacement/reset. Determine whether any path introduces a host-only, non-forgeable authority check absent from `advance_stage` / `complete_final_stage`. Then seek a contrasting public agent runtime with privileged mutation-service/capability enforcement and matched tests. Keep the Memento Table-4 operator search as the parallel evidence branch and preserve absence explicitly rather than inferring hidden behavior.
