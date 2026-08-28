#!/usr/bin/env python3
"""Cross-field semantic checks for verifier observability records, v2.

v2 keeps the v1 JSON shape but tightens hard-negative evidence binding: every
falsifying-evidence claim used to REJECT/BLOCK/PRUNE/FORBID must name a declared
evidence requirement and carry exactly the digest that is visible to the
verifier for that requirement. This prevents a verifier from citing a stale or
out-of-scope artifact while claiming complete observability.
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
        else:
            for item in falsifying:
                requirement = item.get("requirement")
                evidence_digest = item.get("evidence_digest")
                if requirement not in requirements or visible.get(requirement) != evidence_digest:
                    if "VERIFIER_FALSIFYING_EVIDENCE_UNBOUND" not in codes:
                        codes.append("VERIFIER_FALSIFYING_EVIDENCE_UNBOUND")

    if record.get("evidence_requirement_digest") != context.get("evidence_requirement_digest"):
        codes.append("VERIFIER_REQUIREMENT_DIGEST_STALE")

    if record.get("visible_evidence_digest") != context.get("visible_evidence_digest"):
        codes.append("VERIFIER_VISIBLE_EVIDENCE_DIGEST_STALE")

    if codes and record.get("cached_authorization") is True:
        codes.append("VERIFIER_CACHED_RESULT_INVALID")

    return codes
