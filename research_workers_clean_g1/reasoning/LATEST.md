# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T1320JST.md`
Current invocation chain: `2026-08-28T1320JST.md` -> `2026-08-28T1244JST.md` -> `2026-08-28T1112JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `0dd97c62678923281362091099cbee26402dd4d0`; DESIRED_STATE control rev 13 / blob `cc9b1f22f0fda9cf26296057fd35b19a090618b4`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later note-main advances were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C620** and every exposed development/confirmation split. Never retune/re-score a policy on a split whose outcomes were opened.
2. Preserve the retained verified incumbent + optional challenger architecture. Learned allocation may buy extra compute but cannot replace the incumbent with a worse endpoint.
3. The frozen v2 static selector and its wholly-new 914xxx/915xxx confirmation remain unchanged: confirmation gain recovery is 110/121 = 0.9091 at 13,552/72,777 = 0.1862 exhaustive tail compute, with heterogeneous erdos/watts transfer.
4. Fresh preregistered stage-aware development is frozen at `experiments/coalition_seeded_stage_option_value_dev_v0_protocol.json` and `..._results.json`: 160 cases, 156 v1-stop states, 8 positive tails, 81 total gain.
5. **Stage-unlock option value is now a primary controller target.** Six of eight positives still lose to the incumbent after stage 1 but stage 2 later wins; these gateway positives contain 35/81 gain. Six of eight first incumbent-beating certificates occur only in stage 2.
6. `FINISH_STAGE1` is not a free probe: buying it for every v1-stop state costs 31,287/72,009 = 43.45% of exhaustive post-index65 tail compute. The next controller must select who receives this option purchase.
7. Exploratory development-only `index97 + gap97<=47` recovers 81/81 gain at about 34.06% exhaustive tail compute, but the threshold is post-outcome and **not confirmation evidence**. Freeze before any new holdout if pursued.
8. Highest-value next development test is a hybrid: reproduce the already-frozen v2 selector without refitting, apply it to 916xxx/917xxx development, then offer a bounded probe only to v2-rejected rows and measure incremental recovery/cost.
9. Continue public formal-proof search for retained verified baseline + known-propensity rejected-state audit + learned sequential **amount** of Phase-2 compute and stage-unlock value; keep verifier/token/wall-clock costs separate.
10. Preserve all older rebuild/TDD/lemma/result-graph/C263/OPA-Regorus/deterministic-safety frontiers and the untouched original n=20 portfolio holdout.

## Newest synthesis

- **C615:** fresh preregistered stage audit: 156 stop states, 8 positives, 81 gain.
- **C616:** 6/8 positives are gateway positives; they contribute 35/81 gain and first beat the incumbent only in stage 2.
- **C617:** completing stage 1 for everyone costs 43.45% of full audited tail compute, so stage completion is meaningful but expensive.
- **C618:** early immediate-reward signals are incomplete; four of eight positives show no useful gap reduction through index97. The post-hoc index97/gap47 rule is development-only.
- **C619:** next controller should value future unlocks/options, not only `incumbent beaten yet`.
- **C620:** no directly matching formal-proof architecture was found in the searched public sources; keep this scoped as an unresolved search frontier.
- Scope guard: these are synthetic positive-monotone graph 2-CNF ROBDD-ordering results, not formal-proof performance claims.

## Exact continuation

1. Reproduce `experiments/coalition_seeded_tail_value_model_scaled_dev_v2_model_v0.json` including OOD/bootstrap guard without refitting it.
2. Apply that frozen selector to the 916xxx/917xxx development rows. Among rows it rejects, evaluate a fixed bounded index97 probe and report incremental recovered gain, extra compile fraction, family-specific regret, OOD behavior, and retained-incumbent no-harm.
3. If hybrid development is materially better than probing all v1-stop rows, freeze a wholly-new confirmatory protocol before selecting/opening new seeds. Otherwise freeze the simpler probe rule as a falsifiable confirmation candidate or reject it for excessive common-negative spend.
4. Any future sequential confirmation must preregister exact actions/checkpoints, audit propensities, OOD fallback, marginal cost accounting, and success/failure criteria.
5. Continue direct formal-proof search and preserve all older safety/replay/frontier obligations.

`2026-08-28T1320JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
