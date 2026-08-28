# Phase 1 follow-up — dynamic selection boundary and consolidated acceptance table

Status: role-local Phase-1 continuation under frozen semantic tuple `4632516483a5fb873c0ebc4b1709cb8505a9271a` / control rev 16 / reasoning config rev 6. This follows the fixed-cohort fairness checkpoint. No post-freeze repository semantics were adopted.

## Dynamic-selection result

The durable wait-credit rule extends farther than the fixed-graph result: **conflict edges may change arbitrarily between epochs without destroying first-service liveness**, provided the fairness identity/order assumptions do not inject new actions ahead of a continuously waiting action.

For a continuously eligible target `v` in a fixed hard-priority class, define its current ordering position by `(credit, stable_key)`. If `v` is not selected in an epoch, greedy maximality implies some earlier selected action conflicts with it. That blocker resets its credit to zero. While `v` remains unselected its credit increases every epoch, so the same blocker cannot get ahead of and block `v` again before `v` is served. Arbitrary changes in the conflict edge itself do not alter that credit argument.

Therefore let `Ahead(v,t0)` be the finite set of same-hard-class fairness keys that, at the start of the interval, have greater credit than `v`, or equal credit and a stable key preceding `v`. If during the interval:

1. `v` remains eligible and in the same hard class;
2. newly eligible keys enter with credit zero;
3. no fairness migration clones/injects positive credit into additional keys ahead of `v`;
4. each selected blocker resets credit to zero;
5. higher-hard-class conflicts block `v` at most `H` epochs;

then `v` is selected within at most `|Ahead(v,t0)| + H + 1` relevant epochs. In a fresh all-zero fixed cohort of size `n` and no higher-class blocking, this reduces to the previous `<= n` first-service bound.

### Dynamic edge exhaustive model

Companion artifact: `research_workers_clean_g1/reasoning/2026-08-28T2225JST_phase1_dynamic_fairness_properties.py`.

The model exhaustively branches over **every possible conflict graph at every epoch** for fixed continuously eligible cohorts of size `n <= 5`, merging equivalent `(credits, ever_served)` states. It evaluates **913,527 scheduler transitions** total:

- n=1: 1 transition, reachable states `[1]`;
- n=2: 6 transitions, states `[2,3]`;
- n=3: 112 transitions, states `[4,9,14]`;
- n=4: 6,144 transitions, states `[8,27,60,96]`;
- n=5: 907,264 transitions, states `[16,81,248,540,886]`.

After epoch `n`, every reachable state has served every vertex at least once. No conflict-edge schedule within the enumerated model violates the first-service bound. This verifies the dynamic-edge part only; arrivals, hard-class changes and fairness-key migrations are covered by explicit conditions rather than exhaustive enumeration.

## Arrival/departure rules

- New same-class fairness key starts at credit zero. It cannot jump ahead of a target that has already accumulated positive waiting credit.
- An action that becomes ineligible loses its continuous-eligibility claim; on re-entry it starts a new age interval at zero unless an exact policy explicitly defines another safe rule.
- Infinite arrivals do not by themselves starve an already positive-credit target if arrivals start at zero, but a same-epoch unbounded cohort is outside the finite-action assumption and must report `LIVENESS_UNPROVEN_DYNAMIC_SET`.
- Hard-priority changes are semantic policy events. If a target can be preempted by an unbounded stream of higher-class conflicts, no same-class fairness rule can prove service. Report the bounded higher-class interference assumption (`H`) or leave liveness unproven.

## Fairness-key migration rules

Fairness identity is stateful and must not be guessed.

1. exact one-to-one semantic rename with proof: carry credit to renamed key;
2. many-to-one proven merge: carry `max(predecessor_credit)` so longest legitimate wait is not erased and no extra key is created;
3. one-to-many split: new children start at zero unless a separately proven entitlement-allocation rule is preregistered; copying one positive credit into many children is forbidden credit cloning;
4. ambiguous mapping: reset affected keys in a new fairness epoch and record `FAIRNESS_EPOCH_RESET(migration_ambiguous)`;
5. every reset weakens historical liveness; repeated resets are surfaced, never hidden by timestamps.

## Consolidated Phase-1 acceptance table

