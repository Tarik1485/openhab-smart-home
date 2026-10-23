import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
PORT = int(os.getenv("MQTT_PORT", "1884"))
USERNAME = os.getenv("MQTT_USERNAME", "sensor")
PASSWORD = os.getenv("MQTT_PASSWORD")

BASE = "weather-station"
STATUS_TOPIC = f"{BASE}/status"

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="weather_station_simulator",
)

if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)

client.will_set(
    STATUS_TOPIC,
    payload="OFFLINE",
    qos=1,
    retain=True,
)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT connected")
        client.publish(STATUS_TOPIC, "ONLINE", qos=1, retain=True)
    else:
        print(f"MQTT connection failed: {reason_code}")

client.on_connect = on_connect

def publish_sensor(topic, value):
    result = client.publish(
        f"{BASE}/{topic}",
        str(value),
        qos=1,
        retain=True,
    )
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"Publish failed for {topic}: {result.rc}")

print(f"Connecting to MQTT broker {BROKER}:{PORT}...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

try:
    while True:
        temperature = round(random.uniform(18.0, 28.0), 1)
        humidity = round(random.uniform(30.0, 75.0), 1)
        pressure = round(random.uniform(990.0, 1035.0), 1)
        rssi = random.randint(-85, -35)

        publish_sensor("temperature", temperature)
        publish_sensor("humidity", humidity)
        publish_sensor("pressure", pressure)
        publish_sensor("rssi", rssi)

        print(
            f"{datetime.now(timezone.utc).isoformat()} | "
            f"T={temperature} C | H={humidity}% | "
            f"P={pressure} hPa | RSSI={rssi} dBm"
        )
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping weather station...")

finally:
    client.publish(STATUS_TOPIC, "OFFLINE", qos=1, retain=True)
    client.loop_stop()
    client.disconnect()
