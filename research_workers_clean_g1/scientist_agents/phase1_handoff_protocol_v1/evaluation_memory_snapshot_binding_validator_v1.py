#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

HEX = re.compile(r"^[0-9a-f]+$")


def load_schema():
    return json.loads(Path(__file__).with_name("evaluation_memory_snapshot_binding_v1.schema.json").read_text())


def digest_key(d):
    return (d["algorithm"], d["value"])


def validate_digest_shape(d, label, errors):
    value = d["value"]
    algo = d["algorithm"]
    expected = 64 if algo == "sha256" else 40
    if len(value) != expected or not HEX.fullmatch(value):
        errors.append(f"{label}: {algo} digest must be {expected} lowercase hex chars")


def semantic_validate(doc):
    errors = []
    schema_errors = sorted(Draft202012Validator(load_schema()).iter_errors(doc), key=lambda e: list(e.path))
    if schema_errors:
        return ["schema: " + e.message for e in schema_errors]

    env = doc["environment"]
    validate_digest_shape(env["artifact_digest"], "environment.artifact_digest", errors)
    if env["artifact_channel"] == "pypi_distribution" and env["artifact_digest"]["algorithm"] != "sha256":
        errors.append("PyPI distribution identity requires SHA256 of the exact distribution artifact")

    source = env.get("source_binding")
    if source and source["claims_exact_package_source_commit"] and not source["archive_byte_binding"]:
        errors.append("exact package-to-source-commit attribution requires archive_byte_binding=true")

    mp = doc["memory_pair"]
    a, b = mp["condition_a"], mp["condition_b"]
    if a["condition_id"] == b["condition_id"]:
        errors.append("paired conditions must have distinct condition_id values")

    for name, c in (("condition_a", a), ("condition_b", b)):
        for field in (
            "initial_memory_snapshot_digest", "retrieval_config_digest", "task_query_digest",
            "pre_retrieval_memory_state_digest", "candidate_pool_digest", "output_artifact_digest"
        ):
            validate_digest_shape(c[field], f"{name}.{field}", errors)
        for i, member in enumerate(c["candidate_members"]):
            validate_digest_shape(member["content_digest"], f"{name}.candidate_members[{i}].content_digest", errors)
        for opt in ("task_order_digest", "update_ledger_digest"):
            if c.get(opt) is not None:
                validate_digest_shape(c[opt], f"{name}.{opt}", errors)

    rb = doc["run_binding"]
    for field in ("runner_artifact_digest", "dataset_digest", "model_artifact_digest", "environment_config_digest"):
        validate_digest_shape(rb[field], f"run_binding.{field}", errors)
    if rb["table_binding_manifest_digest"] is not None:
        validate_digest_shape(rb["table_binding_manifest_digest"], "run_binding.table_binding_manifest_digest", errors)

    level = doc["claim_level"]
    if level in ("same_initial_memory_snapshot", "same_retrieved_candidate_pool", "evaluated_run_bundle"):
        if digest_key(a["initial_memory_snapshot_digest"]) != digest_key(b["initial_memory_snapshot_digest"]):
            errors.append("same-initial-memory claim requires identical initial memory snapshot digests")

    if level in ("same_retrieved_candidate_pool", "evaluated_run_bundle"):
        if a["trace_identity_level"] != "member_identity" or b["trace_identity_level"] != "member_identity":
            errors.append("strong same-M claim requires member_identity traces; count summaries are insufficient")
        if digest_key(a["retrieval_config_digest"]) != digest_key(b["retrieval_config_digest"]):
            errors.append("same-M claim requires identical retrieval configuration digests")
        if digest_key(a["task_query_digest"]) != digest_key(b["task_query_digest"]):
            errors.append("same-M claim requires identical task/query digests")
        if digest_key(a["pre_retrieval_memory_state_digest"]) != digest_key(b["pre_retrieval_memory_state_digest"]):
            errors.append("same-M claim requires identical pre-retrieval memory-state digests")
        if digest_key(a["candidate_pool_digest"]) != digest_key(b["candidate_pool_digest"]):
            errors.append("same-M claim requires identical candidate-pool digests")
        members_a = [(m["memory_id"], digest_key(m["content_digest"])) for m in a["candidate_members"]]
        members_b = [(m["memory_id"], digest_key(m["content_digest"])) for m in b["candidate_members"]]
        if members_a != members_b:
            errors.append("same-M claim requires identical ordered candidate member IDs and content digests")
        if not mp["allow_empty_pool"] and not members_a:
            errors.append("candidate pool is empty but allow_empty_pool=false")
        if mp["update_policy"] == "online":
            for field in ("task_order_digest", "update_ledger_digest"):
                if a.get(field) is None or b.get(field) is None:
                    errors.append(f"online-memory same-M claim requires {field} in both conditions")
                elif digest_key(a[field]) != digest_key(b[field]):
                    errors.append(f"online-memory same-M claim requires identical {field} values")

    if level == "evaluated_run_bundle":
        if rb["table_binding_manifest_digest"] is None:
            errors.append("evaluated-run attribution requires a table/run binding manifest digest")
        if digest_key(a["output_artifact_digest"]) == digest_key(b["output_artifact_digest"]):
            errors.append("paired evaluated conditions must bind distinct output artifacts")

    return errors


def main():
    doc = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else json.load(sys.stdin)
    errors = semantic_validate(doc)
    out = {"valid": not errors, "errors": errors}
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
