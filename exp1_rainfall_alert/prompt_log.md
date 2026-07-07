# Prompt Log - Experiment 1

Documentation of AI interactions

---

## Part 0: Initial

**prompt 1**

> read this document know the basic information

**answer 1**

> I read [Experiment1_Rainfall_Alert.docx](Experiment1_Rainfall_Alert.docx). It’s a 2-hour lab handout for **Specialized Experiment 1: Short-term Rainfall Forecasting & Alert System** in the **Smart Water Lab Series**.

> Main points:
>
> - **Goal:** build a real-time rainfall monitoring system using external weather APIs, threshold-based alert logic, and a Streamlit dashboard.
> - **Learning objectives:** API integration, alert logic, dashboard building, validating results with domain knowledge, and documenting AI interactions in a prompt log.
> - **Core tasks:**
>   1. Fetch weather data from OpenWeatherMap
>   2. Implement alert thresholds
>   3. Build the dashboard
>   4. Test and validate physical reasonableness
> - **Deliverables:** `weather_monitor.py`, `alert_log.txt`, `prompt_log.md`, and a dashboard screenshot.
> - **Thresholds:** Green `< 10 mm/h`, Yellow `10–20 mm/h`, Red `>= 20 mm/h`.
> - **Extra table:** rainfall intensity categories: Light, Moderate, Heavy, Violent.
> - **Grading:** API integration 25%, alert logic 25%, dashboard 25%, prompt log 15%, code quality 10%.
>
> The document also includes a sample code structure, success tips, and optional extensions like multi-city monitoring, notifications, prediction, and map visualization.

## Part 1: API Integration

**prompt 1**

> I am a water resources student building a rainfall monitoring system. Please write Python code to fetch current weather data for Beijing using the OpenWeatherMap API. The code should: 1. Use the requests library to make the API call 2. Extract rainfall intensity from the response 3. Handle API errors gracefully 4. Include comments explaining each step  API endpoint: https://api.openweathermap.org/data/2.5/weather

**answer 1**

> [PYTHON CODE CREATED]
>
> A few notes:
>
> - `rainfall = 0.0` usually means no rain is currently reported.
> - OpenWeather often returns rain only when it is actively raining.
> - If you want, I can also add the alert-threshold logic and logging part next.

## Part 2: Alert Logic Implementation

prompt 1

> Requirements:  - Green: Rainfall < 10 mm/h (Normal) - Yellow: 10 ≤ Rainfall < 20 mm/h (Moderate) - Red: Rainfall ≥ 20 mm/h (Heavy - ALERT)  When Red alert triggers: - Display warning message - Log event to file with timestamp - Show alert in dashboard

answer 1

> [UPDATE PYTHON CODE CREATED]
> Done. Alarm levels have been updated:
>
> - **Green**: < 10 mm/h (Normal)
> - **Yellow**: 10-20 mm/h (Moderate)
> - **Red**: ≥ 20 mm/h (ALERT)
>
> When Red is triggered: display warning message, record to `rainfall_alerts.json`, display on the dashboard

---

## Part 3: Dashboard Creation

prompt 1

> Dashboard Requirements:  1. Title: 'Rainfall Monitor - [City Name]' 2. Current rainfall display (large metric) 3. Alert status indicator (color-coded) 4. Historical data chart (if time permits) 5. Auto-refresh every 5 minutes

answer 1

> Created the dashboard structure in `weather_monitor.py`.
>
> - Added a sidebar for API key and city input
> - Added current rainfall metric display
> - Added color-coded alert status
> - Added a recent rainfall history chart
> - Added optional 5-minute auto-refresh support

## Part 4: Optional Extensions

**prompt 1**

> Finish the optional extensions and decorate the app UI.

**answer 1**

> Upgraded `weather_monitor.py` with:
>
> - multi-city monitoring
> - a trend-based rainfall forecast panel
> - Folium map visualization for city locations
> - optional email and SMS alert hooks
> - a cleaner dashboard layout with styled KPI cards and tabs

## Part 5: UI Revision

**prompt 1**

> Make the UI cleaner like the reference screenshot and change city selection to country, province/region, and city. Default should be China / Beijing.

**answer 1**

> Rebuilt `weather_monitor.py` with a map-first layout, direct city status cards, a top control area, and a hierarchical location selector.
>
> - Default selector: China -> Beijing -> Beijing
> - Added optional comparison cities for multi-city monitoring
> - Kept history, prediction, alert log, email/SMS hooks, and Folium map visualization

## Part 6: Project Quality Supplements

**prompt 1**

> Supplement the project according to teacher feedback: add test scripts, verification reports, and unified dependency management.

**answer 1**

> Added project quality files:
>
> - `requirements.txt` for unified dependency management
> - `run_tests.py` as a simple local test runner
> - `tests/test_weather_monitor.py` for offline unit tests
> - `tests/README.md` as the test guide
> - `reports/verification_report.md` as the verification report
>
> Updated `README.md` with project structure, Quick Run, test instructions, and verification report location.
>
> Test result: 8 tests passed.

## Part 7: Logic and UI Separation

**prompt 1**

> Separate code logic: `weather_monitor.py` should handle core weather data fetching, prediction, and monitoring, while another file should handle the web dashboard. The monitor should avoid a fixed city tree and extract country, province/state, and city information from API data.

**answer 1**

> Refactored the project:
>
> - `weather_monitor.py` now contains only core logic: weather API access, geocoding API access, API-derived city tree construction, alert thresholds, prediction, logs, and notifications.
> - `dashboard_app.py` now contains the Streamlit dashboard UI, Folium map, city cards, controls, and tabs.
> - The city tree is now built from OpenWeather Geocoding API fields: `country`, `state`, `name`, `lat`, and `lon`.
> - Updated tests for geocoding, city-tree construction, location-based weather fetching, and core monitoring logic.
>
> Test result: 10 tests passed.

## Part 8: Reference-Based Reset

**prompt 1**

> Use the provided reference files from the repository as a guide, not a direct copy. Rebuild the core implementation and tests, especially alert-log tests.

**answer 1**

> Reset the project toward the reference structure:
>
> - `weather_monitor.py`: OpenWeatherMap API fetch and normalization.
> - `weather_alert.py`: threshold classification and alert logging.
> - `weather_dashboard.py`: Streamlit dashboard.
> - `dashboard_app.py`: compatibility wrapper for the dashboard.
> - `tests/test_weather_monitor.py`: offline tests for API parsing, thresholds, and alert logging.
>
> The alert-log tests now verify:
>
> - Green readings are not logged.
> - Yellow readings are logged.
> - Red readings are logged.
> - A test-generated Red record is appended to `alert_log.txt` with `[DEBUG]`.
>
> Test result: 8 tests passed.
