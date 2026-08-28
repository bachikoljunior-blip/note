#!/usr/bin/env python3
"""Cross-field semantic checks for verifier observability records, v3.

v3 models evidence coverage over requirement×artifact membership. A claim is
not completely observable merely because some figures exist. Each declared
requirement must have a non-empty artifact manifest and every member must be
present in the verifier-visible artifact set. Hard-negative evidence must name
an artifact that belongs to the cited requirement and match the exact visible
digest. Requirement, manifest-membership, or visible-set drift invalidates a
cached verification result.
"""

HARD_NEGATIVE = {"REJECT", "BLOCK", "PRUNE", "FORBID"}


def validate(record, context):
    codes = []
    requirements = record.get("claim_evidence_requirements", [])
    manifest = record.get("requirement_artifact_manifest", {})
    visible = record.get("visible_artifacts", {})
    coverage = record.get("coverage_status")
    disposition = record.get("disposition")

    missing_manifest = [req for req in requirements if not manifest.get(req)]
    if missing_manifest:
        codes.append("VERIFIER_REQUIREMENT_ARTIFACT_MANIFEST_MISSING")

    undeclared_manifest = [req for req in manifest if req not in requirements]
    if undeclared_manifest:
        codes.append("VERIFIER_MANIFEST_HAS_UNDECLARED_REQUIREMENT")

    missing_artifacts = []
    for req in requirements:
        for artifact_id in manifest.get(req, []):
            if artifact_id not in visible:
                missing_artifacts.append((req, artifact_id))
    if coverage == "complete" and missing_artifacts:
        codes.append("VERIFIER_MULTI_ARTIFACT_COVERAGE_INCOMPLETE")

    if coverage in {"partial", "uninspectable"} and disposition in HARD_NEGATIVE:
        codes.append("VERIFIER_HARD_REJECT_WITH_INCOMPLETE_EVIDENCE")

    if disposition in HARD_NEGATIVE:
        falsifying = record.get("falsifying_evidence", [])
        if coverage != "complete" or missing_artifacts or not falsifying:
            codes.append("VERIFIER_HARD_REJECT_UNSUPPORTED")
        else:
            for item in falsifying:
                requirement = item.get("requirement")
                artifact_id = item.get("artifact_id")
                evidence_digest = item.get("evidence_digest")
                if requirement not in requirements or artifact_id not in manifest.get(requirement, []):
                    if "VERIFIER_FALSIFIER_WRONG_REQUIREMENT_MEMBERSHIP" not in codes:
                        codes.append("VERIFIER_FALSIFIER_WRONG_REQUIREMENT_MEMBERSHIP")
                    continue
                if visible.get(artifact_id) != evidence_digest:
                    if "VERIFIER_FALSIFYING_EVIDENCE_UNBOUND" not in codes:
                        codes.append("VERIFIER_FALSIFYING_EVIDENCE_UNBOUND")

    if record.get("evidence_requirement_digest") != context.get("evidence_requirement_digest"):
        codes.append("VERIFIER_REQUIREMENT_DIGEST_STALE")

    if record.get("requirement_artifact_manifest_digest") != context.get("requirement_artifact_manifest_digest"):
        codes.append("VERIFIER_ARTIFACT_MANIFEST_DIGEST_STALE")

    if record.get("visible_evidence_digest") != context.get("visible_evidence_digest"):
        codes.append("VERIFIER_VISIBLE_EVIDENCE_DIGEST_STALE")

    if codes and record.get("cached_authorization") is True:
        codes.append("VERIFIER_CACHED_RESULT_INVALID")

    return codes
