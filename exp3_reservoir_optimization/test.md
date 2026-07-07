# Experiment 3 Testing and Verification

This file documents the verification workflow requested for the reservoir optimization lab.

## Test Scripts

- `test_reservoir_optimization.py` checks mass balance, revenue calculation, ecological deficit, and feasibility of the optimized schedule.
- `validation.py` reads `optimal_schedule.csv` and writes a formal `validation_report.txt` with six pass/fail checks.

## Quick Verification

```powershell
python reservoir_optimize.py
python validation.py
python -m unittest test_reservoir_optimization.py
```

## Validation Checks

1. Storage lower bound: `storage >= 100,000 m3`
2. Storage upper bound: `storage <= 1,000,000 m3`
3. Ecological release: `release >= 10 m3/s`
4. Maximum release: `release <= 100 m3/s`
5. Mass balance: `V[t+1] = V[t] + (inflow - release) * dt`
6. Revenue calculation consistency
