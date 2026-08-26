# CLEAN self-improvement checkpoint — exogenous acceptance and evidence warrants

Run timestamp: 2026-08-26 14:02 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `d015ba42a6f12e1996850825fb185d1b1dd03676`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement, if any, is mutation transport only and is not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1313_JST_trace_grounded_repair_vs_warrant.md`.

Semantic inputs remained restricted to own role-local clean state, own sanitized mechanical feedback, and public sources/public implementation artifacts. No O/O-derived state, other worker state, downstream state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used.

## SIG-SEAL-EXOGENOUS-ACCEPTANCE-BOUNDARY

Primary source: *Self-Authored Verification Is Unreliable in Heuristic Self-Improving Agents*, arXiv:2607.24300v1, submitted 2026-07-27. Full-text extraction was cross-checked through a current public mirror because direct arXiv HTML retrieval was intermittently unavailable.

This paper directly tests a failure mode adjacent to the current warrant frontier: the same self-improving agent is allowed to rewrite both a programmatic Atari policy and its self-authored tests. The agent-visible self-score can remain high while hidden deployment performance collapses.

Across the 35 valid model-game cells in the unprotected cross-game experiment, every final self-score is at least 0.70, yet 15/35 final policies score below the corresponding random-play reference; six terminate at Pong's -21 floor. The failure does not require explicit cheating: policy and tests can co-adapt around the same mistaken assumptions.

The proposed Sealed Exogenous Acceptance Loop (SEAL) preserves self-authored tests for debugging/proposal generation but removes their sole deploy authority. Before each promotion, a fixed harness-private audit compares the candidate against the incumbent on hidden task-native rollouts disjoint from training, self-tests, and final deployment evaluation. The agent cannot author or inspect the audit and receives only an accept/reject bit; a clear regression rolls back the entire policy+test state.

On the main Breakout ablation matrix, SEAL exceeds the unprotected condition for all six core models. Internal-only constraints are not enough: monotone self-test strengthening and an agent-authored discriminative check both fall below no protection for four of the six core models. Illustrative model means include Gemini 7.9 -> 30.0 and Doubao 19.1 -> 35.1 under SEAL.

The compute-matched pilot fixes proposal count. Mean final deployment truth is 7.7 for no protection, 13.9 for an endogenous gate, and 15.4 for SEAL; mean peak-to-final loss is 6.9, 0.5, and 0.4 respectively. This makes retention rather than extra search a central mechanism. Audit confidentiality matters: revealing numerical audit scores after rejection is lower than sealed SEAL in five of six rows; the largest displayed reversal is Doubao 35.1 -> 12.7.

Primary: https://arxiv.org/abs/2607.24300
Current public full-text mirror used for table extraction: https://paperz.arrangedbits.com/papers/e887da67-fffe-46e3-a009-4e1200e91ad6

### Scope / unresolved boundary

SEAL is strong evidence for an **exogenous deployment-acceptance boundary**, not a complete long-horizon statistical solution. Its audit is fixed and repeatedly queried through accept/reject bits. The paper itself shows that the audit is an imperfect proxy: in an illustrative long trace, the second accepted state raises audit score from 12.7 to 14.2 while deployment truth falls from 17.6 to 13.8. Therefore hidden/exogenous evidence sharply reduces overwrite risk but does not imply zero false acceptance.

The fixed audit is not described as an anytime-valid e-process, reusable-holdout mechanism, or proposal/round-level global error-spending contract. Repeated single-bit feedback can still convey adaptive information. A stronger long-loop contract would combine the SEAL boundary with repeated-selection-safe evidence accounting and retain a truly untouched outer deployment test.

## SIG-EVE-EVIDENCE-VERIFIABLE-CURRICULUM

Primary source: *EVE-Agent: Evidence-Verifiable Self-Evolving Agents*, arXiv:2605.22905v1, submitted 2026-05-21.

EVE-Agent is the clearest self-evolving system found in this branch that makes **support evidence itself a first-class training object**. The proposer emits `(question, answer, evidence)` and the evidence span must be copied verbatim from the source document or retrieved snippets. The evidence verifier estimates the marginal contribution of the span by comparing the current solver's probability of producing the proposer-provided answer with evidence versus without evidence, with search disabled in both conditions:

`V_t(q,e,a) = p_t(answer=a | q,e) - p_t(answer=a | q)`.

This is materially stronger than accepting a fluent explanation or a syntactically present citation block. In the matched comparison, backbone, retriever, search tool, and optimization framework are unchanged relative to the prior Dr. Zero-style system; the central change is the evidence-oriented reward (plus the solver's evidence-recovery objective).

Across seven open-domain QA benchmarks, average exact-match answer accuracy is 0.221 for EVE-Agent versus 0.115 for Dr. Zero. The external GPT-4.1 evidence-support judge averages 0.313 versus 0.195. The strict joint answer-and-supporting-evidence score is 0.167 versus 0.044. On NaturalQuestions the joint score is 0.242 versus 0.021. The prior system emits an evidence block in >90% of rollouts, so the bottleneck is support quality, not evidence-field presence.

Primary: https://arxiv.org/abs/2605.22905
Public full text used for equations/tables: https://www.researchgate.net/publication/405221674_EVE-Agent_Evidence-Verifiable_Self-Evolving_Agents/download

### Scope / warrant distinction

EVE-Agent's evidence verifier is **warrant-like but not an independent truth oracle**. In the reported experiments the auxiliary scorer uses the same current solver weights, the target answer is proposer-provided, and the training-time verifier asks whether the evidence makes that answer easier to produce. The external GPT-4.1 evidence judge is used for evaluation, not as the training-time admission authority.

Therefore `evidence causes the current solver to emit a` is not logically identical to `e independently proves that a is true`. This is still valuable: it supplies inspectable provenance and a counterfactual usefulness test, but a full repair warrant should additionally test semantic/causal support against an exogenous predicate when one exists.

## SIG-CEGIS-EXACT-COUNTEREXAMPLE-WARRANT

Primary source: *Counterexample Guided Learning in the Large using Reasoning Agents*, arXiv:2606.11521, submitted 2026-06-09.

This work supplies the clean formal-oracle end of the spectrum. In regex induction the learner proposes a regex and the teacher checks equivalence to the target regular language. Because regular-language equivalence is decidable, the teacher can sample a witness from the symmetric difference. A returned counterexample is therefore a genuine proof that the current hypothesis is wrong on a concrete input, not a model-authored diagnosis.

On the hardest Simple Regex group, standard prompting succeeds on 3.2% of runs, clustered-counterexample single-shot learning on 23.8%, and the full agentic counterexample/reflection/repair workflow on 38.1%. On the hardest Extended Regex group the corresponding values are 38.9%, 68.5%, and 74.1%.

Primary: https://arxiv.org/abs/2606.11521

### Scope

This is symbolic concept learning rather than persistent open-world harness evolution. It shows that exact failure-existence/support predicates can dramatically improve refinement where a formal teacher exists. It does not show that such predicates are available for semantic agent failures, nor does it solve repeated promotion or persistent lifecycle governance.

## SIG-HARNESSFIX-PLAN-DIFF-AUDIT-IS-SCOPE-NOT-WARRANT

Public implementation audit: `HarnessFix/HarnessFix/failure_analysis/plan_diff_audit.py`.

The current code confirms the prior checkpoint's distinction mechanically. `audit_candidate`:
- computes changed files;
- rejects edits outside allowed paths or touching forbidden paths;
- enforces a maximum changed-file count;
- checks whether each planned fix touches at least one declared target file;
- compiles changed Python files for syntax validity.

It does **not** check that cited traces actually demonstrate the alleged failure mechanism, that a repair component is causally supported by those traces, or that a specific diff hunk is justified by a component-level evidence predicate. A planned fix is considered `covered` when at least one target file was touched.

Public code: https://github.com/HarnessFix/HarnessFix/blob/main/failure_analysis/plan_diff_audit.py

This makes the layers explicit:
1. **scope/syntax gate** — HarnessFix's diff audit;
2. **evidence provenance/usefulness gate** — EVE-Agent-style source span + counterfactual usefulness;
3. **exact failure witness** where available — CEGIS-style verifier counterexample;
4. **exogenous deploy acceptance** — SEAL-style hidden incumbent-vs-candidate audit;
5. **repeated-selection-safe statistical control** — still separate and still missing from the above systems;
6. **untouched outer lockbox** — final evaluation must not participate in proposal, promotion, rollback, retirement, best-version selection, or early stop.

## Updated synthesis

The current frontier is no longer simply `warrant gate vs performance gate`. Evidence now supports a more precise decomposition:

`component evidence provenance -> failure-existence/support predicate -> scoped immutable candidate -> incumbent/candidate behavioral comparison under exogenous evidence -> sequential/global selection control -> versioned persistence/rollback -> untouched outer evaluation`.

Three distinct failure classes are now separated:
- **unsupported repair**: a component has no real defect/evidence warrant even if outcome-neutral;
- **shared verifier error**: policy and endogenous evaluator co-adapt and agree on the same wrong world model;
- **adaptive audit overfit**: even a hidden fixed audit can leak information through repeated decisions unless repeated-selection is controlled.

## Exact continuation

1. Deep-search for a real self-improving agent that combines **component-level evidence warrant** with an **exogenous incumbent-vs-candidate promotion gate** in the same loop; prioritize systems where each edit component carries an evidence id / counterexample / formal obligation rather than only a global trace summary.
2. Search SEAL follow-ups / code / supplemental material for exact round count, hidden-audit sample reuse, false-accept / false-reject rates, and whether any fresh-audit or spending variant exists; determine how quickly one-bit leakage can adapt to a fixed audit under >20 proposals.
3. Search EVE-Agent ablations or follow-ups that replace the current-solver marginal evidence score with a frozen/exogenous verifier or entailment oracle, and measure whether the joint answer+evidence gains persist.
4. Search long-horizon (>10 proposal) systems that combine CEGIS/formal counterexamples or evidence-bound repair specs with anytime-valid/reusable-holdout admission and a truly untouched final test.
5. Maintain the target experiment matrix: performance acceptor (`greedy / fixed-alpha / anytime-valid / global-spending`) x warrant source (`none / endogenous evidence-utility / exogenous witness`) x task-order permutations, with immutable candidates, complete chronology, persistent lineage, component-level support ids, merge-as-candidate validation, and outer lockbox.

Frontier remains nonempty. No global completion is claimed.