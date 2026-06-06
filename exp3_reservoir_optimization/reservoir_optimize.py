"""Reservoir dispatch optimization for Experiment 3."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linprog


DT_SECONDS = 86_400.0
REVENUE_SCALE = 4_800.0

INITIAL_STORAGE = 500_000.0
V_MIN = 100_000.0
V_MAX = 1_000_000.0
Q_ECO = 10.0
Q_MAX = 100.0

INFLOWS = np.array([15, 12, 10, 8, 12, 15, 18], dtype=float)
PRICES = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10], dtype=float)


@dataclass(frozen=True)
class OptimizationResult:
    releases: np.ndarray
    storage: np.ndarray
    revenue: float
    ecological_deficit: float
    success: bool
    message: str


def simulate_storage(releases: np.ndarray, initial_storage: float = INITIAL_STORAGE) -> np.ndarray:
    """Return storage at the end of each day."""
    storage = np.empty(releases.size, dtype=float)
    current = float(initial_storage)
    for i, (inflow, release) in enumerate(zip(INFLOWS, releases, strict=True)):
        current = current + (inflow - release) * DT_SECONDS
        storage[i] = current
    return storage


def compute_revenue(releases: np.ndarray, prices: np.ndarray = PRICES) -> float:
    """Compute a lab-scaled hydropower revenue proxy."""
    return float(np.sum(releases * prices) * REVENUE_SCALE)


def compute_ecological_deficit(releases: np.ndarray, threshold: float = Q_ECO) -> float:
    """Sum the daily shortfall below ecological release."""
    return float(np.sum(np.maximum(0.0, threshold - releases)))


def _storage_constraints(releases: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    storage = simulate_storage(releases)
    lower = storage - V_MIN
    upper = V_MAX - storage
    return lower, upper


def _storage_matrix() -> np.ndarray:
    """Matrix mapping releases to cumulative storage after each day."""
    return np.tril(np.ones((INFLOWS.size, INFLOWS.size), dtype=float)) * DT_SECONDS


def _storage_inequalities() -> tuple[np.ndarray, np.ndarray]:
    """Return linear inequalities A_ub x <= b_ub for storage bounds."""
    cumulative_inflow = np.cumsum(INFLOWS)
    cumulative_matrix = _storage_matrix()

    upper = V_MAX - INITIAL_STORAGE - DT_SECONDS * cumulative_inflow
    lower = INITIAL_STORAGE + DT_SECONDS * cumulative_inflow - V_MIN

    a_ub = np.vstack([-cumulative_matrix, cumulative_matrix])
    b_ub = np.concatenate([upper, lower])
    return a_ub, b_ub


def optimize_schedule(
    release_lower_bound: float = Q_ECO,
    release_upper_bound: float = Q_MAX,
    storage_weight: float = 0.0,
) -> OptimizationResult:
    """Optimize daily releases with SLSQP.

    storage_weight is used for trade-off analysis only:
    objective = -revenue + storage_weight * terminal_storage
    """

    c = -PRICES * REVENUE_SCALE
    c = c + storage_weight * DT_SECONDS * np.ones_like(c)

    a_ub, b_ub = _storage_inequalities()
    bounds = [(release_lower_bound, release_upper_bound)] * INFLOWS.size

    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")

    releases = np.asarray(result.x if result.success else np.clip(INFLOWS, release_lower_bound, release_upper_bound), dtype=float)
    storage = simulate_storage(releases)
    revenue = compute_revenue(releases)
    deficit = compute_ecological_deficit(releases)
    return OptimizationResult(
        releases=releases,
        storage=storage,
        revenue=revenue,
        ecological_deficit=deficit,
        success=bool(result.success),
        message=str(result.message),
    )


def validate_solution(result: OptimizationResult) -> list[str]:
    """Validate storage, release, and mass-balance constraints."""
    messages: list[str] = []

    if np.any(result.releases < Q_ECO - 1e-6):
        messages.append("Release dropped below ecological minimum.")
    if np.any(result.releases > Q_MAX + 1e-6):
        messages.append("Release exceeded maximum release.")
    if np.any(result.storage < V_MIN - 1e-6):
        messages.append("Storage dropped below minimum storage.")
    if np.any(result.storage > V_MAX + 1e-6):
        messages.append("Storage exceeded maximum storage.")

    reconstructed = INITIAL_STORAGE + np.cumsum((INFLOWS - result.releases) * DT_SECONDS)
    if not np.allclose(reconstructed, result.storage, atol=1e-6):
        messages.append("Mass balance reconstruction check failed.")

    if np.isclose(result.ecological_deficit, 0.0, atol=1e-9) is False:
        messages.append("Ecological deficit should be zero for the hard-constrained schedule.")

    if not messages:
        messages.append("All constraints satisfied.")
    return messages


def build_schedule_table(result: OptimizationResult) -> pd.DataFrame:
    """Create a day-by-day table for export."""
    storage_start = np.concatenate(([INITIAL_STORAGE], result.storage[:-1]))
    return pd.DataFrame(
        {
            "day": np.arange(1, INFLOWS.size + 1),
            "inflow_m3_s": INFLOWS,
            "release_m3_s": result.releases,
            "storage_start_m3": storage_start,
            "storage_end_m3": result.storage,
            "price_usd_per_kwh": PRICES,
            "revenue_usd_equiv": result.releases * PRICES * REVENUE_SCALE,
        }
    )


def write_validation_report(path: Path, result: OptimizationResult) -> None:
    """Write a short validation summary."""
    lines = [
        "Experiment 3 validation report",
        f"Success: {result.success}",
        f"Optimizer message: {result.message}",
        f"Total revenue (proxy): {result.revenue:.2f}",
        f"Ecological deficit: {result.ecological_deficit:.4f}",
        f"Minimum storage: {result.storage.min():.2f}",
        f"Maximum storage: {result.storage.max():.2f}",
        "",
    ]
    lines.extend(validate_solution(result))
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_tradeoff(output_path: Path) -> pd.DataFrame:
    """Generate a Pareto-style frontier across storage weights."""
    weights = np.linspace(0.0, 100_000.0, 18)
    rows = []
    for weight in weights:
        tradeoff = optimize_tradeoff_penalty(float(weight))
        rows.append(
            {
                "storage_weight": float(weight),
                "revenue": tradeoff.revenue,
                "ecological_deficit": tradeoff.ecological_deficit,
                "terminal_storage": float(tradeoff.storage[-1]),
            }
        )

    df = pd.DataFrame(rows)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(df["ecological_deficit"], df["revenue"], marker="o")
    ax1.set_xlabel("Ecological deficit (m3/s-day)")
    ax1.set_ylabel("Revenue (proxy USD)")
    ax1.set_title("Reservoir Trade-off Frontier")
    ax1.grid(True, alpha=0.3)

    for _, row in df.iloc[::4].iterrows():
        ax1.annotate(
            f"w={row['storage_weight']:.0e}",
            (row["ecological_deficit"], row["revenue"]),
            textcoords="offset points",
            xytext=(6, 5),
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return df


def optimize_tradeoff_penalty(storage_weight: float) -> OptimizationResult:
    """Optimize with an ecological deficit penalty to trace the frontier."""
    n = INFLOWS.size
    c = np.concatenate([-PRICES * REVENUE_SCALE, storage_weight * np.ones(n, dtype=float)])

    a_storage, b_storage = _storage_inequalities()
    a_storage = np.hstack([a_storage, np.zeros((a_storage.shape[0], n), dtype=float)])
    a_deficit = np.hstack([-np.eye(n, dtype=float), -np.eye(n, dtype=float)])
    b_deficit = -np.full(n, Q_ECO, dtype=float)

    a_ub = np.vstack([a_storage, a_deficit])
    b_ub = np.concatenate([b_storage, b_deficit])
    bounds = [(0.0, Q_MAX)] * n + [(0.0, None)] * n

    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if result.success:
        releases = np.asarray(result.x[:n], dtype=float)
        deficit_terms = np.asarray(result.x[n:], dtype=float)
    else:
        releases = np.clip(INFLOWS, 0.0, Q_MAX)
        deficit_terms = np.maximum(0.0, Q_ECO - releases)

    storage = simulate_storage(releases)
    revenue = compute_revenue(releases)
    deficit = float(np.sum(deficit_terms))
    return OptimizationResult(
        releases=releases,
        storage=storage,
        revenue=revenue,
        ecological_deficit=deficit,
        success=bool(result.success),
        message=str(result.message),
    )


def main() -> None:
    root = Path(__file__).resolve().parent

    main_result = optimize_schedule()
    schedule = build_schedule_table(main_result)
    schedule.to_csv(root / "optimal_schedule.csv", index=False)

    write_validation_report(root / "validation_report.txt", main_result)

    tradeoff_df = plot_tradeoff(root / "tradeoff_analysis.png")
    tradeoff_df.to_csv(root / "tradeoff_frontier.csv", index=False)

    print("Optimized schedule:")
    print(schedule[["day", "release_m3_s", "storage_end_m3"]].to_string(index=False))
    print()
    print(f"Revenue proxy: {main_result.revenue:.2f}")
    print(f"Ecological deficit: {main_result.ecological_deficit:.4f}")
    print(f"Validation: {'; '.join(validate_solution(main_result))}")


if __name__ == "__main__":
    main()
