# self_improvement clean checkpoint — Recuris settlement/feedback-channel audit and StarHarness release gap

checkpointed_at: 2026-08-27T04:06:08+09:00
clean_generation: clean_g1
worker: self_improvement
frozen_note_main_sha: 064ab82e0a0e054d4ca9b1edd0ae58441bea64cb
frozen_control_revision: 10
frozen_config_revision: 6
frozen_role_config_blob: 9298edd872e0ab5e2d9e67aceb9f6cffbf02516f
predecessor: research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0326_JST_recuris_progressive_search_gate_boundary.md

## Source identity

- Recuris public repository: `Gen-Verse/Recuris`, inspected commit `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`.
- Recuris inspected paths: `src/recuris/cli.py`, `src/recuris/metaagent/driver.py`, `src/recuris/metaagent/gates.py`, `src/recuris/metaagent/settle.py`, `configs/metaagent/retail_progressive.yaml`, `configs/metaagent/airline_progressive.yaml`, repository tree and operations documentation.
- StarHarness primary paper: arXiv:2608.24804, submitted 2026-08-25.
- StarHarness public repository: `ServiceNow/StarHarness`, inspected current main `d70f53e60ef1fa048adab5632edc8aadadfcf64a`.

## New observations

1. **The public Recuris `metaagent run` and `metaagent settle` are separate CLI capabilities, and the current driver does not itself invoke settlement.** `src/recuris/cli.py` dispatches `run` to `driver.main` and `settle` to `settle.main` as separate subcommands. Inspection of the current `driver.py` found settlement language/comments but no call that launches `settle.main` or the `recuris metaagent settle` command. The current repository tree likewise exposes `settle.py` but no wrapper script that automatically chains a normal multi-round run to settlement. Therefore, at this public revision, terminal frozen-set settlement is an **external/manual orchestration obligation relative to plain `metaagent run`**, not an automatic step inside that command. This does not establish what was done in private/paper-run orchestration.

2. **The shipped campaign configs resolve the round-gate mode and proposal-round counts for the public retail/airline evolution campaigns.** `retail_progressive.yaml` explicitly describes the retail evolution campaign as progressive gating and sets `rounds: 4`, `k: 4`, `round_gate: progressive`. `airline_progressive.yaml` sets `rounds: 5`, `k: 6`, `round_gate: progressive`. The retail config also states that a frozen-split settlement at the end decides what is kept. Thus the public campaign contract is not a strict-only lineage; it intentionally permits progressive search and expects a later settlement certificate.

3. **The repeated dev/selection feedback channel is materially higher-bandwidth than a one-bit ACCEPT/REJECT signal.** The driver removes only these private fields before persisting `led_verdict`: `base_dev_matrix`, `cand_dev_matrix`, `base_dev_fp`, `cand_dev_fp`, `base_dev_fp_by_task`, `cand_dev_fp_by_task`. The remaining verdict includes at least `accept`, `net_pp`, bootstrap CI endpoints, `up`, `dn`, repair base/candidate scores, `repair_ok`, repair-change details, `gate_stats`, and `held_out_damage`. `gate_stats` includes dev paired flips, `p_dev_pos`, `p_harm`, and when available repair flips and `p_rep`; dense-reward runs additionally expose the estimator/materiality metadata. The ledger record also carries the plan bundle digest, plan summaries including evidence task ids/components/fix actions, and ceilings.

4. **Those ledger records are fed back verbatim to future proposal generation.** `state_md()` reads the machine ledger and injects its last 12 JSON lines as `Ledger tail (recent attempts, machine-recorded)`. Therefore a proposal generator can condition on continuous-valued scores, interval endpoints, p-values, flip/regression counts, repair outcomes, and plan metadata from repeated reuse of the same dev/selection instrument. Raw example matrices remain hidden, but the release channel is not low-bandwidth. A useful audit distinction is now: sample secrecy, outcome-summary bandwidth, provisional-parent selection, and final fresh certification.

