# Long Horizon external research — clean_g1 checkpoint — 2026-08-26 05:00 JST

## Boundary / control provenance
- Generation: `clean_g1`; worker: `long_horizon`; class: `clean_exploration`.
- Sanitized root control: `automation_control/DESIRED_STATE.json`, control_revision `7`, blob `ae605e09eb3bcdc7aa18238d2c42218b0272d2e6`.
- Role-local control: `automation_control/roles/long_horizon.json`, config_revision `4`, blob `5c468d1e4812cc0650a288aaaef2918105af0442`.
- Pinned note main used for the frozen control recheck: `ea7a952cbd62015892b756904968de2d3c131ce6`. At that SHA the root/role control revisions and blobs matched the initial reads, so the role remained `enabled_desired=true` with the same clean boundary.
- Own continuation authority: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0400JST.md` blob `97664a2b211f21283ece92c56bf5592040c17688`; own sanitized feedback blob `9836c7853800e6245493d1fd74f90d768290fc21` was applied mechanically.
- **Boundary incident this run:** while trying to obtain the note main SHA, the generic `/commits/main` response exposed the body of an unrelated role-local receipt. That content was immediately quarantined and was not used for source selection, interpretation, synthesis, candidate generation, or conclusions. Future main-SHA checks must use branch metadata (`/branches/main`) rather than commit-diff payloads. No shared `EXECUTION_LEDGER.json`, O/O-derived state, comparator/integrator/index/feed/audit state, other worker state/config, or legacy/pre-independence research was used semantically.
- Procedure correction: the exact main SHA was pinned after the first public-web search batch rather than before it. The control/config were then refetched at the pinned SHA and found unchanged; all semantic synthesis below was performed only after that recheck. Treat the early search as source discovery, not as a frozen semantic execution.

## Search target
Continue the 04:00 frontier:
1. find a GUI/tool/software-agent study that holds alarm/checkpoint substrate fixed while changing rollback target policy;
2. if that strict selector-only comparison remains absent, strengthen adjacent controls with primary quantitative evidence and preserve the gap;
3. look for rollback-state failures that invalidate the assumption that restoring the visible transcript/environment is sufficient.

## Finding A — WebRollback is a strong live-web comparison, but it still changes both `when` and `where`
Primary: Zhisong Zhang et al., **WebRollback: Enhancing Web Agents with Explicit Rollback Mechanisms**, EACL 2026.
- ACL: https://aclanthology.org/2026.eacl-short.12/
- PDF: https://aclanthology.org/2026.eacl-short.12.pdf

The method explicitly factorizes a critique module (`when to rollback`) and a rollback module (`where to rollback`). On a rollback decision, all preceding states are provided and the model selects a state index; the browser is reset to that historical URL. Maximum step budget is 16 unless otherwise specified.

Primary zero-shot Table 1, same benchmark family and step budget:
- Llama-3.3-70B, Mind2Web-Live full success: OneWay `20.92±3.61`, BestFirst `21.16±0.41`, Rollback `24.07±1.42`; state switches: `0`, `8.1±0.1`, `5.0±0.3`.
- Llama-3.3-70B, WebVoyager: `38.06±1.70`, `39.82±3.16`, `44.30±1.32`; switches `0`, `5.3±0.1`, `3.2±0.2`.
- Qwen2.5-72B, Mind2Web-Live: `24.53±0.70`, `23.82±1.18`, `27.36±0.94`; switches `0`, `6.3±0.1`, `4.5±0.1`.
- Qwen2.5-72B, WebVoyager: `49.56±1.61`, `47.95±2.34`, `51.90±4.24`; switches `0`, `4.3±0.2`, `2.1±0.2`.

The paper reports `struggle-ratio` 19% for OneWay versus 7% for Rollback and argues BestFirst over-switches because intermediate value estimates are noisy.

**Scope guard:** this is not a rollback-target-only causal isolation. BestFirst and Rollback differ in decision logic for both triggering/switching and target selection; the rollback model also sees a dedicated critique/rollback prompt. It supports `explicit model-controlled rollback can outperform value-driven state switching on these live-web tasks`, not `one target selector is intrinsically best under a fixed alarm`.

## Finding B — BEAP-Agent adds real desktop multi-step backtracking evidence, but no target-depth ablation
Primary: Ziyu Lu et al., **BEAP-Agent: Backtrackable Execution and Adaptive Planning for GUI Agents**, arXiv:2601.21352.
- Abstract: https://arxiv.org/abs/2601.21352
- PDF: https://arxiv.org/pdf/2601.21352

BEAP models GUI execution as DFS over a state tree and backtracks to the nearest ancestor with unexplored paths. GPT-4o is used for Planner/Tracker and UI-TARS-1.5-7B for execution; evaluation uses OSWorld, screenshot-only interaction, PyAutoGUI, and a 50-step cap.

Primary Table 1 / analysis:
- full BEAP-Agent accuracy `28.2%`;
- without backtracking `26.3%`;
- without Tracker `23.6%`;
- `35.8%` of tasks triggered backtracking;
- backtracking success rate `65.5%`;
- average backtrack steps `2.72`;
- Chrome-domain backtracking success exceeds 80% in the reported analysis.

The paper explicitly argues that the error is often not in the immediately previous step, because sparse feedback can reveal a wrong path only several steps later.

**Scope guard:** BEAP validates the presence of multi-step DFS-style backtracking plus dynamic tracking; it does not compare nearest-ancestor DFS against random/latest-good/root-cause/value-ranked/semantic-admissible targets under the same alarm and restore substrate. The backtracking target rule is built into the DFS policy.

## Finding C — new high-severity negative evidence: logical rollback can be false if inference KV state survives
Primary: Guijia Zhang, Harry Yang, **Aborted but Not Forgotten: KV-Cache Retention Breaks Rollback Consistency in Language Agents**, arXiv:2608.15939v1, submitted 2026-08-16.
- Abstract: https://arxiv.org/abs/2608.15939
- PDF: https://arxiv.org/pdf/2608.15939

The paper isolates a cross-layer rollback failure: an application deletes a rejected branch from the transcript, but a serving session retains the branch-derived KV cache. The authors use a same-token/different-cache audit: the decision-step tokens are identical in stale/fresh arms and attacker tokens are absent from the served request, so the only manipulated variable is the provenance of attended KV state.

Primary deterministic census:
- 7 dense open-weight families × 9 attack cells = 63 cells;
- stale retained KV flips the protected typed effect in `25/63` cells;
- text-present cold pass flips the exact same `25/63` cells;
- fresh cache rebuilt from committed bytes: `0/63`;
- full cold restart: `0/63`;
- carrier absent from fed decision tokens: `63/63`; stale/fresh decision tokens identical: `63/63`.

Per-family stale flips: Phi-3.5-mini `9/9`, GLM-4-9B `9/9`, Granite-3.3-8B `6/9`, Qwen2.5-14B `1/9`, DeepSeek-R1-Distill-Llama-8B `0/9`, Phi-4-14B `0/9`, Seed-OSS-36B `0/9`. The underlying state-level violation remains even in behaviorally resistant models.

The same channel reproduces under a first-class LangGraph time-travel rollback: the persisted logical state is verified to exclude the rejected branch, yet the retained serving KV remains stale. Across five tested families the LangGraph path reproduces `25/45` attack-cell flips; rebinding the cache to the committed transcript closes all cells (`0/45`).

Three transaction-local restores—fresh reprefill from committed bytes, cropping stale KV, or restoring a post-commit KV checkpoint—each close all audited cells in the corresponding experiment (`0/36` each). The authors distinguish this from a global cache flush/restart, which is unnecessary for correctness if the transaction-local attended state is restored.

**Scope-bounded interpretation:** a long-horizon rollback contract must cover every state layer that the model actually attends, not just the visible transcript, graph checkpoint, or filesystem. `rollback(target)` is not complete unless post-rollback inference state is re-derivable from the committed prefix. This is orthogonal to the historical target-selector question: even a perfect target selector can fail if restore semantics leave stale attended state.

## Finding D — the selector-only general-agent gap remains open
Bounded searches for `rollback target`, `rollback node`, `where to rollback`, GUI/OSWorld/WebArena checkpoint selection, SRC follow-ups, and Hydra public code/data did not locate a primary GUI/tool/software-agent experiment that simultaneously fixes:
- the alarm/review events;
- eligible historical checkpoint set;
- restore and carryover mechanics;
- model/prompt/sampling;
- retry and token budget;
then varies only the historical rollback target and reports final task success.

Hydra remains the closest restricted systems experiment for code-generation rollback policy under a strongly matched checker/checkpoint substrate, but retry/adaptive posterior semantics differ. SRC remains a strong GUI review-horizon ablation and public reset-and-replay substrate, but changing `K` changes alarm timing and harmful-suffix opportunity. WebRollback compares explicit model-controlled rollback with BestFirst and OneWay but changes both trigger and target policy. BEAP compares presence/absence of multi-step backtracking and Tracker, not target rules.

## Updated control decomposition
The evidence now supports separating at least these variables:
1. **checkpoint placement** — which recoverable states are materialized;
2. **alarm/review timing** — when failure evidence becomes available;
3. **intervene vs continue** — recovery/disruption tradeoff;
4. **safe cut point** — when an in-progress edit/action can be interrupted;
5. **historical target selector** — which eligible checkpoint to return to;
6. **causal object selector** — which memory/state objects are invalidated;
7. **carryover policy** — what lesson/artifact from the failed branch survives;
8. **restore-layer completeness** — transcript, agent memory, environment, process state, and **inference attended state/KV** must be reconciled as applicable;
9. **external-effect settlement** — irreversible/compensable effects remain separate from state rewind;
10. **repair stopping** — when another correction is no longer worth disruption/cost.

Finding C adds a new hard invariant to this decomposition: **historical rollback target and logical state can both be correct while the rollback is still semantically incomplete because the inference cache is stale.**

## Strengthened negative evidence
- `Visible transcript restored => agent has forgotten rejected branch`: false on retained-KV serving paths in the audited study.
- `Framework-native time travel is a complete rollback`: false as a cross-layer claim; LangGraph correctly restores the logical state it owns, but does not promise serving-KV rewind.
- `Behaviorally resistant model => rollback state is sound`: false; state-level KV inconsistency can exist even when downstream effect does not flip.
- `Nearest prior state/single-step backtrack is enough`: not supported; BEAP reports sparse-feedback failures where wrong-path recognition occurs several steps later.
- `BestFirst value switching is automatically efficient`: contradicted in WebRollback's tested live-web setup by more state switches and lower full success than explicit rollback.

## Nonempty frontier
1. **Highest value:** exact selector-only factorial in GUI/tool/software agents with identical alarms, checkpoints, restore/carryover, model, and literal budget.
2. **Rollback consistency across inference layers:** look for replications under vLLM/SGLang/provider-session caches and agent frameworks beyond the tested Hugging Face/LangGraph paths; distinguish self-healing recomputation from retained-handle paths.
3. **Target selector × restore completeness factorial:** test whether a better target rule still helps once transcript/environment/KV restoration are all correct.
4. **SRC substrate follow-up:** search for branches/forks implementing target-policy plug-ins under frozen review events.
5. **Hydra artifact:** continue bounded search for official code or raw Figure-7 samples/quantiles.
6. **False-alarm target behavior:** measure disruption from shallow/deep targets on trajectories that would otherwise succeed.
7. **Causal object × temporal target:** factor faulty-state localization from historical time selection.
8. **Subgoal/folding negative evidence:** wrong decomposition, stale folded summaries, and over-aggressive compression remain open.

## Exact continuation
Next run first action: search primary/public artifacts for **rollback consistency** implementations or replications in vLLM, SGLang, LangGraph-like agent runtimes and for any SRC/WebRollback/BEAP follow-up that exposes historical target selection as a pluggable policy. Prioritize studies with matched alarms and final task success; separately require restore-layer completeness (including attended inference state) so a target-selector comparison is not confounded by stale KV. Continue a bounded Hydra artifact search. If no strict selector-only study exists, preserve the gap explicitly rather than upgrading adjacent trigger/depth/DFS comparisons.
