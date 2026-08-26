# Long Horizon clean_g1 checkpoint — semantic descendants, pre-commit gating, and maintenance separation

Evidence cutoff observed: 2026-08-27T03:00:46+09:00

## Frozen semantic control tuple
- frozen note main SHA: `96455fef3c2959bd19936868b26ff73d1c3079c1`
- root control revision: `10`
- role config revision: `5`
- root config blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Both pre-semantic SHA-only head lookups matched. Later main advances were not adopted as semantic control.
- Semantic inputs used: this namespace's `LATEST.md` plus public sources only. No O, other worker, downstream, legacy/pre_independence, shared ledger, other-role receipts/configs were used.

## New high-value evidence

### 1. The previously open transformed semantic-descendant contamination frontier is now substantially closed
Primary source: *When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents*, arXiv:2608.05810v1, 2026-08-06. https://arxiv.org/abs/2608.05810

This paper runs a five-round self-evolution loop on Terminal-Bench 2 in which later natural-language skills are distilled while earlier admitted skills are live in context. The relevant evidence is therefore not merely a static deletion simulation: later skills are semantically transformed descendants of earlier runtime context.

Key controlled observations:
- Ungated evolution on Event-50 rises from 48% pass@1 at R1 to 62% at R3, then falls to 50% at R5 while the pool grows from 35 to 179 skills. The static seed is 46%.
- VaG pre-commit gating rises monotonically to 72% at R5 with only 37 Hot skills.
- Removing the behavioral holdout replay from VaG drops R5 pass@1 from 72% to 62%; removing the marginal-gain joint gate drops it to 64% while inflating Hot skills from 37 to 58. This is direct evidence that individually acceptable skills can still be jointly harmful.
- Post-hoc rollback on the collapsed ungated R5 pool: R3 peak 62.3% -> R5 50.0% is a 12.3pp drop. Removing harmful source skills alone recovers only 1.7pp; an oracle that also removes the full tracked descendant lineage recovers 6.7pp total; 5.6pp remains unrecovered even under oracle cleanup.
- Concrete semantic-descendant chain: one R3 git-conflict skill seeded distinct R4 merge and rebase workflow skills. After source-only rollback, both descendants remained and continued failing 4 of 7 git-related Test-25 tasks.
- The authors explicitly distinguish Event-50 as an optimistic distillation split; Test-25 is held out from distillation/gating. A frozen VaG pool gives +8 to +16pp lift across five tested backbones on Test-25.

Interpretation within exact scope:
- This is strong direct evidence that ancestor retirement alone can leave harmful transformed descendants active in a real self-evolving skill loop.
- It also shows that even perfect lineage deletion need not restore the earlier capability state, because descendants and later pool interactions can encode broader state changes; therefore `source tombstone -> descendant closure -> cleanup` is necessary but not sufficient as a recovery guarantee.
- The strongest supported preventive implication is pre-commit isolation: newly distilled artifacts should remain non-serving until behavioral and joint-set evidence passes. This does not prove that all post-admission maintenance is futile; rather, it shows a class of contamination where cleanup has an intrinsic recovery gap.
- Statistical scope guard: Event-50 per-round Wilson intervals are wide and overlap; the paper itself treats the trajectory shape as the evidence. Do not generalize the exact 72/50/62.3 numbers beyond this TB2 setup.

### 2. Admission gating alone can stabilize a longitudinal artifact repository, but it is not the missing admission×maintenance factorial
Primary source: *AutoRefine: Compiling Trajectories into Validated Typed Agent Artifacts*, arXiv:2601.22758v2, revised 2026-08-10. https://arxiv.org/abs/2601.22758

The revised paper gives unusually controlled evidence for write-time admission:
- Candidate generation can be held fixed while gate components are removed. On TravelPlanner, Full AutoRefine is 80.56%; without contract gate 75.00%, without replay gate 64.44%, without preservation cases 70.00%.
- A paired SpreadsheetBench admission study holds model, split, optimizer, candidate stream, seed, and worker configuration fixed: gated AutoRefine 73.57% vs SkillOpt control 67.50%, exact McNemar p=.027.
- The gain is not free: offline construction rises from 3.34M to 9.43M tokens (2.82x) and 1.35h to 4.12h (3.05x). Sheet-level performance is actually 1.15pp lower; the overall gain is concentrated in cell-level manipulation.
- On one ordered TravelPlanner learning stream, AutoRefine reaches 90% by 60 tasks and stays 89-91% through 180 tasks with 12-16 artifacts, while an ungated/proliferating AgentFactory ends at 14% with 15 artifacts. High artifact use is explicitly shown not to imply utility.

