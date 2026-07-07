"""Unit tests for Experiment 3 reservoir optimization."""

from __future__ import annotations

import unittest

import numpy as np

from reservoir_optimize import (
    DT_SECONDS,
    INFLOWS,
    INITIAL_STORAGE,
    Q_ECO,
    Q_MAX,
    V_MAX,
    V_MIN,
    compute_ecological_deficit,
    compute_revenue,
    optimize_schedule,
    simulate_storage,
    validate_solution,
)


class ReservoirOptimizationTests(unittest.TestCase):
    def test_storage_mass_balance(self) -> None:
        releases = np.array([10, 11, 10, 10, 10, 25, 18], dtype=float)
        storage = simulate_storage(releases)
        expected = INITIAL_STORAGE + np.cumsum((INFLOWS - releases) * DT_SECONDS)
        np.testing.assert_allclose(storage, expected)

    def test_revenue_is_positive_for_feasible_releases(self) -> None:
        releases = np.maximum(INFLOWS, Q_ECO)
        self.assertGreater(compute_revenue(releases), 0.0)

    def test_ecological_deficit(self) -> None:
        releases = np.array([10, 9, 8, 10, 12, 7, 15], dtype=float)
        self.assertAlmostEqual(compute_ecological_deficit(releases), 6.0)

    def test_optimized_solution_is_feasible(self) -> None:
        result = optimize_schedule()
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.releases.min(), Q_ECO - 1e-6)
        self.assertLessEqual(result.releases.max(), Q_MAX + 1e-6)
        self.assertGreaterEqual(result.storage.min(), V_MIN - 1e-6)
        self.assertLessEqual(result.storage.max(), V_MAX + 1e-6)
        self.assertEqual(validate_solution(result), ["All constraints satisfied."])


if __name__ == "__main__":
    unittest.main()
