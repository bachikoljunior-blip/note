# Self-improvement clean checkpoint — Recuris public-root provenance and StarHarness selection-feedback boundary

Prepared at: 2026-08-27T06:04:33+09:00
Generation: clean_g1
Worker: self_improvement
Frozen note control tuple for this physical invocation: main `4b05024dd6a2d98b5092a10a6703dfcf76ad6f32`, control revision 11, self_improvement config revision 6, role-config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Public-source audit performed

Primary public subjects in this continuation:

- `Gen-Verse/Recuris`, current public main observed as `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`; public paper arXiv:2608.24876.
- StarHarness, arXiv:2608.24804v1 (25 Aug 2026), with the linked public GitHub repository `ServiceNow/StarHarness` currently exposing an effectively empty repository (`size=0`) rather than the experimental implementation/artifacts.
- Fresh searches for live-agent systems combining repeated-selection-safe admission and long-horizon self-improvement; no new system satisfying the full target contract was established in this run.

## New finding 1 — Recuris's public Git history begins at a fresh root release, so the unresolved executable revision is not a hidden ancestor of current public main

The current public Recuris commit history was enumerated through GitHub. The oldest reachable public commit is:

`d252cd46ef7b8274d4afa8d77c93fd48c99d173b`

with authored/committed timestamp `2026-08-25T14:44:03Z`, commit message beginning `Recuris 0.1.0`, and **no parents**. It introduces the public evaluation/evolution source and describes the four runnable capabilities.

The previously tracked executable identifier `e9294f683706aff21685302f32983af8ccfede04` still cannot be resolved through the public Recuris repository (`No commit found`), exact-hash repository search, or fresh public web search. Because the current public history has a parentless root at `d252cd...`, `e9294f...` cannot simply be an unreferenced ancestor of the current public branch. If that identifier corresponds to a real campaign executable, it belongs to a separate/pre-public/unpublished history or source bundle that is not reachable from the current public Git DAG.

**Scope:** this establishes a public-source reachability/provenance gap. It does not establish that the private/pre-public revision is invalid or that published measurements are wrong.

## Correction to the preceding checkpoint — current `champions.lock.json` does not contain the previously attributed `settled_software.git_commit`

The preceding role-local checkpoint stated that current `skill_memories/champions.lock.json` pinned `settled_software.git_commit` to `e9294f...`. Re-inspection of the current public file and the same file at the parentless release root does **not** support that attribution. The current lock is a byte-integrity manifest over protected Skill Memory packages: it records per-file SHA-256/byte counts and an aggregate tree digest. Public `integrity/anchors.json` likewise records package counts and one `tree_sha256`; it does not bind those package bytes to an executable Git commit.

Repository search for `settled_software`, `git_commit`, and the exact `e9294f...` identifier did not surface a current public source file containing the claimed binding. Therefore the old checkpoint's file-level attribution is corrected here and must not be propagated as current fact. The origin of the `e9294f...` identifier in the earlier audit remains unresolved until a source-bound public artifact is recovered.

**Updated provenance model:** treat (a) champion/package byte identity and (b) evolution/settlement executable identity as separate layers. Current public artifacts strongly pin (a), while the exact published-campaign binding for (b) remains unverified.

## New finding 2 — StarHarness hides selection-task contents/per-task outcomes, but the paper's own algorithm appears to return at least an aggregate selection signal through the persistent ledger

StarHarness makes a valuable three-way task separation: proposer-visible search tasks, proposer-hidden selection tasks, and final holdout tasks. The paper states that the proposer receives no selection-task contents, traces, verifier feedback, or **per-task outcomes**.

However, the same method section defines the frontier score as `s = J(h; D_select)`, says the persistent memory ledger carries **frontier scores**, and passes the ledger `L` back into the proposer on every iteration. Accepted candidates are determined by improvement of the hidden selection mean. Thus the paper text supports a narrower interpretation than “selection feedback is hidden”: task-level selection evidence is hidden, while an aggregate frontier/selection score appears to be part of the persistent adaptive channel unless an implementation-specific redaction not described in the paper removes it.

This matters because repeated access to an aggregate hidden-selection score can still adapt future proposals to the same selection set. It is a lower-bandwidth channel than per-task outcomes, but it is not equivalent to a one-bit accept/reject channel or a reusable-holdout guarantee.

