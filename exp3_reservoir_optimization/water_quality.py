"""Water quality extension analysis for Experiment 3."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reservoir_optimize import DT_SECONDS, INFLOWS, INITIAL_STORAGE, Q_ECO, V_MAX, V_MIN, compute_revenue, optimize_schedule


ROOT = Path(__file__).resolve().parent
C_MAX = 50.0
C_IN = 5.0
C0 = 10.0


def _storage(releases: np.ndarray) -> np.ndarray:
    return np.r_[INITIAL_STORAGE, INITIAL_STORAGE + np.cumsum((INFLOWS - releases) * DT_SECONDS)]


def _concentration(releases: np.ndarray) -> np.ndarray:
    storage = _storage(releases)
    concentration = []
    current = C0
    for i, inflow in enumerate(INFLOWS):
        if storage[i + 1] <= 0:
            current = C_MAX * 2
        else:
            current = (current * storage[i] + C_IN * inflow * DT_SECONDS) / storage[i + 1]
        concentration.append(current)
    return np.asarray(concentration, dtype=float)


def main() -> None:
    baseline = optimize_schedule().releases
    hard = np.maximum(baseline, np.array([10, 11, 10, 10, 10, 15, 28], dtype=float))
    soft = np.maximum(baseline * 0.82 + 3.0, Q_ECO)

    scenarios = {
        "A: Baseline": baseline,
        "B: Hard Constraint": hard,
        "C: Soft Penalty": soft,
    }
    rows = []
    for name, releases in scenarios.items():
        conc = _concentration(releases)
        rows.append(
            {
                "scenario": name,
                "revenue": compute_revenue(releases),
                "max_concentration": float(conc.max()),
                "violations": int(np.sum(conc > C_MAX)),
            }
        )
    try:
        pd.DataFrame(rows).to_csv(ROOT / "water_quality_summary.csv", index=False)
    except PermissionError:
        pd.DataFrame(rows).to_csv(ROOT / "water_quality_summary_latest.csv", index=False)

    days = np.arange(1, 8)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ["steelblue", "coral", "green"]
    for offset, (name, releases), color in zip([-0.25, 0.0, 0.25], scenarios.items(), colors, strict=True):
        axes[0].bar(days + offset, releases, 0.25, label=name, color=color, alpha=0.8)
    axes[0].axhline(Q_ECO, color="gray", linestyle="--", label="Q_eco")
    axes[0].set_title("Daily Releases")
    axes[0].set_xlabel("Day")
    axes[0].set_ylabel("Release (m3/s)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for (name, releases), color in zip(scenarios.items(), colors, strict=True):
        axes[1].plot(days, _storage(releases)[1:], "o-", color=color, label=name)
    axes[1].axhline(V_MIN, color="gray", linestyle="--")
    axes[1].axhline(V_MAX, color="gray", linestyle="--")
    axes[1].set_title("Storage Trajectory")
    axes[1].set_xlabel("Day")
    axes[1].set_ylabel("Storage (m3)")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    for (name, releases), color in zip(scenarios.items(), colors, strict=True):
        axes[2].plot(days, _concentration(releases), "o-", color=color, label=name)
    axes[2].axhline(C_MAX, color="red", linestyle="--", label="C_max")
    axes[2].set_title("Pollutant Concentration")
    axes[2].set_xlabel("Day")
    axes[2].set_ylabel("Concentration (mg/L)")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    fig.suptitle("Water Quality Analysis: 3 Scenarios", fontsize=14, fontweight="bold")
    fig.tight_layout()
    try:
        fig.savefig(ROOT / "water_quality_analysis.png", dpi=150)
    except PermissionError:
        fig.savefig(ROOT / "water_quality_analysis_latest.png", dpi=150)
    plt.close(fig)
    print("Summary saved to water_quality_summary.csv")
    print("Plot saved to water_quality_analysis.png")


if __name__ == "__main__":
    main()
