"""Source-isolated OpenCompass 0.5.1 vs 0.5.2 fixture for DeMix reconstruction.

This is a public-reconstruction fixture, NOT evidence of the DeMix authors' exact
OpenCompass model wrapper or runtime. It intentionally fixes the simple
HuggingFaceCausalLM path because opencompass/models/huggingface.py is byte-identical
at the two source anchors being compared.

Safety note: HumanEval/MBPP evaluation may execute generated code. Compare raw
inference hashes first; run code evaluators only inside an appropriate isolated
sandbox.
"""

from opencompass.models import HuggingFaceCausalLM
from opencompass.configs.datasets.ARC_e.ARC_e_ppl_a450bd import ARC_e_datasets
from opencompass.configs.datasets.hellaswag.hellaswag_ppl_47bff9 import hellaswag_datasets
from opencompass.configs.datasets.piqa.piqa_ppl_1cf9f0 import piqa_datasets
from opencompass.configs.datasets.siqa.siqa_ppl_ced5f6 import siqa_datasets
from opencompass.configs.datasets.winogrande.winogrande_ll_c5cf57 import winogrande_datasets
from opencompass.configs.datasets.mbpp.deprecated_mbpp_gen_1e1056 import mbpp_datasets
from opencompass.configs.datasets.humaneval.humaneval_gen_8e312c import humaneval_datasets
from opencompass.configs.datasets.gsm8k.gsm8k_gen_1d7fe4 import gsm8k_datasets
from opencompass.configs.datasets.math.math_gen_265cce import math_datasets

HF_REPO = "sshleifer/tiny-gpt2"
HF_REVISION = "5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be"

models = [
    dict(
        type=HuggingFaceCausalLM,
        abbr="tiny-gpt2-track-a1",
        path=HF_REPO,
        tokenizer_path=HF_REPO,
        tokenizer_kwargs=dict(
            revision=HF_REVISION,
            padding_side="left",
            truncation_side="left",
        ),
        model_kwargs=dict(
            revision=HF_REVISION,
            torch_dtype="torch.float",
        ),
        generation_kwargs=dict(
            do_sample=False,
            use_cache=True,
        ),
        pad_token_id=50256,
        max_seq_len=1024,
        max_out_len=512,
        batch_size=1,
        batch_padding=False,
        mode="none",
        run_cfg=dict(num_gpus=0, num_procs=1),
    )
]

# Keep the reconstruction order explicit and stable.
datasets = [
    *ARC_e_datasets,
    *hellaswag_datasets,
    *piqa_datasets,
    *siqa_datasets,
    *winogrande_datasets,
    *mbpp_datasets,
    *humaneval_datasets,
    *gsm8k_datasets,
    *math_datasets,
]
