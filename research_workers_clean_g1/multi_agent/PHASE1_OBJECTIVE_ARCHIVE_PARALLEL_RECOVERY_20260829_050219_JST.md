# Phase-1 objective-first recovery archive and conflict-gated parallel fragments

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple remains note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- semantic inputs: own Phase-1 multi-effect recovery checkpoint and this finite synthetic comparative model only. No other-worker/downstream/O/legacy/shared-ledger semantics were used.

## Leaf objective

The prior leaf produced a safe archive of behaviorally different recovery dispositions (`all-forward`, `all-rollback`, `mixed-vector`, manual). This leaf asks two multi-agent planning questions:

1. should a controller select the globally cheapest proposal before checking the current business objective/proof, or keep an objective-indexed archive of current safe proposals?
2. when two safe fragments are independently available, can they be executed in parallel without reintroducing duplicate exclusive effects?

It also includes an explicit **synthetic early-diversity-collapse negative mechanism** that retains one cheapest feasible proposal before objective/current-proof filtering. This is not a general claim that critique or communication is harmful; it isolates the structural loss caused by collapsing alternatives before the decisive constraints are known.

## Finite model

The executed model enumerates **46,080 equal-weight synthetic scenarios** over:

- objective contract: all-forward / all-rollback / atomic-all-or-nothing / mixed permitted / manual permitted;
- which of `F/R/M` proposals are feasible;
- which proposal proofs are still current;
- six cost orderings;
- fragment composition permitted/forbidden;
- exclusive effect keys disjoint/shared;
- reservation/fence present/absent;
- three independent latency profiles, including cases where an `F+R` fragment composition is faster than any whole safe proposal and cases where it is not.

Compared policies:

1. `scalar_cheapest_only` — choose cheapest feasible proposal, then execute even if its proof is stale or it violates the current objective.
2. `objective_first_archive` — filter by current proof + objective behavior first, then choose the cheapest remaining proposal.
3. `early_crosscritique` — collapse to one cheapest feasible proposal before objective/current-proof filtering; if that retained proposal is later invalid, fail closed even if a discarded valid objective proposal existed.
4. `fragment_parallel_fenced` — start from the objective-first archive; use `F+R` fragments only if they are both current, composable, objective-compatible, strictly lower latency, and shared exclusive keys are reserved/fenced.
5. `neg_parallel_unfenced` — same latency decision but ignores shared-key reservation, intentionally exposing duplicate authoritative effects.

## Main results

| policy | safe terminal coverage | unsafe scenarios | proposal-loss / parallel facts | mean safe latency proxy |
|---|---:|---:|---|---:|
| scalar cheapest only | 13,440 / 46,080 = **29.17%** | **26,880 = 58.33%** | 20,160 stale proofs; 13,440 objective violations | 5.733 |
| objective-first archive | **19,296 = 41.88%** | **0** | preserves valid alternatives | 5.741 |
| early diversity collapse | 13,440 = **29.17%** | **0** | **5,856 valid-objective opportunities lost** | 5.733 |
| fenced fragment parallel | **19,296 = 41.88%** | **0** | 534 beneficial parallel executions; 178 conflicts denied | **5.669** |
| unfenced parallel negative | 19,118 = 41.49% | **178 duplicate-effect scenarios** | 712 parallel executions | 5.660 among safe terminals |

All rates are equal-weight synthetic mechanism coverage, not empirical multi-agent failure frequencies.

## Result 1: objective/proof filtering must precede scalar cost selection

`scalar_cheapest_only` is unsafe in **26,880 / 46,080 = 58.33%** of the lattice. It accepts **20,160** stale proposal proofs and violates the explicit business objective in **13,440** scenarios (these mechanisms can overlap).

The objective-first archive has unsafe count 0 and safe coverage **41.88%**, a **12.71 percentage-point** gain over the scalar baseline's safe coverage. The gain comes from retaining a non-cheapest proposal that remains current and objective-compatible when the cheapest proposal is not.

The generic ordering is therefore:

`objective/version currentness + proof validity + behavior compatibility -> safe candidate set -> cost/latency selection`

not `global cheapest -> try to justify afterward`.

## Result 2: early collapse can be safe but unnecessarily block useful work

