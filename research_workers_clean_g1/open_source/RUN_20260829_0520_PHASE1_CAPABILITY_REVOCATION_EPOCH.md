# Open Source Phase-1: Capability Revocation Adds a Stronger Effect-Bound Pattern Than Detached Authorization Checks

Frozen semantic tuple for this invocation remains: `note=8c11c50aa491507fc1cec3ffef72887691cd0966`, root control `22` / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, open_source config `6` / blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`.

This checkpoint continues `RUN_20260829_0459_PHASE1_AUTH_MIDDLEWARE_FENCE.md` within the same frozen invocation. The previous leaf found no cross-system API that accepted a prior authorization-decision revision as an atomic external mutation precondition. This leaf asked a narrower question: can capability/token systems provide an effect-bound revocation mechanism strong enough to be useful for Chat tool execution without pretending that token validity is an authorization-revision lease?

## 1. OAuth token introspection is a revocation-aware request gate, but caching creates a measurable stale window

RFC 7662 gives protected resources a standard way to query the authorization server for the current state of a token. `active=true` generally means the token was issued by that server, is within its validity window, has not been revoked, and is valid at the requesting protected resource. The RFC explicitly requires the authorization server to test revocation when tokens can be revoked.

This is materially stronger than verifying an offline bearer JWT's signature and expiry alone. When the protected resource introspects at request time and treats an unavailable/negative check as denial, the effect request is gated by current authorization-server state. The classifier calls this `REVOCATION_AWARE_REQUEST_GATE`.

However RFC 7662 also explicitly allows protected resources to cache introspection responses and warns that a token can be revoked while a cached `active=true` response is still trusted. Thus a cached implementation has a bounded-but-real stale authorization window and must not be modeled as an exact revocation epoch. The classifier calls this `REVOCATION_STATE_FRESHNESS_UNPROVED` unless the concrete cache/freshness contract is proven.

RFC 7009 reinforces the distinction. A handle/reference access token can force the resource server to consult the authorization server each time, making revocation visible on use. A self-contained access token can be validated without that interaction, so immediate revocation may require a separate backend mechanism or short lifetimes. Revocation is therefore a property of the validation path, not just a property of having a `jti` or signed token.

Official sources:
- https://www.rfc-editor.org/rfc/rfc7662
- https://www.rfc-editor.org/rfc/rfc7009

## 2. DPoP is proof of possession, not a revocation epoch or standalone access-control decision

RFC 9449 sender-constrains OAuth tokens. A DPoP proof binds the request to a client-held key and covers request context such as method/URI, time/unique proof material, and the access-token hash when applicable. The resource server verifies that the proof key matches the token's binding and refuses malformed or mismatched requests.

The RFC is explicit that a DPoP proof by itself is not an authentication or access-control mechanism, and that the access token must still be valid in all other respects. DPoP therefore reduces stolen-token replay but does not make a prior ALLOW current after revocation. It is classified as `PROOF_OF_POSSESSION_ONLY`, orthogonal to revocation freshness.

Official source:
- https://www.rfc-editor.org/rfc/rfc9449

## 3. Biscuit revocation identifiers show why distribution freshness is part of authority

Biscuit tokens have revocation identifiers, including identifiers for derived/attenuated token blocks. During authorization a verifier can reject a Biscuit whose revocation identifier appears in the supplied revocation list.

Crucially, Biscuit's official revocation guide says the specification does not mandate how revocation IDs are published or distributed. That is architecture-specific. Therefore a verifier can be locally fail-closed against the list it has while still authorizing a token that was revoked centrally but has not yet reached that list.

This is a concrete reason to keep two bits of evidence separate:

- `revocation_check_performed=true`;
- `revocation_state_authoritative_or_fresh=true/false`.

Without the second, the result stays `REVOCATION_STATE_FRESHNESS_UNPROVED` rather than being upgraded to an effect lease.

Official source:
- https://www.biscuitsec.org/docs/guides/revocation/

## 4. Macaroons support request-context caveats but do not themselves supply a current revocation epoch

The original Macaroons design and current open-source implementations support first-party caveats checked by the target service and third-party caveats discharged by an external service. This is useful for narrowing authority and for requiring fresh contextual evidence such as a short-lived authentication discharge.

But a successfully verified macaroon/discharge is still a credential presented to the target service. The core mechanism does not by itself define a monotonic current authorization epoch that invalidates every older credential at effect commit. A third-party discharge can be short-lived or re-requested, which is useful request-bound policy, but it should not be labeled `TRUE_EXTERNAL_REVISION_GATE` without a separate revocation/current-state contract.

Official sources:
- https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/
- https://github.com/go-macaroon/macaroon

## 5. NØNOS provides a concrete positive analogue: an effect-side revocation epoch checked before every syscall

Exact current `NON-OS/nonos-micro-kernel` main inspected: `c6f021d10278d1494d88835dd8c98b041ef13d65`.

The current source has a strong pattern that is different from a detached authorization check:

- `src/process/caps.rs::new_token` reads the process's current `revocation_epoch` and MAC-signs it into each capability token.
- `revoke(pid, mask)` increments that epoch before minting/installing the replacement token with reduced bits.
- `src/syscall/contract/resolver/check_epoch.rs` rejects a token whenever `token.revocation_epoch < ctx.capsule_revocation_epoch` with `RevocationEpochStale`.
- `src/syscall/contract/resolver/resolve.rs` executes token/session/ASID/epoch/syscall checks in order before returning success.
- `Capability::resolve` constructs an in-kernel witness only after that resolver succeeds; user space cannot construct the witness directly.

This means a previously valid token remains cryptographically authentic after revocation but is no longer authoritative: its signed epoch is behind current kernel state, so the next syscall is denied before the handler obtains the capability witness.

This is the strongest positive mechanism found in this leaf and is classified as `EFFECT_SIDE_REVOCATION_EPOCH_GATE`.

It is **not** reclassified as the earlier `TRUE_EXTERNAL_REVISION_GATE`, because there is no prior decision made by an independent authorization service and later transferred into an unrelated effect API. The capability token and revocation epoch are issued and enforced by the same effect-serving authority. That co-location is exactly why the mechanism is strong.

Exact source-qualified files:
- https://github.com/NON-OS/nonos-micro-kernel/blob/c6f021d10278d1494d88835dd8c98b041ef13d65/src/process/caps.rs
- https://github.com/NON-OS/nonos-micro-kernel/blob/c6f021d10278d1494d88835dd8c98b041ef13d65/src/syscall/contract/resolver/check_epoch.rs
- https://github.com/NON-OS/nonos-micro-kernel/blob/c6f021d10278d1494d88835dd8c98b041ef13d65/src/syscall/contract/resolver/resolve.rs
- https://github.com/NON-OS/nonos-micro-kernel/blob/c6f021d10278d1494d88835dd8c98b041ef13d65/src/syscall/contract/capability.rs

## 6. IBM ContextForge gives the opposite MCP counterexample: revocation-aware JWTs that fail open on lookup outage

Exact current `IBM/mcp-context-forge` main inspected: `555a9f3be253290151ac51ed45fbdca4565f132b`.

Its current security guide recommends `REQUIRE_JTI=true`, stores token revocations in a `token_revocations` database table, and says normal auth/MCP transport paths enforce token revocation and active-user checks.

But the same official guide explicitly documents an availability trade-off: if revocation or user lookups fail because the database is unavailable, those checks currently **fail open**. The current credential-verification source logs `Token revocation check failed for JTI ...` on lookup errors rather than treating every lookup failure as a denial.

This is a high-value Chat/MCP capability-detection rule: “supports revocation” is not sufficient. A safe fingerprint must also capture outage semantics. For a high-impact tool effect, a revocation check that can fail open is classified as `REVOCATION_GATE_FAIL_OPEN`, not `REVOCATION_AWARE_REQUEST_GATE`.

Exact sources:
- https://github.com/IBM/mcp-context-forge/blob/555a9f3be253290151ac51ed45fbdca4565f132b/docs/docs/manage/securing.md
- https://github.com/IBM/mcp-context-forge/blob/555a9f3be253290151ac51ed45fbdca4565f132b/mcpgateway/utils/verify_credentials.py

## 7. Updated pattern for Chat-capable tool authorization

The useful ladder is now more precise:

1. `BEARER_CAPABILITY_ONLY`: signature/scope/expiry are checked, but current revocation state is not proven.
2. `PROOF_OF_POSSESSION_ONLY`: sender binding/replay resistance such as DPoP; still requires independently current authorization.
3. `REVOCATION_STATE_FRESHNESS_UNPROVED`: revocation IDs/list exist, but propagation/cache freshness is not proven.
4. `REVOCATION_GATE_FAIL_OPEN`: revocation is checked on the normal path but outage semantics allow the request through.
5. `REVOCATION_AWARE_REQUEST_GATE`: the effect request checks authoritative/current revocation state and fails closed.
6. `EFFECT_SIDE_REVOCATION_EPOCH_GATE`: the effect authority itself compares a signed capability epoch to its current epoch before running the handler.
7. `TRUE_EXTERNAL_REVISION_GATE`: a prior independent authorization-decision revision is atomically accepted/revalidated by a different effect authority. Still unobserved in the bounded sample.

For Chat agents, 5 and 6 are directly useful. Pattern 6 is particularly durable: a checkpoint may retain an old capability token, but replay after revocation fails because the effect authority compares it with current epoch at execution. This is safer than checkpointing a detached `authorized=true` result.

## 8. Executable classifier V3

Created and self-tested before persistence:

`research_workers_clean_g1/open_source/AUTH_EFFECT_PROVENANCE_MATRIX_20260829_0520_V3.py`

V3 adds token semantics `CAPABILITY_TOKEN`, `REVOCATION_ID`, `REVOCATION_EPOCH`, and `PROOF_OF_POSSESSION`, plus explicit evidence for:

- whether revocation state is checked at the effect boundary;
- whether that state is authoritative/fresh;
- whether lookup failure is fail-closed;
- whether the effect authority compares the capability's current revocation epoch.

Twenty-two fixtures and seven provenance invariants passed locally before persistence. New fixtures cover RFC 7662 no-cache vs cached introspection, DPoP, Biscuit revocation-list freshness, ContextForge fail-open revocation lookup, and the NØNOS effect-side epoch gate. The hypothetical cross-system `TRUE_EXTERNAL_REVISION_GATE` remains separate.

## Semantic barrier / continuation

The frozen root/config identities remained unchanged across unrelated main-head movement through `ec8afca4548ea54ee5e0a0df16569d986bb3d0ae`; later-head semantic content was not adopted. Before this leaf was persisted, the current role-local `LATEST.json` blob was still the prior own write `bd5938f755215c4d15031ed1299f511dd577a521`, so there was no own-state reconstruction conflict.

Exact Phase-1 continuation:

1. Search for a production Chat/MCP or API gateway that implements the NØNOS-like pattern at network/tool scale: a signed capability carrying a monotonic authorization/revocation epoch that the effect server compares with authoritative current epoch on every mutation, fail-closed on state uncertainty.
2. Distinguish per-principal epoch, per-resource epoch, and global/policy epoch: a global epoch may over-revoke safely, while a too-narrow epoch can miss revocations outside its scope.
3. Add crash/retry fixtures for checkpointed capabilities: token minted at epoch `e`, checkpoint, epoch increments to `e+1`, replay must be denied; new token at `e+1` must pass only if its resource/method caveats also match.
4. Audit whether any agent-facing MCP gateway exposes revocation/freshness provenance in a structured tool response, rather than only enforcing it internally.
5. If no network-scale epoch gate appears after bounded official-source search, persist the effect-side epoch design as a reusable Chat handoff pattern and resume the safely-authorized GitHub Rule Suite leaf.
6. Preserve a nonempty Phase-1 frontier; do not restore unrelated base research while the overlay remains active.

No source repository, branch/ref, PR, issue, release, workflow, DESIRED_STATE, other-worker/downstream state, O state, or shared aggregate ledger was mutated. Writes remain confined to the authorized `research_workers_clean_g1/open_source/` namespace and own immutable receipt namespace.
