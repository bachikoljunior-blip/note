#!/usr/bin/env python3
import copy
import json
import unittest
from pathlib import Path

from calc_gumroad_license_mix import calculate


ROOT = Path(__file__).resolve().parents[1]


class LicenseMixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads((ROOT / "config/gumroad_license_mix.json").read_text())

    def scenario(self, fee_model: str, usd_jpy: int):
        result = calculate(self.config)
        return next(row for row in result["scenarios"] if row["fee_model"] == fee_model and row["usd_jpy"] == usd_jpy)

    def test_direct_fee_math(self):
        row = self.scenario("direct", 130)
        self.assertEqual(row["seller_net_usd_per_sale"], {"standard": "22.00", "extended": "313.60"})

    def test_conservative_extended_target_is_five(self):
        self.assertEqual(self.scenario("direct", 130)["extended_only_sales"], 5)

    def test_four_extended_need_thirteen_standard_at_130(self):
        row = self.scenario("direct", 130)
        mix = next(item for item in row["minimum_mix_frontier"] if item["extended_sales"] == 4)
        self.assertEqual(mix["standard_sales"], 13)
        self.assertGreaterEqual(mix["monthly_net_yen"], 200000)

    def test_discover_requires_seven_extended_at_130(self):
        self.assertEqual(self.scenario("discover", 130)["extended_only_sales"], 7)

    def test_every_frontier_point_reaches_target(self):
        result = calculate(self.config)
        self.assertTrue(all(item["target_reached"] for row in result["scenarios"] for item in row["minimum_mix_frontier"]))

    def test_duplicate_stress_rate_rejected(self):
        config = copy.deepcopy(self.config)
        config["usd_jpy_stress_rates"] = [130, 130]
        with self.assertRaisesRegex(ValueError, "unique"):
            calculate(config)

    def test_boolean_price_rejected(self):
        config = copy.deepcopy(self.config)
        config["prices_usd"]["standard"] = True
        with self.assertRaisesRegex(ValueError, "numeric"):
            calculate(config)


if __name__ == "__main__":
    unittest.main()
