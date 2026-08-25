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
