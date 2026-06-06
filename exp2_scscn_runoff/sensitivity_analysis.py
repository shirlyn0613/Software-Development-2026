"""Sensitivity analysis and visualization for the SCS-CN runoff method."""

from __future__ import annotations

import matplotlib.pyplot as plt

from scscn_runoff import calculate_runoff


def plot_sensitivity(output_path: str = "runoff_comparison.png") -> None:
    """Generate sensitivity plots for runoff under varying CN values."""
    cn_values = [60, 70, 80, 90, 95, 100]
    fixed_rainfall = 50.0
    q_values = [calculate_runoff(fixed_rainfall, cn) for cn in cn_values]

    rainfall_values = [0, 10, 20, 30, 40, 50, 60, 80, 100]
    comparison_cns = [60, 80, 95, 100]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(cn_values, q_values, marker="o")
    axes[0].set_title("CN vs Runoff at P = 50 mm")
    axes[0].set_xlabel("Curve Number (CN)")
    axes[0].set_ylabel("Runoff Q (mm)")
    axes[0].grid(True, alpha=0.3)

    for cn in comparison_cns:
        runoff_series = [calculate_runoff(p, cn) for p in rainfall_values]
        axes[1].plot(rainfall_values, runoff_series, marker="o", label=f"CN {cn}")

    axes[1].set_title("Rainfall vs Runoff for Different CN Values")
    axes[1].set_xlabel("Rainfall P (mm)")
    axes[1].set_ylabel("Runoff Q (mm)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    plot_sensitivity()
