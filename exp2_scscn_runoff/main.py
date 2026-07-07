"""End-to-end runner for Experiment 2."""

from __future__ import annotations

import subprocess
import sys


def run(command: list[str]) -> None:
    """Run a command and stop the pipeline if it fails."""
    print(f"\n$ {' '.join(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    """Run tests, validation, and figure generation."""
    python = sys.executable
    run([python, "-m", "unittest", "test_scscn.py"])
    run([python, "-m", "unittest", "test_extensions.py"])
    run([python, "validate_scs_cn.py"])
    run([python, "sensitivity_analysis.py"])

    print("\nExperiment 2 pipeline completed successfully.")


if __name__ == "__main__":
    main()
