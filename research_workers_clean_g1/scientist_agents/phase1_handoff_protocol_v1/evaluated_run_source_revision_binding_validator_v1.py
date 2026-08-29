#!/usr/bin/env python3
import json, sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'evaluated_run_source_revision_binding_v1.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def _dt(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def validate_packet(p):
    errors = []
    for e in VALIDATOR.iter_errors(p):
        errors.append('STRUCTURE:' + '/'.join(str(x) for x in e.absolute_path) + ':' + e.message)
    if errors:
        return errors

    claim = p['claim']
    impl = p['evaluated_implementation']
    manifest = p['run_manifest']
    cases = p['cases']
    auth = p['authorization']

    if manifest['kind'] != 'evaluated_run_manifest':
        errors.append('RUN_MANIFEST_REQUIRED: dataset/input manifest is not evaluated-run provenance')

    case_ids = [c['case_id'] for c in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append('DUPLICATE_CASE_ID')
    if len(cases) != claim['expected_case_count']:
        errors.append('CASE_COUNT_MISMATCH')
    if set(case_ids) != set(manifest['case_ids']):
        errors.append('CASE_SET_MISMATCH')

    if manifest['source_tree_sha256'] != impl['source_tree_sha256']:
        errors.append('SOURCE_TREE_BINDING_MISMATCH')
    if manifest['claim_gate_revision'] != impl['claim_gate_revision']:
        errors.append('CLAIM_GATE_REVISION_MISMATCH')

    if _dt(impl['source_first_public_at']) > _dt(p['publication']['published_at']):
        b = impl['bridge']
        if not (b.get('present') and b.get('evaluated_source_bundle_sha256') and b.get('bridge_statement_sha256')):
            errors.append('POSTPUBLICATION_SOURCE_WITHOUT_EVALUATED_SOURCE_BRIDGE')

    if claim['claim_edition'] != impl['edition']:
        if not auth.get('edition_equivalence_proof_sha256'):
            errors.append('CROSS_EDITION_CERTIFICATE_WITHOUT_EQUIVALENCE_PROOF')

    if auth['requested_level'] == 'cross_edition_certificate' and not auth.get('edition_equivalence_proof_sha256'):
        errors.append('CROSS_EDITION_LEVEL_REQUIRES_EQUIVALENCE_PROOF')

    if auth['requested_level'] in ('evaluated_run_bound','cross_edition_certificate'):
        for c in cases:
            for k in ('input_manifest_sha256','execution_trace_sha256','result_artifact_sha256','gate_report_sha256'):
                if not c.get(k):
                    errors.append(f'CASE_EVIDENCE_MISSING:{c.get("case_id")}:{k}')
    return errors


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: validator packet.json')
    p = json.loads(Path(sys.argv[1]).read_text())
    errors = validate_packet(p)
    print(json.dumps({'ok': not errors, 'errors': errors}, indent=2))
    raise SystemExit(0 if not errors else 2)

if __name__ == '__main__':
    main()
