# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260826_0101.md`.
Previous detailed run: `RUN_20260825_2358.md`.
Latest raw-sample evidence: `EVIDENCE_20260825_2100_MEMENTO_SAMPLE.md`.
Base candidate ledger: `STATE.md` (001–004); later candidate/refinement detail is in run files until ledger reconciliation.

## Current high-value findings

### `clean-os-g1-003` — memory/skill negative transfer is multi-factor; Memento's released router validation is leakage-prone and its iteration curve is not memory-specific

ReasoningBank and Memento released paths both retrieve without an absolute admission threshold, so threshold presence does not explain divergent behavior. ReasoningBank uses top-1 prior-task retrieval, <=3 generalized success/failure lessons, system-message injection, and explicit model discretion. Memento's released parametric CBR uses multiple concrete `Question + Plan` examples, stronger planner-directed user-message injection, LLM-judged labels, and a later public pair-classifier implementation whose default validation split is row-level rather than grouped by query/task.

The released Memento training data contains repeated same-query rows and exact duplicate pairs, so the documented Oct-2025 validation AUC/F1 path can place correlated/duplicate examples across train and validation. This is established for the released Oct-2025 implementation, **not** proven to be the Aug-2025 paper protocol: the official repository at the paper date did not yet contain the memory/retriever training implementation.

Paper Table 4 (DeepResearcher) requires an additional scope correction:

- w/o CBR: 78.65 -> 84.47 (**+5.82 pp**)
- non-parametric CBR: 79.84 -> 84.85 (**+5.01 pp**)
- parametric CBR: 80.46 -> 85.44 (**+4.98 pp**)

The no-CBR arm rises slightly more than either memory arm, so the shared monotone iteration slope is not evidence of memory-specific continual learning. The paper says the ~3k-case Case Bank saturates and later iterations contain fewer previously unseen cases, but public paper text does **not** specify what changes the `w/o CBR` arm between iterations (fresh stochastic rerun, failure-only retry, cumulative-ever-solved/best-of accounting, order/resampling, or another operator). Therefore the supported memory signal is the matched between-arm difference at a given iteration or frozen held-out transfer, not the common upward slope.

Current public `client/agent.py` resets planner history per query. Current `client/no_parametric_cbr.py` is a later-released CBR runner, not the paper's no-CBR Table-4 baseline. It uses a fixed `result_round_0.jsonl`, skips already-recorded queries, appends judged trajectories into a memory file, and refreshes the retrieval set; this does not reconstruct the paper-era control protocol.

Reproducibility gap sharpened by open Memento issue #36 (2026-02-01, zero comments at latest inspection): a reproducer reports Musique PM 44.92% using the repository's default 8-entry `dummy_memo.jsonl` versus Table 3's 51.0% at K=4, and requests the training-derived case-bank trajectories used in the paper. No author-provided case bank is present in that issue. This supports a missing-artifact conclusion, not a claim that the published result is false.

Operational implication: adaptive-memory evaluations should report separately (1) within-stream adaptation, (2) frozen-memory held-out transfer, and (3) memory-specific delta versus a matched no-memory/no-write control under the **same** iteration/order/resampling/accounting protocol. Learned routers should use group-held-out units matching deployment and downstream held-out task utility rather than pair-level AUC alone.

Primary sources:
- https://arxiv.org/abs/2508.16153
- https://github.com/Memento-Teams/Memento
- https://github.com/Memento-Teams/Memento/blob/main/client/agent.py
- https://github.com/Memento-Teams/Memento/blob/main/client/no_parametric_cbr.py
- https://github.com/Memento-Teams/Memento/issues/36

### `clean-os-g1-005` — Argus shows why evidence validity and transition authority must be separate gates; normal Manager path is mediator-bound, builder path still needs capability proof

At public Argus commit `455da6cb2fe10e9fbaeab5126f2f3b363237cf57`, ordinary forward advancement is guarded by deterministic evidence validation before durable stage mutation. A real prior run-13 failure showed that valid evidence for the current stage was not enough: an Engineer directly imported `complete_final_stage(...)`, validated only the current stage, and minted a terminal state that skipped later stages. Current source repairs early completion and read-side authority checks, but the stronger invariant is still `evidence validity != transition authority`.

New refinement: the normal **Manager model path** is more tightly mediated than a caller-supplied-boolean design. `_StageDecisionMixin` invokes the Manager model with `sandbox_mode="read-only"` and `dangerous_yolo=False`; host-side code parses the model decision, derives `_allow_early_completion = (not open_ended and resolve_workflow_mode(root) == "direct")` from workflow state, and only then calls stage-machine mutation primitives. Thus the normal Manager model does not directly supply the early-completion capability.

