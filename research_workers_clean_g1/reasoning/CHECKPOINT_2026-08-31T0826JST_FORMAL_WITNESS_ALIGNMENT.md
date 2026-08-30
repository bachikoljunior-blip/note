# Reasoning Phase-1 bounded slice — formal witness semantic alignment

control_commit_sha: `d0ce5484245d8e20f87d0d8efd6d9b36946501e6`
role: `reasoning`
lane: `isolated_clean_research`
enabled_desired: `true`
global_completion: `false`
phase1_completion_claimed: `false`
termination: `bounded_phase1_slice_complete_recurring_open`

## Slice choice

Executed exactly one bounded Phase-1 leaf on the explicit role axis **record-level failure detection / verifier calibration**. The slice tests whether stronger external/formal verification can be trusted without separately verifying that the formalized object is semantically faithful to the original reasoning step.

## Fresh public evidence

Primary source: Ziyu Wang, Qiming Dai, Yishan Wu, Zaiwen Wen, **“FaithSieve: Fine-Grained Evaluation of Math Proofs with Faithful Formal Evidence”**, arXiv:2608.26310, submitted 2026-08-26. Source URL: https://arxiv.org/abs/2608.26310

Evidence used is restricted to the public arXiv record/abstract observed in this run. The abstract reports:

- FaithSieve decomposes coarse natural-language proof steps into local reasoning units and extracts typed proof obligations.
- Formal Lean validation is not accepted directly; it is gated by a semantic-alignment score intended to preserve the original context, mathematical objects, and logical form.
- On an expert-verified 350-problem Olympiad first-error-localization dataset, a GPT-5.4-backed FaithSieve reports 81.43% exact first-error accuracy versus 72.29% for direct judging.
- On a 200-problem university benchmark spanning six advanced domains, it reports 84.5% exact accuracy versus 75.0% for the direct judge.
- The paper explicitly motivates the gate with two failure modes: a prover can bypass a local flaw by proving an overly broad target, or can validate an auto-formalized statement that has drifted from the original intent.

Evidence maturity: `fresh_primary_source_abstract_empirical_claims`; no claim is made here about independent replication or about transfer outside proof evaluation.

## Material revision

### FORMAL_WITNESS_SEMANTIC_ALIGNMENT_GATE

A stronger verifier or formal witness is not automatically higher-assurance evidence for an informal/local claim. Verification should be decomposed into at least:

1. `source_claim_id` — the exact local reasoning unit being checked;
2. `formalization_hash` — the machine-checkable obligation actually sent to the verifier;
3. `semantic_alignment_verdict` — whether objects, context, quantification, and logical form are preserved;
4. `formal_validity_verdict` — whether the formal obligation is proved/validated;
5. `locality_verdict` — whether the witness proves the intended local step rather than a broader or bypassing statement;
6. `first_error_index` — earliest local unit that fails under the aligned check;
7. `verifier_family` and `alignment_checker_family` — kept separate to avoid treating correlated components as independent witnesses.

Acceptance rule for an external/formal witness:

`usable_witness = semantic_alignment_pass AND locality_pass AND formal_validity_pass`

A `formal_validity_pass` with failed or unavailable semantic alignment must remain `UNRESOLVED`, not be promoted to a positive correctness label.

## Why this changes the current audit contract

The role already treats verifier calibration and record-level failure detection as Phase-1 evidence axes. This slice adds a necessary precondition for using high-assurance/formal evidence: **verify the translation before trusting the proof**. It prevents a controller from gaining apparent verifier accuracy by silently changing the object being verified, and it makes first-error localization evaluable at the same granularity as the intervention target.

## Required negative controls

- **Broad-target bypass:** replace one flawed local step with a formal obligation that is true but strictly broader/different; the formal prover may pass, while semantic/locality alignment must reject witness reuse.
- **Object drift:** alter a key object or quantifier during formalization while preserving a provable statement; the system must not convert the prover PASS into a source-step PASS.
- **Granularity mismatch:** ask a trajectory-level verifier to localize the first faulty record without local obligations; compare with local-unit verification so that improved global correctness is not mislabeled as localization capability.
- **Correlated witness control:** use the same model family for formalization and alignment checking, then compare with an independent alignment checker; do not count agreement as independent corroboration without family separation.

## Paired prediction

Holding source proof, backbone, and compute budget fixed, an aligned-local formal-witness pipeline should improve exact first-error localization relative to direct natural-language judging **only on records for which the formalization and locality gates pass**. On semantically drifted formalizations, the correct behavior is increased abstention/rejection rather than higher apparent pass rate.

## Non-conflicting state update

This checkpoint adds a verifier-evidence contract and does not claim router readiness, Phase-1 completion, or global completion. No scheduler or automation control file was mutated.

## Exact continuation

`NEXT_EXACT_CONTINUATION`: On the next invocation, re-bootstrap from the latest INSTRUCTION_CONTROL_MANIFEST.json, RUN_LIFECYCLE.json, DESIRED_STATE.json, and roles/reasoning.json; freeze their exact authority tuple; read this role-local checkpoint plus the current role-local frontier; then execute exactly one highest-value remaining Phase-1 leaf outside this completed formal-witness-alignment leaf. Prefer the least-covered required evidence axis, and do not reuse FaithSieve as new positive evidence except as an explicitly paired negative/control comparison. Preserve enabled_desired=true, global_completion=false, phase1_completion_claimed=false, and leave another nonempty exact continuation after durable readback.
