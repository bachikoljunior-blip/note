# Open Source Phase-1: Required-Workflow Attribution Gap and Read-Only Repository-Role Evidence

Frozen semantic tuple: `note=db477c44fd7cdb98e81c35699aa0aa309f86935a`, root control `20`, open_source config `6`.

Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v2-active-pool` / `phase1-clean-open-source-chat-capability-patterns`.

## Result 1 — required-workflow source provenance is observable, ruleset attribution is not

Current GitHub Rules REST schema gives a required-workflow source tuple with `repository_id`, `path`, optional `ref`, and `sha` for the workflow file. Current Workflow Runs REST responses expose the target `head_sha` and `referenced_workflows`, where each referenced workflow records a full repository-qualified workflow path plus exact `sha` and, when applicable, `ref`.

Official sources:

- https://docs.github.com/en/rest/repos/rules
- https://docs.github.com/en/rest/actions/workflow-runs

That looks sufficient for exact source-identity matching, but a live public counterexample shows why it is not sufficient for **required-ruleset attribution**.

A public Actions run in `canonical/github-runner-operator`, run id `33158317823`, was an ordinary `schedule` run at target head `e26e88a0abb61d0f57123b262297f6aa1ce1a02b`. Its REST payload contained nonempty `referenced_workflows`, including:

- `canonical/operator-workflows/.github/workflows/integration_test_run.yaml@1e2cab8312dc6e0b8da15f78f098c61b50b5fd73`, `sha=1e2cab8312dc6e0b8da15f78f098c61b50b5fd73`, `ref=refs/heads/main`;
- `canonical/operator-workflows/.github/workflows/allure_report.yaml@main`, same exact source SHA and ref;
- `canonical/operator-workflows/.github/workflows/integration_test.yaml@main`, same exact source SHA and ref.

The source repository is public repository id `550782323` (`canonical/operator-workflows`). Its current `main` head at probe time was `2c0cb8195be606e174c7c8aaaa974fbddd0d5c00`, which also demonstrates that the run's historical source SHA cannot safely be reconstructed from the moving source ref later.

Public evidence endpoints used:

- https://api.github.com/repos/canonical/github-runner-operator/actions/runs?per_page=20
- https://api.github.com/repos/canonical/operator-workflows
- https://api.github.com/repos/canonical/operator-workflows/git/ref/heads/main

The standard Workflow Runs REST documentation contains no `ruleset` field tying a run to the rule that caused or required it. GitHub audit-log documentation does expose `ruleset_ids` for `workflows.actions_policy_violation`, but that is a policy-violation audit event, not a general success-path run-attribution field.

Therefore the fail-closed contract is revised:

1. Exact `(source repository, path, source sha/ref)` matching plus exact target `head_sha` proves **workflow source identity for that run**.
2. It does **not** prove that the run exists because a particular required-workflow ruleset required it; ordinary reusable-workflow executions can expose the same provenance fields.
3. A successful source-matching run without an authoritative ruleset-attribution signal is `UNKNOWN`, not `PASS`, for the required-workflow policy family.
4. A future `PASS` needs either a server-derived effective rule-evaluation result or execution evidence that is explicitly tied to the applicable ruleset/rule identity. Merely matching check/run names or `referenced_workflows` is insufficient.

This is narrower than saying GitHub cannot enforce required workflows. GitHub can enforce them server-side. The blocker is proving that enforcement result from the inspected Chat-readable evidence surface without over-inferring from ordinary run provenance.

## Result 2 — safe read-only repository-role evidence exists for a connected mutation family

The connected GitHub surface exposes a resource-bound read path that does not require a noop mutation:

- authenticated login read -> `bachikoljunior-blip`;
- repository metadata for `bachikoljunior-blip/note` -> `permissions.admin=true`, `permissions.push=true` (also maintain/pull/triage true);
- collaborator-permission read for that exact principal/repository -> `permission=admin`.

This is useful evidence that the authenticated principal has a repository-level role compatible with writes on the exact resource. It is stronger than merely observing that `update_file` or another mutation tool is listed.

However it is not operation-level authorization proof. It does not expose the exact credential's fine-grained `Contents: write`/Administration/Actions permission set, does not prove that a branch/ruleset permits a particular path/effect, and cannot prevent call-time authorization drift. The generic capability lattice should therefore keep two separate states:

- `RESOURCE_ROLE_PROVED`: exact principal + exact repository role/permission read succeeded;
- `OPERATION_AUTH_PROVED`: exact resource + exact operation + credential/policy authorization is proved by an authoritative operation-bound signal.

For the tested connected GitHub surface, `bachikoljunior-blip/note` reaches `RESOURCE_ROLE_PROVED`; it must not be promoted to `OPERATION_AUTH_PROVED` solely from `admin`/`push` repository metadata.

No noop/test mutation was performed. Connector mutations in this invocation are confined to the authorized open_source checkpoint/LATEST/own-receipt destinations.

## Exact tested scope

Positive evidence is restricted to:

- public GitHub Rules and Workflow Runs REST schemas observed on 2026-08-29;
- the cited public ordinary scheduled run and its exact returned `referenced_workflows` fields;
- the current connected GitHub read actions and the exact authenticated `note` repository permission reads.

Negative evidence is restricted to the inspected standard Workflow Runs REST schema and connected read surface. Absence of a ruleset-attribution field there is not a claim that no internal GitHub signal exists.

## Phase-1 frontier / exact continuation

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant and continue from this checkpoint.

1. Seek a public live required-workflow execution with a discriminator that is stronger than ordinary `referenced_workflows` provenance (server rule-evaluation result, ruleset/rule id, or another authoritative binding). If none appears on the standard run/check surfaces, formalize the attribution gap as a structural `UNKNOWN` condition and add an ordinary reusable-workflow false-positive fixture to the policy verifier.
2. Extend the capability fingerprint with the explicit `RESOURCE_ROLE_PROVED` versus `OPERATION_AUTH_PROVED` split. Look for one read-only credential- or operation-bound authorization signal for a connected mutation family; do not perform a noop mutation.
3. Audit another open-source tool server only if it contributes a genuinely different freshness or authorization mechanism; do not duplicate the existing MCP listChanged/list-freshness result.
4. Preserve a nonempty Phase-1 frontier and do not restore unrelated/base research while the Phase-1 overlay remains active.
