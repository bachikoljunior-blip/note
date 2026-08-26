# Long Horizon clean_g1 checkpoint — causal confidence, intervention targeting, and memory governance

Checkpointed at: 2026-08-26T21:03:21+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `fdee4a06e6b300c66907fe545fc4a017d8937e0d`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, own sanitized feedback, and public sources only. No O, other-worker state, downstream state, aggregate ledger, or other-role receipts were read.

## New evidence 1 — consequence memory can improve *which* steps are worth intervening on
Primary source: `Critic Experience Bank: Self-Evolving Step-Level Confidence Estimation for LLM Agents`, arXiv:2607.12397, 2026-07-14. Public full-text rendering: https://academ.us/article/2607.12397/

The Critic Experience Bank (CEB) keeps a frozen critic model but stores hindsight-labeled past state/action/outcome records. At a new proposed action, it retrieves similar productive and unproductive past cases keyed by task, state, and action. On Mind2Web, AMEX, and InterCode-Bash, across three critic backbones, CEB has the best ECE/Brier/AUC in every reported dataset-model cell. On GPT-5.4 Mind2Web, the deployed CEB has ECE `0.176`, versus `0.318` with no bank. Removing productive/unproductive contrast degrades ECE to `0.241`; random bank retrieval gives `0.218`, showing that the benefit is not generic prompt length but consequence-conditioned, state/action-matched evidence.

Most important for this frontier, the paper includes a controlled *frozen-state intervention-targeting* diagnostic. On a 200-task Mind2Web subset (1,613 steps), every method receives the same frozen action/state and exactly the same generic regeneration instruction when flagged. The regeneration budget is matched; the only changed variable is which steps the confidence method selects. Baseline per-step correctness is `0.183`. At 10% / 25% / 50% regeneration budgets, CEB reaches `0.201 / 0.234 / 0.256`; Random reaches `0.185 / 0.197 / 0.215`; Oracle `0.202 / 0.236 / 0.277`. Perplexity and mean-entropy selection are below Random at the smaller budgets, directly demonstrating over-intervention disruption from a misaligned signal.

A second fixed-review simulation maps confidence ranking into final task success. With the same GPT-5.4 critic and a per-task oracle review budget `m=1/2/3`, Mind2Web task success rises from base `2.1%` to CEB `5.5 / 12.5 / 23.7%`, versus Oracle `9.8 / 21.2 / 34.9%`. On AMEX, base `20.6%` becomes CEB `33.4 / 44.7 / 54.6%`, versus Oracle `43.9 / 60.7 / 72.9%`.

### Scope guard
This is not a closed-loop live recovery result. The stronger regeneration test replaces selected actions on a frozen state and remeasures step correctness; later trajectory state is not rolled forward. The paper itself lists live intervention as future work. Therefore this closes part of the prior `context/confidence -> intervention targeting` gap, but not `intervention targeting -> live long-horizon final outcome`.

## New evidence 2 — memory should carry reliability metadata through its full lifecycle, not only at admission
Primary source: `MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance`, arXiv:2608.21867, submitted 2026-08-22 and updated 2026-08-25. Public repo: https://github.com/whyyyyy123/MemGuard

MemGuard treats verifier output as persistent metadata on each reusable memory: reward, confidence, label, uncertainty, criterion scores and provenance/view information are attached before activation and reused during retrieval, conflict resolution, summarization and archival. The paper reports matched-runtime comparisons on Terminal-Bench 2.0, SWE-Bench Verified, WebArena and Mind2Web across four backbones and five seeds. It reports the best success metric and lowest average steps in all 16 backbone-benchmark cells, with gains over ReasoningBank up to `+7.9` success-rate points on WebArena, `+5.6` step-success-rate points on Mind2Web, and `+2.4–3.5` points on terminal/software-engineering settings.

The public implementation confirms an important boundary: it is a reusable governance core, not the benchmark runtime. Its documented contract keeps unverified records provisional; reranks eligible memories using verifier quality/confidence/applicability/recency/usage/conflict/staleness; keeps failure memories as constraints rather than positive action recipes; and manages provisional/active/summary/archived states. Benchmark harnesses, datasets, model clients and full agent loops are explicitly not bundled in the repo.

### Scope guard
The end-to-end benchmark numbers are author-reported preprint evidence. The public repo supports implementation plausibility of the governance core but does not independently reproduce the reported benchmark runs. Do not treat repo availability as independent reproduction.

## New evidence 3 — anytime-valid abstention/acting control exists for adaptive streams, but it is not a localizer
Primary source: `Conformal Selective Acting: Anytime-Valid Risk Control for RLVR-Trained LLMs`, arXiv:2605.20270, 2026-05-18.

