# CLEAN self-improvement checkpoint — direct benign Remove ablation in a persistent skill bank

Time: 2026-08-26 03:26 JST
Role: self_improvement / clean_g1
Control: DESIRED_STATE control_revision=5; self_improvement config_revision=3.
Continuation: own clean LATEST checkpoint + public primary sources only. No O, other-worker, downstream, or legacy semantic state.

## SIG-SKILLBREW-REMOVE-ABLATION

Primary: Wentao Hu et al., *SkillBrew: Multi-Objective Curation of Skill Banks for LLM Agents*, arXiv:2605.29440v1, submitted 2026-05-28, https://arxiv.org/html/2605.29440v1

This directly fills the prior frontier asking for a benign ordinary-correctness curation experiment with explicit removal. SkillBrew keeps the worker model frozen and treats the persistent skill bank itself as the optimization object. It uses two data roles:
- support trajectories propose Add/Rewrite/Remove edits;
- a separate query set verifies candidate banks under utility, diversity and coverage, with the current bank included as a null/no-edit candidate.

For every retrieved skill, the Diagnoser performs a leave-one-out counterfactual replay on the same task with that skill removed, aggregates factual/counterfactual outcome pairs, and assigns Keep, Rewrite or Remove. This is ordinary task-outcome attribution, not a safety-specific risk label.

### Direct edit-operation ablation (Table 5)

All rows use the same curation framework but permit different edit subsets:

| operations | ALFWorld avg | WebShop score | WebShop success |
|---|---:|---:|---:|
| Add only | 47.0 | 50.0 | 26.4 |
| Add + Rewrite | 53.5 | 51.0 | 37.6 |
| Add + Remove | 48.3 | 49.5 | 34.5 |
| Add + Rewrite + Remove | **59.0** | **59.3** | **38.4** |

The cleanest marginal comparison for Remove is full vs Add+Rewrite: enabling Remove in the presence of Rewrite changes ALFWorld **+5.5 points**, WebShop score **+8.3**, and WebShop success **+0.8** in this tested setting. Remove alone is not sufficient: Add+Remove is far weaker than Add+Rewrite+Remove, supporting a complementary lifecycle where Rewrite salvages partially correct skills and Remove handles the minority whose strategy should not remain in the bank.

This is stronger evidence than an append-only-vs-full comparison because it isolates the presence of Remove while leaving Add and Rewrite available. It still does not identify *which individual removals* caused downstream gains, and planner interactions mean the difference should be interpreted as the value of having Remove available to the bank-level optimizer, not a universal per-skill delete effect.

### Bank-level objectives are also load-bearing

Table 4 holds the curation pipeline fixed and changes selector objectives:
- utility only: 45.8 ALFWorld / 48.2 WebShop score / 28.4 success;
- utility + diversity: 51.4 / 47.6 / 36.5;
- utility + coverage: 52.6 / 51.0 / 37.6;
- utility + diversity + coverage: **59.0 / 59.3 / 38.4**.

Thus local correctness contribution alone is not enough in this system. Diversity and coverage act as bank-level regularizers against redundancy and dormant/bloated content. The current bank is always a null candidate, so candidate-bank selection can choose not to edit.

### Main and transfer results

With frozen Qwen2.5-7B-Instruct, SkillBrew reports 59.0% ALFWorld average and 59.3/38.4 WebShop score/success, vs append-only Voyager 47.0 / 50.0 / 26.4 and ReAct 31.2 / 46.2 / 19.5. Bank size contracts and stabilizes over roughly 9–10 curation rounds while test success rises overall.

Cross-worker bank transfer is substantial but not identity-free. Example ALFWorld: Qwen3-4B's own bank yields 60.4 on Qwen3-4B and 78.4 when transferred to GPT-4o; GPT-4o's own curated bank yields 88.1 on GPT-4o. The procedural bank transfers, but diagonal/source-matched banks remain best in the reported table.

### Statistical/evaluation limitation

The outer query set is reused across curation rounds for candidate-bank verification. The paper supplies a utility non-degradation rule relative to candidates in each round, but this is not an anytime-valid statistical guarantee against adaptive overfitting to the repeatedly reused query set. Test curves are reported separately, which is useful, but the design does not close the reusable-holdout/global multiplicity frontier identified elsewhere.

### Artifact/reproducibility note

The paper is public; the search results checked in this run did not surface a clearly released official code repository or independent reproduction. Therefore the mechanism and ablation are primary-paper evidence only in this checkpoint.

## Synthesis

The benign persistence lifecycle now has a direct component-level result:

`Add + Rewrite` < `Add + Rewrite + Remove`

under the same frozen-worker curation framework. Combined with SAPO, this supports separating:
1. candidate-local **pre-storage** marginal utility (reject bad births),
2. existing-skill **post-storage** counterfactual diagnosis (Rewrite vs Remove),
3. bank-level diversity/coverage control,
4. outer validation that must itself be protected from adaptive reuse.

The important nuance is that deletion is not a substitute for repair. SkillBrew's strongest result requires both Rewrite and Remove, so lifecycle control should retain a graded action set: keep, repair/version, or retire, rather than binary append/delete.

## Nonempty frontier / exact continuation

1. Find an independent reproduction or public implementation of SkillBrew to verify the exact leave-one-out cache, null-candidate selection, and whether Remove remains beneficial under a fresh outer panel.
2. Search for a >10-round curation system with the same Keep/Rewrite/Remove counterfactual attribution but an anytime-valid/reusable-holdout acceptance rule; current SkillBrew query-set reuse is an adaptive-selection exposure.
3. Search for joint control of two multiplicities: many proposed skill edits inside each round and many policy/checkpoint choices across rounds.
4. Investigate whether a calibrated deterministic verifier can replace LLM diagnosis for code-like domains, then compare to the Blind-Curator false-pass boundary on reference-free domains.
5. Continue to seek integrated local validation + lifecycle repair/retirement + global statistical acceptance + untouched final lockbox in one long self-improvement stream.
