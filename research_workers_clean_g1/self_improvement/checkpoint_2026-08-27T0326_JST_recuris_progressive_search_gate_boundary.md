# self_improvement clean checkpoint — Recuris progressive search/gate boundary

checkpointed_at: 2026-08-27T03:26:02+09:00
clean_generation: clean_g1
worker: self_improvement
frozen_note_main_sha: c847473fd8cd8064f37db8c21f7bb05f65d2d5d5
frozen_control_revision: 10
frozen_config_revision: 6
frozen_role_config_blob: 9298edd872e0ab5e2d9e67aceb9f6cffbf02516f
predecessor: research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0206_JST_recuris_atomicity_and_starharness_outer_gate.md

## Source identity

- Public repository: Gen-Verse/Recuris
- Inspected public main commit: f54c9dabfa370c0da495ddabe8ccbe8702b3eae7
- Primary implementation: `src/recuris/metaagent/driver.py` at that commit.
- Settlement implementation inspected separately: `src/recuris/metaagent/settle.py` at the same commit.
- Current README at that commit uses `--round-gate progressive` with `--rounds 4` in the documented Meta-Agent quickstart.

## New observations

1. **Committed-lineage certification and search-lineage evolution are distinct in progressive mode.** The current driver documents `_working_base_package()` so a provisional package can be the next candidate's parent while `state["best"]` remains the committed best. On strict acceptance, the cumulative package is certified against that committed best and any provisional lineage is settled.

2. **A strict gate rejection does not necessarily remove the candidate from future search in `--round-gate progressive`.** `_handle_provisional_after_reject()` checks `progressive = self.a.round_gate == "progressive"`. In progressive mode, a rejected candidate is eligible to become/supersede the provisional working base when `(dev_net_cells > 0 or repair_net_cells > 0)` and `p_harm >= 0.05`; the stricter in-round improvement-significance gate that protects committed `best` is therefore not identical to the rule that determines the next search parent. The code comment explicitly says the committed lineage stays untouched and assigns cumulative-package certification to a later frozen-set settlement.

3. **The same hidden/dev selection outcomes can influence later proposal generation through aggregate feedback even though raw dev matrices/fingerprints are withheld.** Before ledger persistence the driver removes `base_dev_matrix`, `cand_dev_matrix`, and dev fingerprints, but retains the rest of the verdict as `led_verdict`. `state_md()` injects the last 12 ledger lines under `Ledger tail (recent attempts, machine-recorded)`, and `state.md` is a required diagnosis/proposal input in the normal workflows. Thus later meta-agent proposals can condition on aggregate gate outcomes from prior rounds. This is not raw held-out-example leakage, but it is an adaptive feedback channel from the repeatedly reused selection set into the search trajectory.

4. **Therefore a strong commit gate does not by itself imply a selection set remains an untouched holdout.** In progressive mode, dev feedback has two effects: it determines whether a candidate may become a provisional search parent and its aggregate verdict enters later proposal context. The appropriate audit objects are separate: (a) committed best lineage, (b) provisional/search lineage, (c) information released from repeated selection queries, and (d) final fresh certification.

5. **The generic public settlement path is not yet established as the automatic terminal certificate for arbitrary multi-round progressive quickstarts.** `settle.py` is a fresh fail-closed evaluation-only A/B mechanism for frozen candidates and is promising as an outer certificate, but the inspected protocol contains an `expected_generation.round must be 1` binding in one exact-generation path. The current README quickstart search did not expose a `settle` invocation. This does not show that paper runs lack fresh settlement; it means the connection between the documented multi-round progressive run and a disjoint terminal settlement remains unverified from the currently inspected public path.

6. **StarHarness proposal-budget frontier remains unresolved.** The paper/public algorithm still provides a useful contrast—proposer-visible search, proposer-hidden repeated selection, then final held-out evaluation—but this pass did not recover the exact number of selection queries/proposals corresponding to the reported 21 accepted patches. Do not infer it from accepted count.

## Interpretation / design consequence

For persistent self-improvement, distinguish **promotion safety** from **search-feedback safety**. A system may correctly prevent a weak candidate from becoming the durable committed champion while still letting that candidate and the selection-set verdict reshape the next candidate distribution. Repeated hidden-set feedback is therefore a training/control signal even when raw examples never leave the evaluator. A stronger long-run contract is: immutable candidate identity -> candidate-local evidence for durable promotion -> bounded/reusable release channel from any repeated selection set -> explicit treatment of provisional search parents -> disjoint terminal certification -> genuinely untouched outer test.

## Scope guards

- This checkpoint does **not** claim Recuris's reported benchmark gains are invalid.
- It does **not** claim progressive provisional adoption itself is harmful; it can be useful when component improvements are superadditive or below a single-round detection band.
- It does **not** claim raw dev trajectories are exposed to the meta-agent; the observed channel is aggregate ledger/verdict information plus provisional-parent selection.
- It does **not** claim `settle.py` is absent or ineffective. It exists and is deliberately evaluation-only; the unresolved question is whether/how the public multi-round progressive/paper-run path binds its final candidate to a fresh settlement that is not reused for search.
- All claims are limited to public Recuris commit f54c9dabfa370c0da495ddabe8ccbe8702b3eae7 and the inspected paths/configuration semantics.

## Exact continuation frontier

1. Trace the Recuris CLI/orchestration path from documented `metaagent run --round-gate progressive` to any post-run `settle.py`/frozen-set invocation; identify whether settlement is automatic, manual, special-protocol-only, or paper-run-specific.
2. Enumerate exactly which `led_verdict` fields survive into the 12-line ledger tail and quantify the information released per rejected/accepted selection query; distinguish verdict bit, net counts, p-values, regression counts, and any task identities.
3. Identify the exact Recuris paper-run configuration for reported evolved memories: strict vs progressive, number of proposals/rounds, whether provisional chains occurred, and whether final candidates were re-certified on fresh disjoint tasks.
4. Recover StarHarness total proposal/selection-query budget behind the 21 accepted patches from pinned historical code/configs or supplementary artifacts; compare information released by repeated selection with the once-only final holdout.
5. Continue searching for a >10-proposal live LLM-agent experiment with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, complete public proposal chronology, and a genuinely untouched outer test.

frontier_nonempty: true
