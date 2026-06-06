from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from visualization.animation import FloodAnimator, create_static_visualization


BASE_DIR = Path(__file__).resolve().parent
DEM_PATH = BASE_DIR / "dem_data.npy"
EXTENDED_DEM_PATH = BASE_DIR / "dem_data_extended.npy"
EXTENT_40_PATH = BASE_DIR / "flood_extent_40m.png"
EXTENT_50_PATH = BASE_DIR / "flood_extent_50m.png"
CURVE_PATH = BASE_DIR / "flood_curve.png"
GIF_PATH = BASE_DIR / "flood_rising.gif"
VOLUME_PATH = BASE_DIR / "flood_volume_45m.json"


def default_building_footprints() -> list[tuple[slice, slice]]:
    return [(slice(30, 40), slice(20, 35)), (slice(60, 72), slice(65, 82))]


def building_mask_from_footprints(shape: tuple[int, int], footprints: list[tuple[slice, slice]] | None = None) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if footprints is None:
        footprints = default_building_footprints()
    for rows, cols in footprints:
        mask[rows, cols] = True
    return mask


def load_dem(filepath: str | Path | None = None) -> np.ndarray:
    if filepath is not None:
        path = Path(filepath)
        if path.exists() and path.stat().st_size > 0:
            try:
                return np.load(path)
            except Exception:
                pass

    for path in (DEM_PATH, EXTENDED_DEM_PATH):
        if path.exists() and path.stat().st_size > 0:
            try:
                return np.load(path)
            except Exception:
                pass

    rng = np.random.default_rng(42)
    rows = cols = 100
    x = np.linspace(0, 1, cols)
    y = np.linspace(0, 1, rows)
    xx, yy = np.meshgrid(x, y)
    slope = 80 - 50 * (0.6 * xx + 0.4 * yy)
    noise = rng.normal(0, 1.5, size=(rows, cols))
    dem = np.clip(slope + noise, 30, 80)
    np.save(DEM_PATH, dem)
    return dem


def calculate_flood(dem: np.ndarray, water_level: float) -> tuple[np.ndarray, np.ndarray, float]:
    flooded_mask = dem < water_level
    depth = np.where(flooded_mask, water_level - dem, 0.0)
    flooded_percentage = float(flooded_mask.mean() * 100.0)
    return flooded_mask, depth, flooded_percentage


def route_flood(dem: np.ndarray, water_level: float, seed: tuple[int, int] | None = None) -> np.ndarray:
    flooded = dem < water_level
    if not flooded.any():
        return np.zeros_like(flooded, dtype=bool)
    if seed is None:
        seed = tuple(np.argwhere(flooded)[0])
    if not flooded[seed]:
        return np.zeros_like(flooded, dtype=bool)

    routed = np.zeros_like(flooded, dtype=bool)
    q = deque([seed])
    rows, cols = dem.shape
    while q:
        r, c = q.popleft()
        if routed[r, c] or not flooded[r, c]:
            continue
        routed[r, c] = True
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and not routed[nr, nc] and flooded[nr, nc]:
                q.append((nr, nc))
    return routed


def add_building_barriers(dem: np.ndarray, footprints: list[tuple[slice, slice]] | None = None) -> np.ndarray:
    result = dem.copy()
    if footprints is None:
        footprints = default_building_footprints()
    barrier_height = result.max() + 20.0
    for rows, cols in footprints:
        result[rows, cols] = barrier_height
    return result


def calculate_flood_volume(depth: np.ndarray, cell_area: float = 1.0) -> float:
    return float(depth.sum() * cell_area)


