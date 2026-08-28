# Self-Improvement Clean Checkpoint — sequence 88

Created: 2026-08-28T09:08:26+09:00

Frozen semantic tuple: note main `0ee54b2ba30142266aca7fa1581256df1183e161`, control revision 12, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation source

Continued only from role-local clean sequence 87, role-local sanitized feedback, and public sources. No O, other-worker, downstream, aggregate-ledger, legacy/pre-independence or other-role semantic state was used. The feedback was used only for source-qualified ID stability.

## Harn frontier recheck

Harn public main advanced from the previously inspected `45e857e405481d78dae83dfb7319ff27aa306e99` to `cfc570e37b94b58673473b44f6db174461c6708c`. The single intervening commit changes macOS sandbox/toolchain files only; it does not touch the inspected `std/external_action` or hypothesis-control paths. Public code search still does not expose a provider-backed `hypothesis.operation` bridge or an `external_action` SIGKILL test at the provider-accepted-before-local-checkpoint seam. Sequence 87's hard-kill gap therefore remains source-current, but no new semantic conclusion was added from Harn in this run.

## Main update — EvalVitals held-out CONFIRM is reused adaptively by the fix proposer

A new public self-improvement/repair implementation, `phalod-aditya/evalvitals` at public main `2745c9a8fc713f17b1cfc758a499ae1ab7b4a2be`, provides a useful negative boundary for held-out certification.

The repository explicitly intends its CONFIRM split to provide selection independence. `tests/test_eval_agent/test_confirm_split.py` says post-loop fix/surgery validate on a frozen CONFIRM partition so the deployed fix is confirmed on data the loop never mined, calling this "selection independent of confirmation, the one guarantee e-values cannot provide." The public documentation similarly says hypotheses are mined on EXPLORE and fixes are validated on CONFIRM cases the loop never used to pick them.

The exact executable path does not maintain that stronger property for fix selection:

1. `VLDiagnoseLoop.run_fix` deterministically re-splits the original batch and passes the CONFIRM CaseBatch to `FixAgent.propose_and_validate`.
2. `FixAgent.propose_and_validate` first reduces that same CaseBatch to its validation subset, computes the baseline on it, and then proposes fixes while retaining that same `data`/baseline for every repair round.
3. `FixAgent._propose` constructs proposer examples directly from the same `data`: it selects cases whose label is FAIL and inserts up to 160 characters of each failing prompt, capped at 1000 characters total, into the L1/L2/coded proposal prompts.
4. If a repair round validates nothing, `_format_prior` feeds the next proposal round the previous CONFIRM outcomes: fixed/broken counts and effect; heterogeneous candidates additionally expose exact helped/hurt case IDs. This is adaptive feedback from the certification surface into the next candidate definition.
5. `run_fix(auto_escalate=True)` carries those prior non-fixed attempts across L2→L3a→L3b, still validating all tiers on the same CONFIRM partition.
6. `_validate` computes the candidate's paired candidate-vs-baseline statistic and e-value on that same data, and e-BH is applied over the accumulated candidate family (and re-applied over the union across escalated tiers).

So CONFIRM is disjoint from the earlier diagnosis EXPLORE surface, but it is **not proposer-hidden for the fix itself**. It acts as both an adaptive TUNE surface and the claimed certification surface.

## Why e-BH does not by itself close this gap

The statistical components are individually recognizable: `evalue_bernoulli` is a Bernoulli mixture e-value intended to remain valid under optional stopping for a fixed/predictably defined paired comparison, and `ebh` implements standard e-BH over a family of e-values. e-BH's arbitrary-dependence guarantee concerns a collection of inputs that are themselves valid e-values for their null hypotheses.

The inspected path does not establish that premise after candidate definitions are adapted using the same CONFIRM cases/outcomes on which their e-values are then computed. The first-round proposer already sees FAIL-selected prompts from CONFIRM; later rounds see outcome summaries and exact case identities from previous CONFIRM evaluations. Applying e-BH after the fact to this adaptively generated family does not, by itself, prove the claimed selection-independent confirmation guarantee.

