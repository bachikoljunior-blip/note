#!/usr/bin/env python3
"""Cross-field semantic checks for verifier observability records.

This companion validator is intentionally small and fail-closed. JSON Schema
validity is necessary but not sufficient: hard negative dispositions require a
complete evidence surface and bound falsifying evidence, and cached verification
results are invalidated when evidence requirements or visible evidence drift.
"""

HARD_NEGATIVE = {"REJECT", "BLOCK", "PRUNE", "FORBID"}


def validate(record, context):
    codes = []
    requirements = record.get("claim_evidence_requirements", [])
    visible = record.get("visible_evidence", {})
    coverage = record.get("coverage_status")
    disposition = record.get("disposition")

    missing = [name for name in requirements if name not in visible]
    if coverage == "complete" and missing:
        codes.append("VERIFIER_COVERAGE_FALSE_COMPLETE")

    if coverage in {"partial", "uninspectable"} and disposition in HARD_NEGATIVE:
        codes.append("VERIFIER_HARD_REJECT_WITH_INCOMPLETE_EVIDENCE")

    if disposition in HARD_NEGATIVE:
        falsifying = record.get("falsifying_evidence", [])
        if coverage != "complete" or not falsifying:
            codes.append("VERIFIER_HARD_REJECT_UNSUPPORTED")

    if record.get("evidence_requirement_digest") != context.get("evidence_requirement_digest"):
        codes.append("VERIFIER_REQUIREMENT_DIGEST_STALE")

    if record.get("visible_evidence_digest") != context.get("visible_evidence_digest"):
        codes.append("VERIFIER_VISIBLE_EVIDENCE_DIGEST_STALE")

    if codes and record.get("cached_authorization") is True:
        codes.append("VERIFIER_CACHED_RESULT_INVALID")

    return codes
