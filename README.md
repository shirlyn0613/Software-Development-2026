# AI4SD Labs Overview

This folder contains four laboratory projects for the Smart Water Lab series.

## Projects

### Experiment 1: Rainfall Alert System
- Folder: `exp1_rainfall_alert`
- Focus: short-term rainfall monitoring, alert thresholds, and dashboard display
- Main entry: `weather_monitor.py`

### Experiment 2: SCS-CN Runoff Calculation
- Folder: `exp2_scscn_runoff`
- Focus: runoff calculation, unit testing, sensitivity analysis, and extensions
- Main entries: `scscn_runoff.py`, `sensitivity_analysis.py`, `interactive_runoff_plot.py`

### Experiment 3: Reservoir Dispatch Optimization
- Folder: `exp3_reservoir_optimization`
- Focus: reservoir release optimization, trade-off analysis, validation, and optional extensions
- Main entries: `reservoir_optimize.py`, `reservoir_extensions.py`

### Experiment 4: Flood Inundation Analysis
- Folder: `exp4_flood_inundation`
- Focus: DEM-based flood inundation simulation, visualization, and extensions
- Main entry: `flood_inundation.py`

## Quick Run

```powershell
python exp1_rainfall_alert\weather_monitor.py
python exp2_scscn_runoff\sensitivity_analysis.py
python exp3_reservoir_optimization\reservoir_optimize.py
python exp3_reservoir_optimization\reservoir_extensions.py
python exp4_flood_inundation\flood_inundation.py
```

## Notes

- Each experiment folder contains its own `README.md` and `prompt_log.md`.
- Output figures, CSV files, and validation reports are stored inside the corresponding experiment folder.
- The projects are organized as independent lab submissions, so they can be run separately.
