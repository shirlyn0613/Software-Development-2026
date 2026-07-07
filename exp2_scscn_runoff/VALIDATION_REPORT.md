# Validation Report

## Experiment

Specialized Experiment 2: Hydrological Modeling - SCS-CN Runoff Calculation

## Model Formula

The implemented SCS-CN method uses:

```text
S  = (25400 / CN) - 254
Ia = 0.2 * S
Q  = 0, when P < Ia
Q  = (P - Ia)^2 / (P - Ia + S), otherwise
```

The implementation also enforces the hydrological constraint `Q <= P`.

## Reference Case

For `P = 50 mm` and `CN = 80`:

```text
S  = (25400 / 80) - 254 = 63.5 mm
Ia = 0.2 * 63.5 = 12.7 mm
Q  = (50 - 12.7)^2 / (50 - 12.7 + 63.5)
Q  = 13.80 mm
```

The computed result matches the expected value of about `13.8 mm`.

## Validation Checks

| Check | Result |
|---|---|
| Zero rainfall gives zero runoff | Pass |
| Rainfall below initial abstraction gives zero runoff | Pass |
| `Q <= P` for random sampled inputs | Pass |
| Runoff increases as CN increases at fixed rainfall | Pass |
| `P = 50 mm`, `CN = 80` gives about `13.8 mm` | Pass |
| `CN = 100` behaves as an impervious surface | Pass |

## Sensitivity Findings

- At fixed rainfall, higher CN values produce greater runoff.
- The CN-runoff relationship is nonlinear, especially at high CN values.
- Urban or paved surfaces with high CN values generate much larger direct runoff.
- The generated curves remain below or equal to the `Q = P` physical upper bound.

## Reproducibility

Run the validation script:

```bash
python validate_scs_cn.py
```

Run the full pipeline:

```bash
python main.py
```
