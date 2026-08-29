#!/usr/bin/env python3
import json, sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'replay_export_derivation_and_coverage_v1.schema.json').read_text())
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
    run = p['canonical_run']
    exp = p['replay_export']
    cov = p['coverage']
    level = p['authorization']['requested_level']

    if claim['expected_suite_case_count'] != cov['expected_suite_case_count']:
        errors.append('EXPECTED_SUITE_COUNT_MISMATCH')
    if exp['source_run_id'] != run['run_id']:
        errors.append('EXPORT_SOURCE_RUN_ID_MISMATCH')

    binding_ids = [x['run_id'] for x in cov['suite_case_bindings']]
    if len(binding_ids) != len(set(binding_ids)):
        errors.append('DUPLICATE_SUITE_CASE_BINDING_ID')
    if set(binding_ids) != set(cov['public_run_ids']):
        errors.append('PUBLIC_RUN_SET_BINDING_MISMATCH')

    own = [x for x in cov['suite_case_bindings'] if x['run_id'] == run['run_id']]
    if not own:
        errors.append('CANONICAL_RUN_NOT_IN_COVERAGE_BINDINGS')
    else:
        b = own[0]
        if b['canonical_trace_sha256'] != run['canonical_trace_sha256']:
            errors.append('CANONICAL_TRACE_BINDING_MISMATCH')
        if b['source_tree_sha256'] != run['source_tree_sha256']:
            errors.append('SOURCE_TREE_BINDING_MISMATCH')
        if b['model_id'] != run['model_id']:
            errors.append('MODEL_BINDING_MISMATCH')
        if b['gate_revision'] != run['gate_revision']:
            errors.append('GATE_REVISION_BINDING_MISMATCH')

    if exp['export_kind'] == 'lossless_archive':
        if not exp['full_trace']:
            errors.append('LOSSLESS_ARCHIVE_CANNOT_BE_TRUNCATED')
        if exp['paper_sha256'] is None:
            errors.append('LOSSLESS_ARCHIVE_REQUIRES_PAPER_BINDING')

    ts = exp['timestamp_binding']
    if ts['source'] == 'cache_token':
        if not ts.get('cache_token_semantics_sha256'):
            errors.append('CACHE_TOKEN_TIMESTAMP_REQUIRES_GENERATOR_SEMANTICS_PROOF')
        if _dt(ts['timestamp']) != _dt(run['executed_at']):
            errors.append('CACHE_TOKEN_TIMESTAMP_DOES_NOT_MATCH_CANONICAL_RUN')
    elif ts.get('cache_token_semantics_sha256'):
        errors.append('CACHE_TOKEN_SEMANTICS_PRESENT_FOR_NONCACHE_TIMESTAMP')

    if level in ('canonical_run_bound', 'suite_bound'):
        if not exp['full_trace']:
            errors.append('TRUNCATED_REPLAY_CANNOT_AUTHORIZE_CANONICAL_EVIDENCE')
        if exp['source_trace_sha256'] != run['canonical_trace_sha256']:
            errors.append('EXPORT_NOT_BOUND_TO_CANONICAL_TRACE')
        if ts['source'] == 'export_metadata':
            errors.append('EXPORT_METADATA_TIMESTAMP_NOT_EXECUTION_AUTHORITY')
        if _dt(ts['timestamp']) != _dt(run['executed_at']):
            errors.append('EXECUTION_TIMESTAMP_BINDING_MISMATCH')

    if level == 'suite_bound':
        if cov['suite_manifest_sha256'] is None:
            errors.append('SUITE_MANIFEST_REQUIRED')
        if len(cov['public_run_ids']) != cov['expected_suite_case_count']:
            errors.append('SUITE_PUBLIC_RUN_COUNT_MISMATCH')
        if len(cov['suite_case_bindings']) != cov['expected_suite_case_count']:
            errors.append('SUITE_BINDING_COUNT_MISMATCH')

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
