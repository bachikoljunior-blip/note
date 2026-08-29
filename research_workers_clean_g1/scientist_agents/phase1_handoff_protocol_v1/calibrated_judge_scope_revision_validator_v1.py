#!/usr/bin/env python3
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
SCHEMA=Path(__file__).with_name('calibrated_judge_scope_revision_v1.schema.json')
def load_schema(): return json.loads(SCHEMA.read_text())
F=['code_revision','runner_sha256','model_identity_sha256','prompt_sha256','rubric_sha256','input_exposure_policy_sha256']
def semantic_validate(doc):
    errs=[f'schema: {e.message}' for e in Draft202012Validator(load_schema()).iter_errors(doc)]
    if errs:return errs
    cert=doc['certificate']; cj=doc['current_judge']; tgt=doc['target']; cl=doc['claim']; ref=cert['judge']
    drift=[f for f in F if ref[f]!=cj[f]]
    in_scope=tgt['domain'] in cert['domains'] and tgt['claim_type'] in cert['claim_types']
    status=cl['calibration_status']
    if not drift and in_scope:
        if status!='calibrated_in_scope': errs.append('exact matching in-scope judge must be labeled calibrated_in_scope')
        if not cl['certificate_applied']: errs.append('calibrated_in_scope requires certificate_applied=true')
    elif drift:
        if status!='uncalibrated_changed_revision': errs.append('judge fingerprint drift requires uncalibrated_changed_revision')
        if cl['certificate_applied']: errs.append('changed judge revision cannot apply old calibration certificate')
    else:
        if status!='uncalibrated_out_of_scope': errs.append('out-of-scope target requires uncalibrated_out_of_scope')
        if cl['certificate_applied']: errs.append('out-of-scope target cannot apply calibration certificate')
    if cl['authority_level']=='final_scientific_authority': errs.append('human-calibrated automated judge remains benchmark evidence, not final scientific authority')
    if not cl['downstream_human_or_scientific_verification_required']: errs.append('downstream human/scientific verification must remain required')
    m=cert['metrics']
    if m['sample_n']<2: errs.append('calibration certificate requires at least two human-calibrated samples')
    return errs

def main():
    d=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else json.load(sys.stdin);e=semantic_validate(d);print(json.dumps({'valid':not e,'errors':e},indent=2));raise SystemExit(0 if not e else 1)
if __name__=='__main__':main()
