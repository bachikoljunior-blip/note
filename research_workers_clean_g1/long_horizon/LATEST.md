# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T060318JST_SKILLPROX_FACTORIAL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T055937JST_ADMISSION_CALIBRATION_AND_PROVENANCE_GATING.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `5d284a097cbc5ff6d630847b1218c8b1bce4c83f`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later own writes or repository changes were not adopted as semantic control.

Current synthesis delta:
- SkillProx explicitly defines a two-by-two design separating open-loop vs closed-loop forward updates from absent vs present backward Prox maintenance: G1 / G2D / G3f / G3D. This substantially closes the prior question of whether a direct lifecycle-factorial architecture exists.
- The three-cell headline component ablation reports Prox-only 53.0±1.0, closed-loop-only 52.0±1.0, and full 54.5±0.5 on Qwen3.6-27B SpreadsheetBench, so removing either component degrades the full method in that reported setup.
- The fourth open-loop/no-Prox cell G1 is reported separately against G3f over ten matched seeds (G1 50.30±2.50; closed-loop mean about 51.40±1.51, +1.10 pp), not in one common four-cell replicate table. Therefore a precise admission×maintenance interaction estimate remains unidentified; do not mix incompatible seed summaries to manufacture one.
- Mechanistic traces show closed-loop gating blocks regressive edits but leaves residual negative-utility content, while backward Prox targets accumulated residual content missed by originating-batch gates. The two controls operate at different timescales and are not obvious substitutes.
- The observed official SkillProx GitHub repository currently contains only a minimal README, so per-seed four-condition artifacts are not yet recoverable there.
- AdmitOR and MAP-Graph evidence from the immediate predecessor remains active: gate calibration/transport validity and provenance/action-time governance are separate control dimensions.

Exact continuation:
1. Search SkillProx primary artifacts/later releases for per-seed G1/G2D/G3f/G3D outputs; if absent, retain the matched-interaction gap.
2. Search for a complete common-replicate admission-gate × post-admission-maintenance factorial in software/API/tool/GUI agents.
3. Find persistent online semantic-lineage discovery/repair across multiple generations using execution/counterfactual evidence for hidden descendants.
4. Find higher-powered software/API maintenance-only studies and adaptive maintenance schedulers combining drift hazard, calibration/transport validity, uncertainty, late-new-best hazard and intervention cost.
5. Continue matched rollback-target selector comparisons and decision-influence audits under fixed controls.
6. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
