"""SCS-CN runoff calculation utilities."""

from __future__ import annotations


def calculate_runoff(P: float, CN: float) -> float:
    """Calculate direct runoff depth using the SCS-CN method.

    Args:
        P: Rainfall depth in millimeters.
        CN: Curve Number, typically in the range 0 to 100.

    Returns:
        Runoff depth in millimeters.
    """
    if CN <= 0:
        return 0.0

    if CN >= 100:
        return max(P, 0.0)

    S = (25400 / CN) - 254
    Ia = 0.2 * S

    if P < Ia:
        return 0.0

    runoff = (P - Ia) ** 2 / (P - Ia + S)
    return min(runoff, P)
