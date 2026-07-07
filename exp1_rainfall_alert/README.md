# Rainfall Forecasting & Alert System

Experiment 1 rainfall monitoring project using OpenWeatherMap and Streamlit.

## Alert Rules

| Level | Threshold | Behavior |
|---|---:|---|
| Green | `< 10 mm/h` | Normal, no log |
| Yellow | `10 <= rainfall < 20 mm/h` | Warning, append to `alert_log.txt` |
| Red | `>= 20 mm/h` | Heavy alert, append to `alert_log.txt` |

## Files

| File | Role |
|---|---|
| `weather_monitor.py` | Fetch and normalize OpenWeatherMap current weather data |
| `weather_alert.py` | Classify rainfall thresholds and write alert logs |
| `weather_dashboard.py` | Streamlit dashboard for multi-city monitoring |
| `dashboard_app.py` | Compatibility wrapper that launches `weather_dashboard.py` |
| `alert_log.txt` | Timestamped Yellow/Red alert records |
| `tests/test_weather_monitor.py` | Offline tests for API parsing, thresholds, and logging |
| `tests/fixtures/alert_threshold_cases.csv` | Editable rainfall threshold test data |
| `reports/verification_report.md` | Verification report |
| `prompt_log.md` | AI interaction record |

## Quick Run

```powershell
conda activate lab
pip install -r requirements.txt
streamlit run weather_dashboard.py
```

Enter your OpenWeatherMap API key and comma-separated city names in the sidebar.

## Run Tests

```powershell
conda activate lab
python run_tests.py
```

The tests mock OpenWeatherMap responses, so they do not require a real API key.

One test intentionally appends a `[DEBUG]` Red alert record to `alert_log.txt` to prove that Red logging works without mixing test data with real alert data.

## Test Focus

- API response parsing
- 1-hour and 3-hour rainfall extraction
- HTTP error handling
- Green / Yellow / Red threshold boundaries
- Green records are not logged
- Yellow and Red records are logged
- Red test records include `[DEBUG]`
