# Open Source clean_g1 — continuation

Status: active; frontier nonempty.
Latest detailed run: `RUN_20260825_1903.md`.
Base candidate ledger: `STATE.md`.

## Latest completed branch: Memento vs ReasoningBank retrieval mechanics

1. Memento's public non-parametric **and parametric** retrieval paths are forced top-k when the memory bank is nonempty. The parametric path scores every case with a binary relevance classifier and ranks by positive-class probability, but inference has no absolute probability threshold or no-memory fallback.
2. ReasoningBank's public WebArena path also performs forced nearest-memory retrieval: it embedding-ranks the bank and selects `n=1` with no similarity threshold when memories exist. Therefore the earlier hypothesis that a retrieval admission gate distinguishes ReasoningBank from Memento is **not supported by the public code**.
3. The stronger implementation-level distinction is the memory representation and use contract. ReasoningBank distills up to three generalized reasoning items from both successful and failed trajectories, explicitly converting failures into avoidance lessons and removing task-specific literals. The retrieved text is appended as system guidance that the model may use when relevant and should explicitly consider item-by-item before acting. Memento's tracked public memory artifact uses concrete prior `case` + short `plan` units.
4. Independent evidence still supports ReasoningBank as a mechanism family: the ICLR 2026 paper/public Google summary reports matched gains over memory-free agents of +8.3 points on WebArena and +4.6 on SWE-Bench-Verified for Gemini-2.5-Flash, with almost three fewer SWE-Bench execution steps per task. This does not identify the cause of the EvoAgentBench cell.
5. EvoAgentBench's public benchmark release explicitly omits third-party self-evolution integrations and experiment outputs; current public issue/commit search did not recover the Memento/ReasoningBank adapter/config. Causal attribution for the Nanobot/Qwen3.5-27B SWE-Bench Memento 45.8→9.5 cell remains blocked without a matched reproduction or hidden adapter provenance.

## Candidate correction

For `clean-os-g1-003`, retain the high-confidence claim that memory/skill effects are strongly model × scaffold × domain dependent and can be severely negative. Retain confidence-gated/no-memory fallback as a valuable **testable safety mechanism**, but do not claim missing admission gating explains Memento-vs-ReasoningBank. Public ReasoningBank code also retrieves unconditionally.

Refined hypothesis: negative transfer may depend more on the retrieval unit and utilization contract — concrete case/plan memories versus generalized success/failure reasoning, and automatic injection versus explicit model-level relevance consideration — than on retrieval abstention alone. These components should be ablated separately.

## New source pointers

- https://github.com/Memento-Teams/Memento/blob/main/memory/parametric_memory.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/train_memory_retriever.py
- https://github.com/Memento-Teams/Memento/blob/main/memory/memory.jsonl
- https://github.com/google-research/reasoning-bank/blob/main/WebArena/memory_management.py
- https://github.com/google-research/reasoning-bank/blob/main/WebArena/run.py
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/memory/induce_memory.py
- https://github.com/google-research/reasoning-bank/blob/main/third_party/src/minisweagent/memory/instruction.py
- https://github.com/google-research/reasoning-bank/blob/main/WebArena/agents/legacy/agent.py
- https://openreview.net/forum?id=jL7fwchScm
- https://research.google/blog/reasoningbank-enabling-agents-to-learn-from-experience/

## Nonempty frontier

1. Trace ReasoningBank's SWE-Bench mini-swe-agent memory path from CLI/config through retrieval into the model prompt. Record retrieval count, threshold behavior, memory format, prompt location, and whether the model may ignore retrieved memory.
2. Trace Memento's agent-side prompt/injection path in its server/client execution code. Determine how concrete case/plan memories are rendered and whether reward/case labels affect post-retrieval use.
3. Search EvoAgentBench paper appendix/supplement/Hugging Face metadata for archived third-party adapter commit/config/prompt/per-run artifacts; otherwise mark exact causal reconstruction publicly unavailable.
4. Design a matched open reproduction: concrete case/plan vs generalized success/failure reasoning, crossed with forced retrieval vs thresholded retrieval vs model-level utilization discretion; measure held-out success and negative-transfer rate.
5. Continue repo-first search for contextual skill-admission systems with public matched ablations, no-skill fallback, and uncertainty/calibration.

## Exact continuation

Open `google-research/reasoning-bank/third_party/src/minisweagent` and trace the SWE-Bench memory path from CLI/config through memory selection into the model prompt. If the released SWE runner does not actually activate memory, record that gap explicitly. Then inspect Memento's execution/injection path and build a component-level comparison of retrieval unit, ranking, abstention, prompt placement, and utilization discretion.
