# Experiment 3: Reservoir Dispatch Optimization

This project solves a 7-day reservoir dispatch problem with `scipy.optimize`,
then generates a trade-off plot and validation report.

## Files

- `reservoir_optimize.py` - main optimization and analysis script
- `reservoir_extensions.py` - optional extension utilities
- `optimal_schedule.csv` - generated 7-day release schedule
- `tradeoff_analysis.png` - Pareto-style frontier plot
- `tradeoff_frontier.csv` - sampled frontier data
- `validation_report.txt` - constraint validation summary
- `robustness_analysis.csv` - uncertain inflow scenario results
- `stochastic_summary.csv` - uncertainty summary statistics
- `rolling_horizon_schedule.csv` - rolling horizon dispatch output
- `water_quality_proxy.csv` - simple downstream water quality proxy
- `algorithm_comparison.csv` - algorithm comparison table
- `uncertainty_histogram.png` - uncertainty visualization
- `prompt_log.md` - AI interaction log
- `Experiment3_Reservoir_Optimization.docx` - lab handout

## Requirements

- Python 3.10+
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`

## Run

```powershell
python reservoir_optimize.py
python reservoir_extensions.py
```

This will generate the CSV, plot, and validation report in the same folder.

## Notes

- The main schedule uses hard ecological and storage constraints.
- Trade-off analysis relaxes the ecological lower bound so the frontier is visible.
- Revenue is a lab-scale proxy based on release, price, and a fixed scaling factor.
- Optional extensions add inflow uncertainty, rolling horizon optimization, a water quality proxy, and algorithm comparison.
