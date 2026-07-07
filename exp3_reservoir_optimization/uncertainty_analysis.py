"""Monte Carlo inflow uncertainty analysis for Experiment 3."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reservoir_extensions import evaluate_robust_schedule, generate_inflow_scenarios
from reservoir_optimize import INFLOWS, V_MAX, V_MIN, optimize_schedule


ROOT = Path(__file__).resolve().parent


def main() -> None:
    scenarios = generate_inflow_scenarios(INFLOWS, sigma=0.20, n_scenarios=100, seed=42)
    base = optimize_schedule()
    robustness = evaluate_robust_schedule(base.releases, scenarios)
    try:
        robustness.to_csv(ROOT / "uncertainty_analysis.csv", index=False)
    except PermissionError:
        robustness.to_csv(ROOT / "uncertainty_analysis_latest.csv", index=False)

    storage_paths = []
    for inflow in scenarios:
        storage_paths.append(np.r_[500_000.0, 500_000.0 + np.cumsum((inflow - base.releases) * 86_400.0)])
    storage_arr = np.asarray(storage_paths)
    days = np.arange(0, 8)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for scenario in scenarios:
        axes[0].plot(np.arange(1, 8), scenario, color="gray", alpha=0.1, linewidth=0.5)
    axes[0].plot(np.arange(1, 8), INFLOWS, color="blue", linewidth=2.5, label="Base Forecast")
    axes[0].set_title("Inflow Forecast Scenarios (+/-20% uncertainty)")
    axes[0].set_xlabel("Day")
    axes[0].set_ylabel("Inflow (m3/s)")
    axes[0].legend()

    axes[1].fill_between(days, np.percentile(storage_arr, 10, axis=0), np.percentile(storage_arr, 90, axis=0), color="lightblue", alpha=0.5, label="10th-90th pct")
    axes[1].plot(days, storage_arr.mean(axis=0), color="blue", linewidth=2, label="Mean")
    axes[1].axhline(V_MIN, color="red", linestyle="--", label="V_min")
    axes[1].axhline(V_MAX, color="red", linestyle="--", label="V_max")
    axes[1].set_title("Storage Trajectory Under Uncertainty")
    axes[1].set_xlabel("Day")
    axes[1].set_ylabel("Storage (m3)")
    axes[1].legend()

    axes[2].hist(robustness["revenue"], bins=20, color="steelblue", edgecolor="black", alpha=0.75)
    axes[2].axvline(robustness["revenue"].mean(), color="red", linestyle="--", linewidth=2, label=f"Mean = {robustness['revenue'].mean():.2f}")
    axes[2].set_title("Revenue Distribution")
    axes[2].set_xlabel("Total Revenue")
    axes[2].set_ylabel("Frequency")
    axes[2].legend()

    fig.tight_layout()
    try:
        fig.savefig(ROOT / "uncertainty_analysis.png", dpi=150)
    except PermissionError:
        fig.savefig(ROOT / "uncertainty_analysis_latest.png", dpi=150)
    plt.close(fig)
    print("Uncertainty table saved to uncertainty_analysis.csv")
    print("Plot saved to uncertainty_analysis.png")


if __name__ == "__main__":
    main()
