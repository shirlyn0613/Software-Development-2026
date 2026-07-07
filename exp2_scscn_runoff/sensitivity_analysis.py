"""Sensitivity analysis and visualization for the SCS-CN runoff method."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from scscn_runoff import calculate_runoff


CN_VALUES = [60, 70, 80, 90, 95, 100]
FIXED_RAINFALL_MM = 50.0


def cn_sensitivity_analysis() -> list[tuple[int, float, float]]:
    """Calculate runoff for selected CN values at fixed rainfall."""
    results = []
    for cn in CN_VALUES:
        runoff = calculate_runoff(FIXED_RAINFALL_MM, cn)
        runoff_ratio = runoff / FIXED_RAINFALL_MM * 100
        results.append((cn, runoff, runoff_ratio))
    return results


def plot_cn_sensitivity(output_path: str = "cn_sensitivity.png") -> None:
    """Create a CN sensitivity bar and line plot."""
    results = cn_sensitivity_analysis()
    cn_values = [row[0] for row in results]
    runoff_values = [row[1] for row in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(cn_values)))

    bars = ax.bar(
        cn_values,
        runoff_values,
        color=colors,
        alpha=0.75,
        width=4,
        edgecolor="black",
        linewidth=0.5,
    )
    ax.plot(cn_values, runoff_values, "ko-", linewidth=2, label="Runoff trend")

    for bar, runoff in zip(bars, runoff_values):
        ax.annotate(
            f"{runoff:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title("Runoff Sensitivity to Curve Number (P = 50 mm)")
    ax.set_xlabel("Curve Number (CN)")
    ax.set_ylabel("Runoff Q (mm)")
    ax.set_xticks(cn_values)
    ax.set_xlim(55, 105)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_rainfall_runoff_curves(
    output_path: str = "rainfall_runoff_curves.png",
) -> None:
    """Create rainfall-runoff curves for selected CN values."""
    rainfall_values = np.arange(0, 101, 1)
    comparison_cns = [60, 70, 80, 90, 100]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(comparison_cns)))

    for cn, color in zip(comparison_cns, colors):
        runoff_values = [calculate_runoff(float(p), cn) for p in rainfall_values]
        ax.plot(rainfall_values, runoff_values, linewidth=2, color=color, label=f"CN = {cn}")

    ax.plot(
        rainfall_values,
        rainfall_values,
        "k--",
        linewidth=1.5,
        alpha=0.7,
        label="Q = P (max)",
    )
    ax.set_title("SCS-CN Runoff vs Rainfall for Different Curve Numbers")
    ax.set_xlabel("Rainfall P (mm)")
    ax.set_ylabel("Runoff Q (mm)")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_sensitivity(output_path: str = "runoff_comparison.png") -> None:
    """Generate sensitivity plots for runoff under varying CN values."""
    q_values = [calculate_runoff(FIXED_RAINFALL_MM, cn) for cn in CN_VALUES]

    rainfall_values = [0, 10, 20, 30, 40, 50, 60, 80, 100]
    comparison_cns = [60, 80, 95, 100]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(CN_VALUES, q_values, marker="o")
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
    print("SCS-CN sensitivity results at P = 50 mm")
    print("CN    Q(mm)    Runoff ratio(%)")
    for cn, runoff, ratio in cn_sensitivity_analysis():
        print(f"{cn:<5} {runoff:>6.2f} {ratio:>16.2f}")

    plot_sensitivity()
    plot_cn_sensitivity()
    plot_rainfall_runoff_curves()
    print("Generated: runoff_comparison.png, cn_sensitivity.png, rainfall_runoff_curves.png")
