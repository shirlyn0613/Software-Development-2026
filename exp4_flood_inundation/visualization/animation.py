from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

BUILDING_COLOR = "#b22222"


def _legend_handles(has_building: bool) -> list[Patch]:
    handles = [
        Patch(facecolor=plt.cm.terrain(0.55), edgecolor="none", label="Terrain"),
        Patch(facecolor=plt.cm.Blues(0.55), edgecolor="none", label="Flood"),
    ]
    if has_building:
        handles.append(Patch(facecolor=BUILDING_COLOR, edgecolor="none", label="Building"))
    return handles


class FloodAnimator:
    def __init__(self, dem: np.ndarray, resolution: float = 30.0, building_mask: Optional[np.ndarray] = None):
        self.dem = dem
        self.resolution = resolution
        self.building_mask = building_mask
        self.vmin = float(dem.min())
        self.vmax = float(dem.max())

    def _frame(self, water_level: float, flooded: np.ndarray, depth: np.ndarray, ax: plt.Axes) -> None:
        ax.imshow(self.dem, cmap="terrain", vmin=self.vmin, vmax=self.vmax, alpha=0.78)

        flood_display = np.ma.masked_where(~flooded, flooded)
        ax.imshow(flood_display, cmap="Blues", alpha=0.55, vmin=0, vmax=1)

        if self.building_mask is not None:
            building_display = np.ma.masked_where(~self.building_mask, self.building_mask)
            ax.imshow(building_display, cmap="Reds", alpha=0.55, vmin=0, vmax=1)

        flooded_pct = flooded.mean() * 100.0
        ax.set_title(f"Water Level: {water_level:.1f} m", fontsize=13)
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        ax.legend(handles=_legend_handles(self.building_mask is not None), loc="upper right", framealpha=0.9, fontsize=10)
        ax.text(
            0.02,
            0.98,
            f"Flooded: {flooded_pct:.1f}%",
            transform=ax.transAxes,
            fontsize=11,
            va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    def create_animation(self, levels: np.ndarray, output_path: str | Path, fps: int = 3) -> None:
        from flood_inundation import calculate_flood

        fig, ax = plt.subplots(figsize=(10, 8))

        def update(level: float):
            ax.clear()
            flooded, depth, _ = calculate_flood(self.dem, float(level))
            self._frame(level, flooded, depth, ax)
            return ax

        anim = FuncAnimation(fig, update, frames=[float(v) for v in levels], interval=300, blit=False)
        anim.save(output_path, writer=PillowWriter(fps=fps))
        plt.close(fig)


def create_static_visualization(
    dem: np.ndarray,
    levels: np.ndarray,
    building_mask: Optional[np.ndarray] = None,
    save_path: str = "flood_stages.png",
) -> None:
    from flood_inundation import calculate_flood

    n_levels = len(levels)
    fig, axes = plt.subplots(1, n_levels, figsize=(4 * n_levels, 5))
    if n_levels == 1:
        axes = [axes]

    for ax, level in zip(axes, levels):
        flooded, depth, _ = calculate_flood(dem, float(level))

        ax.imshow(dem, cmap="terrain", alpha=0.75)
        flood_display = np.ma.masked_where(~flooded, flooded)
        ax.imshow(flood_display, cmap="Blues", alpha=0.55, vmin=0, vmax=1)

        if building_mask is not None:
            bldg_display = np.ma.masked_where(~building_mask, building_mask)
            ax.imshow(bldg_display, cmap="Reds", alpha=0.55, vmin=0, vmax=1)

        pct = flooded.mean() * 100.0
        ax.set_title(f"{level:.0f} m\n({pct:.1f}% flooded)")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.legend(handles=_legend_handles(building_mask is not None), loc="upper right", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def create_depth_animation(
    dem: np.ndarray,
    levels: np.ndarray,
    save_path: str = "flood_depth.gif",
) -> None:
    from flood_inundation import calculate_flood

    fig, ax = plt.subplots(figsize=(8, 6))

    def update(level: float):
        ax.clear()
        _, depth, _ = calculate_flood(dem, float(level))
        depth_display = np.ma.masked_where(depth == 0, depth)
        im = ax.imshow(depth_display, cmap="Blues", vmin=0)
        ax.set_title(f"Inundation Depth at {level:.0f} m")
        plt.colorbar(im, ax=ax, label="Depth (m)")
        ax.legend(
            handles=[Patch(facecolor=plt.cm.Blues(0.55), edgecolor="none", label="Depth")],
            loc="upper right",
            framealpha=0.9,
            fontsize=10,
        )
        return ax

    anim = FuncAnimation(fig, update, frames=[float(v) for v in levels], interval=300, blit=False)
    anim.save(save_path, writer=PillowWriter(fps=3))
    plt.close(fig)
