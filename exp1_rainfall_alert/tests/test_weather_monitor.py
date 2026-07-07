from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import weather_alert as alert  # noqa: E402
import weather_monitor as monitor  # noqa: E402


FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
PROJECT_ALERT_LOG = PROJECT_ROOT / "alert_log.txt"


def load_threshold_cases() -> list[tuple[float, str, str]]:
    with (FIXTURE_DIR / "alert_threshold_cases.csv").open("r", encoding="utf-8-sig", newline="") as file:
        return [
            (float(row["rainfall"]), row["expected_level"], row["expected_color"])
            for row in csv.DictReader(file)
        ]


class WeatherDataTests(unittest.TestCase):
    @patch("weather_monitor.requests.get")
    def test_get_weather_data_extracts_current_weather(self, mock_get: Mock) -> None:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "name": "Beijing",
            "dt": 1713078000,
            "rain": {"1h": 12.5},
            "main": {"temp": 22.3},
        }
        mock_get.return_value = response

        result = monitor.get_weather_data("Beijing", "fake-key")

        self.assertEqual(result["city"], "Beijing")
        self.assertEqual(result["rainfall_mm_per_hour"], 12.5)
        self.assertEqual(result["temperature_celsius"], 22.3)
        self.assertIn("timestamp", result)

    @patch("weather_monitor.requests.get")
    def test_get_weather_data_uses_three_hour_rainfall_average(self, mock_get: Mock) -> None:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "name": "Sanming",
            "dt": 1713078000,
            "rain": {"3h": 9.0},
            "main": {"temp": 19.5},
        }
        mock_get.return_value = response

        result = monitor.get_weather_data("Sanming", "fake-key")

        self.assertEqual(result["rainfall_mm_per_hour"], 3.0)

    @patch("weather_monitor.requests.get")
    def test_get_weather_data_handles_api_errors(self, mock_get: Mock) -> None:
        response = Mock()
        response.status_code = 404
        response.text = "not found"
        mock_get.return_value = response

        result = monitor.get_weather_data("UnknownCity", "fake-key")

        self.assertIn("error", result)
        self.assertIn("not found", result["error"])


class AlertTests(unittest.TestCase):
    def test_check_alert_thresholds_from_fixture(self) -> None:
        for rainfall, expected_level, expected_color in load_threshold_cases():
            with self.subTest(rainfall=rainfall):
                result = alert.check_alert(rainfall)
                self.assertEqual(result["level"], expected_level)
                self.assertEqual(result["color"], expected_color)

    def test_check_alert_edge_cases(self) -> None:
        self.assertEqual(alert.check_alert(None)["level"], "Green")
        self.assertEqual(alert.check_alert(-1)["level"], "Green")
        self.assertEqual(alert.check_alert(25, yellow_threshold=30, red_threshold=20)["level"], "Red")

    def test_log_alert_skips_green(self) -> None:
        temp_log = FIXTURE_DIR / "tmp_green_log.txt"
        if temp_log.exists():
            temp_log.unlink()

        logged = alert.log_alert("Beijing", 0.0, "Green", log_file=temp_log)

        self.assertFalse(logged)
        self.assertFalse(temp_log.exists())

    def test_log_alert_writes_yellow_and_red_to_temp_file(self) -> None:
        temp_log = FIXTURE_DIR / "tmp_alert_log.txt"
        if temp_log.exists():
            temp_log.unlink()

        yellow_logged = alert.log_alert("Wuhan", 12.0, "Yellow", log_file=temp_log)
        red_logged = alert.log_alert("Sanming", 22.5, "Red", debug=True, log_file=temp_log)
        content = temp_log.read_text(encoding="utf-8")
        temp_log.unlink()

        self.assertTrue(yellow_logged)
        self.assertTrue(red_logged)
        self.assertIn("City: Wuhan", content)
        self.assertIn("Level: Yellow", content)
        self.assertIn("[DEBUG]", content)
        self.assertIn("City: Sanming", content)
        self.assertIn("Level: Red", content)

    def test_process_weather_alert_records_debug_red_in_project_alert_log(self) -> None:
        result = alert.process_weather_alert(
            "DebugTestCity",
            28.8,
            debug=True,
            log_file=PROJECT_ALERT_LOG,
        )
        content = PROJECT_ALERT_LOG.read_text(encoding="utf-8")

        self.assertEqual(result["level"], "Red")
        self.assertTrue(result["logged"])
        self.assertIn("[DEBUG] | City: DebugTestCity", content)
        self.assertIn("Rainfall: 28.8 mm/h", content)
        self.assertIn("Level: Red", content)


if __name__ == "__main__":
    unittest.main()
