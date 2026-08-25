# O / Chat continuity

Updated: 2026-08-25 JST

Mandatory continuity: read this file before every O-related answer/reasoning/action, then update it in the same turn whenever the conversation advances or materially clarifies the current design/state. Treat this as the chat-side reconstruction checkpoint so long conversation history is not required. Before sending new semantic context to O, show the wording and wait for user approval. Safe non-semantic operational defects may be repaired immediately.

## Standing context
- Goal: materially accelerate genuine real-world AGI; O is instrumental/replaceable.
- User-side work should be minimized; repository/tool work belongs on the automated/Work side.
- Treat O and this chat as same-base-model for idea-generation overlap. Before proposing a new idea to send to O, ask whether O could readily derive it from its actual current context. Prefer genuine context asymmetries, user-originated design choices, external evidence/observations, or concrete failures over duplicating reasoning O can readily do itself.
- External ideas and user proposals are hypotheses, not automatic truth.
- Context is an intervention with information value and interference cost; more context is not monotonically better. Prefer minimal, gated, on-demand context and judge usefulness by downstream behavior/results.
- Evaluation itself is fallible. Distinguish measured improvement from metric validity; evaluator design may itself need falsification/calibration.

## O inbox / uptake
- Revisions 7-12: context-conditioning, asynchronous freshness, recursive context selection, context-to-action gaps, behavioral/outcome evaluation, scientist-agent external baselines.
- Revision 13: ChatGPT Work primary; Claude stopped as executor.
- Revision 14: recurring durable-authority reconciliation, not one-time cleanup.
- Revision 15: O-centered context kernel.
- Revision 16: withdrawn integrity quarantine for malformed/truncated write.
- Revision 17: generation 7 resume.
- Revision 18: recursive Skill-in-Skill Context Kernel architecture proposal, safely appended and acknowledged.
- Revision 19: scientist-agent positive-control/evaluation-scope observation, safely appended and acknowledged.
- Revision 20: negative evidence is scoped only to the actually tested candidate/configuration/conditions, no family-wide generalization, and no duplicate positive-control reproduction when provenance-equivalent original conditions are already established; now acknowledged in live execution.
- PR 289 merged `append_remote_user_input_inbox` with expected revision, schema validation, one expected-blob CAS, and exact remote readback.

## Current recursive Skill-in-Skill design
- O Engine is a recursive Skill-in-Skill context-system candidate. All relevant durable context should be reachable from inside O Engine but not materialized all at once.
- Kernel is conceptually the always-entered minimal root context/Skill.
- Each Skill with children may support model-reasoned child selection; no mandatory Selector Skill at every level.
- The model reasons over current context, opens one or multiple useful child Skills, reasons again, and recursively continues until enough context exists to decide/act.
- Local Skill criteria/checklists/priors are optional, situation-dependent, falsifiable, and may guide local judgment and child selection.
- Routing/context selection is evaluated by downstream decision/outcome quality, missed-needed context, unnecessary context load/interference, elapsed time, and cost.

## Scientist-agent evaluation scope
- Scientist-agent family remains an external baseline/research source, not adopted or rejected wholesale.
- Checkpoint inheritance was one extracted/adapted candidate; failure or insufficient evidence there does not disprove the family or untested mechanisms.
- Positive controls are needed only where they disambiguate reproduction failure, adaptation/ablation loss, and evidence against the original method.
- Negative evidence cannot exceed the exact tested candidate/configuration/conditions.
- PR 291 merged a precommitted matched context comparison and scientist-agent causal-classification protocol.

## Zero-Work external research acceleration — current user preference
- User wants external acceleration without increasing ChatGPT Work usage.
- Preferred architecture: keep Work/O primary execution call volume unchanged; run external research harvesting outside Work using free/non-Work infrastructure.
- Strong default candidate is an LLM-free GitHub Actions research harvester: scheduled/matrix jobs query free public sources/APIs (for example arXiv, OpenAlex, Crossref, Semantic Scholar where permitted, GitHub public repos/releases, benchmark/result feeds), collect metadata/full public evidence where allowed, normalize, deduplicate, and score for novelty/evidence strength/relevance.
- Parallelism should use available free GitHub Actions concurrency/quota dynamically; workers are read-only and produce artifacts only, never become main writers.
- Avoid using extra Work model calls for each worker. Retrieval, provenance checks, dedupe, citation graph expansion, keyword/mechanism tagging, and first-pass ranking should be deterministic/programmatic where possible.
- Only a small top-K decision-relevant digest/artifact reaches O, ideally consumed inside an already-existing Root/context-selection call rather than creating extra Work calls. Prefer replacing lower-value context with this digest instead of simply increasing prompt size.
- Research index should persist seen papers/repos/mechanisms, source hashes, extracted claims, evidence type, O-known/tested status, and rejection reasons so later runs avoid repeated discovery.
- If model-based external analysis is ever added, it should use a non-Work/free resource and remain optional; do not assume Copilot or other provider usage is free without checking current quota/terms.

