# Open Source clean_g1 — continuation

Status: active; frontier nonempty.

## Follow-up completed after initial checkpoint

The initial highest-priority EvoAgentBench retrieval branch was partially executed.

1. EvoAgentBench’s public `benchmark/src/skill_evolution/README.md` confirms that the public release includes Baseline and EverOS paths, but **does not include third-party method integrations or experiment outputs**. Therefore the exact adapter/config used to obtain the published Memento/ReasoningBank cells cannot be reconstructed from EvoAgentBench alone.
2. The upstream Memento repository currently resolves to `Memento-Teams/Memento`. Its public `memory/np_memory.py` implements non-parametric retrieval by embedding all stored task/question keys, embedding the current task, computing cosine similarity, and returning the top-k entries. In this code path there is **no minimum similarity threshold, no compatibility classifier, and no vanilla/no-memory fallback based on retrieval confidence**; it always returns up to `top_k` nearest memories when the bank is nonempty. This is a concrete candidate explanation for negative transfer, but not yet a causal explanation of EvoAgentBench’s −36.3 SWE-Bench cell because the benchmark’s third-party adapter is not public.
3. ReasoningBank’s public repository states that its memory content is distilled reasoning learned from **both successful and failed trajectories**, and that it combines this with memory-aware test-time scaling. The repo includes SWE-Bench and WebArena code, but the quick search did not yet identify the exact retrieval/injection implementation used by EvoAgentBench. Thus the Memento-vs-ReasoningBank performance difference remains mechanistically unresolved.

## Updated inference

The evidence for `clean-os-g1-003` is strengthened at the implementation level: at least one public Memento retrieval path performs unconditional top-k similarity retrieval without an explicit confidence/admission gate. Combined with EvoAgentBench’s large negative-transfer cell, this raises the priority of testing a thresholded/verified retrieval admission layer. However, do **not** claim this caused the EvoAgentBench regression until the missing adapter/config is recovered or independently reproduced.

## New source pointers

- https://github.com/EverMind-AI/EvoAgentBench/blob/main/benchmark/src/skill_evolution/README.md
- https://github.com/Memento-Teams/Memento/blob/main/memory/np_memory.py
- https://github.com/google-research/reasoning-bank
- https://github.com/google-research/reasoning-bank/blob/main/README.md

## Exact continuation

1. Inspect `Memento-Teams/Memento/memory/parametric_memory.py` and `train_memory_retriever.py` to determine whether the parametric path adds calibration/thresholding or is also forced-retrieval.
2. Traverse ReasoningBank’s WebArena/SWE-Bench code from run entrypoints to find the exact memory retrieval and prompt-injection path; record whether failures are distilled into generalized strategy text, how memories are ranked, and whether retrieval can be skipped.
3. Search EvoAgentBench issues/commits/releases and paper supplements for the omitted third-party integration/config; if unavailable, mark causal attribution blocked and propose an independent matched reproduction using its official train/test IDs.
4. Preserve `clean-os-g1-003` as interaction/gating evidence even if causal adapter details remain unavailable; do not generalize Memento failure beyond the tested scaffold/model/domain cell.
