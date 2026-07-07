"""Standalone verification report for Experiment 3."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

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
)


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "optimal_schedule.csv"
OUTPUT_FILE = ROOT / "validation_report.txt"
TOLERANCE = 1.0


def _read_schedule() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Run reservoir_optimize.py before validation.py")
    return pd.read_csv(INPUT_FILE)


def _col(df: pd.DataFrame, *names: str) -> np.ndarray:
    for name in names:
        if name in df.columns:
            return df[name].to_numpy(dtype=float)
    raise KeyError(f"Missing required column; expected one of {names}")


def validate() -> tuple[list[tuple[str, bool, str]], float]:
    """Run all six validation checks."""
    df = _read_schedule()
    days = _col(df, "day", "Day").astype(int)
    inflows = _col(df, "inflow_m3_s", "Inflow")
    releases = _col(df, "release_m3_s", "Release")
    storages = _col(df, "storage_end_m3", "Storage")
    prices = _col(df, "price_usd_per_kwh", "Price")
    revenues = _col(df, "revenue_usd_equiv", "Revenue")

    checks: list[tuple[str, bool, str]] = []

    min_storage = float(storages.min())
    min_day = int(days[np.argmin(storages)])
    checks.append(
        (
            "Storage lower bound",
            min_storage >= V_MIN - TOLERANCE,
            f"Min storage {min_storage:,.0f} m3 on Day {min_day}",
        )
    )

    max_storage = float(storages.max())
    max_day = int(days[np.argmax(storages)])
    checks.append(
        (
            "Storage upper bound",
            max_storage <= V_MAX + TOLERANCE,
            f"Max storage {max_storage:,.0f} m3 on Day {max_day}",
        )
    )

    eco_violations = days[releases < Q_ECO - 1e-6]
    checks.append(
        (
            "Ecological release",
            len(eco_violations) == 0,
            f"All releases >= {Q_ECO} m3/s"
            if len(eco_violations) == 0
            else f"Violated on days {eco_violations.tolist()}",
        )
    )

    max_violations = days[releases > Q_MAX + 1e-6]
    checks.append(
        (
            "Maximum release",
            len(max_violations) == 0,
            f"All releases <= {Q_MAX} m3/s"
            if len(max_violations) == 0
            else f"Violated on days {max_violations.tolist()}",
        )
    )

    expected = INITIAL_STORAGE + np.cumsum((inflows - releases) * DT_SECONDS)
    mass_error = float(np.max(np.abs(expected - storages)))
    checks.append(
        (
            "Mass balance",
            mass_error <= TOLERANCE,
            f"Max absolute error {mass_error:,.3f} m3",
        )
    )

    recalculated_total = compute_revenue(releases, prices)
    csv_total = float(np.sum(revenues))
    revenue_error = abs(recalculated_total - csv_total)
    checks.append(
        (
            "Revenue calculation",
            revenue_error <= max(1e-3, 0.001 * abs(recalculated_total)),
            f"CSV total {csv_total:.2f}; recalculated {recalculated_total:.2f}",
        )
    )

    return checks, csv_total


def write_report() -> None:
    checks, total_revenue = validate()
    passed = sum(ok for _, ok, _ in checks)
    lines = [
        "=" * 70,
        "RESERVOIR OPTIMIZATION VALIDATION REPORT",
        "=" * 70,
        "",
    ]
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        lines.append(f"[{status}] {name}: {detail}")
    lines.extend(
        [
            "=" * 70,
            f"{passed}/6 checks passed | Total Revenue: ${total_revenue:,.2f}",
            "=" * 70,
        ]
    )
    output = OUTPUT_FILE
    try:
        output.write_text("\n".join(lines), encoding="utf-8")
    except PermissionError:
        output = OUTPUT_FILE.with_name("validation_report_latest.txt")
        output.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nReport saved to: {output.name}")


if __name__ == "__main__":
    write_report()
