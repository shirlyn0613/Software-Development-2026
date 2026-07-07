"""Validation checks for the SCS-CN runoff model."""

from __future__ import annotations

import random

from scscn_runoff import calculate_runoff


def calculate_s(cn: float) -> float:
    """Calculate potential maximum retention S."""
    if cn <= 0:
        return float("inf")
    if cn >= 100:
        return 0.0
    return (25400 / cn) - 254


def calculate_ia(s_value: float) -> float:
    """Calculate initial abstraction Ia."""
    return 0.2 * s_value


def check_zero_rainfall() -> tuple[bool, str]:
    """Check that zero rainfall gives zero runoff."""
    for cn in [60, 70, 80, 90, 95, 100]:
        runoff = calculate_runoff(0.0, cn)
        if runoff != 0.0:
            return False, f"CN={cn}: expected Q=0, got Q={runoff:.3f}"
    return True, "P=0 produces Q=0 for all tested CN values."


def check_below_initial_abstraction() -> tuple[bool, str]:
    """Check that rainfall below Ia gives zero runoff."""
    for cn in [60, 70, 80, 90, 95]:
        s_value = calculate_s(cn)
        ia = calculate_ia(s_value)
        rainfall = ia * 0.5
        runoff = calculate_runoff(rainfall, cn)
        if runoff != 0.0:
            return False, (
                f"CN={cn}: P={rainfall:.3f} < Ia={ia:.3f}, "
                f"but Q={runoff:.3f}"
            )
    return True, "P < Ia produces Q=0 for all tested CN values."


def check_q_not_greater_than_p() -> tuple[bool, str]:
    """Check Q <= P across random samples."""
    random.seed(42)
    for _ in range(1000):
        rainfall = random.uniform(0.0, 200.0)
        cn = random.uniform(1.0, 100.0)
        runoff = calculate_runoff(rainfall, cn)
        if runoff > rainfall:
            return False, (
                f"P={rainfall:.3f}, CN={cn:.3f}: "
                f"Q={runoff:.3f} exceeds P"
            )
    return True, "Q <= P holds for 1000 random rainfall/CN samples."


def check_monotonicity() -> tuple[bool, str]:
    """Check that runoff increases with CN at fixed rainfall."""
    rainfall = 50.0
    previous = calculate_runoff(rainfall, 60)
    for cn in range(61, 101):
        current = calculate_runoff(rainfall, cn)
        if current < previous:
            return False, (
                f"Runoff decreased between CN={cn - 1} and CN={cn}: "
                f"{previous:.3f} -> {current:.3f}"
            )
        previous = current
    return True, "At P=50 mm, runoff increases monotonically from CN=60 to CN=100."


def check_reference_case() -> tuple[bool, str]:
    """Check the worked example P=50 mm, CN=80."""
    runoff = calculate_runoff(50.0, 80.0)
    if 13.5 <= runoff <= 14.1:
        return True, f"P=50 mm, CN=80 gives Q={runoff:.2f} mm."
    return False, f"P=50 mm, CN=80 gives Q={runoff:.2f} mm, expected about 13.8 mm."


def check_cn_100() -> tuple[bool, str]:
    """Check impervious-surface behavior for CN=100."""
    for rainfall in [10.0, 50.0, 100.0, 150.0]:
        runoff = calculate_runoff(rainfall, 100.0)
        if abs(runoff - rainfall) > 1e-9:
            return False, f"P={rainfall:.1f}, CN=100: expected Q=P, got Q={runoff:.3f}"
    return True, "CN=100 returns Q=P for tested rainfall values."


def run_all_checks() -> int:
    """Run all validation checks and print a structured report."""
    checks = [
        ("Zero rainfall", check_zero_rainfall),
        ("Below initial abstraction", check_below_initial_abstraction),
        ("Physical constraint Q <= P", check_q_not_greater_than_p),
        ("CN monotonicity", check_monotonicity),
        ("Known reference value", check_reference_case),
        ("Impervious surface CN=100", check_cn_100),
    ]

    print("=" * 64)
    print("SCS-CN MODEL VALIDATION REPORT")
    print("=" * 64)

    passed = 0
    for name, check in checks:
        ok, message = check()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}")
        print(f"       {message}")
        if ok:
            passed += 1

    print("=" * 64)
    print(f"{passed}/{len(checks)} validation checks passed")
    print("=" * 64)
    return passed


if __name__ == "__main__":
    raise SystemExit(0 if run_all_checks() == 6 else 1)
