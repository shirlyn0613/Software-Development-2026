# Testing and Verification

This file documents the reproducible checks for Experiment 4.

## Unit Tests

Run:

```bash
python -m unittest discover -s tests
```

Current coverage includes:

- flood mask, depth, and percentage calculation
- no-flood and full-flood edge cases
- monotonic flood percentage under rising water levels
- flood volume calculation
- building barrier handling
- visualization file generation

## Physical Validation Report

Run:

```bash
python validation_suite.py
```

This generates:

```text
validation_report.txt
```

The report checks:

- DEM shape and elevation range
- flood percentage bounds
- edge cases below minimum and above maximum elevation
- maximum depth consistency
- monotonic area and volume behavior
- representative outputs at 40 m, 45 m, and 50 m

## End-to-End Pipeline

Run:

```bash
python example_usage.py
```

This regenerates the analysis outputs and validation report together.
