#!/usr/bin/env python3
"""
Decision-statistic mismatch microbenchmark for repeated LLM inference.

Measure how often a fast/nondeterministic execution differs from a canonical
execution at progressively more decision-relevant layers:

  response object -> emitted tokens/text -> binary score pair -> oriented sign.

For paired binary evaluation, the oriented sign is
    Z = candidate_correct - incumbent_correct in {-1, 0, +1}.

The compare command is Python-stdlib only. collect optionally uses vLLM.

Recommended use:
  VLLM_BATCH_INVARIANT=1 python decision_stat_mismatch_microbenchmark.py collect \
      --output canonical.jsonl --model Qwen/Qwen2.5-0.5B-Instruct --repeats 5

  env -u VLLM_BATCH_INVARIANT python decision_stat_mismatch_microbenchmark.py collect \
      --output fast.jsonl --model Qwen/Qwen2.5-0.5B-Instruct --repeats 20

  python decision_stat_mismatch_microbenchmark.py compare \
      --canonical canonical.jsonl --fast fast.jsonl

Scope guard: mismatch estimates apply only to the exact recorded model/runtime/
hardware/configuration fingerprint. They are not portable determinism claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ANSWER_RE = re.compile(r"<answer>\s*([ABCD])\s*</answer>", re.IGNORECASE)

QUESTIONS = [
    ("q01", "What is 2 + 2?", ["3", "4", "5", "6"], "B"),
    ("q02", "Which number is prime?", ["21", "27", "29", "33"], "C"),
    ("q03", "What is 7 × 8?", ["54", "56", "58", "64"], "B"),
    ("q04", "Which fraction equals one half?", ["2/3", "3/8", "4/8", "5/8"], "C"),
    ("q05", "What is 15 - 9?", ["4", "5", "6", "7"], "C"),
    ("q06", "Which is the largest?", ["0.7", "0.67", "0.706", "0.69"], "C"),
    ("q07", "What is the next even integer after 18?", ["19", "20", "21", "22"], "B"),
    ("q08", "Which expression equals 12?", ["3+8", "2×6", "20-7", "24/3"], "B"),
    ("q09", "How many sides does a hexagon have?", ["5", "6", "7", "8"], "B"),
    ("q10", "Which is a multiple of 9?", ["42", "45", "52", "64"], "B"),
    ("q11", "What is 3 squared?", ["6", "8", "9", "12"], "C"),
    ("q12", "Which value is smallest?", ["-1", "0", "1", "2"], "A"),
    ("q13", "What is 100 divided by 4?", ["20", "25", "30", "40"], "B"),
    ("q14", "Which angle is a right angle?", ["45°", "60°", "90°", "120°"], "C"),
    ("q15", "What is the remainder of 17 divided by 5?", ["1", "2", "3", "4"], "B"),
    ("q16", "Which decimal equals three quarters?", ["0.25", "0.5", "0.75", "0.8"], "C"),
]

CANDIDATE_STYLE = (
    "Answer the multiple-choice question. Put the answer tag first, then one short reason. "
    "Use exactly one tag of the form <answer>A</answer>.\n"
)
INCUMBENT_STYLE = (
    "Solve the multiple-choice question briefly. End with exactly one tag of the form "
    "<answer>A</answer>.\n"
)


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(obj: Any) -> str:
    return hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()


def render_question(stem: str, choices: list[str]) -> str:
    letters = "ABCD"
    return stem + "\n" + "\n".join(f"{letters[i]}. {c}" for i, c in enumerate(choices))


def parse_answer(text: str) -> str | None:
    m = ANSWER_RE.search(text)
    return m.group(1).upper() if m else None


def score_text(text: str, gold: str) -> int:
    return int(parse_answer(text) == gold)


def earliest_certificate_token(tokenizer: Any, token_ids: list[int]) -> int | None:
    """Earliest token prefix after which the frozen first-match scorer is fixed."""
    for i in range(1, len(token_ids) + 1):
        text = tokenizer.decode(token_ids[:i], skip_special_tokens=True)
        if ANSWER_RE.search(text):
            return i
    return None


def make_prompts() -> list[dict[str, Any]]:
    rows = []
    for qid, stem, choices, gold in QUESTIONS:
        body = render_question(stem, choices)
        for side, prefix in (("candidate", CANDIDATE_STYLE), ("incumbent", INCUMBENT_STYLE)):
            rows.append({"case_id": qid, "side": side, "gold": gold, "prompt": prefix + body})
    return rows


def _logprob_payload(output: Any) -> list[Any] | None:
    lp = getattr(output, "logprobs", None)
    if lp is None:
        return None
    result = []
    for step in lp:
        if step is None:
            result.append(None)
            continue
        row = []
        for tok_id, info in sorted(step.items(), key=lambda kv: int(kv[0])):
            row.append({
                "token_id": int(tok_id),
                "logprob": float(getattr(info, "logprob", float("nan"))),
                "rank": getattr(info, "rank", None),
                "decoded_token": getattr(info, "decoded_token", None),
            })
        result.append(row)
    return result


def collect(args: argparse.Namespace) -> None:
    try:
        import torch
        import vllm
        from vllm import LLM, SamplingParams
    except Exception as e:
        raise SystemExit(
            "collect requires vLLM + torch. compare/selftest are stdlib-only. "
            f"Import error: {e}"
        )

    prompts = make_prompts()
    prompt_texts = [r["prompt"] for r in prompts]
    batch_invariant = os.getenv("VLLM_BATCH_INVARIANT", "0") == "1"
    llm_kwargs: dict[str, Any] = {
        "model": args.model,
        "tensor_parallel_size": args.tensor_parallel_size,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "max_num_seqs": args.max_num_seqs,
    }
    if args.disable_fuse_allreduce_rms:
        llm_kwargs["compilation_config"] = {"pass_config": {"fuse_allreduce_rms": False}}
    llm = LLM(**llm_kwargs)
    tokenizer = llm.get_tokenizer()
    sp = SamplingParams(
        temperature=0.0,
        max_tokens=args.max_tokens,
        seed=args.seed,
        logprobs=args.logprobs,
    )

    meta = {
        "record_type": "meta",
        "schema_version": 1,
        "created_unix": time.time(),
        "model": args.model,
        "vllm_version": getattr(vllm, "__version__", "unknown"),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "batch_invariant": batch_invariant,
        "tensor_parallel_size": args.tensor_parallel_size,
        "max_num_seqs": args.max_num_seqs,
        "disable_fuse_allreduce_rms": args.disable_fuse_allreduce_rms,
        "sampling": {"temperature": 0.0, "max_tokens": args.max_tokens, "seed": args.seed, "logprobs": args.logprobs},
        "scorer": "first complete <answer>[A-D]</answer> tag; missing/malformed => incorrect",
        "question_count": len(QUESTIONS),
    }

    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(stable_json(meta) + "\n")
        for repeat in range(args.repeats):
            outputs = llm.generate(prompt_texts, sp, use_tqdm=False)
            if len(outputs) != len(prompts):
                raise RuntimeError("vLLM returned unexpected output count")
            for spec, req in zip(prompts, outputs):
                o = req.outputs[0]
                token_ids = [int(x) for x in o.token_ids]
                text = o.text
                logprobs = _logprob_payload(o)
                score = score_text(text, spec["gold"])
                cert_tok = earliest_certificate_token(tokenizer, token_ids)
                response_projection = {"token_ids": token_ids, "text": text, "logprobs": logprobs}
                record = {
                    "record_type": "sample",
                    "case_id": spec["case_id"],
                    "side": spec["side"],
                    "repeat": repeat,
                    "gold": spec["gold"],
                    "text": text,
                    "token_ids": token_ids,
                    "score": score,
                    "parsed_answer": parse_answer(text),
                    "response_hash": sha256_json(response_projection),
                    "token_hash": sha256_json(token_ids),
                    "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "full_tokens": len(token_ids),
                    "certificate_token": cert_tok,
                    "certificate_fraction": cert_tok / len(token_ids) if cert_tok is not None and token_ids else None,
                }
                f.write(stable_json(record) + "\n")


def load_jsonl(path: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    meta = None
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("record_type") == "meta":
                meta = obj
            elif obj.get("record_type") == "sample":
                rows.append(obj)
    return meta, rows


def _index(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, str, int], dict[str, Any]]:
    out = {}
    for r in rows:
        key = (r["case_id"], r["side"], int(r["repeat"]))
        if key in out:
            raise ValueError(f"duplicate sample key {key}")
        out[key] = r
    return out


def compare(args: argparse.Namespace) -> None:
    can_meta, can_rows = load_jsonl(args.canonical)
    fast_meta, fast_rows = load_jsonl(args.fast)
    can = _index(can_rows)
    fast = _index(fast_rows)
    can_repeats = sorted({k[2] for k in can})
    if not can_repeats:
        raise SystemExit("canonical file has no samples")
    canonical_repeat = can_repeats[0]

    canonical_unstable = []
    by_case_side = defaultdict(list)
    for k, r in can.items():
        by_case_side[(k[0], k[1])].append(r)
    for key, rs in by_case_side.items():
        hashes = {r["response_hash"] for r in rs}
        if len(hashes) > 1:
            canonical_unstable.append({"case_side": key, "distinct_response_hashes": len(hashes)})

    side_n = 0
    side_mismatch = defaultdict(int)
    pair_n = 0
    pair_bit_mismatch = 0
    pair_sign_mismatch = 0
    concordant_subtype_swaps = 0
    cert_fracs = []

    fast_repeats = sorted({k[2] for k in fast})
    case_ids = sorted({k[0] for k in fast})
    for rep in fast_repeats:
        for case_id in case_ids:
            side_records = {}
            canonical_records = {}
            missing = False
            for side in ("candidate", "incumbent"):
                fk = (case_id, side, rep)
                ck = (case_id, side, canonical_repeat)
                if fk not in fast or ck not in can:
                    missing = True
                    break
                fr, cr = fast[fk], can[ck]
                side_records[side] = fr
                canonical_records[side] = cr
                side_n += 1
                for field, name in (("response_hash", "response"), ("token_hash", "tokens"), ("text_hash", "text"), ("score", "score_bit")):
                    if fr[field] != cr[field]:
                        side_mismatch[name] += 1
                if fr.get("certificate_fraction") is not None:
                    cert_fracs.append(float(fr["certificate_fraction"]))
            if missing:
                continue

            pair_n += 1
            cbit_fast = int(side_records["candidate"]["score"])
            ibit_fast = int(side_records["incumbent"]["score"])
            cbit_can = int(canonical_records["candidate"]["score"])
            ibit_can = int(canonical_records["incumbent"]["score"])
            fast_pair = (cbit_fast, ibit_fast)
            can_pair = (cbit_can, ibit_can)
            z_fast = cbit_fast - ibit_fast
            z_can = cbit_can - ibit_can
            if fast_pair != can_pair:
                pair_bit_mismatch += 1
            if z_fast != z_can:
                pair_sign_mismatch += 1
            if fast_pair != can_pair and z_fast == z_can:
                concordant_subtype_swaps += 1

    def rate(x: int, n: int) -> float | None:
        return x / n if n else None

    result = {
        "schema_version": 1,
        "canonical_meta": can_meta,
        "fast_meta": fast_meta,
        "canonical_repeat_used": canonical_repeat,
        "canonical_unstable_case_sides": canonical_unstable,
        "side_comparisons": side_n,
        "pair_comparisons": pair_n,
        "mismatch_rates": {
            "r_response_object": rate(side_mismatch["response"], side_n),
            "r_tokens": rate(side_mismatch["tokens"], side_n),
            "r_text": rate(side_mismatch["text"], side_n),
            "r_score_bit_per_side": rate(side_mismatch["score_bit"], side_n),
            "r_score_pair": rate(pair_bit_mismatch, pair_n),
            "r_oriented_sign": rate(pair_sign_mismatch, pair_n),
            "r_concordant_subtype_swap": rate(concordant_subtype_swaps, pair_n),
        },
        "counts": {
            "response_mismatch": side_mismatch["response"],
            "token_mismatch": side_mismatch["tokens"],
            "text_mismatch": side_mismatch["text"],
            "score_bit_mismatch_per_side": side_mismatch["score_bit"],
            "score_pair_mismatch": pair_bit_mismatch,
            "oriented_sign_mismatch": pair_sign_mismatch,
            "concordant_subtype_swap": concordant_subtype_swaps,
        },
        "certificate_fraction": {
            "n": len(cert_fracs),
            "mean": sum(cert_fracs) / len(cert_fracs) if cert_fracs else None,
            "median": sorted(cert_fracs)[len(cert_fracs) // 2] if cert_fracs else None,
        },
        "hierarchy_checks": {
            "sign_le_pair": pair_sign_mismatch <= pair_bit_mismatch,
            "token_le_response": side_mismatch["tokens"] <= side_mismatch["response"],
            "text_le_response": side_mismatch["text"] <= side_mismatch["response"],
        },
        "scope_note": (
            "Rates apply only to recorded fingerprints. Stable tokens/text do not imply stable logprobs; "
            "stable score/sign does not imply full-response determinism."
        ),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def selftest(_: argparse.Namespace) -> None:
    can_pair = (0, 0)
    fast_pair = (1, 1)
    assert can_pair != fast_pair
    assert can_pair[0] - can_pair[1] == fast_pair[0] - fast_pair[1] == 0
    print("selftest ok: 00<->11 changes score pair while preserving oriented sign")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("collect")
    c.add_argument("--output", required=True)
    c.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    c.add_argument("--repeats", type=int, default=5)
    c.add_argument("--tensor-parallel-size", type=int, default=1)
    c.add_argument("--max-num-seqs", type=int, default=64)
    c.add_argument("--gpu-memory-utilization", type=float, default=0.8)
    c.add_argument("--max-tokens", type=int, default=64)
    c.add_argument("--seed", type=int, default=0)
    c.add_argument("--logprobs", type=int, default=5)
    c.add_argument("--disable-fuse-allreduce-rms", action="store_true")
    c.set_defaults(func=collect)

    q = sub.add_parser("compare")
    q.add_argument("--canonical", required=True)
    q.add_argument("--fast", required=True)
    q.set_defaults(func=compare)

    s = sub.add_parser("selftest")
    s.set_defaults(func=selftest)
    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
