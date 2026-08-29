#!/usr/bin/env python3
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
SCHEMA=Path(__file__).with_name('reviewer_output_nonreentry_v1.schema.json')
def load_schema(): return json.loads(SCHEMA.read_text())
def semantic_validate(doc):
    errs=[f'schema: {e.message}' for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs:return errs
    inv=doc['input_root_inventory']; ids=[x['item_id'] for x in inv]
    if len(ids)!=len(set(ids)): errs.append('input_root_inventory item_id values must be unique')
    byid={x['item_id']:x for x in inv}; visible=doc['visible_item_ids']
    if any(x not in byid for x in visible): errs.append('visible_item_ids include item outside input root inventory')
    if any(x['producer_class']=='evaluator_current' for x in inv): errs.append('current evaluator output must not exist in frozen scoring input snapshot')
    if not doc['snapshot_frozen_before_current_output']: errs.append('review input snapshot must be frozen before current evaluator output')
    prior_ids={x['item_id'] for x in inv if x['producer_class']=='evaluator_prior'}
    exposed_prior = bool(prior_ids & set(visible)) or (doc['tool_read_policy']=='root_read_all' and bool(prior_ids))
    out=doc['output_namespace']
    if doc['review_mode']=='primary_independent':
        if exposed_prior: errs.append('primary independent review must not expose prior evaluator outputs')
        if out['prior_verdict_visibility_reason']!='not_visible': errs.append('primary independent review requires prior verdict visibility reason not_visible')
        if not out['disjoint_from_input_root']: errs.append('primary independent reviewer outputs must use a namespace disjoint from the scoring input root')
    else:
        if exposed_prior and out['prior_verdict_visibility_reason']!='comparison_only': errs.append('meta-comparison prior verdict exposure must be labeled comparison_only')
    return errs

def main():
    d=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin);e=semantic_validate(d);print(json.dumps({'valid':not e,'errors':e},indent=2));raise SystemExit(0 if not e else 1)
if __name__=='__main__':main()
