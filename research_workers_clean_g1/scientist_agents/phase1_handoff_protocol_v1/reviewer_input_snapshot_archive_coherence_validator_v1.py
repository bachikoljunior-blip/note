#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA=Path(__file__).with_name('reviewer_input_snapshot_archive_coherence_v1.schema.json')
def load_schema(): return json.loads(SCHEMA.read_text())
def manifest_digest(items):
    payload=[{'item_id':i['item_id'],'role':i['role'],'path_hint':i['path_hint'],'content_sha256':i['content_sha256']} for i in items]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def semantic_validate(doc):
    errs=[f'schema: {e.message}' for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs:return errs
    m=doc['input_manifest']; items=m['items']; ids=[i['item_id'] for i in items]
    if len(ids)!=len(set(ids)): errs.append('input manifest item_id values must be unique')
    paths=[i['path_hint'] for i in items]
    if len(paths)!=len(set(paths)): errs.append('input manifest path_hint values must be unique')
    if m['manifest_sha256']!=manifest_digest(items): errs.append('input manifest digest does not match item snapshot')
    roles={i['role'] for i in items}
    if 'trace' not in roles: errs.append('authoritative reviewer snapshot requires a trace item')
    if 'produced_artifact' not in roles: errs.append('authoritative reviewer snapshot requires at least one produced_artifact')
    if not ({'claim_input','claim_reference'} & roles): errs.append('authoritative reviewer snapshot requires claim input or claim reference evidence')
    observed=doc['observed_item_ids']; missing=[x for x in observed if x not in ids]
    if missing: errs.append('observed_item_ids contain items outside the bound input manifest')
    if doc['verdict']['input_manifest_sha256']!=m['manifest_sha256']: errs.append('verdict is not bound to current input manifest')
    arc=doc['archive']; embedded=arc['embedded_item_ids']; ext=arc['external_refs']; extids=[x['item_id'] for x in ext]
    if len(extids)!=len(set(extids)): errs.append('external archive item_id values must be unique')
    if any(x not in ids for x in embedded+extids): errs.append('archive references an item outside the input manifest')
    if set(embedded)&set(extids): errs.append('archive item cannot be both embedded and external')
    if arc['mode']=='self_contained':
        if set(embedded)!=set(ids) or ext: errs.append('self-contained archive must embed every manifest item and have no external refs')
    else:
        if set(embedded)|set(extids)!=set(ids): errs.append('thin archive must cover every manifest item with embedded or external storage')
        byid={i['item_id']:i for i in items}
        for r in ext:
            if not r['content_addressed'] or not r['resolvable']: errs.append(f"thin archive external ref {r['item_id']} must be content-addressed and resolvable")
            if r['item_id'] in byid and r['content_sha256']!=byid[r['item_id']]['content_sha256']: errs.append(f"thin archive external ref {r['item_id']} digest mismatch")
    ree=doc['reevaluation']; prevm=ree['previous_input_manifest_sha256']; prevv=ree['previous_verdict_artifact_sha256']
    if (prevm is None)!=(prevv is None): errs.append('previous verdict and previous input manifest must be supplied together')
    if ree['reuse_previous_verdict']:
        if prevm is None: errs.append('cannot reuse previous verdict without previous identity')
        elif prevm!=m['manifest_sha256']: errs.append('previous verdict cannot be reused after input snapshot changed')
        if prevv is not None and prevv!=doc['verdict']['verdict_artifact_sha256']: errs.append('reuse_previous_verdict requires identical verdict artifact identity')
    return errs

def main():
    d=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin); e=semantic_validate(d); print(json.dumps({'valid':not e,'errors':e},indent=2)); raise SystemExit(0 if not e else 1)
if __name__=='__main__':main()
