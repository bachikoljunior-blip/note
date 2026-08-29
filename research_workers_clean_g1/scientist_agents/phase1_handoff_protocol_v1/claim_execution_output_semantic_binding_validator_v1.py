#!/usr/bin/env python3
import json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA=Path(__file__).with_name('claim_execution_output_semantic_binding_v1.schema.json')
def load_schema(): return json.loads(SCHEMA.read_text())
def semantic_validate(doc):
    errs=[f'schema: {e.message}' for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs:return errs
    exe=doc['execution']; claim=doc['claim']; auth=doc['authorization']; outs=doc['outputs']
    ids=[o['output_id'] for o in outs]
    if len(ids)!=len(set(ids)): errs.append('output_id values must be unique')
    matches=[o for o in outs if o['output_id']==claim['source_output_id']]
    if len(matches)!=1: errs.append('claim must bind exactly one source_output_id')
    eligible=(exe['returncode']==0 and not exe['timed_out'] and exe['output_record_complete'])
    if exe['returncode']!=0: errs.append('failed execution cannot authorize quantitative claim')
    if exe['timed_out']: errs.append('timed-out execution cannot authorize quantitative claim')
    if not exe['output_record_complete']: errs.append('incomplete output record cannot authorize quantitative claim')
    for o in outs:
        if o['execution_entry_sha256']!=exe['entry_sha256']:
            errs.append(f"output {o['output_id']} is not bound to the authorized execution entry")
    if matches:
        o=matches[0]
        if claim['quantity_id']!=o['quantity_id']:
            errs.append('claim quantity_id does not match bound output quantity')
        if claim['normalized_unit']!=o['normalized_unit']:
            errs.append('claim normalized_unit does not match bound output unit')
        try:
            if Decimal(claim['normalized_value'])!=Decimal(o['normalized_value']):
                errs.append('claim normalized_value does not equal bound output value')
        except InvalidOperation:
            errs.append('invalid decimal normalization')
        if not o['field_locator'].strip(): errs.append('bound output requires field locator')
    tr=claim['presentation_transform']; td=claim['presentation_transform_digest']
    if tr=='identity' and td is not None: errs.append('identity presentation transform must not invent a transform digest')
    if tr!='identity' and td is None: errs.append('non-identity presentation transform requires a transform digest')
    should_authorize=eligible and len(matches)==1
    if matches:
        o=matches[0]
        should_authorize=should_authorize and claim['quantity_id']==o['quantity_id'] and claim['normalized_unit']==o['normalized_unit']
        try: should_authorize=should_authorize and Decimal(claim['normalized_value'])==Decimal(o['normalized_value'])
        except InvalidOperation: should_authorize=False
    should_authorize=should_authorize and ((tr=='identity' and td is None) or (tr!='identity' and td is not None))
    if auth['authorized']!=should_authorize:
        errs.append('authorization flag does not match semantic gate outcome')
    return errs

def main():
    d=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin);e=semantic_validate(d);print(json.dumps({'valid':not e,'errors':e},indent=2));raise SystemExit(0 if not e else 1)
if __name__=='__main__':main()