## Continuous external research status
- `clean_g1` is the authoritative ongoing external-research generation. `research_index_clean_g1/INDEX.json` is revision 3, digest `4b463efb44299ecfd10540382b823d72b0a8bc89f7311023181b313b30e1a7af`; `research_index_clean_g1/O_FEED.json` is revision 3, digest `d339314cfc52566ebba3db89501d2c16de07f0f2b35fce81460b1d451b932f90`.
- All legacy `research_workers/`, `research_comparators/`, and `research_index/` material is explicitly `pre_independence` historical evidence only. It remains preserved for provenance/comparison, but it does not define or steer clean worker frontiers and is not bridged as clean evidence.
- Clean worker health at integration cutoff `bachikoljunior-blip/note@f08a15edabf6fe39dab219ae96d876015f0f174d`: 11 clean workers have persisted 14 clean artifacts containing 73 raw candidate records, canonicalized into 31 scoped mechanism families. The latest added evaluation checkpoint contributes controlled-intervention, first-error/process-selection, bias/prompt-robustness, and cross-benchmark trajectory-evaluator evidence. All 11 worker frontiers remain nonempty.
- Clean novelty comparator is current only for its 17:42:58 snapshot: it assessed 67 raw candidates as 11 known, 22 partially tested, 34 uncovered, 0 evaluated. Current coverage is 67/73; `self_improvement/C8` plus the five newer evaluation candidates are not yet assessed. Exact O-tested scope remains preserved and no narrow O failure is generalized to a candidate family.
- Clean evidence comparator assessed the prior 68-candidate snapshot and then primary-verified several gaps. Notable scoped upgrades are `self_improvement/C3` A-, `self_improvement/C4` A-, `continual_learning/CLG1-CL-005` A-, `continual_learning/CLG1-CL-006` A, and `long_horizon/LH-Context-Folding` A-. Five newer evaluation candidates remain outside that evidence snapshot. The Integrator preserves these as evidence-strength judgments only, separate from novelty/relevance.
- Clean decision-relevance comparator remains stale at its 16:43:27 state with 0 current candidate assessments. This is the principal non-fatal feed blocker; novelty/evidence are not collapsed into a substitute relevance score.
- O_FEED revision 3 therefore intentionally contains zero items with status `held_pending_current_decision_relevance_and_full_comparator_coverage`. Current gates are novelty 67/73, evidence 68/73 plus verification deltas, relevance 0/73. No candidate is bridged until all required clean dimensions are current, scope-matched, and traceable.
- Clean role separation remains intact: the Integrator used only `research_workers_clean_g1/` and `research_comparators_clean_g1/` as clean primary inputs; no O-derived/comparator/integrator information was written back into clean workers. Raw member-level comparator results are preserved rather than flattened where canonical-family members differ.
- Clean Bridge remains separately stateful in `research_index_clean_g1/BRIDGE_STATE.json`. Its 2026-08-25T17:54:31+09:00 checkpoint observed feed revision 1 before the current Integrator advances; O's authoritative state still acknowledged inbox revision 21 while revision 22 clean-feed reconciliation was active on PR 308 at exact head `d03fd0bdaf7ec6386a0e2c283ac8ee8d509c33a1`. Highest acknowledged clean-feed revision therefore remains 0/digest null until the Bridge re-reads revision 3 at a normal safe boundary; no duplicate subscription and no extra Work invocation were created.
- Legacy inbox revision 21 and legacy `research_index/O_FEED.json` remain `pre_independence`; their acknowledgement is not clean_g1 uptake. Detailed findings stay under `research_workers_clean_g1/`; comparator judgments under `research_comparators_clean_g1/`; canonical state/feed under `research_index_clean_g1/`; bridge cursor/health under `research_index_clean_g1/BRIDGE_STATE.json`.

## Evaluated mechanism/candidate status so far
- Checkpoint inheritance: harness/provenance built in PRs 263-265; genuine matched native observations initially unavailable; not adopted or disproven in principle. Generation 9 later began reconciling 12 bounded-stage measurement receipts under Revision 20 scope rules.
- Deterministic recursive history commitment v2: adopted/merged in PR 266; internal engineering only.
- Lazy recursive Skill context-routing infrastructure: adopted/merged in PR 268; semantic child-selection benefit still under evaluation.
- Held-out recursive routing activation: not adopted after contaminated/insufficient observations.
- Four-way CI sharding: adopted/merged in PR 270 and reduced feedback-loop latency.
- O-centered Context Kernel / DecisionContextManifest + Event-Ledger: selected under revision 15 and actively engineered; not yet proven end-to-end superior.
- Full-context-everywhere/raw-copy default: not selected.

## Current execution process / latest known checkpoint
- Work runtime is the outer executor; O Engine owns semantic decision cycles. A single fenced writer holds development mutation authority.
- O semantic cycle: Root -> Candidate/Preflight -> Execute -> Task Evaluate -> Consolidate/Learn -> Root.
- External effects are fenced/idempotent, exact-head validated, and read back before completion.
- Generation 9 is active after fail-closed recovery from a generation-8 checkpoint durability inconsistency.
- Revision 20 is acknowledged and applied.
- Generation 9 implemented a checkpoint-integrity verifier and then returned to scientist-agent/checkpoint measurement evidence reconciliation.
- Latest observed active work: PR 303 `agi: reconcile checkpoint measurement evidence`, exact head `a175150e05452f28d6b32a78260ad3e65dbfa7d6`, reconciling 12 bounded-stage checkpoint-inheritance receipts, reusing 3 provenance-equivalent controls rather than duplicating them, and explicitly limiting the negative result to the tested candidate/configuration/executor-model/budget/tasks/rubric/conditions. At last check its exact-head CI run `32803793697` was queued.
- AGI remains unsupported; internal engineering progress is not AGI evidence.

## Chat operating policy
- Before each O-related response, restore from this file first.
- Update this file after each substantive conversational step so current design can be reconstructed if old chat context drops.
- Do not automatically send every derived idea to O. Distinguish user-originated design/context, concrete external observation/failure, and inference O can probably derive itself.
- When drafting O input, preserve user semantics while minimizing redundant context and avoiding premature architecture lock-in.