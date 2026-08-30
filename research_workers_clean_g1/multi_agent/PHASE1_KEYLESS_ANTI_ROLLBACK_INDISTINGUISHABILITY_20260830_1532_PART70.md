# Phase-1 multi_agent Part 70 — keyless anti-rollback indistinguishability

## Frozen authority
- DESIRED_STATE: control_revision 26, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- multi_agent config: config_revision 8 / control_revision 11, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- preferred transport: SHA-only main ref + exact-SHA reads; frozen main `2fa6d2f5b12f381d491168121c4b8ccd906344ea`
- assignment: `phase1-clean-multi-agent-concurrency-claims`

## One bounded leaf
Question: can a scheduled-Chat worker, using only the repository rollback domain and no protected secret/manual/external monotonic authority, distinguish a history that never advanced beyond generation g3 from a history that advanced to g4 and was then fully force-rewound/restored so all currently observable repository + worker-own durable state is byte-identical to the g3 history?

Paired histories:
- H0: repository authority reaches state S(g3) and never advances.
- H1: S(g3) -> S(g4) -> full authority-domain rollback/restore -> S(g3), including rollback/loss of worker-owned generation witness and any repository-resident floor/key/grant state.
- Final observation vector O is defined to be identical in H0 and H1: current ref, current reachable tree/blob set used by the protocol, role-local state, repository-resident signing metadata/key state, and compact generation-floor path.

Mechanisms compared:
1. Current-ref / commit-ancestry monotonicity.
2. Separate compact generation-floor record in another repository path but the same rollback domain.
3. Repository-resident signed metadata plus repository-resident verification/key epoch state.
4. Fail-closed detection based only on the final repository/own-state observation vector.

## Result
All four mechanisms fail to distinguish H0 from H1 under the stated full-rollback scope. The reason is structural, not probabilistic: any decision procedure whose complete input is O receives the same input in both histories, so it must produce the same result (or the same output distribution if randomized). Therefore it cannot both accept legitimate H0(g3) and reject rolled-back H1(g3) solely from same-domain current state.

Specific mechanism notes:
- GitHub's REST ref update API explicitly permits a forced ref update when `force=true`; with `force=false` it enforces fast-forward behavior. Thus commit ancestry is a useful fence only while non-fast-forward rollback is excluded by the authority contract; it is not an anti-rollback witness once the ref itself may be force-rewound. Public source: https://docs.github.com/en/rest/git/refs#update-a-reference
- GitHub's Contents update requires the current blob `sha` for an existing file. That is a current-version CAS guard, but a floor file in the same ref/tree rollback domain can be restored along with the authority object, so it does not distinguish H0/H1 after complete rollback. Public source: https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents
- A repository-resident signature proves authenticity relative to the restored key state, not freshness relative to an erased g4 history. If both signed metadata and its trust/floor state are rolled back together, the final verification input is identical.
- Pure fail-closed detection cannot selectively fail only H1 because H0 and H1 expose the same final observation. Failing both is safe but destroys the useful g3 case and therefore is not parity.

## Scope and non-generalization
This is an impossibility result only for the deliberately strong `rollback-complete` model: every worker-visible durable witness that could encode the advance is inside the same rollback domain and is restored/lost together. It does **not** say repository CAS is useless; Part 69's scoped positive remains valid when force-rewind/ABA of the authority domain is excluded and sender identity is not required. It also does not rule out a monotonic witness that is genuinely outside the rollback domain or an authority configuration that makes non-fast-forward rollback impossible; those are separate leaves and must satisfy the Phase-1 no-protected/manual/external/quota/cost constraints.

## Zero-dependency / zero-quota assessment
- incremental monetary cost: 0
- finite monthly/trial/paid quota dependency added: none
- richer-mode / protected-primary / manual-user execution accepted: none
- external hosted coordinator accepted: none
- repository API is transport/evidence only; it is not used as compute
- unresolved child: a zero-cost scheduled-Chat-native way to exclude or witness full authority-domain rollback without protected secret custody, manual configuration, finite quota, external monotonic authority, or a witness that rolls back with the repository

## Exact continuation
Execute exactly one bounded non-conflicting leaf on **rollback-prevention rather than rollback-detection** for the single repository authority object. Compare (a) non-force ref-only publication, (b) immutable/tag-like publication identities, (c) branch/ruleset protection or equivalent repository policy, and (d) two-object CAS with a monotonic pointer, under an adversary that has the same write authority as scheduled Chat. Classify which mechanisms actually make H1 unreachable versus merely make ordinary worker writes fast-forward/CAS-safe, and reject any route that requires protected administrator/manual configuration, external hosted coordination, finite quota, or incremental cost. Preserve Part 69/70 scope and keep Phase 1 open.
