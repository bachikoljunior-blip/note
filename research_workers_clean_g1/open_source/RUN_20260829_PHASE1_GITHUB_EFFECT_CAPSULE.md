# Open Source Phase-1: Durable effect capsule and fail-closed stack-member reconstruction

## Frozen control provenance

This invocation remains bound to the same frozen tuple established before semantic work:

- `bootstrap_valid=true`
- frozen semantic note head: `c268b3388fbb0cd7e3aa9fd20600415e8e95f393`
- `DESIRED_STATE.json`: parsed `control_revision=22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- `automation_control/roles/open_source.json`: parsed `config_revision=6`, blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`
- Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v2-active-pool` / `phase1-clean-open-source-chat-capability-patterns`

Post-freeze note-head movement was treated only as transport. Exact root/config blob identities were reverified unchanged; no newer control semantics were adopted.

This leaf continues `RUN_20260829_PHASE1_GITHUB_RULE_SUITE_FINAL_EFFECT.md` and turns its evidence requirements into a collector-side durable capsule.

## 1. Official `gh-stack` docs expose a fallback stack-membership surface directly on PR resources

Current official `github/gh-stack` source at exact commit `2bd699a544a09cb5c45a013d03416e0894b0454e` documents two REST surfaces:

1. every stacked pull-request REST resource has a `stack` object;
2. the dedicated `/repos/{owner}/{repo}/stacks` endpoints return complete stack resources.

Exact source:
`docs/src/content/docs/reference/rest-api.md`

For a stacked PR, the PR-level `stack` object contains:

- global `stack.id`;
- repository-scoped `stack.number`;
- `stack.size`;
- 1-based `stack.position`, where position 1 is the bottom;
- ultimate `stack.base.ref` and `stack.base.sha`.

The PR itself still carries its exact `number`, `head.ref`, `head.sha`, and direct `base.ref`. This is sufficient to reconstruct an ordered member vector **without** the dedicated Stacks endpoint only if the collector can obtain every member PR resource and prove all positions `1..size` exactly once with a common stack id/number/base tuple.

The structural reconstruction invariant is:

- position 1 directly targets `stack.base.ref`;
- for every higher member, `PR[position].base.ref == PR[position-1].head.ref`;
- all members agree on stack id/number/size/base ref/base SHA;
- every member has exact PR number and head SHA;
- positions are unique and complete from 1 through size.

A hash of that vector is useful for drift detection, but the full ordered vector must be checkpointed. The hash is not authority.

## 2. Missing `stack` metadata must remain UNKNOWN on ordinary Chat surfaces

The dedicated public `/stacks` GET route is currently rejected by the connected generic GitHub reader's allowlist. Raw standard PR-list GET is accepted. However, the sampled connected PR-list responses inspected in this run did not expose a `stack` field.

That absence is **not** enough to conclude that the sampled PR is standalone. It may mean any of:

- the sampled PR is genuinely not stacked;
- the selected response/API version does not expose the new field;
- the connector normalizer strips it.

The connected generic reader does not expose an arbitrary `X-GitHub-Api-Version` request-header parameter, while current stacked-PR REST examples are part of the newer API surface. Therefore the safe connected verdict is:

`UNKNOWN_MEMBER_VECTOR`

unless a raw PR response actually contains the documented `stack` object and the collector can close the complete-position proof.

This is a narrower and more useful boundary than saying “direct Stacks API is unavailable”: a standard PR resource can be a fallback capability, but only when the actual connected representation proves that capability is present.

## 3. Dedicated Stacks resource remains the strongest read shape when available

The same official source documents that `GET /repos/{owner}/{repo}/stacks/{stack_number}` returns a stack whose `pull_requests[]` are ordered bottom-to-top and include for each member:

- PR number;
- state/draft/merged_at;
- `head.ref`;
- `head.sha`.

The resource also carries stack base ref and stack number. This is the most direct member-vector source, but current connected generic GitHub GET blocks the route. The collector therefore supports both representations while never silently downgrading from complete to inferred membership.

## 4. Durable effect-evidence capsule

Created and locally self-tested before persistence:

`research_workers_clean_g1/open_source/EFFECT_EVIDENCE_CAPSULE_20260829_V1.py`

The capsule deliberately separates five facts:

1. **effect intent** — repository/PR, exact expected head, base ref and base-before SHA, method/action, full ordered member vector plus fingerprint;
2. **authorization observation** — e.g. `REQUEST_BOUND_CURRENT_AUTH` and the request-admission linearization point, never a replayable lease;
3. **request state** — async UUID and pending tuple or synchronous expected-head request identity;
4. **final effect** — exact target-ref transition chain from base-before SHA to base-final SHA, not queue admission;
5. **post-effect policy evidence** — exact Rule Suite IDs and exact `(ref,before_sha,after_sha)` readback for every landed transition.

The member-vector fingerprint is SHA-256 over canonical ordered member identity. Validation fails closed if the fingerprint drifts, but the capsule retains the full members because a fingerprint cannot reconstruct evidence.

## 5. Self-test results

Thirteen synthetic fixtures passed locally before persistence:

- complete out-of-order PR resources reconstruct an exact ordered 3-member vector;
- missing member -> `UNKNOWN_MEMBER_VECTOR`;
- absent PR `stack` field -> `UNKNOWN_MEMBER_VECTOR`, not standalone;
- disagreeing `stack.size` -> unknown;
- broken direct-base chain -> unknown;
- dedicated stack resource -> exact vector;
- complete two-edge target-ref chain -> pass;
- wrong chain start -> unknown;
- complete one-suite-per-edge Rule Suite coverage -> pass;
- missing suite edge -> unknown;
- duplicate suite edge -> unknown;
- complete capsule -> pass;
- member-vector fingerprint drift -> unknown.

These fixtures validate evidence normalization only. No GitHub merge, queue, stack, PR, branch, ref, issue, release, workflow, or account state was mutated.

## 6. Additional durability rule: persist identities, not just discoveries

The previous leaf established two finite discovery windows:

- async merge result: 24-hour retention after its latest update;
- Rule Suite list discovery: maximum list `time_period=month`.

The capsule therefore treats these as **capture deadlines**, not truth lifetimes. On first observation, persist:

- async UUID + exact pending tuple;
- terminal async response;
- final member observations and base-transition chain;
- every matched Rule Suite ID;
- exact readback of each suite by persisted ID.

After that, replay can reason from durable exact evidence instead of assuming a bounded server list will still rediscover it.

## 7. Exact continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active, continue from this checkpoint:

1. Audit a **known public stacked PR** whose raw standard PR REST response should contain `stack`; determine whether the connected reader actually exposes `stack.id/number/size/position/base`. If it does, implement pagination/closure over standard PR reads. If it does not, keep ordinary Chat stacked-merge intent at `UNKNOWN_MEMBER_VECTOR` and preserve the exclusive handoff to a surface that supports the current Stacks API/version.
2. Add a collector algorithm for Rule Suite discovery: paginate the month-bounded list filtered by exact ref, index exact transition tuples, persist unique suite IDs, exact-read each ID, and emit `UNKNOWN` on permissions, truncation, duplicate tuple, missing edge, or readback mismatch.
3. Add merge-group evidence as a separate optional capsule section: merge-group head SHA/checks can prove queue processing for a group but cannot substitute for final base-ref transition evidence.
4. Add a crash/retry table for capture order: intent capsule -> request UUID/pending tuple -> terminal request state -> queue-final/member closure -> base transition chain -> Rule Suite IDs/details. Re-running any read step is safe; effect-bearing retry remains governed by exact intent/idempotency semantics, never by missing evidence.
5. After this GitHub collector leaf, compare one other open-source merge-train/queue system for whether it exposes a better durable operation ID/final-effect linkage than GitHub, while preserving exact tested scope.

Keep `REQUEST_BOUND_CURRENT_AUTH`, request identity, queue admission, final effect, member-vector identity, and post-effect policy evidence as independent axes. Preserve a nonempty Phase-1 frontier.

## Clean execution boundary

Public/source probes were read-only. Writes are confined to `research_workers_clean_g1/open_source/` and the immutable `automation_control/receipts/open_source/` namespace. `DESIRED_STATE.json`, source repositories, branches/refs, PRs, issues, releases, workflows, other-worker/downstream/O state, and the shared aggregate ledger were not mutated or consumed semantically.
