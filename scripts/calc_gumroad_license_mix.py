#!/usr/bin/env python3
"""Calculate conservative monthly Gumroad license-sale targets.

This is a planning calculator, not checkout, sales, or contract evidence. It
uses integer cents for USD fee arithmetic and rounds seller proceeds down to
whole yen so a boundary result can never overstate target attainment.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from typing import Any


def _positive_number(value: Any, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    number = Decimal(str(value))
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    return number


def _net_usd(price: Decimal, percent: Decimal, fixed: Decimal) -> Decimal:
    net = price * (Decimal("1") - percent / Decimal("100")) - fixed
    if net <= 0:
        raise ValueError("fee model leaves no positive seller proceeds")
    return net.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def _yen(net_usd: Decimal, rate: Decimal) -> int:
    return int((net_usd * rate).to_integral_value(rounding=ROUND_DOWN))


def _ceil_div(target: int, proceeds: int) -> int:
    if proceeds <= 0:
        raise ValueError("seller proceeds must be positive")
    return (target + proceeds - 1) // proceeds


def calculate(config: dict[str, Any]) -> dict[str, Any]:
    target = int(_positive_number(config["monthly_target_yen"], "monthly_target_yen"))
    prices = {
        name: _positive_number(value, f"prices_usd.{name}")
        for name, value in config["prices_usd"].items()
    }
    if set(prices) != {"standard", "extended"}:
        raise ValueError("prices_usd must contain standard and extended")

    rates = [_positive_number(value, "usd_jpy_stress_rates") for value in config["usd_jpy_stress_rates"]]
    if not rates or len(set(rates)) != len(rates):
        raise ValueError("usd_jpy_stress_rates must be non-empty and unique")

    models: dict[str, Any] = {}
    for model_name, model in config["fee_models"].items():
        percent = Decimal(str(model["percent"]))
        fixed = Decimal(str(model["fixed_usd"]))
        if percent < 0 or percent >= 100 or fixed < 0:
            raise ValueError(f"invalid fee model: {model_name}")
        models[model_name] = {
            name: _net_usd(price, percent, fixed) for name, price in prices.items()
        }

    scenarios: list[dict[str, Any]] = []
    for rate in rates:
        for model_name, proceeds_usd in models.items():
            proceeds_yen = {name: _yen(value, rate) for name, value in proceeds_usd.items()}
            extended_only = _ceil_div(target, proceeds_yen["extended"])
            frontier = []
            for extended_sales in range(extended_only + 1):
                remaining = max(0, target - extended_sales * proceeds_yen["extended"])
                standard_sales = _ceil_div(remaining, proceeds_yen["standard"]) if remaining else 0
                total = extended_sales * proceeds_yen["extended"] + standard_sales * proceeds_yen["standard"]
                frontier.append({
                    "extended_sales": extended_sales,
                    "standard_sales": standard_sales,
                    "monthly_net_yen": total,
                    "target_reached": total >= target,
                })
            scenarios.append({
                "fee_model": model_name,
                "usd_jpy": int(rate),
                "seller_net_usd_per_sale": {
                    name: str(value) for name, value in proceeds_usd.items()
                },
                "seller_net_yen_per_sale": proceeds_yen,
                "standard_only_sales": _ceil_div(target, proceeds_yen["standard"]),
                "extended_only_sales": extended_only,
                "minimum_mix_frontier": frontier,
            })

    conservative = next(
        row for row in scenarios
        if row["fee_model"] == "direct" and row["usd_jpy"] == min(int(rate) for rate in rates)
    )
    four_extended = next(
        row for row in conservative["minimum_mix_frontier"] if row["extended_sales"] == 4
    )
    return {
        "schema_version": 1,
        "classification": "planning_model_not_revenue_or_contract_evidence",
        "monthly_target_yen": target,
        "official_fee_source": config["official_fee_source"],
        "scenarios": scenarios,
        "conservative_direct_summary": {
            "usd_jpy": conservative["usd_jpy"],
            "extended_only_sales": conservative["extended_only_sales"],
            "standard_only_sales": conservative["standard_only_sales"],
            "four_extended_plus_standard_sales": four_extended["standard_sales"],
            "four_extended_plus_standard_net_yen": four_extended["monthly_net_yen"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = calculate(json.loads(args.config.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
