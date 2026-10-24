import json
import logging
import math
import os
import sqlite3
import time
from collections import deque
from datetime import datetime, timezone

from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt

# Налаштування з'єднань
PLC_HOST = "127.0.0.1"
PLC_PORT = 1502
PLC_DEVICE_ID = 1

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1886
MQTT_TOPIC = "industrial/edge"

POLL_INTERVAL = 2
DB_PATH = os.path.join(os.path.dirname(__file__), "industrial_history.db")

TEMP_LIMIT = 75.0
VIBRATION_LIMIT = 4.0
PRESSURE_MIN = 100.0
PRESSURE_MAX = 140.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Останні вимірювання для фільтра рухомого середнього.
temperature_history = deque(maxlen=5)
vibration_history = deque(maxlen=5)

# Локальна історія зберігається у SQLite.
def init_database():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                vibration REAL,
                pressure REAL,
                power REAL,
                availability REAL,
                performance REAL,
                quality REAL,
                oee REAL,
                wear_index REAL,
                alarms TEXT
            )
        """)
        connection.commit()


def moving_average(history, value):
    history.append(value)
    return sum(history) / len(history)


def calculate_oee(produced, good, availability):
    # Навчальна модель: планова продуктивність 6 одиниць за хвилину.
    ideal_rate_per_minute = 6.0
    elapsed_minutes = max((time.time() - START_TIME) / 60.0, 1 / 60)

    performance = min(
        1.0,
        produced / max(ideal_rate_per_minute * elapsed_minutes, 1.0),
    )

    quality = good / produced if produced > 0 else 1.0
    quality = max(0.0, min(1.0, quality))

    oee = availability * performance * quality
    return performance, quality, oee


def read_plc(client):
    result = client.read_input_registers(
        address=0,
        count=25,
        device_id=PLC_DEVICE_ID,
    )

    if result.isError():
        raise RuntimeError(f"Помилка читання PLC: {result}")

    values = result.registers

    temperatures = [values[i] / 10.0 for i in range(4)]
    vibrations = [values[i] / 100.0 for i in range(4, 10)]
    phase_powers = [values[i] / 100.0 for i in range(10, 13)]

    pressure = values[13] / 10.0
    conveyor_sections = values[14:22]
    total_power = values[22] / 100.0
    produced = values[23]
    good = values[24]

    return {
        "temperatures": temperatures,
        "vibrations": vibrations,
        "phase_powers": phase_powers,
        "pressure": pressure,
        "conveyor_sections": conveyor_sections,
        "total_power": total_power,
        "produced": produced,
        "good": good,
    }


def main():
    global START_TIME
    START_TIME = time.time()

    init_database()

    plc = ModbusTcpClient(
        PLC_HOST,
        port=PLC_PORT,
        timeout=3,
    )

    if not plc.connect():
        raise RuntimeError(
            "Не вдалося підключитися до PLC. Перевір, чи працює plc_simulator.py."
        )

    mqtt_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="industrial-edge-processor",
    )

    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        mqtt_client.loop_start()
        logging.info("MQTT connected: %s:%s", MQTT_HOST, MQTT_PORT)
    except Exception as error:
        logging.warning(
            "MQTT недоступний (%s). Дані продовжать зберігатися локально.",
            error,
        )
        mqtt_client = None

    cycle_count = 0

    try:
        while True:
            try:
                data = read_plc(plc)

                avg_temperature = moving_average(
                    temperature_history,
                    sum(data["temperatures"]) / len(data["temperatures"]),
                )

                avg_vibration = moving_average(
                    vibration_history,
                    max(data["vibrations"]),
                )

                pressure = data["pressure"]
                power = data["total_power"]

                alarms = []

                if avg_temperature >= TEMP_LIMIT:
                    alarms.append("HIGH_TEMPERATURE")

                if avg_vibration >= VIBRATION_LIMIT:
                    alarms.append("HIGH_VIBRATION")

                if not PRESSURE_MIN <= pressure <= PRESSURE_MAX:
                    alarms.append("HYDRAULIC_PRESSURE_OUT_OF_RANGE")

                stopped_sections = [
                    index + 1
                    for index, status in enumerate(data["conveyor_sections"])
                    if status == 0
                ]

                if stopped_sections:
                    alarms.append(
                        "CONVEYOR_STOPPED_SECTIONS_" +
                        "_".join(map(str, stopped_sections))
                    )

                availability = (
                    sum(data["conveyor_sections"]) /
                    len(data["conveyor_sections"])
                )

                performance, quality, oee = calculate_oee(
                    data["produced"],
                    data["good"],
                    availability,
                )

                # Навчальний індекс зношення: відносний показник 0–100%.
                temperature_factor = max(
                    0.0,
                    (avg_temperature - 40.0) / 40.0,
                )
                vibration_factor = max(
                    0.0,
                    avg_vibration / VIBRATION_LIMIT,
                )
                wear_index = min(100.0, temperature_factor * 40 + vibration_factor * 60)
                

                timestamp = datetime.now(timezone.utc).isoformat()

                payload = {
                    "timestamp": timestamp,
                    "temperature": round(avg_temperature, 2),
                    "vibration": round(avg_vibration, 3),
                    "pressure": round(pressure, 2),
                    "power": round(power, 2),
                    "phase_powers": [
                        round(value, 2)
                        for value in data["phase_powers"]
                    ],
                    "availability": round(availability, 3),
                    "performance": round(performance, 3),
                    "quality": round(quality, 3),
                    "oee": round(oee, 3),
                    "wear_index": round(wear_index, 2),
                    "produced": data["produced"],
                    "good": data["good"],
                    "conveyor_sections": data["conveyor_sections"],
                    "alarms": alarms,
                }

                with sqlite3.connect(DB_PATH) as connection:
                    connection.execute(
                        """
                        INSERT INTO measurements (
                            timestamp, temperature, vibration, pressure,
                            power, availability, performance, quality,
                            oee, wear_index, alarms
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            timestamp,
                            payload["temperature"],
                            payload["vibration"],
                            payload["pressure"],
                            payload["power"],
                            payload["availability"],
                            payload["performance"],
                            payload["quality"],
                            payload["oee"],
                            payload["wear_index"],
                            json.dumps(alarms),
                        ),
                    )
                    connection.commit()

              if mqtt_client is not None:
    mqtt_values = {
        "industrial/temperature": payload["temperature"],
        "industrial/vibration": payload["vibration"],
        "industrial/pressure": payload["pressure"],
        "industrial/power": payload["power"],
        "industrial/phase1_power": payload["phase_powers"][0],
        "industrial/phase2_power": payload["phase_powers"][1],
        "industrial/phase3_power": payload["phase_powers"][2],
        "industrial/availability": payload["availability"],
        "industrial/performance": payload["performance"],
        "industrial/quality": payload["quality"],
        "industrial/oee": payload["oee"],
        "industrial/wear_index": payload["wear_index"],
        "industrial/produced": payload["produced"],
        "industrial/good": payload["good"],
        "industrial/conveyor_sections": ",".join(
            str(value) for value in payload["conveyor_sections"]
        ),
        "industrial/alarms": ",".join(payload["alarms"]) or "NONE",
    }

    for topic, value in mqtt_values.items():
        info = mqtt_client.publish(
            topic,
            str(value),
            qos=1,
            retain=True,
        )
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            logging.warning("MQTT publish failed for %s: %s", topic, info.rc)
                cycle_count += 1

                logging.info(
                    "T=%.1f°C | V=%.2f mm/s | P=%.1f bar | "
                    "Power=%.2f kW | OEE=%.1f%% | Wear=%.1f%% | Alarms=%s",
                    avg_temperature,
                    avg_vibration,
                    pressure,
                    power,
                    oee * 100,
                    wear_index,
                    alarms or "none",
                )

            except Exception:
                logging.exception("Помилка циклу Edge Computing")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Edge processor stopped.")

    finally:
        plc.close()

        if mqtt_client is not None:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


if __name__ == "__main__":
    main()
