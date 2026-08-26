# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1808_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, and `RUN_20260826T1808_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- CLDD provenance correction remains: the public 5→10 tuning-stream table delta does not isolate stream-count causality because each fresh Optuna study has an unspecified TPE sampler seed. No public realized-HPO receipt/archive was found through the newly checked channels. The Zenodo parquet files are present with published MD5s, but this runtime still cannot fetch the 13.5/28.0 MB binaries for independent verification.
- New strong supervised task-free candidate: CVPR Findings 2026 `SinglePrompt` shows that learned prompt selection can be a complexity tax. On CIFAR100, 10-prompt learned selection (79.89 A_auc / 82.12 A_last) is almost the same as random selection (79.78/81.85), while one prompt without a selector reaches 81.05/82.38 with about 75% fewer learnable parameters in that stripped comparison.
- More important than the prompt itself, SinglePrompt's component ablation identifies local classifier-interference control: removing minibatch label masking collapses CIFAR100 from 85.58/87.53 A_auc/A_last to 65.57/51.81 and raises F_last from 5.89 to 48.19. The code confirms that this mask is built from current+replay ground-truth labels, so the evidence is task-boundary-free but supervised, not label-free.
- Public SinglePrompt artifact is pinned to `efficient-learning-lab/SinglePrompt@de86f7594057ebdeaf5eb33173a96669a70c0439`. Apparent paper/code batch mismatch is resolved: paper batch 32 corresponds to the script's stream `temp_batchsize=64//2=32`; buffer mode adds a separate 32-example replay minibatch.
- High-impact artifact knobs are now pinned: ImageNet-21k `ViT-B_16.npz` frozen backbone; prompt layers 0–4, length 20, Uniform[-1,1] prompt init; cosine head temperature 0.1; Adam LR .005, weight decay 0, constant scheduler; deterministic seeds 1–5; supplied commands leave AMP off. Buffer mode uses reservoir replacement and uniform random replay, not specialized replay selection.
- SinglePrompt's no-buffer full results exceed the reported MISA baseline on CIFAR100/Tiny-ImageNet/ImageNet-R by +6.55/+8.03/+14.96 A_last points, but baseline values are borrowed from MISA rather than re-run in the same codebase. Preserve that caveat. No independent numerical rerun/failure was found in the newly checked public channels.
- Provisional negative-evidence benchmark: DRIFT (arXiv:2605.12998) continuously mixes latent graph-task distributions and reports large degradation of several boundary/partition-dependent continual methods under smooth Gaussian transitions. Use it only as a benchmark constraint against assuming crisp boundaries until artifact/final-publication verification is stronger.

Exact next action:
1. CLDD: stop repetitive archive searching unless a genuinely new channel appears; otherwise prepare the paired `72d12ff...` five-stream vs `f186455...` ten-stream reconstruction with identical `my_f1`, fixed streams and matched explicit `TPESampler(seed=s)` values across several seeds.
2. SinglePrompt: seek independent reproduction/failure or a same-code MISA rerun; do not re-read already pinned internals unless a discrepancy appears.
3. Search for matched-budget text/LLM analogues of `shared adapter + label-local negative-gradient suppression` versus dynamic prompt/router/MoE selection. Keep supervision semantics explicit and do not transfer the vision result by analogy alone.
4. DRIFT: verify code/final artifact and extract a minimal smooth-transition matched protocol for boundary-triggered versus continuous-control methods.
5. When CLDD binary transport becomes available, MD5-check A/B and recompute event confusion from stored arrays, then separate held-out open-loop detector quality from closed-loop learner utility.
6. continue broader replay/plasticity/world-model/curriculum frontier.

Frontier must remain nonempty.
