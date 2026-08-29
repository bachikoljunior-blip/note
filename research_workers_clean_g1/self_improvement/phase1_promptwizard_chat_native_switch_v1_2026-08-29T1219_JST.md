# Self-improvement Phase-1 — PromptWizard Chat-native joint instruction/example audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-002`
- calibration candidate: `CAND-FRESH-002`
- bound public family: `PromptWizard`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 2, decision blob `cae1ab5af3e06e821a12f3856754cee01ab93413`
- mechanism: `PROMPTWIZARD-CHAT-JOINT-v1`
- semantic work observed at: `2026-08-29T12:18:47.962871+09:00`

## 1. Public mechanism audit

Primary source: Agarwal et al., *PromptWizard: Optimizing Prompts via Task-Aware, Feedback-Driven Self-Evolution*, Findings of ACL 2025, https://aclanthology.org/2025.findings-acl.1025/ . A Microsoft Research description is at https://www.microsoft.com/en-us/research/blog/promptwizard-the-future-of-prompt-optimization-through-feedback-driven-self-evolving-prompts/ and the earlier preprint is https://arxiv.org/abs/2405.18369 .

PromptWizard is a discrete prompt-optimization framework that iteratively uses feedback-driven critique and synthesis while refining both prompt instructions and in-context examples. The public description also includes synthetic example generation and self-generated reasoning chains for examples. This Phase-1 leaf does not reproduce PromptWizard's task/cost benchmarks; it tests whether its joint instruction/example optimization can be reduced safely to recurring scheduled Chat.

## 2. Safe recurring-Chat reduction

`PROMPTWIZARD-CHAT-JOINT-v1` represents a candidate as a stable pair of (a) bounded role-local assignment-plan text and (b) a role-local constructed test/counterexample fixture. The example side is never allowed to import O, other-worker, downstream or legacy semantics, and a synthetic/curated example is never terminal evidence by itself.

Critique, synthesis, synthetic labels and self-generated reasoning are proposal mechanisms only. A model may propose or criticize an instruction/example pair, but the same prose cannot certify success, expand authority, alter CLEAN input boundaries, or produce milestone credit. Every pair starts `UNEVALUATED`; selection changes only after independent terminal evidence is durably read back. Root/config/control binding, safety/protected-authority boundary, stable frontier/candidate/transition identity, sealed selector decision, two-phase outcome durability and readback-before-credit remain immutable. Exact evidence ties keep the incumbent.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_promptwizard_chat_native_ablation_v1_2026-08-29T1218_JST.json`, blob `a2a399d351cfea3c31e4138c75d4bb572b6605cb`.

The unchanged frozen OPRO guard set passes **8/8** under `PROMPTWIZARD-CHAT-JOINT-v1`. Eleven joint-optimization counterexamples pass **11/11**: forbidden-source synthetic example quarantine; synthetic self-label gives no evidence/credit; same critic cannot generate and certify; self-generated reasoning is ignored as terminal evidence; control-rewriting feedback is quarantined; authority-escalating example is quarantined; safe instruction plus unevidenced example remains `UNEVALUATED` as a pair; pair/transition identities deduplicate; safe independently evidenced pair improvement may be selected; exact terminal tie keeps incumbent; and a fabricated negative example contradicted by durable evidence is diagnostic-only.

The conclusion is exact-scope controller conformance only. No PromptWizard benchmark result or general task-quality improvement is claimed.

## 4. Exact-scope terminal outcome

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-002`: **SATISFIED_EXACT_SCOPE**, bound to PromptWizard.

Stable terminal transition ID:

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-002:SATISFIED:PROMPTWIZARD-CHAT-JOINT-v1:20260829T1219JST`

Under the pre-frozen `TERMINAL-UTILITY-v2.1` mapping this status has utility `2`, subject to immutable outcome-record creation/readback and the external outcome seal. No selector archive or sticky-incumbent update occurs in this terminal artifact itself.

## 5. Next non-semantic candidate predeclaration

To maintain a nonempty frontier without choosing a specific future family before selector admission, predeclare:

- frontier: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-003`
- candidate id: `CAND-FRESH-003`
- strategy class: `unclassified_public_optimizer`
- priority index: `30`
- safe Chat-capable: `true`

Exact acceptance: after a future selector decision for this candidate is durably sealed, search primary public sources for a self-improvement/meta-optimization family not already audited in current own state; bind its exact identity before substantive adaptation; and test a Chat-native reduction under the unchanged frozen recovery/safety/evidence/durability guards. No specific future family semantics are selected or read in this predeclaration.

## 6. Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this terminal evidence; create/read back the immutable round-2 outcome record referencing its blob; persist/read back the external outcome seal; only then update the v2.1 archive with `unclassified_public_optimizer -> [2]`, set sticky incumbent to `unclassified_public_optimizer`, award this frontier's single credit, and admit `CAND-FRESH-003` to the next prospective decision.
