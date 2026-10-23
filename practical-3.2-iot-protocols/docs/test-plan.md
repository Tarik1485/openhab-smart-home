# Test plan and results

## Automated software checks

Run from the repository root:

```powershell
python -m unittest discover -s .\practical-3.2-iot-protocols\tests -v
python .\practical-3.2-iot-protocols\simulations\zigbee_recovery.py
```

Covered checks:
- Binary payload round trip.
- Fixed 22-byte simulated sensor payload.
- Invalid soil sensor count rejection.
- Zigbee route availability and router failure.
- CoAP resource reads, unknown resource errors, and actuator updates.

## Hardware tests not yet performed

- LoRaWAN RSSI at different distances, LOS/NLOS.
- OTAA join through The Things Network.
- Zigbee RF rejoin and router recovery on physical devices.
- Battery current measurements and battery-life validation.
- Coverage heat map.
