"""Tests for the extended runoff utilities."""

import unittest

from runoff_extensions import (
    adjust_curve_number_for_amc,
    compare_scs_cn_and_rational,
    rational_method_peak_discharge,
    route_with_time_area,
)


class TestRunoffExtensions(unittest.TestCase):
    def test_amc_adjustment_orders(self) -> None:
        cn_ii = 80.0
        cn_i = adjust_curve_number_for_amc(cn_ii, "I")
        cn_iii = adjust_curve_number_for_amc(cn_ii, "III")
        self.assertLess(cn_i, cn_ii)
        self.assertGreater(cn_iii, cn_ii)

    def test_rational_method(self) -> None:
        q = rational_method_peak_discharge(0.5, 20.0, 1.0)
        self.assertAlmostEqual(q, 2.78, places=2)

    def test_time_area_routing(self) -> None:
        routed = route_with_time_area([1.0, 2.0, 3.0], [0.0, 0.5, 1.0])
        self.assertEqual(len(routed), 3)
        self.assertTrue(all(value >= 0 for value in routed))

    def test_comparison_table(self) -> None:
        table = compare_scs_cn_and_rational([10.0, 20.0], 80.0, 0.4)
        self.assertEqual(len(table), 2)
        self.assertEqual(table[0][0], 10.0)


if __name__ == "__main__":
    unittest.main()
