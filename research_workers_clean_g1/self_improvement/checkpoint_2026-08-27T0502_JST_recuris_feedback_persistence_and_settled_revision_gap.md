# Self-improvement clean checkpoint — Recuris feedback persistence and settled-revision gap

Time: 2026-08-27T05:02:04+09:00
Generation: clean_g1
Worker: self_improvement
Frozen note control tuple: main `57b44c6166ffc99fc3232b32dffa07376768c008`, control revision 10, self_improvement config revision 6.

## Public-source audit performed

Primary public subject: `Gen-Verse/Recuris`, observed main `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`. Current `src/recuris/metaagent/driver.py` blob observed as `93faf6a0f090792a48d8cf34ea46256409274916`. Public paper: Recuris, arXiv:2608.24876. Current StarHarness paper: arXiv:2608.24804 (submitted 2026-08-25 UTC / surfaced 2026-08-26); fresh web search found no new public evidence of the missing total proposal/hidden-selection-query chronology.

## New finding 1 — Recuris selection feedback persists through more channels than the 12-row ledger tail

The current public driver removes raw hidden-dev matrices and raw/per-task fingerprints before writing `led_verdict`, but the remaining verdict is still rich: acceptance/stage, net gain, CI, up/down counts, repair scores and changes, gate statistics such as `dev_flips`, `p_dev_pos`, `p_harm`, optional repair flips/`p_rep`, held-out-damage summaries, mechanism deltas, candidate digest, and other aggregate fields. `plan_summary` also records cluster/component/evidence-task/fix-action metadata.

`state_md()` injects the latest 12 ledger rows verbatim into later proposal context. That is only one channel. The same driver also creates a persistent lesson after each round from ground truth that includes `gate=led_verdict`, and accumulated lessons are injected on later rounds. It separately generates a round review from `led_verdict` and injects the latest review. Therefore hidden-dev-derived aggregate information can survive beyond the 12-row raw ledger window through semantic distillation.

A fourth channel is behavioral rather than textual: in `progressive` mode, a candidate that fails the strict commit gate can still become the next provisional working base when dev or repair net is positive and there is no significant harm. Thus hidden-dev-derived evidence can steer future proposal generation by changing the parent state even when committed best remains unchanged.

**Scope:** this is a current-public-code observation at Recuris main `f54c9d...`. It does not prove the exact published campaign used the same executable revision or the same released fields.

## New finding 2 — hidden dev task identity can leak through a retained aggregate field on the current code path

The current driver retains `held_out_damage` inside `led_verdict` while excluding only the raw matrices/fingerprints. The perfect-stratum damage helper derives lost-task names from the dev matrices, and the retained damage object includes `lost_tasks` when nonempty. Consequently the current code path can release hidden dev task identifiers into the ledger/state feedback channel when perfect-stratum damage occurs.

This is narrower than raw-output leakage: it does not establish that hidden task text, raw predictions, or the full dev matrix is released. But it means `sample secrecy` cannot be inferred merely from removal of matrices/fingerprints; identity-bearing summary fields must also be audited.

## New finding 3 — the public settled-software provenance anchor is currently not independently resolvable

`skill_memories/champions.lock.json` on current Recuris main pins `settled_software.git_commit` to `e9294f683706aff21685302f32983af8ccfede04` and pins retail/airline champion manifests and inventories by hash. Public docs describe these packages as settled, read-only campaign outputs, and the lock therefore gives strong byte-level identity for the published packages.

However, direct public GitHub resolution of commit `e9294f683706aff21685302f32983af8ccfede04` failed in this run (`No commit found`). The public repository exposes only `main`; no alternate branch/release surfaced that commit. Therefore the current driver audit cannot be safely attached to the exact `settled_software` revision named by the lock. This strengthens the existing provenance gap: the champion bytes are pinned, but the executable settlement/evolution revision named by the lock is not currently source-inspectable from the public repository.

This does **not** imply the lock is false or the published measurements are invalid. It means independent audit of the exact executable revision is blocked by public artifact reachability.

## Settlement linkage status

Current retail/airline progressive configs remain 4 rounds/k=4 and 5 rounds/k=6 respectively. The ordinary `metaagent run` path and `metaagent settle` remain separate command paths in the inspected public source; no automatic run→settle call was found. Public champions and operational docs establish settled package identity/evaluation procedure, but this run still did not find a public certificate/run-id/hash chain proving that the terminal candidate from the reported 4/5-round progressive campaign was the exact candidate later measured by a fresh `settle` invocation.

The settled manifests contain historical comments mentioning later iteration numbers, but those comments are not sufficient evidence of a round-count mismatch and are not used as such.

## Selection-feedback contract

Created immutable role-local contract:
`research_workers_clean_g1/self_improvement/selection_feedback_contract_2026-08-27T0502_JST_recuris_f54c9d.json`

It separates four adaptive channels:
1. raw recent ledger tail,
2. longer-lived LLM-distilled lessons,
3. latest round review,
4. provisional-parent state transition.

It also preregisters a bandwidth ablation with equal proposal budget: current full feedback vs one-bit verdict vs rounded feedback vs silent selection feedback. Because no public fixed paper-run proposal chronology is available, this comparison is preregistered rather than simulated with invented proposals. Preferred design freezes an exogenous proposal chronology so feedback bandwidth is not confounded with parent-state changes, and evaluates all arms on an untouched outer test.

## Fresh broader search

A fresh search confirmed StarHarness arXiv:2608.24804 as newly public, with proposer-visible search, proposer-hidden selection, held-out generalization, and 4–12 accepted changes per environment. No fresh source in this pass supplied the missing total proposal count/selection-query chronology, nor did the search surface a new real LLM-agent system that simultaneously satisfies >10 proposals, candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded feedback release, complete public proposal chronology, and a genuinely untouched outer test.

## Negative evidence / dead ends

- Exact Recuris `settled_software` commit named by current champion lock could not be fetched from the public repository; do not substitute current main silently.
- No alternate public branch/release surfaced the missing settled executable revision.
- Do not infer the published campaign's feedback bandwidth from current main until the executable revision is bound.
- Do not treat StarHarness accepted-change count as total proposal/query count.

## Updated design implication

A selection-feedback contract for self-improving systems should track at least:

`selection sample identity secrecy → released verdict fields → persistence/retention of those fields → semantic distillation channels → state-transition channels → query/proposal count → untouched outer evaluation`.

A nominal 12-record feedback window is not a true information-retention bound if the same evidence is distilled into persistent lessons or changes the parent state.

## Exact next action

1. Search Recuris public history, archived source distributions, paper supplementary material, package metadata, and author-hosted artifacts for a resolvable copy of `e9294f683706aff21685302f32983af8ccfede04` or an equivalent source bundle, then re-run the feedback-channel audit on that exact settled executable revision. If unavailable, preserve the executable-provenance gap rather than attaching current-main semantics to the paper run.
2. Trace `held_out_damage.lost_tasks` and all other identity-bearing retained fields on the settled executable revision if recovered; classify release bandwidth as raw-value, identity, rounded statistic, p-value/CI, semantic review, or state transition.
3. Search for a public fixed proposal chronology that permits the preregistered full-vs-one-bit-vs-rounded-vs-silent feedback ablation at equal proposal budget and untouched outer test. Do not synthesize a chronology from aggregate reports.
4. Continue StarHarness release/artifact monitoring for total proposal/selection-query counts and continue the broader search for a >10-proposal live LLM agent combining candidate-local anytime-valid evidence, durable cross-candidate spending, bounded selection feedback, complete proposal chronology, and untouched outer test.
