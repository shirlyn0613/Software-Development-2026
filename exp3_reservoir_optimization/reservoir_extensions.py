"""Optional extension utilities for Experiment 3."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, minimize

from reservoir_optimize import (
    DT_SECONDS,
    INFLOWS,
    INITIAL_STORAGE,
    PRICES,
    Q_ECO,
    Q_MAX,
    V_MAX,
    V_MIN,
    compute_ecological_deficit,
    compute_revenue,
    optimize_schedule,
    simulate_storage,
)


@dataclass(frozen=True)
class StochasticSummary:
    scenario: str
    revenue_mean: float
    revenue_std: float
    storage_end_mean: float
    deficit_mean: float


def generate_inflow_scenarios(
    base_inflows: np.ndarray = INFLOWS,
    sigma: float = 0.15,
    n_scenarios: int = 100,
    seed: int = 42,
) -> np.ndarray:
    """Generate uncertain inflow scenarios with multiplicative noise."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=1.0, scale=sigma, size=(n_scenarios, base_inflows.size))
    scenarios = np.clip(base_inflows * noise, 0.0, None)
    return scenarios


def evaluate_robust_schedule(
    releases: np.ndarray,
    inflow_scenarios: np.ndarray,
) -> pd.DataFrame:
    """Evaluate one release schedule under uncertain inflows."""
    rows = []
    for i, inflows in enumerate(inflow_scenarios, start=1):
        storage = INITIAL_STORAGE + np.cumsum((inflows - releases) * DT_SECONDS)
        rows.append(
            {
                "scenario": i,
                "revenue": compute_revenue(releases),
                "deficit": compute_ecological_deficit(releases),
                "terminal_storage": float(storage[-1]),
                "storage_min": float(storage.min()),
                "storage_max": float(storage.max()),
            }
        )
    return pd.DataFrame(rows)


def rolling_horizon_optimization(
    horizon: int = 3,
    initial_storage: float = INITIAL_STORAGE,
) -> pd.DataFrame:
    """Re-optimize the first part of the schedule in a rolling horizon."""
    remaining_storage = float(initial_storage)
    rows = []
    for start in range(0, INFLOWS.size, horizon):
        inflow_window = INFLOWS[start : start + horizon]
        price_window = PRICES[start : start + horizon]
        if inflow_window.size == 0:
            break

        def objective(x: np.ndarray) -> float:
            return -float(np.sum(x * price_window) * 4_800.0)

        a_rows = []
        b_rows = []
        for j in range(inflow_window.size):
            coeff = np.zeros(inflow_window.size)
            coeff[: j + 1] = DT_SECONDS
            cum_inflow = float(np.sum(inflow_window[: j + 1]))
            a_rows.append(-coeff)
            b_rows.append(V_MAX - remaining_storage - DT_SECONDS * cum_inflow)
            a_rows.append(coeff)
            b_rows.append(remaining_storage + DT_SECONDS * cum_inflow - V_MIN)

        bounds = Bounds(np.full(inflow_window.size, Q_ECO), np.full(inflow_window.size, Q_MAX))
        x0 = np.clip(inflow_window, Q_ECO, Q_MAX)
        result = minimize(objective, x0, method="L-BFGS-B", bounds=bounds)
        releases = np.asarray(result.x, dtype=float)
        storage = _simulate_window_storage(inflow_window, releases, remaining_storage)
        rows.append(
            {
                "window_start_day": start + 1,
                "days": inflow_window.size,
                "releases": releases.tolist(),
                "terminal_storage": float(storage[-1]),
                "success": bool(result.success),
            }
        )
        remaining_storage = float(storage[-1])
    return pd.DataFrame(rows)


def _simulate_window_storage(
    inflows: np.ndarray,
    releases: np.ndarray,
    initial_storage: float,
) -> np.ndarray:
    """Simulate storage for a local rolling horizon window."""
    storage = np.empty(releases.size, dtype=float)
    current = float(initial_storage)
    for i, (inflow, release) in enumerate(zip(inflows, releases, strict=True)):
        current = current + (inflow - release) * DT_SECONDS
        storage[i] = current
    return storage


def water_quality_proxy(releases: np.ndarray) -> pd.DataFrame:
    """A simple water-quality proxy based on stable downstream flow."""
    target = 20.0
    rows = []
    for day, release in enumerate(releases, start=1):
        quality_index = max(0.0, 100.0 - abs(release - target) * 2.5)
        rows.append({"day": day, "release": float(release), "quality_index": quality_index})
    return pd.DataFrame(rows)


def compare_algorithms(output_path: Path) -> pd.DataFrame:
    """Compare SLSQP-style and L-BFGS-B-style schedules."""
    base = optimize_schedule()
    clipped = np.clip(INFLOWS * 0.9, Q_ECO, Q_MAX)
    lbfgs_like = pd.DataFrame(
        [
            {
                "algorithm": "HiGHS LP",
                "revenue": base.revenue,
                "deficit": base.ecological_deficit,
                "success": base.success,
            },
            {
                "algorithm": "Heuristic clip",
                "revenue": compute_revenue(clipped),
                "deficit": compute_ecological_deficit(clipped),
                "success": True,
            },
        ]
    )
    lbfgs_like.to_csv(output_path, index=False)
    return lbfgs_like


def build_extension_report(root: Path) -> dict[str, Path]:
    """Generate all optional extension outputs."""
    outputs: dict[str, Path] = {}

    scenarios = generate_inflow_scenarios()
    base = optimize_schedule()
    robustness = evaluate_robust_schedule(base.releases, scenarios)
    robustness_path = root / "robustness_analysis.csv"
    robustness.to_csv(robustness_path, index=False)
    outputs["robustness_analysis.csv"] = robustness_path

    summary = pd.DataFrame(
        [
            {
                "scenario": "uncertain inflows",
                "revenue_mean": robustness["revenue"].mean(),
                "revenue_std": robustness["revenue"].std(ddof=0),
                "storage_end_mean": robustness["terminal_storage"].mean(),
                "deficit_mean": robustness["deficit"].mean(),
            }
        ]
    )
    summary_path = root / "stochastic_summary.csv"
    summary.to_csv(summary_path, index=False)
    outputs["stochastic_summary.csv"] = summary_path

    rolling = rolling_horizon_optimization()
    rolling_path = root / "rolling_horizon_schedule.csv"
    rolling.to_csv(rolling_path, index=False)
    outputs["rolling_horizon_schedule.csv"] = rolling_path

    quality = water_quality_proxy(base.releases)
    quality_path = root / "water_quality_proxy.csv"
    quality.to_csv(quality_path, index=False)
    outputs["water_quality_proxy.csv"] = quality_path

    algo_path = root / "algorithm_comparison.csv"
    compare_algorithms(algo_path)
    outputs["algorithm_comparison.csv"] = algo_path

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(robustness["terminal_storage"], bins=12, color="#4C78A8", edgecolor="white")
    ax.set_title("Uncertain Inflow Terminal Storage Distribution")
    ax.set_xlabel("Terminal storage (m3)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(root / "uncertainty_histogram.png", dpi=200)
    plt.close(fig)
    outputs["uncertainty_histogram.png"] = root / "uncertainty_histogram.png"

    return outputs


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    outputs = build_extension_report(root)
    for name, path in outputs.items():
        print(f"{name}: {path}")
