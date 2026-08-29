#!/usr/bin/env python3
import copy, json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from replay_export_derivation_and_coverage_validator_v1 import validate_packet, SCHEMA

HERE = Path(__file__).resolve().parent
H = lambda c: c * 64

BASE = {
  "schema_version": 1,
  "claim": {"claim_id": "suite-claim", "expected_suite_case_count": 3},
  "canonical_run": {
    "run_id": "run-a", "source_tree_sha256": H('1'), "model_id": "model-v1", "gate_revision": "gate-v1",
    "canonical_trace_sha256": H('2'), "structured_record_sha256": H('3'), "markdown_sha256": H('4'), "pdf_sha256": H('5'),
    "executed_at": "2026-08-12T09:30:00Z"
  },
  "replay_export": {
    "export_revision": "export-v1", "export_builder_sha256": H('6'), "export_kind": "lossless_archive",
    "source_run_id": "run-a", "source_trace_sha256": H('2'), "script_sha256": H('7'), "log_sha256": H('8'), "paper_sha256": H('5'),
    "full_trace": True, "transformations_sha256": H('9'), "immutable_export_digest": H('a'),
    "timestamp_binding": {"source": "canonical_run_record", "timestamp": "2026-08-12T09:30:00Z", "cache_token_semantics_sha256": None}
  },
  "coverage": {
    "expected_suite_case_count": 3, "suite_manifest_sha256": H('b'), "public_run_ids": ["run-a", "run-b", "run-c"], "selection_rule_sha256": None,
    "suite_case_bindings": [
      {"run_id":"run-a","canonical_trace_sha256":H('2'),"source_tree_sha256":H('1'),"model_id":"model-v1","gate_revision":"gate-v1"},
      {"run_id":"run-b","canonical_trace_sha256":H('c'),"source_tree_sha256":H('1'),"model_id":"model-v1","gate_revision":"gate-v1"},
      {"run_id":"run-c","canonical_trace_sha256":H('d'),"source_tree_sha256":H('1'),"model_id":"model-v1","gate_revision":"gate-v1"}
    ]
  },
  "authorization": {"requested_level": "suite_bound"}
}


def set_path(obj, path, value):
    parts = path.split('.')
    cur = obj
    for p in parts[:-1]:
        cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    last = parts[-1]
    if isinstance(cur, list): cur[int(last)] = value
    else: cur[last] = value


def main():
    tests = json.loads((HERE / 'replay_export_derivation_and_coverage_tests_v1.json').read_text())['tests']
    structural = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    out = []
    for t in tests:
        p = copy.deepcopy(BASE)
        for path, value in t['mutations']:
            set_path(p, path, value)
        struct_ok = not list(structural.iter_errors(p))
        errors = validate_packet(p)
        ok = not errors
        out.append({"name":t['name'],"expect_ok":t['expect_ok'],"structurally_valid":struct_ok,"actual_ok":ok,"matched":ok==t['expect_ok'],"errors":errors})
    result = {
      "schema_version":1,
      "structurally_valid_count":sum(x['structurally_valid'] for x in out),
      "case_count":len(out),
      "expected_semantic_match_count":sum(x['matched'] for x in out),
      "results":out
    }
    print(json.dumps(result, indent=2))
    if result['structurally_valid_count'] != len(out) or result['expected_semantic_match_count'] != len(out):
        raise SystemExit(2)

if __name__ == '__main__': main()
