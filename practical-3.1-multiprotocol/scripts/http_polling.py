import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8090/api/weather"
INTERVAL_SECONDS = 60
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "http_weather_history.csv"


def fetch_weather():
    request = Request(
        f"{BASE_URL}/current",
        headers={"Accept": "application/json"},
    )

    with urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP status: {response.status}")

        data = json.loads(response.read().decode("utf-8"))

    for field in ("temperature", "humidity", "pressure"):
        if field not in data:
            raise ValueError(f"Missing field: {field}")

    return data


def save_weather(data):
    file_exists = OUTPUT_FILE.exists()

    with OUTPUT_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "collected_at",
                "temperature",
                "humidity",
                "pressure",
                "api_timestamp",
                "status",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "pressure": data["pressure"],
            "api_timestamp": data.get("timestamp", ""),
            "status": "ONLINE",
        })


def main():
    print(f"HTTP polling started. Interval: {INTERVAL_SECONDS} seconds")
    print(f"CSV history: {OUTPUT_FILE}")
    print("Press Ctrl+C to stop.")

    while True:
        try:
            weather = fetch_weather()
            save_weather(weather)
            print(
                f"OK | Temperature: {weather['temperature']} °C | "
                f"Humidity: {weather['humidity']} % | "
                f"Pressure: {weather['pressure']} hPa"
            )
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as error:
            print(f"ERROR | {error}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHTTP polling stopped.")