# Phase-1 Multi-Agent Part 68 — positive authorization capability transport boundary

## Frozen authority
- role: `multi_agent`
- phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- frozen main SHA: `b9bb725cb238d3032788221cfdadbc45ad715952`
- root: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26
- role config: `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8
- lifecycle: `automation_control/RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- transport: SHA-only main ref + exact-SHA reads; presemantic witness persisted/read back before own-state/public semantic input.

## Question and bounded model
Part 67 showed that a sink-local `min_generation` is only a lower-bound freshness fence: a useful effect boundary needs positive exact/current-generation authorization plus durable effect identity atomically enforced at effect application. This leaf isolates authorization-token transport.

A finite equal-weight lattice enumerated 384 scenarios per token mechanism over seven binary factors and one ternary factor: generation advances after mint; token stolen; effect digest matches; sink incarnation matches; successful apply response is ambiguous; retry occurs; the sink has an atomic current-epoch surface; and expiry state is `valid`, `expired_rejected`, or `expired_but_clock_skew_accepts`. Worker-side current-epoch read access is not assumed; where currentness is checked it is checked by the effect sink at apply time.

Mechanisms compared:
1. signed bearer generation capability;
2. bearer capability + effect ID consumed atomically with apply;
3. generation capability additionally bound to sink incarnation + exact effect digest + single-use effect ID;
4. (3) plus sender-constrained proof and server nonce/replay tracking;
5. (4) plus atomic sink-side `token_generation == current_generation` check;
6. fail-closed when the atomic current-epoch surface is unavailable;
7. a repository-only special case: co-locate generation + durable applied-effect IDs in one repository object and update it with current-blob CAS.

The model separates authority failures from time-expiry policy failures. `authority_unsafe` means stale generation, wrong effect/incarnation, stolen-token use, or duplicate effect after ambiguous success/retry. `clock_expiry_violation` means an actually expired token is accepted in the explicit skew state.

| mechanism | scenarios | authority_unsafe | clock_expiry_violation | current-safe opportunities blocked |
|---|---:|---:|---:|---:|
| signed bearer generation | 384 | 244 | 128 | 0 |
| + atomic single-use effect ID | 384 | 240 | 128 | 0 |
| + sink-incarnation/effect binding | 384 | 48 | 32 | 0 |
| + sender constraint + server nonce | 384 | 16 | 16 | 0 |
| + atomic current-epoch check | 384 | 0 | 4 | 4/8 |
| fail closed without atomic epoch | 384 | 0 | 4 | 4/8 |
| repository single-object CAS special case | 384* | 0 | n/a* | 0/8 |

`*` The repository special case has no time-bounded capability in the tested protocol, so the ternary expiry dimension is semantically irrelevant; the 384 enumeration contains three copies of each 128-scenario non-expiry state. It is kept only for shape comparability and is not a generic external-sink result.

### Targeted falsifying slices
- **Generation advance after mint:** with otherwise-valid right-target requests and an available epoch surface, every capability that did not atomically check the current generation admitted stale authority in `4/4`; the atomic-current-epoch candidate admitted `0/4`.
- **Token theft:** bearer forms admitted a stolen otherwise-valid capability in `4/4`; the sender-constrained form admitted `0/4` under the tested assumption that the proof key is not also stolen.
- **Cross-effect / cross-incarnation substitution:** unbound bearer forms accepted `12/12`; sink-incarnation + exact-effect binding reduced this to `0/12`.
- **Ambiguous successful response + retry:** the plain signed bearer duplicated `1/1`; every candidate with effect ID consumed atomically with apply duplicated `0/1`.
- **Clock-skewed expiry:** every token candidate whose expiry decision depended on the sink's skewed wall clock accepted the explicitly expired token in `4/4`. Therefore wall-clock expiry cannot be the current-generation authority fence. If expiry itself is a material authorization condition, a trustworthy sink-side time/nonce policy remains a separate requirement.
- **No epoch surface:** the exact-current candidate fails closed, intentionally blocking `4/8` otherwise-current safe opportunities in the full current-opportunity slice because half the lattice removes the required atomic epoch surface. This is an availability cost, not a safety pass for an unavailable mechanism.

## Public mechanism evidence
1. RFC 6750 defines bearer-token semantics: possession of the bearer token is sufficient to use the associated authorization; no proof of possession of a cryptographic key is required. This supports the token-theft negative control. Source: https://www.rfc-editor.org/info/rfc6750/
2. RFC 9449 (DPoP) sender-constrains tokens with proof of possession, binds the proof to token/request data, and describes server-provided nonces plus `jti` replay tracking. It also states that a DPoP proof by itself is not an access-control mechanism; the resource server must still validate the access token. This supports the separation between sender binding/replay defense and current-generation authorization. Source: https://www.rfc-editor.org/info/rfc9449/
3. GitHub's repository Contents API requires the current blob `sha` when updating an existing file and documents `409 Conflict`. Therefore, for the narrow repository-resident special case where generation and durable applied-effect IDs are co-located in one file, stale writers can be fenced by one current-blob CAS and ambiguous retries can be reconciled from that same object. Source: https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents

## Observation versus inference
**Observed in the finite model:** binding, sender constraint, single-use effect identity, and current-generation authorization eliminate different counterexample classes; none substitutes for the others. The strong token composite has zero modeled authority failures only when the effect sink itself owns an atomic current-epoch comparison and durable effect-ID consume/apply boundary. Time-expiry skew remains independent.

**Inference, scope-limited:** a signed or sender-constrained capability format can transport authorization evidence, but cannot by itself make an arbitrary external sink current-generation-safe. Freshness/revocation and single-use effect application must be sink-enforced. A repository single-object CAS is a scheduled-Chat-accessible narrow positive for repository-resident effects, not proof for arbitrary external effects or multi-object effects.

## Phase-1 zero-dependency / zero-quota / cost assessment
- incremental monetary cost added by this leaf: **0**;
- optional monthly/trial/paid quota dependency added by accepted route: **none**;
- richer-mode / protected-primary / manual-user execution dependency introduced: **none**;
- external hosted coordination accepted as a solution: **no**;
- public standards are evidence only; lightweight repository API is transport only and must fail closed/checkpoint on rate limits.

The generic external-effect route remains unresolved: no tested capability-token mechanism alone provides the sink-side atomic `current generation + exact effect binding + durable single-use effect ID` boundary while also proving scheduled-Chat-native availability at zero optional finite quota. This is an unresolved child, not an irreducibility/completion claim.

## Exact continuation
Next invocation, execute exactly one bounded non-conflicting leaf on **capability issuance/key custody without protected secrets**. Compare (a) signature-bearing capability requiring a long-lived signing key, (b) repository-CAS-issued opaque grant ID with no worker-held secret, (c) sender-constrained proof key, (d) capability key rotation/revocation with repository rollback, and (e) fail-closed issuance. Enumerate issuer rollback/ABA, stolen grant, key rotation after mint, issuer response loss, worker restart with no secret access, and rate-limit interruption. Determine whether scheduled Chat can issue a positive exact-generation grant for the repository-resident special case without introducing protected/manual execution, hosted coordination, finite monthly quota, or a new rollbackable authority. Keep arbitrary external sinks as a separate unresolved child; do not generalize repository CAS beyond its tested single-object effect domain.

Termination remains recurring-open: `global_completion=false`, `phase1_completion_claimed=false`, `enabled_desired=true`; worker scheduler mutation is forbidden.
