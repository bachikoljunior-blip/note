#!/usr/bin/env python3
"""
Source-equivalent algebra validation for the released CPO + TRL + Transformers +
Accelerate + DeepSpeed gradient-accumulation composition.

This does NOT execute the pinned PyTorch 2.8.0 + DeepSpeed 0.16.4 binaries.
It validates the scalar/vector algebra implied by the pinned public sources:

- CPO release 9429452...: mask grad scale includes / current_gradient_accumulation_steps.
- TRL v0.27.0 GRPO: policy loss includes / current_gradient_accumulation_steps.
- Transformers v4.57.3: DeepSpeed training_step passes scale_wrt_gas=False.
- Accelerate v1.11.0: DeepSpeed backward delegates to engine backward.
- DeepSpeed v0.16.4: loss GAS scaling occurs only when scale_wrt_gas=True.
- DeepSpeed ZeRO-3 reduce-scatter averages by world size (established in prior role-local checkpoint).

Question tested:
Does gradient accumulation add another attenuation to the already-established
owner-only ZeRO-3 CPO regularizer attenuation of 1/world_size?

Expected from source composition:
- policy/data gradient after one accumulation group = mean over microbatches and ranks.
- released owner-only CPO regularizer after one group = R / world_size.
- multiplying owner-only injection by world_size (separate correction axis) = R.
- no residual factor of 1/G remains, including short final accumulation groups.
"""

import random
import json
import hashlib

SEED = 20260828
TOL = 1e-12
rng = random.Random(SEED)

def simulate_case(world_size: int, group_size: int, ncoords: int = 37, ndata: int = 19):
    owners = [rng.randrange(world_size) for _ in range(ncoords)]
    regularizer = [rng.uniform(-3.0, 3.0) for _ in range(ncoords)]
    data = [
        [[rng.uniform(-2.0, 2.0) for _ in range(ndata)] for _ in range(world_size)]
        for _ in range(group_size)
    ]

    final_data = [0.0] * ndata
    final_release = [0.0] * ncoords
    final_corrected = [0.0] * ncoords

    for micro in range(group_size):
        # TRL has already divided each microbatch policy loss by the *current*
        # accumulation-group length. DeepSpeed GAS scaling is disabled by
        # Transformers for this path, then DP reduction averages over W ranks.
        for k in range(ndata):
            final_data[k] += (
                sum(data[micro][rank][k] / group_size for rank in range(world_size))
                / world_size
            )

        # CPO similarly divides the owner-only regularizer contribution by the
        # current accumulation-group length before backward. ZeRO-3 DP averaging
        # then applies 1/W to an owner-only term.
        for j in range(ncoords):
            released_rank_sum = sum(
                regularizer[j] / group_size if rank == owners[j] else 0.0
                for rank in range(world_size)
            )
            final_release[j] += released_rank_sum / world_size

            corrected_rank_sum = sum(
                regularizer[j] * world_size / group_size if rank == owners[j] else 0.0
                for rank in range(world_size)
            )
            final_corrected[j] += corrected_rank_sum / world_size

    expected_data = [
        sum(
            data[micro][rank][k]
            for micro in range(group_size)
            for rank in range(world_size)
        )
        / (group_size * world_size)
        for k in range(ndata)
    ]
    expected_release = [x / world_size for x in regularizer]
    expected_corrected = list(regularizer)

    return {
        "world_size": world_size,
        "group_size": group_size,
        "max_abs_data_error": max(abs(a-b) for a,b in zip(final_data, expected_data)),
        "max_abs_released_reg_error": max(abs(a-b) for a,b in zip(final_release, expected_release)),
        "max_abs_corrected_reg_error": max(abs(a-b) for a,b in zip(final_corrected, expected_corrected)),
    }

def main():
    rows = []
    for world_size in [1, 2, 3, 4, 8, 16]:
        # Includes full GAS=4 and short final groups 1/2/3, plus other lengths.
        for group_size in [1, 2, 3, 4, 5, 7]:
            for _ in range(50):
                rows.append(simulate_case(world_size, group_size))

    maxima = {
        "data": max(r["max_abs_data_error"] for r in rows),
        "released_regularizer": max(r["max_abs_released_reg_error"] for r in rows),
        "corrected_regularizer": max(r["max_abs_corrected_reg_error"] for r in rows),
    }
    passed = all(v <= TOL for v in maxima.values())
    result = {
        "schema_version": 1,
        "seed": SEED,
        "tolerance": TOL,
        "cases": len(rows),
        "world_sizes": [1, 2, 3, 4, 8, 16],
        "accumulation_group_sizes": [1, 2, 3, 4, 5, 7],
        "max_abs_error": maxima,
        "passed": passed,
        "conclusion": (
            "Under the pinned source composition, gradient accumulation introduces no "
            "additional residual 1/G attenuation. Released owner-only ZeRO-3 CPO remains "
            "R/world_size after a complete accumulation group; a separate owner injection "
            "*world_size correction recovers R. Dynamic short final groups are also correct."
        ),
        "scope": (
            "Source-equivalent algebra only; not pinned PyTorch 2.8.0 + DeepSpeed 0.16.4 "
            "distributed binary execution and not a training-quality result."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
