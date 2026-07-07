"""Rainfall alert classification and logging for Experiment 1."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


LOG_FILE = Path("alert_log.txt")
YELLOW_THRESHOLD = 10.0
RED_THRESHOLD = 20.0


def check_alert(
    rainfall: float | None,
    yellow_threshold: float = YELLOW_THRESHOLD,
    red_threshold: float = RED_THRESHOLD,
) -> dict[str, str]:
    """Classify rainfall as Green, Yellow, or Red."""
    if rainfall is None or rainfall < 0:
        rainfall = 0.0

    try:
        yellow = float(yellow_threshold)
        red = float(red_threshold)
    except (TypeError, ValueError):
        yellow = YELLOW_THRESHOLD
        red = RED_THRESHOLD

    if red < yellow:
        yellow = YELLOW_THRESHOLD
        red = RED_THRESHOLD

    if rainfall >= red:
        return {
            "level": "Red",
            "color": "red",
            "message": "HEAVY RAIN ALERT - Take precautions!",
        }
    if rainfall >= yellow:
        return {
            "level": "Yellow",
            "color": "yellow",
            "message": "Moderate Warning - Rain expected to continue",
        }
    return {
        "level": "Green",
        "color": "green",
        "message": "Normal - No alert",
    }


def format_alert_log_entry(
    city: str,
    rainfall: float,
    level: str,
    debug: bool = False,
) -> str:
    """Format one alert-log line."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    marker = " [DEBUG]" if debug else ""
    return f"[{timestamp}]{marker} | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}\n"


def log_alert(
    city: str,
    rainfall: float,
    level: str,
    debug: bool = False,
    log_file: Path = LOG_FILE,
) -> bool:
    """Append Yellow/Red alerts to the alert log.

    Green records are ignored. Tests may pass `debug=True` to mark synthetic
    alert records in `alert_log.txt`.
    """
    if level not in {"Yellow", "Red"}:
        return False

    try:
        with log_file.open("a", encoding="utf-8") as file:
            file.write(format_alert_log_entry(city, rainfall, level, debug=debug))
        return True
    except OSError:
        return False


def process_weather_alert(
    city: str,
    rainfall: float,
    debug: bool = False,
    log_file: Path = LOG_FILE,
) -> dict[str, str | bool]:
    """Classify rainfall and log it when the level is Yellow or Red."""
    alert = check_alert(rainfall)
    logged = log_alert(city, rainfall, alert["level"], debug=debug, log_file=log_file)
    return {**alert, "logged": logged}
