# Long Horizon clean_g1 checkpoint — SkillProx forward/backward lifecycle factorial and remaining interaction-identification gap

Evidence cutoff observed: 2026-08-27T06:03:18.839496+09:00

## Frozen semantic control tuple
- frozen note main SHA: `5d284a097cbc5ff6d630847b1218c8b1bce4c83f`
- root control revision: `11`
- role config revision: `5`
- root config blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Semantic control remained frozen after the first role-local/public semantic read. Later own checkpoint/receipt writes were not adopted as new control.
- Semantic inputs used: own clean latest/predecessor chain already opened in this invocation and public primary sources only. No O, other worker, downstream, legacy/pre_independence, shared ledger, other-role receipt/config, or unrelated repository semantic payload was used.

## New high-value evidence

### SkillProx explicitly instantiates the sought two-timescale 2x2 design, but the published headline outcome table still does not provide one fully matched four-cell interaction estimate
Primary source: *SkillProx: Self-Evolving Agent Skills via Proximal Textual Gradient Descent*, arXiv:2608.07449v1, 2026-08-07.

The paper is much closer to the unresolved lifecycle factorial than the earlier headline ablation suggested. Appendix C explicitly states that its four evolved-skill conditions form a **two-by-two component design**:

| Forward update policy | Without backward Prox | With backward Prox |
| --- | --- | --- |
| Open-loop | G1 | G2D |
| Closed-loop | G3f | G3D / SkillProx |

This maps closely onto the lifecycle question:
- **closed-loop forward** = candidate edit is re-executed on the originating batch, accepted only if hard correctness and mean cell accuracy do not regress, otherwise rolled back/retried and the measured rejection is fed to later diagnosis;
- **open-loop forward** = generated patches are committed without a post-edit execution acceptance test;
- **backward Prox** = after accumulation, units are leave-one-out audited on a fixed validation split, then consolidation/demotion/removal trials are revalidated before commit;
- **without Prox** = no retrospective unit-level shrinkage/maintenance stage.

The paper itself summarizes these timescales as `closed-loop forward = online update verification` and `backward Prox = post-training utility refinement`, making the admission-vs-maintenance analogy unusually direct.

### Reported outcomes establish both marginal mechanisms, but not a clean interaction estimate from one common replicate set
The main Qwen3.6-27B component ablation reports three cells under the same training configuration and fixed training-set seed protocol:
- G2D-like `w/o closed-loop diagnosis` / Prox only: `53.0 ± 1.0` SpreadsheetBench accuracy;
- G3f-like `w/o Prox` / closed-loop forward only: `52.0 ± 1.0`;
- G3D full: `54.5 ± 0.5`.

Removing either component therefore lowers held-out accuracy relative to full by 1.5 pp and 2.5 pp respectively in that reported ablation.

The fourth cell, open-loop/no-Prox G1, is not included in Table 3. It is separately evaluated in Appendix D on ten Qwen3.6-27B matched training seeds against G3f. Across those ten seeds:
- G1 mean OJ hard accuracy is `50.30 ± 2.50`;
- G3f mean is about `51.40 ± 1.51` (six wins, two ties, two losses; +1.10 pp mean hard improvement);
- the lower tail improves more clearly than the upper tail: minimum hard accuracy rises 46 -> 49, while two seeds still regress.

Because the G1/G3f ten-seed comparison and the three-cell headline ablation do **not** use one explicitly reported common four-cell replicate table, it would be invalid to calculate a precise interaction term by mixing those summaries. The paper defines the full factorial design, but the published aggregate evidence available in the paper does not expose one matched four-cell outcome matrix sufficient for a clean interaction estimate.

### Mechanistic evidence explains why the two controls are non-substitutable
The same paper provides direct traces showing why the stages address different failure modes:
- in one closed-loop seed, 22 attempted edits include 8 hard-regressing attempts that are blocked; one entire iteration is reverted;
- closed-loop forward does not eliminate all negative-utility accumulated content: on the matched seed it still retains two estimated-negative units and produces a longer skill than open-loop;
- backward Prox can remove/consolidate harmful residual content missed by the originating-batch gate; a representative consolidation keeps validation hard accuracy while improving the independent OJ hard result 46% -> 54%, but the authors explicitly caution that independent sampling prevents attributing every task transition causally to that single edit.

This supports the architectural conclusion that **online update admission and retrospective maintenance are complementary timescales rather than obvious substitutes**. It still does not establish a universal positive interaction or the exact magnitude of synergy.

### Important reproducibility limitation
The paper links an official GitHub repository, but at the observed public state the repository contains only a minimal README and no released per-seed four-condition result artifacts. Therefore the missing common-replicate fourth-cell matrix cannot currently be reconstructed from the official code repository. Do not infer it from condition naming or combine incompatible seed summaries.

## Updated synthesis
The prior frontier statement should be refined:

- It is no longer accurate to say that no direct 2x2 lifecycle design has been found. **SkillProx explicitly implements a 2x2 forward-gating × backward-maintenance design.**
- What remains missing is a **fully reported, same-replicate four-cell outcome matrix** that supports an interaction estimate under one matched candidate/task stream and evaluation sample.
- SKILL.nb still offers strong same-stream three-cell evidence in a web-agent workflow setting; SkillProx offers the explicit four-condition design in a spreadsheet skill-evolution setting but only partially aligned aggregate reporting.

The high-value experiment is therefore narrower than before: recover or rerun G1/G2D/G3f/G3D on the same seeds with identical candidate/task selection, evaluation protocol and compute accounting, then estimate main effects and interaction rather than only single-component drops.

## Frontier status
Substantially narrowed:
1. Existence of a lifecycle-factorial architecture separating online candidate gating from retrospective maintenance: **closed by SkillProx's explicit 2x2 condition design**.
2. Evidence that each mechanism can matter under the same system family: **narrowed by the three-cell component ablation plus matched G1-vs-G3f seed study**.

Still open:
1. **Matched four-cell interaction estimate:** G1/G2D/G3f/G3D evaluated over the same replicate set, candidate/task stream, model, compute and evaluation protocol, with uncertainty on the interaction term.
2. **Generalization beyond spreadsheet skill evolution:** analogous complete factorial in software/API/tool/GUI agents with persistent libraries.
3. Persistent hidden semantic-lineage discovery/repair across multiple generations.
4. Higher-powered maintenance-only studies and adaptive maintenance scheduling with intervention cost/calibration validity.
5. Strict matched rollback-target-selector comparison and decision-influence audits.

## Exact next action
1. Search the SkillProx paper/source artifacts and any later public release for per-seed G1/G2D/G3f/G3D outputs; if still absent, preserve the interaction gap rather than mixing summaries.
2. Search for another software/API/tool-agent paper that reports all four admission-gate × maintenance cells on one common replicate set.
3. Continue persistent semantic-lineage discovery/repair and cost-aware adaptive maintenance scheduler search.
4. Continue rollback-target selector and decision-influence evidence under fixed controls.
5. Preserve exact tested scope and a nonempty frontier; checkpoint findings are never global completion.
