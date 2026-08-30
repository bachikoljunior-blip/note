# Phase-1 multi_agent Part 74 — server-monotonic repository primitives

## Authority freeze
- role: `multi_agent`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`
- root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- instruction manifest: blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`
- frozen main SHA: `1e8e26ee8ede2c279f27f481cba9335a793a6c6b`
- transport: preferred SHA-only main-ref lookup plus exact-SHA control reads
- bootstrap valid: true

## Selected bounded leaf
Part73 established only a fault-threshold amplification from repository-local witness replication when every accepting witness can be deleted/recreated or exactly rewound in the same rollback domain. This invocation executed exactly one next leaf: compare server-side ref/content mutation primitives and identify the exact operation set, if any, that supplies monotonic freshness without protected branch policy.

Compared mechanisms:
1. REST Git ref update with `force=false`.
2. Client explicit current/ancestry precheck followed by REST ref update with `force=false`.
3. GraphQL `updateRefs` with atomic multi-ref `beforeOid` compares and `force=false`.
4. One co-located authority file updated by ordinary Contents blob-SHA CAS.
5. Create-only path witness.

## Public-source observations
1. GitHub REST Git References documents that ref update takes target `sha`; `force=false` (default) requires a fast-forward update, and the endpoint can return `409 Conflict`. This gives server-enforced ancestry monotonicity for that update operation, but the same public reference family also has create/delete operations, so the update contract alone does not make a ref permanently non-recreatable. Source: https://docs.github.com/en/rest/git/refs (retrieved 2026-08-30).
2. GitHub GraphQL documents `updateRefs` as an atomic multi-ref mutation: all ref updates succeed or none do. Each `RefUpdate.beforeOid` can require the exact old OID; all-zero OID can require nonexistence. `afterOid` all-zero deletes a ref, and `force=true` permits non-fast-forward updates. This is a materially stronger compare-and-publish primitive than client-side precheck for multi-ref transitions, but its own schema also exposes deletion and forced rewrites, so it does not by itself create permanent anti-rollback freshness. Source: https://docs.github.com/en/graphql/reference/git (retrieved 2026-08-30).
3. Current Chat GitHub connector contract exposes role-usable Contents create/update/delete writes; update requires the current blob SHA. In this invocation no ref-write or GraphQL mutation action was exposed by the connector. Therefore the publicly documented ref primitives are mechanism evidence, not an accepted scheduled-Chat execution route in the currently exposed surface.

## Bounded stress grammar
A finite micro-model used 8 adversarial families, each crossed with 4 replay variants `{response observed|lost} × {immediate recovery|stateless restart}`. The same 32 scenario variants were applied to each of the 5 mechanisms, for 160 mechanism-traces total.

Families:
- stale sibling advance before publish;
- a second authority ref/object changes before publish;
- delete + recreate with the same old identity before publish;
- successful publish followed by force-rewind;
- successful publish followed by delete + recreate of the old identity;
- response loss after successful publish while current state still contains the transition identity;
- response loss after successful publish followed by rollback to the old state;
- branch-name/path reuse with a different current identity.

The model assumes a durable deterministic transition/integration identity is available for read-before-retry. A trace is counted as a counterexample when the primitive would be unsafe **if treated as sufficient evidence of current freshness**; a production protocol may instead fail closed.

### Counterexample counts
| mechanism | counterexample traces / 32 | bounded interpretation |
|---|---:|---|
| REST `force=false` | 20/32 | blocks non-fast-forward stale sibling updates, but not same-OID delete/recreate or later force/delete rollback; single-ref only |
| client precheck + REST `force=false` | 20/32 | precheck improves diagnostics but adds no server-side expected-old atomicity; rollback/recreate counterexamples remain |
| GraphQL `updateRefs(beforeOid, force=false)` | 16/32 | exact atomic compare closes the multi-ref TOCTOU family, but same-OID recreate and later force/delete rollback remain |
| co-located Contents blob CAS | 16/32 | exact current-blob compare is strong for one co-located authority object, but same-blob delete/recreate and repository rewind remain |
| create-only path witness | 28/32 | protects only current nonexistence; deletion erases the witness and allows replay/recreation |

