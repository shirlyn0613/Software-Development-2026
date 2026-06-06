"""Extended runoff utilities for the SCS-CN experiment."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from scscn_runoff import calculate_runoff


def adjust_curve_number_for_amc(cn_ii: float, amc: str = "II") -> float:
    """Adjust a Curve Number for antecedent moisture condition.

    Args:
        cn_ii: Curve Number under average conditions (AMC/ARC II).
        amc: Antecedent moisture condition. Use "I", "II", or "III".

    Returns:
        Adjusted Curve Number clipped to [0, 100].
    """
    amc = amc.upper()
    if amc == "II":
        adjusted = cn_ii
    elif amc == "I":
        adjusted = cn_ii / (2.281 - 0.01281 * cn_ii)
    elif amc == "III":
        adjusted = cn_ii / (0.427 + 0.00573 * cn_ii)
    else:
        raise ValueError("amc must be one of: 'I', 'II', 'III'")

    return float(np.clip(adjusted, 0.0, 100.0))


def rational_method_peak_discharge(
    runoff_coefficient: float,
    rainfall_intensity_mm_per_hr: float,
    area_km2: float,
) -> float:
    """Estimate peak discharge using the Rational Method.

    Args:
        runoff_coefficient: Dimensionless runoff coefficient C.
        rainfall_intensity_mm_per_hr: Rainfall intensity in mm/h.
        area_km2: Watershed area in km^2.

    Returns:
        Peak discharge in m^3/s.
    """
    if runoff_coefficient < 0 or rainfall_intensity_mm_per_hr < 0 or area_km2 < 0:
        return 0.0
    return 0.278 * runoff_coefficient * rainfall_intensity_mm_per_hr * area_km2


def route_with_time_area(
    excess_hyetograph_mm: Sequence[float],
    time_area_curve: Sequence[float],
) -> list[float]:
    """Route excess rainfall through a discrete time-area curve.

    The time-area curve is treated as cumulative contributing area fractions.

    Args:
        excess_hyetograph_mm: Excess rainfall or runoff depth by timestep.
        time_area_curve: Monotonic cumulative area fractions from 0 to 1.

    Returns:
        Routed discharge-like series with the same length as the input.
    """
    if not excess_hyetograph_mm:
        return []
    if not time_area_curve:
        raise ValueError("time_area_curve must not be empty")

    curve = np.asarray(time_area_curve, dtype=float)
    if curve[0] > 0.0:
        curve = np.insert(curve, 0, 0.0)
    if curve[-1] < 1.0:
        curve = np.append(curve, 1.0)

    curve = np.clip(curve, 0.0, 1.0)
    weights = np.diff(curve, prepend=0.0)
    weights = np.clip(weights, 0.0, None)
    if weights.sum() == 0:
        raise ValueError("time_area_curve must contain positive area fractions")
    weights = weights / weights.sum()

    excess = np.asarray(excess_hyetograph_mm, dtype=float)
    routed = np.convolve(excess, weights, mode="full")[: excess.size]
    return routed.tolist()


def compare_scs_cn_and_rational(
    rainfall_depths_mm: Iterable[float],
    cn_value: float,
    runoff_coefficient: float,
    area_km2: float = 1.0,
    storm_duration_hr: float = 1.0,
) -> list[tuple[float, float, float]]:
    """Create a simple comparison table between SCS-CN and Rational Method."""
    comparison = []
    for p in rainfall_depths_mm:
        scs_cn_q = calculate_runoff(float(p), cn_value)
        intensity = float(p) / storm_duration_hr if storm_duration_hr > 0 else 0.0
        rational_q = rational_method_peak_discharge(
            runoff_coefficient, intensity, area_km2
        )
        comparison.append((float(p), scs_cn_q, rational_q))
    return comparison
