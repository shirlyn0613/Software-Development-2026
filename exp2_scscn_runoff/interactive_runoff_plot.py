"""Interactive runoff plot with sliders for rainfall and CN."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from scscn_runoff import calculate_runoff


def build_interactive_plot() -> None:
    """Open an interactive plot with sliders for P and CN."""
    rainfall_values = list(range(0, 151, 5))
    initial_p = 50.0
    initial_cn = 80.0

    fig, ax = plt.subplots(figsize=(8, 5))
    plt.subplots_adjust(bottom=0.25)

    runoff_values = [calculate_runoff(p, initial_cn) for p in rainfall_values]
    (line,) = ax.plot(rainfall_values, runoff_values, lw=2)
    (point,) = ax.plot([initial_p], [calculate_runoff(initial_p, initial_cn)], "o")

    ax.set_xlabel("Rainfall P (mm)")
    ax.set_ylabel("Runoff Q (mm)")
    ax.set_title("Interactive SCS-CN Runoff Explorer")
    ax.grid(True, alpha=0.3)

    ax_p = plt.axes([0.15, 0.12, 0.7, 0.03])
    ax_cn = plt.axes([0.15, 0.07, 0.7, 0.03])
    slider_p = Slider(ax_p, "P", 0.0, 150.0, valinit=initial_p, valstep=1.0)
    slider_cn = Slider(ax_cn, "CN", 1.0, 100.0, valinit=initial_cn, valstep=1.0)

    def update(_value: float) -> None:
        cn = slider_cn.val
        y = [calculate_runoff(p, cn) for p in rainfall_values]
        line.set_ydata(y)
        current_p = slider_p.val
        point.set_data([current_p], [calculate_runoff(current_p, cn)])
        fig.canvas.draw_idle()

    slider_p.on_changed(update)
    slider_cn.on_changed(update)
    plt.show()


if __name__ == "__main__":
    build_interactive_plot()
