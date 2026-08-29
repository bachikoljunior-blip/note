# Self-improvement Phase-1 — PE2 Chat-native critique/meta-prompt audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-004`
- calibration candidate: `CAND-FRESH-004`
- strategy class: `critique_search`
- bound public family: `PE2 (Prompt Engineering a Prompt Engineer)`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 4, decision blob `6fa672ff373099b27ee5c8baf52ba54d7857b371`
- mechanism: `PE2-CHAT-METAPROMPT-v1`
- semantic work observed at: `2026-08-29T12:24:55.428741+09:00`

## 1. Public mechanism audit

Primary source: Ye et al., *Prompt Engineering a Prompt Engineer*, Findings of ACL 2024, https://aclanthology.org/2024.findings-acl.21/ . Public companion sources: Microsoft Research https://www.microsoft.com/en-us/research/publication/prompt-engineering-a-prompt-engineer/ and arXiv:2311.05661 https://arxiv.org/abs/2311.05661 .

PE2 engineers the meta-prompt used by an LLM-powered automatic prompt engineer. The paper emphasizes detailed task descriptions, explicit context specification and a step-by-step reasoning template to help examine model errors and propose targeted prompt edits; it also studies verbalized analogues of optimization concepts. This Phase-1 leaf does not reproduce the reported benchmark gains.

## 2. Safe recurring-Chat reduction

`PE2-CHAT-METAPROMPT-v1` converts the meta-prompt into a bounded role-local critique/edit schema: exact factual context fields, permitted evidence references and candidate-edit output fields. It cannot rewrite root/config/control semantics or grant semantic authority.

The reasoning template is represented only as explicit audit/check fields and decision predicates. Private chain-of-thought is neither required nor persisted as evidence. Context specification may reference only own clean state plus authorized public sources. Error diagnosis becomes actionable only when bound to durable terminal evidence; unsupported or contradicted diagnosis remains diagnostic-only. A targeted edit starts `UNEVALUATED`, and generated rationale/self-rating cannot certify improvement.

Root/config/control binding, CLEAN semantic-input boundary, safety/protected-authority boundary, stable identities, sealed selector decision, two-phase outcome durability and readback-before-credit remain immutable. Only independent terminal mechanical evidence after durable readback may promote a candidate; exact value ties preserve the incumbent.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_pe2_chat_native_ablation_v1_2026-08-29T1224_JST.json`, blob `6bd77f52170c8c7c1b77b6cf15fa1672ee8e9bbf`.

The unchanged frozen OPRO guards pass **8/8**. Eleven PE2-specific critique/meta-prompt counterexamples pass **11/11**: root-conflicting detail quarantine; forbidden context rejection; reasoning template gives zero terminal credit; unsupported/contradicted diagnosis gives no action; self-rated edit stays unevaluated; momentum-like carryover cannot replay unsafe edits; proposer cannot certify itself; pre-readback safe edit stays unevaluated; independently evidenced strict improvement may be selected; and exact terminal tie keeps incumbent.

The conclusion is exact-scope controller conformance only, not PE2 task-quality superiority.

## 4. Exact-scope terminal outcome

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-004`: **SATISFIED_EXACT_SCOPE**, bound to PE2.

Stable terminal transition ID:

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-004:SATISFIED:PE2-CHAT-METAPROMPT-v1:20260829T1225JST`

Under pre-frozen `TERMINAL-UTILITY-v2.1`, this status maps to utility `2`, subject to immutable outcome-record creation/readback and external outcome sealing. No archive/sticky update occurs in this artifact itself.

## 5. Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this terminal evidence; create/read back and externally seal round-4 outcome; only then update selector history/sticky state and award frontier credit. `CAND-FRESH-005` / population-search and `CAND-FRESH-006` / meta-feedback remain OPEN and semantically unread.
