# Rainfall Alert System

A Streamlit-based rainfall monitoring app for the **Short-term Rainfall Forecasting & Alert System** lab.

## What It Does

- Fetches current weather data from OpenWeatherMap
- Extracts rainfall intensity
- Classifies rainfall into:
  - Green: `< 10 mm/h`
  - Yellow: `10-20 mm/h`
  - Red: `>= 20 mm/h`
- Logs red alerts with timestamps
- Shows a live dashboard with:
  - current rainfall metric
  - color-coded alert status
  - country / province-region / city selector
  - multi-city comparison cards
  - rainfall trend forecast
  - map-first view with Folium
  - optional email/SMS hooks

## Main Files

- `weather_monitor.py` - main Streamlit app
- `alert_log.txt` - red alert records
- `prompt_log.md` - AI interaction log for the lab
- `Experiment1_Rainfall_Alert.docx` - lab handout

## Requirements

- Python 3.10+
- `requests`
- `pandas`
- `streamlit`
- `folium`
- optional: `streamlit-autorefresh`
- optional: `twilio`

## Setup

Create and activate the conda environment:

```powershell
conda activate lab
```

Install packages:

```powershell
pip install requests pandas streamlit folium streamlit-autorefresh twilio
```

## Run

Start the dashboard:

```powershell
streamlit run weather_monitor.py
```

Then enter:

- your OpenWeatherMap API key
- a location using the country -> province/region -> city selector
- optional comparison cities

Default location:

- Country: China
- Province / Region: Beijing
- City: Beijing

Example comparison cities:

- Shanghai
- Guangzhou
- Shenzhen
- Wuhan

## Optional Alerts

The app includes optional notification inputs for:

- Email alerts via SMTP
- SMS alerts via Twilio

These are optional and only work if you provide valid credentials.

## Output

The app may create or update:

- `alert_log.txt`

## Notes

- The forecast panel is trend-based and meant for lab demonstration.
- The map view depends on returned city coordinates.
- If the autorefresh package is missing, you can still refresh manually.
