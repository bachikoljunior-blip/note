#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).with_name('evaluation_cache_context_binding_v1.schema.json')
FIELDS = [
 'runner_revision','runner_artifact_sha256','environment_artifact_sha256',
 'environment_transition_contract_sha256','dataset_record_sha256','codebook_sha256',
 'system_prompt_sha256','user_prompt_sha256','generation_config_sha256',
 'backend_fingerprint_sha256','sampling_contract_sha256','cache_policy_revision'
]

def load_schema(): return json.loads(SCHEMA.read_text())
def canonical_context_digest(ctx):
    return hashlib.sha256(json.dumps(ctx,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def semantic_validate(doc):
    errs=[f'schema: {e.message}' for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs: return errs
    e,c=doc['entry_context'],doc['current_context']; req=doc['reuse_request']; ce=doc['cache_entry']
    for f in FIELDS:
        if e[f] != c[f]: errs.append(f'cache context drift: {f}')
    if ce['bound_context_sha256'] != canonical_context_digest(e):
        errs.append('cache entry bound_context_sha256 does not match entry_context')
    if not req['codebook_is_empty']:
        errs.append('observed public cache scope is empty-codebook only')
    if not req['cache_hit_authorized']:
        errs.append('cache hit is not authorized by current request')
    if req['reuse_semantics'] == 'independent_replication':
        errs.append('independent replication must execute anew rather than reuse a cached outcome')
    if req['treat_as_new_independent_sample']:
        errs.append('a memoized cache hit must not be counted as a new independent sample')
    return errs

def main():
    doc=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin)
    errs=semantic_validate(doc); print(json.dumps({'valid':not errs,'errors':errs},indent=2)); raise SystemExit(0 if not errs else 1)
if __name__=='__main__': main()
