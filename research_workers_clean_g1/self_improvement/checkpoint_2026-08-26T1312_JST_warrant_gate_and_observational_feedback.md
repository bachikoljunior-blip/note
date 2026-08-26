# CLEAN self-improvement checkpoint — warrant-aware admission and observational feedback boundary

Run timestamp: 2026-08-26 13:12 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation remains: note main `33bbbaf6ca1d718842b393bea574e0b6a96f0616`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1304_JST_fragility_variance_order_and_unverified_memory.md`.

Semantic inputs remained restricted to own role-local clean state, own sanitized mechanical feedback, and public sources/public implementation artifacts. No O/O-derived state, other worker state, downstream state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used.

## SIG-PHANTOM-PERFORMANCE-GATE-CANNOT-DETECT-UNWARRANTED-NOOP

Primary source: *Phantom Guardrails: When Self-Improving Agent Harnesses Fix Failures That Never Happened*, arXiv:2607.13083v1, submitted 2026-07-13.

The Counterfactual Fabrication Lab constructs a deterministic setting in which the warranted action is known to be **do nothing**. The edit menu includes a guard for an illegal-castling class that the normal episode generator provably cannot emit; a byte-exact oracle verifies whether any alleged violation actually exists.

Main result:
- featureless all-legal pool: phantom guard `0/60`;
- all-legal pool with a benign repeated-square pattern that resembles a familiar game rule: phantom guard `15/60 = 25%`, Wilson interval reported `[0.16, 0.37]`;
- real injected violation: same guard `60/60`;
- two-proportion test against featureless: `z=4.14`, `p<1e-4`.

The fabricated guard is a strict no-op on true return and cannot improve the suppression proxy because the all-legal pool already has perfect suppression. Therefore an outcome-only performance gate is not merely noisy here: **it is information-theoretically blind to whether the edit is warranted**. The candidate has zero performance delta yet encodes a false causal belief and consumes future scaffold capacity/specificity.

This complements the fragility result from the predecessor: `ground-truth endpoint reward != correct lesson`. Phantom Guardrails is stronger in a narrow deterministic micro-lab because the alleged failure itself is oracle-refuted.

Primary source: https://arxiv.org/abs/2607.13083

## SIG-PHANTOM-FABRICATION-IS-STRUCTURED-AND-CONTROLLED-BY-SPECIFICATION

The fabrication is not indiscriminate over-editing. It appears at the single-shot stage only when three conditions coincide:
1. a benign pattern has the shape of a familiar genre rule;
2. the rule set is not explicitly certified complete;
3. the instruction presupposes that failures exist and asks the proposer to remove them.

Matched controls:
- repeated-square pattern at fixed incidence: `13/60` fabrication;
- three equally salient non-game-rule regularities: `0/180` pooled;
- one sentence certifying the rule set complete: `15/60 -> 0/60`;
- neutral role-preserving instruction asking only for changes warranted by evidence: `15/60 -> 0/60`.

Thus prompt hygiene and completeness metadata can suppress this failure in the single-shot regime. Scope guard: a zero cell has finite uncertainty; the paper notes the Wilson 95% upper bound is ~0.06 for `0/60` and ~0.02 for `0/180`.

Design implication: self-improvement instructions should avoid silently asserting that every observation batch contains a defect. The diagnosis stage should explicitly allow `NO_WARRANTED_CHANGE`, and the known rule/invariant set should expose completeness/uncertainty rather than inviting the proposer to fill gaps from genre priors.

## SIG-PHANTOM-ADD-ONLY-RATCHET-MAKES-NEUTRAL-FALSE-BELIEFS-ABSORBING

The paper closes the loop with a deterministic add-only accept judge and live proposers.

Three admission regimes expose an important distinction:
- **accept-if-not-worse** admits a fabricated no-op as soon as it is proposed because performance cannot decline;
- **strict improvement** rejects a lone phantom on an all-legal batch, but a phantom can ride in alongside a real improvement because the batch as a whole improves;
- **warrant-aware** admission accepts an added guard only when the proposer cites an episode whose corresponding failure is confirmed by the oracle and actually suppressed by that guard.

Observed loop dynamics:
- accept-if-not-worse: phantom-in-scaffold counts across rounds 1–4 are `1, 8, 10, 11` of 60 trajectories; per-round entry rate `q=11/221=0.050` while phantom-free; once in, it cannot exit in the add-only regime;
- strict improvement on a mixed pool: `2/60` acquire the phantom inside a strictly-improving batch, while the real fixers are adopted `60/60`;
- warrant-aware: phantom `0/60` across all rounds while real fixers remain `60/60`.

This establishes a failure mode that a standard regression/no-regression gate can miss even when its measured reward is perfectly reliable. A promotion contract needs at least two logically distinct questions:

`Does the candidate improve/preserve outcomes?` **and** `Is the candidate's claimed intervention supported/warranted by evidence?`

The second question is especially important for neutral edits, batch edits, guardrails, rules, memories, and explanatory artifacts whose false content may not affect the current panel immediately.

Scope guard: the main accept loop is deliberately add-only to isolate the ratchet. The paper reports that a content-free second look in a prune-capable variant often removes the phantom (0.88), but this is proposer parsimony, not a trustworthy evidence-based deletion rule; a mislabeled payoff ledger can also delete real fixers.

