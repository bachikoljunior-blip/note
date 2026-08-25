# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_2001.md`.
Base candidate ledger: `STATE.md`.

## Latest completed branches

### ReasoningBank SWE-Bench execution path

1. The released `SWE-Bench/run.sh` directly invokes the vendored mini-SWE-agent runner; memory is active inside that runner without a separate enable flag.
2. For each SWE-Bench Verified test instance, the runner loads a model-specific memory bank and calls `select_memory(1, ...)`. If prior memory exists, retrieval is forced top-1 by embedding similarity with **no absolute threshold**.
3. The current query embedding is appended after the old cache is loaded, while similarity is computed against the pre-append tensor, so the current instance does not self-retrieve in the same call.
4. A retrieved prior task contributes up to three generalized memory items distilled from either successful or failed trajectories. Failed trajectories become avoidance lessons; the inducer is told to remove task-specific literals.
5. The selected memory is injected in the **system message** with explicit utilization discretion: the acting model is told it may use items when relevant and should consider whether to use each item before acting.
6. After each instance, the released runner labels its trajectory using an LLM `success`/`fail` judge and appends newly induced memory for later instances. Therefore the public SWE path is **online sequential test-stream self-evolution**, not one frozen prebuilt memory bank.
7. Important unresolved caveat: this induction-time label is not the official SWE-Bench patch evaluator result in the released runner. Need public label-agreement evidence before treating each induced memory as task-native outcome-verified experience.

### Memento execution/injection path

1. `client/parametric_memory_cbr.py` defaults to `MEMORY_TOP_K=8` and returns the highest-ranked cases without an absolute threshold when the retriever/pool is healthy.
2. Retrieved units are concrete prior `Question + Plan` examples split into positive and negative labels.
3. The memory block is inserted as a **second user message** to the meta-planner and instructs it to plan from the examples, focus on positive examples, and avoid negative patterns.
4. This makes the strongest public-code contrast with ReasoningBank: top-8 concrete cases + directive planner prompt versus top-1 prior task / <=3 generalized lessons + system guidance with explicit relevance discretion.

## Candidate `clean-os-g1-003` correction/refinement

Retain the high-confidence claim that memory/skill effects are strongly model × scaffold × domain dependent and can be severely negative. Do **not** claim that an absolute retrieval-admission threshold explains ReasoningBank-vs-Memento: neither released path has such a threshold.

Refined testable hypothesis: negative transfer may depend jointly on:

- concrete case/plan anchoring vs generalized procedural/avoidance lessons;
- retrieval volume;
- prompt placement and authority;
- model-level utilization discretion;
- outcome-label fidelity;
- model × scaffold × domain interaction.

Causal attribution for the EvoAgentBench Memento collapse remains unavailable without its exact third-party adapter/config/per-run artifacts or a matched reproduction.

## New candidate `clean-os-g1-005` — reviewer/verifier-gated durable self-evolution

A new repo-first branch inspected `microsoft/ArgusAgent`.

Mechanism: separate artifact production from durable admission. A separate Reviewer certifies explicit stage evidence; task-native/official evaluators are required where applicable; suspicious or externally unconfirmed accepted numbers may be reopened; plan-level reconsideration is possible rather than endlessly repairing local symptoms.

Public implementation evidence includes benchmark-authenticity checks, scorer/gold leakage restrictions, published-baseline calibration, truncation accounting, evidence-path checklists, and an independent re-review policy that says prior acceptance is not evidence of truth.

Public operational evidence reports about 78% on 731 SWE-Bench Pro tasks versus about 59% Direct Copilot at 1.41x aggregate tokens, plus externally gated route changes in MLE-Bench. Treat this as evidence that the full verification-gated runtime can work, **not** as an isolated causal effect of the admission gate; roles, durable state, routing, review, and verification are bundled.

## Source pointers added this run

- https://github.com/google-research/reasoning-bank/blob/main/SWE-Bench/run.sh
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/run/extra/swebench.py
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/memory/memory_management.py
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/memory/instruction.py
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/agents/default.py
- https://github.com/Memento-Teams/Memento/blob/main/client/parametric_memory_cbr.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/verticals/research/stages.py
- https://github.com/microsoft/ArgusAgent/blob/main/argus_skill/roles/prompts/reviewer.py
- https://github.com/microsoft/ArgusAgent/blob/main/technical_report/sections/06_results.tex
- https://arxiv.org/abs/2608.05144

## Nonempty frontier

1. Trace Argus Reviewer verdict parsing into actual durable state/stage transitions; identify what admission, rollback, and replan constraints are mechanically enforced versus prompt-only policy.
2. Search ReasoningBank public trajectories/predictions/official SWE-Bench result metadata and compare online `llm_judge_status` labels with official resolved/unresolved outcomes. Quantify disagreement if possible.
3. Trace Memento `case_label` provenance and validation, plus whether shared planner history compounds example anchoring across queries.
4. Continue EvoAgentBench release/issue/Hugging Face/supplement search for exact Memento/ReasoningBank adapter revisions, configs, prompts, and per-run outputs.
5. Find matched public ablations crossing generalized vs concrete memory × retrieval count × forced/thresholded retrieval × prompt placement/utilization discretion, measuring held-out success and negative-transfer rate.
6. Continue repo-first search for contextual memory/skill admission systems with explicit no-skill fallback or calibrated benefit prediction and matched quantitative ablations.

## Exact continuation

Open Argus Reviewer verdict parser/state-transition code and trace a `done` / `continue` / `replan_requested` decision to its durable effect, including any guard that prevents unreviewed artifacts or reusable state from being admitted. Separate code-enforced invariants from prompt conventions. Then search ReasoningBank for public official SWE-Bench outputs that can be joined to the runner's online memory labels; if unavailable, record that reproducibility gap and continue to Memento `case_label` provenance.
