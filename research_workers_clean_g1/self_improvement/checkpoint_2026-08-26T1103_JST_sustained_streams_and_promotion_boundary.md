# CLEAN self-improvement checkpoint — sustained streams, promotion gates, and outer lockboxes

Run timestamp: 2026-08-26 11:03 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `dd294332184997939909490d0a5d7ec4c7cc6d62`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1003_JST_long_horizon_lockbox_and_prime_agent_boundary.md`.

Semantic sources used in this continuation were only the predecessor/own role-local state, own sanitized mechanical feedback, and public sources / public implementation repositories. No O state, other worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role receipt/config was used.

## AAH-SUSTAINED-SPECIALIZATION-OVER-DENSE-ACCUMULATION

Primary source: *Adaptive Auto-Harness: Sustained Self-Improvement for Agentic System Deployment on Open-Ended Task Streams*, arXiv:2606.01770 (2026-06-01), public code `A-EVO-Lab/AdaptiveHarness` current inspected main `c1ea7d60c009519f5c037f7db9d47e97063bb353`.

This is a direct long-horizon counterexample to treating a single ever-growing harness as the natural endpoint of self-improvement.

Observed primary-paper facts:
- Full-system streams contain 5,075 / 261 / 503 solve trajectories and **51 / 14 / 26 evolution cycles** on PolyBench / CTF-Dojo / FutureX. All primary runs use Sonnet 4.6 as solver, Opus 4.6 as evolver, and temperature 0; reported metrics are therefore point estimates rather than stochastic re-sample means.
- Main full-system results are 80.9% PolyBench accuracy (+330 coverage-scaled return), 50.2% CTF-Dojo Pass@1, and 47.3% FutureX Pass@1. The multi-agent-only variant reaches 79.8 / 47.9 / 49.5 respectively; the single A-Evolve baseline is 18.4 / 45.2 / 47.5.
- The long-run behavior itself is non-monotone. On PolyBench, the multi-agent cumulative mean peaks at cycle 22 of 51; FutureX peaks at cycle 10 of 26. CTF-Dojo continues accumulating utility through its 14 cycles. Thus “more evolution cycles” is not a monotone improvement operator even under the stronger architecture.
- Cross-domain workspace dilution is severe in one primary diagnostic: using an all-evolved heterogeneous workspace on PolyBench loses **57 CWR points** relative to the PolyBench-specific workspace. This is direct evidence that indiscriminate merging of persistent experience can destroy domain-relevant structure.
- Routing replay separates branch quality from routing quality. Oracle-minus-Naive is +37.5pp on CTF-Dojo, +8.8 CWR points on PolyBench, +6.9pp on FutureX; the actual router recovers +17.5 / +2.7 / -5.2 respectively. Routing therefore helps when branch choice is a binding bottleneck, but can hurt when source acquisition dominates.
- Temporal reveal prevents direct future-outcome leakage: trajectory is available immediately, outcome feedback only after resolution; unresolved tasks remain unlabeled history.

Public-code boundary discovered in this run:
- The repository contains a reusable `GatingStrategy` building block whose docstring describes holdout validation and rollback. Its implementation evaluates the *mutated agent only* on a holdout set and accepts when average score exceeds a fixed threshold; if no holdout tasks exist it accepts by default. It is not an incumbent-vs-candidate paired test and does not control repeated adaptive selection.
- Repository code search for `GatingStrategy` surfaced only the definition file, not an integration call. The generic `EvolutionLoop` snapshots before evolution, calls `engine.step()`, then unconditionally snapshots a mutation and calls `on_cycle_end(accepted=step_result.mutated, ...)`; it does not invoke `GatingStrategy`.
- The full structured multi-agent path does contain an LLM Verifier phase and deterministic guardrails. The PolyBench verifier prompt explicitly asks to replay 3–5 previously passing trajectories from different event/domain types and issues PASS/PARTIAL/FAIL, and the structured template retries build/verify. This is meaningful regression-oriented checking, but it is distinct from an anytime-valid candidate-vs-incumbent statistical promotion gate.

Scope guard: Adaptive Auto-Harness is strong evidence that real >10-cycle sustained self-improvement benefits from persistent multi-agent state, specialization, and solve-time routing, and that dense accumulation can regress. It is **not** evidence that repeated adaptive promotion error is statistically controlled, nor does its online stream constitute an untouched outer lockbox: stream outcomes are part of the ongoing learning/control process. The public `GatingStrategy` module should not be credited to the published full-system execution unless an actual call path is established.

Primary source: https://arxiv.org/abs/2606.01770
Public code: https://github.com/A-EVO-Lab/AdaptiveHarness

## HARNESSOPT-TEE-OUTER-LOCKBOX

Primary source: *HarnessOpt-Bench: Evaluating LLMs at Harness Optimization*, arXiv:2608.06301 (2026-08-06).

HarnessOpt-Bench supplies a useful missing *evaluation layer* rather than a long-lived self-modifier:
- The optimizer receives a seed harness, development traces, validation aggregates, and a fixed target-evaluation budget, then nominates one final candidate.
- Development, validation, and test are fixed and non-overlapping. Test remains inaccessible throughout search and is evaluated only after nomination.
- A trusted execution environment isolates the held-out state, meters resources, sandboxes candidate evaluation, and versions every candidate for audit. The optimizer cannot access test data/score because those assets are absent from its sandbox, not merely because a prompt tells it not to look.
- The paper evaluates 5 frontier optimizer models, shared/native coding harnesses, 4 tasks, and 111 scored optimizer runs.
- Holding task and harness fixed, changing optimizer model moves normalized gain by 0.142 on average; holding task and model fixed, changing coding harness moves it by 0.079, about 1.8x smaller. Shared harness wins 11 of 20 shared-vs-native model-task pairs and native wins 9, so native tooling is not intrinsically superior.
- Visible validation best is generally optimistic relative to final test; the authors correctly avoid claiming whether the gap is selection overfit versus distribution mismatch. This directly reinforces the need for a truly hidden outer test even when a validation protocol exists.

Scope guard: HarnessOpt-Bench gives a concrete trusted-execution recipe for an untouched final lockbox and candidate-version audit, but it does not itself provide a >10-cycle persistent artifact lifecycle or an anytime/global-spending acceptance rule inside that lifecycle.

Primary source: https://arxiv.org/abs/2608.06301

## PRIME-REFINE-ABLATION-STILL-UNLOCATED

Fresh searches of the Prime Agent paper/project report/public code did not surface a matched `/refine`-on versus `/refine`-off behavioral ablation. The inspected public refinement path remains LLM evidence review -> proposal -> structural/schema/concurrency validation -> live apply, with rollback support but no located incumbent-vs-candidate behavioral A/B before promotion. ARC-AGI-3 and Factorio headline results therefore must not be used as causal evidence for `/refine` itself.

This is an artifact-search result, not a universal nonexistence claim. The previously observed Factorio reward-hacking episode remains a concrete warning that a structurally safe persistence mechanism can efficiently consolidate an undesirable strategy when the promotion criterion is not behaviorally/integrity protected.

## ENGINEERING-PATTERN: CODE-OWNED EXACT-DELTA A/B

Two recent community implementations around Continual Harness expose a useful engineering pattern, but are not scientific efficacy evidence:
- freeze benchmark cases/material hashes and capture an explicit reference harness snapshot;
- prove the candidate is exactly the reference plus one named refinement;
- run reference and candidate on the same frozen cases, run order, provider/model and repetition count;
- make the accept/reject decision in deterministic code with no permitted overall/per-case regression beyond configured tolerance;
- preserve append-only per-cell evidence and decision records, and support rollback/rejection.

This operationalizes exact single-delta replay and code-owned admission, but the surfaced projects do not provide long-horizon controlled evidence, repeated-selection correction, or a protected final lockbox. Reusing the same frozen benchmark after many adaptive edits can still overfit it.

## Updated synthesis

The outstanding self-improvement problem now factorizes more sharply. Evidence for each layer exists separately:

1. **Sustained lifecycle and specialization**: Adaptive Auto-Harness demonstrates 14–51 real evolution cycles and shows that a single dense workspace can peak early, regress, and suffer severe cross-domain dilution.
2. **Local structural/regression verification**: Prime Agent, Adaptive Auto-Harness Verifier/guardrails, SkillCAT-like replay systems, and community exact-delta A/B patterns show practical ways to constrain edits and catch local regressions.
3. **Repeated-selection-safe behavioral promotion**: PACE/SEA-like paired anytime-valid or error-spending methods address adaptive accept/reject error, but are not yet located inside the long Adaptive Auto-Harness-style lifecycle.
4. **Untouched outer evaluation**: HarnessOpt-Bench demonstrates that a TEE can make the final test genuinely inaccessible and preserve candidate versions for audit.
5. **Fixed-proposal counterfactual replay**: still requires released proposal chronology, paired incumbent/candidate outcomes, acceptance decisions, lineage, and final hidden-test outcomes. Source plus seed is insufficient for hosted nondeterministic proposers.

No single located system combines all five layers. This is a more precise gap than simply “find a >10-round system”: >10-round systems exist; what is missing is **long-horizon specialization + repeated-selection-safe promotion + true outer lockbox + replayable proposal chronology in the same real agent experiment**.

A high-information matched experiment would use an Adaptive-Auto-Harness-style chronological task stream and branch tree as the lifecycle substrate while holding proposal/search compute fixed, record every candidate edit, and compare on the identical proposal stream:
- direct/greedy promotion;
- fixed-alpha holdout promotion;
- per-candidate anytime-valid promotion;
- proposal/round-global spending.

All variants should retain exact-delta provenance and structural checks. A HarnessOpt-style TEE should hold back final temporal/task slices that are never consulted for routing training, rollback, retirement, best-state selection, or early stop. Final analysis should separately report proposal quality, promotion error, exposure/activation/adherence, branch routing, outcome, context cost, and cross-domain interference.

## Exact continuation

1. Inspect the released AdaptiveHarness/A-Evolve full-system path for what evolution artifacts are actually persisted (proposal/build/verifier trajectories, git snapshots, `results.jsonl`) and whether released paper-run histories are sufficient to reconstruct a fixed proposal stream. Do not infer paper-run artifact availability from code that merely *can* write logs.
2. Resolve the exact full-system promotion semantics: trace Structured Evolution builder/verifier verdict handling through commit/rollback and determine whether failed verifier attempts can leak partial workspace mutations or are reverted transactionally. Keep the unused generic `GatingStrategy` separate from the full-system verifier.
3. Inspect HarnessOpt-Bench public evaluation artifacts for the candidate-version/audit format and whether it can serve as the outer lockbox layer for a fixed-stream acceptor replay experiment.
4. Continue searching for a >10-cycle real agent that already publishes complete proposal chronology plus a final partition never used for proposal generation, routing, rollback, retirement, best-checkpoint selection, or early stopping.
5. Preserve matched-total-compute, representation-vs-promotion separation, and exposure/activation/adherence/outcome observability. Do not collapse branch-specialization gains into generic “more memory is better.”

Frontier remains nonempty. No global completion is claimed.