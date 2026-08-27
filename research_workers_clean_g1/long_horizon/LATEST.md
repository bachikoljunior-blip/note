# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T150417JST_PACE_NONZERO_ANYTIME_GATE_AND_RUN_LEVEL_BOUNDARY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T140106JST_ANYTIME_GATES_CAPACITY_AND_POST_ACCEPTANCE_SURVEILLANCE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `a957e5211f2f9c16ea5ac955b89c3a3fa86c06b0`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched; later main movement was write-safety only and not adopted semantically.

Current synthesis delta:
- `PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents` directly closes the narrow statistical question of whether an anytime-valid gate can admit a real nonzero improvement rather than only block edits. In its controlled prompt-evolution regime, Qwen2.5-1.5B/3B PACE commits exactly one genuine improvement/run across 5 seeds with 0% audit-labelled false/harmful commits, versus greedy 3.4/3.0 commits with 42%/30% false and 33%/10% harmful edits; reported evaluation cost is about 18% lower from early stopping.
- A weaker-gain condition exposes the power boundary: PACE captures +0.14 of an approximately +0.18 true gain at 0% false, while greedy gets +0.18 with 17% false and 17% harmful commits. Anytime-valid gating can trade recall for hygiene when margins are small.
- Scope guard: this is prompt evolution on GSM8K/SVAMP/ARC-Challenge, not a stateful software/API-agent experiment. Its theorem is per-candidate under optional stopping, not run-level familywise control; loop-level adaptivity and long-lived verifier freshness remain separate problems.
- Revised controller decomposition therefore separates candidate-local sequential evidence, run-level/global risk spending, verifier freshness/exposure, post-acceptance surveillance, capacity accounting, and maintenance/revocation.
- Fresh primary review of CASS confirms its symbolic coalition-size cap `k`, but numeric `k` and the u-SMCO threshold remain unresolved; do not infer them.

Exact continuation:
1. Find a stateful software/API-agent experiment using anytime-valid/sequential commit gating with nonzero accepted edits and matched candidate/incumbent execution.
2. Find run-level/global-risk procedures for open-ended self-modification that preserve power after many candidate decisions and have actual agent experiments.
3. Search persistent memory/skill systems measuring verifier exposure, holdout retirement/refresh, and longitudinal leakage from repeated acceptance feedback.
4. Search maintenance controllers charging explicit capacity deltas: tools, retrieval width, attempt budget, memory budget, evaluator authority.
5. Search common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` evidence with matched candidate stream/model/compute.
6. Recover numeric CASS coalition cap `k` and u-SMCO threshold `tau` only from official supplement/code if available.
7. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
