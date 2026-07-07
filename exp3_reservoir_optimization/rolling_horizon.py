"""Full-horizon vs rolling-horizon comparison for Experiment 3."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linprog

from reservoir_optimize import (
    DT_SECONDS,
    INFLOWS,
    INITIAL_STORAGE,
    PRICES,
    Q_ECO,
    Q_MAX,
    V_MAX,
    V_MIN,
    compute_revenue,
    optimize_schedule,
)


ROOT = Path(__file__).resolve().parent


def _solve_window(inflows: np.ndarray, prices: np.ndarray, start_storage: float) -> np.ndarray:
    n = len(inflows)
    c = -prices
    lower = []
    upper = []
    mat = np.tril(np.ones((n, n))) * DT_SECONDS
    cum_inflow = np.cumsum(inflows)
    lower.extend(V_MAX - start_storage - DT_SECONDS * cum_inflow)
    upper.extend(start_storage + DT_SECONDS * cum_inflow - V_MIN)
    a_ub = np.vstack([-mat, mat])
    b_ub = np.asarray(lower + upper, dtype=float)
    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=[(Q_ECO, Q_MAX)] * n, method="highs")
    if not result.success:
        return np.clip(inflows, Q_ECO, Q_MAX)
    return np.asarray(result.x, dtype=float)


def rolling_horizon(horizon: int = 3) -> tuple[np.ndarray, np.ndarray, float]:
    releases = []
    storages = []
    current_storage = INITIAL_STORAGE
    for day in range(len(INFLOWS)):
        inflows = INFLOWS[day : day + horizon]
        prices = PRICES[day : day + horizon]
        q_window = _solve_window(inflows, prices, current_storage)
        q = float(q_window[0])
        current_storage = current_storage + (INFLOWS[day] - q) * DT_SECONDS
        current_storage = float(np.clip(current_storage, V_MIN, V_MAX))
        releases.append(q)
        storages.append(current_storage)
    release_arr = np.asarray(releases, dtype=float)
    return release_arr, np.asarray(storages, dtype=float), compute_revenue(release_arr)


def main() -> None:
    full = optimize_schedule()
    roll_q, roll_s, roll_revenue = rolling_horizon()

    df = pd.DataFrame(
        {
            "day": np.arange(1, 8),
            "full_release": full.releases,
            "rolling_release": roll_q,
            "full_storage": full.storage,
            "rolling_storage": roll_s,
        }
    )
    try:
        df.to_csv(ROOT / "rolling_horizon_comparison.csv", index=False)
    except PermissionError:
        df.to_csv(ROOT / "rolling_horizon_comparison_latest.csv", index=False)

    days = np.arange(1, 8)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    width = 0.35
    axes[0].bar(days - width / 2, full.releases, width, label="Full Horizon", color="steelblue", alpha=0.8)
    axes[0].bar(days + width / 2, roll_q, width, label="Rolling Horizon", color="coral", alpha=0.8)
    axes[0].axhline(Q_ECO, color="green", linestyle="--", label="Q_eco")
    axes[0].axhline(Q_MAX, color="red", linestyle="--", label="Q_max")
    axes[0].set_title("Daily Releases Comparison")
    axes[0].set_xlabel("Day")
    axes[0].set_ylabel("Release (m3/s)")
    axes[0].set_xticks(days)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(days, full.storage, "o-", label="Full Horizon", color="steelblue")
    axes[1].plot(days, roll_s, "s-", label="Rolling Horizon", color="coral")
    axes[1].axhline(V_MIN, color="green", linestyle="--", label="V_min")
    axes[1].axhline(V_MAX, color="red", linestyle="--", label="V_max")
    axes[1].set_title("Storage Trajectory Comparison")
    axes[1].set_xlabel("Day")
    axes[1].set_ylabel("Storage (m3)")
    axes[1].set_xticks(days)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    fig.suptitle("Full Horizon vs Rolling Horizon", fontsize=14, fontweight="bold")
    fig.tight_layout()
    try:
        fig.savefig(ROOT / "rolling_horizon_comparison.png", dpi=150)
    except PermissionError:
        fig.savefig(ROOT / "rolling_horizon_comparison_latest.png", dpi=150)
    plt.close(fig)

    print(f"Full horizon revenue: {full.revenue:.2f}")
    print(f"Rolling horizon revenue: {roll_revenue:.2f}")
    print("Comparison saved to rolling_horizon_comparison.csv")
    print("Plot saved to rolling_horizon_comparison.png")


if __name__ == "__main__":
    main()
