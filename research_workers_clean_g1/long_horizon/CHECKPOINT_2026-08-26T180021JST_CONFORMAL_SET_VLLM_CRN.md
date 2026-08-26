# Long Horizon clean_g1 — conformal-set rollback / vLLM CRN checkpoint

## Frozen semantic control tuple
- invocation_started_at: `2026-08-26T17:57:27+09:00`
- checkpointed_at: `2026-08-26T18:00:21+09:00`
- frozen note main SHA: `cc9cb9fae8c79c150521a860142ab7d7b0e27e85`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- pre-semantic second SHA-only lookup matched the frozen SHA.
- semantic boundary preserved: only this role's own clean state, own sanitized feedback, and public sources were used. No O/O-derived state, other worker state/config/output, downstream/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, other-role receipts, or commit-message/diff payload was used semantically.
- own sanitized feedback item `lh-own-observability-boundary-20260825` was consumed mechanically: shared aggregate ledger and other-role receipts were not read.

## New primary-source findings

### 1. Conformal error attribution provides a principled *set-valued* rollback uncertainty layer, but its guarantee is coverage of one labeled decisive step — not recovery success
`Conformal Agent Error Attribution` (arXiv:2605.06788; May 7, 2026) defines the decisive error as the earliest error from which the MAS cannot recover, then outputs a contiguous interval of trajectory steps with finite-sample marginal coverage under exchangeability. Its Left/Right/Two-Way filtration methods are therefore directly relevant to the current frontier on calibrated top-k/set-valued localization and abstention-like behavior.

Primary source: https://arxiv.org/abs/2605.06788
Code: https://github.com/layer6ai-labs/conformal-agent-error-attribution

Scope guard: the paper assumes one decisive error per failed trajectory and exchangeability between calibration/test examples. The coverage theorem is not a generic guarantee under deployment shift and is not a guarantee that rolling back to the returned interval will improve the final task outcome.

### 2. The paper's own rollback table is strong evidence that decisive-error coverage and downstream recovery utility are different quantities
The automated rollback experiment samples 100 MACNET failed trajectories for each GSM8K location-density variant, uses a fine-tuned Qwen3-1.7B scoring model, targets 80% conformal coverage, rolls back to the *first* step in the conformal set, and restarts the MAS with a modified prompt containing information from the failed trace.

Reported Table 5 values:
- Left Dense: Top-1 success `0.76±0.05`, coverage `0.92±0.03`, cost `0.83±0.02`; VCP success `0.73±0.05`, coverage `0.85±0.03`, cost `0.79±0.02`; LF success `0.77±0.04`, coverage `0.81±0.05`, cost `0.90±0.00`.
- Mid Dense: Top-1 success `0.67±0.05`, coverage `0.86±0.03`, cost `0.56±0.02`; VCP success `0.59±0.05`, coverage `0.95±0.02`, cost `0.65±0.01`; LF success `0.68±0.05`, coverage `0.81±0.03`, cost `0.65±0.01`.
- Right Dense: Top-1 success `0.71±0.05`, coverage `0.86±0.04`, cost `0.50±0.02`; VCP success `0.70±0.05`, coverage `1.00±0.00`, cost `0.66±0.02`; LF success `0.75±0.04`, coverage `0.82±0.04`, cost `0.40±0.01`.

The clearest counterexample is Right Dense: VCP attains perfect measured rollback coverage (`1.00`) but lower success (`0.70`) and higher redo cost (`0.66`) than LF, whose coverage is only `0.82` but success is `0.75` with cost `0.40`. Mid Dense shows the same qualitative separation: VCP coverage `0.95` but success `0.59`, versus LF coverage `0.81` and success `0.68`.

Operational implication: **do not optimize a rollback target/localizer for decisive-error coverage alone.** Coverage can be a safety/uncertainty constraint, but target utility must be measured by live post-rollback outcome, disruption, and recovery cost. A calibrated prediction set is better viewed as a candidate region / uncertainty envelope around the historical target.

### 3. The rollback success numbers above do not isolate historical target selection because the carry-forward intervention changes too
The paper's rollback implementation does not simply restore state and resume. It restarts with a modified prompt that marks a prior conversation segment as containing wrong information and includes failed-trace context so the MAS can avoid repeating the mistake. This is a substantive failed-branch carry-forward / corrective-hint intervention.

Therefore Table 5 cannot identify the causal value of VCP/LF target selection alone. Target location, amount of redo, and restart guidance are bundled. This preserves the strict selector-only gap from the previous checkpoint.

### 4. Current vLLM main supplies a practical *token-position-keyed* common-random-number primitive for local/open-model branch experiments
The current vLLM GPU Gumbel sampler constructs noise using the request `seed`, absolute token `pos`, and token-id key. The code explicitly states that token ids key the noise and `pos`+`seed` place the draw in the request stream; the kernel computes `gumbel_seed = tl.randint(seed, pos)` and then draws keyed Gumbel noise per token id.

