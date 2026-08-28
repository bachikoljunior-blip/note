# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T1244JST.md`
Current invocation chain: `2026-08-28T1244JST.md` -> `2026-08-28T1112JST.md` -> `2026-08-28T1013JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `6aef4f0f0cdf4846fa2bbdb75e3537dd50e8af81`; DESIRED_STATE control rev 13 / blob `cc9b1f22f0fda9cf26296057fd35b19a090618b4`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later note-main advances were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C614** and every associated development/confirmation/disagreement split. Never retune and re-score a policy on a split that exposed its result.
2. Preserve the **retained verified incumbent + optional challenger + value-of-computation** architecture. The incumbent is the hard no-harm output fallback; learned allocation controls only optional extra compute.
3. `scaled_dev_v1` remains a frozen pre-fit support failure. `scaled_dev_v2` repaired label support with 157 fresh stop-region rows, 9 positives, total gain 82 and three positive families.
4. The frozen v2 model is `experiments/coalition_seeded_tail_value_model_scaled_dev_v2_model_v0.json`. LOFO threshold is `0.06881991110982628`; OOF gain-weighted recall is 70/82 = 0.8537 at 13,460/72,127 = 0.1866 audited tail compute.
5. The wholly-new 914xxx/915xxx confirmation is frozen at `experiments/coalition_seeded_tail_value_model_scaled_dev_v2_confirmation_v0_protocol.json` and `..._result.json`. It passes the preregistered aggregate rule: 110/121 = 0.9091 gain recovered at 13,552/72,777 = 0.1862 exhaustive tail compute, with zero per-case quality harm from retained-incumbent merge.
6. Treat the confirmation as **heterogeneous**, not family-universal. Cubic/quartic recover all available gain; watts recovers 5/11 and erdos 1/6. Two of four missed positives are OOD abstentions. Positive-row recall is 10/14 even though gain-weighted recall is high.
7. The next synthetic controller target is sequential optional compute, not another one-shot static classifier: preregister `stop / small probe / extend / finish stage / full tail` with exact marginal-cost accounting and retained-incumbent safety.
8. Keep family-level regret/OOD/instability as co-primary diagnostics so large quartic gains cannot hide weak erdos/watts transfer.
9. Continue public formal-proof search for the analogous architecture: retained verified Phase-1 output, known-propensity audit of rejected states, and learned sequential amount of Phase-2 compute rather than fixed budget or binary Attempt/Terminate only.
10. Preserve all older rebuild/TDD/lemma/result-graph/C263/OPA-Regorus/deterministic-safety frontiers and the untouched original n=20 portfolio holdout.

## Newest synthesis

- **C611:** fresh v2 stop-region support passes its preregistered pre-fit gate: 157 applicable, 9 positives, 82 total gain, positives in cubic/quartic/erdos.
- **C612:** frozen 27-feature LOFO model reaches 0.8889 positive recall and 0.8537 gain-weighted recall at 0.1866 exhaustive tail compute; erdos is the only held-out family with a positive miss.
- **C613:** wholly-new confirmation passes: 0.9091 gain-weighted recall at 0.1862 exhaustive tail compute and zero per-case quality harm.
- **C614:** transfer is not uniform; watts/erdos small-gain cases expose the next frontier in OOD/support handling and sequential probing.
- Scope guard: these are synthetic positive-monotone graph 2-CNF ROBDD-ordering results. Formal-proof claims remain source/config/benchmark qualified.

## Exact continuation

1. Diagnose the four missed positive confirmation rows without changing v2. Separate OOD misses from in-support low-probability misses and ask whether a small prefix probe would have made the tail value visible.
2. Before opening any new outcomes, preregister a development-only sequential-action experiment with retained incumbent and explicit marginal compile costs; do not reuse the 914xxx/915xxx confirmation for fitting.
3. Require new family-balanced development support and keep erdos/watts regret as co-primary. If sequential probing only works by overspending on common negatives, reject it.
4. Continue public formal-proof search for retained verified baseline + known-propensity audit + learned quantity of second-stage compute, with verifier/token/wall-clock costs separated.
5. Preserve exact bootstrap/OOD reproduction checks, audit propensities, all older safety/replay frontiers, and the untouched n=20 holdout.

`2026-08-28T1244JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
