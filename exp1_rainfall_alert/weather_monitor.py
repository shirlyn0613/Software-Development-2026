"""Core weather data access for Experiment 1.

This module only talks to OpenWeatherMap and normalizes the returned weather
payload. Alert classification and logging live in `weather_alert.py`; the
Streamlit UI lives in `weather_dashboard.py`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests


API_URL = "https://api.openweathermap.org/data/2.5/weather"


def _read_rainfall(data: dict[str, Any]) -> float:
    """Return rainfall intensity in mm/h from an OpenWeatherMap response."""
    rain = data.get("rain", {})
    if "1h" in rain:
        return float(rain["1h"])
    if "3h" in rain:
        return float(rain["3h"]) / 3.0
    return 0.0


def _read_timestamp(data: dict[str, Any]) -> str:
    timestamp = data.get("dt")
    if timestamp is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_weather_data(city: str, api_key: str) -> dict[str, Any]:
    """Fetch current weather data for a city from OpenWeatherMap.

    Returns a normalized dictionary:
    {
        "city": str,
        "rainfall_mm_per_hour": float,
        "temperature_celsius": float,
        "timestamp": str,
        "raw": dict
    }

    On failure, returns {"error": "..."} instead of raising.
    """
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 401:
            return {"error": "Invalid API key. Please check your OpenWeatherMap API key."}
        if response.status_code == 404:
            return {"error": f"City '{city}' not found. Please check the city name."}
        if response.status_code != 200:
            return {"error": f"HTTP error {response.status_code}: {response.text}"}

        data = response.json()
        return {
            "city": data["name"],
            "rainfall_mm_per_hour": _read_rainfall(data),
            "temperature_celsius": float(data["main"]["temp"]),
            "timestamp": _read_timestamp(data),
            "raw": data,
        }
    except requests.exceptions.Timeout:
        return {"error": "Connection timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Network error. Please check your internet connection."}
    except requests.exceptions.RequestException as exc:
        return {"error": f"Request failed: {exc}"}
    except (KeyError, TypeError, ValueError) as exc:
        return {"error": f"Failed to parse response: {exc}"}


def fetch_weather(city: str, api_key: str) -> dict[str, Any]:
    """Backward-compatible alias used by older code/tests."""
    return get_weather_data(city, api_key)
