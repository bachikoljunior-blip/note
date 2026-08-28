# Phase-1 witness membership reconfiguration and configuration epochs

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_DECISION_WITNESS_REPLICATION_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, public etcd membership documentation, and one finite synthetic reconfiguration model.

## Leaf objective

The witness-replication leaf assumed a fixed three-replica set. This leaf changes membership from old `ABC` to new `BCD` and asks whether the old witness authority transfers safely.

Each synthetic case starts with an old-configuration quorum carrying an old membership-epoch witness. During replacement, some subset of `B,C,D` receives a witness attested under the new membership epoch. One node can fail, a takeover can read using either the old or new configuration, and the logical transaction ID may be reused with a different transaction generation.

Compared policies:

1. `naive_switch` — changes membership without proving that a new quorum carries the witness and accepts responses without a membership epoch fence.
2. `joint_quorum` — completes cutover only after both the old authority and a new-configuration quorum have the witness; recovery rejects an old membership epoch.
3. `epoch_failclosed` — allows cutover without a transfer quorum but never acts on an old/missing membership epoch; unresolved reads become manual.
4. `consensus_store` — abstract benchmark: membership change completes only after the replicated consensus state safely includes the witness; subsequent reads are linearizable through the current configuration.

## Public mechanism boundary

Current etcd documentation defines quorum as a majority required for consensus. Its API guarantees say completed writes are committed through consensus and ordinary KV reads are linearizable by default. The etcd learner design explains why membership changes are operationally hazardous: a new learner is non-voting until caught up, then is promoted only after it has sufficiently caught up with the leader. Runtime reconfiguration guidance also requires a majority to process membership changes and recommends sequential changes.

Sources:
- https://etcd.io/docs/v3.7/learning/api_guarantees/
- https://etcd.io/docs/v3.7/learning/glossary/
- https://etcd.io/docs/v3.3/learning/learner/ (older design document; mechanism precedent only)
- https://etcd.io/docs/v3.8/op-guide/runtime-configuration/ (draft, used only for the generic majority/sequential-reconfiguration statement; latest stable docs remain v3.7)

The synthetic policies below are not claims that etcd implements these exact W/R rules.

## Finite model

The script enumerates **2,520 equal-weight synthetic scenarios** over:

- one old quorum among `AB`, `AC`, `BC`;
- every nonempty subset of new members `B,C,D` carrying the new membership-epoch witness;
- no node failure or one failed node among `A,B,C,D`;
- recovery reader using old or new membership;
- every quorum pair of that reader's membership;
- `COMMIT` / `ABORT`;
- logical transaction-ID reuse absent/present, with a changed current decision when reused.

### Aggregate comparison

| policy | unsafe | stale old-epoch acceptance | split authority | recovered | manual | cutover unavailable | lost |
|---|---:|---:|---:|---:|---:|---:|---:|
| naive switch | **732** | **720** | **312** | 780 | 1,008 | 0 | 1,032 |
| joint old+new quorum | **0** | 0 | 0 | 432 | 1,008 | 1,080 | 1,008 |
| epoch-failclosed | **0** | 0 | 0 | 648 | 1,872 | 0 | 1,872 |
| consensus-store abstraction | **0** | 0 | 0 | **1,440** | 0 | 1,080 | 0 |

Synthetic `cost` counts are stored separately in the result artifact and are not latency estimates.

## Result 1: membership cutover before the new quorum owns the witness is a recovery hole

There are **1,080** scenarios where fewer than two members of `BCD` carry the current membership-epoch witness at cutover.

- `naive_switch` is unsafe in **420/1,080** and loses the decision in 456;
- `joint_quorum` refuses to complete reconfiguration in **1,080/1,080**;
- `epoch_failclosed` may complete the membership change but later refuses unprovable recovery rather than fabricating authority.

This is the membership analogue of the earlier fragment reservation result: a past quorum in `ABC` is not a plan-wide lease for future `BCD`. Before removing the old authority, the decision proof must be transferred into the new authority domain.

## Result 2: old-member reads remain dangerous even after the new quorum is healthy

In **720** scenarios where a new quorum already has the current witness but recovery still queries the old membership:

- `naive_switch` accepts an old membership epoch in **240** and creates split authority in all 240;
- `joint_quorum` fails closed/manual in all 720 old-reader cases rather than letting removed-member state compete with the current configuration.

A current transaction generation therefore needs a **membership/configuration epoch** in addition to its transaction generation. `txn_generation` prevents reuse collisions; `membership_epoch` identifies which replica set is allowed to attest that generation.

## Result 3: safe reconfiguration requires both state transfer and epoch fencing

`epoch_failclosed` is safe in all 2,520 scenarios but has poor recovery coverage because it does not require the witness to be transferred before cutover. `joint_quorum` adds the transfer proof but still loses availability whenever the tested explicit recovery pair is unavailable or uses the wrong epoch.

The abstract consensus-store benchmark completes only the 1,440 cases where a new quorum has the witness; within those completed cases and the model's one-node-failure assumption, it recovers all 1,440 with unsafe 0. This benchmark captures the architectural target: state transfer and membership authority must be one consensus history, not two loosely coupled configuration files.

## Candidate protocol

1. Every witness binds `{txn_id, txn_generation, membership_epoch, decision, participant_digest}`.
2. A membership epoch is authoritative only through its configured consensus/quorum mechanism.
3. Before retiring an old membership epoch, ensure the current witness state is durably represented by a quorum of the new epoch or by a consensus log whose membership transition preserves that state.
4. Recovery using an old membership epoch must fail closed after the new epoch becomes authoritative; content equality does not restore authority.
5. Do not let transaction-generation reuse and membership-epoch change share an unversioned logical key.
6. Prefer learner/catch-up or consensus-native reconfiguration mechanisms that avoid promoting a replica before it has caught up.
7. Measure reconfiguration availability separately from authority safety; refusing cutover can be the correct safe behavior.

## Exact scope limits

- Fixed old set `ABC` and new set `BCD`; one member replaced.
- At most one node failure.
- New-epoch witness transfer is abstract; log indexes, snapshots, and learner promotion thresholds are not modeled.
- Consensus-store benchmark assumes linearizable current-configuration reads after successful transition.
- Counts are synthetic mechanism counts, not production incident probabilities.

## Exact Phase-1 continuation

Continue with **claim/witness coupling across two independent consensus domains**.

Next finite grammar:

- task claim stored in consensus domain X, effect/decision witness stored in domain Y;
- X and Y independently available/unavailable;
- claim epoch advances before/after Y write;
- Y write clear/ambiguous;
- takeover reads X fresh but Y stale, or Y fresh but X stale;
- transaction generation and effect identity reuse;
- optional cross-domain durable intent linking `{claim_epoch, effect_id}`;
- compare `read-both-then-act`, `X-authoritative`, `Y-authoritative`, `durable cross-domain intent + fail-closed`, `single-domain co-location`, and safe archive;
- measure stale effect authority, duplicate effect, orphan witness, false exclusion, read/write burden, and safe recovery coverage.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
