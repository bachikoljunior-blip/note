#!/usr/bin/env python3
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).with_name('skill_replay_admission_sidecar_v1.schema.json')

def load_schema(): return json.loads(SCHEMA.read_text())

def validate_semantic(doc):
    errs = [f"schema: {e.message}" for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs: return errs
    tx, env, dec = doc['transaction'], doc['environment'], doc['decision']
    reps = doc['replays']
    if tx['pre_codebook_sha256'] == tx['candidate_codebook_sha256']:
        errs.append('candidate codebook must differ from pre-codebook when candidate functions are present')
    names = [x['name'] for x in tx['candidate_functions']]
    if len(names) != len(set(names)):
        errs.append('candidate function names must be unique')
    tasks = tx['successful_task_ids']
    replay_tasks = [r['task_id'] for r in reps]
    if len(replay_tasks) != len(set(replay_tasks)):
        errs.append('at most one replay record per successful task_id')
    passed = [r['used_new_helper'] and r['solution_success'] and r.get('error_class') is None for r in reps]
    if doc['claim_level'] == 'replay_verified_admission':
        if not tx['allow_replay']:
            errs.append('replay_verified_admission requires allow_replay=true')
        if env['replay_equivalence_packet_sha256'] is None:
            errs.append('replay_verified_admission requires an environment replay-equivalence packet')
        if replay_tasks != tasks:
            errs.append('replay_verified_admission requires exactly one ordered replay for every successful task_id')
    if tx['allow_replay']:
        expected_commit = bool(reps) and replay_tasks == tasks and all(passed)
        if expected_commit and dec['status'] != 'commit':
            errs.append('all required replays passed, so decision must be commit')
        if not expected_commit and dec['status'] != 'revert':
            errs.append('missing/failed replay requires revert')
    else:
        if reps:
            errs.append('allow_replay=false must not claim executed replay records')
        if dec['status'] != 'commit':
            errs.append('no-replay branch with a constructed candidate is a static-validation commit')
    expected_post = tx['candidate_codebook_sha256'] if dec['status']=='commit' else tx['pre_codebook_sha256']
    if dec['post_codebook_sha256'] != expected_post:
        errs.append('post-codebook digest does not match commit/revert transaction semantics')
    return errs

def main():
    doc=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin)
    errs=validate_semantic(doc); print(json.dumps({'valid':not errs,'errors':errs},indent=2)); raise SystemExit(bool(errs))
if __name__=='__main__': main()
