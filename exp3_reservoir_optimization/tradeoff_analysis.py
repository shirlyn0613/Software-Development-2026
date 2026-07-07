"""Pareto trade-off analysis for Experiment 3."""

from __future__ import annotations

from pathlib import Path

from reservoir_optimize import plot_tradeoff


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    df = plot_tradeoff(root / "tradeoff_analysis.png")
    try:
        df.to_csv(root / "tradeoff_frontier.csv", index=False)
    except PermissionError:
        df.to_csv(root / "tradeoff_frontier_latest.csv", index=False)
    print("Pareto frontier saved to tradeoff_frontier.csv")
    print("Plot saved to tradeoff_analysis.png")
