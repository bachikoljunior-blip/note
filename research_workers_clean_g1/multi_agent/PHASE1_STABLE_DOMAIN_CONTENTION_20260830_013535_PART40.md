# Phase-1 multi_agent checkpoint — stable conflict-domain contention design (Part 40)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_DYNAMIC_DOMAIN_TAKEOVER_20260830_013535_PART39.md`

Part 39 showed that dynamic local remapping is not safely added by a separate topology-version read. This leaf therefore asks a narrower question: if correctness domains are stable, how much locality can a scheduled-Chat repository protocol retain while guaranteeing that every pair of overlapping multi-effect tasks actually collides on authoritative state?

Executable model: `research_workers_clean_g1/multi_agent/phase1_stable_domain_contention_20260830_part40.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_stable_domain_contention_20260830_part40.json`

The model uses six canonical effects and a stable three-way partition `{0,1}`, `{2,3}`, `{4,5}`. It evaluates two finite task families:

- **arbitrary family:** all 41 nonempty sets of size 1–3 (`820` task pairs; `570` overlapping, `250` disjoint);
- **locality-biased family:** 15 tasks consisting of six singletons, three within-partition pairs and six selected cross-partition pairs (`105` pairs; `36` overlapping, `69` disjoint).

Counts are mechanism counts, not production probabilities.

## Result 1 — a one-manifest anchor cannot preserve arbitrary intersection conflicts without collapsing to one component

For the arbitrary family, the graph whose vertices are task effect sets and whose edges connect any two sets with nonempty intersection has **one connected component containing all 41 tasks**.

That gives a useful finite proof obligation: if a strategy assigns each task to exactly one authority object and requires *every overlapping pair* to choose the same object, then equality propagates along every overlap edge. Because the overlap graph is connected, all 41 tasks must ultimately map to one authority object. For this unrestricted family, perfect collision completeness plus exactly-one-object-per-task implies a global domain.

The tested anchor heuristics demonstrate the failure mode:

| strategy | unsafe overlapping pairs | false exclusions on disjoint pairs | max tasks on one domain |
| --- | ---: | ---: | ---: |
| min-effect anchor | 367 / 570 | 0 / 250 | 16 |
| hash(effect-set) | 493 / 570 | 44 / 250 | 8 |
| rendezvous bucket | 391 / 570 | 83 / 250 | 15 |
| one global manifest | **0 / 570** | **250 / 250** | 41 |

Hashing balances load but does not solve semantic intersection. Two sets can overlap while their chosen anchors/buckets differ.

This is scoped to arbitrary effect sets and one authority object per task. It does not rule out locality when the task family is restricted, when a task can atomically touch several authority objects, or when wide tasks use a different publication path.

## Result 2 — stable partitions are safe only if cross-partition work is rejected or escalated

A fixed partition can safely admit work whose whole effect set lies within one partition. In the arbitrary family it accepts 9 tasks and fail-closes 32 wide tasks, with unsafe overlap `0` and only 3 false-exclusion pairs among accepted local work.

The same scheme in the locality-biased family accepts 9/15 tasks and blocks 6 wide tasks, again with unsafe overlap `0` and 3 local false exclusions.

This is a real safety/locality improvement, but fail-closing wide work is not full useful-outcome parity. The wide cases therefore remain unresolved unless another zero-dependency publication mechanism can handle them.

## Result 3 — a hybrid local-manifest + wide Git-ref path is safe in the tested cooperative branch model

The hybrid strategy is:

- single-partition task: use the Part 38 PREPARED/APPLIED local manifest for that stable partition;
- cross-partition task: create immutable stages and a proposal commit that atomically updates *every touched local manifest* plus the wide transition identity, then publish with `update_ref(force=false)` and reconcile lost responses by ancestry/transition ID.

Because a wide commit changes every local manifest it overlaps, any local worker holding an older file SHA fails its later CAS after the wide commit publishes. If a local commit wins first, the wide non-force ref update is no longer a fast-forward from its old base and must retry. Thus the branch ref supplies the multi-manifest publication fence only for wide work.

In both finite families this hybrid has **0 unsafe overlapping pairs**. Its cost depends strongly on how common wide work is:

- arbitrary family: 32/41 tasks are wide; false exclusion is 223/250 disjoint pairs, close to the global-ref worst case;
- locality-biased family: 6/15 tasks are wide; false exclusion falls to **42/69**, versus 69/69 for always-global publication.

So the hybrid is not a universal contention cure, but it has a clear workload-sensitive Pareto region: local tasks avoid branch-wide contention, while wide tasks pay the global publication cost needed to touch several manifests atomically under the exposed primitives.

GitHub's tree/commit/ref APIs and `force=false` fast-forward rule remain the public repository mechanism:
- https://docs.github.com/en/rest/git/trees
- https://docs.github.com/en/rest/git/refs

## Result 4 — effect-set identity is part of the claim, not metadata

A local task can become wide if its effect contract drifts after PREPARED. The model includes 36 local-to-cross-partition drift cases. A weak protocol that finalizes the old local manifest without binding the effect-set digest is **36/36 unsafe**. Binding the canonical effect-set/contract digest into PREPARED causes all 36 to fail/replan rather than publish under the wrong domain.

Likewise, reusable domain names are not sufficient authority identity. In three modeled delete/recreate cases, reusing the same domain ID/epoch namespace permits **3/3 ABA failures**; incarnation-sensitive domain IDs reduce that slice to 0.

For 15 modeled lost-response publication cases, blind retry produces 15 duplicate logical attempts, while durable `transition_id`/applied-state reconciliation resolves 15/15 without retrying the authoritative effect.

## Phase-1 zero-dependency / zero-quota assessment

Within the tested **stable partition + no-complete-rewind + cooperative non-force branch writer** scope:

- local PREPARED/APPLIED manifest publication remains zero incremental cost, zero finite monthly/trial/paid quota, and has no richer-mode/manual/protected execution dependency;
- wide Git tree/commit/ref publication uses the same lightweight repository transport and has the same acceptance assessment;
- no external hosted coordinator or background executor is introduced.

The hybrid does not solve direct fixed-path consumer parity from Part 38, complete same-domain rewind from Part 36, or arbitrary external sinks that cannot validate authority/idempotency. It also does not make an unavailable multi-ref connector mutation part of the accepted path.

## Exact continuation

Next Phase-1 leaf: **wide-operation admission and fairness under a full recurring pool**.

Stress the hybrid where many local tasks continuously advance unrelated manifests while a wide operation repeatedly loses its branch-base race. Compare:

- immediate retry from newest base;
- bounded retry then fail-closed checkpoint;
- deterministic wide-operation priority ticket stored in one repository authority object;
- quiescence request that local manifests must honor before new PREPARED admissions;
- branch-ref-only serialization;
- global manifest serialization.

Required negatives: local workers that read a separate quiescence flag then CAS their local manifest (TOCTOU), abandoned priority tickets, takeover of a stalled wide owner, rate-limit interruption during the quiescence window, and response-loss after wide publication. Measure starvation/livelock, false exclusion, stale admission and whether a priority/quiescence protocol secretly reintroduces a global per-operation hotspot.