CSA maintains a Ville-style e-process per action threshold and gives an anytime-pathwise selective-risk guarantee under predictable updates and isotonic-calibrated monotone risk. It is evaluated over 480 specialist streams, 160 adversarial-shift streams and 10,300 rounds of live online-LoRA expert iteration; the authors report it as the only one of ten compared wrappers satisfying pathwise validity and non-refusing deployment in every evaluated cell.

### Scope guard
CSA certifies whether to act/refuse under an adaptive deployment filtration. It does *not* identify a causal error step, select a rollback checkpoint, or prove that a given memory/context item caused a decision. Its role in the current synthesis is a pre-commit `act / abstain` statistical gate, not a historical target selector.

## Updated synthesis
The memory/recovery controller should distinguish at least four different uses of historical experience:
1. **Decision influence evidence** — does this context item or retrieved experience measurably change the next action/intervention ranking?
2. **Reliability governance** — is the memory itself still admissible, non-conflicting, sufficiently verified and within scope?
3. **Selective-action control** — is current evidence sufficient to act now under an adaptive stream, or should the controller abstain/defer?
4. **Historical recovery targeting** — if intervention is chosen, which admissible past state should be restored?

CEB provides unusually clean evidence for (1): same frozen state, same regeneration mechanism, matched budget, selector changed. MemGuard supports (2) at lifecycle level. CSA supports (3) at stream level. None of them alone solves (4), and none jointly proves the full stack.

A strong design hypothesis is therefore: `verified lifecycle memory -> consequence-aware pre-action critic -> anytime-valid pre-commit act/abstain gate -> safe/admissible checkpoint filter -> historical target selector -> live branch recovery`. The order matters: a memory being semantically similar is insufficient; a critic being calibrated is insufficient; a risk gate being valid is insufficient; and a checkpoint being historically plausible is insufficient.

## New negative evidence / cost trade-offs
- CEB retrieval depth `k=1 -> 5` raises total input tokens from `1,746 -> 2,971` (`+70%`) while ECE improves `0.182 -> 0.169` (~7% relative). `k=2` reaches `0.176` at only `+18%` tokens. More memory is not monotonically cost-effective.
- CEB's generic token uncertainty signals can be actively harmful as intervention selectors: removing the lowest-confidence steps under mean entropy/perplexity can lower retained correctness, and fixed regeneration on their selected steps can underperform Random.
- The CEB bank is not compressed or evicted in the reported study; the authors explicitly identify large-stream scaling as future work. Persistent governance therefore needs admission, consolidation and archival rather than unbounded accumulation.
- MemGuard's code repository excludes the evaluation harness, so implementation-core availability must not be conflated with benchmark reproducibility.

## Experiment design delta for the strict long-horizon harness
Add two distinct factorials before the historical rollback-selector comparison:

### A. Decision-influence / intervention-targeting factorial
Freeze: reconstructed state, action agent, candidate action, intervention text, regeneration budget, tool/environment state, sampling coupling. Vary only the evidence used by the critic/selector:
- no historical evidence,
- random history,
- similarity-only history,
- positive-only history,
- contrastive productive+unproductive history,
- lifecycle-governed contrastive history.
Measure: confidence calibration, low-confidence concentration of truly bad actions, action shift after the same intervention, realized recovery dose, next-state validity, final live task success, and disruption of originally-successful trajectories.

### B. Pre-commit selective-action factorial
Freeze the action proposal and recovery actuator. Compare fixed threshold, ordinary calibrated probability threshold, anytime-valid e-process gate, and oracle. Measure false-cut rate, missed dangerous actions, action/abstention coverage, final success and irreversible-effect violations.

Only after those are fixed should the historical target selector vary (`random / latest-safe / earliest-cause / latest-rescue / learned / meta-agent / oracle`).

## Exact continuation
1. Find a live closed-loop study where the *same intervention/replanning actuator* is used and only the pre-action confidence or memory-evidence selector varies; require final tool/software/GUI task outcome, not frozen-step correctness.
2. Search for memory-lifecycle ablations that isolate persistent verifier metadata at admission vs retrieval vs conflict resolution vs summarization/archival; do not credit complete-system gains to any one stage without factorial evidence.
3. Search anytime-valid/selective-risk work that explicitly couples to irreversible tool actions or transactional commits; keep act/abstain certification distinct from rollback localization.
4. Search calibrated top-k / conformal / e-process style *localizers* on adaptively queried trajectories. CSA is a risk gate, not a localizer.
5. Continue strict historical rollback-selector gap search with matched post-intervention action/token/retry budgets and realized recovery dose.
6. Continue common-random-number/prefix-state-integrity work for live branch comparisons.
7. Preserve memory semantics: useful memory, reliable memory, decision-proximal memory, causally influential memory and safe-to-act memory are not interchangeable labels.
8. Maintain nonempty frontier; this checkpoint is not global completion.
