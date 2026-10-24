import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1885
PREFIX = "greenhouse/sensors"

SENSORS = {
    "air_temperature": lambda: round(random.uniform(20, 30), 1),
    "air_humidity": lambda: round(random.uniform(40, 80), 1),
    "soil_moisture": lambda: round(random.uniform(20, 75), 1),
    "illuminance": lambda: round(random.uniform(1000, 15000), 0),
    "air_quality": lambda: round(random.uniform(250, 900), 1),
    "soil_temperature": lambda: round(random.uniform(18, 27), 1),
}

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="greenhouse-simulator"
)

def main():
    print(f"Connecting to {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            for sensor, generate in SENSORS.items():
                value = generate()
                topic = f"{PREFIX}/{sensor}"
                client.publish(topic, str(value), qos=1)
                print(f"{topic} = {value}")

            client.publish(
                f"{PREFIX}/timestamp",
                datetime.now(timezone.utc).isoformat(),
                qos=1
            )
            print("-" * 40)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
