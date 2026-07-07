# Experiment 3: Reservoir Dispatch Optimization

This project solves a 7-day reservoir dispatch problem with `scipy.optimize`,
then generates a trade-off plot, optional extension analyses, tests, and a
formal validation report.

## Files

- `reservoir_optimize.py` - main optimization and analysis script
- `reservoir_extensions.py` - optional extension utilities
- `tradeoff_analysis.py` - Pareto frontier analysis
- `rolling_horizon.py` - full-horizon vs rolling-horizon comparison
- `uncertainty_analysis.py` - Monte Carlo inflow uncertainty analysis
- `water_quality.py` - water quality extension analysis
- `validation.py` - standalone six-check validation report generator
- `test_reservoir_optimization.py` - unit tests for core logic
- `TESTING.md` - testing and verification notes
- `requirements.txt` - dependency list for this experiment
- `optimal_schedule.csv` - generated 7-day release schedule
- `tradeoff_analysis.png` - Pareto-style frontier plot
- `tradeoff_frontier.csv` - sampled frontier data
- `validation_report.txt` - constraint validation summary
- `validation_report_latest.txt` - fallback report if `validation_report.txt` is open during regeneration
- `robustness_analysis.csv` - uncertain inflow scenario results
- `stochastic_summary.csv` - uncertainty summary statistics
- `rolling_horizon_schedule.csv` - rolling horizon dispatch output
- `water_quality_proxy.csv` - simple downstream water quality proxy
- `water_quality_analysis.png` - three-scenario water quality plot
- `water_quality_summary.csv` - water quality scenario summary
- `algorithm_comparison.csv` - algorithm comparison table
- `uncertainty_histogram.png` - uncertainty visualization
- `uncertainty_analysis.png` - three-panel uncertainty plot
- `uncertainty_analysis.csv` - scenario results under inflow uncertainty
- `rolling_horizon_comparison.png` - full vs rolling horizon plot
- `rolling_horizon_comparison.csv` - full vs rolling horizon comparison table
- `prompt_log.md` - AI interaction log
- `Experiment3_Reservoir_Optimization.docx` - lab handout

## Requirements

- Python 3.10+
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Quick Run

```powershell
python reservoir_optimize.py
python validation.py
python tradeoff_analysis.py
python rolling_horizon.py
python uncertainty_analysis.py
python water_quality.py
python reservoir_extensions.py
```

This will generate the schedule CSV, validation report, analysis tables, and
figures in the same folder.

## Tests

```powershell
python -m unittest test_reservoir_optimization.py
```

The tests cover storage mass balance, revenue calculation, ecological deficit,
and final schedule feasibility.

## Notes

- The main schedule uses hard ecological and storage constraints.
- Trade-off analysis relaxes the ecological lower bound so the frontier is visible.
- Revenue is a lab-scale proxy based on release, price, and a fixed scaling factor.
- Optional extensions add inflow uncertainty, rolling horizon optimization, a water quality proxy, and algorithm comparison.
- If an output CSV/TXT/PNG is open in another program on Windows, scripts write a `_latest` copy instead.
