#!/usr/bin/env python3
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from evaluation_memory_snapshot_binding_validator_v1 import load_schema, semantic_validate

S = "a" * 64
T = "b" * 64
U = "c" * 64
V = "d" * 64
W = "e" * 64
X = "f" * 64


def dig(v=S):
    return {"algorithm": "sha256", "value": v}


def member(mid="m1", v=S):
    return {"memory_id": mid, "content_digest": dig(v)}


def condition(cid, out):
    return {
        "condition_id": cid,
        "initial_memory_snapshot_digest": dig(S),
        "retrieval_config_digest": dig(T),
        "task_query_digest": dig(U),
        "pre_retrieval_memory_state_digest": dig(V),
        "trace_identity_level": "member_identity",
        "candidate_pool_digest": dig(W),
        "candidate_members": [member("m1", X)],
        "task_order_digest": dig(S),
        "update_ledger_digest": dig(T),
        "output_artifact_digest": dig(out),
    }


def base(level="same_retrieved_candidate_pool", online=False):
    return {
        "schema_version": 1,
        "claim_level": level,
        "environment": {
            "package_name": "scienceworld",
            "version": "1.2.2",
            "artifact_channel": "pypi_distribution",
            "artifact_filename": "scienceworld-1.2.2-py3-none-any.whl",
            "artifact_digest": dig("1" * 64),
            "source_binding": {
                "repository": "allenai/ScienceWorld",
                "commit": "1" * 40,
                "jar_blob_sha": "2" * 40,
                "archive_byte_binding": False,
                "claims_exact_package_source_commit": False
            }
        },
        "memory_pair": {
            "update_policy": "online" if online else "frozen",
            "allow_empty_pool": False,
            "condition_a": condition("A", "2" * 64),
            "condition_b": condition("B", "3" * 64),
        },
        "run_binding": {
            "runner_revision": "runner-v1",
            "runner_artifact_digest": dig("4" * 64),
            "dataset_digest": dig("5" * 64),
            "model_artifact_digest": dig("6" * 64),
            "environment_config_digest": dig("7" * 64),
            "table_binding_manifest_digest": None,
        }
    }


def cases():
    out = []
    out.append(("valid_frozen_same_M", base(), True))
    out.append(("valid_online_same_M", base(online=True), True))

    d = base(); d["memory_pair"]["condition_b"]["initial_memory_snapshot_digest"] = dig("8"*64)
    out.append(("initial_snapshot_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["pre_retrieval_memory_state_digest"] = dig("8"*64)
    out.append(("pre_retrieval_state_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["retrieval_config_digest"] = dig("8"*64)
    out.append(("retrieval_config_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["task_query_digest"] = dig("8"*64)
    out.append(("task_query_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["candidate_pool_digest"] = dig("8"*64)
    out.append(("candidate_pool_digest_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["candidate_members"] = [member("m2", X)]
    out.append(("candidate_identity_drift", d, False))
    d = base(); d["memory_pair"]["condition_b"]["trace_identity_level"] = "count_summary"
    out.append(("counts_only_not_same_M", d, False))
    d = base(online=True); d["memory_pair"]["condition_b"]["task_order_digest"] = dig("8"*64)
    out.append(("online_task_order_drift", d, False))
    d = base(online=True); d["memory_pair"]["condition_b"]["update_ledger_digest"] = None
    out.append(("online_missing_update_ledger", d, False))

    d = base(level="environment_artifact_identity"); d["environment"]["source_binding"]["claims_exact_package_source_commit"] = True
    out.append(("unbound_package_to_source_commit", d, False))

    d = base(level="evaluated_run_bundle"); d["run_binding"]["table_binding_manifest_digest"] = dig("9"*64)
    out.append(("valid_evaluated_bundle", d, True))
    d = base(level="evaluated_run_bundle")
    out.append(("missing_table_run_manifest", d, False))
    d = base(level="evaluated_run_bundle"); d["run_binding"]["table_binding_manifest_digest"] = dig("9"*64); d["memory_pair"]["condition_b"]["output_artifact_digest"] = copy.deepcopy(d["memory_pair"]["condition_a"]["output_artifact_digest"])
    out.append(("reused_output_artifact", d, False))

    d = base(level="same_retrieved_candidate_pool"); d["memory_pair"]["allow_empty_pool"] = True; d["memory_pair"]["condition_a"]["candidate_members"] = []; d["memory_pair"]["condition_b"]["candidate_members"] = []
    out.append(("valid_explicit_empty_pool", d, True))
    return out


def main():
    validator = Draft202012Validator(load_schema())
    results = []
    for name, doc, expected in cases():
        schema_ok = not list(validator.iter_errors(doc))
        sem_ok = not semantic_validate(doc)
        results.append({"case": name, "schema_valid": schema_ok, "semantic_valid": sem_ok, "expected": expected, "pass": schema_ok and sem_ok == expected})
    manifest = {
        "schema_version": 1,
        "suite": "evaluation_memory_snapshot_binding_v1",
        "cases": results,
        "structurally_valid": sum(r["schema_valid"] for r in results),
        "semantic_expected_pass": sum(r["pass"] for r in results),
        "total": len(results)
    }
    Path(__file__).with_name("evaluation_memory_snapshot_binding_test_manifest_v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    if not all(r["pass"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