Primary implementation inspected on current public vLLM main:
- `vllm/v1/worker/gpu/sample/gumbel.py`
- https://github.com/vllm-project/vllm/blob/main/vllm/v1/worker/gpu/sample/gumbel.py

This is useful for the current strict rollback-selector benchmark: at the same token position and seed, divergent logits/contexts can be exposed to the same per-token Gumbel noise, which is a much stronger model-side CRN primitive than a stateful generator whose draw index drifts with branch control flow.

But it is **position-keyed, not semantic-event-keyed**. If different rollback arms reconstruct prompts of different lengths or otherwise shift the decode position, `pos` changes and the coupling no longer corresponds to the same causal event. The benchmark must either align branch-local token positions by construction or record where model-CRN alignment ceases to be meaningful.

### 5. vLLM's new trace-replay path is a useful exact-prefix audit primitive, but not yet a live historical-target branch API by itself
Current vLLM documentation (dated Aug. 20, 2026) exposes `trace_decode_token_ids`: the engine can force a predetermined decoded token sequence while still computing the model's real logprobs/ranks under the current inference configuration. The request emits exactly the trace and then stops; stop conditions are disabled during the trace. The current implementation derives replay step from GPU state (`total_len - prompt_len`) and overwrites sampled tokens with the recorded trace.

Primary docs/source:
- https://docs.vllm.ai/en/latest/serving/online_serving/trace_replay/
- https://github.com/vllm-project/vllm/blob/main/vllm/v1/worker/gpu/sample/trace_replay.py

This provides a practical way to audit prefix reconstruction and model-probability consistency before a counterfactual branch. Limitations matter: the documented path is incompatible with `n>1`, speculative decoding, structured outputs, several logit-masking features, and it terminates after the forced trace rather than automatically switching the same request into live sampling. A rollback benchmark therefore still needs an explicit verified handoff from forced prefix replay to live continuation (or a new request/session whose prefix/inference state is proven equivalent).

## Synthesis delta
The historical-target controller should now separate **uncertainty region** from **target choice**:
1. Produce a calibrated/set-valued candidate region where feasible (e.g. conformal contiguous interval under a validated exchangeability regime).
2. Apply exact admissibility/safe-boundary constraints.
3. Within the admissible region, choose the actual historical restore target according to the explicitly declared objective (earliest cause / first sufficient intervention / latest rescue / latest safe / intended version).
4. If the admissible set is empty or target evidence is insufficient, abstain or acquire a bounded counterfactual probe rather than force a single point.
5. Evaluate live task success, disruption of originally-successful trajectories, redo cost, external-effect safety, allocated recovery budget, and realized recovery dose separately from localization coverage.

For strict local-model counterfactual evaluation, vLLM now offers two useful building blocks:
- forced trace replay for prefix/logprob auditing;
- seed+absolute-position+token-id keyed Gumbel sampling for partial model-side CRN coupling.
Neither removes the need to verify workspace/tool state, inference-state rebinding, branch-local budget equality, and the semantic meaning of token-position alignment after divergent rollback targets.

## Strict selector-only gap status
Still open. The conformal rollback paper is useful precisely because it demonstrates why coverage and final recovery can diverge, but it does not hold carry-forward policy and historical target selector as the only varying factor. I still did not locate a software/tool/GUI-agent study that fixes target objective, alarm, candidate set, admissibility, restore/carry-forward, model/verifier, probe budget, allocated and realized recovery opportunity, and stochastic coupling while varying only the historical target selector and measuring final live task success.

## Exact continuation
1. Audit `Conformal Agent Error Attribution` against *executed replay* ground truth rather than injected/annotated decisive-error labels: search whether conformal intervals retain their nominal coverage for causally pivotal or first-sufficient-intervention targets.
2. Search conformal/selective localization under distribution shift or non-exchangeable sequential agent traces; identify online/reweighted/risk-control variants that can fail closed when coverage assumptions break.
3. Quantify vLLM model-CRN fidelity across divergent prompts/branches: same seed + same absolute decode position vs shifted prefix length/position. Measure token/action agreement and outcome variance under same-model control branches.
4. Search for or prototype a verified `trace replay -> live sample` handoff that preserves prefix token state/KV equivalence; otherwise treat trace replay only as an audit/reconstruction primitive.
5. Continue searching rollback studies that report realized post-rollback model calls, admissible actions, environment steps and successful tool calls, not only nominal limits.
6. Extend the strict selector harness with `conformal_candidate_region`, `coverage_assumption_status`, `model_crn_alignment_span`, `trace_replay_verified_prefix`, and `live_handoff_equivalence` fields.
7. Preserve target semantics: decisive-error label, earliest causal origin, first sufficient intervention point, latest rescue/point-of-commitment, latest admissible/safe checkpoint and intended semantic version are distinct.
8. Preserve the strict selector-only gap unless all non-target variables are genuinely controlled.
9. Maintain a nonempty frontier; this checkpoint is not global completion.
