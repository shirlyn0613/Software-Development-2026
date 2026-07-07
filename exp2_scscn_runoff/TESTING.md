# Testing Guide

This document explains how the SCS-CN experiment is tested.

## Test Files

| File | Purpose |
|---|---|
| `test_scscn.py` | Tests the core SCS-CN runoff function and required boundary conditions. |
| `test_extensions.py` | Tests optional extension utilities including AMC adjustment, Rational Method, and time-area routing. |
| `validate_scs_cn.py` | Runs physical validation checks and prints a structured PASS/FAIL report. |

## Quick Test Commands

```bash
python -m unittest test_scscn.py
python -m unittest test_extensions.py
python validate_scs_cn.py
```

## Required Boundary Conditions

The core tests cover:

- `P = 0`, expected `Q = 0`
- `P < Ia`, expected `Q = 0`
- `P = Ia`, expected `Q = 0`
- normal case `P = 50 mm`, `CN = 80`, expected `Q ~= 13.8 mm`
- maximum curve number `CN = 100`
- physical constraint `Q <= P`

## Expected Result

All tests should pass:

```text
Ran 6 tests ... OK
Ran 4 tests ... OK
6/6 validation checks passed
```