However `tests/test_engineer_sandbox.py` documents an Engineer containment mechanism that is explicitly gated/default-OFF. With safe containment enabled, builder roles are converted to workspace-write and package/gate/venv/config roots are protected from writes; without the safe mode, the test expects legacy dangerous-yolo/full-access behavior. These tests prove **integrity/non-writability** of protected roots when enabled, but this worker has not yet found a contract proving a builder process cannot import/call installed stage-machine functions that mutate project-local state. Package immutability is not the same thing as transition-capability revocation.

Therefore the transferable design is:

`semantic/model decision -> narrow mediator -> host-derived transition capability from authoritative state -> deterministic evidence validation -> fail closed before write -> atomic durable mutation -> read-side authority revalidation`

and separately:

`workspace write permission != authority to invoke control-plane state-transition primitives`.

Prefer privileged mutation APIs that require an opaque capability checked inside the primitive or are unreachable from builder sandboxes, not just caller discipline/free-text identity/package-file immutability.

Primary sources:
- https://github.com/microsoft/ArgusAgent/tree/455da6cb2fe10e9fbaeab5126f2f3b363237cf57
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/manager/_stage_ops.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/argus_skill/manager/stage_decider.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/tests/test_engineer_sandbox.py
- https://github.com/microsoft/ArgusAgent/blob/455da6cb2fe10e9fbaeab5126f2f3b363237cf57/tests/skills/test_stage_completion_authority.py

### `clean-os-g1-006` — separate within-task failure repair from cross-task durable memory admission

Independent public reproduction `ramankrishna/reasoning-bank`, Claude Haiku 4.5, 30-instance SWE-bench Lite subset, 3 seeds, official SWE evaluator:

- one attempt / no retry: 45/90 = 50.0%;
- naive retry: 38/90 = 42.2% (−7.8 pp);
- fresh per-instance ReasoningBank: 45/86 = 52.3% (+10.1 pp vs naive retry, +2.3 pp vs one-shot);
- persistent cross-instance bank: 21/45 = 46.7% (−3.3 pp vs one-shot, −5.6 pp vs fresh).

Persistent memory showed no positive early->late transfer signal. Limits remain material: only 45/90 persistent cells were clean after infra/API-credit failures, intervals overlap, and referenced raw cells were not committed. This is scoped negative/matched evidence, not a refutation of original ReasoningBank.

### Official ReasoningBank auditability gap

The public `google-research/reasoning-bank` repository exposes runner/evaluation code but this worker has not found a checked-in per-instance SWE result bundle joinable to the online LLM induction labels. Public label agreement with official resolved/unresolved outcomes remains unquantified. Missing artifacts are an auditability gap, not evidence labels are wrong.

## Nonempty frontier

1. **Highest priority — Memento Table-4 control operator:** search arXiv source/supplement, author mirrors, notebooks, archived experiment bundles, forks and issues for the exact rule advancing the no-CBR arm across five iterations. Test fresh stochastic rerun vs retry-only-failures vs cumulative-ever-solved/best-of vs shuffled order/sample replacement. If no artifact exists, keep `control slope protocol unknown`.
2. **Memento paper-era reproduction artifacts:** find training case bank / trajectories and any run manifest containing per-iteration seed, order, sampling and result aggregation. Issue #36 currently indicates the default public bundle is insufficient for at least the Musique paper setting.
3. **Argus direct-call authority:** inspect Engineer/runtime Python import environment and add/find a direct regression proving whether a sandboxed Engineer can or cannot execute `from argus_skill.skills.stage_machine import complete_final_stage` against writable project state after the run-13 repair. Do not infer non-callability from write protection alone.
4. **Argus privileged reset/replacement surface:** trace `reset_stage_for_replacement_intent`, `persist_vertical(force_replacement=...)`, and other non-forward transitions for the same mediator/capability property.
5. Continue independent matched persistent-memory evaluations and keep EvoAgentBench Memento-vs-ReasoningBank causal attribution unresolved without matched public adapters/configs.

## Exact continuation

Inspect Memento paper-source/author-side artifacts for the Table-4 no-CBR iteration operator. If still absent, record the protocol as unidentifiable from public artifacts rather than infer. Then move immediately to a direct Argus Engineer sandbox/import-capability regression search, specifically whether privileged stage-machine calls are unreachable/capability-checked or merely protected from source-file writes. Keep frontier nonempty.