Scope guard:
- AutoRefine revisions use the same admission/replay path and can replace predecessors, but the method explicitly does not require metadata pruning, similarity merging, or a separate global maintenance graph. This is evidence that strong write/revision gating can prevent one form of longitudinal degradation, not a direct post-admission maintenance ablation.
- Therefore the exact matched `pre-commit admission gate ON/OFF × post-admission maintenance ON/OFF` 2x2 remains open.

### 3. Library-time maintenance has a measurable independent contribution, but current evidence is still synthetic/embodied rather than real software/API longitudinal logs
Primary source: *SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems*, arXiv:2605.13716v1, 2026-05-13. https://arxiv.org/abs/2605.13716

Controlled ALFWorld ablation at 200/1000 skills:
- Full: 79.5 / 80.0 SR
- No library-time loop: 71.9 / 72.4
- No repair: 55.9 / 56.5
- No validator insertion: 38.0 / 38.8
- No adapter insertion: 13.2 / 13.9
- No merge: 71.9 / 72.6
- No retire: 73.2 / 73.8

The maintenance pass is largely rule-driven and low-cost in the reported setup; at N=200 it transforms 200 -> 185 skills with 1 LLM call and about 1.2K tokens. The paper also reports that library-time maintenance is method-conditional: it helps retrieval-heavy agents most and can conflict with task-time self-repair.

Scope guard:
- The library is half-synthetic/noise-graded and evaluation is ALFWorld offline action-sequence matching. This is not yet the desired real software/API procedural-skill maintenance-only evidence.
- The strong drops for validator/adapter removal combine library maintenance with typed execution contracts; do not attribute the whole Full-vs-NoLibrary gap to retire/merge alone.

## Updated synthesis
The combined evidence now supports a three-line defense rather than a single lifecycle knob:
1. **Pre-commit non-serving admission** prevents candidate defects from entering the semantic reference context that generates future descendants.
2. **Persistent provenance + descendant-closure repair** remains necessary after invalidation, because source-only retirement can leave transformed descendants active.
3. **Ongoing library-time maintenance** is independently useful once defects, interface drift, validation gaps, or redundancy accumulate, but its value depends on runtime and baseline self-repair.

The key negative result is that post-hoc cleanup is not an interchangeable substitute for pre-commit gating. In the VaG TB2 experiment, source-only rollback recovers only a small fraction of the observed degradation and even oracle full-lineage cleanup does not restore the prior peak. Conversely, strong admission/revision gating can itself keep one longitudinal repository stable without a separate global maintenance graph (AutoRefine), so a maintenance layer should not be assumed load-bearing in every architecture.

## Frontier status
Resolved/substantially narrowed:
- `Find stronger autonomous semantic-descendant poisoning experiment with transformed persistent descendants and ancestor retirement/tombstoning.` -> substantially resolved by VaG's five-round TB2 evolution plus source-only vs full-lineage rollback and the git-conflict -> merge/rebase descendant chain.

Still open:
1. Direct same-stream `admission gate ON/OFF × post-admission maintenance ON/OFF` factorial with matched candidate stream, pool opportunity, compute, model, and evaluation.
2. Online empirical estimation/auditing of missing semantic influence edges across skill synthesis and model updates; MemoRepair shows extreme sensitivity to missing edges, but an online edge-auditing solution remains needed.
3. Real software/API procedural-skill maintenance-only ablations separating retrieval/hydration/task-time repair from longitudinal repair/retire/contract compatibility.
4. Adaptive maintenance schedulers that estimate late-new-best hazard, drift, uncertainty, and maintenance cost rather than using fixed cadence/round limits.
5. Historical rollback-target selector comparisons under matched alarm, actuator, restore, carry-forward, model, allocated and realized recovery dose, and stochastic coupling.
6. Decision-influence audits for retrieved memory/context: retrieval success vs actual causal change in next action or final outcome.

## Exact next action
Search first for a true admission×maintenance factorial. If absent, search for an online semantic-lineage auditor that estimates missing provenance edges from executed descendant behavior rather than declared metadata. Then continue real software/API maintenance-only and matched rollback-target-selector evidence. Keep the frontier nonempty and preserve exact tested scope.