5. **`settle.py` is genuinely evaluation-only/fail-closed, but the public generic path inspected still does not establish a terminal certificate for an arbitrary multi-round progressive run.** Its module contract freezes candidate bytes and preregistered shards without edit/meta-agent tools. However one exact-generation binding explicitly requires `expected_generation.round == 1`. Combined with the absence of an automatic `run -> settle` call, this leaves unresolved exactly how the public 4/5-round progressive campaign endpoint is bound to fresh settlement evidence. Do not infer that the reported paper runs omitted settlement; the public orchestration link is simply not yet demonstrated.

6. **StarHarness independently demonstrates the complementary outer-test boundary.** Its primary paper separates proposer-visible search, proposer-hidden selection, and a remaining holdout that never affects proposal or acceptance; the final harness is evaluated once on holdout after search. The paper reports exactly 21 accepted patches across three runs: 4 ITBench, 12 EnterpriseOps-Gym, 5 AutomationBench. However the numeric total proposal/selection-query budget is not stated in the paper body/algorithm beyond an abstract budget `B`.

7. **The current public StarHarness repository cannot yet close that proposal-budget gap.** Current main contains only a 28-byte `README.md` with commit message `Coming soon`; the repository exposes only the main branch, and the release list is empty. Consequently there is currently no public code/results/proposal chronology from which to recover how many hidden-selection queries produced those 21 accepted patches. Do not infer proposal count from accepted count.

## Interpretation / design consequence

A self-improvement system can have strong candidate identity, a mathematically explicit promotion gate, and a truly fresh terminal settlement while still adapting aggressively to a repeatedly reused internal selection set through released summary statistics. Promotion safety, search-feedback safety, and final certification are separate controls.

A stronger long-run contract is:

`immutable candidate -> bounded selection-feedback release -> candidate-local promotion evidence -> explicit provisional/search lineage -> durable versioning -> fresh terminal settlement -> untouched outer test`.

For a fixed reusable selection set, hiding task text and matrices is insufficient if exact continuous scores, CIs, p-values, regression counts, repair outcomes or task-level plan metadata are repeatedly released to the proposer. The release channel itself should have a documented information/query budget or a reusable-holdout/anytime-valid contract appropriate to the adaptive search.

## Scope guards

- This checkpoint does **not** claim Recuris's reported benchmark gains are invalid.
- It does **not** claim Recuris paper runs lacked frozen-set settlement; only that current public `metaagent run` does not automatically invoke `settle`, and the public multi-round-to-settlement binding remains unverified.
- It does **not** claim raw Recuris dev matrices/fingerprints are exposed to the proposer; they are explicitly removed from `led_verdict`.
- It does **not** claim progressive provisional adoption is harmful. The finding is that it makes dev feedback part of search, so that dev is not an untouched holdout for the search trajectory.
- StarHarness's once-only holdout claim is limited to the primary paper protocol. Total candidate/query count remains unknown because the current public repository is placeholder-only.
- All implementation observations are limited to the exact public commits named above.

## Exact continuation frontier

1. Search Recuris paper/supplementary artifacts, champion provenance, tags/commits and any evaluation records for an executed settlement certificate that binds the final 4-round retail or 5-round airline progressive endpoint to fresh disjoint tasks; distinguish standard campaign settlement from the `expected_generation.round == 1` special protocol.
2. Build a source-bound `selection_feedback_contract` for Recuris that enumerates every `led_verdict`/ledger field released to `state.md`, whether task identities are exposed, numeric precision/range, retention depth (12 records), and which fields can steer provisional-parent choice versus only diagnosis.
3. Quantify the selection feedback channel under repeated reuse: compare one-bit verdict, rounded score, CI/p-value release, and current full ledger-tail release in a controlled adaptive-selection simulation; measure selection overfit at equal proposal budget.
4. Re-check `ServiceNow/StarHarness` when code/results are released; recover total candidate proposals, hidden-selection queries, rejection chronology and selection-set reuse behind the 21 accepted patches. Current public history is a single `Coming soon` commit with no releases.
5. Continue searching for a >10-proposal live LLM-agent experiment that combines candidate-local anytime-valid evidence, durable cross-candidate statistical spending, a bounded selection-feedback channel, complete public proposal chronology, and a genuinely untouched outer test.

frontier_nonempty: true
