# Experiment 2: SCS-CN Runoff Calculation

This project implements the Soil Conservation Service Curve Number (SCS-CN) runoff method, tests physical boundary conditions, and performs sensitivity analysis.

## Files

- `scscn_runoff.py` - core SCS-CN runoff calculation
- `test_scscn.py` - boundary-condition unit tests
- `sensitivity_analysis.py` - plots for CN sensitivity analysis
- `runoff_comparison.png` - generated comparison figure
- `runoff_extensions.py` - optional extension utilities
- `interactive_runoff_plot.py` - interactive slider-based plot
- `test_extensions.py` - tests for extension utilities
- `prompt_log.md` - AI interaction record

## Run

```bash
python -m unittest test_scscn.py
python sensitivity_analysis.py
python -m unittest test_extensions.py
python interactive_runoff_plot.py
```

## Notes

- The main runoff function follows:
  - `S = (25400 / CN) - 254`
  - `Ia = 0.2 * S`
  - `Q = 0` when `P < Ia`
  - otherwise `Q = (P - Ia)^2 / (P - Ia + S)`
- The implementation ensures runoff does not exceed rainfall.
- Sensitivity analysis uses fixed `P = 50 mm` and multiple CN values.