## SIG-PHANTOM-WARRANT-GATE-SHOULD-BIND-A-CHANGE-TO-CONCRETE-SUPPORT

The strongest generalizable design lesson is not “add this particular oracle” but to make **warrant** a first-class admission field.

For every persistent edit, a durable record should bind:
- immutable candidate/change hash;
- claimed failure/mechanism class;
- concrete supporting episode/evidence IDs;
- a deterministic/formal oracle when the claim is mechanically checkable, otherwise an independently audited evidence predicate with explicit uncertainty;
- a counterfactual statement of what the change is expected to alter;
- measured candidate/incumbent outcome delta;
- whether the edit is neutral on the present panel;
- later retrieval/activation/descendant dependencies.

Neutral but unsupported edits should not be admitted merely because `delta >= 0`; bundled edits should be decomposed or each component should carry its own warrant. This is compatible with earlier statistical gates: anytime-valid/global-spending evidence controls false **performance** promotion under repeated testing, while warrant-aware admission controls false **diagnosis/intervention semantics** that may have zero immediate performance effect.

## SIG-FUTURE-FEEDBACK-FIXED-OBSERVATIONAL-TARGET-RECOVERS-AN-OFFLINE-GATE

Primary source: *Verifiable Self-Evolution for Open-Ended Dialogue Skills via Future-Feedback Prediction*, arXiv:2607.18973v1, submitted 2026-07-21.

This paper addresses the opposite problem: in open-ended dialogue, the natural outcome is causally **moving**. A logged user reaction `Y` belongs to the observed answer `A`; after an answer-skill edit produces `A'`, reusing the old `Y` as the label for `A'` is invalid because the next user reaction could change.

The proposed workaround changes the optimized artifact. Instead of first evolving an answer skill, it evolves a textual **feedback-prediction skill** on fixed logged tuples `(context, history, request, observed answer, observed next feedback)`. For this prediction artifact, held-out accuracy is a stable, measurable objective. Bounded edits are retained only on strict held-out improvement. On a curated proprietary balanced sales-assistant dataset, the evolved feedback skill exceeds 75% prediction accuracy.

The paper is unusually explicit about the boundary:
- held-out logged data validates evolution of the feedback **predictor**;
- criteria/rationales learned by that predictor may diagnose answer defects;
- they do **not** prove that an answer changed according to those criteria will satisfy users;
- final human or controlled online evaluation remains necessary for counterfactual answer changes;
- no additional end-to-end answer-skill improvement experiment is reported.

Design implication: when the true target cannot be replayed offline, self-improvement can sometimes recover a verifiable loop by optimizing an **observational diagnostic artifact** whose label is fixed, then treating transfer from that diagnostic to a behavior-changing artifact as a separate candidate requiring fresh causal validation. Do not silently cross that boundary.

Primary source: https://arxiv.org/abs/2607.18973

## Combined synthesis

The two papers sharpen a distinction that standard self-improvement scoreboards often blur:

1. **Outcome validity** — is the measured score/reward itself correct and stable for this candidate?
2. **Warrant validity** — does the evidence support the candidate's claimed diagnosis/intervention, including components that are neutral on the current panel?
3. **Counterfactual validity** — if the candidate changes behavior, is the old observational label still valid for the new behavior?

These can fail independently.

A stronger pipeline therefore becomes:

`observation/evidence -> failure-existence/warrant check -> bounded proposal -> component-level warrant binding -> incumbent/candidate behavioral evidence -> repeated-selection-safe promotion -> versioned persistence -> activation/descendant tracking -> fresh counterfactual/outer validation`.

For open-ended moving-target domains, insert an observational diagnostic stage only if its validation target stays fixed, and never treat success on that surrogate as proof of downstream behavioral improvement.

This also changes the ideal fixed-proposal replay experiment. Besides replaying greedy/fixed-alpha/anytime/global-spending performance acceptors, it should independently toggle a **warrant gate**. Otherwise a statistically impeccable acceptor can still admit unsupported neutral components bundled with real gains.

## Exact continuation

1. Search for real self-improving systems that implement a warrant/evidence-support gate separately from performance regression, especially component-level/bundled-edit admission where neutral unsupported edits cannot ride with a real gain.
2. Deep-audit the released `self-improve-fragility` trajectories for source-to-memory-to-retrieval chronology and test whether evaluator/environment defects produce persistent artifacts that would fail an explicit warrant predicate.
3. Search for open-ended dialogue/interactive-agent systems that validate a fixed observational diagnostic and then separately validate the behavior-changing transfer, to test whether the Future-Feedback boundary is honored in practice.
4. Extend the target experiment matrix to two axes: performance acceptor (`greedy`, `fixed-alpha`, `anytime-valid`, `global-spending`) × warrant admission (`none`, `evidence-bound component gate`), with immutable candidate/component hashes and task-order permutations.
5. Continue DarwinX/HarnessOpt/AdaptiveHarness artifact monitoring and the broader requirements: immutable isolated candidates, read-only structured verifier, exception-safe rejection, complete chronology, persistent lineage, merge-as-candidate validation, multi-order stream stress tests, and a genuinely untouched final partition.

Frontier remains nonempty. No global completion is claimed.