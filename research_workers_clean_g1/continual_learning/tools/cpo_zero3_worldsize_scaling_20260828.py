#!/usr/bin/env python3
from __future__ import annotations
import json
CPO_COMMIT="9429452cb536a9e713b73b91c0011b96df44962c"
CPO_TRAINER_BLOB="2715d5f79fd45fcbc0f7e4155d82f2042042a358"
CPO_2B_LAUNCHER_BLOB="ecfa0dafec9bb813646ebef789dddd15e9158fe2"
CPO_4B_LAUNCHER_BLOB="155ccbba4034fb34521f8edd0f9b85321cfa3dff"
CPO_8B_LAUNCHER_BLOB="54931993f3e98259c8ce89f82999fb552be6568f"
DEEPSPEED_COMMIT="e2dc3eeb1923073e32739596a4fd051417d4ff92"
DEEPSPEED_COLLECTIVE_BLOB="2fadce52222cda680600253ae840f84b89bda7ed"
DEEPSPEED_HOOK_HELPER_BLOB="1d32775fe64a8e9bf1bff5df6aaa111c2974d53d"
def avg(xs): return sum(xs)/len(xs)
def main():
    rows=[]
    for w in (1,2,4,8):
        z2=avg([1.0]*w)
        z3=avg([1.0]+[0.0]*(w-1))
        rows.append({"world_size":w,"zero2_relative_regularizer":z2,
                     "zero3_owner_only_relative_regularizer":z3,
                     "lambda_100_equivalent_zero2":100*z2,
                     "lambda_100_equivalent_zero3":100*z3})
    assert rows[-1]["zero3_owner_only_relative_regularizer"]==0.125
    out={"schema_version":1,
         "scope":"Static/source-locked gradient-scaling consequence; no live H100/8-GPU run and no claim that public release semantics generated paper tables.",
         "source_contract":{"cpo_release_commit":CPO_COMMIT,"cpo_trainer_blob":CPO_TRAINER_BLOB,
             "cpo_2b_launcher_blob":CPO_2B_LAUNCHER_BLOB,"cpo_4b_launcher_blob":CPO_4B_LAUNCHER_BLOB,
             "cpo_8b_launcher_blob":CPO_8B_LAUNCHER_BLOB,"deepspeed_0_16_4_commit":DEEPSPEED_COMMIT,
             "deepspeed_reduce_scatter_blob":DEEPSPEED_COLLECTIVE_BLOB,
             "deepspeed_hook_helper_blob":DEEPSPEED_HOOK_HELPER_BLOB,
             "pytorch_paper_runtime":"2.8.0 per public CPO README"},
         "premises_verified_from_public_source":[
             "CPO ZeRO-3 computes pending regularizer coordinates only for the current rank's parameter partition.",
             "CPO injects those pending values with Tensor.register_hook.",
             "DeepSpeed 0.16.4 uses register_post_accumulate_grad_hook for its gradient-reduction hook on torch>=2.1.",
             "PyTorch 2.8 hook order runs Tensor.register_hook before post-accumulate-grad hooks.",
             "DeepSpeed 0.16.4 reduce_scatter_coalesced divides the full gradient buffer by data-parallel world size before reduce-scatter.",
             "Public CPO launchers use ZeRO-2 for 2B and ZeRO-3 for 4B/8B; README states eight GPUs for RL methods."],
         "derivation":"For a protected coordinate owned by rank r, CPO's Tensor hook adds g only on r before DeepSpeed's post-accumulate reduction. DeepSpeed averages full gradients across W data-parallel ranks, so that coordinate contributes g/W after reduction. In ZeRO-2, every rank injects g at the same protected coordinate, so averaging preserves g.",
         "rows":rows,
         "paper_lambda_100_public_launcher_implication_at_8_gpus":{"2B_zero2":100.0,"4B_zero3":12.5,"8B_zero3":12.5},
         "logging_note":"CPO's ZeRO-3 mask_loss logger also averages rank-local partial masked losses with nanmean, so the logged value is likewise approximately 1/W of the sum of per-tensor masked means, absent empty/uneven-partition edge effects.",
         "not_established":["A live 8-GPU DeepSpeed reproduction.","Whether the paper tables were generated from exactly this public release.","Whether authors compensated externally in unreleased code/config.","The quantitative impact on retention/adaptation metrics."]}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
