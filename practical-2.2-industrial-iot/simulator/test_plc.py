from pymodbus.client import ModbusTcpClient

HOST = "127.0.0.1"
PORT = 1502

client = ModbusTcpClient(HOST, port=PORT, timeout=3)

try:
    if not client.connect():
        print("ERROR: Не вдалося підключитися до PLC.")
        raise SystemExit(1)

    print("OK: З'єднання з PLC встановлено.")

    result = client.read_input_registers(
        address=0,
        count=25,
        device_id=1,
    )

    if result.isError():
        print("ERROR: Не вдалося прочитати Input Registers:", result)
    else:
        values = result.registers

        print("\n=== PLC INPUT REGISTERS ===")

        for i in range(4):
            print(f"Motor {i + 1} temperature: {values[i] / 10:.1f} °C")

        for i in range(4, 10):
            print(f"Bearing {i - 3} vibration: {values[i] / 100:.2f} mm/s")

        for i in range(10, 13):
            print(f"Phase {i - 9} power: {values[i] / 100:.2f} kW")

        print(f"Hydraulic pressure: {values[13] / 10:.1f} bar")
        print("Conveyor sections:", values[14:22])
        print(f"Total power: {values[22] / 100:.2f} kW")
        print(f"Produced units: {values[23]}")
        print(f"Good units: {values[24]}")

finally:
    client.close()