# Open Source Phase-1: Gerrit NoteDb history freezes change metadata, not the whole submit-policy universe

## Frozen control provenance

This leaf remains under frozen `control_revision=22` / `config_revision=6` with root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb` and open_source config blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`. No newer control semantics were adopted.

It follows `RUN_20260829_PHASE1_OPERATION_EFFECT_TAXONOMY.md` and resolves the frontier item about Gerrit historical NoteDb snapshots.

## 1. `meta=SHA-1` is a historical change-state snapshot

Gerrit's Get Change REST endpoint accepts `meta=SHA-1`. The current docs state that Gerrit uses that historical NoteDb snapshot to populate `ChangeInfo`; a SHA that is not reachable as a NoteDb state returns `412`.

Primary source:
`https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html`

This is strong provenance for the **change's own review metadata history**: patch-set associations, votes/comments/change state recorded in NoteDb can be tied to a Git commit in the change's meta ref.

NoteDb itself is Git-backed and designed for auditability, but Gerrit explicitly documents that meta refs may be rewritten and provides no strict guarantee that all historical meta commits remain forever reachable.

Primary source:
`https://gerrit-review.googlesource.com/Documentation/note-db.html`

So a durable external checkpoint should preserve the meta SHA and, where long-term replay matters, not assume the server will retain reachability indefinitely.

## 2. Submit requirements live in a different versioned ref

Gerrit submit requirements are configured in `project.config` on the project's `refs/meta/config` branch. The project-configuration docs explicitly note that this branch is versioned and its history shows how configuration changed over time and which configuration was active when.

Primary sources:
- `https://gerrit-review.googlesource.com/Documentation/config-submit-requirements.html`
- `https://gerrit-review.googlesource.com/Documentation/config-project-config.html`

This creates a critical provenance split:

- change NoteDb `meta` SHA = historical **change metadata**;
- project `refs/meta/config` SHA = historical **project policy/config definition**.

A historical ChangeInfo loaded at `meta=SHA` is therefore not, by itself, a certificate of the exact submit-policy configuration that was active at the time. Submit requirements can also be inherited from parent projects, and plugin-provided submit rules participate in the server decision.

Consequently:

`historical change meta SHA != historical policy universe`

## 3. Exact submit-decision provenance needs a multi-root capsule

For a strong Gerrit submission capsule, preserve independently:

1. exact reviewed patch-set revision SHA;
2. change NoteDb meta SHA surrounding the decision/effect;
3. exact project `refs/meta/config` SHA;
4. exact inherited parent project config SHAs needed for effective policy;
5. the server-returned submit requirement results, including `OVERRIDDEN`/failure states rather than a scalar green bit;
6. plugin submit-rule provenance/version if those plugins contribute to submittability;
7. submitted-together closure and post-effect `submission_id`;
8. exact destination-ref transition after submit.

If any effective-policy root cannot be captured, the durable classification is policy provenance `UNKNOWN`, even if the historical change meta SHA is available.

## 4. A useful testing surface exists, but it is not a historical-policy replay token

Gerrit's submit-requirement docs expose a Check Submit Requirement endpoint that can evaluate a named submit requirement against a change and can load a requirement from a specified `refs/meta/config` **change** via `refs-config-change-id`.

This is valuable for testing prospective config changes, but it does not convert the change NoteDb meta SHA into a single historical policy revision token. The policy definition, inheritance chain, labels/groups and plugin rules remain distinct provenance roots.

Therefore the earlier authorization lesson generalizes again: a convenient revision token for one datastore does not automatically fence every authority participating in the decision.

## 5. Exact continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active:

1. Extend `OPERATION_EFFECT_CLASSIFIER_20260829_V1.py` with a `POLICY_PROVENANCE_ROOTS_EXACT` axis distinct from `POST_EFFECT_POLICY_EXACT`; test partial change-meta-only and project-config-only cases as `UNKNOWN`.
2. Finish the GitHub known-stacked-PR connected representation audit; if the raw PR `stack` object is not demonstrably present, finalize `UNKNOWN_MEMBER_VECTOR` for ordinary connected Chat.
3. Add capture-order/crash-recovery fixtures spanning GitHub async result expiry, Rule Suite list discovery window, GitLab train-car ID, and Gerrit change-meta/config-root provenance.
4. Audit whether another open-source policy engine/tool protocol exposes a single compound revision that really covers both decision data and policy definition; use it as a counterexample or confirmation of the multi-root rule.
5. Preserve a nonempty Phase-1 frontier.

## Clean execution boundary

Public research was read-only. Writes remain confined to authorized `research_workers_clean_g1/open_source/` plus own immutable receipts. No source repository, branch/ref, PR/issue/release/workflow, `DESIRED_STATE.json`, other-worker/downstream/O state, or shared aggregate ledger was mutated or consumed semantically.
