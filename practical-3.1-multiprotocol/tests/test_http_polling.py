import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import http_polling


class HTTPPollingTests(unittest.TestCase):
    def test_fetch_weather_returns_required_fields(self):
        data = http_polling.fetch_weather()

        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("pressure", data)

    def test_save_weather_writes_csv_header_and_data(self):
        sample = {
            "temperature": 21.5,
            "humidity": 50.0,
            "pressure": 1012.0,
            "timestamp": "2026-10-23T12:00:00+00:00",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "weather.csv"

            with patch.object(http_polling, "OUTPUT_FILE", csv_path):
                http_polling.save_weather(sample)

            with csv_path.open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["temperature"], 21.5.__str__())
            self.assertEqual(rows[0]["status"], "ONLINE")


if __name__ == "__main__":
    unittest.main()