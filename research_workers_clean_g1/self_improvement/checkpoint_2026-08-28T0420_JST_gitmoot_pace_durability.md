# Self-improvement clean checkpoint — sequence 83

Created: 2026-08-28T04:20:00+09:00
Generation: clean_g1
Worker: self_improvement
Frozen control tuple remains note main `ab7d475334153c77932b30e91f2324a0abd17ac1`, control revision 12, role config revision 6.
Predecessor: sequence 82 `checkpoint_2026-08-28T0414_JST_openonce_provider_effect_component.md`.

## A real self-improvement path with an implemented anytime-valid promotion gate

Source-bound system: `gitmoot/gitmoot@ab854269230e814131f00fe0b1ccbc21b46bfd67`.
PACE implementation was merged by PR #690 on 2026-07-06 and remains on current inspected main.

This is the strongest direct implementation result in this branch so far: GitMoot's SkillOpt candidate promotion path has an actual PACE-style candidate-local anytime-valid gate, not just a paper/RFC. The pure `PaceAccumulator` applies the betting update to paired candidate-vs-champion discordant outcomes; it commits at `E >= 1/alpha`, discards ties, and rejects when the pair budget is exhausted without crossing. The promotion seam runs existing guardrails first and then requires PACE commit when enabled; `continue` and `reject` both fail safe and stop promotion. The RFC/PR are explicit that the guarantee is **per candidate**, not run-level familywise.

The current production seam does not persist an in-memory e-process. Instead it reconstructs candidate wins/losses from the persisted challenger bandit arm (`Alpha-1`, `Beta-1`) and computes an order-invariant terminal-wealth gate. That has a useful restart property: process restart does not erase the terminal sufficient statistic. It is intentionally more conservative than pretending an unknown historical ordering crossed earlier.

## Newly exposed crash/atomicity gap

The persistent sufficient statistic is not yet one atomic logical comparison stream.

Manual `skillopt ab` does the following in source order:

1. run champion response;
2. run challenger response;
3. mint a fresh per-invocation `comparisonToken`;
4. persist one ranked human feedback event using that token;
5. increment the champion bandit arm in its own SQL transaction;
6. increment the challenger bandit arm in a second SQL transaction.

The live A/B interceptor uses the same record-then-two-increments path. `IncrementBanditArm` itself explicitly documents that the two arms of one A/B are updated with two calls. No comparison/event ID is passed to that function, so the inspected bandit mutation is not visibly idempotent per logical comparison.

This creates concrete failure boundaries:

- crash after feedback persistence but before bandit updates: durable evidence row exists while PACE's candidate sufficient statistic omits it;
- crash between champion and challenger increments: paired posterior state is asymmetric;
- crash after challenger increment but before command completion: a retry/new invocation can mint a new comparison token and add another candidate outcome; nothing inspected binds the prior physical comparison to an exactly-once bandit application.

For PACE specifically, a champion-only orphan does not directly change challenger-derived win/loss counts, but it does corrupt auxiliary champion confidence. A crash after challenger increment is more serious for PACE: a retry can double-count candidate evidence unless a higher-level idempotent comparison transaction exists. None was observed in the inspected path.

There is an even earlier logical-ID issue: the champion/challenger model deliveries happen before the durable comparison token is minted, so a crash during/after those remote evaluations cannot be reconciled under a stable logical comparison identity in this path.

## What this establishes and what it does not

Established in current public code:
- real persistent self-improvement promotion path;
- candidate-local anytime-valid PACE decision logic;
- fail-safe no-promotion on insufficient PACE evidence;
- persisted aggregate candidate win/loss sufficient statistics;
- restart-recomputable terminal PACE decision.

Not established:
- exactly-once logical pair consumption;
- atomic winner+loser sufficient-statistic updates;
- provider-side exactly-once candidate/champion evaluation;
- cross-candidate/familywise statistical spending;
- a fully untouched outer evaluation for the whole adaptive SkillOpt lineage.

This is therefore a strong positive mechanism plus a concrete systems gap, not a complete long-horizon safety solution.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/pace_promotion_durability_contract_2026-08-28T0420_JST_gitmoot.json`.

## Direct repair/falsification target

A minimally stronger evidence layer would mint a stable `logical_comparison_id` before either arm is evaluated, bind candidate/champion/prompt/evaluator identities and query/statistical budget to it, store one immutable outcome row keyed by that ID, and in **one transaction** mark that comparison applied while updating both bandit arms. Replaying the same ID would become a no-op; reusing the ID with changed semantic inputs would fail.

Then SIGKILL at: after outcome persist, between logical-apply and arm mutations, after arm mutations before command return, and before/after promotion. Uninterrupted and kill-resume runs must produce identical comparison count, both arm posteriors, PACE verdict, feedback release and candidate state.

## Exact continuation / nonempty frontier

Search first for an existing public implementation that atomically binds an immutable comparison/event ID to paired sufficient-statistic updates and persistent sequential-test state. Also inspect whether GitMoot has a newer alternate seam doing this transactionally. If absent, this exact SkillOpt path is now a concrete minimal prototype target. In parallel continue the broader search for durable cross-candidate statistical spending, provider/logical-query exactly-once evaluation, bounded selection-feedback bandwidth, complete proposal chronology, immutable promotion identity, restart durability, >10 proposals, and an outer test unused by adaptive selection/rollback/routing/stopping.

Frontier remains nonempty; no global completion is claimed.
