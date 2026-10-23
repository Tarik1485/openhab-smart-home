import os
import random
import time
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
PORT = int(os.getenv("MQTT_PORT", "1884"))
USERNAME = os.getenv("MQTT_USERNAME", "sensor")
PASSWORD = os.getenv("MQTT_PASSWORD")

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="openhab_sensor_simulator"
)

if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to Mosquitto successfully!")
    else:
        print(f"Connection failed: {reason_code}")

client.on_connect = on_connect

print(f"Connecting to {BROKER}:{PORT}...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

try:
    while True:
        temperature = round(random.uniform(19.0, 28.0), 1)
        humidity = round(random.uniform(35.0, 70.0), 1)
        motion = random.choice(["ON", "OFF"])

        client.publish("home/kitchen/temperature", str(temperature), qos=1)
        client.publish("home/kitchen/humidity", str(humidity), qos=1)
        client.publish("home/kitchen/motion", motion, qos=1)

        print(
            f"Temperature: {temperature} C | "
            f"Humidity: {humidity}% | Motion: {motion}"
        )

        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping simulator...")

finally:
    client.loop_stop()
    client.disconnect()
