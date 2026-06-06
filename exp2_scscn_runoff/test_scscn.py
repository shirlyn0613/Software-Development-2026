"""Tests for the SCS-CN runoff calculation."""

import unittest

from scscn_runoff import calculate_runoff


class TestSCSCNRunoff(unittest.TestCase):
    def test_zero_rainfall(self) -> None:
        self.assertEqual(calculate_runoff(0, 80), 0.0)

    def test_rainfall_below_initial_abstraction(self) -> None:
        cn = 80
        s = (25400 / cn) - 254
        ia = 0.2 * s
        self.assertEqual(calculate_runoff(ia - 0.1, cn), 0.0)

    def test_rainfall_equal_initial_abstraction(self) -> None:
        cn = 80
        s = (25400 / cn) - 254
        ia = 0.2 * s
        self.assertEqual(calculate_runoff(ia, cn), 0.0)

    def test_normal_case(self) -> None:
        runoff = calculate_runoff(50, 80)
        self.assertGreater(runoff, 0.0)
        self.assertLessEqual(runoff, 50.0)
        self.assertAlmostEqual(runoff, 13.8, places=1)

    def test_maximum_cn(self) -> None:
        self.assertEqual(calculate_runoff(50, 100), 50.0)

    def test_runoff_never_exceeds_rainfall(self) -> None:
        rainfall_values = [0.0, 1.0, 5.0, 10.0, 25.0, 50.0, 100.0]
        cn_values = [60, 70, 80, 90, 95, 100]

        for p in rainfall_values:
            for cn in cn_values:
                with self.subTest(P=p, CN=cn):
                    runoff = calculate_runoff(p, cn)
                    self.assertLessEqual(runoff, p)
                    self.assertGreaterEqual(runoff, 0.0)


if __name__ == "__main__":
    unittest.main()
