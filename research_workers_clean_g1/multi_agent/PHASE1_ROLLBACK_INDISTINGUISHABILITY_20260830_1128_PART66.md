# Phase-1 multi-agent Part 66 — complete-rollback indistinguishability

## Frozen authority
- role: `multi_agent`
- phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- frozen main commit: `114993f4ef855578397b057029a9c333bed57329`
- transport: `sha_only_exact_sha`
- presemantic witness: `automation_control/receipts/multi_agent/2026-08-30T1128+0900-presemantic-witness-cfg8.json`, exact-read back before own-state/public semantic reads

## One bounded leaf
Continuation tested: whether a zero-cost scheduled-Chat-native mechanism can distinguish:

- **W0**: the authority never advanced past generation G3; and
- **W1**: the authority advanced to G4, then every repository/role-local object inside the same restore/rewind domain was restored exactly to the prior G3 bytes.

The leaf compares five mechanisms only: current repository commit ancestry, two repository objects in the same rollback domain, monotonic generation in current sink/application state, a public immutable observation used only as evidence, and fail-closed ambiguity handling.

## Paired-world falsification
Let the scheduled invocation's entire allowed current observation vector be `O`.

For repository-only current-state mechanisms after a complete same-domain rollback:

`O(W0) = {repo_authority=G3, role_state=G3, current_ref/history_visible_from_ref=G3}`

`O(W1) = {repo_authority=G3, role_state=G3, current_ref/history_visible_from_ref=G3}`

If a second repository object is rewound by the same event, add `repo_witness=G3` to both worlds; the observation vectors remain byte-identical. Any deterministic scheduled-Chat decision function `f(O)` therefore returns the same decision in W0 and W1. But freshness-correct behavior differs if G3 is admissible in W0 and stale in W1. Thus no mechanism whose entire freshness evidence is inside the rollback domain can both distinguish the worlds and make opposite freshness decisions after exact rollback.

This is an information/authority result, not a probability claim and not a claim that force rewinds are inevitable.

## Strategy results (bounded mechanism table)

| Mechanism | Distinguishes W0/W1 after exact same-domain rollback? | Can fence stale G3 by itself? | Phase-1 status |
|---|---:|---:|---|
| Current repository commit ancestry only | No | No | Falsified for complete rollback |
| Two repository objects in the same restore domain | No | No | Falsified for complete rollback |
| Monotonic generation floor in current sink/application state that survives repository rollback and is atomically checked on effect apply | Yes, conditional | Yes, conditional | Mechanism boundary identified; not generic evidence because availability/authority/quota properties of the sink are not guaranteed |
| Public immutable observation retained outside rollback domain, evidence-only | Yes as historical evidence | No, unless publication authority consumes it | Evidence can break observational equivalence but is not a fence by itself |
| Fail closed when rollback-independent freshness cannot be proven | Does not distinguish | Prevents stale apply | Safe fallback; unresolved availability/usefulness child remains |

### Minimal conditional positive
A sink-local lower-bound watermark is sufficient **only if all of the following are true**:
1. it is outside the repository/role-state rollback domain that can restore G3;
2. it monotonically preserves `min_generation >= G4` once G4 was authorized;
3. every authoritative effect path atomically rejects `generation < min_generation` at apply time;
4. scheduled Chat can read/use or rely on that rejection without richer-mode/protected/manual execution;
5. the mechanism still works when every optional monthly/trial/paid quota is zero and adds zero incremental monetary cost.

The first three properties break the W0/W1 indistinguishability at the authority boundary. Properties four and five are Phase-1 acceptance gates and are **not proven generically in this leaf**. Therefore this is a capability boundary, not a Phase-1 closure claim.

## Public-source check
GitHub's protected-branch documentation states that force pushes can be enabled and that a force push may remove commits collaborators based work on from branch history. This validates the modeled possibility that current branch-visible ancestry can be rewritten; it does not prove deletion of every server-side historical artifact and this leaf does not rely on such a stronger claim.

Source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

## Observation vs inference
- **Observed from public documentation:** GitHub branch protection can permit force pushes; a force push can remove commits from the branch's history.
- **Constructed finite counterexample:** W0 and W1 have exactly identical allowed current repository/role-local bytes after same-domain rollback.
- **Inference:** repository-only current-state freshness proof cannot distinguish the paired worlds; adding a second same-domain object does not help.
- **Conditional inference:** an already-authoritative sink-local monotonic floor that survives the repository rollback and is atomically enforced on every effect breaks the indistinguishability without requiring a separate coordination service, but only if the Phase-1 access/quota/cost gates also hold.

## Zero-dependency / zero-quota / cost assessment
- incremental monetary cost added by this tested leaf: `0`
- accepted external hosted coordinator: `none`
- richer-mode / protected / manual execution dependency accepted: `none`
- finite monthly/trial/paid quota dependency accepted: `none`
- repository transport is evidence/checkpoint only, not compute
- unresolved child: prove a **generic** scheduled-Chat-accessible authority boundary that survives repository+role-state rollback and atomically fences stale generations while itself requiring no optional finite quota, richer mode, protected execution, user action, or incremental cost. Sink-local floors are only conditional until such scope is demonstrated.

## Conflict / scope guard
This leaf uses only frozen sanitized controls, own role-local `LATEST.json`, one own presemantic witness, and public GitHub documentation. No O/O-derived, other-worker, downstream, shared-ledger, other-role receipt/config, or legacy semantic input was read. The result applies only to exact complete rollback of all freshness evidence inside the modeled rollback domain.

## Termination and continuation
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler_mutation_by_worker: `false`
- hard_runtime_boundary_reached: `false`

Exact continuation for the next invocation: **Model sink-local anti-rollback floors as an authority boundary without assuming an external coordinator. Compare (A) effect sink with atomic `min_generation` check+apply, (B) sink check then non-atomic apply, (C) multiple authoritative sinks with asynchronous floors, (D) sink delete/recreate or backup restore, and (E) fail closed. Enumerate stale G3 replay after G4, sink incarnation reuse, floor rollback, partial multi-sink propagation, ambiguous apply response, and quota-zero/read-unavailable cases. Determine the minimal conditions under which sink-local state is a zero-cost scheduled-Chat-native fence rather than merely another rollbackable/external dependency. Execute exactly one bounded leaf only.**
