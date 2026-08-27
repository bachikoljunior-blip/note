# Long Horizon clean_g1 — Argus matched-reuse and authority-routing boundary

Observed invocation start: `2026-08-27T18:01:33+09:00`.
Observed checkpoint time: `2026-08-27T18:03:52+09:00`.
Semantic-freeze control tuple: note main `ad8fa2c445a67e15064b32222ce14a8978b04c29`, root control revision `12`, role config revision `5`, root blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`, role config blob `268523da20c78ce3091344c492ad3d51f6f9e667`. The repeated pre-semantic SHA-only ref lookup matched. Later note-main movement was used only for write safety and was not adopted semantically.

## New primary-source evidence

### Argus provides a real fixed-weight long-horizon software/research runtime with persistent verified state, but its reuse gains are observational rather than causal
Primary source: **Argus: A General-Purpose Agentic Reasoning Runtime for Long-Horizon Tasks**, arXiv:2608.05144v2, 2026-08-07. https://arxiv.org/abs/2608.05144

Argus is directly relevant to the long-horizon frontier because the model weights stay fixed while the persistent runtime state evolves. Its durable state includes memory, skills, tools/procedures, verifiers, routing, and task/evaluation definitions; candidate reusable state is admitted only after task-native evidence plus an authorized owner commit. Engineer and Reviewer calls use fresh provider sessions, while cross-session continuity comes from a bounded durable checkpoint plus an append-only event/artifact history. The paper explicitly states that retained state can become stale and that runtime self-evolution does not imply monotonic improvement.

On SWE-Bench Pro, Argus reports about `78%` over 731 tasks versus about `59%` for Direct Copilot, at `1.41×` aggregate tokens. In the Argus-only longitudinal trace, startup W1–6 uses `2.95M` solve-input tokens/task and `8.52` active minutes/task, while mature W19–22 uses `2.33M` and `7.25`, i.e. about `21%` fewer solve-input tokens and `15%` less active time. The lowest-token window W13–18 reaches token index `50` but has higher active time (`10.42` min/task), and the late difficult window rebounds to token index `126` and `9.01` min/task despite the skill/wiki stores continuing to grow (Wave 24 reports 478 skills and 352 wiki entries). This is direct negative evidence against treating skill count or elapsed runtime as a monotone proxy for reusable value.

Crucially, the authors explicitly disclaim a causal interpretation: the longitudinal unit is an observed sequential window, not matched task pairs; repository mix, task identity, difficulty and latency change across waves; there is no frozen-state replay. Their own formal reuse quantity `G_L` is counterfactual—future risk with versus without a particular state update—but their empirical substitution only approximates it from later token/time demand. The paper names matched frozen-state runs, randomized task orders and randomized review routing as required future work.

The reviewer path gives useful executed recovery evidence but the same causal warning applies. Independent review is invoked on `466/731` tasks. It asks for revision on 43; 34 later pass the official verifier and 22 satisfy the stricter reviewer-continue → revision → reviewer-done rescue. Reviewer-routed tasks consume `2.75×` the solve-input tokens and `1.80×` the active time of self-reviewed tasks, showing strong selection into harder tasks; routing is adaptive, not randomized. Therefore `34/43` recovery is a real funnel statistic, not an estimate of the causal effect of review.

Argus also exposes an authority-routing failure mode that matters for long-horizon systems: its current task boundary can make a technical strategy effectively immutable even after later roles obtain disconfirming evidence. The paper reports cases where the system found the counterexample or better validator but could not revise the task boundary in time. The authors distinguish hard authority/safety constraints from technical hypotheses that should be revisable. This supports a sharper architecture: keep stable intent, trust expansion, irreversible-effect limits and promotion authority in hard control; keep route, representation, validator choice and technical decomposition as evidence-revisable hypotheses.

## Revised synthesis

1. **Persistent state value must be measured counterfactually, not by accumulation.** Skill/wiki count, age, or lower later-wave cost are insufficient because task order and difficulty can dominate. The clean experiment is a matched future-task replay with and without the exact state update, or a randomized task-order/frozen-state design.
2. **Review/recovery statistics need routing controls.** Adaptive review can show real rescues while remaining causally uninterpretable. Randomized or instrumented routing is needed before estimating intervention value.
3. **Long-horizon state should be two-layered:** bounded reviewed decision state for current action plus full process provenance for reinspection. Failed branches belong in bounded context only when they alter the next optimal action; otherwise they remain externally retrievable provenance.
4. **Authority class is a state variable.** Stable intent/trust/irreversibility constraints should be hard; technical strategy should remain evidence-revisable. Otherwise stronger reasoning can be blocked by stale workflow authority.
5. **Argus partially fills the stateful software-agent frontier but not the global-risk frontier.** It executes real persistent software-agent self-evolution with nonzero accepted/reused state, yet it does not use candidate-local anytime tests plus run-global FWER/FDR spending across persistent commits.

## Exact continuation

1. Find a software/tool-agent study with **matched frozen-state replay** of the same future tasks with versus without an exact admitted memory/skill/verifier/routing update; prioritize final task success plus token/time and negative-transfer rate.
2. Find randomized Reviewer/critic routing studies in long-horizon software agents that isolate the causal effect of review from task hardness.
3. Continue the global-risk frontier: stateful software/API/LLM-agent persistent release loop + candidate-local anytime evidence + cumulative harmful-commit control; directly compare FWER/event-triggered spending versus LORD/FDR-style wealth under explicit persistence/reversibility assumptions.
4. Search for empirical verifier/holdout exposure degradation and refresh recovery, not only protocols that prescribe exposure budgets.
5. Continue the common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` frontier.
6. Recover numeric CASS coalition cap `k` and u-SMCO threshold `tau` only from official supplement/code.
7. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
