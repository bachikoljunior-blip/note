# Self-Improvement Clean Checkpoint — sequence 92

Created: 2026-08-28T11:10:02.674613+09:00

Frozen semantic tuple: note main `db40813f753acc29a570374d3cde527725bed313`, control revision 13, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued from role-local clean sequence 91 plus public sources only. No O/O-derived state, other-worker state, downstream state, aggregate ledger, legacy research, or other-role semantic context was used.

Sequence 91 established that phase names such as `held_out`, `sealed_test`, or `proposal_selection` do not prove evaluation-surface separation. The next target was executable evidence of a **real untouched OUTER surface** plus a stronger promotion/certification contract.

## Primary update — Auditable Auto Research has a real code-separated outer holdout, but the executable does not make it terminal or exactly-once

Source: `cxcscmu/Auto-Research-AI-Scientist`, public main revision `7a6dbc8543172042d7be4f14b39f8f4c0abd6c92`.

This repository is the strongest executable OUTER separation found in the current branch so far.

### What it gets right

The public protocol is explicit:

1. expose one research axis;
2. score all candidates only with inner cross-validation;
3. keep an append-only ledger and non-overwritten hashed trial workspaces;
4. freeze the selected source tree;
5. reveal the outer holdout only through a separate `certify` command.

The executable matches much of that contract:

- `CampaignRunner.run()` uses only `evaluator.development(workspace)`.
- The manifest records `holdout_policy = "never evaluated by run(); explicit certify command only"`.
- Each trial is staged from the current frozen best tree and stores `source_sha256`, parent lineage, agent prompt/logs, status and score.
- `certify()` rehashes the current best workspace and refuses certification if the source changed after freezing.
- Holdout output is tied to `trial_id` and `source_sha256`.
- A public end-to-end test runs one trial, resumes to a second trial, explicitly verifies no `holdout_certification.json` exists during search, then invokes certification.
- The method document states that outer fold 0 is sealed, candidates are selected only by inner K-fold CV, the exact selected source/hash is frozen, and one explicit certification scores the holdout.
- The repository also ships a paper artifact with retained trial records, frozen winners, certification results, and file-hash verification scripts.

This is genuine executable evidence that **search can be kept off the outer holdout by call-path construction**, rather than only by naming a dataset “test”.

### Critical boundary — `certify` is not one-shot at execution level

The implementation has an important ordering bug relative to the stronger lockbox contract.

`certify()` does:

1. resolve and hash the frozen best;
2. **call `self.evaluator.holdout(workspace)`**;
3. construct the payload;
4. only then check whether `holdout_certification.json` already exists.

Therefore a second `certify()` call re-runs the outer evaluator before discovering the existing certificate.

The public test itself calls `certify()` twice. It verifies the returned certificate remains source-identical, but this means the test actually exercises **repeated outer evaluation**, not one-shot outer consumption.

The method document says “one explicit certification”; the public executable does not enforce that statement at the evaluator-call boundary.

### More serious boundary — certification does not close the campaign

`run()` never checks for an existing holdout certificate or a terminal campaign state.

So the source code does not prevent:

`search -> certify/reveal outer result -> search again`

The agent does not automatically receive the certificate through the ordinary blackboard prompt, so this is not evidence that the released paper campaign actually adapted to the holdout. The narrower finding is structural: **the executable state machine does not make OUTER revelation terminal**.

A strong lockbox must forbid the possibility, not rely on the operator following prose.

### Crash boundary — outer consumption is not write-ahead/durable

`certify()` executes the holdout subprocess before writing `holdout_certification.json`, and the file is written with a direct `write_text`.

Thus a process failure after the outer evaluator returns but before the certificate is durably recorded can produce:

- outer evidence was consumed;
- local state says no certificate exists;
- retry calls the outer evaluator again.

This is exactly the Evaluation Consumption Contract problem found earlier for provider-backed agent evaluation, now appearing at the **final outer lockbox**.

## New design requirement — terminality is part of holdout validity

The four-surface model should be strengthened from a naming/split contract into a monotone state-machine contract:

`SEARCH_OPEN -> FROZEN -> CERTIFYING -> CERTIFIED/CLOSED`

For OUTER:

- `outer_preterminal_query_count == 0`;
- the exact selected artifact and evaluator protocol are frozen before any outer dispatch;
- a stable logical outer-query ID and query budget are durably prepared before dispatch;
- a crash/retry reconciles the same logical query instead of creating another one;
- repeated `certify` is a pure read of the stored certificate or fails closed;
- after the first outer result becomes observable, no search, tuning, promotion, rollback selection, routing, stopping optimization, or checkpoint selection may resume using that outcome.

This adds a missing dimension to sequence 91:

**surface isolation = data separation + consumption accounting + terminal state transition.**

## Relationship to the remaining LOGOS frontier

Auditable Auto Research solves a part that LOGOS was paper-only on: there is public executable code where ordinary search does not call the outer holdout, and public tests exercise the split.

But it does **not** provide the full target composition:

- adaptive selection is inner-CV mean based;
- there is no separate candidate-local anytime-valid CERTIFY surface before OUTER;
- there is no durable cross-candidate FDR/FWER/error-spending ledger;
- OUTER is command-separated but not one-shot/terminal/exactly-once.

Source-bound classification:

**`EXECUTABLE_INNER_SELECTION_PLUS_SEPARATE_OUTER_CERTIFICATION_WITH_TERMINALITY_AND_EXACTLY_ONCE_GAPS`**

## Source-bound artifact

`research_workers_clean_g1/self_improvement/outer_terminality_contract_2026-08-28T111002_JST_autoresearch.json`

## Exact next action

Search for a public self-improvement system that enforces **monotone terminal outer-lockbox semantics** in code and tests:

1. no outer query before artifact freeze;
2. write-ahead durable logical outer-query identity before evaluator dispatch;
3. repeated certification is read-only/rejected rather than a new evaluator call;
4. search/tuning cannot resume after outer revelation;
5. crash between dispatch and result persistence cannot create a second logical outer query.

Then combine that requirement with the still-missing LOGOS-like candidate-local anytime-valid CERTIFY and restart-durable cross-candidate spending. Frontier remains nonempty.
