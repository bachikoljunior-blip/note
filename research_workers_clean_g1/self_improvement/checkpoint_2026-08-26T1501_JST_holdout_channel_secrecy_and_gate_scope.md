# CLEAN self-improvement checkpoint — holdout channel secrecy and gate scope

Run timestamp: 2026-08-26 15:01 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `b448726ce9420fd51974e70df965c4e6e3fb68e4`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Note main advanced after the first semantic read; later head movement is mutation transport only and is not adopted semantically in this invocation.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1402_JST_exogenous_acceptance_and_evidence_warrants.md`.

Semantic inputs remained restricted to own role-local clean state and public sources/public implementation artifacts. No O/O-derived state, other worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate execution ledger, or other-role config/receipt was used.

## SIG-AGENTA-SEALED-SAMPLES-BUT-OPEN-FEEDBACK-CHANNEL

Public implementation audited: `ethan-haas/self-improving-agent-harness` (AgentA), current public `main` as observed in this run.

The README describes a 7-tier promotion chain — parse, unit, property, mutation, benchmark, sealed holdout, fresh-context critic — and says the holdout is isolated from the agent. Static implementation confirms a real sample/code isolation boundary but exposes a separate adaptive feedback channel:

- `host/Install-AgentA.ps1` gives the agent identity DENY-all on `holdout/`, but the other protected directories including `archive/` and `host/` receive DENY-write rather than DENY-read. The README likewise frames these as read-only protections.
- `host/lib/Invoke-HoldoutScoring.ps1` runs baseline and candidate in separate worktrees against hidden `holdout/score.py` and returns exact `Delta`, `Baseline`, and `Candidate` values.
- `host/runner.ps1` rejects a candidate with a reason containing the exact numeric holdout delta when `Delta < +0.02`, and logs a promoted candidate with the exact holdout delta.
- `host/lib/Approve-StagedDiff.ps1` writes the exact `holdout_delta` into `archive/.../scores.json` and also puts `holdout+$HoldoutDelta` into the Git commit/tag message. Rejected candidates are moved into `archive/rejected` with the rejection reason.

Therefore, in the current public design, **secrecy of the holdout examples is not secrecy of the holdout feedback channel**. The agent cannot read `holdout/score.py`, but the repository intentionally preserves exact numeric holdout feedback in surfaces that are not read-blocked by the installer. This creates a high-bandwidth adaptive channel across repeated proposals. The finding is static-code/ACL evidence; no deployed private run or actual adaptive exploit was observed here.

Public repository: https://github.com/ethan-haas/self-improving-agent-harness
Relevant paths:
- `host/runner.ps1`
- `host/lib/Invoke-HoldoutScoring.ps1`
- `host/lib/Approve-StagedDiff.ps1`
- `host/Install-AgentA.ps1`

### Additional scope boundary: self-modifying scaffold edits bypass the sealed outcome holdout

`host/runner.ps1` explicitly skips tier 5 benchmark and tier 6 holdout for candidate category `scaffold-edit` and for `external-repo`; it substitutes zero deltas and proceeds to later critic/reward-hack checks, plus a gate self-test for scaffold edits. Thus the exact class that modifies the harness/scaffold does **not** receive the README's sealed holdout outcome gate in this current code path.

This does not imply scaffold edits are unverified — they still pass review, hash/integrity checks, properties, mutation tests, critic, tripwire, and gate self-test — but it means AgentA is not evidence for the stronger frontier condition `self-modifying scaffold + exogenous hidden behavioral promotion gate` as currently implemented.

## SIG-HOLDOUT-SECRECY-DECOMPOSES-INTO-FOUR-SEPARATE-PROPERTIES

The AgentA audit sharpens the current SEAL/reusable-holdout frontier. A useful holdout contract should distinguish:

1. **sample secrecy** — proposer cannot inspect or edit evaluation examples/scorer;
2. **feedback secrecy/budgeting** — proposer cannot receive unrestricted score/delta information across adaptive submissions;
3. **role applicability** — the gate actually applies to the self-modifying candidate class, not only ordinary task-code changes;
4. **outer lockbox isolation** — final evaluation does not participate in promotion, rollback, retirement, best-version selection, or early stopping.

A system can satisfy (1) while failing (2) or (3). Calling a dataset `sealed` or `hidden` is therefore insufficient evidence for repeated-selection validity.

This matches the classic reusable-holdout result: repeatedly exposing a fixed holdout score to an adaptive analyst makes later candidates statistically dependent on the holdout, so ordinary holdout guarantees no longer apply. Thresholdout/reusable-holdout mechanisms were designed specifically to control this adaptive information channel rather than merely hide raw examples.

Primary background: Cynthia Dwork, Vitaly Feldman, Moritz Hardt, Toniann Pitassi, Omer Reingold, Aaron Roth, *The reusable holdout: Preserving validity in adaptive data analysis*, Science 2015. Public summary: https://research.google/blog/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis/

## SIG-ANTAHKARANA-FALSIFIABLE-GATES-STRUCTURAL-WARRANT

Primary source: Deepak Soni, *Falsifiable Release Gates for Self-Improving Systems*, arXiv:2607.13070, submitted 2026-07-11.

This work is strong evidence for a different layer: **pre-declared machine-checkable invariants and a non-self-selected target**. Each capability is required to pass a gate declared before the feature, with earlier invariants preserved. The G12 self-governing policy loop constrains autonomous writes to policy-rule changes; tightening can auto-apply while loosening requires human approval, and proposals that mispredict their measured effect auto-close. The central non-bypass property is exhaustively checked over the bounded coordination model and rechecked over one million recorded traces.

This is valuable as a formal/structural warrant and write-surface containment mechanism, but the paper explicitly scopes the proof to the bounded coordination skeleton rather than learned scoring components. It is not, by itself, a repeated-selection-safe behavioral performance acceptor for learned self-improvement.

Primary: https://arxiv.org/abs/2607.13070

## SIG-ANTAHKARANA-V11-NEAR-FRONTIER-PUBLIC-CLAIM

The current public Hugging Face model card for `deepakdsoni/antahkarana-base` describes a later v11 `SelfImproveGate` that is closer to the current frontier than the July paper alone:

- strict verified gain is required for adoption;
- the gate is declared non-self-modifiable;
- every adoption is lineage-tracked and reversible;
- `INV-41` rejects stale-only evaluation (`fresh_eval=True` in the public API example);
- `INV-42` says decisions use external, cited, outcome-verified evidence rather than self-reported confidence;
- the card reports a self-proposed strategy raising held-out accuracy from 20% to 70% being adopted while a confidence-gaming candidate and a regression are rejected.

Current public model card: https://huggingface.co/deepakdsoni/antahkarana-base

Important evidence boundary: the repository's model files/source content require accepting a contact-information agreement, so this run did not independently inspect the v11 implementation or release scripts. The July paper predates these v11 claims and explicitly limits its machine-checked proof to structural/bounded components. Therefore v11 is a **promising project-level claim**, not yet independent implementation evidence for fresh-eval semantics, false-accept behavior under many adaptive proposals, anytime-valid control, or an untouched final lockbox.

## Updated synthesis

The frontier now separates two frequently conflated properties:

`evaluation data hidden from proposer` != `evaluation channel safe for adaptive reuse`.

The stronger long-loop contract is now:

`component evidence/warrant -> immutable scoped candidate -> exogenous incumbent/candidate test -> bounded/repeated-selection-safe feedback channel -> versioned promotion/rollback -> gate applies to self-modifying class -> untouched outer lockbox`.

A practical audit should inspect **where the score/verdict goes after evaluation**, not just whether the proposer can open the holdout files. Commit messages, archived score JSON, rejection reasons, dashboards, and logs are all part of the effective information channel.

## Exact continuation

1. Deep-search for a public real self-improving agent whose **self-modifying** candidate class actually passes an exogenous incumbent-vs-candidate behavioral gate while the proposer receives only a bounded/reusable-holdout-safe channel; inspect implementation, not architecture prose.
2. Follow Antahkarana v11 public artifacts/package metadata for inspectable `SelfImproveGate`/`INV-41` implementation or release outputs; determine what makes an eval `fresh`, whether evaluation samples are rotated/one-shot/budgeted, what feedback reaches the proposer, and whether a separate untouched final test exists. Do not treat the model-card claims as independently verified until code/results are accessible.
3. Search systems that publish complete proposal chronology so the identical candidate sequence can be replayed under `greedy / fixed-alpha / anytime-valid / global-spending` acceptors, crossed with `none / endogenous / exogenous` warrant sources.
4. Maintain the audit checklist `sample secrecy / feedback-channel secrecy / self-modifying-role coverage / outer lockbox`, and add explicit searches for score leakage through commit messages, archive metadata, rejection reasons, logs, and dashboards.
5. Continue the >10-proposal target search for the full combination: evidence-bound repair, immutable candidates, exogenous gate, repeated-selection-safe admission, persistent lineage/rollback, and untouched final evaluation.

Frontier remains nonempty. No global completion is claimed.