The 16/32 result for GraphQL and Contents is not a claim that they are equivalent APIs. It only means the selected failure grammar left each with four unresolved rollback/recreation families. GraphQL uniquely supplies atomic exact-old compare across multiple refs; Contents supplies Chat-exposed CAS only for one file/path authority object.

## Main findings
### F1 — `updateRefs.beforeOid` is the strongest public multi-ref compare primitive found in this leaf
For concurrent multi-agent publication, atomic multi-ref `beforeOid` removes the client-read/TOCTOU gap and prevents partial ref-set publication when any compared ref changed. This directly addresses the prior multi-authority atomicity problem under the exact ref mutation operation.

### F2 — exact expected-old compare is not permanent anti-rollback
If a ref can later be force-rewound, or deleted and recreated at the same old OID, a future stateless invocation can again observe the old OID. `beforeOid == old_oid` then cannot distinguish "never advanced" from "advanced and rolled back to the same OID". The same indistinguishability applies to Contents blob SHA after delete/recreate with identical content and to create-only witnesses after deletion.

### F3 — REST `force=false` has a scoped monotonic positive, not a universal one
Within the restricted operation set where the authority ref already exists, every accepted mutation uses `force=false`, and no actor can delete/recreate or force-rewind that ref, the server contract preserves monotonic ancestry. The smallest unresolved assumption is therefore explicit: **no delete/recreate and no `force=true` for the authority ref outside the accepted protocol**. Without a protected policy or an equivalent non-bypassable server restriction, this assumption is not proven by the ref-update API itself.

### F4 — GraphQL atomicity is currently a missing Chat capability, not an accepted handoff
The public GraphQL primitive is attractive because it can atomically compare multiple refs, including nonexistence via zero OID. But the current Chat connector surface inspected in this invocation exposes Contents writes and read-only generic GitHub fetch, not GraphQL/ref mutations. Requiring a human, richer mode, shell, external runner, or another protected executor to call `updateRefs` would violate Phase-1 acceptance. This is preserved as an unresolved capability child.

### F5 — ambiguous success remains reconcilable only while the transition evidence has not itself been rolled back
With a durable transition OID/integration ID, response loss can be reconciled by reading current state when the transition is still present or is an ancestor of current ref state. If later rollback restores exactly the pre-transition state, a stateless retry cannot prove that the prior transition once succeeded from the current repository state alone. Fail-closed remains safe; blind replay is not justified.

## Zero-dependency / zero-quota / cost assessment
- incremental monetary cost added: 0
- finite monthly/trial/paid quota dependency accepted: no
- hosted runner / Codespaces / artifact/LFS/package / external model dependency accepted: no
- richer-mode/protected/manual-user execution accepted: no
- external hosted coordination accepted: no
- repository transport used for persistence only; no API-volume-as-compute
- unresolved child 1: repository-only anti-rollback freshness when ref/path deletion or force-rewrite remains possible in the same authority domain
- unresolved child 2: atomic GraphQL `updateRefs` is publicly documented but not exposed as a write action in the current Chat GitHub connector surface

## Scope guard
This is a finite mechanism model plus public API/connector-contract audit. It is not a destructive live ref test, not a claim about GitHub administrative security, and not a universal impossibility theorem. The positive REST statement is limited to the explicitly restricted non-delete/non-force operation set. The GraphQL positive is limited to mutation-time atomic exact-old comparison, not permanent freshness.

## Result
`bounded_slice_complete_recurring_open`; global completion=false; Phase-1 completion claimed=false; enabled_desired=true; scheduler mutation=false.

## Exact continuation
Part75: execute exactly one bounded leaf on **server-assigned repository identities outside branch/path rollback state** that may be reachable from scheduled Chat without richer mode: issue/comment/release or other repository object IDs/numbers exposed by the current GitHub connector. Test whether creation is Chat-exposed, whether IDs are documented as non-reused/monotonic or merely unique, delete/recreate behavior, repository transfer/restore/name reuse, ambiguous create response, stale-worker replay, and quota-zero/cost behavior. Accept an anti-rollback anchor only if the server contract makes old authority non-resurrectable without relying on protected/manual execution; otherwise preserve the exact smallest assumption or missing capability and stop after this one leaf.
