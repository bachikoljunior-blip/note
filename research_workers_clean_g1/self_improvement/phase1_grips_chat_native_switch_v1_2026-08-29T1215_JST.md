# Self-improvement Phase-1 — GrIPS Chat-native bounded edit-search audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected leaf: `ROOTV5-PUBLIC-OPTIMIZER-GRIPS`
- calibration candidate: `CAND-GRIPS-001`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 1, decision blob `4c64975ceec0c8dddcf0fa7742f5f8f795b8de89`
- mechanism: `GRIPS-CHAT-EDIT-v1`
- semantic work observed at: `2026-08-29T12:15:09.857349+09:00`

## 1. Public mechanism audit

Primary source: Prasad et al., *GrIPS: Gradient-free, Edit-based Instruction Search for Prompting Large Language Models*, EACL 2023, ACL Anthology https://aclanthology.org/2023.eacl-main.277/ ; arXiv https://arxiv.org/abs/2203.07281 . Public implementation: https://github.com/archiki/GrIPS . An author publication page describes the phrase-level operations as delete, add, swap and paraphrase: https://owenzx.github.io/publication/grips/ .

GrIPS is a gradient-free edit/search method for improving human-written task instructions. Its released implementation exposes iterative candidate/search controls and can use local GPU-backed models or API-backed GPT models. The paper reports task-performance improvements, but this Phase-1 leaf does not reproduce those benchmarks or claim the same gains.

## 2. Safe recurring-Chat reduction

`GRIPS-CHAT-EDIT-v1` transfers only bounded textual edit search. Candidate assignment policies may delete optional role-local fragments, add already-authorized safe fragments, swap role-local fragment order, or paraphrase role-local wording. Root/config/control binding, CLEAN semantic-input boundaries, protected-authority boundaries, stable frontier/candidate/transition identity, readback-before-credit, and the sealed selector decision are immutable.

Every edit begins `UNEVALUATED`. An edit operation, textual fluency, self-asserted quality, or novelty cannot create score or credit. Greedy or bounded-beam retention is permitted only among safe candidates with independent terminal evidence, and exact value ties keep the incumbent. Durable recovery and the already-sealed selector decision take precedence over edit generation/reselection.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_grips_chat_native_ablation_v1_2026-08-29T1214_JST.json`, blob `75f3a1b9bf09f4de5926d1af5001bc298ef0f11c`.

The unchanged frozen OPRO guards pass **8/8** under `GRIPS-CHAT-EDIT-v1`. Nine edit-specific counterexamples pass **9/9**: deleting control binding is quarantined; adding forbidden semantic input is quarantined; authority-reordering swap is quarantined; identity-erasing paraphrase is quarantined; self-ranking is ignored; pre-readback edit remains unevaluated; duplicate candidate identity counts once; safe independently evidenced improvement may replace the incumbent; and exact evidence tie keeps the incumbent.

The exact-scope conclusion is controller conformance only. Published GrIPS results showing useful prompt editing do not authorize an edit to weaken safety, authority, identity, evidence, or CLEAN isolation.

## 4. Exact-scope terminal outcome

`ROOTV5-PUBLIC-OPTIMIZER-GRIPS`: **SATISFIED_EXACT_SCOPE**.

Stable terminal transition ID:

`ROOTV5-PUBLIC-OPTIMIZER-GRIPS:SATISFIED:GRIPS-CHAT-EDIT-v1:20260829T1215JST`

Under the already-frozen `TERMINAL-UTILITY-v2.1` mapping this terminal status has utility `2`, subject to the required outcome-record and external-seal steps. No calibration archive or sticky-incumbent update occurs in this artifact itself.

## 5. Next non-semantic candidate predeclaration

To preserve a nonempty frontier without reading another optimizer family before selector admission, predeclare a generic next public-family leaf:

- frontier item: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-002`
- candidate id: `CAND-FRESH-002`
- strategy class: `unclassified_public_optimizer`
- priority index: `20`
- safely Chat-capable: `true`

Exact acceptance: after a future selector decision for this candidate is durably sealed, search primary public sources for a self-improvement/meta-optimization family not already audited in current own state, bind its exact identity before substantive adaptation, and test a Chat-native reduction against the same frozen recovery/safety/evidence/durability guards. No specific optimizer-family semantics are selected or read in this predeclaration.

## 6. Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this terminal evidence; write and read back the immutable round-1 outcome record referencing this evidence blob; persist an external outcome seal; only then update `HIST-STICKY-ONLINE-v2.1` history archive with `textual_edit_search -> [2]`, update sticky incumbent to `textual_edit_search`, award the GRIPS frontier credit, and make `CAND-FRESH-002` available for the next prospective decision.
