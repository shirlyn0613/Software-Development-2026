# Test Guide

This folder contains offline tests for the rainfall alert system.

## What Is Tested

- OpenWeatherMap API parsing with mocked responses
- 1-hour rainfall extraction
- 3-hour rainfall average conversion
- HTTP error handling
- Green / Yellow / Red threshold boundaries from `fixtures/alert_threshold_cases.csv`
- Green records are not logged
- Yellow and Red records are logged
- Red test records include `[DEBUG]`
- Running tests appends one debug Red record to project `alert_log.txt`

## Run Tests

From the project root:

```powershell
conda activate lab
python run_tests.py
```

Or run unittest directly:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

The tests do not call the real OpenWeatherMap API. One test intentionally appends a `[DEBUG]` Red alert record to the project `alert_log.txt`.
