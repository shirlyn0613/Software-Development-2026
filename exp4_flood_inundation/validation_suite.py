from __future__ import annotations

from pathlib import Path

import numpy as np

from flood_inundation import (
    calculate_flood,
    calculate_flood_volume,
    load_dem,
    simulate_rising_water,
)


REPORT_PATH = Path(__file__).resolve().parent / "validation_report.txt"


def run_validation(dem: np.ndarray, cell_area: float = 900.0) -> str:
    lines: list[str] = []
    passed = 0
    total = 0

    def record(name: str, ok: bool, details: str = "") -> None:
        nonlocal passed, total
        total += 1
        if ok:
            passed += 1
        status = "PASS" if ok else "FAIL"
        suffix = f" - {details}" if details else ""
        lines.append(f"[{status}] {name}{suffix}")

    lines.append("=" * 60)
    lines.append("FLOOD INUNDATION PHYSICAL VALIDATION REPORT")
    lines.append("=" * 60)

    min_elev = float(dem.min())
    max_elev = float(dem.max())
    mean_elev = float(dem.mean())

    lines.append("\nSECTION 1: DEM DATA")
    record("DEM shape is 100x100", dem.shape == (100, 100), f"shape={dem.shape}")
    record("DEM minimum is within expected range", 29.0 <= min_elev <= 31.0, f"min={min_elev:.2f} m")
    record("DEM maximum is within expected range", 79.0 <= max_elev <= 101.0, f"max={max_elev:.2f} m")

    lines.append("\nSECTION 2: EDGE CASES")
    mask, depth, pct = calculate_flood(dem, min_elev - 1.0)
    record("No flooding below minimum elevation", not mask.any() and pct == 0.0, f"flooded={pct:.1f}%")
    record("Depth is zero below minimum elevation", np.isclose(depth.max(), 0.0), f"max_depth={depth.max():.3f} m")

    mask, depth, pct = calculate_flood(dem, max_elev + 1.0)
    record("Full flooding above maximum elevation", mask.all() and np.isclose(pct, 100.0), f"flooded={pct:.1f}%")
    record(
        "Maximum depth matches water level minus minimum elevation",
        np.isclose(depth.max(), (max_elev + 1.0) - min_elev),
        f"max_depth={depth.max():.3f} m",
    )

    lines.append("\nSECTION 3: WATER LEVEL SWEEP")
    levels = np.arange(40, 51, 1, dtype=float)
    _, percentages = simulate_rising_water(dem, levels)
    record("Flooded percentage stays within 0-100%", np.all((percentages >= 0.0) & (percentages <= 100.0)))
    record("Flooded percentage is non-decreasing", np.all(np.diff(percentages) >= -1e-9))

    max_depths = []
    volumes = []
    for level in levels:
        _, depth, _ = calculate_flood(dem, float(level))
        max_depths.append(float(depth.max()))
        volumes.append(calculate_flood_volume(depth, cell_area=cell_area))
    max_depths = np.array(max_depths)
    volumes = np.array(volumes)
    record("Maximum depth is non-decreasing", np.all(np.diff(max_depths) >= -1e-9))
    record("Flood volume is non-decreasing", np.all(np.diff(volumes) >= -1e-9))

    lines.append("\nSECTION 4: REPRESENTATIVE LEVELS")
    for level in (40.0, 45.0, 50.0):
        mask, depth, pct = calculate_flood(dem, level)
        volume = calculate_flood_volume(depth, cell_area=cell_area)
        lines.append(
            f"- {level:.0f} m: flooded={pct:.2f}%, cells={int(mask.sum())}, "
            f"max_depth={depth.max():.2f} m, volume={volume:.2f} m3"
        )

    lines.append("\n" + "=" * 60)
    lines.append(f"SUMMARY: {passed}/{total} checks passed")
    lines.append(f"PHYSICAL VALIDITY: {'CONFIRMED' if passed == total else 'NEEDS REVIEW'}")
    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> None:
    dem = load_dem()
    report = run_validation(dem)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved: {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
