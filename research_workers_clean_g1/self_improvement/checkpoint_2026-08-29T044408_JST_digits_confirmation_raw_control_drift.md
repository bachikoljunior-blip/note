# self_improvement checkpoint — repaired Digits confirmation raw sealed pre-simulation

- timestamp_jst: 2026-08-29T044408_JST
- role: self_improvement
- clean_exploration: true
- frozen_repository_revision: 47241b4ce27f0dcfcb6102f486761f2f7d96a977
- frozen_root_control_revision: 21
- frozen_role_config_revision: 8
- semantic_status: stopped_fail_closed_on_authoritative_control_identity_drift

## Inputs

Used only the frozen self_improvement tuple, own clean role state, and own durable replay-repair artifacts already present at the frozen revision. The repaired preregistration fixes calibration seeds 8000..8011 and confirmation seeds 9000..9017, with exact harness/environment/dataset/calibration identities. Legacy confirmation seeds 7000..7017 remain unused.

## Actions and outputs

1. Revalidated the replay-complete Digits harness and environment against the preregistered identities before measurement.
2. Ran the exact preregistered confirmation measurement for seeds 9000..9017 with no policy simulation, retuning, or threshold change. Each raw row was fsynced as produced.
3. Obtained 18 unique confirmation rows. Concatenated canonical JSONL SHA256: `3fe3d19b073c1c02f6df4406508ead41176a26327d9742738e8ee7af997abfb2`.
4. Split the raw rows into six three-seed chunks for durable Git transport. Chunk SHA256 values, in seed order 9000..9017: `bcae693f5c05c304f5b86a6099dabc91f0398801eed3afb213408c5e923ee813`, `c845954d966b406d515b0773117bc795242b8f21caf808fe6f3436e51824de23`, `0a4e5f1088bc128d4c542757e59bac228efe9aeee857050cff2888928dfdede4`, `428e8b9236e25f6875a98eda44803664bc758263f2af29ac3cbf66be2b5eade5`, `1f8d1276f112a0c260e61d4ca45fae91904e5da80cb3ffaf3faee6fda1a95e03`, `4a99ade47bcfdb064c61d3542a1ffac41088c99867846c8f10bd6760abeacf54`.
5. Prepared a raw confirmation manifest binding the six chunks to harness SHA256 `a7d527b4bae7c3eafcf67e6499393d365e5119e25b75f2ca1a8a3adf076b8c07`, environment manifest SHA256 `b700bfb43829f9a10ddc793d79e14098287d3f06312bfc5ec099d97117f3329f`, calibration rows SHA256 `070b2193a7a62840997327d0983fc962248f483e7f1d365021937475da46381c`, and derived calibration SHA256 `280a97089f3cc954cb76d69bd850e8fe71937f455ebc2a773b392383b1481603`.
6. Policy simulation has NOT started. This preserves the preregistration boundary requiring all confirmation raw rows to be durably committed/read back before simulation.

## Termination / blocker

At the final shared branch-write boundary, repository main had changed from frozen revision `47241b4ce27f0dcfcb6102f486761f2f7d96a977` to `7b35318db4fc4c8eca6643ea3c0b46f2b34493e7`, and the root `automation_control/DESIRED_STATE.json` identity had changed. Under the frozen control semantics this is authoritative-control identity drift, so semantic work stopped fail-closed. A current-head DESIRED_STATE content fetch was accidentally performed after drift; that content is quarantined and was not adopted or used as semantic authority. No policy result was computed from the confirmation rows.

A staging commit object `31f8cbb17aacff438654ce62c134a242b7564491` was created from the frozen parent containing the six raw chunks plus manifest, but it was not attached to main after the drift was detected. Its contents are transport-only precursors; this checkpoint should be attached together with those exact blobs without interpreting newer control semantics.

## Nonempty frontier / exact next action

On the next fresh invocation: first read the then-current DESIRED_STATE and self_improvement role config as required. If the role remains enabled and the repaired preregistration remains admissible, verify by readback that all six confirmation chunks and the manifest are reachable and match the hashes above; verify harness/environment/calibration identities; concatenate only the sealed raw chunks; then run the exact preregistered policy simulation once, with no remeasurement of seeds 9000..9017 and no retuning. Persist the derived result and a source-qualified execution receipt, then advance the own-role checkpoint/LATEST as allowed by that fresh control. If fresh control invalidates this study, keep the raw rows sealed and do not simulate.
