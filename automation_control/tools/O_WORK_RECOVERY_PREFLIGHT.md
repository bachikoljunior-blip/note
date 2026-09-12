# O recovery evidence checks

This read-only helper enforces evidence requirements before the o_work_monitor_recovery controller reuses an unchanged hold or suppresses a blocked-publication notice. It grants no execution, publication, lease, or safety permission.

Fetch the current O_OPERATIONS control/role configuration first. Preserve all existing routing, slot audit, stop-proof, single-writer, CAS/readback, frozen-invocation, publication, and continuation requirements. The helper adds evidence checks; a false full_refresh_required result is not sufficient authorization to reuse a hold. All current repository requirements still apply.

Run the checked-in regression tests after fetching these exact files, and run the helper on normalized, non-secret observations:

```sh
python -m unittest discover -s automation_control/tests -v
python automation_control/tools/o_work_recovery_preflight.py facts.json --now <actual-UTC-observation-time>
```

Use fresh SHA-only O main and control observations first. Read the previous full receipt and human-monitor source receipt by their exact references. Populate:
- main_sha, prior_main_sha, control_blob_sha, prior_control_blob_sha.
- prior_hold_eligibility_verified and hold_fingerprint_complete_and_unchanged only after checking every configured field.
- prior_full_observed_at and consecutive_lightweight_reuses from actual receipts.
- human_monitor with observed_at, main_sha, result, and source_ref. A queue blob alone is not an exact main reference.
- new_user_message, explicit_recovery_candidate, and other uncertainty/read-order flags truthfully.
- blocked_action_key bound to destination, target ref, commit, tree and manifest. Do not reuse a notice for a changed payload.
- notification with status, action_key, notice_text and emission containing kind, source_ref and text_sha256 only if the actual final message is visible, or the platform has acknowledged delivery. Compute the digest from that observed text. A planned notice or a previous monitor's claim is not source evidence.
- accepted_pending_operation and separate_owner_substantive_progress_verified only from current owner-bound native/tool/PR/CI or accepted-operation receipts.
- consumed_response_successor_unpublished, frozen_native_objects_verified, original_commit_available and replacement_proposal_available from exact objects.

Persist helper inputs, output and tool/file blob references with the ordinary receipt. If it errors or evidence is incomplete, perform a full read-only assessment; never grant mutation permission. Config revision15 limits are 5,400 seconds for human evidence, 10,800 for the full hold and two consecutive reuses. Measure age at the actual decision time. Newer config requirements remain mandatory.

When notification_due is true, prepare a concrete reviewable result and emit the exact actionable blocker and required user action. Save planned/emitted/delivery-confirmed as distinct states. Only a subsequently observed final-message reference may support emitted; only an actual delivery acknowledgement supports delivery-confirmed. Never mark a prepared response delivered.

When a predecessor response is already consumed and saved successor records exist, missing old commit headers do not justify replay. An isolated local replacement proposal may use the exact preserved native bytes, current main, current replay guards and honestly new commit metadata. Preserve old identities as provenance. It is not the old commit, a native effect, or publication authorization. A new proposal remains subject to actual platform review and the exact user authorization required by that review. No alternate uploader, identity, destination or indirect route may bypass a refusal.

Before publication, verify directive-source binding against the latest inbox; prepare reviewed atoms for unacknowledged input without granting extra permission or mutating frozen requests. Do not weaken CI or the resume guard. After authorized publication, full required CI and exact main readback, ingest pending inputs and revalidate the existing fenced continuation authorization before Candidate5. Never repeat Task4.

Ordinary transient errors remain automatically retryable with bounded backoff. An account-holder-only approval need must be stated clearly, not mislabeled as recoverable by waiting. After the exact notice has been observed, deduplicate it while continuing fresh safe checks. No monitor receipt alone proves primary progress, successful recovery or invocation overlap.