def simulate_rising_water(dem: np.ndarray, levels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    percentages = []
    for level in levels:
        _, _, pct = calculate_flood(dem, float(level))
        percentages.append(pct)
    return levels, np.array(percentages)


def visualize_flood(
    dem: np.ndarray,
    flooded_mask: np.ndarray,
    depth: np.ndarray,
    water_level: float,
    out_path: str | Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    im0 = axes[0].imshow(dem, cmap="terrain", origin="lower", alpha=0.78)
    axes[0].imshow(np.ma.masked_where(~flooded_mask, flooded_mask), cmap="Blues", alpha=0.55, origin="lower")
    axes[0].set_title(f"Flood Extent at {water_level:.0f} m")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Elevation (m)")

    im1 = axes[1].imshow(depth, cmap="Blues", origin="lower")
    axes[1].set_title(f"Inundation Depth at {water_level:.0f} m")
    axes[1].set_xticks([])
    axes[1].set_yticks([])
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04, label="Depth (m)")
    fig.suptitle(f"Flood Analysis at Water Level {water_level:.0f} m", fontsize=14)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def save_curve(levels: np.ndarray, percentages: np.ndarray, out_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.plot(levels, percentages, marker="o", linewidth=2, color="#1f77b4")
    ax.set_xlabel("Water Level (m)")
    ax.set_ylabel("Flooded Percentage (%)")
    ax.set_title("Water Level vs. Flooded Percentage")
    ax.grid(True, alpha=0.3)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def create_rising_water_gif(dem: np.ndarray, levels: np.ndarray, out_path: str | Path) -> None:
    building_mask = building_mask_from_footprints(dem.shape)
    animator = FloodAnimator(dem, building_mask=building_mask)
    animator.create_animation(levels, out_path, fps=3)


def validate_physics(dem: np.ndarray, levels: np.ndarray) -> None:
    min_elev = float(dem.min())
    max_elev = float(dem.max())

    below_mask, below_depth, below_pct = calculate_flood(dem, min_elev - 1.0)
    assert not below_mask.any()
    assert np.isclose(below_depth.max(), 0.0)
    assert 0.0 <= below_pct <= 100.0

    above_mask, above_depth, above_pct = calculate_flood(dem, max_elev + 1.0)
    assert above_mask.all()
    assert np.isclose(above_depth.max(), (max_elev + 1.0) - min_elev)
    assert np.isclose(above_pct, 100.0)

    flooded_percentages = []
    for level in levels:
        _, _, pct = calculate_flood(dem, float(level))
        flooded_percentages.append(pct)
    flooded_percentages = np.array(flooded_percentages)
    assert np.all((flooded_percentages >= 0.0) & (flooded_percentages <= 100.0))
    assert np.all(np.diff(flooded_percentages) >= -1e-9)


def main() -> None:
    dem = load_dem()
    water_levels = np.arange(40, 51, 1, dtype=float)
    validate_physics(dem, water_levels)
    _, percentages = simulate_rising_water(dem, water_levels)

    save_curve(water_levels, percentages, CURVE_PATH)
    for level, out_path in [(40.0, EXTENT_40_PATH), (50.0, EXTENT_50_PATH)]:
        flooded_mask, depth, _ = calculate_flood(dem, level)
        visualize_flood(dem, flooded_mask, depth, level, out_path)

    np.save(DEM_PATH, dem)

    footprints = default_building_footprints()
    bmask = building_mask_from_footprints(dem.shape, footprints)
    extended_dem = add_building_barriers(dem)
    np.save(EXTENDED_DEM_PATH, extended_dem)
    create_rising_water_gif(extended_dem, water_levels, GIF_PATH)
    create_static_visualization(
        extended_dem,
        np.array([40.0, 45.0, 50.0]),
        building_mask=bmask,
        save_path=BASE_DIR / "flood_stages.png",
    )

    routed_mask = route_flood(extended_dem, 45.0)
    routed_depth = np.where(routed_mask, 45.0 - extended_dem, 0.0)
    volume = calculate_flood_volume(routed_depth, cell_area=1.0)
    VOLUME_PATH.write_text(json.dumps({"water_level": 45.0, "volume": volume}, indent=2), encoding="utf-8")

    if np.any(np.diff(percentages) < -1e-9):
        print("Warning: flooded percentage is not strictly monotonic.")
    else:
        print("Flooded percentage increases monotonically across the tested levels.")


if __name__ == "__main__":
    main()