| Invariant | Positive acceptance evidence | Counterexample / trigger | Fail-closed response | Recovery evidence |
| --- | --- | --- | --- | --- |
| FROZEN_CONFIG | all semantic artifacts cite one frozen SHA/control/config tuple | post-freeze control/head drift | do not reinterpret current invocation | next clean bootstrap reads new tuple |
| ROLE_BOUNDARY | provenance contains only own clean state/public/root/own config | O/peer/downstream/legacy semantic payload encountered | quarantine/discard; stop dependent semantic path | clean re-read from allowed source |
| LATEST_OR_AMBIGUOUS | causal valid heads reconcile uniquely/compatibly | stale pointer, incomparable conflicting heads | reconstruct DAG; return explicit ambiguity | valid predecessor/migration/resolver evidence |
| PROVENANCE | every adopted checkpoint reaches verified allowed root/predecessor | missing predecessor/digest mismatch | `INVALID_PROVENANCE` | predecessor restored or valid independent-root contract |
| POLICY_COMPATIBILITY | exact same semantics or bound migration proof | policy/config revisions alter eligibility/effects | `AMBIGUOUS_POLICY` | exact migration/equivalence proof |
| TASK_DISJOINTNESS | selected set has no explicit conflict edge | write/write, write/read, exclusive resource, ownership-generation conflict | do not co-select | conflict removed or proof of commutativity/equivalence |
| SELECTION_MAXIMALITY | every unselected eligible action has selected conflict witness | eligible unselected action with no witness | scheduler contract failure | deterministic reselection from canonical set |
| REPEATED_RUN_LIVENESS | durable credits, stable fairness keys, bounded hard interference | recurring fixed priority/starvation, fairness reset, credit injection | no fairness claim; reset epoch if metadata invalid | stable credits/keys and explicit liveness assumptions |
| DIRECT_FIRST | direct attempt returns solved or explicit blockers before decomposition | decomposition proposed from START/timeout only | reject decomposition; retry direct or checkpoint | blocker witness |
| TRANSVERSAL_TRIGGER | forecast exceeded and emitted hitting set covers every blocker minimally | branch proliferation without frozen forecast/blockers | preserve branches; build blocker hypergraph | verified blockers + minimal transversal |
| DURABLE_CHECKPOINT | immutable checkpoint exact-readback/digest verified | create failure/digest contradiction | no semantic publication claim | successful exact verify |
| POINTER_CAS | update uses preread expected blob/version | current pointer differs | preserve checkpoint; never stale-overwrite | reconstruct and fresh guarded promotion |
| POSTREAD_TRUTH | receipt records actual pointer observed after CAS | CAS success but pointer superseded before receipt | record promoted/superseded facts separately | postread value/version |
| RECEIPT_AFTER_VERIFY | receipt after checkpoint verify + pointer postread | terminal receipt attempted earlier | refuse terminal receipt | verified artifact + postread |
| HANDOFF_CAS | owner changes only source,g -> target,g+1 exact CAS | duplicate/foreign/stale handoff | exact duplicate idempotent only; otherwise reconstruct | exact durable owner tuple |
| FENCING | protected effect validates current owner generation | lease-only lock or stale source local ACTIVE cache | refuse exclusive external effect | resource-side generation/version validation |
| NO_FALSE_COMPLETION | hard stop produces checkpoint + nonempty continuation | runtime boundary treated as parent success | record invocation termination only | next run resumes unresolved frontier |

## Phase-1 reasoning status

The reasoning assignment now has a deterministic architecture, explicit proof obligations, negative-path recovery rules, and finite executable models for state reconciliation, conflict-safe action selection, direct-first transitions, blocker transversals, pointer CAS, handoff races/crashes, checkpoint-publication crashes, causal DAG reconstruction, fixed-graph fairness, and arbitrary dynamic conflict edges.

The remaining irreducible external dependency is unchanged:

`XROLE_OWNERSHIP_SURFACE` — global cross-role non-conflict/exclusive handoff requires an authorized shared transactional ownership/claim primitive with fencing. Clean role-local evidence cannot prove or execute that global condition, so cross-role handoff must remain advisory here.

## Exact next Phase-1 action

Perform a final **architecture composition audit**: verify that the individual contracts compose without circular authority. In particular:

1. latest-state reconstruction must not depend on `LATEST` or receipt truth that itself depends on unreconstructed state;
2. task selection/fairness must consume only reconstructed semantic state plus independently validated scheduling metadata;
3. direct/decomposition state transitions must checkpoint through the crash-safe publication contract;
4. handoff ownership must be an external authoritative primitive rather than inferred from role-local scheduler state;
5. produce a dependency DAG/topological order of proof obligations and identify any cycle or missing primitive.

If no internal cycle exists, checkpoint the reasoning Phase-1 assignment as **locally architecture-complete but globally handoff-dependent**, preserve the nonempty generic Phase-1 frontier required by control, and continue to the next unresolved generic reasoning leaf rather than restoring the base research frontier.

Keep `2026-08-28T1807JST_budget_conditioned_joint_value.md` as base restoration metadata only while Phase 1 remains active.

Termination for this leaf: dynamic selection boundary and consolidated acceptance table completed; Phase-1 parent remains open with the composition audit above.
