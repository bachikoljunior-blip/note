# Self-improvement Phase-1 — PromptAgent Chat-native strategic tree-search audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-003`
- calibration candidate: `CAND-FRESH-003`
- bound public family: `PromptAgent`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 3, decision blob `53bac6afcf72dc3969c9581731c275cc8dad689c`
- mechanism: `PROMPTAGENT-CHAT-TREE-v1`
- semantic work observed at: `2026-08-29T12:22:23.041203+09:00`

## 1. Public mechanism audit

Primary/public sources: Wang et al., *PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization*, ICLR 2024 / arXiv:2310.16427, https://arxiv.org/abs/2310.16427 ; Microsoft Research publication page https://www.microsoft.com/en-us/research/publication/promptagent-strategic-planning-with-language-models-enables-expert-level-prompt-optimization/ ; official repository https://github.com/XinyuanWangCS/PromptAgent .

PromptAgent formulates prompt optimization as strategic planning rooted in Monte Carlo Tree Search. Intermediate prompts are treated as states, error-feedback-based refinements as actions, and future rewards guide search toward high-reward prompt paths. The released implementation stores intermediate nodes/paths and uses task correctness/reward metrics. This Phase-1 leaf does not reproduce its benchmark performance or literal MCTS runtime.

## 2. Safe recurring-Chat reduction

`PROMPTAGENT-CHAT-TREE-v1` maps a tree node to a stable role-local assignment-policy candidate with lineage. Tree actions are bounded role-local edits proposed from durable error evidence. Error/reflection prose is advisory only.

The crucial separation is factual versus simulated reward. A hypothetical rollout or simulated future reward may order exploration, but it is always `NONFACTUAL`: it cannot satisfy terminal evidence, update the selector archive, produce frontier credit, or certify completion. Only independent terminal mechanical evidence after durable readback becomes factual node reward. Factual backpropagation is delayed until readback and applies only to pre-existing safe ancestor IDs; same-transition generation and reward cannot self-certify.

Root/config/control binding, CLEAN semantic-input boundaries, safety/protected-authority boundaries, stable frontier/candidate/node/transition identities, sealed selector decision, two-phase outcome durability and readback-before-credit remain immutable. Unsafe or unevidenced nodes are not promotable by simulated reward. Recovery and the sealed factual selector decision override tree expansion/reselection.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_promptagent_chat_native_ablation_v1_2026-08-29T1222_JST.json`, blob `432c4a5ac9149b0affa975fbf8bc068604a3428a`.

The unchanged frozen OPRO guard set passes **8/8**. Ten planning-specific counterexamples pass **10/10**: simulated reward cannot create credit; simulated outcome is not terminal evidence; unsupported error feedback cannot drive an action; control-rewriting expansion is quarantined; unsafe high-simulation node is quarantined; same-transition self-certifying backprop is rejected; pre-readback factual reward does not backpropagate; duplicate node/transition updates once; safe independently evidenced node improvement may be selected; and exact factual tie keeps the incumbent.

This establishes exact-scope controller conformance only, not PromptAgent task-quality superiority.

## 4. Exact-scope terminal outcome

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-003`: **SATISFIED_EXACT_SCOPE**, bound to PromptAgent.

Stable terminal transition ID:

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-003:SATISFIED:PROMPTAGENT-CHAT-TREE-v1:20260829T1222JST`

Under pre-frozen `TERMINAL-UTILITY-v2.1`, this status maps to utility `2`, subject to immutable outcome-record creation/readback and external outcome sealing. No archive/sticky update occurs in this artifact itself.

## 5. Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this terminal evidence; create/read back the immutable round-3 outcome record; externally seal it; only then update the v2.1 history archive and sticky state and award this frontier credit. The already-predeclared `CAND-FRESH-004` / critique-search, `CAND-FRESH-005` / population-search and `CAND-FRESH-006` / meta-feedback leaves remain OPEN for subsequent selector rounds without any family-specific semantic read yet.