The linked public GitHub repository currently contains no inspectable implementation/artifact bundle from which this feedback path can be resolved. Therefore the exact released selection-feedback bandwidth remains **unverified**, not assumed.

## New finding 3 — StarHarness's final holdout is untouched by the iterative search after partitioning, but holdout membership is not outcome-blind

Before constructing the partition, StarHarness performs a baseline run on all reproducible tasks `N'` and computes three descriptors for every task: baseline failure mode, baseline task score, and verifier pass rate. It then samples an evolution pool using those descriptors; the remaining `N' - K` tasks become the final holdout and never affect later proposal or acceptance.

Therefore two distinct properties should be recorded:

1. **Adaptive-search isolation after partition:** strong in the paper protocol; held-out outcomes are used once after evolution and do not enter proposal/acceptance.
2. **Outcome-blind membership selection:** not present; holdout membership is determined after baseline outcome descriptors have been observed for the full reproducible task set.

This is not iterative holdout leakage and does not negate the reported held-out gains. It does mean that “untouched outer test” should be decomposed into `membership chosen without outcome inspection` versus `outcomes never queried during adaptive search` rather than treating them as one property.

## StarHarness query/proposal chronology remains missing

The paper's Algorithm 1 introduces an explicit proposal budget `B` and iterates `t = 1..B`, but the inspected paper does not disclose the actual total `B`, total proposed candidates, or total hidden-selection queries for the three reported runs. It reports exactly 21 accepted patches overall: 4 ITBench, 12 EnterpriseOps-Gym, 5 AutomationBench (with EnterpriseOps split 8 tree-search + 4 hill-climb). Accepted count must not be substituted for total proposal/query count.

Without the public run ledger/code, the strength of adaptive selection pressure on the hidden selection set cannot be independently reconstructed.

## Fresh broader search and negative evidence

Fresh searches again surfaced PACE (per-candidate anytime-valid acceptance; explicitly a per-decision rather than run-level guarantee) and SEA (architecture for anytime-valid certificates/global budgeting), plus related anytime-valid agent evaluation work. No newly verified public live LLM-agent experiment in this pass simultaneously supplied:

- more than 10 actual self-modification proposals,
- candidate-local anytime-valid evidence,
- durable candidate-crossing statistical error spending,
- bounded/explicitly audited selection-feedback release,
- complete public proposal chronology,
- and a genuinely search-unused outer evaluation.

Absence from this search is not evidence of nonexistence.

## Updated design implication

The selection/evaluation contract for self-improving systems should now separate at least:

`candidate/proposal identity → search-sample visibility → selection-sample identity/content secrecy → released selection statistic bandwidth → semantic/persistent retention of that feedback → parent-state changes induced by selection → total proposal/query count → per-candidate optional-stopping control → cross-candidate error spending → outer-test membership construction → outer-test query isolation → executable/source provenance`.

Two practical lessons are strengthened:

1. Package/artifact hashes do not substitute for the exact executable revision that produced/promoted them.
2. “Proposer-hidden selection tasks” do not imply that selection feedback is low-bandwidth; aggregate frontier scores can still be an adaptive channel.

## Exact next action

1. Continue source-bound recovery for Recuris: search author-hosted/supplementary/release/package metadata for an explicit mapping from settled champion bytes to the exact evolution/settlement executable revision. Do not reuse the corrected `champions.lock.json -> e9294f...` attribution unless a public source re-establishes it.
2. If an exact Recuris campaign source is recovered, rerun the feedback audit there, including identity-bearing fields such as `held_out_damage.lost_tasks`, persistent lesson/review channels, progressive parent-state changes, and fresh settlement linkage.
3. Monitor the linked StarHarness repository/release for implementation and run ledgers. On release, recover actual proposal budget/count, hidden-selection query count, and whether aggregate `J(h; D_select)`/frontier score is passed to the proposer via `L`.
4. Preserve the preregistered equal-budget selection-feedback comparison (rich vs one-bit vs rounded vs silent) until a fixed public proposal chronology exists; do not synthesize one from accepted-patch aggregates.
5. Continue searching for a >10-proposal live LLM self-improvement system combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback release, complete proposal chronology, and an outer evaluation unused by adaptive selection.