The early-collapse negative control never executes a stale/disallowed retained proposal, so its unsafe count is 0. But it loses a still-valid objective solution in **5,856 / 46,080 = 12.71%** of scenarios because the one retained proposal is stale/disallowed while another independently generated proposal would pass the current gates.

This is a different failure class from unsafe execution: **premature convergence reduces safe feasible-objective coverage**. The role's QD bias is therefore useful operationally even when every execution remains conservative — behavior/proof diversity preserves fallback options after objective/version changes.

## Result 3: parallel recovery is a conditional optimization, not the default

The model contains **712** scenarios where current `F` and `R` fragments are objective-compatible, composable, and strictly faster as a parallel composition than the selected whole proposal. `fragment_parallel_fenced` executes **534** of them.

It denies **178** candidates because the two fragments share an exclusive effect key and no reservation/fence exists. The unfenced negative policy runs all 712 and produces **178 / 178 duplicate authoritative effects** in exactly that shared-key/no-reservation slice.

Thus the parallelization rule is stricter than “both fragments are individually safe”:

- both proofs current;
- fragment merge/composition contract valid;
- objective permits the combined disposition;
- parallel latency is actually better;
- **exclusive effect/compensation keys are disjoint or atomically reserved/fenced**.

If any gate fails, use the whole objective-safe proposal sequentially rather than losing business coverage.

## Result 4: safe parallelism slightly improves latency without changing safe coverage

Objective-first whole-proposal selection and fenced fragment parallelism both cover **19,296** safe terminal scenarios. The latency proxy falls from **5.7413** to **5.6688** under the fenced parallel policy because it parallelizes only the 534 cases where the synthetic latency profile is strictly beneficial.

The unfenced policy looks slightly faster (5.6600 among safe terminals) only because it also attempts the 178 conflicted cases and those cases are excluded from its safe-latency average after becoming unsafe. This is another reason latency should not be compared without the safety/coverage denominator.

## Current candidate multi-agent recovery protocol

1. Independent proposal workers write immutable proposal artifacts only; they do not mutate authoritative effects directly.
2. Every proposal binds `{parent/objective version, behavior disposition, required proof digests, effect/compensation key set, estimated action/latency/exposure descriptors}`.
3. The current integrator first filters proposals by exact parent/objective version, proof currentness, and objective-compatible behavior.
4. Keep a behavior-indexed archive of remaining safe proposals; scalar costs rank **within** that safe/objective set rather than deleting other behavior niches globally.
5. Fragment-level parallel execution is optional and requires deterministic composition plus disjoint exclusive effect keys or one atomic reservation/fencing transaction covering the union.
6. If conflict-free parallel execution is not strictly beneficial under the current latency/cost model, execute the chosen whole proposal; do not parallelize merely because multiple workers exist.
7. After any parent objective/version change, old proposal proofs are revalidated or rejected; cost rank does not preserve authority.

## Scope limits

- Finite synthetic lattice only.
- The early-collapse mechanism models loss from pre-filter convergence; it does not empirically estimate communication/critique effects in real multi-agent systems.
- Latency values are ordinal synthetic proxies, not wall-clock measurements.
- Only a two-fragment `F+R` composition is modeled. Three-way fragment scheduling and partial merge failure remain untested.
- Reservation/fencing is treated as an exact capability when present; acquisition conflict/expiry during the parallel plan remains a separate leaf.

## Exact Phase-1 continuation

Continue with **proposal proof-digest invalidation and reservation lifetime during parallel recovery**.

Next finite grammar:

- proposal created under parent/objective version V1 then parent moves to V2 before fragment reservation/execution;
- evidence/proof digest changes without objective text changing;
- reservation obtained before proof recheck vs after proof recheck;
- reservation expires between fragment A and B;
- stale fragment finishes after integrator takeover;
- partial parallel completion with one irreversible effect already issued;
- compare pre-reserve-only proof, proof-before-reserve, reserve-then-final-revalidate, per-fragment currentness fence, and immutable stage + current integrator publication;
- measure stale proposal execution, duplicate effect, objective-version violation, reservation leakage, partial irreversible exposure, safe recovery coverage, and latency/action overhead.

Keep the behavior archive intact across revalidation and preserve a nonempty Phase-1 frontier afterward.