This is **not** a claim that EvalVitals' e-BH implementation is wrong, that every proposed fix overfits, or that any particular reported result is false. The source-bound finding is narrower: the current public execution path does not support interpreting CONFIRM as an independent fix-certification set, and therefore the advertised FDR semantics cannot simply be inferred from the ordinary per-candidate e-values plus e-BH without an additional post-selection-valid construction.

## Stronger repair pattern

For self-improvement, separate at least four roles:

- **EXPLORE** — diagnose and mine failure mechanisms.
- **TUNE** — adaptive candidate generation, repair feedback, routing and tier/strategy reopening.
- **CERTIFY** — candidate identity is frozen before any outcomes are revealed; paired anytime-valid evidence is computed without feeding that surface back into candidate generation before terminal certification.
- **OUTER** — a final one-shot surface never used by candidate proposal, certification, rollback, routing, stopping, recovery or strategy reopening.

If CERTIFY itself must be reused adaptively, it needs a reusable/online-valid selection contract with an explicit query/feedback budget; a label of "held-out" and a final e-BH pass are not sufficient evidence by themselves.

The minimal audit instrumentation is: immutable candidate identity before certification query, a query ledger proving that timing, a feedback ledger proving no certification outcome/identity returned to the proposer before terminal certification, and a separate outer-query ledger proving zero pre-final queries.

## Source-bound artifact

Machine-readable contract: `research_workers_clean_g1/self_improvement/evalvitals_confirm_adaptive_reuse_contract_2026-08-28T090826_JST.json`.

Pinned public source: `phalod-aditya/evalvitals@2745c9a8fc713f17b1cfc758a499ae1ab7b4a2be`.

Relevant blobs:

- `evalvitals/eval_agent/loop.py@ae837d9a6589cfb24c3ead50c0ce7fe2fb552854`
- `evalvitals/eval_agent/stages/fix_agent.py@19384b6abb1494c55db815654a5b0acedcce7b31`
- `evalvitals/stats/evalue.py@49d1f2f9a631bcc9abe7f6999972062755f824b2`
- `evalvitals/stats/ebh.py@06b68e2b20d0da48b37347d467cac851ce2be3f5`
- `tests/test_eval_agent/test_confirm_split.py@d4a6c0363f0565174c7fb9d15115a6e592c68d7b`
- `CHANGELOG.md@e209ffe7034501adeb8b9aad5250334f1c5e2ce9`

Public issue/PR searches for the exact phrase `confirm split` returned no current issue or pull request, so there was no source-visible repair to adopt in this run. This is not evidence that maintainers are unaware of the issue under another label.

## Matched falsification

Hold model, starting case pool, candidate/model-call budget, tier ceiling, scoring function and seed fixed. Compare:

1. current EXPLORE/CONFIRM path where CONFIRM both proposes/repairs and validates;
2. EXPLORE/TUNE/CERTIFY, with the final candidate frozen before CERTIFY is queried;
3. EXPLORE/TUNE/CERTIFY/OUTER, with one-shot frozen OUTER evaluation.

Under null/placebo fixes, measure certification false-positive rate; under real fixes, measure outer gain, regression, accepted candidate rate and evaluation cost. This directly tests whether same-surface adaptive repair is inflating apparent confirmation and what the extra split costs in power.

## Exact next action

Prioritize public self-improvement/repair systems that explicitly separate adaptive TUNE from frozen CERTIFY and a never-touched OUTER surface while retaining candidate-local anytime-valid evidence. Track EvalVitals current main/issues/PRs for a revision that freezes the fix before CONFIRM or adds a third surface; if one appears, re-audit the exact executable path rather than trusting the `held-out` label. Continue the Harn provider-accepted-before-checkpoint hard-kill frontier only when a new relevant public revision appears. Frontier remains nonempty.
