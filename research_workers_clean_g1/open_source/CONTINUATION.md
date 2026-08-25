# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260826_0202.md`.
Previous detailed run: `RUN_20260826_0101.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; Memento's public evaluation artifacts leave two distinct protocol gaps

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent behavior. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's later released parametric CBR uses multiple concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged labels, and a pair classifier whose default validation split is row-level rather than grouped by query/task.

The released Memento training data contains repeated same-query rows and exact duplicate pairs, so the documented Oct-2025 validation AUC/F1 path can place correlated/duplicate examples across train and validation. This is established for the released Oct-2025 implementation, **not** proven to be the Aug-2025 paper protocol: the official paper-date repository did not yet contain the memory/retriever training implementation.

A second, now sharper paper-era protocol gap concerns Table 4. The paper explicitly defines `w/o CBR` as keeping episodic memory disabled, yet its five-iteration curve rises:

- w/o CBR: 78.65 -> 84.47 (**+5.82 pp**)
- non-parametric CBR: 79.84 -> 84.85 (**+5.01 pp**)
- parametric CBR: 80.46 -> 85.44 (**+4.98 pp**)

The no-CBR arm rises slightly more than either memory arm. The paper explains iteration convergence via the ~3k Case Bank saturating and leaving fewer previously unseen/potentially failing cases, but that mechanism alone cannot explain the explicitly memory-disabled arm's slope. Therefore the common upward trend is not evidence of memory-specific continual learning; the supported memory signal is same-iteration arm differences or frozen held-out transfer under a matched protocol.

The last official commit before the paper-v2 timestamp (`f1aa7e3b46f7b2e737bb1e8c2d38e97db368972f`) contains only the basic runtime/figures/server tools. Its `client/agent.py` is a single-query interactive planner/executor that resets `shared_history` per query; no five-iteration dataset control loop, Case-Bank experiment harness, seed/order manifest or aggregation rule is present. Later public CBR releases therefore cannot be silently substituted for the paper protocol.

Current status: **`control slope protocol unknown`**. Public artifacts inspected so far do not identify whether no-CBR advances via fresh stochastic rerun, failure-only retry, cumulative-ever-solved/best-of accounting, order/resampling, or another operator. This is an auditability/ablation-interpretation gap, not evidence that the reported values are false.

Reproducibility remains limited by open Memento issue #36: a reproducer reports Musique PM 44.92% using the repository's default 8-entry memory versus Table 3's 51.0% at K=4 and requests the paper's training-derived case-bank trajectories. Missing artifacts support a reproducibility-gap conclusion only.

Operational implication: adaptive-memory evaluations should separately report (1) within-stream adaptation, (2) frozen-memory held-out transfer, and (3) memory-specific delta versus a matched no-memory/no-write control under the **same** iteration/order/resampling/accounting operator. Learned routers should use group-held-out deployment units and downstream held-out utility rather than pair-level AUC alone.

Primary sources:
- https://arxiv.org/abs/2508.16153
- https://github.com/Memento-Teams/Memento/tree/f1aa7e3b46f7b2e737bb1e8c2d38e97db368972f
- https://github.com/Memento-Teams/Memento/issues/36

### `clean-os-g1-005` — Argus confirms evidence validity and transition authority are separate gates; low-level mutators remain caller-unauthenticated in inspected public source

At public Argus commit `455da6cb2fe10e9fbaeab5126f2f3b363237cf57`, ordinary forward advancement is guarded by deterministic evidence validation before durable stage mutation. But `stage_machine.py` explicitly states that Manager-only use is an intention, not an authenticated primitive property: `advanced_by` is free text and any role that can import the module can call `advance_stage`.

The same source documents the real run-13 failure where an Engineer imported `complete_final_stage(...)` at stage 1 and minted a structurally valid terminal record that skipped later stages. The current function blocks off-final-stage completion unless `allow_early_completion=True`, but its own docstring calls this **"a lock, not a signature"** because `completed_by` is free text and a determined caller can still pass the boolean.

`reset_stage_for_replacement_intent(...)` is a thin low-level reset mutation over `_set_stage`, downgrades downstream state, and does not itself run the normal stage-completion validator. Its intended caller is Manager-confirmed replacement logic, but the low-level transition still uses free-text caller identity rather than an opaque host capability.

Engineer sandboxing does not close that semantic capability gap by itself. The public sandbox is opt-in/default-OFF. When enabled it protects the package, gate brain, Codex config and active venv from writes, strips VCS credentials and uses `PYTHONSAFEPATH=1`; these are strong integrity controls. But the inspected code/tests do not establish that the installed `argus_skill` package is unimportable or that stage-machine mutation APIs require a non-forgeable host credential. File immutability != transition-capability revocation.

The stronger transferable invariant is:

`semantic/model decision -> narrow host mediator -> host-derived, non-forgeable transition capability -> deterministic evidence validation -> fail closed before write -> atomic durable mutation -> read-side authority revalidation`.

This run did **not** reproduce a live unauthorized Argus mutation. The finding is source-level authentication/reachability analysis, strengthened by explicit repository comments and the documented prior incident.

Primary sources:
- https://github.com/microsoft/ArgusAgent/tree/455da6cb2fe10e9fbaeab5126f2f3b363237cf57
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

### Official ReasoningBank auditability gap

The public `google-research/reasoning-bank` repository exposes runner/evaluation code but this worker has not found a checked-in per-instance SWE result bundle joinable to the online LLM induction labels. Public label agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence labels are wrong.

## Cross-branch synthesis

Two reliability themes now reinforce one another:

1. **Adaptive evaluation needs a fully specified intervention/control operator.** A shared iteration slope is not an intervention effect if the matched control changes too and its inter-iteration operator is unspecified.
2. **Durable agent-state mutation needs both evidence admission and path/caller admission.** A verifier can establish that evidence is valid without establishing that the caller is entitled to cause a transition.

Reusable contract candidate:

`explicit intervention/control operator + source-qualified immutable provenance + matched no-intervention control + authenticated state-transition capability + deterministic evidence gate + rollback/read-side verification`.

## Nonempty frontier

1. **Highest priority — Argus direct-call authority regression:** inspect commit/issue/test history after the run-13 repair for an explicit Engineer-subprocess attempt to `import argus_skill.skills.stage_machine` and mutate project state. Determine whether a host/process capability boundary exists or current protection is source-write containment plus caller discipline.
2. Trace Argus non-forward mutation surfaces (`reset_stage_for_replacement_intent`, vertical replacement/reset, rollback and other privileged mutators) for the same caller-authentication property.
3. Continue Memento author-mirror/fork/notebook/supplement searches for a paper-era Table-4 run manifest identifying no-CBR inter-iteration operator, seeds/order and aggregation. If absent, retain `control slope protocol unknown`.
4. Search for open-source systems that enforce state transitions through opaque capability tokens or a privileged mutation service/process and have matched agent ablations.
5. Continue independent matched persistent-memory evaluations; keep EvoAgentBench Memento-vs-ReasoningBank causal attribution unresolved without public matched adapters/configs.

## Exact continuation

Inspect Argus public commit/issue/test history around the run-13 completion repair for a direct builder-subprocess import/call regression. Specifically determine whether privileged stage-machine calls are unreachable/capability-checked or merely protected from source-file writes. Then continue the Memento paper-era artifact search for a concrete Table-4 no-CBR inter-iteration operator. If either artifact is absent, preserve that absence explicitly as an auditability boundary rather than inferring behavior.
