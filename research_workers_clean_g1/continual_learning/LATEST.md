# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260825T2032_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the clean run checkpoints through `RUN_20260825T2032_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator output, or any other worker state.

Exact next action: begin with independent ARROW replication/failure and a matched dual-buffer model-free ablation; if no direct replication exists, inspect the public ARROW artifact to isolate which updates consume FIFO versus long-term replay and whether the causal gain is specifically world-model consolidation. Then compare EEM against a newer label-independent same-label-domain-shift detector (ODDL/DEMD/expansible-ViT), extracting exact boundary delay/false-expansion/parameter-growth/forgetting evidence from a PDF-capable path. After that, return to HESTIA exact-table retrieval and visually extract Li–Hiratani real-image task-order gains. Do not stop after one branch resolves.

Frontier must remain nonempty. Current priority gaps: HESTIA exact tables/ablations; same-label label-independent boundary evidence with capacity accounting; independent EEM/ARROW/FOREVER replication; ARROW causal world-model-vs-buffer isolation; adaptive short-/long-term replay allocation; task-order exact real-image gains and similarity-estimation cost; matched memory/FLOPs/parameter-growth/boundary-information comparisons; plasticity-specific controls; autonomous active curriculum under unknown future streams.
