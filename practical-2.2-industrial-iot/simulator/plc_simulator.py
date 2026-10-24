import asyncio
import math
import random
import time

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import SimData, SimDevice, DataType

HOST = "127.0.0.1"
PORT = 1502
DEVICE_ID = 1
STARTED_AT = time.time()


def make_registers(address, count):
    return SimData(
        address=address,
        count=count,
        values=[0] * count,
        datatype=DataType.REGISTERS,
    )


# Чотири простори даних Modbus:
# coils, discrete inputs, holding registers, input registers.
device = SimDevice(
    id=DEVICE_ID,
    simdata=(
        [SimData(0, count=10, values=False, datatype=DataType.BITS)],
        [SimData(0, count=10, values=False, datatype=DataType.BITS)],
        [make_registers(0, 10)],
        [make_registers(0, 40)],
    ),
)


def encode(value, scale=10):
    return max(0, min(65535, int(round(value * scale))))


def generate_registers():
    elapsed = time.time() - STARTED_AT
    phase = elapsed / 15.0

    # Input Registers 0–3: температури чотирьох двигунів, °C × 10.
    temperatures = [
        48 + 3 * math.sin(phase) + random.uniform(-0.8, 0.8),
        51 + 4 * math.sin(phase + 0.5) + random.uniform(-0.8, 0.8),
        46 + 2 * math.sin(phase + 1.0) + random.uniform(-0.8, 0.8),
        53 + 3 * math.sin(phase + 1.5) + random.uniform(-0.8, 0.8),
    ]

    # Input Registers 4–9: вібрація шести підшипників, мм/с × 100.
    vibrations = [
        2.0 + random.uniform(-0.25, 0.25)
        for _ in range(6)
    ]

    # Періодична аномалія вібрації.
    if int(elapsed) % 45 >= 35:
        vibrations[2] += 2.5

    # Input Registers 10–12: потужність фаз, кВт × 100.
    powers = [
        4.0 + random.uniform(-0.3, 0.3),
        4.2 + random.uniform(-0.3, 0.3),
        3.9 + random.uniform(-0.3, 0.3),
    ]

    # Input Register 13: гідравлічний тиск, бар × 10.
    pressure = (
        120 + 4 * math.sin(phase) + random.uniform(-1, 1)
    )

    # Input Registers 14–21: вісім секцій конвеєра.
    conveyor = [1] * 8

    # Імітація зупинки шостої секції.
    if int(elapsed) % 60 >= 50:
        conveyor[5] = 0

    # Input Registers 22–24: потужність та виробництво.
    total_power = sum(powers)
    produced = int(elapsed / 10)
    good = max(0, produced - int(produced * 0.03))

    registers = [0] * 40

    for index, value in enumerate(temperatures):
        registers[index] = encode(value, 10)

    for index, value in enumerate(vibrations, start=4):
        registers[index] = encode(value, 100)

    for index, value in enumerate(powers, start=10):
        registers[index] = encode(value, 100)

    registers[13] = encode(pressure, 10)

    for index, value in enumerate(conveyor, start=14):
        registers[index] = value

    registers[22] = encode(total_power, 100)
    registers[23] = min(65535, produced)
    registers[24] = min(65535, good)

    return registers, temperatures[0], vibrations[2], pressure, total_power


async def main():
    print("=" * 55)
    print("Industrial PLC Simulator")
    print(f"Modbus TCP: {HOST}:{PORT}")
    print(f"Device ID: {DEVICE_ID}")
    print("Input Registers: 0-39")
    print("Holding Registers: 0-9")
    print("=" * 55)

    # Створення сервера всередині запущеного asyncio event loop.
    server = ModbusTcpServer(
        device,
        address=(HOST, PORT),
    )

    async def update_plc():
        print("PLC data updater started.", flush=True)

        while True:
            (
                registers,
                temperature,
                vibration,
                pressure,
                power,
            ) = generate_registers()

            # Function code 4: Input Registers.
            await server.async_setValues(
                DEVICE_ID, 4, 0, registers
            )

            # Function code 3: Holding Registers.
            # 0: температурний поріг 75 °C × 10.
            # 1: поріг вібрації 4 мм/с × 100.
            # 2: команда конвеєра (1 = працювати).
            await server.async_setValues(
                DEVICE_ID,
                3,
                0,
                [750, 400, 1, 0, 0, 0, 0, 0, 0, 0],
            )

            print(
                f"PLC | M1={temperature:.1f} °C | "
                f"V3={vibration:.2f} mm/s | "
                f"Pressure={pressure:.1f} bar | "
                f"Power={power:.2f} kW",
                flush=True,
            )

            await asyncio.sleep(1)

    updater = asyncio.create_task(update_plc())

    try:
        await server.serve_forever()
    finally:
        updater.cancel()
        await asyncio.gather(updater, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPLC simulator stopped.")