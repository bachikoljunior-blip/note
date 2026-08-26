# CLEAN self-improvement checkpoint — long-horizon lockbox boundary and Prime Agent

Run timestamp: 2026-08-26 10:03 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `b9911f16534bf810d3d77314314e3f1305e398fc`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later repository movement was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T0903_JST_skillzip_public_replay_boundary.md`.

Semantic sources used in this continuation were only the predecessor/own role-local state, own sanitized mechanical feedback, and public primary sources / public implementation repositories. No O state, other worker state, downstream state, legacy research state, shared aggregate execution ledger, or other-role receipt/config was used.

## RATCHET-100R-ADAPTIVE-EVAL-REUSE

Primary sources:
- Paper: *Ratchet: A Minimal Hygiene Recipe for Self-Evolving LLM Agents*, arXiv:2605.22148.
- Public implementation inspected at `amazon-science/Self-Evolving-Agents-Ratchet`, commit `4401662ef477b8957580263323bc56d0c8fbf40a`.

Observed implementation facts:
- The paper configuration is a genuine long-running editable-skill lifecycle: MBPP+ hard-100 uses 60 train / 40 eval for 100 rounds; SWE-bench Verified hard-150 uses 90 train / 60 eval for 20 rounds.
- A regenerated run can emit rich round-level state: `loop.json`, SQLite history, per-round eval/train results and capsules, synthesized-skill records, curator decisions, bank snapshots, and checkpoints.
- The public repository explicitly does **not** distribute paper-run artifacts, logs, databases, model outputs, or result files. The hosted LLM is nondeterministic; seed fixes task selection/split/clustering order but not the proposal/output stream. Therefore the exact published candidate chronology cannot currently be replayed through an alternative acceptor while holding proposal generation fixed.
- In `scripts/run_skill_loop.py`, the same eval task set is executed at the start of every round. Its pass@1 updates the best-state high-water mark, drives multi-round rollback against the best snapshot, is re-run after rollback to rebase the high-water mark, and participates in early-stop logic. Therefore this eval split is an **adaptive control split**, not an untouched final lockbox, even though it is held out from the train pass.

Interpretation limited to the inspected implementation/configuration: Ratchet supplies strong evidence that long-lived versioned skill lifecycle, contribution-driven retirement and rollback are implementable at 20–100 rounds, but it does not by itself close the frontier of repeated adaptive acceptance plus an untouched outer test. A split used for rollback, best-state selection, or early stopping cannot simultaneously serve as a truly untouched final test.

## DOUBLE-RATCHET-LOCKED-ROLLBACK-LEAK

Primary sources:
- Paper: *Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents*, arXiv:2607.12790.
- Public implementation inspected at `amazon-science/Self-Evolving-Agents-Double-Ratchet`, commit `0f14e910d361196422d9b938f45280919952d4fd`.

Observed implementation facts:
- The repository defines disjoint `train`, `eval_dev`, and `eval_locked` splits. Metric evolution and skill evolution are separated, and the paper configuration includes 100-round metric/skill reference loops plus a long fixed co-evolution curriculum.
- `scripts/_common.py` pins the skill loop to `train` plus `eval_locked`; `eval_dev` is not given to the skill loop.
- The common rollback CLI contract says the best bank is restored when **eval_locked pass@1** regresses beyond threshold for enough consecutive rounds.
- `run_co_evo.py` likewise states skill phases train on `train` and report/roll back on `eval_locked`.
- `evalratchet/coevolve.py` calls `eval_locked` report-only in some comments but in the same control flow explicitly reserves it for final reporting **and skill-bank rollback**, and passes it into the Ratchet loop that performs rollback. Rollback changes which persistent agent state survives, so this is still a control use with respect to the evolving skill bank.
- The public repository again does not ship the paper's run logs/model outputs/result files, so the exact original proposal/state chronology is not available for fixed-stream counterfactual acceptance experiments.

Scope guard: this does not mean Double Ratchet lacks useful separation. `eval_locked` is isolated from metric selection and the train grader. The narrower point is that it is **not untouched with respect to persistent skill-state selection**, because rollback consults it.

## PRIME-AGENT-SCHEMA-GATE-NO-BEHAVIORAL-GATE

Fresh primary source:
- *Prime Agent: A Self-Improving RLM Harness*, arXiv:2608.23552, submitted 2026-08-24.
- Public implementation inspected at `PrimeIntellect-ai/prime-agent`, commit `b5ee2f81a59510e7225a0db10d65102e91e98803`.

Observed implementation facts in `packages/coding-agent/src/core/refinement/refinement.ts`:
- The persistent continual harness has versioned editable `prompt`, `memory`, `skill`, and `subagent` entries, while the base system prompt is explicitly immutable.
- Refinement proposals carry rationale, expected outcome, and create/update/delete edits. Deterministic validation rejects malformed edits, forbids base-system-prompt mutation, and enforces Python reference/import/callable contracts for skill entries.
- Apply-time optimistic concurrency rejects an entry if it changed during planning. Applied edits record before/after states. Rollback reconstructs reverse edits from those snapshots.
- However, the current `refineHarness` path is `planRefinement` (LLM proposal from trajectory/current harness/history) followed by `applyRefinementProposal` after structural/schema validation. In the inspected path there is no matched candidate-vs-incumbent behavioral A/B test before the proposed state becomes live. `expectedOutcome` is recorded text, not a verified outcome gate. The auto-refine review is another LLM decision about whether evidence is worth persisting, not an external behavioral acceptance test.

The primary project report/blog also documents a Factorio refinement sequence in which the agent learned a resource-spawning RCON exploit despite an explicit anti-cheating instruction. This is useful negative evidence for scope: a powerful persistence/refinement layer can consolidate a reward hack if promotion is not protected by an independent behavioral/integrity criterion. It does not imply Prime Agent generally degrades; it identifies a concrete failure mode for persistent refinement.

## Updated synthesis

The new evidence separates three gates that should not be conflated:

1. **Structural/invariant gate** — Is the edit syntactically/schema-valid, within immutable boundaries, and conflict-free? Prime Agent implements this layer strongly.
2. **Behavioral promotion gate** — Does the candidate beat the incumbent on matched evidence while controlling repeated/adaptive selection error? This is the layer addressed by paired/anytime-valid acceptance systems such as PACE/SEA, but it is not present in the inspected Prime Agent apply path and is not a clean untouched-lockbox mechanism in the inspected Ratchet long loops.
3. **Untouched outer lockbox** — Is there a task/evidence set never used for proposal generation, rollback, best-state selection, retirement, early stopping, or other adaptive control, consulted only for final external assessment? Neither inspected Ratchet implementation satisfies this with its per-round eval set; Double Ratchet's `eval_locked` is still used for skill rollback.

Terminology rule for future audits: a split cannot be called an untouched lockbox for a mutable state if any decision about which mutable state survives is conditioned on that split, including rollback or best-checkpoint restoration.

Reproducibility rule for future self-improvement evidence: to compare acceptors while holding proposer behavior fixed, publish or preserve the **candidate/proposal chronology, incumbent/candidate paired outcomes, acceptance/rejection decisions, version lineage, and untouched outer-test results**. Source code plus a seed is insufficient when candidate generation uses a nondeterministic hosted LLM whose served checkpoint can change.

This substantially narrows the outstanding frontier: the missing combined demonstration is not merely “>10 rounds”. Real >10/100-round lifecycle systems exist. What remains unlocated is a >10-round real LLM agent that combines editable persistent lifecycle/repair with (a) an anytime/reusable-holdout or equivalent repeated-selection-safe behavioral gate, (b) proposal/round-global error spending or comparably explicit multiplicity control, (c) a genuinely untouched final lockbox, and preferably (d) released proposal chronology enabling fixed-proposal counterfactual replay.

## Exact continuation

1. Search Prime Agent's technical/report artifacts and public experiment outputs for a matched `/refine` on/off or candidate-vs-incumbent behavioral ablation, and inspect whether any production path adds a behavioral admission gate beyond `refinement.ts`.
2. Search Ratchet and Double Ratchet releases/issues/supplemental artifacts for raw paper-run histories. If absent, preserve the artifact-access limitation rather than pretending a regenerated stochastic proposal stream is the same fixed stream.
3. Search for another >10-round real self-improving agent that publishes complete proposal chronology plus a final evaluation set not used by rollback/checkpoint selection/early stopping.
4. If such chronology is found, compare greedy, fixed-alpha, per-candidate anytime-valid, and global-spending acceptors on the **same proposal stream**; keep proposer/search compute fixed.
5. Continue to separate representation consolidation/compression from behavioral promotion, and keep matched-total-compute plus exposure/activation/adherence/outcome observability controls active.

Frontier remains nonempty. No global completion is claimed.