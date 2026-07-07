# Experiment 2: SCS-CN Runoff Calculation

This experiment implements the Soil Conservation Service Curve Number (SCS-CN) method for direct runoff estimation. It includes formula implementation, boundary-condition tests, physical validation, sensitivity analysis, optional hydrological extensions, and AI prompt documentation.

## Quick Run

```bash
pip install -r requirements.txt
python main.py
```

The full pipeline runs core tests, extension tests, validation checks, and plot generation.

## Individual Commands

```bash
python -m unittest test_scscn.py
python -m unittest test_extensions.py
python validate_scs_cn.py
python sensitivity_analysis.py
python interactive_runoff_plot.py
```

## Model

```text
S  = (25400 / CN) - 254
Ia = 0.2 * S
Q  = 0, when P < Ia
Q  = (P - Ia)^2 / (P - Ia + S), otherwise
```

The implementation ensures `Q <= P` and handles the special cases `CN <= 0` and `CN >= 100`.

## Verified Reference Case

For `P = 50 mm` and `CN = 80`:

```text
S  = 63.5 mm
Ia = 12.7 mm
Q  = 13.80 mm
```

This matches the value provided in the experiment handout.

## Project Files

| File | Description |
|---|---|
| `scscn_runoff.py` | Core SCS-CN runoff function. |
| `test_scscn.py` | Required boundary-condition test suite. |
| `sensitivity_analysis.py` | Generates CN sensitivity and rainfall-runoff plots. |
| `validate_scs_cn.py` | Structured physical validation report script. |
| `runoff_extensions.py` | Optional AMC, Rational Method, and time-area routing utilities. |
| `interactive_runoff_plot.py` | Interactive matplotlib sliders for `P` and `CN`. |
| `test_extensions.py` | Tests for optional extension utilities. |
| `main.py` | End-to-end pipeline runner. |
| `requirements.txt` | Unified dependency list. |
| `TESTING.md` | Test documentation. |
| `VALIDATION_REPORT.md` | Physical validation summary. |
| `prompt_log.md` | AI interaction record. |

## Output Figures

| File | Description |
|---|---|
| `runoff_comparison.png` | Combined comparison figure from the original lab requirements. |
| `cn_sensitivity.png` | CN vs runoff plot at fixed `P = 50 mm`. |
| `rainfall_runoff_curves.png` | Rainfall-runoff curves for several CN values. |

## Test Coverage

Core tests cover:

- `P = 0`
- `P < Ia`
- `P = Ia`
- normal case `P = 50 mm`, `CN = 80`
- maximum CN behavior
- `Q <= P` across sampled cases

See `TESTING.md` for details.

## Validation Summary

Physical validation confirms:

- all boundary conditions pass
- runoff never exceeds rainfall
- runoff increases as CN increases
- the worked example produces `Q ~= 13.8 mm`
- `CN = 100` behaves as an impervious surface

See `VALIDATION_REPORT.md` for details.
